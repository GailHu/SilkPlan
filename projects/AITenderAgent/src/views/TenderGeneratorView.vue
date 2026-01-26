<template>
  <div class="generator-container">
    <el-card class="generator-card">
      <template #header>
        <div class="card-header">
          <span>标书生成</span>
        </div>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="项目名称">
          <el-input v-model="form.projectName" placeholder="请输入项目名称" />
        </el-form-item>

        <el-form-item label="生成方式">
          <el-radio-group v-model="form.generationType">
            <el-radio label="score">根据评分标准生成</el-radio>
            <el-radio label="template">使用历史模板</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="标题样式">
          <el-select v-model="form.titleStyle" placeholder="请选择标题样式">
            <el-option label="样式一" value="style1" />
            <el-option label="样式二" value="style2" />
            <el-option label="样式三" value="style3" />
          </el-select>
        </el-form-item>

        <el-form-item label="大纲编辑">
          <el-button type="primary" @click="showOutlineEditor">编辑大纲</el-button>
        </el-form-item>

        <el-form-item label="生成方式">
          <el-radio-group v-model="form.generationMode">
            <el-radio label="full">一键生成全文</el-radio>
            <el-radio label="step">逐条生成</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="generateTender" :loading="generating">
            开始生成
          </el-button>
        </el-form-item>
      </el-form>

      <el-dialog v-model="outlineDialogVisible" title="大纲编辑" width="60%">
        <div class="outline-editor">
          <el-tree
            :data="outlineData"
            node-key="id"
            draggable
            :allow-drop="allowDrop"
            @node-drop="handleDrop"
          >
            <template #default="{ node, data }">
              <div class="custom-tree-node">
                <span>{{ data.label }}</span>
                <span>
                  <el-button type="text" @click="append(data)">添加</el-button>
                  <el-button type="text" @click="remove(node, data)">删除</el-button>
                </span>
              </div>
            </template>
          </el-tree>
        </div>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="outlineDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="saveOutline">保存</el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const form = reactive({
  projectName: '',
  generationType: 'score',
  titleStyle: 'style1',
  generationMode: 'full'
})

const generating = ref(false)
const outlineDialogVisible = ref(false)
const outlineData = ref([
  {
    id: 1,
    label: '第一章 项目概述',
    children: [
      {
        id: 2,
        label: '1.1 项目背景'
      },
      {
        id: 3,
        label: '1.2 项目目标'
      }
    ]
  }
])

const showOutlineEditor = () => {
  outlineDialogVisible.value = true
}

const allowDrop = (draggingNode: any, dropNode: any, type: string) => {
  return type !== 'inner'
}

const handleDrop = (draggingNode: any, dropNode: any, dropType: string) => {
  console.log('drop', draggingNode, dropNode, dropType)
}

const append = (data: any) => {
  const newChild = { id: Date.now(), label: '新节点' }
  if (!data.children) {
    data.children = []
  }
  data.children.push(newChild)
}

const remove = (node: any, data: any) => {
  const parent = node.parent
  const children = parent.data.children || parent.data
  const index = children.findIndex((d: any) => d.id === data.id)
  children.splice(index, 1)
}

const saveOutline = () => {
  ElMessage.success('大纲保存成功')
  outlineDialogVisible.value = false
}

const generateTender = async () => {
  generating.value = true
  try {
    const response = await axios.post('/api/generate', {
      ...form,
      outline: outlineData.value
    })
    ElMessage.success('标书生成成功')
    // 处理生成结果
  } catch (error) {
    ElMessage.error('标书生成失败')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.generator-container {
  padding: 20px;
}

.generator-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}

.outline-editor {
  height: 400px;
  overflow-y: auto;
}
</style> 