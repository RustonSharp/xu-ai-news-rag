import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * 统一数据源 API (支持RSS、Web等多种类型)
 */
export const sourceAPI = {
  /**
   * 获取数据源列表 (支持RSS和Web类型)
   * @param {Object} params - 查询参数
   * @param {string} params.type - 数据源类型 ('rss', 'web', 或空字符串获取所有)
   * @returns {Promise} 数据源列表
   */
  getSources: (params: { type?: string; page?: number; size?: number; search?: string } = {}) => {
    const queryParams = { ...params }
    if (params.type) {
      queryParams.type = params.type.toLowerCase()
    }
    return request.get(API_ENDPOINTS.COLLECTION.RSS_SOURCES, { params: queryParams })
  },

  /**
   * 获取数据源详情
   * @param {string|number} id - 数据源ID
   * @returns {Promise} 数据源详情
   */
  getSource: (id: string | number) => {
    return request.get(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id))
  },

  /**
   * 创建数据源
   * @param {Object} sourceData - 数据源数据
   * @param {string} sourceData.name - 数据源名称
   * @param {string} sourceData.url - 数据源URL
   * @param {string} sourceData.interval - 采集间隔（'SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY'）
   * @param {string} sourceData.description - 描述
   * @param {string[]} sourceData.tags - 标签
   * @returns {Promise} 创建结果
   */
  createSource: (sourceData: {
    name: string;
    url: string;
    source_type?: string;
    interval?: string;
    description?: string;
    tags?: string;
  }) => {
    const data = {
      ...sourceData,
      source_type: sourceData.source_type || 'rss'
    }
    return request.post(API_ENDPOINTS.COLLECTION.RSS_SOURCES, data)
  },

  /**
   * 更新数据源
   * @param {string|number} id - 数据源ID
   * @param {Object} sourceData - 数据源数据
   * @param {string} sourceData.name - 数据源名称
   * @param {string} sourceData.url - 数据源URL
   * @param {string} sourceData.interval - 采集间隔（'SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY'）
   * @param {string} sourceData.description - 描述
   * @param {string[]} sourceData.tags - 标签
   * @param {boolean} sourceData.is_paused - 是否暂停
   * @param {boolean} sourceData.is_active - 是否激活
   * @returns {Promise} 更新结果
   */
  updateSource: (id: string | number, sourceData: {
    name?: string;
    url?: string;
    source_type?: string;
    interval?: string;
    description?: string;
    tags?: string;
    is_paused?: boolean;
    is_active?: boolean;
  }) => {
    return request.put(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id), sourceData)
  },

  /**
   * 删除数据源
   * @param {string|number} id - 数据源ID
   * @returns {Promise} 删除结果
   */
  deleteSource: (id: string | number) => {
    return request.delete(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id))
  },

  /**
   * 获取数据源订阅内容
   * @param {string|number} id - 数据源ID
   * @returns {Promise} 订阅内容
   */
  getFeeds: (id: string | number) => {
    return request.get(API_ENDPOINTS.COLLECTION.RSS_FEEDS(id)).then(response => {
      // 处理后端返回的数据
      return response.data || response;
    })
  },

  /**
   * 手动触发数据源采集
   * @param {string|number} id - 数据源ID
   * @returns {Promise} 采集结果
   */
  triggerCollection: (id: string | number) => {
    return request.post(`${API_ENDPOINTS.COLLECTION.RSS_SOURCE(id)}/collect`).then(response => {
      // 处理后端返回的数据
      return response.data || response;
    })
  },

  /**
   * 获取数据源统计信息
   * @returns {Promise} 统计信息
   */
  getStats: () => {
    return request.get(`${API_ENDPOINTS.COLLECTION.RSS_SOURCES}/stats`)
  },

  // 兼容性方法 - 保持与现有代码的兼容性
  getRssSources: (params: { type?: string; page?: number; size?: number; search?: string } = {}) => {
    return sourceAPI.getSources(params)
  },

  getRssSource: (id: string | number) => {
    return sourceAPI.getSource(id)
  },

  createRssSource: (sourceData: {
    name: string;
    url: string;
    source_type?: string;
    interval?: string;
    description?: string;
    tags?: string;
  }) => {
    return sourceAPI.createSource(sourceData)
  },

  updateRssSource: (id: string | number, sourceData: {
    name?: string;
    url?: string;
    source_type?: string;
    interval?: string;
    description?: string;
    tags?: string;
    is_paused?: boolean;
    is_active?: boolean;
  }) => {
    return sourceAPI.updateSource(id, sourceData)
  },

  deleteRssSource: (id: string | number) => {
    return sourceAPI.deleteSource(id)
  },

  getRssFeeds: (id: string | number) => {
    return sourceAPI.getFeeds(id)
  },

  triggerRssCollection: (id: string | number) => {
    return sourceAPI.triggerCollection(id)
  },

  getRssStats: () => {
    return sourceAPI.getStats()
  }
}

// 兼容性导出 - 保持与现有代码的兼容性
export const rssAPI = sourceAPI