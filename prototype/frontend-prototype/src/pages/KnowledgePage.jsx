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

  // Simulated data
  const mockDocuments = [
    {
      id: 1,
      title: 'AI Technology Development Trend Report',
      type: 'pdf',
      source: 'tech_news',
      url: 'https://example.com/ai-report.pdf',
      tags: ['AI', 'Technology', 'Report'],
      created_at: '2024-01-15T10:30:00Z',
      updated_at: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      title: 'Applications of Machine Learning in Finance',
      type: 'html',
      source: 'finance_blog',
      url: 'https://example.com/ml-finance',
      tags: ['Machine Learning', 'Finance', 'Application'],
      created_at: '2024-01-14T15:20:00Z',
      updated_at: '2024-01-14T15:20:00Z'
    },
    {
      id: 3,
      title: 'Deep Learning Frameworks Comparative Analysis',
      type: 'markdown',
      source: 'research_paper',
      url: null,
      tags: ['Deep Learning', 'Framework', 'Comparison'],
      created_at: '2024-01-13T09:15:00Z',
      updated_at: '2024-01-13T09:15:00Z'
    },
    {
      id: 4,
      title: 'Latest Advances in Natural Language Processing',
      type: 'txt',
      source: 'academic_journal',
      url: null,
      tags: ['NLP', 'Progress'],
      created_at: '2024-01-12T11:45:00Z',
      updated_at: '2024-01-12T11:45:00Z'
    }
  ]

  useEffect(() => {
    fetchDocuments()
  }, [filters, pagination.page])

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))

      // Apply filters
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
      console.error('Failed to fetch documents:', error)
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

    if (confirm(`Are you sure you want to delete the selected ${selectedDocs.size} documents?`)) {
      try {
        // Simulate batch delete API call
        await new Promise(resolve => setTimeout(resolve, 1000))

        setDocuments(prev => prev.filter(doc => !selectedDocs.has(doc.id)))
        setSelectedDocs(new Set())
        alert('Deletion successful')
      } catch (error) {
        console.error('Deletion failed:', error)
        alert('Deletion failed, please try again later')
      }
    }
  }

  const handleDeleteDoc = async (docId) => {
    if (confirm('Are you sure you want to delete this document?')) {
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        setDocuments(prev => prev.filter(doc => doc.id !== docId))
        alert('Deletion successful')
      } catch (error) {
        console.error('Deletion failed:', error)
        alert('Deletion failed, please try again later')
      }
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US')
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
          <h1 className="page-title">Knowledge Library Management</h1>
          <p className="page-subtitle">Manage and organize your document knowledge library</p>
        </div>
        <button
          onClick={fetchDocuments}
          className="btn btn-secondary"
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? 'spinning' : ''} />
          Refresh
        </button>
      </div>

      {/* Toolbar */}
      <div className="toolbar">
        <div className="toolbar-left">
          <div className="search-box">
            <Search size={16} />
            <input
              type="text"
              placeholder="Search document title..."
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
            Filter
          </button>
        </div>

        <div className="toolbar-right">
          {selectedDocs.size > 0 && (
            <>
              <span className="selected-count">
                Selected {selectedDocs.size} documents
              </span>
              <button
                onClick={handleBatchDelete}
                className="btn btn-danger btn-sm"
              >
                <Trash2 size={14} />
                Batch Delete
              </button>
            </>
          )}
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="filters-panel">
          <div className="filters-grid">
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
                <option value="txt">Text</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Source</label>
              <select
                value={filters.source}
                onChange={(e) => setFilters(prev => ({ ...prev, source: e.target.value }))}
                className="input"
              >
                <option value="">All Sources</option>
                <option value="tech_news">Tech News</option>
                <option value="finance_blog">Finance Blog</option>
                <option value="research_paper">Research Paper</option>
                <option value="academic_journal">Academic Journal</option>
                <option value="medical_news">Medical News</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Start Date</label>
              <input
                type="date"
                value={filters.startDate}
                onChange={(e) => setFilters(prev => ({ ...prev, startDate: e.target.value }))}
                className="input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">End Date</label>
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

      {/* Document List */}
      <div className="card">
        {loading ? (
          <div className="loading">
            <div className="spinner" />
            Loading document...
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
                <span className="table-title">Document List ({documents.length})</span>
              </div>
            </div>

            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th width="40"></th>
                    <th>Title</th>
                    <th width="80">Type</th>
                    <th width="120">Source</th>
                    <th width="200">Tags</th>
                    <th width="160">Creation Time</th>
                    <th width="100">Actions</th>
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
                                View Original
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
                            title="Edit"
                          >
                            <Edit3 size={14} />
                          </button>
                          <button
                            onClick={() => handleDeleteDoc(doc.id)}
                            className="btn-icon danger"
                            title="Delete"
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
                  <h3>No Documents</h3>
                  <p>No documents uploaded yet, go to upload page to add some content</p>
                  <a href="/upload" className="btn btn-primary">
                    Upload Document
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