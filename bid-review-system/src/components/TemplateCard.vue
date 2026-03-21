<template>
  <div
    class="card-vercel p-4 cursor-pointer group"
    @click="$emit('apply', template.id)"
  >
    <!-- 标签区域 - Vercel 风格 -->
    <div v-if="template.tags && template.tags.length > 0" class="flex flex-wrap gap-2 mb-2.5">
      <span
        v-for="tag in template.tags"
        :key="tag"
        class="px-2 py-0.5 rounded-vercel-sm text-xs font-medium bg-gray-100 text-black"
      >
        {{ tag }}
      </span>
    </div>

    <!-- 标题 -->
    <h3 class="text-sm font-semibold text-black mb-2 group-hover:text-vercel-blue transition-colors">
      {{ template.name }}
    </h3>

    <!-- 描述 -->
    <p v-if="template.description" class="text-sm text-gray-600 mb-3 line-clamp-2">
      {{ template.description }}
    </p>

    <!-- 任务数量 -->
    <div class="flex items-center text-xs text-gray-500 mb-3">
      <svg class="w-3.5 h-3.5 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <span>{{ template.tasks?.length || 0 }} 个任务</span>
    </div>

    <!-- 操作按钮 - Vercel 风格 -->
    <div class="flex items-center gap-2 pt-2.5 border-t border-gray-100">
      <button
        @click.stop="$emit('apply', template.id)"
        class="flex-1 bg-vercel-blue text-white py-2 px-3 rounded-vercel-sm text-sm font-medium transition-all duration-200 hover:bg-vercel-blue-hover focus:outline-none focus:ring-2 focus:ring-vercel-blue-light flex items-center justify-center gap-1.5"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"></path>
        </svg>
        应用
      </button>
      <button
        @click.stop="$emit('edit', template.id)"
        class="p-2 text-gray-500 hover:text-black hover:bg-gray-100 rounded-vercel-sm transition-colors"
        title="编辑"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5a2 2 0 00-2-2h-2M11 5a2 2 0 002 2h2a2 2 0 002-2v-2.828l8.586-8.586a2 2 0 002.828 15H9v-2.828l8.586-8.586z"></path>
        </svg>
      </button>
      <button
        @click.stop="$emit('delete', template.id)"
        class="p-2 text-gray-500 hover:text-black hover:bg-gray-100 rounded-vercel-sm transition-colors"
        title="删除"
      >
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
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
</script>

<style scoped>
/* 极简卡片 - Vercel 风格 */
.card-vercel {
  background: white;
  border: 1px solid #eaeaea;
  border-radius: 2px;
  transition: border-color 200ms ease-out;
}

.card-vercel:hover {
  border-color: #0070f3;
}

/* 文本截断 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
