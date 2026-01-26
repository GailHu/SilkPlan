<template>
  <div class="editor-container">
    <el-card class="editor-card">
      <template #header>
        <div class="card-header">
          <span>标书编辑器</span>
          <div class="header-actions">
            <el-button type="primary" @click="saveTender">保存</el-button>
            <el-button @click="previewTender">预览</el-button>
            <el-button @click="downloadTender">下载</el-button>
          </div>
        </div>
      </template>

      <div class="editor-toolbar">
        <el-button-group>
          <el-button @click="aiContinue">AI续写</el-button>
          <el-button @click="aiExpand">AI扩写</el-button>
          <el-button @click="aiPolish">AI润色</el-button>
        </el-button-group>
        <el-button-group>
          <el-button @click="insertImage">插入图片</el-button>
          <el-button @click="searchOnline">联网搜索</el-button>
        </el-button-group>
      </div>

      <div class="editor-content">
        <Editor
          v-model="content"
          :init="editorInit"
          :disabled="false"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import Editor from '@tinymce/tinymce-vue'
import axios from 'axios'

const content = ref('')
const editorInit = {
  height: 500,
  menubar: false,
  plugins: [
    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
    'insertdatetime', 'media', 'table', 'code', 'help', 'wordcount'
  ],
  toolbar: 'undo redo | blocks | ' +
    'bold italic forecolor | alignleft aligncenter ' +
    'alignright alignjustify | bullist numlist outdent indent | ' +
    'removeformat | help',
  content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }'
}

const saveTender = async () => {
  try {
    await axios.post('/api/save', { content: content.value })
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const previewTender = () => {
  // 实现预览逻辑
  window.open('/preview', '_blank')
}

const downloadTender = async () => {
  try {
    const response = await axios.post('/api/download', { content: content.value }, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '标书.docx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const aiContinue = async () => {
  try {
    const response = await axios.post('/api/ai/continue', { content: content.value })
    content.value += response.data.continuedText
  } catch (error) {
    ElMessage.error('AI续写失败')
  }
}

const aiExpand = async () => {
  try {
    const response = await axios.post('/api/ai/expand', { content: content.value })
    content.value = response.data.expandedText
  } catch (error) {
    ElMessage.error('AI扩写失败')
  }
}

const aiPolish = async () => {
  try {
    const response = await axios.post('/api/ai/polish', { content: content.value })
    content.value = response.data.polishedText
  } catch (error) {
    ElMessage.error('AI润色失败')
  }
}

const insertImage = () => {
  // 实现插入图片逻辑
}

const searchOnline = () => {
  // 实现联网搜索逻辑
}
</script>

<style scoped>
.editor-container {
  padding: 20px;
}

.editor-card {
  max-width: 1200px;
  margin: 0 auto;
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

.editor-toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 20px;
}

.editor-content {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}
</style> 