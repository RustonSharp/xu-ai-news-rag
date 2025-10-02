import request from '../request'
import { API_ENDPOINTS } from '../endpoints'
import type { ApiResponse } from '@/types'

// 分析相关类型定义
export interface AnalyticsParams {
  period?: 'day' | 'week' | 'month' | 'year'
  startDate?: string
  endDate?: string
  groupBy?: 'type' | 'source' | 'date'
  type?: 'query' | 'result' | 'click'
  action?: string
  limit?: number
}

export interface OverviewData {
  totalDocuments: number
  totalSearches: number
  totalUsers: number
  avgResponseTime: number
  successRate: number
}

export interface DocumentsStats {
  period: string
  count: number
  type?: string
  source?: string
}

export interface SearchStats {
  period: string
  queries: number
  results: number
  clicks: number
  avgPosition: number
}

export interface UserActivity {
  period: string
  activeUsers: number
  newUsers: number
  sessions: number
  avgSessionDuration: number
}

export interface TrendData {
  period: string
  value: number
  change: number
  changePercent: number
}

export interface PopularKeyword {
  keyword: string
  count: number
  clickRate: number
  avgPosition: number
}

export interface SourceDistribution {
  source: string
  count: number
  percentage: number
}

export interface ExportParams {
  type: 'overview' | 'documents' | 'search' | 'users'
  format: 'csv' | 'excel' | 'pdf'
  period?: string
  startDate?: string
  endDate?: string
}

/**
 * 分析相关 API
 */
export const analyticsAPI = {
  /**
   * 获取总览数据
   */
  getOverview: (params: AnalyticsParams = {}): Promise<ApiResponse<OverviewData>> => {
    return request.get(API_ENDPOINTS.ANALYTICS.OVERVIEW, { params })
  },
  
  /**
   * 获取文档统计数据
   */
  getDocumentsStats: (params: AnalyticsParams = {}): Promise<ApiResponse<DocumentsStats[]>> => {
    return request.get(API_ENDPOINTS.ANALYTICS.DOCUMENTS_STATS, { params })
  },
  
  /**
   * 获取搜索统计数据
   */
  getSearchStats: (params: AnalyticsParams = {}): Promise<ApiResponse<SearchStats[]>> => {
    return request.get(API_ENDPOINTS.ANALYTICS.SEARCH_STATS, { params })
  },
  
  /**
   * 获取用户活动数据
   */
  getUserActivity: (params: AnalyticsParams = {}): Promise<ApiResponse<UserActivity[]>> => {
    return request.get(API_ENDPOINTS.ANALYTICS.USER_ACTIVITY, { params })
  },
  
  /**
   * 获取趋势数据
   */
  getTrends: (params: AnalyticsParams = {}): Promise<ApiResponse<TrendData[]>> => {
    return request.get(API_ENDPOINTS.ANALYTICS.TRENDS, { params })
  },
  
  /**
   * 获取热门搜索关键词
   */
  getPopularKeywords: (params: AnalyticsParams = {}): Promise<ApiResponse<PopularKeyword[]>> => {
    return request.get(`${API_ENDPOINTS.ANALYTICS.SEARCH_STATS}/keywords`, { params })
  },
  
  /**
   * 获取文档来源分布
   */
  getSourceDistribution: (params: AnalyticsParams = {}): Promise<ApiResponse<SourceDistribution[]>> => {
    return request.get(`${API_ENDPOINTS.ANALYTICS.DOCUMENTS_STATS}/sources`, { params })
  },
  
  /**
   * 导出分析报告
   */
  exportReport: (exportParams: ExportParams): Promise<ApiResponse<Blob>> => {
    return request.post(`${API_ENDPOINTS.ANALYTICS.OVERVIEW}/export`, exportParams, {
      responseType: 'blob'
    })
  }
}