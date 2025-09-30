// 文档相关类型定义

// 文档状态
export type DocumentStatus = 'pending' | 'processing' | 'processed' | 'failed'

// 文档类型
export type DocumentType = 'pdf' | 'docx' | 'txt' | 'md'

// 文档实体
export interface Document {
  id: number
  title: string
  content: string
  type: DocumentType
  size: number
  uploadedAt: string
  created_at: string
  status: DocumentStatus
  source: string
  url?: string
  tags: string[]
}

// 文档过滤器
export interface DocumentFilter {
  keyword?: string
  tags?: string[]
  status?: DocumentStatus
  type?: DocumentType
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
  type: DocumentType
  size: number
  uploadedAt: string
  status: DocumentStatus
  tags: string[]
  source: string
}

// 文档统计
export interface DocumentStats {
  total: number
  byStatus: Record<DocumentStatus, number>
  byType: Record<DocumentType, number>
  totalSize: number
}