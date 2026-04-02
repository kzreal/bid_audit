<template>
  <div class="tag-selector">
    <div class="flex items-center gap-2 mb-3">
      <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
      </svg>
      <span class="text-xs font-medium text-gray-600">标签</span>
    </div>

    <!-- 已选标签 -->
    <div v-if="modelValue.length > 0" class="flex flex-wrap gap-2 mb-3">
      <span
        v-for="(tag, index) in modelValue"
        :key="index"
        @click="removeTag(index)"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-50 text-blue-700 cursor-pointer hover:bg-blue-100 transition-colors"
      >
        {{ tag }}
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      </span>
    </div>

    <!-- 添加新标签 -->
    <div class="flex items-center gap-2">
      <input
        v-model="newTagInput"
        type="text"
        placeholder="添加标签..."
        class="flex-1 px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
        @keyup.enter="addNewTag"
      >
      <button
        @click="addNewTag"
        class="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        :disabled="!newTagInput.trim()"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
      </button>
    </div>

    <!-- 可选标签建议 -->
    <div v-if="showSuggestions && suggestedTags.length > 0" class="mt-3">
      <p class="text-xs text-gray-400 mb-2">常用标签</p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="tag in suggestedTags"
          :key="tag"
          @click="selectSuggestedTag(tag)"
          class="px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
        >
          {{ tag }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  tags: {
    type: Array,
    default: () => []
  },
  allowCreate: {
    type: Boolean,
    default: true
  },
  showSuggestions: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

// 新标签输入
const newTagInput = ref('')

// 建议标签（排除已选标签）
const suggestedTags = computed(() => {
  return props.tags.filter(tag => !props.modelValue.includes(tag))
})

// 添加新标签
function addNewTag() {
  const tag = newTagInput.value.trim()
  if (tag && !props.modelValue.includes(tag)) {
    emit('update:modelValue', [...props.modelValue, tag])
    newTagInput.value = ''
  }
}

// 移除标签
function removeTag(index) {
  const newTags = [...props.modelValue]
  newTags.splice(index, 1)
  emit('update:modelValue', newTags)
}

// 选择建议标签
function selectSuggestedTag(tag) {
  if (!props.modelValue.includes(tag)) {
    emit('update:modelValue', [...props.modelValue, tag])
  }
}
</script>

<style scoped>
/* 聚焦样式 */
input:focus {
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}
</style>
