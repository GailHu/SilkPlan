<template>
    <div class="proposal-editor">
        <el-card class="editor-card">
            <template #header>
                <div class="card-header">
                    <span>标书编辑器</span>
                    <div class="header-actions">
                        <el-button type="primary" @click="generateFullProposal" :loading="generating">
                            一键生成全文
                        </el-button>
                        <el-button type="success" @click="saveProposal">
                            保存
                        </el-button>
                        <el-button type="warning" @click="previewProposal">
                            预览
                        </el-button>
                        <el-button type="info" @click="downloadProposal">
                            下载
                        </el-button>
                    </div>
                </div>
            </template>

            <!-- 生成进度 -->
            <div v-if="generating" class="generation-progress">
                <el-progress :percentage="generationProgress" :status="generationStatus" />
                <p class="progress-text">{{ generationMessage }}</p>
            </div>

            <div class="editor-container">
                <div class="outline-panel">
                    <h3>大纲</h3>
                    <el-tree :data="outlineTree" node-key="id" :props="defaultProps" @node-click="handleNodeClick" />
                </div>

                <div class="content-panel">
                    <div class="toolbar">
                        <el-button-group>
                            <el-button @click="aiContinue">AI续写</el-button>
                            <el-button @click="aiExpand">AI扩写</el-button>
                            <el-button @click="aiPolish">AI润色</el-button>
                        </el-button-group>
                        <el-button-group>
                            <el-button @click="insertImage">插入图片</el-button>
                            <el-button @click="searchContent">联网搜索</el-button>
                        </el-button-group>
                    </div>

                    <Editor v-model="content" api-key="6sbli4vlsv3jv11f6zrr4a3etvvld71gfwchwllyj95m10rz" :init="{
                        height: 500,
                        menubar: true,
                        plugins: [
                            'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                            'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                            'insertdatetime', 'media', 'table', 'help', 'wordcount'
                        ],
                        toolbar: 'undo redo | blocks | ' +
                            'bold italic forecolor | alignleft aligncenter ' +
                            'alignright alignjustify | bullist numlist outdent indent | ' +
                            'removeformat | help',
                        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
                        language: 'zh_CN',
                        branding: false,
                        promotion: false,
                        images_upload_url: '/api/upload-image',
                        automatic_uploads: true,
                        paste_data_images: true,
                        image_title: true,
                        image_caption: true,
                        image_advtab: true,
                        image_uploadtab: true,
                        image_class_list: [
                            { title: 'None', value: '' },
                            { title: 'Responsive', value: 'img-responsive' }
                        ]
                    }" />
                </div>
            </div>
        </el-card>

        <!-- 预览对话框 -->
        <el-dialog v-model="previewVisible" title="标书预览" width="80%" fullscreen>
            <div class="preview-content" v-html="previewContent"></div>
        </el-dialog>

        <!-- 图片选择对话框 -->
        <el-dialog v-model="imageDialogVisible" title="选择图片" width="60%">
            <div class="image-grid">
                <el-image v-for="(img, index) in imageLibrary" :key="index" :src="img.url" :preview-src-list="[img.url]"
                    fit="cover" class="image-item" @click="selectImage(img)" />
            </div>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Editor from '@tinymce/tinymce-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const content = ref('')
const generating = ref(false)
const previewVisible = ref(false)
const previewContent = ref('')
const imageDialogVisible = ref(false)
const imageLibrary = ref([])
const selectedNode = ref(null)

const outline = ref([])
const projectInfo = ref({})
const scoringCriteria = ref([])

const generationProgress = ref(0)
const generationStatus = ref('')
const generationMessage = ref('')

