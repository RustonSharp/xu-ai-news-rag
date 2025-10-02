// API 相关类型定义

// 基础 API 响应类型
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页参数
export interface PaginationParams {
  page?: number
  pageSize?: number
  keyword?: string
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

// 登录请求
export interface LoginRequest {
  email: string
  password: string
}

// 注册请求
export interface RegisterRequest {
  email: string
  username: string
  password: string
}

// 认证响应
export interface AuthResponse {
  user: User
  token: string
}

// 用户类型
export interface User {
  id: number
  email: string
  username: string
  role: 'admin' | 'user'
  createdAt: string
}

// 文档上传进度回调
export type UploadProgressCallback = (progress: number) => void

// 搜索参数
export interface SearchParams {
  query: string
  limit?: number
  threshold?: number
}

// 搜索结果
export interface SearchResult {
  id: number
  title: string
  content: string
  score: number
  source: string
  url?: string
}

// 聊天消息
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

// 聊天响应
export interface ChatResponse {
  message: ChatMessage
  sources?: SearchResult[]
}