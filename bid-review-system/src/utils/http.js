import axios from 'axios'

// 创建 axios 实例
// 开发环境使用代理，baseURL 设为空，请求通过 Vite 代理转发到本地后端
const http = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 添加 API key
    if (config.url.includes('/hiagent/')) {
      config.headers['Authorization'] = `Bearer ${getApiKey(config.url)}`
    }

    // 添加请求时间戳（防止缓存）
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    const { data } = response

    // hiagent API 返回纯文本，直接返回
    if (response.config.url?.includes('/hiagent/')) {
      return data
    }

    // 其他 API 返回格式为 { code: 200, data: {}, message: '' }
    if (typeof data === 'object' && data.code !== undefined) {
      if (data.code === 200) {
        return data.data
      } else {
        // 非 200 状态码
        const error = new Error(data.message || '请求失败')
        error.code = data.code
        throw error
      }
    }

    // 其他情况直接返回数据
    return data
  },
  (error) => {
    // 处理 HTTP 错误
    let message = '网络请求失败'

    if (error.response) {
      // 服务器返回了错误状态码
      const { status, data } = error.response
      switch (status) {
        case 400:
          message = data.message || '请求参数错误'
          break
        case 401:
          message = '认证失败，请检查 API key'
          break
        case 403:
          message = '权限不足'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 429:
          message = '请求过于频繁，请稍后再试'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data.message || `请求失败 (${status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请检查网络连接'
    }

    const err = new Error(message)
    err.code = error.code || 'NETWORK_ERROR'
    err.originalError = error

    return Promise.reject(err)
  }
)

// 根据 URL 获取对应的 API key
function getApiKey(url) {
  if (url.includes('/generate-tasks')) {
    return import.meta.env.VITE_HIAGENT_API_KEY
  } else if (url.includes('/review-task')) {
    return import.meta.env.VITE_HIAGENT_REVIEW_API_KEY
  }
  return import.meta.env.VITE_HIAGENT_API_KEY
}

// 请求重试机制
export const retryRequest = async (requestFn, maxRetries = 3, delay = 1000) => {
  let lastError

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error

      // 如果是认证错误，不再重试
      if (error.code === 401) {
        throw error
      }

      // 如果是网络错误或服务器错误，进行重试
      if (error.code === 'NETWORK_ERROR' || error.code === 500 || error.code === 429) {
        const waitTime = delay * Math.pow(2, i) // 指数退避
        await new Promise(resolve => setTimeout(resolve, waitTime))
        continue
      }

      // 其他错误直接抛出
      throw error
    }
  }

  throw lastError
}

export default http