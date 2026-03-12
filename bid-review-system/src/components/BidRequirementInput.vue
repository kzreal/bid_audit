<template>
  <div class="mb-6">
    <label class="block text-gray-700 text-sm font-medium mb-2">
      招标信息提取
    </label>

    <!-- 下拉框选择要求类型 -->
    <div class="mb-3">
      <select v-model="store.requirementType" @change="onRequirementTypeChange" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
        <option value="">请选择要求类型</option>
        <option :value="RequirementType.INFORMATION_CHECK">信息核对</option>
        <option :value="RequirementType.BIDDING_REQUIREMENT">招标要求</option>
        <option :value="RequirementType.GENERAL_REQUIREMENT">通用要求</option>
      </select>
    </div>

    <!-- 可编辑文本区域 -->
    <textarea
      class="text-editor w-full h-28 resize-none"
      v-model="store.requirementText"
      placeholder="在此粘贴或输入招标信息..."
    ></textarea>

    <!-- 底部操作栏 -->
    <div class="mt-2 flex justify-between items-center">
      <span class="text-xs text-gray-500">
        字符数: {{ store.requirementText.length }}
      </span>
      <button v-if="store.requirementText" @click="clearRequirementText"
              class="text-xs text-red-600 hover:text-red-800">
        清空
      </button>
    </div>

    <!-- 提示信息 -->
    <div v-if="store.requirementType" class="mt-2 p-2 bg-blue-50 text-blue-700 text-xs rounded">
      已选择: {{ getRequirementTypeName(store.requirementType) }}
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/appStore'
import { RequirementType } from '../types'

const store = useAppStore()

const clearRequirementText = () => {
  store.clearRequirement()
}

const getRequirementTypeName = (type) => {
  const typeMap = {
    [RequirementType.INFORMATION_CHECK]: '信息核对',
    [RequirementType.BIDDING_REQUIREMENT]: '招标要求',
    [RequirementType.GENERAL_REQUIREMENT]: '通用要求'
  }
  return typeMap[type] || type
}

const onRequirementTypeChange = () => {
  store.setRequirement(store.requirementType, store.requirementText)
}
</script>