onMounted(() => {
    try {
        outline.value = JSON.parse(route.query.outline as string)
        projectInfo.value = JSON.parse(route.query.projectInfo as string)
        scoringCriteria.value = JSON.parse(route.query.scoringCriteria as string)

        // 如果有任务ID，自动开始检查生成状态
        const generationTaskId = route.query.generationTaskId as string
        if (generationTaskId) {
            generating.value = true
            generationProgress.value = 0
            generationStatus.value = 'processing'
            generationMessage.value = '正在生成标书...'
            checkGenerationProgress(generationTaskId)
        }
    } catch (error) {
        ElMessage.error('数据加载失败')
        router.push('/upload')
    }
})

const outlineTree = computed(() => {
    return outline.value.map(item => ({
        id: item.id,
        label: item.title,
        children: item.key_points.map((point, index) => ({
            id: `${item.id}-${index}`,
            label: point
        }))
    }))
})

const defaultProps = {
    children: 'children',
    label: 'label'
}

const handleNodeClick = (data: any) => {
    selectedNode.value = data
    // TODO: 加载对应节点的内容
}

const generateFullProposal = async () => {
    generating.value = true
    generationProgress.value = 0
    generationStatus.value = 'processing'
    generationMessage.value = '开始生成标书...'

    try {
        // 创建任务ID
        const taskId = `generate_${Date.now()}`

        // 发送生成请求
        const response = await axios.post('/api/generate-proposal', {
            outline: outline.value,
            projectInfo: projectInfo.value,
            scoringCriteria: scoringCriteria.value,
            task_id: taskId
        })

        // 开始轮询生成状态
        await checkGenerationStatus(taskId)

        // 获取生成的内容
        if (response.data && response.data.content) {
            content.value = response.data.content
            ElMessage.success('标书生成成功')
        } else {
            throw new Error('未能获取生成的标书内容')
        }
    } catch (error) {
        console.error('标书生成失败', error)
        ElMessage.error('标书生成失败：' + (error.message || '未知错误'))
        generationStatus.value = 'exception'
        generationMessage.value = '生成失败：' + (error.message || '未知错误')
    } finally {
        // 确保显示完成状态
        if (generationStatus.value !== 'exception') {
            generationProgress.value = 100
            generationStatus.value = 'success'
            generationMessage.value = '标书生成完成'
        }
        setTimeout(() => {
            generating.value = false
        }, 1000) // 延迟关闭进度条，让用户看到完成状态
    }
}

const checkGenerationStatus = async (taskId: string) => {
    return new Promise((resolve, reject) => {
        const checkStatus = async () => {
            try {
                const response = await axios.get(`/api/generation-status/${taskId}`)

                if (response.data && response.data.progress !== undefined) {
                    generationProgress.value = response.data.progress
                    generationStatus.value = response.data.status
                    generationMessage.value = response.data.message

                    if (response.data.status === 'processing') {
                        // 继续轮询
                        setTimeout(checkStatus, 1000)
                    } else if (response.data.status === 'error') {
                        reject(new Error(response.data.message || '生成失败'))
                    } else if (response.data.status === 'success') {
                        // 成功完成
                        resolve(true)
                    }
                } else {
                    // 返回数据格式不正确
                    reject(new Error('状态数据格式不正确'))
                }
            } catch (error) {
                console.error('获取生成状态失败', error)
                reject(error)
            }
        }

        // 开始检查状态
        checkStatus()
    })
}

const saveProposal = async () => {
    try {
        await axios.post('/api/save-proposal', {
            content: content.value,
            projectInfo: projectInfo.value
        })
        ElMessage.success('标书保存成功')
    } catch (error) {
        ElMessage.error('标书保存失败')
    }
}

const previewProposal = () => {
    previewContent.value = content.value
    previewVisible.value = true
}

