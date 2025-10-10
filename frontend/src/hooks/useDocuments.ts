import { useState, useEffect, useCallback } from 'react'
import { documentAPI } from '../api'

interface Document {
    id: number
    title: string
    link: string
    description: string
    pub_date: string | null
    author: string | null
    tags: string[]
    source_id: number | null
    crawled_at: string
}

interface DocumentStats {
    total_documents: number
    documents_by_source: Record<string, number>
    documents_by_date: Record<string, number>
    top_tags: Array<{ tag: string; count: number }>
    recent_documents: Array<{
        id: number
        title: string
        crawled_at: string
        source_id: number | null
    }>
}

interface DocumentSearchParams {
    page: number
    size: number
    search?: string
    type?: string
    source?: string
    start?: string
    end?: string
}

export const useDocuments = () => {
    const [documents, setDocuments] = useState<Document[]>([])
    const [stats, setStats] = useState<DocumentStats | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const fetchDocuments = useCallback(async (params?: DocumentSearchParams) => {
        setLoading(true)
        setError(null)

        try {
            const response = await documentAPI.getDocuments(params)
            setDocuments(response.data || [])
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch documents')
        } finally {
            setLoading(false)
        }
    }, [])

    const fetchDocumentStats = useCallback(async () => {
        try {
            const response = await documentAPI.getDocumentStats()
            setStats(response.data)
        } catch (err) {
            console.error('Failed to fetch document stats:', err)
        }
    }, [])

    const searchDocuments = useCallback(async (searchTerm: string, filters?: Partial<DocumentSearchParams>) => {
        setLoading(true)
        setError(null)

        try {
            const params: DocumentSearchParams = {
                page: 1,
                size: 20,
                search: searchTerm,
                ...filters
            }
            const response = await documentAPI.getDocuments(params)
            setDocuments(response.data || [])
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to search documents')
        } finally {
            setLoading(false)
        }
    }, [])

    const getDocumentsBySource = useCallback(async (sourceId: number) => {
        setLoading(true)
        setError(null)

        try {
            const response = await documentAPI.getDocumentsBySource(sourceId)
            setDocuments(response.data || [])
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch documents by source')
        } finally {
            setLoading(false)
        }
    }, [])

    const refreshDocuments = useCallback(() => {
        fetchDocuments()
        fetchDocumentStats()
    }, [fetchDocuments, fetchDocumentStats])

    useEffect(() => {
        fetchDocuments()
        fetchDocumentStats()
    }, [fetchDocuments, fetchDocumentStats])

    return {
        documents,
        stats,
        loading,
        error,
        fetchDocuments,
        fetchDocumentStats,
        searchDocuments,
        getDocumentsBySource,
        refreshDocuments
    }
}
