import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * 文档相关 API
 */
export const documentsAPI = {
  /**
   * 获取文档列表
   * @param {Object} params - 查询参数
   * @param {number} params.page - 页码
   * @param {number} params.size - 每页数量
   * @param {string} params.search - 搜索关键词
   * @param {string} params.type - 文档类型
   * @param {string} params.source - 文档来源
   * @param {string} params.startDate - 开始日期
   * @param {string} params.endDate - 结束日期
   * @returns {Promise} 文档列表
   */
  getDocuments: (params = {}) => {
    return request.get(API_ENDPOINTS.DOCUMENTS.LIST, { params })
  },
  
  /**
   * 获取文档详情
   * @param {string|number} id - 文档ID
   * @returns {Promise} 文档详情
   */
  getDocument: (id) => {
    return request.get(API_ENDPOINTS.DOCUMENTS.DETAIL(id))
  },
  
  /**
   * 创建文档
   * @param {Object} documentData - 文档数据
   * @returns {Promise} 创建结果
   */
  createDocument: (documentData) => {
    return request.post(API_ENDPOINTS.DOCUMENTS.CREATE, documentData)
  },
  
  /**
   * 更新文档
   * @param {string|number} id - 文档ID
   * @param {Object} documentData - 文档数据
   * @returns {Promise} 更新结果
   */
  updateDocument: (id, documentData) => {
    return request.put(API_ENDPOINTS.DOCUMENTS.UPDATE(id), documentData)
  },
  
  /**
   * 删除文档
   * @param {string|number} id - 文档ID
   * @returns {Promise} 删除结果
   */
  deleteDocument: (id) => {
    return request.delete(API_ENDPOINTS.DOCUMENTS.DELETE(id))
  },
  
  /**
   * 批量删除文档
   * @param {Array} ids - 文档ID数组
   * @returns {Promise} 删除结果
   */
  batchDeleteDocuments: (ids) => {
    return request.delete(API_ENDPOINTS.DOCUMENTS.BATCH_DELETE, {
      data: { ids }
    })
  },
  
  /**
   * 搜索文档
   * @param {Object} searchParams - 搜索参数
   * @param {string} searchParams.query - 搜索关键词
   * @param {Object} searchParams.filters - 过滤条件
   * @returns {Promise} 搜索结果
   */
  searchDocuments: (searchParams) => {
    return request.post(API_ENDPOINTS.DOCUMENTS.SEARCH, searchParams)
  },
  
  /**
   * 上传文档
   * @param {FormData} formData - 文件数据
   * @param {Function} onProgress - 上传进度回调
   * @returns {Promise} 上传结果
   */
  uploadDocument: (formData, onProgress) => {
    return request.post(API_ENDPOINTS.DOCUMENTS.UPLOAD, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      }
    })
  }
}