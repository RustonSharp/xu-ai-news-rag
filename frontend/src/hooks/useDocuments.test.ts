import { renderHook, act, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useDocuments } from './useDocuments'
import { documentAPI } from '@/api'

// Mock the documentAPI
vi.mock('@/api', () => ({
    documentAPI: {
        getDocuments: vi.fn(),
        getDocumentStats: vi.fn(),
        getDocumentsBySource: vi.fn(),
    },
}))

const mockDocumentAPI = vi.mocked(documentAPI)

describe('useDocuments', () => {
    const mockDocuments = [
        {
            id: 1,
            title: 'Test Document 1',
            link: 'https://example.com/1',
            description: 'Test description 1',
            pub_date: '2024-01-01',
            author: 'Test Author',
            tags: ['tag1', 'tag2'],
            source_id: 1,
            crawled_at: '2024-01-01T00:00:00Z',
        },
        {
            id: 2,
            title: 'Test Document 2',
            link: 'https://example.com/2',
            description: 'Test description 2',
            pub_date: '2024-01-02',
            author: 'Test Author 2',
            tags: ['tag3'],
            source_id: 2,
            crawled_at: '2024-01-02T00:00:00Z',
        },
    ]

    const mockStats = {
        total_documents: 2,
        documents_by_source: { '1': 1, '2': 1 },
        documents_by_date: { '2024-01-01': 1, '2024-01-02': 1 },
        top_tags: [{ tag: 'tag1', count: 1 }],
        recent_documents: [
            {
                id: 1,
                title: 'Test Document 1',
                crawled_at: '2024-01-01T00:00:00Z',
                source_id: 1,
            },
        ],
    }

    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should initialize with empty state', async () => {
        mockDocumentAPI.getDocuments.mockResolvedValue({ data: [] })
        mockDocumentAPI.getDocumentStats.mockResolvedValue({ data: null })

        const { result } = renderHook(() => useDocuments())

        // Wait for initial effects to complete
        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.documents).toEqual([])
        expect(result.current.stats).toBeNull()
        expect(result.current.error).toBeNull()
    })

    it('should fetch documents on mount', async () => {
        mockDocumentAPI.getDocuments.mockResolvedValue({ data: mockDocuments })
        mockDocumentAPI.getDocumentStats.mockResolvedValue({ data: mockStats })

        const { result } = renderHook(() => useDocuments())

        await waitFor(() => {
            expect(result.current.documents).toEqual(mockDocuments)
            expect(result.current.stats).toEqual(mockStats)
        })

        expect(mockDocumentAPI.getDocuments).toHaveBeenCalled()
        expect(mockDocumentAPI.getDocumentStats).toHaveBeenCalled()
    })

    it('should handle fetch documents error', async () => {
        const errorMessage = 'Failed to fetch documents'
        mockDocumentAPI.getDocuments.mockRejectedValue(new Error(errorMessage))
        mockDocumentAPI.getDocumentStats.mockResolvedValue({ data: mockStats })

        const { result } = renderHook(() => useDocuments())

        await waitFor(() => {
            expect(result.current.error).toBe(errorMessage)
            expect(result.current.loading).toBe(false)
        })
    })

    it('should search documents with search term', async () => {
        mockDocumentAPI.getDocuments.mockResolvedValue({ data: mockDocuments })

        const { result } = renderHook(() => useDocuments())

        await act(async () => {
            await result.current.searchDocuments('test search', { type: 'news' })
        })

        expect(mockDocumentAPI.getDocuments).toHaveBeenCalledWith({
            page: 1,
            size: 20,
            search: 'test search',
            type: 'news',
        })

        await waitFor(() => {
            expect(result.current.documents).toEqual(mockDocuments)
        })
    })

    it('should get documents by source', async () => {
        mockDocumentAPI.getDocumentsBySource.mockResolvedValue({ data: mockDocuments })

        const { result } = renderHook(() => useDocuments())

        await act(async () => {
            await result.current.getDocumentsBySource(1)
        })

        expect(mockDocumentAPI.getDocumentsBySource).toHaveBeenCalledWith(1)

        await waitFor(() => {
            expect(result.current.documents).toEqual(mockDocuments)
        })
    })

    it('should refresh documents', async () => {
        mockDocumentAPI.getDocuments.mockResolvedValue({ data: mockDocuments })
        mockDocumentAPI.getDocumentStats.mockResolvedValue({ data: mockStats })

        const { result } = renderHook(() => useDocuments())

        await act(async () => {
            result.current.refreshDocuments()
        })

        await waitFor(() => {
            expect(mockDocumentAPI.getDocuments).toHaveBeenCalledTimes(2) // Once on mount, once on refresh
            expect(mockDocumentAPI.getDocumentStats).toHaveBeenCalledTimes(2)
        })
    })

    it('should handle search error', async () => {
        const errorMessage = 'Search failed'
        mockDocumentAPI.getDocuments.mockRejectedValue(new Error(errorMessage))

        const { result } = renderHook(() => useDocuments())

        await act(async () => {
            await result.current.searchDocuments('test')
        })

        await waitFor(() => {
            expect(result.current.error).toBe(errorMessage)
        })
    })

    it('should handle getDocumentsBySource error', async () => {
        const errorMessage = 'Failed to fetch by source'
        mockDocumentAPI.getDocumentsBySource.mockRejectedValue(new Error(errorMessage))

        const { result } = renderHook(() => useDocuments())

        await act(async () => {
            await result.current.getDocumentsBySource(1)
        })

        await waitFor(() => {
            expect(result.current.error).toBe(errorMessage)
        })
    })

    it('should set loading state during operations', async () => {
        let resolvePromise: (value: any) => void
        const promise = new Promise((resolve) => {
            resolvePromise = resolve
        })
        mockDocumentAPI.getDocuments.mockReturnValue(promise)

        const { result } = renderHook(() => useDocuments())

        act(() => {
            result.current.fetchDocuments()
        })

        expect(result.current.loading).toBe(true)

        act(() => {
            resolvePromise!({ data: mockDocuments })
        })

        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })
    })
})
