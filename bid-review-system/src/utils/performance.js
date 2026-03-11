/**
 * 性能优化工具
 */

/**
 * 防抖函数
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function} 防抖后的函数
 */
export const debounce = (fn, delay = 300) => {
  let timeoutId
  return function (...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 要节流的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 节流后的函数
 */
export const throttle = (fn, limit = 300) => {
  let inThrottle
  return function (...args) {
    if (!inThrottle) {
      fn.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 虚拟滚动工具
 * @param {Array} items - 数据列表
 * @param {number} itemHeight - 每项高度
 * @param {number} containerHeight - 容器高度
 * @param {number} buffer - 缓冲区大小
 * @returns {Object} 虚拟滚动配置
 */
export const useVirtualScroll = (items, itemHeight = 50, containerHeight = 500, buffer = 5) => {
  const scrollTop = ref(0)
  const containerRef = ref(null)

  const visibleCount = Math.ceil(containerHeight / itemHeight) + buffer * 2
  const startIndex = Math.max(0, Math.floor(scrollTop.value / itemHeight) - buffer)
  const endIndex = Math.min(items.length - 1, startIndex + visibleCount - 1)

  const visibleItems = computed(() => {
    return items.slice(startIndex, endIndex + 1).map((item, index) => ({
      item,
      index: startIndex + index,
      style: {
        position: 'absolute',
        top: `${(startIndex + index) * itemHeight}px`,
        height: `${itemHeight}px`,
        width: '100%'
      }
    }))
  })

  const totalHeight = computed(() => items.length * itemHeight)
  const offsetY = computed(() => startIndex * itemHeight)

  const onScroll = throttle((e) => {
    scrollTop.value = e.target.scrollTop
  }, 16) // 60fps

  return {
    containerRef,
    visibleItems,
    totalHeight,
    offsetY,
    onScroll,
    startIndex,
    endIndex
  }
}

/**
 * 图片懒加载
 * @param {string} selector - 元素选择器
 * @param {number} threshold - 阈值
 */
export const lazyLoad = (selector = '[data-src]', threshold = 0.1) => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target
        const src = img.dataset.src
        if (src) {
          img.src = src
          img.removeAttribute('data-src')
          observer.unobserve(img)
        }
      }
    })
  }, { threshold })

  // 观察所有符合条件的元素
  document.querySelectorAll(selector).forEach(img => {
    observer.observe(img)
  })

  return observer
}

/**
 * 代码分割工具
 */
export const loadComponent = (componentFactory) => {
  return () => ({
    component: componentFactory(),
    loading: { template: '<div class="loading">加载中...</div>' },
    error: { template: '<div class="error">加载失败</div>' },
    delay: 200,
    timeout: 5000
  })
}

/**
 * 缓存工具
 */
export const SimpleCache = (maxSize = 100) => {
  const cache = new Map()
  const keys = new Set()

  return {
    get(key) {
      if (cache.has(key)) {
        // 更新访问顺序
        keys.delete(key)
        keys.add(key)
        return cache.get(key)
      }
      return null
    },

    set(key, value) {
      if (keys.size >= maxSize) {
        // 删除最久未使用的项
        const oldestKey = keys.values().next().value
        keys.delete(oldestKey)
        cache.delete(oldestKey)
      }
      keys.add(key)
      cache.set(key, value)
    },

    clear() {
      cache.clear()
      keys.clear()
    },

    size() {
      return cache.size
    }
  }
}

/**
 * 性能监控
 */
export const performanceMonitor = {
  metrics: {
    firstPaint: 0,
    firstContentfulPaint: 0,
    domInteractive: 0,
    loadComplete: 0
  },

  init() {
    // 监听性能指标
    if (window.performance) {
      window.addEventListener('load', () => {
        this.metrics.loadComplete = performance.now()
      })

      if (performance.getEntriesByType('navigation')[0]) {
        const navEntry = performance.getEntriesByType('navigation')[0]
        this.metrics.domInteractive = navEntry.domInteractive
      }
    }
  },

  mark(name) {
    if (window.performance) {
      performance.mark(name)
    }
  },

  measure(name, startMark, endMark) {
    if (window.performance) {
      performance.measure(name, startMark, endMark)
      const measures = performance.getEntriesByName(name)
      if (measures.length > 0) {
        return measures[measures.length - 1].duration
      }
    }
    return 0
  },

  getMetrics() {
    return this.metrics
  }
}

// 初始化性能监控
if (typeof window !== 'undefined') {
  performanceMonitor.init()
}