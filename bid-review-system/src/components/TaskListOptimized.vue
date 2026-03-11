<template>
  <div>
    <!-- 空状态 -->
    <div v-if="filteredTasks.length === 0" class="p-8 text-center text-gray-500">
      <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
      </svg>
      <p>{{ tasks.length === 0 ? '暂无任务' : '没有符合条件的任务' }}</p>
      <p class="text-sm mt-2">{{ tasks.length === 0 ? '请在左侧输入招标信息和投标文件后点击"开始分析"' : '请调整筛选条件' }}</p>
    </div>

    <!-- 虚拟滚动容器 -->
    <div
      ref="scrollContainer"
      class="overflow-y-auto"
      :style="{ height: virtualScroll ? '600px' : 'auto' }"
      @scroll="handleScroll"
    >
      <div :style="{ height: virtualScroll ? totalHeight + 'px' : 'auto' }">
        <!-- 任务项 -->
        <transition-group name="fade" tag="div" class="p-4 space-y-3">
          <div
            v-for="item in visibleItems"
            :key="item.index"
            :class="[
              'task-card',
              { active: selectedTaskId === tasks[item.index]?.id }
            ]"
            :style="item.style"
            @click="selectTask(tasks[item.index])"
          >
            <div class="flex justify-between items-start mb-2">
              <div class="flex-1 pr-4">
                <h3 class="font-medium text-gray-800">{{ item.item.title }}</h3>
                <p class="text-xs text-gray-400 mt-1">任务 {{ item.item.id }}</p>
              </div>
              <span class="text-xs text-gray-400 flex-shrink-0">
                {{ formatDate(item.item.createdAt) }}
              </span>
            </div>

            <p class="text-sm text-gray-600 mb-3 line-clamp-2">{{ item.item.description }}</p>

            <!-- 状态和操作 -->
            <div class="flex justify-between items-center">
              <div class="flex items-center">
                <span v-if="!item.item.review" class="text-xs text-gray-500">
                  <span class="inline-block w-2 h-2 bg-gray-400 rounded-full mr-1"></span>
                  待审核
                </span>
                <span v-else :class="['text-xs', getStatusClass(item.item.review.status)]">
                  <span class="inline-block w-2 h-2 rounded-full mr-1" :class="getStatusBg(item.item.review.status)"></span>
                  {{ item.item.review.status }}
                </span>
              </div>

              <div class="flex items-center gap-2">
                <button
                  v-if="!item.item.review"
                  @click.stop="startReview(item.item)"
                  :disabled="store.loading && store.selectedTaskId === item.item.id"
                  class="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  <span v-if="store.loading && store.selectedTaskId === item.item.id" class="inline-flex items-center">
                    <div class="loader mr-1"></div>
                    审核中
                  </span>
                  <span v-else>开始审核</span>
                </button>
                <span v-if="item.item.review" class="text-xs text-gray-400">
                  已审核
                </span>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
    </div>

    <!-- 加载更多 -->
    <div v-if="hasMore && !virtualScroll" class="p-4 text-center">
      <button
        @click="loadMore"
        :disabled="loadingMore"
        class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <span v-if="loadingMore" class="inline-flex items-center">
          <div class="loader mr-2"></div>
          加载中...
        </span>
        <span v-else>加载更多</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAppStore } from '../stores/appStore'
import { throttle } from '../utils/performance'

const props = defineProps({
  tasks: {
    type: Array,
    required: true
  },
  selectedTaskId: {
    type: Number,
    default: null
  },
  selectedFilter: {
    type: String,
    default: 'all'
  },
  virtualScroll: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select-task', 'start-review'])

const store = useAppStore()

// 虚拟滚动相关
const scrollContainer = ref(null)
const scrollTop = ref(0)
const itemHeight = 120 // 每个任务项的高度
const containerHeight = ref(600)
const bufferSize = 5

// 计算筛选后的任务
const filteredTasks = computed(() => {
  if (!props.selectedFilter || props.selectedFilter === 'all') {
    return props.tasks
  }

  switch (props.selectedFilter) {
    case 'pending':
      return props.tasks.filter(task => !task.review)
    case 'reviewed':
      return props.tasks.filter(task => task.review)
    case 'pass':
      return props.tasks.filter(task => task.review?.status === '通过')
    case 'fail':
      return props.tasks.filter(task => task.review?.status === '不通过')
    case 'pending-review':
      return props.tasks.filter(task => task.review?.status === '待确认')
    default:
      return props.tasks
  }
})

// 虚拟滚动计算
const visibleCount = computed(() => Math.ceil(containerHeight.value / itemHeight) + bufferSize * 2)
const startIndex = computed(() => Math.max(0, Math.floor(scrollTop.value / itemHeight) - bufferSize))
const endIndex = computed(() => Math.min(filteredTasks.value.length - 1, startIndex.value + visibleCount.value - 1))

const visibleItems = computed(() => {
  return filteredTasks.value.slice(startIndex.value, endIndex.value + 1).map((task, index) => ({
    task,
    index: startIndex.value + index,
    style: {
      position: 'absolute',
      top: `${(startIndex.value + index) * itemHeight}px`,
      height: `${itemHeight}px`,
      width: '100%'
    }
  }))
})

const totalHeight = computed(() => filteredTasks.value.length * itemHeight)

// 加载更多
const displayedCount = ref(20)
const loadingMore = ref(false)
const hasMore = computed(() => displayedCount.value < filteredTasks.value.length)

const loadMore = () => {
  loadingMore.value = true
  setTimeout(() => {
    displayedCount.value = Math.min(displayedCount.value + 20, filteredTasks.value.length)
    loadingMore.value = false
  }, 300)
}

// 滚动处理
const handleScroll = throttle((e) => {
  scrollTop.value = e.target.scrollTop
}, 16)

// 获取容器高度
const updateContainerHeight = () => {
  if (scrollContainer.value) {
    containerHeight.value = scrollContainer.value.clientHeight
  }
}

onMounted(() => {
  updateContainerHeight()
  window.addEventListener('resize', updateContainerHeight)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateContainerHeight)
})

// 其他方法
const getStatusClass = (status) => {
  const statusMap = {
    '通过': 'text-green-600',
    '不通过': 'text-red-600',
    '待确认': 'text-yellow-600'
  }
  return statusMap[status] || 'text-gray-600'
}

const getStatusBg = (status) => {
  const statusMap = {
    '通过': 'bg-green-500',
    '不通过': 'bg-red-500',
    '待确认': 'bg-yellow-500'
  }
  return statusMap[status] || 'bg-gray-400'
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN')
}

const selectTask = (task) => {
  emit('select-task', task.id)
}

const startReview = (task) => {
  emit('start-review', task)
}
</script>

<style scoped>
.loader {
  border: 2px solid #f3f4f6;
  border-top: 2px solid #2563eb;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>