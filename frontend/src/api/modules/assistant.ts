import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * 助手相关 API
 */
export const assistantAPI = {
  /**
   * 查询助手
   * @param {Object} params - 查询参数
   * @param {string} params.query - 查询内容
   * @param {Object} [params.options] - 查询选项
   * @returns {Promise} 查询结果
   */
  query: (params: {
    query: string;
    options?: {
      use_knowledge_base?: boolean;
      use_online_search?: boolean;
    };
  }) => {
    return request.post(API_ENDPOINTS.ASSISTANT.QUERY, params).then(response => {
      // 处理后端返回的数据
      return response.data || response;
    })
  },

  /**
   * 检查助手服务状态
   * @returns {Promise} 服务状态
   */
  health: () => {
    return request.get(API_ENDPOINTS.ASSISTANT.HEALTH).then(response => {
      // 处理后端返回的数据
      return response.data || response;
    })
  },
}