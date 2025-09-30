import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * 搜索相关 API
 */
export const searchAPI = {
  /**
   * 执行搜索查询
   * @param {Object} searchParams - 搜索参数
   * @param {string} searchParams.query - 搜索关键词
   * @param {Object} searchParams.filters - 过滤条件
   * @param {number} searchParams.page - 页码
   * @param {number} searchParams.size - 每页数量
   * @returns {Promise} 搜索结果
   */
  search: (searchParams) => {
    return request.post(API_ENDPOINTS.SEARCH.QUERY, searchParams)
  },

  /**
   * 智能问答聊天
   * @param {Object} chatParams - 聊天参数
   * @param {string} chatParams.query - 用户问题
   * @param {string} chatParams.conversation_id - 会话ID（可选）
   * @param {Array} chatParams.context - 上下文消息（可选）
   * @returns {Promise} 回答结果
   */
  chat: (chatParams) => {
    return request.post(API_ENDPOINTS.SEARCH.CHAT, chatParams)
  },

  /**
   * 获取搜索历史
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.size - 每页数量
   * @returns {Promise} 搜索历史
   */
  getSearchHistory: (params = {}) => {
    return request.get(API_ENDPOINTS.SEARCH.HISTORY, { params })
  },

  /**
   * 获取搜索建议
   * @param {string} query - 搜索关键词
   * @returns {Promise} 搜索建议
   */
  getSearchSuggestions: (query: string) => {
    return request.get(API_ENDPOINTS.SEARCH.SUGGESTIONS, {
      params: { q: query }
    })
  },

  /**
   * 清除搜索历史
   * @returns {Promise} 清除结果
   */
  clearSearchHistory: () => {
    return request.delete(API_ENDPOINTS.SEARCH.HISTORY)
  }
}