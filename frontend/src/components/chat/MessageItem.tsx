import React from 'react'
import { Bot, User, Copy, ThumbsUp, ThumbsDown } from 'lucide-react'
import SourcesList from './SourcesList'

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

interface MessageItemProps {
    message: Message
}

const MessageItem: React.FC<MessageItemProps> = ({ message }) => {
    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        alert('Copied to clipboard')
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('en-US')
    }

    return (
        <div className={`message ${message.type}`}>
            <div className="message-avatar">
                {message.type === 'user' ? <User size={20} /> : <Bot size={20} />}
            </div>
            <div className="message-content">
                {message.type === 'bot' && (
                    <div style={{ marginBottom: 6 }}>
                        <span style={{
                            fontSize: 12,
                            padding: '2px 8px',
                            borderRadius: 12,
                            background: 'var(--elev)',
                            color: 'var(--muted)'
                        }}>
                            {message.origin === 'online_search' ? 'Source: Online Search' : 'Source: Knowledge Base'}
                        </span>
                    </div>
                )}
                <div className="message-text">
                    {message.type === 'bot' ? (
                        <div className="bot-answer">
                            {message.content.split('\n').map((paragraph, index) => (
                                <p key={index}>{paragraph}</p>
                            ))}
                        </div>
                    ) : (
                        message.content.split('\n').map((paragraph, index) => (
                            <p key={index}>{paragraph}</p>
                        ))
                    )}
                </div>

                {message.type === 'bot' && message.sources && message.sources.length > 0 && (
                    <SourcesList sources={message.sources} />
                )}

                {message.type === 'bot' && message.rawAnswer && (
                    <details className="raw-answer-details">
                        <summary>View Raw Answer</summary>
                        <div className="raw-answer-content">
                            <SourcesList sources={message.rawAnswer} isRawAnswer={true} />
                        </div>
                    </details>
                )}

                <div className="message-actions">
                    <span className="message-time">
                        {formatDate(message.timestamp)}
                    </span>

                    {message.type === 'bot' && (
                        <div className="action-buttons">
                            <button
                                onClick={() => copyToClipboard(message.content)}
                                className="action-btn"
                                title="Copy"
                            >
                                <Copy size={14} />
                            </button>
                            <button className="action-btn" title="Like">
                                <ThumbsUp size={14} />
                            </button>
                            <button className="action-btn" title="Dislike">
                                <ThumbsDown size={14} />
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default MessageItem
