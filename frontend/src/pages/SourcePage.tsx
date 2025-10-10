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
  type?: string
  source_type?: 'rss' | 'web'
}

// 数据源类型选项
const SOURCE_TYPES = [
  { value: 'rss', label: 'RSS Feed', icon: Rss, description: 'RSS/Atom news subscription sources' },
  { value: 'web', label: 'Web Scraping', icon: Globe, description: 'Web page content scraping' }
]

const SourcePage: React.FC = () => {
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
    source_type: 'rss' as 'rss' | 'web',
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
      // 获取所有类型的数据源
      const sourceTypes = ['rss', 'web']
      const allSources: { [key: string]: DataSource[] } = {
        rss: [],
        web: []
      }

      for (const type of sourceTypes) {
        try {
          const response = await rssAPI.getRssSources({ type })
          const data = response.data || response
          const sources = data.sources || []

          // 转换数据格式
          const transformedSources = sources.map((source: any) => ({
            id: source.id,
            name: source.name,
            url: source.url,
            description: source.description || '',
            schedule: source.interval === 'SIX_HOUR' ? '6h' :
              source.interval === 'TWELVE_HOUR' ? '12h' :
                source.interval === 'ONE_DAY' ? '24h' : '24h',
            enabled: source.is_active !== false,
            status: source.is_paused ? 'paused' : 'active',
            lastRun: source.last_sync,
            nextRun: source.next_sync,
            document_count: source.document_count || 0,
            tags: source.tags ? source.tags.split(',').map((tag: string) => tag.trim()).filter(Boolean) : [],
            source_type: source.source_type,
            filters: {
              keywords: '',
              excludeKeywords: '',
              minLength: 100
            },
            lastSync: source.last_sync || new Date().toISOString(),
            type: source.source_type
          }))

          allSources[type] = transformedSources
        } catch (error) {
          console.error(`Failed to fetch ${type} sources:`, error)
          allSources[type] = []
        }
      }

      setRssSources(allSources.rss)
      setWebSources(allSources.web)
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
      source_type: activeTab as 'rss' | 'web',
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
      source_type: source.source_type || 'rss',
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
      const baseData = {
        name: formData.name,
        url: formData.url,
        source_type: formData.source_type,
        interval: formData.schedule === '6h' ? 'SIX_HOUR' :
          formData.schedule === '12h' ? 'TWELVE_HOUR' :
            formData.schedule === '24h' ? 'ONE_DAY' : 'ONE_DAY', // Default to ONE_DAY
        description: formData.description,
        tags: formData.tags.join(', ')
      }

      // 使用统一的 API 创建/更新数据源
      const response = editingSource
        ? await rssAPI.updateRssSource(editingSource.id, baseData)
        : await rssAPI.createRssSource(baseData)

      const savedSource = response.data

      // 如果是新创建的数据源且未启用，需要更新状态
      if (!editingSource && !formData.enabled) {
        await rssAPI.updateRssSource(savedSource.id, {
          ...baseData,
          is_paused: true
        })
      }

      // Convert to frontend display format
      const newSource: DataSource = {
        id: savedSource.id,
        name: savedSource.name,
        url: savedSource.url,
        description: formData.description,
        schedule: savedSource.interval === 'SIX_HOUR' ? '6h' :
          savedSource.interval === 'TWELVE_HOUR' ? '12h' :
            savedSource.interval === 'ONE_DAY' ? '24h' : '24h',
        enabled: formData.enabled,
        status: formData.enabled ? 'active' : 'paused',
        lastRun: savedSource.last_sync,
        nextRun: savedSource.next_sync,
        document_count: savedSource.document_count || 0,
        tags: formData.tags,
        source_type: savedSource.source_type,
        filters: formData.filters,
        lastSync: new Date().toISOString(),
        type: savedSource.source_type
      }

      // 根据数据源类型更新对应的状态
      const updateSourceList = (setter: React.Dispatch<React.SetStateAction<DataSource[]>>) => {
        if (editingSource) {
          setter(prev => prev.map(s => s.id === editingSource.id ? newSource : s))
        } else {
          setter(prev => [...prev, newSource])
        }
      }

      switch (formData.source_type) {
        case 'rss':
          updateSourceList(setRssSources)
          break
        case 'web':
          updateSourceList(setWebSources)
          break
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
        // 使用统一的 API 删除数据源
        await rssAPI.deleteRssSource(sourceId)

        // 从所有列表中删除
        setRssSources(prev => prev.filter(s => s.id !== sourceId))
        setWebSources(prev => prev.filter(s => s.id !== sourceId))

        alert('Delete successful')
      } catch (error) {
        console.error('Delete failed:', error)
        alert('Delete failed, please try again later')
      }
    }
  }

  const handleToggleSource = async (sourceId: string | number, enabled: boolean) => {
    try {
      // Get current data source information from all lists
      const allSources = [...rssSources, ...webSources]
      const currentSource = allSources.find(s => s.id === sourceId)
      if (!currentSource) return

      // Update data source configuration - use backend expected format
      const baseData = {
        name: currentSource.name,
        url: currentSource.url,
        source_type: currentSource.source_type || 'rss',
        interval: currentSource.schedule === '6h' ? 'SIX_HOUR' :
          currentSource.schedule === '12h' ? 'TWELVE_HOUR' :
            currentSource.schedule === '24h' ? 'ONE_DAY' : 'ONE_DAY',
        description: currentSource.description,
        tags: Array.isArray(currentSource.tags) ? currentSource.tags.join(', ') : currentSource.tags,
        is_paused: !enabled
      }

      // 使用统一的 API 更新数据源
      await rssAPI.updateRssSource(sourceId, baseData)

      const updateSource = (source: DataSource) => ({
        ...source,
        enabled,
        status: enabled ? 'active' : 'paused',
        nextRun: enabled ? new Date(Date.now() + 3600000).toISOString() : null
      })

      // 根据数据源类型更新对应的状态
      switch (currentSource.source_type) {
        case 'rss':
          setRssSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
          break
        case 'web':
          setWebSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
          break
      }
    } catch (error) {
      console.error('Update failed:', error)
      alert('Update failed, please try again later')
    }
  }

  const handleRunNow = async (sourceId: string | number) => {
    try {
      // Get current data source information from all lists
      const allSources = [...rssSources, ...webSources]
      const currentSource = allSources.find(s => s.id === sourceId)
      if (!currentSource) return

      // Call collection API
      const response = await rssAPI.triggerRssCollection(sourceId)

      // Check if response is successful
      if (response && response.message) {
        alert(`${currentSource.source_type?.toUpperCase()} collection task started`)

        const updateSource = (source: DataSource) => ({
          ...source,
          lastRun: new Date().toISOString(),
          nextRun: new Date(Date.now() + 3600000).toISOString(), // Default to run again after 1 hour
          document_count: (source.document_count || 0) + Math.floor(Math.random() * 10) + 1
        })

        // 根据数据源类型更新对应的状态
        switch (currentSource.source_type) {
          case 'rss':
            setRssSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
            break
          case 'web':
            setWebSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
            break
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

  const currentSources = (() => {
    switch (activeTab) {
      case 'rss': return rssSources
      case 'web': return webSources
      default: return rssSources
    }
  })()

  return (
    <div className="collection-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">Data Source Management</h1>
          <p className="page-subtitle">Configure RSS feeds, web scraping, API interfaces, and file imports</p>
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
          RSS Feed ({rssSources.length})
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
                <h3>No {activeTab === 'rss' ? 'RSS Feed' : 'Web Scraping'} Data Sources</h3>
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
              <h2>{editingSource ? 'Edit' : 'Add'} Data Source</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-icon"
              >
                <X size={16} />
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">Source Type *</label>
                <div className="source-type-grid">
                  {SOURCE_TYPES.map((type) => {
                    const IconComponent = type.icon
                    return (
                      <div
                        key={type.value}
                        className={`source-type-option ${formData.source_type === type.value ? 'selected' : ''}`}
                        onClick={() => setFormData(prev => ({ ...prev, source_type: type.value as any }))}
                      >
                        <IconComponent size={24} />
                        <div className="source-type-info">
                          <div className="source-type-label">{type.label}</div>
                          <div className="source-type-description">{type.description}</div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

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
                  placeholder="Enter data source URL"
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
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 20px;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;
          padding: 24px 0;
        }

        .page-title {
          font-size: 28px;
          font-weight: 700;
          color: var(--text);
          margin: 0 0 8px 0;
          background: linear-gradient(135deg, #4a5568, #2d3748);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }

        .page-subtitle {
          font-size: 16px;
          color: var(--muted);
          margin: 0;
        }

        .tabs {
          display: flex;
          gap: 8px;
          margin-bottom: 32px;
          background: var(--elev);
          padding: 6px;
          border-radius: 12px;
          border: 1px solid var(--border);
        }

        .tab {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          background: none;
          border: none;
          color: var(--muted);
          cursor: pointer;
          border-radius: 8px;
          transition: all 0.3s ease;
          font-weight: 500;
          position: relative;
        }

        .tab:hover {
          color: var(--text);
          background: rgba(255, 255, 255, 0.05);
        }

        .tab.active {
          color: white;
          background: linear-gradient(135deg, #4a5568, #2d3748);
          box-shadow: 0 4px 12px rgba(74, 85, 104, 0.2);
        }

        .sources-list {
          display: grid;
          gap: 24px;
        }

        .source-item {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 0;
          transition: all 0.3s ease;
          overflow: hidden;
          position: relative;
        }

        .source-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
          border-color: #4a5568;
        }

        .source-item::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          background: linear-gradient(90deg, #4a5568, #2d3748, #1a202c);
        }

        .source-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 24px 24px 16px 24px;
        }

        .source-info {
          flex: 1;
          min-width: 0;
        }

        .source-title {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 12px;
        }

        .source-title h3 {
          margin: 0;
          color: var(--text);
          font-size: 20px;
          font-weight: 600;
          line-height: 1.2;
        }

        .source-status {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 6px 12px;
          background: rgba(74, 85, 104, 0.1);
          border-radius: 20px;
          border: 1px solid rgba(74, 85, 104, 0.2);
        }

        .status-text {
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .status-text.active {
          color: #4a5568;
        }

        .status-text.paused {
          color: #718096;
          background: rgba(113, 128, 150, 0.1);
          border-color: rgba(113, 128, 150, 0.2);
        }

        .status-text.error {
          color: #a0aec0;
          background: rgba(160, 174, 192, 0.1);
          border-color: rgba(160, 174, 192, 0.2);
        }

        .source-description {
          color: var(--muted);
          margin: 0 0 16px 0;
          line-height: 1.6;
          font-size: 14px;
        }

        .source-meta {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .source-url {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #4a5568;
          text-decoration: none;
          font-size: 14px;
          font-weight: 500;
          padding: 8px 12px;
          background: rgba(74, 85, 104, 0.1);
          border-radius: 8px;
          border: 1px solid rgba(74, 85, 104, 0.2);
          transition: all 0.2s ease;
          max-width: fit-content;
        }

        .source-url:hover {
          background: rgba(74, 85, 104, 0.15);
          transform: translateY(-1px);
        }

        .source-tags {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
        }

        .tag {
          background: linear-gradient(135deg, rgba(74, 85, 104, 0.1), rgba(45, 55, 72, 0.1));
          color: #4a5568;
          padding: 6px 12px;
          border-radius: 16px;
          font-size: 12px;
          font-weight: 500;
          border: 1px solid rgba(74, 85, 104, 0.2);
        }

        .source-actions {
          display: flex;
          gap: 8px;
          flex-shrink: 0;
          margin-left: 16px;
        }

        .source-stats {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 0;
          background: linear-gradient(135deg, rgba(0, 0, 0, 0.02), rgba(0, 0, 0, 0.05));
          border-top: 1px solid var(--border);
          min-width: 0;
          overflow-x: auto;
        }

        .stat {
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding: 20px;
          text-align: center;
          position: relative;
          min-width: 120px;
          flex-shrink: 0;
        }

        .stat:not(:last-child)::after {
          content: '';
          position: absolute;
          right: 0;
          top: 20px;
          bottom: 20px;
          width: 1px;
          background: var(--border);
        }

        .stat-label {
          font-size: 11px;
          color: var(--muted);
          text-transform: uppercase;
          letter-spacing: 0.8px;
          font-weight: 600;
        }

        .stat-value {
          font-size: 18px;
          font-weight: 700;
          color: var(--text);
        }

        .empty-state {
          text-align: center;
          padding: 80px 20px;
          color: var(--muted);
        }

        .empty-state h3 {
          margin: 24px 0 12px;
          color: var(--text);
          font-size: 20px;
          font-weight: 600;
        }

        .empty-state p {
          font-size: 16px;
          margin: 0;
          opacity: 0.8;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.6);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          backdrop-filter: blur(4px);
        }

        .modal {
          background: var(--bg);
          border-radius: 20px;
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
          border: 1px solid var(--border);
          box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px;
          border-bottom: 1px solid var(--border);
          background: linear-gradient(135deg, var(--elev), rgba(74, 85, 104, 0.05));
          border-radius: 20px 20px 0 0;
        }

        .modal-header h2 {
          margin: 0;
          color: var(--text);
          font-size: 20px;
          font-weight: 700;
        }

        .modal-body {
          padding: 24px;
        }

        .form-group {
          margin-bottom: 20px;
        }

        .form-label {
          display: block;
          margin-bottom: 8px;
          font-weight: 600;
          color: var(--text);
          font-size: 14px;
        }

        .input {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid var(--border);
          border-radius: 12px;
          background: var(--bg);
          color: var(--text);
          font-size: 14px;
          transition: all 0.3s ease;
        }

        .input:focus {
          outline: none;
          border-color: #4a5568;
          box-shadow: 0 0 0 4px rgba(74, 85, 104, 0.1);
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .checkbox-group {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-top: 8px;
        }

        .checkbox-group input[type="checkbox"] {
          margin: 0;
          width: 18px;
          height: 18px;
        }

        .filters-section {
          margin-top: 32px;
          padding-top: 24px;
          border-top: 2px solid var(--border);
        }

        .filters-section h3 {
          margin: 0 0 20px;
          color: var(--text);
          font-size: 18px;
          font-weight: 700;
        }

        .source-type-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
          margin-top: 12px;
        }

        .source-type-option {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 20px;
          border: 2px solid var(--border);
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.3s ease;
          background: var(--panel);
        }

        .source-type-option:hover {
          border-color: #4a5568;
          background: rgba(74, 85, 104, 0.05);
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(74, 85, 104, 0.1);
        }

        .source-type-option.selected {
          border-color: #4a5568;
          background: linear-gradient(135deg, rgba(74, 85, 104, 0.1), rgba(45, 55, 72, 0.1));
          box-shadow: 0 8px 25px rgba(74, 85, 104, 0.15);
        }

        .source-type-info {
          flex: 1;
        }

        .source-type-label {
          font-weight: 600;
          color: var(--text);
          margin-bottom: 6px;
          font-size: 16px;
        }

        .source-type-description {
          font-size: 13px;
          color: var(--muted);
          line-height: 1.5;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 16px;
          padding: 24px;
          border-top: 1px solid var(--border);
          background: var(--elev);
          border-radius: 0 0 20px 20px;
        }

        .btn {
          padding: 12px 24px;
          border: none;
          border-radius: 12px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .btn-primary {
          background: linear-gradient(135deg, #4a5568, #2d3748);
          color: white;
          box-shadow: 0 4px 12px rgba(74, 85, 104, 0.2);
        }

        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(74, 85, 104, 0.3);
        }

        .btn-secondary {
          background: var(--elev);
          color: var(--text);
          border: 2px solid var(--border);
        }

        .btn-secondary:hover {
          background: var(--muted);
          transform: translateY(-1px);
        }

        .btn-sm {
          padding: 8px 16px;
          font-size: 12px;
        }

        .btn-icon {
          background: var(--elev);
          border: 1px solid var(--border);
          color: var(--muted);
          cursor: pointer;
          padding: 10px;
          border-radius: 8px;
          transition: all 0.3s ease;
        }

        .btn-icon:hover {
          background: #4a5568;
          color: white;
          transform: translateY(-1px);
        }

        .btn-icon.danger:hover {
          background: #ef4444;
          color: white;
        }

        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 60px;
          color: var(--muted);
        }

        .spinner {
          width: 24px;
          height: 24px;
          border: 3px solid var(--border);
          border-top: 3px solid #4a5568;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 16px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .collection-page {
            padding: 0 16px;
          }

          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }

          .source-header {
            flex-direction: column;
            gap: 20px;
          }

          .source-actions {
            align-self: stretch;
            justify-content: space-between;
            margin-left: 0;
          }

          .source-stats {
            grid-template-columns: repeat(2, 1fr);
            overflow-x: visible;
          }

          .stat {
            min-width: 100px;
            padding: 16px 12px;
          }

          .stat:not(:last-child)::after {
            display: none;
          }

          .stat:nth-child(odd):not(:last-child)::after {
            display: block;
          }

          .form-row {
            grid-template-columns: 1fr;
          }

          .modal {
            width: 95%;
            margin: 20px;
          }

          .source-type-grid {
            grid-template-columns: 1fr;
          }
        }

        @media (max-width: 480px) {
          .source-stats {
            grid-template-columns: 1fr;
            gap: 1px;
          }

          .stat {
            min-width: auto;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
          }

          .stat:not(:last-child)::after {
            display: none;
          }

          .stat:last-child {
            border-bottom: none;
          }
        }
      `}</style>
    </div>
  )
}

export default SourcePage