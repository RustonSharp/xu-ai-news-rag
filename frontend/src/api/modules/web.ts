import request from '../request'
import { API_ENDPOINTS } from '../endpoints'

/**
 * Web 采集相关 API
 */
export const webAPI = {
    /**
     * 获取 Web 源列表
     * @param {Object} params - 查询参数
     * @returns {Promise} Web 源列表
     */
    getWebSources: (params = {}) => {
        return request.get(API_ENDPOINTS.COLLECTION.WEB_SOURCES, { params })
    },

    /**
     * 获取 Web 源详情
     * @param {string|number} id - Web 源ID
     * @returns {Promise} Web 源详情
     */
    getWebSource: (id: string | number) => {
        return request.get(API_ENDPOINTS.COLLECTION.WEB_SOURCE(id))
    },

    /**
     * 创建 Web 源
     * @param {Object} webData - Web 源数据
     * @param {string} webData.name - Web 源名称
     * @param {string} webData.url - Web 源URL
     * @param {string} webData.interval - 采集间隔（'SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY'）
     * @param {boolean} webData.is_paused - 是否暂停
     * @returns {Promise} 创建结果
     */
    createWebSource: (webData: {
        name: string;
        url: string;
        interval?: string;
        is_paused?: boolean;
    }) => {
        return request.post(API_ENDPOINTS.COLLECTION.WEB_SOURCES, webData)
    },

    /**
     * 更新 Web 源
     * @param {string|number} id - Web 源ID
     * @param {Object} webData - Web 源数据
     * @param {string} webData.name - Web 源名称
     * @param {string} webData.url - Web 源URL
     * @param {string} webData.interval - 采集间隔（'SIX_HOUR', 'TWELVE_HOUR', 'ONE_DAY'）
     * @param {boolean} webData.is_paused - 是否暂停
     * @returns {Promise} 更新结果
     */
    updateWebSource: (id: string | number, webData: {
        name?: string;
        url?: string;
        interval?: string;
        is_paused?: boolean;
    }) => {
        return request.put(API_ENDPOINTS.COLLECTION.WEB_SOURCE(id), webData)
    },

    /**
     * 删除 Web 源
     * @param {string|number} id - Web 源ID
     * @returns {Promise} 删除结果
     */
    deleteWebSource: (id: string | number) => {
        return request.delete(API_ENDPOINTS.COLLECTION.WEB_SOURCE(id))
    },
}
