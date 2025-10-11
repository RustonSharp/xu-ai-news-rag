import { renderHook, act, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useRssSources } from './useSources'
import { sourceAPI } from '@/api'

// Mock the sourceAPI
vi.mock('@/api', () => ({
    sourceAPI: {
        getSources: vi.fn(),
        getStats: vi.fn(),
        createSource: vi.fn(),
        updateSource: vi.fn(),
        deleteSource: vi.fn(),
        triggerCollection: vi.fn(),
    },
}))

const mockSourceAPI = vi.mocked(sourceAPI)

describe('useRssSources', () => {
    const mockSources = [
        {
            id: 1,
            name: 'Test RSS Source 1',
            url: 'https://example.com/rss1',
            source_type: 'RSS' as const,
            interval: 'ONE_DAY' as const,
            is_paused: false,
            is_active: true,
            last_sync: '2024-01-01T00:00:00Z',
            next_sync: '2024-01-02T00:00:00Z',
            document_count: 10,
            last_document_count: 5,
            sync_errors: 0,
            last_error: null,
            description: 'Test description 1',
            tags: 'tag1,tag2',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
        },
        {
            id: 2,
            name: 'Test RSS Source 2',
            url: 'https://example.com/rss2',
            source_type: 'RSS' as const,
            interval: 'TWELVE_HOUR' as const,
            is_paused: true,
            is_active: false,
            last_sync: null,
            next_sync: null,
            document_count: 5,
            last_document_count: 0,
            sync_errors: 2,
            last_error: 'Connection timeout',
            description: 'Test description 2',
            tags: 'tag3',
            created_at: '2024-01-01T00:00:00Z',
            updated_at: '2024-01-01T00:00:00Z',
        },
    ]

    const mockStats = {
        total_sources: 2,
        sources_by_type: { RSS: 2, WEB: 0 },
        sources_by_interval: { ONE_DAY: 1, TWELVE_HOUR: 1 },
        active_sources: 1,
        paused_sources: 1,
        sources_due_for_sync: 1,
        total_documents: 15,
    }

    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should initialize with empty state', async () => {
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: [] } })
        mockSourceAPI.getStats.mockResolvedValue({ data: null })

        const { result } = renderHook(() => useRssSources())

        // Wait for initial effects to complete
        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.sources).toEqual([])
        expect(result.current.stats).toBeNull()
        expect(result.current.error).toBeNull()
    })

    it('should fetch sources on mount', async () => {
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: mockSources } })
        mockSourceAPI.getStats.mockResolvedValue({ data: mockStats })

        const { result } = renderHook(() => useRssSources())

        await waitFor(() => {
            expect(result.current.sources).toEqual(mockSources)
            expect(result.current.stats).toEqual(mockStats)
        })

        expect(mockSourceAPI.getSources).toHaveBeenCalledWith({ type: 'rss' })
        expect(mockSourceAPI.getStats).toHaveBeenCalled()
    })

    it('should handle fetch sources error', async () => {
        const errorMessage = 'Failed to fetch sources'
        mockSourceAPI.getSources.mockRejectedValue(new Error(errorMessage))
        mockSourceAPI.getStats.mockResolvedValue({ data: mockStats })

        const { result } = renderHook(() => useRssSources())

        await waitFor(() => {
            expect(result.current.error).toBe(errorMessage)
            expect(result.current.loading).toBe(false)
        })
    })

    it('should create source successfully', async () => {
        const newSourceData = {
            name: 'New RSS Source',
            url: 'https://example.com/new-rss',
            interval: 'ONE_DAY',
            description: 'New description',
            tags: ['tag1', 'tag2'],
        }

        const createdSource = { id: 3, ...newSourceData }
        mockSourceAPI.createSource.mockResolvedValue({ data: createdSource })
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: [...mockSources, createdSource] } })

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            const response = await result.current.createSource(newSourceData)
            expect(response).toEqual(createdSource)
        })

        expect(mockSourceAPI.createSource).toHaveBeenCalledWith({
            ...newSourceData,
            tags: 'tag1, tag2',
        })
    })

    it('should handle create source error', async () => {
        const errorMessage = 'Failed to create source'
        mockSourceAPI.createSource.mockRejectedValue(new Error(errorMessage))

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            try {
                await result.current.createSource({
                    name: 'Test',
                    url: 'https://example.com',
                })
            } catch (error) {
                expect(error).toBeInstanceOf(Error)
            }
        })

        await waitFor(() => {
            expect(result.current.error).toBe(errorMessage)
        })
    })

    it('should update source successfully', async () => {
        const updateData = {
            name: 'Updated Source',
            is_paused: true,
        }

        const updatedSource = { ...mockSources[0], ...updateData }
        mockSourceAPI.updateSource.mockResolvedValue({ data: updatedSource })
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: [updatedSource, mockSources[1]] } })

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            const response = await result.current.updateSource(1, updateData)
            expect(response).toEqual(updatedSource)
        })

        expect(mockSourceAPI.updateSource).toHaveBeenCalledWith(1, updateData)
    })

    it('should delete source successfully', async () => {
        mockSourceAPI.deleteSource.mockResolvedValue({})
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: [mockSources[1]] } })

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            await result.current.deleteSource(1)
        })

        expect(mockSourceAPI.deleteSource).toHaveBeenCalledWith(1)
    })

    it('should trigger collection successfully', async () => {
        const triggerResponse = { success: true, documents_collected: 5 }
        mockSourceAPI.triggerCollection.mockResolvedValue({ data: triggerResponse })
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: mockSources } })

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            const response = await result.current.triggerCollection(1)
            expect(response).toEqual(triggerResponse)
        })

        expect(mockSourceAPI.triggerCollection).toHaveBeenCalledWith(1)
    })

    it('should refresh sources', async () => {
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: mockSources } })
        mockSourceAPI.getStats.mockResolvedValue({ data: mockStats })

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            result.current.refreshSources()
        })

        await waitFor(() => {
            expect(mockSourceAPI.getSources).toHaveBeenCalledTimes(2) // Once on mount, once on refresh
            expect(mockSourceAPI.getStats).toHaveBeenCalledTimes(2)
        })
    })

    it('should set loading state during operations', async () => {
        let resolvePromise: (value: any) => void
        const promise = new Promise((resolve) => {
            resolvePromise = resolve
        })
        mockSourceAPI.createSource.mockReturnValue(promise)

        const { result } = renderHook(() => useRssSources())

        act(() => {
            result.current.createSource({
                name: 'Test',
                url: 'https://example.com',
            })
        })

        expect(result.current.loading).toBe(true)

        act(() => {
            resolvePromise!({ data: {} })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })
    })

    it('should handle tags array conversion', async () => {
        const sourceData = {
            name: 'Test Source',
            url: 'https://example.com',
            tags: ['tag1', 'tag2', 'tag3'],
        }

        mockSourceAPI.createSource.mockResolvedValue({ data: { id: 1, ...sourceData } })
        mockSourceAPI.getSources.mockResolvedValue({ data: { sources: [] } })

        const { result } = renderHook(() => useRssSources())

        await act(async () => {
            await result.current.createSource(sourceData)
        })

        expect(mockSourceAPI.createSource).toHaveBeenCalledWith({
            ...sourceData,
            tags: 'tag1, tag2, tag3',
        })
    })
})
