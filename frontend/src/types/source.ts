// 数据源相关类型定义

// 数据源类型
export type SourceType = 'rss' | 'web' | 'api'

// 数据源状态
export type SourceStatus = 'active' | 'inactive' | 'error'

// 数据源实体
export interface Source {
  id: number
  name: string
  type: SourceType
  url: string
  status: SourceStatus
  lastSync?: string
  description?: string
  config?: SourceConfig
  createdAt?: string
  updatedAt?: string
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
  type: SourceType
  url: string
  description?: string
  config?: SourceConfig
}

// 更新数据源请求
export interface UpdateSourceRequest extends Partial<CreateSourceRequest> {
  status?: SourceStatus
}

// 数据源过滤器
export interface SourceFilter {
  type?: SourceType
  status?: SourceStatus
  keyword?: string
}

// 数据源统计
export interface SourceStats {
  total: number
  byType: Record<SourceType, number>
  byStatus: Record<SourceStatus, number>
  lastSyncTime?: string
}