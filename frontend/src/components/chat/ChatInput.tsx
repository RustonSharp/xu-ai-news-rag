import React, { useState, useRef } from 'react'
import { Send, RefreshCw } from 'lucide-react'

interface ChatInputProps {
    onSendMessage: (message: string) => void
    loading: boolean
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, loading }) => {
    const [query, setQuery] = useState('')
    const inputRef = useRef<HTMLInputElement>(null)

    const handleSubmit = () => {
        if (!query.trim()) return
        onSendMessage(query)
        setQuery('')
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit()
        }
    }

    return (
        <div className="input-container">
            <div className="input-wrapper">
                <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Enter your question..."
                    className="search-input"
                    disabled={loading}
                />

                <button
                    onClick={handleSubmit}
                    disabled={!query.trim() || loading}
                    className="send-btn"
                >
                    {loading ? (
                        <RefreshCw size={20} className="spinning" />
                    ) : (
                        <Send size={20} />
                    )}
                </button>
            </div>
        </div>
    )
}

export default ChatInput
