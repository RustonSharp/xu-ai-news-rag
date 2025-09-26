import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import {
  Search,
  Send,
  Bot,
  User,
  FileText,
  ExternalLink,
  Copy,
  ThumbsUp,
  ThumbsDown,
  RefreshCw,
  Filter,
  Clock,
  Bookmark,
  Share,
  MoreHorizontal
} from 'lucide-react'

const SearchPage = () => {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchResults, setSearchResults] = useState([])
  const [searchMode, setSearchMode] = useState('chat') // 'chat' or 'search'
  const [filters, setFilters] = useState({
    dateRange: '',
    source: '',
    type: ''
  })
  const [showFilters, setShowFilters] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Simulated search results
  const mockSearchResults = [
    {
      id: 1,
      title: 'Research on GPT-4 Applications in Medical Diagnosis',
      content: 'GPT-4, as the latest large language model, shows great potential in medical diagnosis. Studies have shown that GPT-4 can accurately identify various disease symptoms and provide preliminary diagnostic suggestions...',
      source: 'medical_journal',
      type: 'pdf',
      url: 'https://example.com/gpt4-medical.pdf',
      date: '2024-01-15T10:30:00Z',
      relevance: 0.95,
      tags: ['GPT-4', 'Medical', 'Diagnosis', 'AI']
    },
    {
      id: 2,
      title: 'Latest Advances of AI in Financial Risk Control',
      content: 'With the continuous development of AI technology, financial institutions are increasingly adopting AI to enhance risk control capabilities. Machine learning algorithms can analyze large amounts of transaction data in real time...',
      source: 'finance_news',
      type: 'html',
      url: 'https://example.com/ai-finance.html',
      date: '2024-01-14T15:20:00Z',
      relevance: 0.89,
      tags: ['AI', 'Finance', 'Risk Control']
    }
  ]

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSearch = async () => {
    if (!query.trim()) return

    setLoading(true)

    if (searchMode === 'chat') {
      // Add user message
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: query,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])

      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000))

        // Generate AI response
        const aiResponse = {
          id: Date.now() + 1,
          type: 'assistant',
          content: `Based on your question "${query}", I've found the following relevant information:\n\nAccording to the latest research materials, the technology related to ${query} is developing very rapidly. Key advances include:\n\n1. **Technical Breakthroughs**: Significant improvements in algorithm optimization and model architecture\n2. **Application Scenarios**: Widely applied across multiple industry domains\n3. **Future Trends**: Expected to continue its rapid growth trajectory\n\nThis information is sourced from authoritative documents and the latest research reports in our knowledge base. If you need more detailed information, I can provide specific document references for you.`,
          timestamp: new Date().toISOString(),
          sources: mockSearchResults.slice(0, 2)
        }

        setMessages(prev => [...prev, aiResponse])
      } catch (error) {
        console.error('Search failed:', error)
        const errorMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: 'Sorry, an error occurred during the search. Please try again later.',
          timestamp: new Date().toISOString(),
          error: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } else {
      // Semantic search mode
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))

        // Filter search results
        let filteredResults = mockSearchResults.filter(result =>
          result.title.toLowerCase().includes(query.toLowerCase()) ||
          result.content.toLowerCase().includes(query.toLowerCase()) ||
          result.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
        )

        // Apply filter conditions
        if (filters.source) {
          filteredResults = filteredResults.filter(r => r.source === filters.source)
        }
        if (filters.type) {
          filteredResults = filteredResults.filter(r => r.type === filters.type)
        }

        setSearchResults(filteredResults)
      } catch (error) {
        console.error('Search failed:', error)
        setSearchResults([])
      }
    }

    setLoading(false)
    setQuery('')
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSearch()
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard')
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US')
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'pdf': return '📄'
      case 'html': return '🌐'
      case 'markdown': return '📝'
      default: return '📄'
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  return (
    <div className="search-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Intelligent Search</h1>
          <p className="page-subtitle">Semantic-based intelligent search and Q&A</p>
        </div>
        <div className="mode-switcher">
          <button
            onClick={() => setSearchMode('chat')}
            className={`mode-btn ${searchMode === 'chat' ? 'active' : ''}`}
          >
            <Bot size={16} />
            AI Q&A
          </button>
          <button
            onClick={() => setSearchMode('search')}
            className={`mode-btn ${searchMode === 'search' ? 'active' : ''}`}
          >
            <Search size={16} />
            Semantic Search
          </button>
        </div>
      </div>
      <div className="search-container">
        {searchMode === 'chat' ? (
          // Chat mode
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
                  Clear Conversation
                </button>
              )}
            </div>
            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="welcome-message">
                  <Bot size={48} />
                  <h3>Hello! I am your AI assistant</h3>
                  <p>I can help you search and analyze information in the knowledge base. Please enter your question.</p>
                  <div className="example-questions">
                    <h4>Example Questions:</h4>
                    <div className="examples">
                      <button
                        onClick={() => setQuery('What are the applications of AI in the medical field?')}
                        className="example-btn"
                      >
                        What are the applications of AI in the medical field?
                      </button>
                      <button
                        onClick={() => setQuery('What is the difference between deep learning and machine learning?')}
                        className="example-btn"
                      >
                        What is the difference between deep learning and machine learning?
                      </button>
                      <button
                        onClick={() => setQuery('The development history of GPT models')}
                        className="example-btn"
                      >
                        The development history of GPT models
                      </button>

                    </div>
                  </div>
                </div>
              ) : (
                <div className="messages">
                  {messages.map((message) => (
                    <div key={message.id} className={`message ${message.type}`}>
                      <div className="message-avatar">
                        {message.type === 'user' ? (
                          <User size={20} />
                        ) : (
                          <Bot size={20} />
                        )}
                      </div>

                      <div className="message-content">
                        <div className="message-text">
                          {message.content.split('\n').map((line, index) => (
                            <p key={index}>{line}</p>
                          ))}
                        </div>

                        {message.sources && (
                          <div className="message-sources">
                            <h4>Related Documents:</h4>
                            <div className="sources-list">
                              {message.sources.map((source) => (
                                <div key={source.id} className="source-item">
                                  <div className="source-icon">
                                    {getTypeIcon(source.type)}
                                  </div>
                                  <div className="source-info">
                                    <h5>{source.title}</h5>
                                    <p>{source.content.substring(0, 100)}...</p>
                                    <div className="source-meta">
                                      <span className="relevance">
                                        Relevance: {Math.round(source.relevance * 100)}%
                                      </span>
                                      {source.url && (
                                        <a
                                          href={source.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="source-link"
                                        >
                                          <ExternalLink size={12} />
                                          View Original
                                        </a>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="message-actions">
                          <span className="message-time">
                            {formatDate(message.timestamp)}
                          </span>

                          {message.type === 'assistant' && (
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
        ) : (
          // Search mode
          <div className="search-results-container">
            <div className="search-header">
              <div className="search-filters">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`btn btn-secondary ${showFilters ? 'active' : ''}`}
                >
                  <Filter size={16} />
                  Filter
                </button>
              </div>

              {searchResults.length > 0 && (
                <div className="search-stats">
                  Found {searchResults.length} relevant results
                </div>
              )}
            </div>

            {showFilters && (
              <div className="filters-panel">
                <div className="filters-grid">
                  <div className="form-group">
                    <label className="form-label">Source</label>
                    <select
                      value={filters.source}
                      onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                      className="input"
                    >
                      <option value="">All Sources</option>
                      <option value="medical_journal">Medical Journal</option>
                      <option value="finance_news">Finance News</option>
                      <option value="tech_blog">Tech Blog</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Document Type</label>
                    <select
                      value={filters.type}
                      onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                      className="input"
                    >
                      <option value="">All Types</option>
                      <option value="pdf">PDF</option>
                      <option value="html">HTML</option>
                      <option value="markdown">Markdown</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">Time Range</label>
                    <select
                      value={filters.dateRange}
                      onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
                      className="input"
                    >
                      <option value="">All Time</option>
                      <option value="1d">Last 1 day</option>
                      <option value="1w">Last 1 week</option>
                      <option value="1m">Last 1 month</option>
                      <option value="3m">Last 3 months</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            <div className="search-results">
              {loading ? (
                <div className="loading">
                  <div className="spinner" />
                  Searching...
                </div>
              ) : searchResults.length > 0 ? (
                <div className="results-list">
                  {searchResults.map((result) => (
                    <div key={result.id} className="result-item">
                      <div className="result-header">
                        <div className="result-title">
                          <span className="result-icon">{getTypeIcon(result.type)}</span>
                          <h3>{result.title}</h3>
                          <span className="relevance-score">
                            {Math.round(result.relevance * 100)}%
                          </span>
                        </div>

                        <div className="result-actions">
                          <button className="action-btn" title="Bookmark">
                            <Bookmark size={16} />
                          </button>
                          <button className="action-btn" title="Share">
                            <Share size={16} />
                          </button>
                          <button className="action-btn" title="More">
                            <MoreHorizontal size={16} />
                          </button>
                        </div>
                      </div>

                      <div className="result-content">
                        <p>{result.content}</p>
                      </div>

                      <div className="result-meta">
                        <div className="result-tags">
                          {result.tags.map((tag, index) => (
                            <span key={index} className="tag">{tag}</span>
                          ))}
                        </div>

                        <div className="result-info">
                          <span className="result-date">
                            <Clock size={12} />
                            {formatDate(result.date)}
                          </span>

                          {result.url && (
                            <a
                              href={result.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="result-link"
                            >
                              <ExternalLink size={12} />
                              View Original
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : query && !loading ? (
                <div className="empty-results">
                  <Search size={48} />
                  <h3>No Relevant Results Found</h3>
                  <p>Please try different keywords or adjust filter conditions</p>
                </div>
              ) : (
                <div className="search-placeholder">
                  <Search size={48} />
                  <h3>Start Your Search</h3>
                  <p>Enter keywords to search for relevant documents in the knowledge base</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Input box */}
        <div className="input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={searchMode === 'chat' ? 'Enter your question...' : 'Enter search keywords...'}
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
      <style jsx>{`
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
        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
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
      `}</style>
    </div>
  )
}

export default SearchPage