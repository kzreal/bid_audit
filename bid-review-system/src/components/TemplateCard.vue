<template>
  <div
    class="template-card bg-white rounded-xl border border-gray-100 p-5 shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300 cursor-pointer group"
    @click="$emit('apply', template.id)"
  >
    <!-- 标签区域 -->
    <div v-if="template.tags && template.tags.length > 0" class="flex flex-wrap gap-2 mb-3">
      <span
        v-for="tag in template.tags"
        :key="tag"
        :class="getTagColor(tag)"
        class="inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium"
      >
        {{ tag }}
      </span>
    </div>

    <!-- 标题 -->
    <h3 class="text-base font-semibold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">
      {{ template.name }}
    </h3>

    <!-- 描述 -->
    <p v-if="template.description" class="text-sm text-gray-500 mb-4 line-clamp-2">
      {{ template.description }}
    </p>

    <!-- 任务数量 -->
    <div class="flex items-center text-xs text-gray-400 mb-4">
      <svg class="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <span>{{ template.tasks?.length || 0 }} 个任务</span>
    </div>

    <!-- 操作按钮 -->
    <div class="flex items-center gap-2 pt-3 border-t border-gray-50">
      <button
        @click.stop="$emit('apply', template.id)"
        class="flex-1 bg-blue-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-1.5"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        应用
      </button>
      <button
        @click.stop="$emit('edit', template.id)"
        class="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
        title="编辑"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
      </button>
      <button
        @click.stop="$emit('delete', template.id)"
        class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
        title="删除"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  template: {
    type: Object,
    required: true
  }
})

defineEmits(['apply', 'edit', 'delete'])

// 根据标签获取颜色
function getTagColor(tag) {
  const colors = [
    'bg-blue-50 text-blue-700',
    'bg-purple-50 text-purple-700',
    'bg-green-50 text-green-700',
    'bg-orange-50 text-orange-700',
    'bg-pink-50 text-pink-700',
    'bg-cyan-50 text-cyan-700',
    'bg-indigo-50 text-indigo-700',
    'bg-amber-50 text-amber-700'
  ]
  // 基于标签内容生成一致的索引
  const index = tag.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length
  return colors[index]
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
