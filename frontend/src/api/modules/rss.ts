import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * 采集相关 API
 */
export const rssAPI = {
  /**
   * 获取 RSS 源列表
   * @param {Object} params - 查询参数
   * @returns {Promise} RSS 源列表
   */
  getRssSources: (params = {}) => {
    return request.get(API_ENDPOINTS.COLLECTION.RSS_SOURCES, { params })
  },

  /**
   * 获取 RSS 源详情
   * @param {string|number} id - RSS 源ID
   * @returns {Promise} RSS 源详情
   */
  getRssSource: (id: string | number) => {
    return request.get(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id))
  },

  /**
   * 创建 RSS 源
   * @param {Object} rssData - RSS 源数据
   * @param {string} rssData.name - RSS 源名称
   * @param {string} rssData.url - RSS 源URL
   * @param {string} rssData.description - 描述
   * @param {number} rssData.update_interval - 更新间隔（分钟）
   * @returns {Promise} 创建结果
   */
  createRssSource: (rssData: {}) => {
    return request.post(API_ENDPOINTS.COLLECTION.RSS_SOURCES, rssData)
  },

  /**
   * 更新 RSS 源
   * @param {string|number} id - RSS 源ID
   * @param {Object} rssData - RSS 源数据
   * @returns {Promise} 更新结果
   */
  updateRssSource: (id: string | number, rssData: {}) => {
    return request.put(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id), rssData)
  },

  /**
   * 删除 RSS 源
   * @param {string|number} id - RSS 源ID
   * @returns {Promise} 删除结果
   */
  deleteRssSource: (id: string | number) => {
    return request.delete(API_ENDPOINTS.COLLECTION.RSS_SOURCE(id))
  },

  /**
   * 手动触发 RSS 采集
   * @param {string|number} id - RSS 源ID
   * @returns {Promise} 采集结果
   */
  triggerRssCollection: (id: string | number) => {
    return request.post(`${API_ENDPOINTS.COLLECTION.RSS_SOURCE(id)}/collect`)
  },
}