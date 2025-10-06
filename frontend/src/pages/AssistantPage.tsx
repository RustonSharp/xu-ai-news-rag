import React, { useState, useRef, useEffect } from 'react'
import { assistantAPI } from '../api'
import {
  Send,
  Bot,
  User,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw
} from 'lucide-react'

// Type definitions
interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: string
  sources?: SearchResult[]
  rawAnswer?: any // Add rawAnswer field to Message interface
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

// Backend response data structure
interface AssistantResponse {
  query: string
  response: string
  answer: string | object
  sources: SearchResult[]
  status: string
  origin?: 'knowledge_base' | 'online_search'
}

const AssistantPage: React.FC = () => {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSearch = async () => {
    if (!query.trim()) return

    setLoading(true)

    try {
      // Chat mode
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user' as const,
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

      // Use AssistantResponse type to process backend response data structure
      // Check if response contains necessary fields
      if (!response) {
        throw new Error('Backend returned empty data')
      }

      // Based on actual response structure, data may be directly in response or in response.data
      const responseData: AssistantResponse = (response.data || response) as AssistantResponse
      const rawAnswer = responseData.answer || `Based on your question "${query}", I found relevant information for you.`
      let rawSources = (responseData as any).raw_answer || [] // Get original source information
      if (rawSources.length == 0 || rawSources[0]['title'] == "" || rawSources[0]['content'] == "Placeholder text") {
        rawSources = []
      }
      console.log('Raw answer data:', rawAnswer)
      console.log('Raw source data:', rawSources)
      console.log('Answer type:', typeof rawAnswer)
      // Use formatAnswer function to format answer
      const answer = formatAnswer(rawAnswer)
      console.log('Formatted answer:', answer)
      // Extract sources from response
      const sources = responseData.sources || []
      const origin = responseData.origin || (sources.length > 0 ? 'knowledge_base' : 'online_search')

      // Generate AI response
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot' as const,
        content: answer,
        timestamp: new Date().toISOString(),
        sources: sources,
        rawAnswer: rawSources, // Save original source information
        origin: origin
      }

      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('Assistant query failed:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot' as const,
        content: 'Sorry, an error occurred during the assistant query. Please try again later.',
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    }

    setLoading(false)
    setQuery('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSearch()
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US')
  }

  // Knowledge search display removed, placeholder kept to avoid misuse

  const clearChat = () => {
    setMessages([])
  }

  // Format backend returned answer - only display answer.output part
  const formatAnswer = (answer: any): string => {
    console.log('formatAnswer input:', answer)
    console.log('formatAnswer input type:', typeof answer)

    // If answer is string, try to parse JSON structure
    if (typeof answer === 'string') {
      console.log('Answer is string, trying to parse JSON')
      try {
        // Try to parse string as object
        const parsedAnswer = JSON.parse(answer)
        console.log('Parse successful:', parsedAnswer)

        // If parse successful and contains output field, return output value
        if (parsedAnswer && typeof parsedAnswer === 'object' && parsedAnswer.hasOwnProperty('output')) {
          console.log('Found output field, value:', parsedAnswer.output)
          return String(parsedAnswer.output);
        }
      } catch (e) {
        console.log('JSON parse failed, trying other methods')
        // If JSON parse fails, try using regex to extract output field
        const outputMatch = answer.match(/'output':\s*'([^']*)'/);
        if (outputMatch && outputMatch[1]) {
          console.log('Regex matched output field, value:', outputMatch[1])
          return outputMatch[1];
        }
      }

      // If cannot parse or no output field, return original string
      console.log('Cannot extract output field, returning original string')
      return answer;
    }

    // If answer is object, only extract output field
    if (typeof answer === 'object' && answer !== null) {
      console.log('Answer is object, checking output field')
      console.log('Object keys:', Object.keys(answer))
      console.log('Has output field:', answer.hasOwnProperty('output'))

      // If has output field, use output field value
      if (answer.hasOwnProperty('output')) {
        console.log('Found output field, value:', answer.output)
        return String(answer.output);
      }

      // If no output field, return empty string or prompt message
      console.log('No output field, returning prompt message')
      return 'No available content';
    }

    // Other cases, convert to string
    console.log('Other cases, convert to string')
    return String(answer);
  }

  return (
    <div className="search-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">AI Assistant</h1>
          <p className="page-subtitle">Intelligent Q&A Assistant based on Knowledge Base</p>
        </div>
      </div>

      <div className="search-container">
        {/* Chat mode */}
        <div className="chat-container">
          <div className="chat-header">
            <div className="chat-info">
              <Bot size={20} />
              <span>AI Assistant</span>
              <span className="status online">Online</span>
            </div>

            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="btn btn-secondary btn-sm"
              >
                <RefreshCw size={14} />
                Clear Chat
              </button>
            )}
          </div>

          <div className="messages-container">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <Bot size={48} />
                <h3>Hello! I'm an AI Assistant</h3>
                <p>I can help you answer questions and analyze information. Please enter your question.</p>

                <div className="example-questions">
                  <h4>Example Questions:</h4>
                  <div className="examples">
                    <button
                      onClick={() => setQuery('What are the applications of artificial intelligence in healthcare?')}
                      className="example-btn"
                    >
                      What are the applications of artificial intelligence in healthcare?
                    </button>
                    <button
                      onClick={() => setQuery('What is the difference between deep learning and machine learning?')}
                      className="example-btn"
                    >
                      What is the difference between deep learning and machine learning?
                    </button>
                    <button
                      onClick={() => setQuery('Development history of GPT models')}
                      className="example-btn"
                    >
                      Development history of GPT models
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="messages">
                {messages.map((message) => (
                  <div key={message.id} className={`message ${message.type}`}>
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
                          // Bot answer uses special format
                          <div className="bot-answer">
                            {message.content.split('\n').map((paragraph, index) => (
                              <p key={index}>{paragraph}</p>
                            ))}
                          </div>
                        ) : (
                          // User message keeps original format
                          message.content.split('\n').map((paragraph, index) => (
                            <p key={index}>{paragraph}</p>
                          ))
                        )}
                      </div>

                      {/* Display raw answer information, only shown when there is rawAnswer and it's a bot message */}
                      {message.type === 'bot' && message.rawAnswer && (
                        <details className="raw-answer-details">
                          <summary>View Raw Answer</summary>
                          <div className="raw-answer-content">
                            {(() => {
                              // If rawAnswer is array (original source information)
                              if (Array.isArray(message.rawAnswer)) {
                                return (
                                  <div className="raw-sources-list">
                                    {message.rawAnswer.map((source, index) => (
                                      <div key={index} className="raw-source-item">
                                        <h5>Source {index + 1}:</h5>
                                        <div className="raw-source-content">
                                          <p><strong>Content:</strong> {source.content || 'No content'}</p>
                                          {source.metadata && (
                                            <div className="raw-source-meta">
                                              <p><strong>Title:</strong> {source.metadata.title || 'No title'}</p>
                                              <p><strong>Author:</strong> {source.metadata.author || 'Unknown'}</p>
                                              <p><strong>Publish Date:</strong> {source.metadata.pub_date || 'Unknown'}</p>
                                              <p><strong>Tags:</strong> {source.metadata.tags || 'No tags'}</p>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                );
                              }

                              // If string, try to parse and extract output
                              if (typeof message.rawAnswer === 'string') {
                                try {
                                  const parsed = JSON.parse(message.rawAnswer);
                                  if (parsed && parsed.hasOwnProperty('output')) {
                                    return <div className="raw-answer-text">{String(parsed.output)}</div>;
                                  }
                                } catch (e) {
                                  // If JSON parse fails, try regex
                                  const outputMatch = message.rawAnswer.match(/'output':\s*'([^']*)'/);
                                  if (outputMatch && outputMatch[1]) {
                                    return <div className="raw-answer-text">{outputMatch[1]}</div>;
                                  }
                                }
                              }
                              // If object and has output field
                              if (typeof message.rawAnswer === 'object' && message.rawAnswer !== null && message.rawAnswer.hasOwnProperty('output')) {
                                return <div className="raw-answer-text">{String(message.rawAnswer.output)}</div>;
                              }
                              // Other cases display original content
                              return <div className="raw-answer-text">{String(message.rawAnswer)}</div>;
                            })()}
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
            )}
          </div>
        </div>

        {/* Input box */}
        <div className="input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={'Enter your question...'}
              className="search-input"
              disabled={loading}
            />

            <button
              onClick={handleSearch}
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
      </div>

      <style>{`
        .search-page {
          max-width: 1000px;
          margin: 0 auto;
          height: calc(100vh - 120px);
          display: flex;
          flex-direction: column;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }

        .mode-switcher {
          display: flex;
          gap: 4px;
          background: var(--elev);
          border-radius: var(--radius);
          padding: 4px;
        }

        .mode-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          border-radius: calc(var(--radius) - 2px);
          transition: all 0.2s ease;
        }

        .mode-btn:hover {
          color: var(--text);
        }

        .mode-btn.active {
          background: var(--bg);
          color: var(--primary);
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .search-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          overflow: hidden;
        }

        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .chat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid var(--border);
          background: var(--panel);
        }

        .chat-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .status {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .status.online {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success);
        }

        .chat-container {
          display: flex;
          flex-direction: column;
          height: 100%;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
          min-height: 0; /* Ensure flex container shrinks correctly */
          /* Ensure scrollbar is always visible */
          scrollbar-width: thin;
          scrollbar-color: #ccc #f1f1f1;
          max-height: calc(100vh - 280px); /* Set maximum height */
          border: 1px solid #eee; /* Add border to make container boundaries more obvious */
        }
        
        /* Webkit browser scrollbar styles */
        .messages-container::-webkit-scrollbar {
          width: 8px;
        }
        
        .messages-container::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 4px;
        }
        
        .messages-container::-webkit-scrollbar-thumb {
          background-color: #ccc;
          border-radius: 4px;
        }
        
        .messages-container::-webkit-scrollbar-thumb:hover {
          background-color: #999;
        }

        .welcome-message {
          text-align: center;
          padding: 60px 20px;
          color: var(--muted);
        }

        .welcome-message h3 {
          margin: 16px 0 8px;
          color: var(--text);
        }

        .example-questions {
          margin-top: 32px;
          text-align: left;
          max-width: 500px;
          margin-left: auto;
          margin-right: auto;
        }

        .example-questions h4 {
          margin-bottom: 16px;
          color: var(--text);
          font-size: 14px;
        }

        .examples {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .example-btn {
          text-align: left;
          padding: 12px 16px;
          background: var(--elev);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          color: var(--text);
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .example-btn:hover {
          background: var(--panel);
          border-color: var(--primary);
        }

        .messages {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .message {
          display: flex;
          gap: 12px;
          align-items: flex-start;
        }

        .message.user {
          flex-direction: row-reverse;
        }

        .message-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: var(--elev);
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .message.user .message-avatar {
          background: var(--primary);
          color: white;
        }

        .message-content {
          flex: 1;
          max-width: 70%;
        }

        .message.user .message-content {
          text-align: right;
        }

        .message-text {
          background: var(--panel);
          padding: 12px 16px;
          border-radius: 12px;
          margin-bottom: 8px;
        }

        .message.user .message-text {
          background: var(--primary);
          color: white;
        }

        .message-text p {
          margin: 0 0 8px;
          line-height: 1.5;
        }

        .message-text p:last-child {
          margin-bottom: 0;
        }

        /* Special styles for bot answers */
        .bot-answer {
          font-size: 15px;
          line-height: 1.6;
        }

        .bot-answer p {
          margin: 0 0 12px;
        }

        .bot-answer p:last-child {
          margin-bottom: 0;
        }

        .bot-answer code {
          background: rgba(0, 0, 0, 0.05);
          padding: 2px 4px;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
          font-size: 14px;
        }

        .bot-answer pre {
          background: rgba(0, 0, 0, 0.05);
          padding: 12px;
          border-radius: 6px;
          overflow-x: auto;
          margin: 12px 0;
        }

        .bot-answer ul, .bot-answer ol {
          margin: 12px 0;
          padding-left: 20px;
        }

        .bot-answer li {
          margin: 6px 0;
        }

        .message-sources {
          margin-top: 16px;
          padding: 16px;
          background: var(--elev);
          border-radius: 8px;
        }

        .message-sources h4 {
          margin: 0 0 12px;
          font-size: 14px;
          color: var(--text);
        }

        .sources-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .source-item {
          display: flex;
          gap: 12px;
          padding: 12px;
          background: var(--bg);
          border-radius: 6px;
          border: 1px solid var(--border);
        }

        .source-icon {
          font-size: 16px;
          flex-shrink: 0;
        }

        .source-info {
          flex: 1;
        }

        .source-info h5 {
          margin: 0 0 4px;
          font-size: 14px;
          color: var(--text);
        }

        .source-info p {
          margin: 0 0 8px;
          font-size: 12px;
          color: var(--muted);
          line-height: 1.4;
        }

        .source-meta {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .relevance {
          font-size: 11px;
          color: var(--success);
          font-weight: 500;
        }

        .source-link {
          display: flex;
          align-items: center;
          gap: 4px;
          color: var(--primary);
          text-decoration: none;
          font-size: 11px;
        }

        .source-link:hover {
          text-decoration: underline;
        }

        .message-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-top: 8px;
        }

        .message.user .message-actions {
          flex-direction: row-reverse;
        }

        .message-time {
          font-size: 12px;
          color: var(--muted);
        }

        .action-buttons {
          display: flex;
          gap: 4px;
        }

        .action-btn {
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .action-btn:hover {
          background: var(--elev);
          color: var(--text);
        }

        .typing-indicator {
          display: flex;
          gap: 4px;
          padding: 12px 16px;
          background: var(--panel);
          border-radius: 12px;
        }

        .typing-indicator span {
          width: 8px;
          height: 8px;
          background: var(--muted);
          border-radius: 50%;
          animation: typing 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% {
            transform: translateY(0);
            opacity: 0.5;
          }
          30% {
            transform: translateY(-10px);
            opacity: 1;
          }
        }

        .search-results-container {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .search-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid var(--border);
          background: var(--panel);
        }

        .search-stats {
          color: var(--muted);
          font-size: 14px;
        }

        .filters-panel {
          padding: 20px;
          background: var(--elev);
          border-bottom: 1px solid var(--border);
        }

        .filters-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .search-results {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
        }

        .results-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .result-item {
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 20px;
          background: var(--panel);
          transition: all 0.2s ease;
        }

        .result-item:hover {
          border-color: var(--primary);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .result-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 12px;
        }

        .result-title {
          display: flex;
          align-items: center;
          gap: 12px;
          flex: 1;
        }

        .result-icon {
          font-size: 18px;
        }

        .result-title h3 {
          margin: 0;
          color: var(--text);
          font-size: 16px;
          flex: 1;
        }

        .relevance-score {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success);
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .result-actions {
          display: flex;
          gap: 8px;
        }

        .result-content p {
          margin: 0 0 16px;
          color: var(--muted);
          line-height: 1.6;
        }

        .result-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
          flex-wrap: wrap;
          gap: 12px;
        }

        .result-tags {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }

        .tag {
          background: rgba(91, 157, 255, 0.1);
          color: var(--primary);
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .result-info {
          display: flex;
          gap: 16px;
          align-items: center;
        }

        .result-date {
          display: flex;
          align-items: center;
          gap: 4px;
          color: var(--muted);
          font-size: 12px;
        }

        .result-link {
          display: flex;
          align-items: center;
          gap: 4px;
          color: var(--primary);
          text-decoration: none;
          font-size: 12px;
        }

        .result-link:hover {
          text-decoration: underline;
        }

        .empty-results,
        .search-placeholder {
          text-align: center;
          padding: 60px 20px;
          color: var(--muted);
        }

        .empty-results h3,
        .search-placeholder h3 {
          margin: 16px 0 8px;
          color: var(--text);
        }

        .input-container {
          padding: 20px;
          border-top: 1px solid var(--border);
          background: var(--panel);
        }

        .input-wrapper {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .search-input {
          flex: 1;
          padding: 12px 16px;
          border: 1px solid var(--border);
          border-radius: var(--radius);
          background: var(--bg);
          color: var(--text);
          font-size: 14px;
        }

        .search-input:focus {
          outline: none;
          border-color: var(--primary);
        }

        .send-btn {
          padding: 12px;
          background: var(--primary);
          border: none;
          border-radius: var(--radius);
          color: white;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .send-btn:hover:not(:disabled) {
          background: var(--primary-dark);
        }

        .send-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .spinning {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            gap: 16px;
          }

          .message-content {
            max-width: 85%;
          }

          .result-header {
            flex-direction: column;
            gap: 12px;
          }

          .result-meta {
            flex-direction: column;
            align-items: stretch;
          }

          .filters-grid {
            grid-template-columns: 1fr;
          }
        }
        
        .raw-answer-details {
          margin-top: 12px;
        }
        
        .raw-answer-details summary {
          cursor: pointer;
          font-weight: 500;
          color: var(--primary);
          padding: 8px 0;
        }
        
        .raw-answer-content {
          background: rgba(0, 0, 0, 0.03);
          border-radius: 6px;
          padding: 12px;
          margin-top: 8px;
          border: 1px solid var(--border);
        }

        .raw-answer-content pre {
          margin: 0;
          white-space: pre-wrap;
          word-break: break-all;
          font-size: 12px;
          line-height: 1.4;
        }

        .raw-answer-text {
          white-space: pre-wrap;
          word-break: break-word;
          font-size: 13px;
          line-height: 1.5;
          color: var(--text);
        }
        
        .raw-sources-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        
        .raw-source-item {
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 16px;
          background: var(--elev);
        }
        
        .raw-source-item h5 {
          margin: 0 0 12px;
          color: var(--primary);
          font-size: 14px;
          font-weight: 600;
        }
        
        .raw-source-content p {
          margin: 0 0 8px;
          font-size: 13px;
          line-height: 1.5;
        }
        
        .raw-source-content p:last-child {
          margin-bottom: 0;
        }
        
        .raw-source-meta {
          margin-top: 12px;
          padding-top: 12px;
          border-top: 1px solid var(--border);
        }
        
        .raw-source-meta p {
          margin: 0 0 4px;
          font-size: 12px;
          color: var(--muted);
        }
        
        .raw-source-meta p:last-child {
          margin-bottom: 0;
        }
        
      `}</style>
    </div>
  )
}

export default AssistantPage