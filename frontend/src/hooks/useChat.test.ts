import { renderHook, act, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useChat } from './useChat'
import { assistantAPI } from '@/api'

// Mock the assistantAPI
vi.mock('@/api', () => ({
    assistantAPI: {
        query: vi.fn(),
    },
}))

const mockAssistantAPI = vi.mocked(assistantAPI)

describe('useChat', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should initialize with empty messages and not loading', () => {
        const { result } = renderHook(() => useChat())

        expect(result.current.messages).toEqual([])
        expect(result.current.loading).toBe(false)
    })

    it('should send message successfully', async () => {
        const mockResponse = {
            data: {
                answer: 'Test answer',
                sources: [],
                origin: 'knowledge_base'
            }
        }

        mockAssistantAPI.query.mockResolvedValue(mockResponse)

        const { result } = renderHook(() => useChat())

        await act(async () => {
            await result.current.sendMessage('Test query')
        })

        await waitFor(() => {
            expect(result.current.messages).toHaveLength(2)
            expect(result.current.messages[0].type).toBe('user')
            expect(result.current.messages[0].content).toBe('Test query')
            expect(result.current.messages[1].type).toBe('bot')
            expect(result.current.messages[1].content).toBe('Test answer')
        })

        expect(mockAssistantAPI.query).toHaveBeenCalledWith({
            query: 'Test query',
            options: {
                use_knowledge_base: true,
                use_online_search: false
            }
        })
    })

    it('should handle API error gracefully', async () => {
        mockAssistantAPI.query.mockRejectedValue(new Error('API Error'))

        const { result } = renderHook(() => useChat())

        await act(async () => {
            await result.current.sendMessage('Test query')
        })

        await waitFor(() => {
            expect(result.current.messages).toHaveLength(2)
            expect(result.current.messages[1].type).toBe('bot')
            expect(result.current.messages[1].content).toContain('Sorry, an error occurred')
        })
    })

    it('should not send empty message', async () => {
        const { result } = renderHook(() => useChat())

        await act(async () => {
            await result.current.sendMessage('')
        })

        await act(async () => {
            await result.current.sendMessage('   ')
        })

        expect(result.current.messages).toHaveLength(0)
        expect(mockAssistantAPI.query).not.toHaveBeenCalled()
    })

    it('should clear chat messages', () => {
        const { result } = renderHook(() => useChat())

        // Add some messages first
        act(() => {
            result.current.sendMessage('Test query')
        })

        // Clear messages
        act(() => {
            result.current.clearChat()
        })

        expect(result.current.messages).toEqual([])
    })

    it('should handle example click', async () => {
        const mockResponse = {
            data: {
                answer: 'Example answer',
                sources: [],
                origin: 'knowledge_base'
            }
        }

        mockAssistantAPI.query.mockResolvedValue(mockResponse)

        const { result } = renderHook(() => useChat())

        await act(async () => {
            result.current.handleExampleClick('Example query')
        })

        await waitFor(() => {
            expect(result.current.messages).toHaveLength(2)
            expect(result.current.messages[0].content).toBe('Example query')
        })
    })

    it('should format answer correctly for string response', () => {
        const { result } = renderHook(() => useChat())

        const mockResponse = {
            data: {
                answer: 'Simple string answer',
                sources: [],
                origin: 'knowledge_base'
            }
        }

        mockAssistantAPI.query.mockResolvedValue(mockResponse)

        act(async () => {
            await result.current.sendMessage('Test')
        })

        waitFor(() => {
            expect(result.current.messages[1].content).toBe('Simple string answer')
        })
    })

    it('should format answer correctly for JSON string response', () => {
        const { result } = renderHook(() => useChat())

        const mockResponse = {
            data: {
                answer: '{"output": "JSON formatted answer"}',
                sources: [],
                origin: 'knowledge_base'
            }
        }

        mockAssistantAPI.query.mockResolvedValue(mockResponse)

        act(async () => {
            await result.current.sendMessage('Test')
        })

        waitFor(() => {
            expect(result.current.messages[1].content).toBe('JSON formatted answer')
        })
    })

    it('should handle object response with output field', () => {
        const { result } = renderHook(() => useChat())

        const mockResponse = {
            data: {
                answer: { output: 'Object output answer' },
                sources: [],
                origin: 'knowledge_base'
            }
        }

        mockAssistantAPI.query.mockResolvedValue(mockResponse)

        act(async () => {
            await result.current.sendMessage('Test')
        })

        waitFor(() => {
            expect(result.current.messages[1].content).toBe('Object output answer')
        })
    })
})
