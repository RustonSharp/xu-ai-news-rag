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

// 类型定义
interface Message {
  id: string
  type: 'user' | 'bot'
  content: string
  timestamp: string
  sources?: SearchResult[]
  rawAnswer?: any // 添加rawAnswer字段到Message接口
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

// 后端返回的响应数据结构
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
      // 聊天模式
      // 添加用户消息
      const userMessage: Message = {
        id: Date.now().toString(),
        type: 'user' as const,
        content: query,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])

      // 调用助手API
      const response = await assistantAPI.query({
        query: query,
        options: {
          use_knowledge_base: true,
          use_online_search: false
        }
      })
      console.log('助手查询响应:', response)

      // 使用AssistantResponse类型处理后端返回的数据结构
      // 检查响应是否包含必要字段
      if (!response) {
        throw new Error('后端返回数据为空')
      }

      // 根据实际响应结构，数据可能直接在response中，也可能在response.data中
      const responseData: AssistantResponse = (response.data || response) as AssistantResponse
      const rawAnswer = responseData.answer || `基于您的问题"${query}"，我为您找到了相关信息。`
      let rawSources = (responseData as any).raw_answer || [] // 获取原始来源信息
      if (rawSources.length == 0 || rawSources[0]['title'] == "" || rawSources[0]['content'] == "Placeholder text") {
        rawSources = []
      }
      console.log('原始答案数据:', rawAnswer)
      console.log('原始来源数据:', rawSources)
      console.log('答案类型:', typeof rawAnswer)
      // 使用formatAnswer函数格式化答案
      const answer = formatAnswer(rawAnswer)
      console.log('格式化后的答案:', answer)
      // 从响应中提取sources
      const sources = responseData.sources || []
      const origin = responseData.origin || (sources.length > 0 ? 'knowledge_base' : 'online_search')

      // 生成AI回复
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot' as const,
        content: answer,
        timestamp: new Date().toISOString(),
        sources: sources,
        rawAnswer: rawSources, // 保存原始来源信息
        origin: origin
      }

      setMessages(prev => [...prev, aiResponse])
    } catch (error) {
      console.error('助手查询失败:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'bot' as const,
        content: '抱歉，助手查询过程中出现了错误，请稍后重试。',
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
    alert('已复制到剪贴板')
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN')
  }

  // 已移除知识搜索展示，保留占位避免误用

  const clearChat = () => {
    setMessages([])
  }

  // 格式化后端返回的答案 - 仅展示answer.output部分
  const formatAnswer = (answer: any): string => {
    console.log('formatAnswer 输入:', answer)
    console.log('formatAnswer 输入类型:', typeof answer)

    // 如果答案是字符串，尝试解析其中的JSON结构
    if (typeof answer === 'string') {
      console.log('答案是字符串，尝试解析JSON')
      try {
        // 尝试解析字符串为对象
        const parsedAnswer = JSON.parse(answer)
        console.log('解析成功:', parsedAnswer)

        // 如果解析成功且包含output字段，返回output值
        if (parsedAnswer && typeof parsedAnswer === 'object' && parsedAnswer.hasOwnProperty('output')) {
          console.log('找到output字段，值:', parsedAnswer.output)
          return String(parsedAnswer.output);
        }
      } catch (e) {
        console.log('JSON解析失败，尝试其他方法')
        // 如果JSON解析失败，尝试使用正则表达式提取output字段
        const outputMatch = answer.match(/'output':\s*'([^']*)'/);
        if (outputMatch && outputMatch[1]) {
          console.log('正则匹配到output字段，值:', outputMatch[1])
          return outputMatch[1];
        }
      }

      // 如果无法解析或没有output字段，直接返回原字符串
      console.log('无法提取output字段，返回原字符串')
      return answer;
    }

    // 如果答案是对象，仅提取output字段
    if (typeof answer === 'object' && answer !== null) {
      console.log('答案是对象，检查output字段')
      console.log('对象键:', Object.keys(answer))
      console.log('是否有output字段:', answer.hasOwnProperty('output'))

      // 如果有output字段，使用output字段的值
      if (answer.hasOwnProperty('output')) {
        console.log('找到output字段，值:', answer.output)
        return String(answer.output);
      }

      // 如果没有output字段，返回空字符串或提示信息
      console.log('没有output字段，返回提示信息')
      return '暂无可用内容';
    }

    // 其他情况，转换为字符串
    console.log('其他情况，转换为字符串')
    return String(answer);
  }

  return (
    <div className="search-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">AI助手</h1>
          <p className="page-subtitle">基于知识库的智能问答助手</p>
        </div>
      </div>

      <div className="search-container">
        {/* 聊天模式 */}
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
                <p>我可以帮您解答问题、分析信息，请输入您的问题。</p>

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
                            {message.origin === 'online_search' ? '来源：联网搜索' : '来源：知识库'}
                          </span>
                        </div>
                      )}
                      <div className="message-text">
                        {message.type === 'bot' ? (
                          // 机器人回答使用特殊格式
                          <div className="bot-answer">
                            {message.content.split('\n').map((paragraph, index) => (
                              <p key={index}>{paragraph}</p>
                            ))}
                          </div>
                        ) : (
                          // 用户消息保持原格式
                          message.content.split('\n').map((paragraph, index) => (
                            <p key={index}>{paragraph}</p>
                          ))
                        )}
                      </div>

                      {/* 显示原始答案信息，仅在有rawAnswer且为bot消息时显示 */}
                      {message.type === 'bot' && message.rawAnswer && (
                        <details className="raw-answer-details">
                          <summary>查看原始答案</summary>
                          <div className="raw-answer-content">
                            {(() => {
                              // 如果rawAnswer是数组（原始来源信息）
                              if (Array.isArray(message.rawAnswer)) {
                                return (
                                  <div className="raw-sources-list">
                                    {message.rawAnswer.map((source, index) => (
                                      <div key={index} className="raw-source-item">
                                        <h5>来源 {index + 1}:</h5>
                                        <div className="raw-source-content">
                                          <p><strong>内容:</strong> {source.content || '无内容'}</p>
                                          {source.metadata && (
                                            <div className="raw-source-meta">
                                              <p><strong>标题:</strong> {source.metadata.title || '无标题'}</p>
                                              <p><strong>作者:</strong> {source.metadata.author || '未知'}</p>
                                              <p><strong>发布日期:</strong> {source.metadata.pub_date || '未知'}</p>
                                              <p><strong>标签:</strong> {source.metadata.tags || '无标签'}</p>
                                            </div>
                                          )}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                );
                              }

                              // 如果是字符串，尝试解析并提取output
                              if (typeof message.rawAnswer === 'string') {
                                try {
                                  const parsed = JSON.parse(message.rawAnswer);
                                  if (parsed && parsed.hasOwnProperty('output')) {
                                    return <div className="raw-answer-text">{String(parsed.output)}</div>;
                                  }
                                } catch (e) {
                                  // 如果JSON解析失败，尝试正则表达式
                                  const outputMatch = message.rawAnswer.match(/'output':\s*'([^']*)'/);
                                  if (outputMatch && outputMatch[1]) {
                                    return <div className="raw-answer-text">{outputMatch[1]}</div>;
                                  }
                                }
                              }
                              // 如果是对象且有output字段
                              if (typeof message.rawAnswer === 'object' && message.rawAnswer !== null && message.rawAnswer.hasOwnProperty('output')) {
                                return <div className="raw-answer-text">{String(message.rawAnswer.output)}</div>;
                              }
                              // 其他情况显示原始内容
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

        {/* 输入框 */}
        <div className="input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={'输入您的问题...'}
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
          min-height: 0; /* 确保flex容器正确收缩 */
          /* 确保滚动条始终可见 */
          scrollbar-width: thin;
          scrollbar-color: #ccc #f1f1f1;
          max-height: calc(100vh - 280px); /* 设置最大高度 */
          border: 1px solid #eee; /* 添加边框使容器边界更明显 */
        }
        
        /* Webkit浏览器的滚动条样式 */
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

        /* 机器人回答的特殊样式 */
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