import axios, { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'

// Mock API 类型声明 - 使用动态导入避免类型检查
const mockAPI = (await import('../mock/server.js' as any)).mockAPI

// 扩展 ImportMeta 接口
declare global {
  interface ImportMeta {
    env: {
      VITE_USE_MOCK?: string
      VITE_API_BASE_URL?: string
    }
  }
}

// 检查是否使用 Mock 模式
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001',
  timeout: 180000, // 3分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// Mock 请求处理器
const mockRequest = async (config: InternalAxiosRequestConfig): Promise<any> => {
  const { method, url, data } = config
  const path = url?.replace('/api', '').split('?')[0] || ''

  try {
    let result

    // 根据路径和方法路由到对应的 mock 函数
    // 认证相关
    if (path === '/auth/login' && method === 'post') {
      result = await mockAPI.auth.login(data.email, data.password)
    } else if (path === '/auth/register' && method === 'post') {
      result = await mockAPI.auth.register(data)
    } else if (path === '/auth/logout' && method === 'post') {
      result = await mockAPI.auth.logout()
    } else if (path === '/auth/profile' && method === 'get') {
      result = await mockAPI.auth.getProfile()
    } else if (path === '/auth/profile' && method === 'put') {
      result = await mockAPI.auth.updateProfile(data)
    } else if (path === '/auth/refresh' && method === 'post') {
      result = await mockAPI.auth.refreshToken()
    }
    // 文档相关
    else if (path === '/documents' && method === 'get') {
      const params = new URLSearchParams(url?.split('?')[1] || '')
      result = await mockAPI.documents.getList(Object.fromEntries(params))
    } else if (path === '/documents/page' && method === 'get') {
      const params = new URLSearchParams(url?.split('?')[1] || '')
      result = await mockAPI.documents.getPage(Object.fromEntries(params))
    } else if (path.startsWith('/documents/') && method === 'get' && !path.includes('cluster_analysis') && !path.includes('get_documents_by_source_id')) {
      const id = parseInt(path.split('/')[2])
      result = await mockAPI.documents.getDetail(id)
    } else if (path.startsWith('/documents/get_documents_by_source_id/') && method === 'get') {
      const sourceId = parseInt(path.split('/')[3])
      result = await mockAPI.documents.getDocumentsBySourceId(sourceId)
    } else if (path === '/documents/cluster_analysis' && method === 'get') {
      result = await mockAPI.documents.getClusterAnalysis()
    } else if (path === '/documents/cluster_analysis/latest' && method === 'get') {
      result = await mockAPI.documents.getLatestClusterAnalysis()
    } else if (path === '/documents/upload_excel' && method === 'post') {
      result = await mockAPI.documents.uploadExcel(data.file)
    } else if (path === '/documents/upload' && method === 'post') {
      result = await mockAPI.documents.upload(data, data.onProgress)
    } else if (path.startsWith('/documents/') && method === 'delete') {
      const id = parseInt(path.split('/')[2])
      result = await mockAPI.documents.delete(id)
    }
    // RSS源相关
    else if (path === '/rss/sources' && method === 'get') {
      const params = new URLSearchParams(url?.split('?')[1] || '')
      result = await mockAPI.rss.getRssSources(Object.fromEntries(params))
    } else if (path.startsWith('/rss/sources/') && method === 'get') {
      const id = parseInt(path.split('/')[3])
      result = await mockAPI.rss.getRssSource(id)
    } else if (path === '/rss/sources' && method === 'post') {
      result = await mockAPI.rss.createRssSource(data)
    } else if (path.startsWith('/rss/sources/') && method === 'put') {
      const id = parseInt(path.split('/')[3])
      result = await mockAPI.rss.updateRssSource(id, data)
    } else if (path.startsWith('/rss/sources/') && method === 'delete') {
      const id = parseInt(path.split('/')[3])
      result = await mockAPI.rss.deleteRssSource(id)
    } else if (path.startsWith('/rss/feeds/') && method === 'get') {
      const id = parseInt(path.split('/')[3])
      result = await mockAPI.rss.getRssFeeds(id)
    } else if (path.startsWith('/rss/feeds/') && method === 'post') {
      const id = parseInt(path.split('/')[3])
      result = await mockAPI.rss.triggerRssCollection(id)
    }
    // 助手相关
    else if (path === '/assistant/query' && method === 'post') {
      result = await mockAPI.assistant.query(data)
    } else if (path === '/assistant/health' && method === 'get') {
      result = await mockAPI.assistant.health()
    }
    // 默认成功响应
    else {
      result = { 
        code: 200, 
        message: '请求成功', 
        data: null 
      }
    }

    return result
  } catch (error: any) {
    throw { response: { data: { message: error.message } } }
  }
}

// 请求拦截器
request.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // 如果使用 Mock 模式，直接返回 mock 数据
    if (USE_MOCK) {
      const mockResult = await mockRequest(config)
      // 创建一个模拟的响应对象
      const mockResponse = {
        data: mockResult,
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      }
      // 抛出一个特殊的错误，在响应拦截器中捕获并返回 mock 数据
      throw { __isMockResponse: true, response: mockResponse }
    }

    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {
    // 检查响应格式，如果包含code、message和data字段，则返回整个响应
    // 否则，将响应包装为标准格式
    if (response.data && typeof response.data === 'object') {
      if ('code' in response.data && 'message' in response.data && 'data' in response.data) {
        return response.data
      } else {
        // 包装为标准格式
        return {
          code: response.status,
          message: 'success',
          data: response.data
        }
      }
    }
    return response.data
  },
  (error: AxiosError) => {
    // 处理 Mock 响应
    if ((error as any).__isMockResponse) {
      return (error as any).response.data
    }

    const { response } = error

    // 处理 401 未授权
    if (response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 避免在非浏览器环境中出错
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
      return Promise.reject(new Error('登录已过期，请重新登录'))
    }

    // 处理 403 权限不足
    if (response?.status === 403) {
      return Promise.reject(new Error('权限不足，无法访问该资源'))
    }

    // 处理 404 资源不存在
    if (response?.status === 404) {
      return Promise.reject(new Error('请求的资源不存在'))
    }

    // 处理 500+ 服务器错误
    if (response?.status && response.status >= 500) {
      return Promise.reject(new Error('服务器错误，请稍后重试'))
    }

    // 处理其他错误
    const errorMessage = (response?.data as any)?.message || (response?.data as any)?.error || '请求失败'
    return Promise.reject(new Error(errorMessage))
  }
)

export default request