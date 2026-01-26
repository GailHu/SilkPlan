<template>
  <div class="upload-container">
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <span>招标文件上传</span>
        </div>
      </template>

      <el-upload class="upload-demo" drag :action="uploadUrl" :headers="headers" :on-success="handleSuccess"
        :on-error="handleError" :before-upload="beforeUpload" :file-list="fileList" accept=".pdf,.doc,.docx">
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 PDF、DOC、DOCX 格式文件
          </div>
        </template>
      </el-upload>

      <!-- 解析进度 -->
      <div v-if="parsing" class="parsing-progress">
        <el-progress :percentage="parsingProgress" :status="parsingStatus" />
        <p class="progress-text">{{ parsingMessage }}</p>
      </div>

      <div v-if="projectInfo" class="project-info">
        <h3>项目信息</h3>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">{{ projectInfo.name }}</el-descriptions-item>
          <el-descriptions-item label="项目类型">{{ projectInfo.type }}</el-descriptions-item>
          <el-descriptions-item label="预算金额">{{ projectInfo.budget }}</el-descriptions-item>
          <el-descriptions-item label="截止日期">{{ projectInfo.deadline }}</el-descriptions-item>
        </el-descriptions>

        <div class="requirements-section">
          <h4>主要要求</h4>
          <el-tag v-for="(req, index) in projectInfo.requirements" :key="index" class="requirement-tag">
            {{ req }}
          </el-tag>
        </div>
      </div>

      <!-- 评分标准 -->
      <div v-if="scoringCriteria.length > 0" class="scoring-criteria">
        <h3>评分标准</h3>
        <el-table :data="scoringCriteria" border style="width: 100%">
          <el-table-column prop="category" label="评分类别" width="120" />
          <el-table-column prop="item" label="评分项" width="150" />
          <el-table-column prop="score" label="分值" width="80" />
          <el-table-column prop="description" label="评分标准描述" />
          <el-table-column label="具体要求">
            <template #default="{ row }">
              <el-tag v-for="(req, index) in row.requirements" :key="index" class="requirement-tag">
                {{ req }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="editScoringCriteria(row)">
                编辑
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 评分标准编辑对话框 -->
      <el-dialog v-model="scoringDialogVisible" title="编辑评分标准" width="50%">
        <el-form :model="editingScoringCriteria" label-width="100px">
          <el-form-item label="评分类别">
            <el-input v-model="editingScoringCriteria.category" />
          </el-form-item>
          <el-form-item label="评分项">
            <el-input v-model="editingScoringCriteria.item" />
          </el-form-item>
          <el-form-item label="分值">
            <el-input-number v-model="editingScoringCriteria.score" :min="0" :max="100" />
          </el-form-item>
          <el-form-item label="评分标准描述">
            <el-input type="textarea" v-model="editingScoringCriteria.description" :rows="3" />
          </el-form-item>
          <el-form-item label="具体要求">
            <el-tag v-for="(req, index) in editingScoringCriteria.requirements" :key="index" closable
              @close="removeRequirement(index)">
              {{ req }}
            </el-tag>
            <el-input v-model="newRequirement" class="input-new-tag" size="small" @keyup.enter="addRequirement"
              @blur="addRequirement" />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="scoringDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveScoringCriteria">保存</el-button>
          </span>
        </template>
      </el-dialog>

      <div v-if="outline.length > 0" class="outline-section">
        <h3>标书大纲</h3>
        <el-checkbox-group v-model="selectedOutline">
          <el-card v-for="item in outline" :key="item.id" class="outline-item">
            <template #header>
              <div class="outline-header">
                <el-checkbox :label="item.id" :disabled="item.required">
                  {{ item.title }}
                </el-checkbox>
                <el-tag v-if="item.required" type="danger" size="small">必选</el-tag>
              </div>
            </template>
            <div class="outline-description">{{ item.description }}</div>
            <div class="key-points">
              <h4>关键点：</h4>
              <el-tag v-for="(point, index) in item.key_points" :key="index" class="key-point-tag" type="info">
                {{ point }}
              </el-tag>
            </div>
            <div v-if="!item.required" class="outline-custom">
              <el-input v-model="customContent[item.id]" type="textarea" :rows="2" placeholder="自定义内容（选填）" />
            </div>
          </el-card>
        </el-checkbox-group>

        <div class="action-buttons">
          <el-button type="primary" @click="generatePrompt" :loading="generating">
            生成提示词
          </el-button>
        </div>
      </div>

      <div v-if="generatedPrompt" class="prompt-section">
        <h3>生成的提示词</h3>
        <el-input type="textarea" :rows="6" v-model="generatedPrompt" readonly />
        <div class="action-buttons">
          <el-button type="primary" @click="startGeneration">
            进入编辑器
          </el-button>
          <el-button type="success" @click="startDirectGeneration" :loading="directGenerating">
            一键生成全文
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const fileList = ref([])
const projectInfo = ref(null)
const outline = ref([])
const scoringCriteria = ref([])
const selectedOutline = ref([])
const customContent = ref({})
const generatedPrompt = ref('')
const generating = ref(false)
const parsing = ref(false)
const parsingProgress = ref(0)
const parsingStatus = ref('')
const parsingMessage = ref('')
const scoringDialogVisible = ref(false)
const editingScoringCriteria = ref({})
const newRequirement = ref('')
const directGenerating = ref(false)
const generationTaskId = ref('')

const uploadUrl = 'http://localhost:5000/api/upload'

const headers = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const router = useRouter()

const beforeUpload = (file: File) => {
  const isLt16M = file.size / 1024 / 1024 < 16
  if (!isLt16M) {
    ElMessage.error('文件大小不能超过 16MB!')
    return false
  }
  parsing.value = true
  parsingProgress.value = 0
  parsingStatus.value = ''
  parsingMessage.value = '准备上传文件...'
  return true
}

const handleSuccess = (response: any) => {
  if (response.message) {
    ElMessage.success(response.message)
    projectInfo.value = response.project_info
    outline.value = response.outline
    scoringCriteria.value = response.scoring_criteria
    // 默认选中所有必选项
    selectedOutline.value = response.outline
      .filter(item => item.required)
      .map(item => item.id)

    // 如果有任务ID，轮询解析状态
    if (response.task_id) {
      parsing.value = true  // 确保设置为解析中状态
      parsingProgress.value = 10  // 初始化进度
      parsingStatus.value = 'processing'
      parsingMessage.value = '开始解析文件...'
      checkParsingStatus(response.task_id)
    } else {
      parsing.value = false
      parsingProgress.value = 100
      parsingStatus.value = 'success'
    }
  }
}

const handleError = (error: any) => {
  ElMessage.error('上传失败：' + (error.message || '未知错误'))
  parsing.value = false
  parsingStatus.value = 'error'
  parsingMessage.value = '上传失败'
}

const checkParsingStatus = async (taskId: string) => {
  try {
    const response = await axios.get(`/api/parsing-status/${taskId}`)

    if (response.data && response.data.progress !== undefined) {
      parsingProgress.value = response.data.progress
      parsingStatus.value = response.data.status
      parsingMessage.value = response.data.message

      if (response.data.status === 'processing') {
        // 继续轮询，每秒查询一次
        setTimeout(() => checkParsingStatus(taskId), 1000)
      } else if (response.data.status === 'error') {
        ElMessage.error('解析失败：' + response.data.message)
        parsing.value = false
      } else if (response.data.status === 'success') {
        // 成功完成
        parsing.value = false
        ElMessage.success('文件解析完成')
      }
    } else {
      // 返回数据格式不正确
      ElMessage.warning('状态数据格式不正确')
      parsing.value = false
    }
  } catch (error) {
    console.error('获取解析状态失败', error)
    parsing.value = false
    parsingStatus.value = 'exception'
    parsingMessage.value = '获取解析状态失败'
    ElMessage.error('无法获取解析进度')
  }
}

const editScoringCriteria = (criteria: any) => {
  editingScoringCriteria.value = { ...criteria }
  scoringDialogVisible.value = true
}

const addRequirement = () => {
  if (newRequirement.value) {
    if (!editingScoringCriteria.value.requirements) {
      editingScoringCriteria.value.requirements = []
    }
    editingScoringCriteria.value.requirements.push(newRequirement.value)
    newRequirement.value = ''
  }
}

const removeRequirement = (index: number) => {
  editingScoringCriteria.value.requirements.splice(index, 1)
}

const saveScoringCriteria = () => {
  const index = scoringCriteria.value.findIndex(
    item => item.id === editingScoringCriteria.value.id
  )
  if (index !== -1) {
    scoringCriteria.value[index] = { ...editingScoringCriteria.value }
  }
  scoringDialogVisible.value = false
  ElMessage.success('评分标准已更新')
}

const generatePrompt = () => {
  generating.value = true
  try {
    // 构建提示词
    let prompt = `请根据以下要求生成标书内容：\n\n`
    prompt += `项目信息：\n`
    prompt += `- 项目名称：${projectInfo.value.name}\n`
    prompt += `- 项目类型：${projectInfo.value.type}\n`
    prompt += `- 预算金额：${projectInfo.value.budget}\n`
    prompt += `- 截止日期：${projectInfo.value.deadline}\n`
    prompt += `- 主要要求：${projectInfo.value.requirements.join('、')}\n\n`

    prompt += `需要包含以下章节：\n`
    outline.value
      .filter(item => selectedOutline.value.includes(item.id))
      .forEach(item => {
        prompt += `- ${item.title}：${item.description}\n`
        prompt += `  关键点：${item.key_points.join('、')}\n`
        if (customContent.value[item.id]) {
          prompt += `  自定义要求：${customContent.value[item.id]}\n`
        }
      })

    generatedPrompt.value = prompt
    ElMessage.success('提示词生成成功')
  } catch (error) {
    ElMessage.error('生成提示词失败')
  } finally {
    generating.value = false
  }
}

const startGeneration = () => {
  router.push({
    name: 'editor',
    query: {
      outline: JSON.stringify(outline.value),
      projectInfo: JSON.stringify(projectInfo.value),
      scoringCriteria: JSON.stringify(scoringCriteria.value)
    }
  })
}

const startDirectGeneration = async () => {
  try {
    directGenerating.value = true

    // 创建任务ID
    const taskId = `generate_${Date.now()}`
    generationTaskId.value = taskId

    // 发送生成请求
    await axios.post('/api/generate-proposal', {
      outline: outline.value,
      projectInfo: projectInfo.value,
      scoringCriteria: scoringCriteria.value,
      task_id: taskId
    })

    // 直接跳转到编辑器并带上任务ID参数
    router.push({
      name: 'editor',
      query: {
        outline: JSON.stringify(outline.value),
        projectInfo: JSON.stringify(projectInfo.value),
        scoringCriteria: JSON.stringify(scoringCriteria.value),
        generationTaskId: generationTaskId.value
      }
    })
  } catch (error) {
    ElMessage.error('启动生成失败：' + (error.message || '未知错误'))
  } finally {
    directGenerating.value = false
  }
}
</script>

<style scoped>
.upload-container {
  padding: 20px;
}

.upload-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.project-info {
  margin-top: 20px;
}

.requirements-section {
  margin-top: 20px;
}

.requirement-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.outline-section {
  margin-top: 20px;
}

.outline-item {
  margin-bottom: 10px;
}

.outline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.outline-description {
  color: #666;
  font-size: 14px;
  margin: 10px 0;
}

.key-points {
  margin: 10px 0;
}

.key-point-tag {
  margin-right: 10px;
  margin-bottom: 10px;
}

.outline-custom {
  margin-top: 10px;
}

.action-buttons {
  margin-top: 20px;
  text-align: center;
}

.prompt-section {
  margin-top: 20px;
}

.parsing-progress {
  margin: 20px 0;
  text-align: center;
}

.progress-text {
  margin-top: 10px;
  color: #666;
}

.scoring-criteria {
  margin-top: 20px;
}

.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}
</style>