// 类型定义统一导出

// API 相关类型
export * from './api'

// 文档相关类型
export * from './document'

// 数据源相关类型
export * from './rss'

// 分析统计相关类型
export * from './analytics'

// 组件相关类型
export * from './components'

// 通用类型
export * from './common'

// 重新导出常用类型（便于使用）
export type {
  // API
  ApiResponse,
  PaginationParams,
  User,
  ChatMessage,
} from './api'

export type {
  // Document
  Document,
  DocumentFilter,
  DocumentUploadData,
  DocumentListItem,
} from './document'

export type {
  // Source
  Source,
  SourceConfig,
  CreateSourceRequest,
  UpdateSourceRequest,
} from './rss'

export type {
  // Analytics
  AnalyticsOverview,
  TrendDataPoint,
  QueryStats,
} from './analytics'

export type {
  // Components
  ButtonProps,
  InputProps,
  ModalProps,
  TableProps,
  TableColumn,
} from './components'

export type {
  // Common
  Theme,
  Language,
  Status,
  ErrorInfo,
  OperationResult,
  MenuItem,
  Notification
} from './common'

// 类型工具函数
export type Prettify<T> = {
  [K in keyof T]: T[K]
} & {}

export type PickByType<T, U> = {
  [K in keyof T as T[K] extends U ? K : never]: T[K]
}

export type OmitByType<T, U> = {
  [K in keyof T as T[K] extends U ? never : K]: T[K]
}