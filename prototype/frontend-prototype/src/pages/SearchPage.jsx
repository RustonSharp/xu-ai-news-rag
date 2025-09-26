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

  // 模拟搜索结果
  const mockSearchResults = [
    {
      id: 1,
      title: 'GPT-4在医疗诊断中的应用研究',
      content: 'GPT-4作为最新的大语言模型，在医疗诊断领域展现出了巨大的潜力。研究表明，GPT-4能够准确识别多种疾病症状，并提供初步的诊断建议...',
      source: 'medical_journal',
      type: 'pdf',
      url: 'https://example.com/gpt4-medical.pdf',
      date: '2024-01-15T10:30:00Z',
      relevance: 0.95,
      tags: ['GPT-4', '医疗', '诊断', 'AI']
    },
    {
      id: 2,
      title: '人工智能在金融风控中的最新进展',
      content: '随着人工智能技术的不断发展，金融机构越来越多地采用AI技术来提升风险控制能力。机器学习算法能够实时分析大量交易数据...',
      source: 'finance_news',
      type: 'html',
      url: 'https://example.com/ai-finance-risk',
      date: '2024-01-14T15:20:00Z',
      relevance: 0.87,
      tags: ['人工智能', '金融', '风控', '机器学习']
    },
    {
      id: 3,
      title: '深度学习在自然语言处理中的突破',
      content: '近年来，深度学习技术在自然语言处理领域取得了重大突破。从BERT到GPT系列模型，每一次技术进步都推动了NLP应用的边界...',
      source: 'tech_blog',
      type: 'markdown',
      url: null,
      date: '2024-01-13T09:15:00Z',
      relevance: 0.82,
      tags: ['深度学习', 'NLP', 'BERT', 'GPT']
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
      // 添加用户消息
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: query,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])
      
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // 生成AI回复
        const aiResponse = {
          id: Date.now() + 1,
          type: 'assistant',
          content: `基于您的问题"${query}"，我为您找到了以下相关信息：\n\n根据最新的研究资料，${query}相关的技术发展非常迅速。主要的进展包括：\n\n1. **技术突破**：在算法优化和模型架构方面有显著改进\n2. **应用场景**：在多个行业领域得到广泛应用\n3. **未来趋势**：预计将继续保持快速发展态势\n\n这些信息来源于我们知识库中的权威文档和最新研究报告。如果您需要更详细的信息，我可以为您提供具体的文档引用。`,
          timestamp: new Date().toISOString(),
          sources: mockSearchResults.slice(0, 2)
        }
        
        setMessages(prev => [...prev, aiResponse])
      } catch (error) {
        console.error('搜索失败:', error)
        const errorMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: '抱歉，搜索过程中出现了错误，请稍后重试。',
          timestamp: new Date().toISOString(),
          error: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } else {
      // 语义搜索模式
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 过滤搜索结果
        let filteredResults = mockSearchResults.filter(result => 
          result.title.toLowerCase().includes(query.toLowerCase()) ||
          result.content.toLowerCase().includes(query.toLowerCase()) ||
          result.tags.some(tag => tag.toLowerCase().includes(query.toLowerCase()))
        )
        
        // 应用筛选条件
        if (filters.source) {
          filteredResults = filteredResults.filter(r => r.source === filters.source)
        }
        if (filters.type) {
          filteredResults = filteredResults.filter(r => r.type === filters.type)
        }
        
        setSearchResults(filteredResults)
      } catch (error) {
        console.error('搜索失败:', error)
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
    alert('已复制到剪贴板')
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('zh-CN')
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
          <h1 className="page-title">智能检索</h1>
          <p className="page-subtitle">基于语义理解的智能搜索和问答</p>
        </div>
        
        <div className="mode-switcher">
          <button
            onClick={() => setSearchMode('chat')}
            className={`mode-btn ${searchMode === 'chat' ? 'active' : ''}`}
          >
            <Bot size={16} />
            智能问答
          </button>
          <button
            onClick={() => setSearchMode('search')}
            className={`mode-btn ${searchMode === 'search' ? 'active' : ''}`}
          >
            <Search size={16} />
            语义搜索
          </button>
        </div>
      </div>

      <div className="search-container">
        {searchMode === 'chat' ? (
          // 聊天模式
          <div className="chat-container">
            <div className="chat-header">
              <div className="chat-info">
                <Bot size={20} />
                <span>AI助手</span>
                <span className="status online">在线</span>
              </div>
              
              {messages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="btn btn-secondary btn-sm"
                >
                  <RefreshCw size={14} />
                  清空对话
                </button>
              )}
            </div>

            <div className="messages-container">
              {messages.length === 0 ? (
                <div className="welcome-message">
                  <Bot size={48} />
                  <h3>您好！我是AI助手</h3>
                  <p>我可以帮您搜索和分析知识库中的信息，请输入您的问题。</p>
                  
                  <div className="example-questions">
                    <h4>示例问题：</h4>
                    <div className="examples">
                      <button
                        onClick={() => setQuery('人工智能在医疗领域的应用有哪些？')}
                        className="example-btn"
                      >
                        人工智能在医疗领域的应用有哪些？
                      </button>
                      <button
                        onClick={() => setQuery('深度学习和机器学习的区别是什么？')}
                        className="example-btn"
                      >
                        深度学习和机器学习的区别是什么？
                      </button>
                      <button
                        onClick={() => setQuery('GPT模型的发展历程')}
                        className="example-btn"
                      >
                        GPT模型的发展历程
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
                            <h4>相关文档：</h4>
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
                                        相关度: {Math.round(source.relevance * 100)}%
                                      </span>
                                      {source.url && (
                                        <a
                                          href={source.url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="source-link"
                                        >
                                          <ExternalLink size={12} />
                                          查看原文
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
                                title="复制"
                              >
                                <Copy size={14} />
                              </button>
                              <button className="action-btn" title="点赞">
                                <ThumbsUp size={14} />
                              </button>
                              <button className="action-btn" title="点踩">
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
          // 搜索模式
          <div className="search-results-container">
            <div className="search-header">
              <div className="search-filters">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className={`btn btn-secondary ${showFilters ? 'active' : ''}`}
                >
                  <Filter size={16} />
                  筛选
                </button>
              </div>
              
              {searchResults.length > 0 && (
                <div className="search-stats">
                  找到 {searchResults.length} 个相关结果
                </div>
              )}
            </div>

            {showFilters && (
              <div className="filters-panel">
                <div className="filters-grid">
                  <div className="form-group">
                    <label className="form-label">来源</label>
                    <select
                      value={filters.source}
                      onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                      className="input"
                    >
                      <option value="">全部来源</option>
                      <option value="medical_journal">医学期刊</option>
                      <option value="finance_news">金融新闻</option>
                      <option value="tech_blog">技术博客</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">文档类型</label>
                    <select
                      value={filters.type}
                      onChange={(e) => setFilters(prev => ({ ...prev, type: e.target.value }))}
                      className="input"
                    >
                      <option value="">全部类型</option>
                      <option value="pdf">PDF</option>
                      <option value="html">HTML</option>
                      <option value="markdown">Markdown</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label className="form-label">时间范围</label>
                    <select
                      value={filters.dateRange}
                      onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
                      className="input"
                    >
                      <option value="">全部时间</option>
                      <option value="1d">最近1天</option>
                      <option value="1w">最近1周</option>
                      <option value="1m">最近1月</option>
                      <option value="3m">最近3月</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            <div className="search-results">
              {loading ? (
                <div className="loading">
                  <div className="spinner" />
                  正在搜索...
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
                          <button className="action-btn" title="收藏">
                            <Bookmark size={16} />
                          </button>
                          <button className="action-btn" title="分享">
                            <Share size={16} />
                          </button>
                          <button className="action-btn" title="更多">
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
                              查看原文
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
                  <h3>未找到相关结果</h3>
                  <p>请尝试使用不同的关键词或调整筛选条件</p>
                </div>
              ) : (
                <div className="search-placeholder">
                  <Search size={48} />
                  <h3>开始您的搜索</h3>
                  <p>输入关键词来搜索知识库中的相关文档</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 输入框 */}
        <div className="input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={searchMode === 'chat' ? '输入您的问题...' : '输入搜索关键词...'}
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