const downloadProposal = async () => {
    try {
        const response = await axios.post('/api/download-proposal', {
            content: content.value,
            projectInfo: projectInfo.value
        }, {
            responseType: 'blob'
        })

        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${projectInfo.value.name}_标书.docx`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
    } catch (error) {
        ElMessage.error('下载失败')
    }
}

const aiContinue = async () => {
    try {
        const response = await axios.post('/api/ai-continue', {
            content: content.value,
            context: selectedNode.value
        })
        content.value += response.data.continuedContent
        ElMessage.success('AI续写完成')
    } catch (error) {
        ElMessage.error('AI续写失败')
    }
}

const aiExpand = async () => {
    try {
        const response = await axios.post('/api/ai-expand', {
            content: content.value,
            context: selectedNode.value
        })
        content.value = response.data.expandedContent
        ElMessage.success('AI扩写完成')
    } catch (error) {
        ElMessage.error('AI扩写失败')
    }
}

const aiPolish = async () => {
    try {
        const response = await axios.post('/api/ai-polish', {
            content: content.value,
            context: selectedNode.value
        })
        content.value = response.data.polishedContent
        ElMessage.success('AI润色完成')
    } catch (error) {
        ElMessage.error('AI润色失败')
    }
}

const insertImage = async () => {
    try {
        const response = await axios.get('/api/image-library')
        imageLibrary.value = response.data
        imageDialogVisible.value = true
    } catch (error) {
        ElMessage.error('获取图片库失败')
    }
}

const selectImage = (image: any) => {
    // TODO: 在编辑器中插入图片
    imageDialogVisible.value = false
}

const searchContent = async () => {
    try {
        const response = await axios.post('/api/search-content', {
            query: selectedNode.value?.label || '',
            context: content.value
        })
        // TODO: 显示搜索结果
        ElMessage.success('搜索完成')
    } catch (error) {
        ElMessage.error('搜索失败')
    }
}

// 检查生成进度并自动获取内容
const checkGenerationProgress = async (taskId: string) => {
    try {
        const statusResponse = await axios.get(`/api/generation-status/${taskId}`)

        if (statusResponse.data && statusResponse.data.progress !== undefined) {
            generationProgress.value = statusResponse.data.progress
            generationStatus.value = statusResponse.data.status
            generationMessage.value = statusResponse.data.message

            if (statusResponse.data.status === 'processing') {
                // 继续轮询
                setTimeout(() => checkGenerationProgress(taskId), 1000)
            } else if (statusResponse.data.status === 'error') {
                ElMessage.error('生成失败: ' + statusResponse.data.message)
                generating.value = false
            } else if (statusResponse.data.status === 'success') {
                // 成功完成后获取内容
                try {
                    const contentResponse = await axios.get(`/api/generation-result/${taskId}`)
                    if (contentResponse.data && contentResponse.data.content) {
                        content.value = contentResponse.data.content
                        ElMessage.success('标书已自动生成')
                    }
                } catch (contentError) {
                    console.error('获取生成内容失败', contentError)
                    ElMessage.warning('标书生成完成，但获取内容失败，请尝试重新生成')
                } finally {
                    setTimeout(() => {
                        generating.value = false
                    }, 1000)
                }
            }
        } else {
            // 返回数据格式不正确
            ElMessage.warning('状态数据格式不正确')
            generating.value = false
        }
    } catch (error) {
        console.error('获取生成状态失败', error)
        ElMessage.error('无法获取生成进度')
        generating.value = false
    }
}
</script>

<style scoped>
.proposal-editor {
    padding: 20px;
}

.editor-card {
    margin: 0 auto;
    max-width: 1200px;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.editor-container {
    display: flex;
    gap: 20px;
    margin-top: 20px;
}

.outline-panel {
    width: 250px;
    border-right: 1px solid #dcdfe6;
    padding-right: 20px;
}

.content-panel {
    flex: 1;
}

.toolbar {
    margin-bottom: 10px;
    display: flex;
    gap: 10px;
}

.preview-content {
    padding: 20px;
}

.image-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
}

.image-item {
    width: 150px;
    height: 150px;
    cursor: pointer;
    transition: transform 0.3s;
}

.image-item:hover {
    transform: scale(1.05);
}

.generation-progress {
    margin: 20px 0;
    text-align: center;
}

.progress-text {
    margin-top: 10px;
    color: #666;
}
</style>