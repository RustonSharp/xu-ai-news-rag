// 统一 API 入口文件
import request from './request'
import { API_ENDPOINTS, HTTP_METHODS, HTTP_STATUS, type HttpMethod, type HttpStatus } from './endpoints'
import type { ApiResponse } from '@/types'

// 导入所有 API 模块
import { authAPI } from './modules/auth'
import { documentAPI } from './modules/document'
import { rssAPI } from './modules/rss'
import { analyticsAPI } from './modules/analytics'
import { assistantAPI } from './modules/assistant'

// API 配置类型
interface APIConfig {
  baseURL?: string
  timeout?: number
  headers?: Record<string, string>
}

// API 实例类型
interface APIInstance {
  auth: typeof authAPI
  documents: typeof documentAPI
  rss: typeof rssAPI
  analytics: typeof analyticsAPI
  assistant: typeof assistantAPI
}

// 统一导出所有 API
export {
  // 核心请求实例
  request,

  // 常量
  API_ENDPOINTS,
  HTTP_METHODS,
  HTTP_STATUS,

  // API 模块
  authAPI,
  documentAPI,
  rssAPI,
  analyticsAPI,
  assistantAPI
}

// 默认导出（方便直接导入使用）
const api: APIInstance = {
  auth: authAPI,
  documents: documentAPI,
  rss: rssAPI,
  analytics: analyticsAPI,
  assistant: assistantAPI
}

export default api

// 便捷方法：创建带有特定配置的请求实例
export const createAPIInstance = (config: APIConfig = {}): APIInstance => {
  return {
    auth: authAPI,
    documents: documentAPI,
    rss: rssAPI,
    analytics: analyticsAPI,
    assistant: assistantAPI
  }
}

// 便捷方法：设置全局认证 token
export const setAuthToken = (token: string | null): void => {
  if (token) {
    request.defaults.headers.common['Authorization'] = `Bearer ${token}`
    localStorage.setItem('token', token)
  } else {
    delete request.defaults.headers.common['Authorization']
    localStorage.removeItem('token')
  }
}

// 便捷方法：获取当前 token
export const getAuthToken = (): string | null => {
  return localStorage.getItem('token')
}

// 便捷方法：清除认证信息
export const clearAuth = (): void => {
  setAuthToken(null)
  localStorage.removeItem('user')
}