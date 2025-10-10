import React, { useState, useEffect } from 'react'
import { documentAPI, rssAPI } from '../api'
import { Document } from '../types/document'
import { RssSource } from '../types/rss'

import axios from 'axios'
import {
  Search,
  Filter,
  Trash2,
  FileText,
  Calendar,
  Tag,
  ExternalLink,
  CheckSquare,
  Square,
  RefreshCw,
  ChevronLeft,
  ChevronRight
} from 'lucide-react'

const DocsPage: React.FC = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [rssSources, setRssSources] = useState<RssSource[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDocs, setSelectedDocs] = useState<Set<number>>(new Set())
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

  useEffect(() => {
    fetchDocuments()
    fetchRssSources()
  }, [filters, pagination.page, pagination.size])

  const fetchRssSources = async () => {
    try {
      const response = await rssAPI.getRssSources({ type: 'rss' })
      const data = response.data || response
      setRssSources(data.sources || [])
    } catch (error) {
      console.error('Failed to fetch RSS sources:', error)
      setRssSources([])
    }
  }

  const fetchDocuments = async () => {
    setLoading(true)
    try {
      // Build query parameters
      const params = {
        page: pagination.page,
        size: pagination.size
      }

      if (filters.search) (params as any).search = filters.search
      if (filters.type) (params as any).type = filters.type
      if (filters.source) (params as any).source = filters.source
      if (filters.startDate) (params as any).start = filters.startDate
      if (filters.endDate) (params as any).end = filters.endDate

      // Call document list API
      const response = await documentAPI.getDocumentsPage(params)
      const { items, total } = response.data

      setDocuments(items || [])
      setPagination(prev => ({ ...prev, total: total || 0 }))
    } catch (error) {
      console.error('Failed to fetch documents:', error)
      setDocuments([])
      setPagination(prev => ({ ...prev, total: 0 }))
    } finally {
      setLoading(false)
    }
  }

  const handleSelectDoc = (docId: number) => {
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

    if (confirm(`Are you sure you want to delete ${selectedDocs.size} selected documents?`)) {
      try {
        // Call batch delete API
        await axios.delete('/docs/batch', {
          data: { ids: Array.from(selectedDocs) }
        })

        setDocuments(prev => prev.filter(doc => !selectedDocs.has(doc.id)))
        setSelectedDocs(new Set())
        alert('Delete successful')
      } catch (error) {
        console.error('Delete failed:', error)
        alert('Delete failed, please try again later')
      }
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US')
  }

  // Calculate total pages
  const totalPages = Math.ceil(pagination.total / pagination.size)

  // Handle page change
  const handlePageChange = (page: number) => {
    if (page < 1 || page > totalPages) return
    setPagination(prev => ({ ...prev, page }))
  }

  // Handle page size change
  const handleSizeChange = (size: number) => {
    setPagination(prev => ({
      ...prev,
      size,
      page: 1 // Reset to first page
    }))
  }

  return (
    <div className="docs-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Knowledge Base Management</h1>
          <p className="page-subtitle">Manage and organize your document knowledge base</p>
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
              placeholder="Search document titles..."
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
                {selectedDocs.size} documents selected
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

      {/* Filter panel */}
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
                <option value="web">Web Page</option>
                <option value="pdf">PDF</option>
                <option value="article">Article</option>
                <option value="news">News</option>
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

      {/* Document list */}
      <div className="card">
        {loading ? (
          <div className="loading">
            <div className="spinner" />
            Loading documents...
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
                    <th style={{ width: '40px' }}></th>
                    <th>Title</th>
                    <th style={{ width: '120px' }}>Source</th>
                    <th style={{ width: '200px' }}>Tags</th>
                    <th style={{ width: '160px' }}>Crawled At</th>
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
                          <div>
                            <div className="title">{doc.title}</div>
                            {doc.link && (
                              <a
                                href={doc.link}
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
                        <span className="source">{rssSources.find(source => source.id === doc.rss_source_id)?.name || 'Unknown'}</span>
                      </td>
                      <td>
                        <div className="tags">
                          {(doc.tags || []).map((tag, index) => (
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
                          {formatDate(doc.crawled_at)}
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
                  <p>No documents have been uploaded yet. Go to the upload page to add some content</p>
                  <a href="/upload" className="btn btn-primary">
                    Upload Documents
                  </a>
                </div>
              )}
            </div>

            {/* Pagination component */}
            {documents.length > 0 && (
              <div className="pagination-container">
                <div className="pagination-info">
                  Showing {(pagination.page - 1) * pagination.size + 1} - {Math.min(pagination.page * pagination.size, pagination.total)} of {pagination.total} items
                </div>
                <div className="pagination-controls">
                  <div className="page-size-selector">
                    <span>Items per page</span>
                    <select
                      value={pagination.size}
                      onChange={(e) => handleSizeChange(Number(e.target.value))}
                      className="page-size-select"
                    >
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                    <span>items</span>
                  </div>
                  <div className="page-numbers">
                    <button
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={pagination.page <= 1}
                      className="page-btn"
                    >
                      <ChevronLeft size={16} />
                    </button>

                    {/* Display page number buttons */}
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum
                      if (totalPages <= 5) {
                        pageNum = i + 1
                      } else if (pagination.page <= 3) {
                        pageNum = i + 1
                      } else if (pagination.page >= totalPages - 2) {
                        pageNum = totalPages - 4 + i
                      } else {
                        pageNum = pagination.page - 2 + i
                      }

                      return (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`page-btn ${pagination.page === pageNum ? 'active' : ''}`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}

                    <button
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={pagination.page >= totalPages}
                      className="page-btn"
                    >
                      <ChevronRight size={16} />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <style>{`
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

        /* Pagination component styles */
        .pagination-container {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 20px;
          border-top: 1px solid var(--border);
        }

        .pagination-info {
          color: var(--muted);
          font-size: 14px;
        }

        .pagination-controls {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .page-size-selector {
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--muted);
          font-size: 14px;
        }

        .page-size-select {
          background: var(--elev);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 4px 8px;
          color: var(--text);
          font-size: 14px;
        }

        .page-numbers {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .page-btn {
          display: flex;
          align-items: center;
          justify-content: center;
          min-width: 32px;
          height: 32px;
          background: var(--elev);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          color: var(--muted);
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .page-btn:hover:not(:disabled) {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .page-btn.active {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .page-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        @media (max-width: 768px) {
          .pagination-container {
            flex-direction: column;
            gap: 12px;
            align-items: flex-start;
          }
          
          .pagination-controls {
            width: 100%;
            justify-content: space-between;
          }
        }
      `}</style>
    </div>
  )
}

export default DocsPage