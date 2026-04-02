<template>
  <div class="mb-5">
    <div class="flex items-center justify-between mb-2.5">
      <label class="flex items-center gap-2 text-black text-xs font-semibold">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        审核要求
      </label>
      <button v-if="store.requirementText" @click="clearRequirementText"
              class="text-xs text-gray-500 hover:text-black transition-colors flex items-center gap-1">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
        </svg>
        清空
      </button>
    </div>

    <!-- 可编辑文本区域 - Vercel 风格 -->
    <div class="relative">
      <textarea
        class="text-editor w-full h-28 resize-none"
        v-model="store.requirementText"
        placeholder="在此输入招标文件中的相关要求或你的审核要求"
      ></textarea>

      <!-- 底部操作栏 -->
      <div class="absolute bottom-2.5 left-3 right-3 flex justify-between items-center">
        <span class="text-xs text-gray-400">
          {{ store.requirementText.length }} 字符
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAppStore } from '../stores/appStore'

const store = useAppStore()

const clearRequirementText = () => {
  store.clearRequirement()
}
</script>
