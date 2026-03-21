<template>
  <teleport to="body">
    <!-- 遮罩层 -->
    <transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
        @click="$emit('close')"
      ></div>
    </transition>

    <!-- 抽屉 -->
    <transition name="slide">
      <div
        v-if="open"
        class="fixed inset-y-0 right-0 w-[480px] bg-white shadow-2xl z-50 flex flex-col"
      >
        <!-- 头部 -->
        <header class="border-b border-gray-100 p-5 flex-shrink-0">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div>
                <h2 class="text-lg font-semibold text-gray-800">模版库</h2>
                <p class="text-xs text-gray-400 mt-0.5">快速应用或管理审核模版</p>
              </div>
            </div>
            <button
              @click="$emit('close')"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <!-- 搜索框 -->
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索模版..."
              class="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all"
            >
          </div>
        </header>

        <!-- 标签筛选 -->
        <div class="px-5 py-4 border-b border-gray-100 flex-shrink-0">
          <div class="flex items-center gap-2 mb-3">
            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
            </svg>
            <span class="text-xs font-medium text-gray-600">标签筛选</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="tag in allTags"
              :key="tag"
              @click="toggleTag(tag)"
              :class="selectedTags.includes(tag) ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
            >
              {{ tag }}
            </button>
            <button
              v-if="selectedTags.length > 0"
              @click="clearTags"
              class="px-3 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            >
              清除
            </button>
          </div>
        </div>

        <!-- 模版列表 -->
        <div class="flex-1 overflow-y-auto p-5">
          <transition name="fade" mode="out-in">
            <div v-if="filteredTemplates.length === 0" class="text-center py-12">
              <div class="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gray-50 flex items-center justify-center">
                <svg class="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <p class="text-sm text-gray-400">没有找到匹配的模版</p>
            </div>
            <div v-else class="grid grid-cols-1 gap-4">
              <template-card
                v-for="template in filteredTemplates"
                :key="template.id"
                :template="template"
                @apply="$emit('apply', $event)"
                @edit="$emit('edit', $event)"
                @delete="handleDelete($event)"
              />
            </div>
          </transition>
        </div>

        <!-- 底部按钮 -->
        <footer class="p-5 border-t border-gray-100 flex-shrink-0">
          <button
            @click="$emit('create-template')"
            class="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-xl font-semibold shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/30 transition-all duration-300 hover:-translate-y-0.5 active:translate-y-0 flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            新建模版
          </button>
        </footer>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { getAllTags } from '../services/templateService'
import TemplateCard from './TemplateCard.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  templates: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'create-template', 'apply', 'edit', 'delete'])

// 搜索查询
const searchQuery = ref('')

// 选中的标签
const selectedTags = ref([])

// 所有标签
const allTags = computed(() => {
  const tagSet = new Set()
  props.templates.forEach(template => {
    template.tags?.forEach(tag => tagSet.add(tag))
  })
  return Array.from(tagSet).sort()
})

// 过滤后的模版
const filteredTemplates = computed(() => {
  // 直接使用 props.templates 进行筛选
  const templatesToFilter = props.templates

  return templatesToFilter.filter(template => {
    // 关键词搜索
    const matchesQuery = !searchQuery.value ||
      template.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      (template.description && template.description.toLowerCase().includes(searchQuery.value.toLowerCase()))

    // 标签筛选
    const matchesTags = selectedTags.value.length === 0 ||
      selectedTags.value.every(tag => template.tags && template.tags.includes(tag))

    return matchesQuery && matchesTags
  })
})

// 切换标签
function toggleTag(tag) {
  const index = selectedTags.value.indexOf(tag)
  if (index === -1) {
    selectedTags.value.push(tag)
  } else {
    selectedTags.value.splice(index, 1)
  }
}

// 清除标签
function clearTags() {
  selectedTags.value = []
}

// 处理删除
function handleDelete(id) {
  emit('delete', id)
}

// 监听 open 变化，重置状态
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    searchQuery.value = ''
    selectedTags.value = []
  }
})

// 监听 templates 变化，更新筛选（确保创建/删除后立即显示变化）
// 已移除 watch，filteredTemplates 直接依赖 props.templates 会自动响应变化

</script>

<style scoped>
/* 淡入淡出 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 侧滑 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease-in-out;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>
