import { useState, useCallback } from 'react'
import { assistantAPI } from '../api'

interface Message {
    id: string
    type: 'user' | 'bot'
    content: string
    timestamp: string
    sources?: SearchResult[]
    rawAnswer?: any
    origin?: 'knowledge_base' | 'online_search'
}

interface SearchResult {
    id: string
    title: string
    content: string
    url: string
    score: number
    type: string
    source: string
    relevance: number
    timestamp: string
}

export const useChat = () => {
    const [messages, setMessages] = useState<Message[]>([])
    const [loading, setLoading] = useState(false)

    const formatAnswer = useCallback((answer: any): string => {
        // If answer is string, try to parse JSON structure
        if (typeof answer === 'string') {
            try {
                const parsedAnswer = JSON.parse(answer)
                if (parsedAnswer && typeof parsedAnswer === 'object' && parsedAnswer.hasOwnProperty('output')) {
                    return String(parsedAnswer.output)
                }
            } catch (e) {
                // If JSON parse fails, try using regex to extract output field
                const outputMatch = answer.match(/'output':\s*'([^']*)'/)
                if (outputMatch && outputMatch[1]) {
                    return outputMatch[1]
                }
            }
            return answer
        }

        // If answer is object, only extract output field
        if (typeof answer === 'object' && answer !== null) {
            if (answer.hasOwnProperty('output')) {
                return String(answer.output)
            }
            return 'No available content'
        }

        return String(answer)
    }, [])

    const sendMessage = useCallback(async (query: string) => {
        if (!query.trim()) return

        setLoading(true)

        try {
            // Add user message
            const userMessage: Message = {
                id: Date.now().toString(),
                type: 'user',
                content: query,
                timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, userMessage])

            // Call assistant API
            const response = await assistantAPI.query({
                query: query,
                options: {
                    use_knowledge_base: true,
                    use_online_search: false
                }
            })

            console.log('Assistant query response:', response)

            // Process response
            if (!response) {
                throw new Error('Backend returned empty data')
            }

            const responseData = (response.data || response) as any
            const rawAnswer = responseData.answer || `Based on your question "${query}", I found relevant information for you.`
            let rawSources = responseData.raw_answer || []

            if (rawSources.length == 0 || rawSources[0]?.['title'] == "" || rawSources[0]?.['content'] == "Placeholder text") {
                rawSources = []
            }

            const answer = formatAnswer(rawAnswer)
            const sources = responseData.sources || []
            const origin = responseData.origin || (sources.length > 0 ? 'knowledge_base' : 'online_search')

            // Generate AI response
            const aiResponse: Message = {
                id: (Date.now() + 1).toString(),
                type: 'bot',
                content: answer,
                timestamp: new Date().toISOString(),
                sources: sources,
                rawAnswer: rawSources,
                origin: origin
            }

            setMessages(prev => [...prev, aiResponse])
        } catch (error) {
            console.error('Assistant query failed:', error)
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                type: 'bot',
                content: 'Sorry, an error occurred during the assistant query. Please try again later.',
                timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, errorMessage])
        }

        setLoading(false)
    }, [formatAnswer])

    const clearChat = useCallback(() => {
        setMessages([])
    }, [])

    const handleExampleClick = useCallback((query: string) => {
        sendMessage(query)
    }, [sendMessage])

    return {
        messages,
        loading,
        sendMessage,
        clearChat,
        handleExampleClick
    }
}
