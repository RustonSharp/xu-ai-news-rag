import React, { useRef, useEffect } from 'react'
import { Bot, User } from 'lucide-react'
import MessageItem from './MessageItem'

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

interface MessageListProps {
    messages: Message[]
    loading: boolean
}

const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    return (
        <div className="messages">
            {messages.map((message) => (
                <MessageItem key={message.id} message={message} />
            ))}
            {loading && (
                <div className="message assistant">
                    <div className="message-avatar">
                        <Bot size={20} />
                    </div>
                    <div className="message-content">
                        <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            )}
            <div ref={messagesEndRef} />
        </div>
    )
}

export default MessageList
