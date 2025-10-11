import request from '../request'
import { API_ENDPOINTS, HTTP_METHODS } from '../endpoints'
import type { ApiResponse } from '@/types'
import type { Document } from '@/types/document'

// 聚类分析结果类型定义
export interface ClusterAnalysis {
    clusters: {
        id: number
        percentage: number
        keyword: string
    }[]
}

// 文档分页响应类型定义
export interface DocumentsResponse {
    items: Document[]
    total: number
    page: number
    size: number
    total_pages: number
}

// 获取所有文档
export const getDocuments = async (): Promise<ApiResponse<DocumentsResponse>> => {
    return request({
        url: API_ENDPOINTS.DOCUMENTS.LIST,
        method: HTTP_METHODS.GET,
    })
}

// 获取文档分页列表
export const getDocumentsPage = async (params?: Record<string, any>): Promise<ApiResponse<DocumentsResponse>> => {
    return request({
        url: "/api/documents/page",
        method: HTTP_METHODS.GET,
        params
    })
}

// 获取单个文档
export const getDocument = async (id: number): Promise<ApiResponse<Document>> => {
    return request({
        url: API_ENDPOINTS.DOCUMENTS.DETAIL(id),
        method: HTTP_METHODS.GET
    })
}

// 获取特定RSS源的所有文档
export const getDocumentsBySourceId = async (sourceId: number): Promise<ApiResponse<Document[]>> => {
    return request({
        url: `/api/documents/get_documents_by_source_id/${sourceId}`,
        method: HTTP_METHODS.GET
    })
}

// 获取聚类分析
export const getClusterAnalysis = async (): Promise<ApiResponse<ClusterAnalysis>> => {
    return request({
        url: '/api/documents/cluster_analysis',
        method: HTTP_METHODS.GET
    })
}

// 获取最新一次聚类分析
export const getLatestClusterAnalysis = async (): Promise<ApiResponse<ClusterAnalysis>> => {
    return request({
        url: '/api/documents/cluster_analysis/latest',
        method: HTTP_METHODS.GET
    })
}

// 上传Excel文件
export const uploadExcel = async (file: File): Promise<ApiResponse<{ message: string }>> => {
    const formData = new FormData()
    formData.append('file', file)

    return request({
        url: API_ENDPOINTS.DOCUMENTS.UPLOAD_EXCEL,
        method: HTTP_METHODS.POST,
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}

// 上传文档
export const uploadDocument = async (
    formData: FormData,
    onProgress?: (progressEvent: any) => void
): Promise<ApiResponse<{ id: string }>> => {
    return request({
        url: API_ENDPOINTS.DOCUMENTS.UPLOAD,
        method: HTTP_METHODS.POST,
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: onProgress
    })
}

// 批量删除文档
export const batchDeleteDocuments = async (ids: number[]): Promise<ApiResponse<{ message: string; deleted_count: number }>> => {
    return request({
        url: API_ENDPOINTS.DOCUMENTS.BATCH_DELETE,
        method: HTTP_METHODS.DELETE,
        data: { ids }
    })
}

// 导出API对象
export const documentAPI = {
    getDocumentsPage,
    getDocuments,
    getDocument,
    getDocumentsBySourceId,
    getClusterAnalysis,
    getLatestClusterAnalysis,
    uploadExcel,
    uploadDocument,
    batchDeleteDocuments
}

export default documentAPI
// 导出Document类型，方便其他组件使用
export type { Document }