// 文档相关类型定义

// 文档实体 - 与后端Document模型保持一致
export interface Document {
  id: number
  title: string
  link: string
  description: string
  pub_date?: string | null
  author?: string | null
  tags: string[]
  rss_source_id: number
  crawled_at: string
}

// 文档过滤器
export interface DocumentFilter {
  keyword?: string
  tags?: string[]
  type?: string
  dateRange?: [string, string]
  source?: string
}

// 文档上传数据
export interface DocumentUploadData {
  file: File
  title?: string
  tags?: string[]
  source?: string
}

// 文档列表项（用于列表显示）
export interface DocumentListItem {
  id: number
  title: string
  type: string
  size: number
  uploadedAt: string
  tags: string[]
  source: string
}

// 文档统计
export interface DocumentStats {
  total: number
  byType: Record<string, number>
  totalSize: number
}