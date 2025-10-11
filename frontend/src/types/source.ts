// 数据源相关类型定义

// 数据源状态
export type SourceStatus = 'active' | 'inactive' | 'error'

// 数据源实体
export interface Source {
  id: number
  name: string
  url: string
  status: SourceStatus
  lastSync?: string
  description?: string
  config?: SourceConfig
  createdAt?: string
  updatedAt?: string
  // 新增字段
  source_type?: 'rss' | 'web'
  interval?: string
  is_paused?: boolean
  is_active?: boolean
  last_sync?: string
  next_sync?: string
  total_documents?: number
  last_document_count?: number
  sync_errors?: number
  last_error?: string
  tags?: string
}

// 数据源配置
export interface SourceConfig {
  // RSS 配置
  rss?: {
    updateInterval: number // 分钟
    maxItems: number
  }
  // Web 爬虫配置
  web?: {
    selector?: string
    depth: number
    delay: number // 毫秒
  }
  // API 配置
  api?: {
    headers?: Record<string, string>
    params?: Record<string, any>
    method: 'GET' | 'POST'
  }
}

// 创建数据源请求
export interface CreateSourceRequest {
  name: string
  url: string
  description?: string
  config?: SourceConfig
}

// 更新数据源请求
export interface UpdateSourceRequest extends Partial<CreateSourceRequest> {
  status?: SourceStatus
}

// 数据源过滤器
export interface RssSourceFilter {
  status?: SourceStatus
  keyword?: string
}

// 数据源统计
export interface RssSourceStats {
  total: number
  byStatus: Record<SourceStatus, number>
  lastSyncTime?: string
}