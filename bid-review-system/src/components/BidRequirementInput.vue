<template>
  <div class="mb-6">
    <div class="flex items-center justify-between mb-3">
      <label class="flex items-center gap-2 text-gray-800 text-sm font-semibold">
        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        招标信息提取
      </label>
      <button v-if="store.requirementText" @click="clearRequirementText"
              class="text-xs text-gray-400 hover:text-red-600 transition-colors flex items-center gap-1">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
        </svg>
        清空
      </button>
    </div>

    <!-- 下拉框选择要求类型 -->
    <div class="mb-4">
      <select
        v-model="store.requirementType"
        @change="onRequirementTypeChange"
        class="w-full px-4 py-3 bg-white border border-gray-200 rounded-xl text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 appearance-none cursor-pointer hover:border-gray-300"
      >
        <option value="">请选择要求类型</option>
        <option :value="RequirementType.INFORMATION_CHECK">信息核对</option>
        <option :value="RequirementType.BIDDING_REQUIREMENT">招标要求</option>
        <option :value="RequirementType.GENERAL_REQUIREMENT">通用要求</option>
      </select>
      <!-- 自定义箭头 -->
      <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
        <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </div>
    </div>

    <!-- 可编辑文本区域 -->
    <div class="relative">
      <textarea
        class="text-editor w-full h-36 resize-none text-gray-700 text-sm leading-relaxed"
        v-model="store.requirementText"
        placeholder="在此粘贴或输入招标信息..."
      ></textarea>

      <!-- 底部操作栏 -->
      <div class="absolute bottom-3 left-4 right-4 flex justify-between items-center">
        <span class="text-xs text-gray-400">
          {{ store.requirementText.length }} 字符
        </span>
      </div>
    </div>

    <!-- 提示信息 -->
    <transition name="fade-up">
      <div v-if="store.requirementType" class="mt-3 p-3 bg-blue-50 border border-blue-100 text-blue-700 text-xs rounded-xl flex items-center gap-2">
        <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>已选择: <strong>{{ getRequirementTypeName(store.requirementType) }}</strong></span>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* 下拉框容器样式 */
.select-wrapper {
  position: relative;
}

/* 淡入上滑过渡 */
.fade-up-enter-active {
  transition: all 0.2s ease-out;
}

.fade-up-leave-active {
  transition: all 0.15s ease-in;
}

.fade-up-enter-from {
  opacity: 0;
  transform: translateY(5px);
}

.fade-up-leave-to {
  opacity: 0;
  transform: translateY(5px);
}
</style>

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