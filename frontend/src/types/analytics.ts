// 分析统计相关类型定义

// 概览统计
export interface AnalyticsOverview {
  totalDocuments: number
  totalQueries: number
  totalUsers: number
  systemHealth: number // 百分比
}

// 趋势数据点
export interface TrendDataPoint {
  date: string
  documents: number
  queries: number
  users?: number
}

// 趋势查询参数
export interface TrendParams {
  startDate?: string
  endDate?: string
  granularity?: 'day' | 'week' | 'month'
}

// 查询统计
export interface QueryStats {
  total: number
  successful: number
  failed: number
  averageResponseTime: number // 毫秒
  popularQueries: PopularQuery[]
}

// 热门查询
export interface PopularQuery {
  query: string
  count: number
  lastUsed: string
}

// 文档使用统计
export interface DocumentUsageStats {
  mostViewed: DocumentUsage[]
  mostSearched: DocumentUsage[]
  recentlyAdded: DocumentUsage[]
}

// 文档使用情况
export interface DocumentUsage {
  id: number
  title: string
  viewCount: number
  searchCount: number
  lastAccessed: string
}

// 系统性能指标
export interface SystemMetrics {
  cpuUsage: number // 百分比
  memoryUsage: number // 百分比
  diskUsage: number // 百分比
  responseTime: number // 毫秒
  uptime: number // 秒
}

// 用户活动统计
export interface UserActivityStats {
  activeUsers: number
  newUsers: number
  totalSessions: number
  averageSessionDuration: number // 分钟
  userGrowth: TrendDataPoint[]
}

// 完整的分析数据
export interface AnalyticsData {
  overview: AnalyticsOverview
  trends: TrendDataPoint[]
  queryStats: QueryStats
  documentUsage: DocumentUsageStats
  systemMetrics: SystemMetrics
  userActivity: UserActivityStats
}