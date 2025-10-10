import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * 统一数据源 API (支持RSS、Web等多种类型)
 */
export const rssAPI = {
  /**
   * 获取数据源列表 (支持RSS和Web类型)
   * @param {Object} params - 查询参数
   * @param {string} params.type - 数据源类型 ('rss', 'web', 或空字符串获取所有)
   * @returns {Promise} 数据源列表
   */
  getRssSources: (params: { type?: string; page?: number; size?: number; search?: string } = {}) => {
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
  getRssSource: (id: string | number) => {
    return request.get(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id))
  },

  /**
   * 创建 RSS 数据源
   * @param {Object} rssData - RSS 源数据
   * @param {string} rssData.name - RSS 源名称
   * @param {string} rssData.url - RSS 源URL
   * @param {string} rssData.interval - 采集间隔（'SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY'）
   * @param {string} rssData.description - 描述
   * @param {string[]} rssData.tags - 标签
   * @returns {Promise} 创建结果
   */
  createRssSource: (rssData: {
    name: string;
    url: string;
    source_type?: string;
    interval?: string;
    description?: string;
    tags?: string;
  }) => {
    const sourceData = {
      ...rssData,
      source_type: 'rss'
    }
    return request.post(API_ENDPOINTS.COLLECTION.RSS_SOURCES, sourceData)
  },

  /**
   * 更新 RSS 数据源
   * @param {string|number} id - 数据源ID
   * @param {Object} rssData - RSS 源数据
   * @param {string} rssData.name - RSS 源名称
   * @param {string} rssData.url - RSS 源URL
   * @param {string} rssData.interval - 采集间隔（'SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY'）
   * @param {string} rssData.description - 描述
   * @param {string[]} rssData.tags - 标签
   * @param {boolean} rssData.is_paused - 是否暂停
   * @param {boolean} rssData.is_active - 是否激活
   * @returns {Promise} 更新结果
   */
  updateRssSource: (id: string | number, rssData: {
    name?: string;
    url?: string;
    source_type?: string;
    interval?: string;
    description?: string;
    tags?: string;
    is_paused?: boolean;
    is_active?: boolean;
  }) => {
    return request.put(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id), rssData)
  },

  /**
   * 删除数据源
   * @param {string|number} id - 数据源ID
   * @returns {Promise} 删除结果
   */
  deleteRssSource: (id: string | number) => {
    return request.delete(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id))
  },

  /**
   * 获取 RSS 订阅内容
   * @param {string|number} id - RSS 源ID
   * @returns {Promise} RSS 订阅内容
   */
  getRssFeeds: (id: string | number) => {
    return request.get(API_ENDPOINTS.COLLECTION.RSS_FEEDS(id)).then(response => {
      // 处理后端返回的数据
      return response.data || response;
    })
  },

  /**
   * 手动触发 RSS 采集
   * @param {string|number} id - RSS 源ID
   * @returns {Promise} 采集结果
   */
  triggerRssCollection: (id: string | number) => {
    return request.post(`${API_ENDPOINTS.COLLECTION.RSS_SOURCE(id)}/collect`).then(response => {
      // 处理后端返回的数据
      return response.data || response;
    })
  },

  /**
   * 获取数据源统计信息
   * @returns {Promise} 统计信息
   */
  getRssStats: () => {
    return request.get(`${API_ENDPOINTS.COLLECTION.RSS_SOURCES}/stats`)
  },

  // 兼容性方法 - 保持与现有代码的兼容性
  getSources: (params: { type?: string; page?: number; size?: number; search?: string } = {}) => {
    return rssAPI.getRssSources(params)
  },

  getSource: (id: string | number) => {
    return rssAPI.getRssSource(id)
  },

  createSource: (sourceData: {
    name: string;
    url: string;
    interval?: string;
    description?: string;
    tags?: string[];
  }) => {
    return rssAPI.createRssSource(sourceData)
  },

  updateSource: (id: string | number, sourceData: {
    name?: string;
    url?: string;
    interval?: string;
    description?: string;
    tags?: string[];
    is_paused?: boolean;
    is_active?: boolean;
  }) => {
    return rssAPI.updateRssSource(id, sourceData)
  },

  deleteSource: (id: string | number) => {
    return rssAPI.deleteRssSource(id)
  },

  triggerCollection: (id: string | number) => {
    return rssAPI.triggerRssCollection(id)
  },

  getStats: () => {
    return rssAPI.getRssStats()
  }
}