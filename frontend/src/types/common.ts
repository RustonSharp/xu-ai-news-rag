// 通用类型定义

// 主题类型
export type Theme = 'light' | 'dark' | 'system'

// 语言类型
export type Language = 'zh-CN' | 'en-US'

// 排序方向
export type SortOrder = 'asc' | 'desc'

// 排序配置
export interface SortConfig {
  field: string
  order: SortOrder
}

// 通用 ID 类型
export type ID = string | number

// 时间戳类型
export type Timestamp = string

// 文件类型
export interface FileInfo {
  name: string
  size: number
  type: string
  lastModified: number
}

// 坐标点
export interface Point {
  x: number
  y: number
}

// 尺寸
export interface Size {
  width: number
  height: number
}

// 矩形区域
export interface Rect extends Point, Size {}

// 颜色值
export type Color = string

// 状态类型
export type Status = 'idle' | 'loading' | 'success' | 'error'

// 错误信息
export interface ErrorInfo {
  code: string | number
  message: string
  details?: any
}

// 操作结果
export interface OperationResult<T = any> {
  success: boolean
  data?: T
  error?: ErrorInfo
}

// 键值对
export type KeyValuePair<K = string, V = any> = {
  key: K
  value: V
}

// 选项类型
export interface Option<T = any> {
  label: string
  value: T
  disabled?: boolean
  description?: string
}

// 菜单项
export interface MenuItem {
  key: string
  label: string
  icon?: string
  path?: string
  children?: MenuItem[]
  disabled?: boolean
  hidden?: boolean
}

// 面包屑项
export interface BreadcrumbItem {
  title: string
  path?: string
}

// 通知类型
export type NotificationType = 'info' | 'success' | 'warning' | 'error'

// 通知消息
export interface Notification {
  id: string
  type: NotificationType
  title: string
  message?: string
  duration?: number
  closable?: boolean
}

// 环境变量
export interface Environment {
  NODE_ENV: 'development' | 'production' | 'test'
  API_BASE_URL: string
  APP_VERSION: string
}

// 工具函数类型
export type Callback<T = void> = () => T
export type AsyncCallback<T = void> = () => Promise<T>
export type EventHandler<T = Event> = (event: T) => void
export type ValueCallback<T, R = void> = (value: T) => R
export type AsyncValueCallback<T, R = void> = (value: T) => Promise<R>

// 深度可选
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P]
}

// 深度必需
export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P]
}

// 排除 null 和 undefined
export type NonNullable<T> = T extends null | undefined ? never : T