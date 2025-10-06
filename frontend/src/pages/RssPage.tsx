import React, { useState, useEffect } from 'react'
import { rssAPI } from '../api'
import {
  Plus,
  Rss,
  Globe,
  Edit3,
  Trash2,
  Play,
  Pause,
  CheckCircle,
  AlertCircle,
  Clock,
  RefreshCw,
  ExternalLink,
  X
} from 'lucide-react'

// Type definitions
interface DataSource {
  id: string
  name: string
  url: string
  status: string
  lastSync: string
  description: string
  schedule: string
  enabled: boolean
  lastRun?: string | null
  nextRun?: string | null
  document_count?: number
  tags: string[]
  filters: {
    keywords: string
    excludeKeywords: string
    minLength: number
  }
}

// API response data type
interface ApiSourceItem {
  id: string
  name: string
  entry: string
  description?: string
  schedule?: string
  enabled?: boolean
  last_run?: string | null
  next_run?: string | null
  articles_count?: number
  tags?: string[]
  filters?: {
    keywords: string
    excludeKeywords: string
    minLength: number
  }
  template?: {
    type?: string
  }
}

const RssPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('rss')
  const [rssSources, setRssSources] = useState<DataSource[]>([])
  const [webSources, setWebSources] = useState<DataSource[]>([])
  const [showAddModal, setShowAddModal] = useState(false)
  const [editingSource, setEditingSource] = useState<DataSource | null>(null)
  const [loading, setLoading] = useState(true)
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    description: '',
    schedule: '24h', // Default value corresponds to backend interval field 'ONE_DAY'
    enabled: true,
    tags: [] as string[],
    filters: {
      keywords: '',
      excludeKeywords: '',
      minLength: 100
    }
  })

  useEffect(() => {
    fetchSources()
  }, [])

  const fetchSources = async () => {
    setLoading(true)
    try {
      // Get RSS data sources
      const response = await rssAPI.getRssSources()
      const sources = response.data || []

      // Convert API data to frontend format, ensuring all necessary properties exist
      const transformedSources = sources.map((source: any) => ({
        id: source.id,
        name: source.name,
        url: source.url,
        description: '', // Backend currently doesn't provide description field
        schedule: source.interval === 'SIX_HOUR' ? '6h' :
          source.interval === 'TWELVE_HOUR' ? '12h' :
            source.interval === 'ONE_DAY' ? '24h' : '24h',
        enabled: true, // Backend currently doesn't provide enabled field, default to true
        status: 'active', // Backend currently doesn't provide status field, default to active
        lastRun: source.last_sync, // Map backend last_sync field
        nextRun: source.next_sync, // Map backend next_sync field
        document_count: source.document_count || 0, // Map backend document_count field
        tags: [], // Backend currently doesn't provide tags field
        filters: { // Backend currently doesn't provide filters field, use default values
          keywords: '',
          excludeKeywords: '',
          minLength: 100
        },
        lastSync: new Date().toISOString(),
        type: 'rss' // Backend currently only has RSS sources, no web sources
      }))

      // Since backend currently only has RSS sources, no web sources, all sources are categorized as RSS
      setRssSources(transformedSources)
      setWebSources([]) // Clear web source list
    } catch (error) {
      console.error('Failed to fetch data sources:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddSource = () => {
    setEditingSource(null)
    setFormData({
      name: '',
      url: '',
      description: '',
      schedule: '24h', // Default value corresponds to backend interval field 'ONE_DAY'
      enabled: true,
      tags: [],
      filters: {
        keywords: '',
        excludeKeywords: '',
        minLength: 100
      }
    })
    setShowAddModal(true)
  }

  const handleEditSource = (source: DataSource) => {
    setEditingSource(source)
    setFormData({
      name: source.name,
      url: source.url,
      description: source.description,
      schedule: source.schedule,
      enabled: source.enabled,
      tags: source.tags || [],
      filters: source.filters || {
        keywords: '',
        excludeKeywords: '',
        minLength: 100
      }
    })
    setShowAddModal(true)
  }

  const handleSaveSource = async () => {
    try {
      // Build data format that matches backend expectations
      const sourceData = {
        name: formData.name,
        url: formData.url,
        interval: formData.schedule === '6h' ? 'SIX_HOUR' :
          formData.schedule === '12h' ? 'TWELVE_HOUR' :
            formData.schedule === '24h' ? 'ONE_DAY' : 'ONE_DAY' // Default to ONE_DAY
      }

      // Call save API
      const response = editingSource
        ? await rssAPI.updateRssSource(editingSource.id, sourceData)
        : await rssAPI.createRssSource(sourceData)
      const savedSource = response.data

      // Convert to frontend display format
      const newSource: DataSource = {
        id: savedSource.id,
        name: savedSource.name,
        url: savedSource.url,
        description: formData.description,
        schedule: savedSource.interval === 'SIX_HOUR' ? '6h' :
          savedSource.interval === 'TWELVE_HOUR' ? '12h' :
            savedSource.interval === 'ONE_DAY' ? '24h' : '24h',
        enabled: true, // Backend currently doesn't provide enabled field, default to true
        status: 'active', // Backend currently doesn't provide status field, default to active
        lastRun: null,
        nextRun: null,
        document_count: 0,
        tags: formData.tags,
        filters: formData.filters,
        lastSync: new Date().toISOString()
      }

      if (activeTab === 'rss') {
        if (editingSource) {
          setRssSources(prev => prev.map(s => s.id === editingSource.id ? newSource : s))
        } else {
          setRssSources(prev => [...prev, newSource])
        }
      } else {
        if (editingSource) {
          setWebSources(prev => prev.map(s => s.id === editingSource.id ? newSource : s))
        } else {
          setWebSources(prev => [...prev, newSource])
        }
      }

      setShowAddModal(false)
      alert('Save successful')
    } catch (error) {
      console.error('Save failed:', error)
      alert('Save failed, please try again later')
    }
  }

  const handleDeleteSource = async (sourceId: string | number) => {
    if (window.confirm('Are you sure you want to delete this data source?')) {
      try {
        // Call delete API
        await rssAPI.deleteRssSource(sourceId)

        if (activeTab === 'rss') {
          setRssSources(prev => prev.filter(s => s.id !== sourceId))
        } else {
          setWebSources(prev => prev.filter(s => s.id !== sourceId))
        }

        alert('Delete successful')
      } catch (error) {
        console.error('Delete failed:', error)
        alert('Delete failed, please try again later')
      }
    }
  }

  const handleToggleSource = async (sourceId: string | number, enabled: boolean) => {
    try {
      // Get current data source information
      const currentSource = [...rssSources, ...webSources].find(s => s.id === sourceId)
      if (!currentSource) return

      // Update data source configuration - use backend expected format
      const updatedSource = {
        name: currentSource.name,
        url: currentSource.url,
        interval: 'ONE_DAY' // Default to ONE_DAY
      }

      await rssAPI.updateRssSource(sourceId, updatedSource)

      const updateSource = (source: DataSource) => ({
        ...source,
        enabled,
        status: enabled ? 'active' : 'paused',
        nextRun: enabled ? new Date(Date.now() + 3600000).toISOString() : null
      })

      if (activeTab === 'rss') {
        setRssSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
      } else {
        setWebSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
      }
    } catch (error) {
      console.error('Update failed:', error)
      alert('Update failed, please try again later')
    }
  }

  const handleRunNow = async (sourceId: string | number) => {
    try {
      // Call RSS collection API
      const response = await rssAPI.triggerRssCollection(sourceId)

      // Check if response is successful
      if (response && response.message) {
        alert('Collection task started')

        const updateSource = (source: DataSource) => ({
          ...source,
          lastRun: new Date().toISOString(),
          nextRun: new Date(Date.now() + 3600000).toISOString(), // Default to run again after 1 hour
          articlesCount: (source.document_count || 0) + Math.floor(Math.random() * 10) + 1
        })

        if (activeTab === 'rss') {
          setRssSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
        } else {
          setWebSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
        }
      } else {
        throw new Error('Collection response invalid')
      }
    } catch (error) {
      console.error('Collection failed:', error)
      alert('Collection failed, please try again later')
    }
  }

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('en-US')
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle size={16} style={{ color: '#10b981' }} />
      case 'paused':
        return <Pause size={16} style={{ color: '#f59e0b' }} />
      case 'error':
        return <AlertCircle size={16} style={{ color: '#ef4444' }} />
      default:
        return <Clock size={16} style={{ color: '#6b7280' }} />
    }
  }

  const currentSources = activeTab === 'rss' ? rssSources : webSources

  return (
    <div className="collection-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Data Collection Configuration</h1>
          <p className="page-subtitle">Configure RSS subscriptions and web scraping tasks</p>
        </div>
        <button
          onClick={handleAddSource}
          className="btn btn-primary"
        >
          <Plus size={16} />
          Add Data Source
        </button>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          onClick={() => setActiveTab('rss')}
          className={`tab ${activeTab === 'rss' ? 'active' : ''}`}
        >
          <Rss size={16} />
          RSS Subscription ({rssSources.length})
        </button>
        <button
          onClick={() => setActiveTab('web')}
          className={`tab ${activeTab === 'web' ? 'active' : ''}`}
        >
          <Globe size={16} />
          Web Scraping ({webSources.length})
        </button>
      </div>

      {/* Data source list */}
      <div className="card">
        {loading ? (
          <div className="loading">
            <div className="spinner" />
            Loading data sources...
          </div>
        ) : (
          <div className="sources-list">
            {currentSources.map((source) => (
              <div key={source.id} className="source-item">
                <div className="source-header">
                  <div className="source-info">
                    <div className="source-title">
                      <h3>{source.name}</h3>
                      <div className="source-status">
                        {getStatusIcon(source.status)}
                        <span className={`status-text ${source.status}`}>
                          {source.status === 'active' ? 'Running' :
                            source.status === 'paused' ? 'Paused' : 'Error'}
                        </span>
                      </div>
                    </div>
                    <p className="source-description">{source.description}</p>
                    <div className="source-meta">
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-url"
                      >
                        <ExternalLink size={12} />
                        {source.url}
                      </a>
                      <div className="source-tags">
                        {source.tags?.map((tag, index) => (
                          <span key={index} className="tag">{tag}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="source-actions">
                    <button
                      onClick={() => handleToggleSource(source.id, !source.enabled)}
                      className={`btn btn-sm ${source.enabled ? 'btn-secondary' : 'btn-primary'}`}
                    >
                      {source.enabled ? <Pause size={14} /> : <Play size={14} />}
                      {source.enabled ? 'Pause' : 'Enable'}
                    </button>

                    <button
                      onClick={() => handleRunNow(source.id)}
                      className="btn btn-sm btn-secondary"
                      disabled={!source.enabled}
                    >
                      <RefreshCw size={14} />
                      Run Now
                    </button>

                    <button
                      onClick={() => handleEditSource(source)}
                      className="btn-icon"
                    >
                      <Edit3 size={14} />
                    </button>

                    <button
                      onClick={() => handleDeleteSource(source.id)}
                      className="btn-icon danger"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                <div className="source-stats">
                  <div className="stat">
                    <span className="stat-label">Collection Frequency</span>
                    <span className="stat-value">{source.schedule}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Article Count</span>
                    <span className="stat-value">{source.document_count || 0}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Last Run</span>
                    <span className="stat-value">{formatDate(source.lastRun)}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Next Run</span>
                    <span className="stat-value">{formatDate(source.nextRun)}</span>
                  </div>
                </div>
              </div>
            ))}

            {currentSources.length === 0 && (
              <div className="empty-state">
                {activeTab === 'rss' ? <Rss size={48} /> : <Globe size={48} />}
                <h3>No {activeTab === 'rss' ? 'RSS' : 'Web Scraping'} Data Sources</h3>
                <p>Click the button above to add the first data source</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingSource ? 'Edit' : 'Add'} {activeTab === 'rss' ? 'RSS' : 'Web Scraping'} Data Source</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-icon"
              >
                <X size={16} />
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="input"
                  placeholder="Enter data source name"
                />
              </div>

              <div className="form-group">
                <label className="form-label">URL *</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                  className="input"
                  placeholder={activeTab === 'rss' ? 'Enter RSS subscription URL' : 'Enter web page URL'}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="input"
                  rows={3}
                  placeholder="Enter data source description"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">Collection Frequency</label>
                  <select
                    value={formData.schedule}
                    onChange={(e) => setFormData(prev => ({ ...prev, schedule: e.target.value }))}
                    className="input"
                  >
                    <option value="6h">6 Hours</option>
                    <option value="12h">12 Hours</option>
                    <option value="24h">24 Hours</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Status</label>
                  <div className="checkbox-group">
                    <input
                      type="checkbox"
                      id="enabled"
                      checked={formData.enabled}
                      onChange={(e) => setFormData(prev => ({ ...prev, enabled: e.target.checked }))}
                    />
                    <label htmlFor="enabled">Enable Data Source</label>
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Tags</label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
                  }))}
                  className="input"
                  placeholder="Enter tags, separated by commas"
                />
              </div>

              <div className="filters-section">
                <h3>Content Filtering</h3>

                <div className="form-group">
                  <label className="form-label">Include Keywords</label>
                  <input
                    type="text"
                    value={formData.filters.keywords}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      filters: { ...prev.filters, keywords: e.target.value }
                    }))}
                    className="input"
                    placeholder="Separate multiple keywords with commas"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Exclude Keywords</label>
                  <input
                    type="text"
                    value={formData.filters.excludeKeywords}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      filters: { ...prev.filters, excludeKeywords: e.target.value }
                    }))}
                    className="input"
                    placeholder="Separate multiple keywords with commas"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Minimum Content Length</label>
                  <input
                    type="number"
                    value={formData.filters.minLength}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      filters: { ...prev.filters, minLength: parseInt(e.target.value) || 0 }
                    }))}
                    className="input"
                    min="0"
                    placeholder="Characters"
                  />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                onClick={() => setShowAddModal(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveSource}
                className="btn btn-primary"
                disabled={!formData.name || !formData.url}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .collection-page {
          max-width: 1000px;
          margin: 0 auto;
        }

        .tabs {
          display: flex;
          gap: 4px;
          margin-bottom: 24px;
          border-bottom: 1px solid var(--border);
        }

        .tab {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 20px;
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          border-bottom: 2px solid transparent;
          transition: all 0.2s ease;
        }

        .tab:hover {
          color: var(--text);
          background: var(--elev);
        }

        .tab.active {
          color: var(--primary);
          border-bottom-color: var(--primary);
        }

        .sources-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
          padding: 20px;
        }

        .source-item {
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 20px;
          background: var(--panel);
        }

        .source-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 16px;
        }

        .source-info {
          flex: 1;
        }

        .source-title {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 8px;
        }

        .source-title h3 {
          margin: 0;
          color: var(--text);
          font-size: 18px;
        }

        .source-status {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .status-text {
          font-size: 12px;
          font-weight: 500;
        }

        .status-text.active {
          color: var(--success);
        }

        .status-text.paused {
          color: var(--warning);
        }

        .status-text.error {
          color: var(--danger);
        }

        .source-description {
          color: var(--muted);
          margin: 0 0 12px;
          line-height: 1.5;
        }

        .source-meta {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .source-url {
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--primary);
          text-decoration: none;
          font-size: 14px;
        }

        .source-url:hover {
          text-decoration: underline;
        }

        .source-tags {
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

        .source-actions {
          display: flex;
          gap: 8px;
          flex-shrink: 0;
        }

        .source-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 16px;
          padding-top: 16px;
          border-top: 1px solid var(--border);
        }

        .stat {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .stat-label {
          font-size: 12px;
          color: var(--muted);
        }

        .stat-value {
          font-size: 14px;
          font-weight: 500;
          color: var(--text);
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

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal {
          background: var(--bg);
          border-radius: var(--radius);
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
          border: 1px solid var(--border);
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid var(--border);
        }

        .modal-header h2 {
          margin: 0;
          color: var(--text);
        }

        .modal-body {
          padding: 20px;
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }

        .checkbox-group {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-top: 8px;
        }

        .checkbox-group input[type="checkbox"] {
          margin: 0;
        }

        .filters-section {
          margin-top: 24px;
          padding-top: 20px;
          border-top: 1px solid var(--border);
        }

        .filters-section h3 {
          margin: 0 0 16px;
          color: var(--text);
          font-size: 16px;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          padding: 20px;
          border-top: 1px solid var(--border);
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 14px;
        }

        .btn-icon {
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          padding: 8px;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .btn-icon:hover {
          background: var(--elev);
          color: var(--text);
        }

        .btn-icon.danger:hover {
          background: rgba(239, 68, 68, 0.1);
          color: var(--danger);
        }

        @media (max-width: 768px) {
          .source-header {
            flex-direction: column;
            gap: 16px;
          }

          .source-actions {
            align-self: stretch;
            justify-content: space-between;
          }

          .source-stats {
            grid-template-columns: repeat(2, 1fr);
          }

          .form-row {
            grid-template-columns: 1fr;
          }

          .modal {
            width: 95%;
            margin: 20px;
          }
        }
      `}</style>
    </div>
  )
}

export default RssPage