import React from 'react'
import { Bot, RefreshCw } from 'lucide-react'
import MessageList from './MessageList'
import ChatInput from './ChatInput'
import WelcomeScreen from './WelcomeScreen'

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

interface ChatContainerProps {
    messages: Message[]
    loading: boolean
    onSendMessage: (message: string) => void
    onClearChat: () => void
    onExampleClick: (query: string) => void
}

const ChatContainer: React.FC<ChatContainerProps> = ({
    messages,
    loading,
    onSendMessage,
    onClearChat,
    onExampleClick
}) => {
    return (
        <div className="chat-container">
            <div className="chat-header">
                <div className="chat-info">
                    <Bot size={20} />
                    <span>AI Assistant</span>
                    <span className="status online">Online</span>
                </div>

                {messages.length > 0 && (
                    <button
                        onClick={onClearChat}
                        className="btn btn-secondary btn-sm"
                    >
                        <RefreshCw size={14} />
                        Clear Chat
                    </button>
                )}
            </div>

            <div className="messages-container">
                {messages.length === 0 ? (
                    <WelcomeScreen onExampleClick={onExampleClick} />
                ) : (
                    <MessageList messages={messages} loading={loading} />
                )}
            </div>

            <ChatInput onSendMessage={onSendMessage} loading={loading} />
        </div>
    )
}

export default ChatContainer
