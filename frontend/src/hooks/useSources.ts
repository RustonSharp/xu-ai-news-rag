import { useState, useEffect, useCallback } from 'react'
import { rssAPI } from '../api'

interface RssSource {
    id: number
    name: string
    url: string
    source_type: 'RSS' | 'WEB'
    interval: 'SIX_HOUR' | 'TWELVE_HOUR' | 'ONE_DAY'
    is_paused: boolean
    is_active: boolean
    last_sync: string | null
    next_sync: string | null
    document_count: number
    last_document_count: number
    sync_errors: number
    last_error: string | null
    description: string | null
    tags: string
    created_at: string
    updated_at: string
}

interface RssStats {
    total_sources: number
    sources_by_type: Record<string, number>
    sources_by_interval: Record<string, number>
    active_sources: number
    paused_sources: number
    sources_due_for_sync: number
    total_documents: number
}

export const useRssSources = () => {
    const [sources, setSources] = useState<RssSource[]>([])
    const [stats, setStats] = useState<RssStats | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const fetchSources = useCallback(async () => {
        setLoading(true)
        setError(null)

        try {
            const response = await rssAPI.getSources({ type: 'rss' })
            // Handle the new API response structure
            const data = response.data || response
            setSources(data.sources || [])
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch RSS sources')
        } finally {
            setLoading(false)
        }
    }, [])

    const fetchStats = useCallback(async () => {
        try {
            const response = await rssAPI.getStats()
            setStats(response.data)
        } catch (err) {
            console.error('Failed to fetch RSS stats:', err)
        }
    }, [])

    const createSource = useCallback(async (sourceData: {
        name: string;
        url: string;
        interval?: string;
        description?: string;
        tags?: string[];
    }) => {
        setLoading(true)
        setError(null)

        try {
            const response = await rssAPI.createSource(sourceData)
            await fetchSources() // Refresh the list
            return response.data
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create RSS source')
            throw err
        } finally {
            setLoading(false)
        }
    }, [fetchSources])

    const updateSource = useCallback(async (id: number, sourceData: {
        name?: string;
        url?: string;
        interval?: string;
        description?: string;
        tags?: string[];
        is_paused?: boolean;
        is_active?: boolean;
    }) => {
        setLoading(true)
        setError(null)

        try {
            const response = await rssAPI.updateSource(id, sourceData)
            await fetchSources() // Refresh the list
            return response.data
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to update RSS source')
            throw err
        } finally {
            setLoading(false)
        }
    }, [fetchSources])

    const deleteSource = useCallback(async (id: number) => {
        setLoading(true)
        setError(null)

        try {
            await rssAPI.deleteSource(id)
            await fetchSources() // Refresh the list
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to delete RSS source')
            throw err
        } finally {
            setLoading(false)
        }
    }, [fetchSources])

    const triggerCollection = useCallback(async (sourceId: number) => {
        setLoading(true)
        setError(null)

        try {
            const response = await rssAPI.triggerCollection(sourceId)
            await fetchSources() // Refresh the list to get updated document counts
            return response.data
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to trigger RSS collection')
            throw err
        } finally {
            setLoading(false)
        }
    }, [fetchSources])

    const refreshSources = useCallback(() => {
        fetchSources()
        fetchStats()
    }, [fetchSources, fetchStats])

    useEffect(() => {
        fetchSources()
        fetchStats()
    }, [fetchSources, fetchStats])

    return {
        sources,
        stats,
        loading,
        error,
        fetchSources,
        fetchStats,
        createSource,
        updateSource,
        deleteSource,
        triggerCollection,
        refreshSources
    }
}
