import React, { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Search,
  Filter,
  Trash2,
  Edit3,
  FileText,
  Calendar,
  Tag,
  ExternalLink,
  CheckSquare,
  Square,
  MoreHorizontal,
  RefreshCw
} from 'lucide-react'

const DocsPage = () => {
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedDocs, setSelectedDocs] = useState(new Set())
  const [filters, setFilters] = useState({
    search: '',
    type: '',
    source: '',
    startDate: '',
    endDate: ''
  })
  const [pagination, setPagination] = useState({
    page: 1,
    size: 20,
    total: 0
  })
  const [showFilters, setShowFilters] = useState(false)

  // 模拟数据
  const mockDocuments = [
    {
      id: 1,
      title: 'AI技术发展趋势报告',
      type: 'pdf',
      source: 'tech_news',
      url: 'https://example.com/ai-report.pdf',
      tags: ['AI', '技术', '报告'],
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      title: '机器学习在金融领域的应用',
      type: 'html',
      source: 'finance_blog',
      url: 'https://example.com/ml-finance',
      tags: ['机器学习', '金融', '应用'],
      created_at: '2024-01-14T15:20:00Z',
      updated_at: '2024-01-14T15:20:00Z'
    },
    {
      id: 3,
      title: '深度学习框架对比分析',
      type: 'markdown',
      source: 'research_paper',
      url: null,
      tags: ['深度学习', '框架', '对比'],
      created_at: '2024-01-13T09:15:00Z',
      updated_at: '2024-01-13T09:15:00Z'
    },
    {
      id: 4,
      title: '自然语言处理最新进展',
      type: 'txt',
      source: 'academic_journal',
      url: 'https://example.com/nlp-progress',
      tags: ['NLP', '自然语言处理', '进展'],
      created_at: '2024-01-12T14:45:00Z',
      updated_at: '2024-01-12T14:45:00Z'
    },
    {
      id: 5,
      title: '计算机视觉在医疗诊断中的应用',
      type: 'pdf',
      source: 'medical_news',
      url: 'https://example.com/cv-medical.pdf',
      tags: ['计算机视觉', '医疗', '诊断'],
      created_at: '2024-01-11T11:30:00Z',
      updated_at: '2024-01-11T11:30:00Z'
    }
  ]

  useEffect(() => {
    fetchDocuments()
  }, [filters, pagination.page])

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // 应用筛选
      let filteredDocs = mockDocuments.filter(doc => {
        if (filters.search && !doc.title.toLowerCase().includes(filters.search.toLowerCase())) {
          return false
        }
        if (filters.type && doc.type !== filters.type) {
          return false
        }
        if (filters.source && doc.source !== filters.source) {
          return false
        }
        return true
      })

      setDocuments(filteredDocs)
      setPagination(prev => ({ ...prev, total: filteredDocs.length }))
    } catch (error) {
      console.error('获取文档失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectDoc = (docId) => {
    const newSelected = new Set(selectedDocs)
    if (newSelected.has(docId)) {
      newSelected.delete(docId)
    } else {
      newSelected.add(docId)
    }
    setSelectedDocs(newSelected)
  }

  const handleSelectAll = () => {
    if (selectedDocs.size === documents.length) {
      setSelectedDocs(new Set())
    } else {
      setSelectedDocs(new Set(documents.map(doc => doc.id)))
    }
  }

  const handleBatchDelete = async () => {
    if (selectedDocs.size === 0) return
    
    if (confirm(`确定要删除选中的 ${selectedDocs.size} 个文档吗？`)) {
      try {
        // 模拟批量删除API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        setDocuments(prev => prev.filter(doc => !selectedDocs.has(doc.id)))
        setSelectedDocs(new Set())
        alert('删除成功')
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败，请稍后重试')
      }
    }
  }

  const handleDeleteDoc = async (docId) => {
    if (confirm('确定要删除这个文档吗？')) {
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        setDocuments(prev => prev.filter(doc => doc.id !== docId))
        alert('删除成功')
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败，请稍后重试')
      }
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('zh-CN')
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'pdf': return '📄'
      case 'html': return '🌐'
      case 'markdown': return '📝'
      case 'txt': return '📃'
      default: return '📄'
    }
  }

  return (
    <div className="docs-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">知识库管理</h1>
          <p className="page-subtitle">管理和组织您的文档知识库</p>
        </div>
        <button
          onClick={fetchDocuments}
          className="btn btn-secondary"
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? 'spinning' : ''} />
          刷新
        </button>
      </div>

      {/* 工具栏 */}
      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="搜索文档标题..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="input"
            />
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`btn btn-secondary ${showFilters ? 'active' : ''}`}
          >
            <Filter size={16} />
            筛选
          </button>
        </div>

        <div className="toolbar-right">
          {selectedDocs.size > 0 && (
            <>
              <span className="selected-count">
                已选择 {selectedDocs.size} 个文档
              </span>
              <button
                onClick={handleBatchDelete}
                className="btn btn-danger btn-sm"
              >
                <Trash2 size={14} />
                批量删除
              </button>
            </>
          )}
        </div>
      </div>

      {/* 筛选面板 */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filters-grid">
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
                <option value="txt">文本</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">来源</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                className="input"
              >
                <option value="">全部来源</option>
                <option value="tech_news">科技新闻</option>
                <option value="finance_blog">金融博客</option>
                <option value="research_paper">研究论文</option>
                <option value="academic_journal">学术期刊</option>
                <option value="medical_news">医疗新闻</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">开始日期</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
                className="input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">结束日期</label>
              <input
                type="date"
                value={filters.endDate}
                onChange={(e) => setFilters(prev => ({ ...prev, endDate: e.target.value }))}
                className="input"
              />
            </div>
          </div>
        </div>
      )}

      {/* 文档列表 */}
      <div className="card">
        {loading ? (
          <div className="loading">
            <div className="spinner" />
            正在加载文档...
          </div>
        ) : (
          <>
            <div className="table-header">
              <div className="table-actions">
                <button
                  onClick={handleSelectAll}
                  className="select-all-btn"
                >
                  {selectedDocs.size === documents.length && documents.length > 0 ? (
                    <CheckSquare size={16} />
                  ) : (
                    <Square size={16} />
                  )}
                </button>
                <span className="table-title">文档列表 ({documents.length})</span>
              </div>
            </div>

            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th width="40"></th>
                    <th>标题</th>
                    <th width="80">类型</th>
                    <th width="120">来源</th>
                    <th width="200">标签</th>
                    <th width="160">创建时间</th>
                    <th width="100">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {documents.map((doc) => (
                    <tr key={doc.id} className={selectedDocs.has(doc.id) ? 'selected' : ''}>
                      <td>
                        <button
                          onClick={() => handleSelectDoc(doc.id)}
                          className="select-btn"
                        >
                          {selectedDocs.has(doc.id) ? (
                            <CheckSquare size={16} />
                          ) : (
                            <Square size={16} />
                          )}
                        </button>
                      </td>
                      <td>
                        <div className="doc-title">
                          <span className="doc-icon">{getTypeIcon(doc.type)}</span>
                          <div>
                            <div className="title">{doc.title}</div>
                            {doc.url && (
                              <a
                                href={doc.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="doc-url"
                              >
                                <ExternalLink size={12} />
                                查看原文
                              </a>
                            )}
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-secondary">{doc.type}</span>
                      </td>
                      <td>
                        <span className="source">{doc.source}</span>
                      </td>
                      <td>
                        <div className="tags">
                          {doc.tags.map((tag, index) => (
                            <span key={index} className="tag">
                              <Tag size={10} />
                              {tag}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <div className="date">
                          <Calendar size={12} />
                          {formatDate(doc.created_at)}
                        </div>
                      </td>
                      <td>
                        <div className="actions">
                          <button
                            className="btn-icon"
                            title="编辑"
                          >
                            <Edit3 size={14} />
                          </button>
                          <button
                            onClick={() => handleDeleteDoc(doc.id)}
                            className="btn-icon danger"
                            title="删除"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {documents.length === 0 && (
                <div className="empty-state">
                  <FileText size={48} />
                  <h3>暂无文档</h3>
                  <p>还没有上传任何文档，去上传页面添加一些内容吧</p>
                  <a href="/upload" className="btn btn-primary">
                    上传文档
                  </a>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <style jsx>{`
        .docs-page {
          max-width: 1200px;
          margin: 0 auto;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 32px;
        }

        .search-box {
          position: relative;
          display: flex;
          align-items: center;
          gap: 8px;
          background: var(--elev);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 0 12px;
          min-width: 300px;
        }

        .search-box input {
          border: none;
          background: transparent;
          padding: 8px 0;
        }

        .filters-panel {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 20px;
          margin-bottom: 20px;
        }

        .filters-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .table-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-bottom: 1px solid var(--border);
        }

        .table-actions {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .select-all-btn {
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
        }

        .select-all-btn:hover {
          background: var(--elev);
          color: var(--text);
        }

        .table-title {
          font-weight: 600;
          color: var(--text);
        }

        .table-container {
          overflow-x: auto;
        }

        .table {
          width: 100%;
          border-collapse: collapse;
        }

        .table th {
          background: var(--elev);
          padding: 12px 16px;
          text-align: left;
          font-weight: 600;
          color: var(--text);
          border-bottom: 1px solid var(--border);
        }

        .table td {
          padding: 16px;
          border-bottom: 1px solid var(--border);
          vertical-align: top;
        }

        .table tr:hover {
          background: var(--elev);
        }

        .table tr.selected {
          background: rgba(91, 157, 255, 0.1);
        }

        .select-btn {
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          padding: 4px;
          border-radius: 4px;
        }

        .select-btn:hover {
          background: var(--elev);
          color: var(--text);
        }

        .doc-title {
          display: flex;
          align-items: flex-start;
          gap: 12px;
        }

        .doc-icon {
          font-size: 20px;
          flex-shrink: 0;
        }

        .title {
          font-weight: 500;
          color: var(--text);
          margin-bottom: 4px;
        }

        .doc-url {
          display: flex;
          align-items: center;
          gap: 4px;
          color: var(--primary);
          font-size: 12px;
          text-decoration: none;
        }

        .doc-url:hover {
          text-decoration: underline;
        }

        .badge-secondary {
          background: var(--elev);
          color: var(--text);
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .source {
          color: var(--muted);
          font-size: 14px;
        }

        .tags {
          display: flex;
          flex-wrap: wrap;
          gap: 6px;
        }

        .tag {
          display: flex;
          align-items: center;
          gap: 4px;
          background: rgba(91, 157, 255, 0.1);
          color: var(--primary);
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 500;
        }

        .date {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--muted);
          font-size: 12px;
        }

        .actions {
          display: flex;
          gap: 8px;
        }

        .btn-icon {
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          padding: 6px;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .btn-icon:hover {
          background: var(--elev);
          color: var(--text);
        }

        .btn-icon.danger:hover {
          background: rgba(239, 85, 82, 0.1);
          color: var(--danger);
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: var(--muted);
        }

        .empty-state h3 {
          margin: 16px 0 8px;
          color: var(--text);
        }

        .empty-state p {
          margin-bottom: 24px;
        }

        .selected-count {
          color: var(--primary);
          font-size: 14px;
          font-weight: 500;
        }

        .spinning {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .toolbar {
            flex-direction: column;
            gap: 16px;
          }

          .toolbar-right {
            margin-left: 0;
          }

          .search-box {
            min-width: auto;
            width: 100%;
          }

          .filters-grid {
            grid-template-columns: 1fr;
          }

          .table-container {
            overflow-x: scroll;
          }
        }
      `}</style>
    </div>
  )
}

export default DocsPage