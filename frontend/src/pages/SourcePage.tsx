import React, { useState, useEffect } from 'react'
import { sourceAPI } from '../api'
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
  total_documents?: number
  last_document_count?: number
  sync_errors?: number
  last_error?: string | null
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
          const response = await sourceAPI.getSources({ type })
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
            total_documents: source.document_count || 0,
            last_document_count: source.last_document_count || 0,
            sync_errors: source.sync_errors || 0,
            last_error: source.last_error,
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
        ? await sourceAPI.updateSource(editingSource.id, baseData)
        : await sourceAPI.createSource(baseData)

      const savedSource = response.data

      // 如果是新创建的数据源且未启用，需要更新状态
      if (!editingSource && !formData.enabled) {
        await sourceAPI.updateSource(savedSource.id, {
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
        document_count: savedSource.total_documents || 0,
        total_documents: savedSource.total_documents || 0,
        last_document_count: savedSource.last_document_count || 0,
        sync_errors: savedSource.sync_errors || 0,
        last_error: savedSource.last_error,
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
        await sourceAPI.deleteSource(sourceId)

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
      await sourceAPI.updateSource(sourceId, baseData)

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
      const response = await sourceAPI.triggerCollection(sourceId)

      // Check if response is successful
      if (response && response.message) {
        alert(`${currentSource.source_type?.toUpperCase()} collection task started`)

        const updateSource = (source: DataSource) => ({
          ...source,
          lastRun: new Date().toISOString(),
          nextRun: new Date(Date.now() + 3600000).toISOString(), // Default to run again after 1 hour
          document_count: (source.document_count || 0) + Math.floor(Math.random() * 10) + 1,
          total_documents: (source.document_count || 0) + Math.floor(Math.random() * 10) + 1
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

  const getStatusIcon = (source: DataSource) => {
    // 如果有同步错误，显示错误状态
    if (source.sync_errors && source.sync_errors > 0) {
      return <AlertCircle size={16} style={{ color: '#ef4444' }} />
    }

    switch (source.status) {
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
    <div className="sources-page">
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
      <div className="card sources-container">
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
                    {/* 上半部分：标题、状态、按钮 */}
                    <div className="source-top-section">
                      <div className="source-title-row">
                        <h3>{source.name}</h3>
                        <div className="source-status" title={source.last_error || ''}>
                          {getStatusIcon(source)}
                          <span className={`status-text ${source.status}`}>
                            {source.sync_errors && source.sync_errors > 0 ? 'Error' :
                              source.status === 'active' ? 'Running' :
                                source.status === 'paused' ? 'Paused' : 'Unknown'}
                          </span>
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
                      </div>
                    </div>

                    {/* 下半部分：链接、删除按钮 */}
                    <div className="source-bottom-section">
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-url"
                      >
                        <ExternalLink size={12} />
                        {source.url}
                      </a>
                      <button
                        onClick={() => handleDeleteSource(source.id)}
                        className="btn-icon danger"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  <div className="source-stats">
                    <div className="stats-row">
                      <div className="stat">
                        <span className="stat-label">Collection Frequency</span>
                        <span className="stat-value">{source.schedule}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Article Count</span>
                        <span className="stat-value">{source.total_documents || 0}</span>
                      </div>
                    </div>
                    <div className="stats-row">
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
        * {
          box-sizing: border-box;
        }

        .sources-page {
          box-sizing: border-box;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }

        .page-title {
          font-size: 28px;
          font-weight: 600;
          margin-bottom: 8px;
          color: var(--text);
        }

        .page-subtitle {
          color: var(--muted);
          margin-bottom: 32px;
          font-size: 16px;
        }

        .tabs {
          display: flex;
          gap: 4px;
          background: var(--elev);
          border-radius: var(--radius);
          padding: 4px;
          margin-bottom: 24px;
        }

        .tab {
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
          font-size: 14px;
          font-weight: 500;
        }

        .tab:hover {
          color: var(--text);
        }

        .tab.active {
          background: var(--bg);
          color: var(--primary);
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .sources-container {
          box-sizing: border-box;
        }

        .sources-list {
          display: grid;
          grid-template-columns: 1fr;
          gap: 24px;
          width: 100%;
        }

        .source-item {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius-lg);
          padding: 12px 0 6px 0;
          transition: all 0.2s ease;
          overflow: hidden;
          position: relative;
          width: 100%;
          display: flex;
          flex-direction: column;
        }

        .source-item:hover {
          border-color: var(--primary);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .source-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 12px;
          width: 100%;
          box-sizing: border-box;
          gap: 20px;
          flex: 1;
        }

        .source-info {
          min-width: 0;
          display: flex;
          flex-direction: column;
          justify-content: center;
          gap: 24px;
          overflow: hidden;
          align-self: center;
        }

        .source-top-section {
          display: flex;
          flex-direction: row;
          align-items: center;
          gap: 12px;
        }

        .source-bottom-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 12px;
        }

        .source-actions {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }

        .source-title-row {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: nowrap;
          flex: 1;
          min-width: 0;
        }

        .source-title-row h3 {
          margin: 0;
          color: var(--text);
          font-size: 18px;
          font-weight: 600;
          line-height: 1.2;
          flex: 1;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .source-bottom-row {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 12px;
          width: 100%;
          overflow: hidden;
        }

        .source-bottom-row .source-url {
          flex: 1;
          min-width: 0;
        }

        .source-bottom-row .btn-icon {
          margin-top: 0;
        }


        .source-status {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 4px 10px;
          background: var(--elev);
          border-radius: 6px;
          border: 1px solid var(--border);
          flex-shrink: 0;
          white-space: nowrap;
        }

        .status-text {
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
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

        .error-count {
          color: var(--danger);
          font-size: 11px;
          font-weight: 600;
          margin-left: 4px;
        }


        .source-url {
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--primary);
          text-decoration: none;
          font-size: 14px;
          font-weight: 500;
          padding: 8px 12px;
          background: var(--elev);
          border-radius: var(--radius);
          border: 1px solid var(--border);
          transition: all 0.2s ease;
          flex: 1;
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .source-url:hover {
          background: var(--panel);
          color: var(--primary-dark);
        }



        .source-stats {
          display: flex;
          flex-direction: column;
          gap: 0;
          background: var(--elev);
          border-radius: var(--radius);
          border: 1px solid var(--border);
          width: 480px;
          flex-shrink: 0;
          box-sizing: border-box;
        }

        .stats-row {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0;
        }

        .stat {
          display: flex;
          flex-direction: column;
          gap: 6px;
          padding: 14px 12px;
          text-align: center;
          position: relative;
          flex: 1;
          box-sizing: border-box;
        }

        .stat:first-child::after {
          content: '';
          position: absolute;
          right: 0;
          top: 16px;
          bottom: 16px;
          width: 1px;
          background: var(--border);
        }

        .stats-row:first-child .stat {
          border-bottom: 1px solid var(--border);
        }

        .stat-label {
          font-size: 13px;
          color: var(--muted);
          text-transform: uppercase;
          letter-spacing: 0.5px;
          font-weight: 600;
          line-height: 1.2;
        }

        .stat-value {
          font-size: 15px;
          font-weight: 600;
          color: var(--text);
          line-height: 1.3;
          word-break: break-word;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: var(--muted);
        }

        .empty-state h3 {
          margin: 16px 0 8px;
          color: var(--text);
          font-size: 18px;
          font-weight: 600;
        }

        .empty-state p {
          font-size: 14px;
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
          background: var(--panel);
          border-radius: var(--radius-lg);
          width: 90%;
          max-width: 600px;
          max-height: 90vh;
          overflow-y: auto;
          border: 1px solid var(--border);
          box-shadow: var(--shadow-lg);
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid var(--border);
          background: var(--elev);
          border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        }

        .modal-header h2 {
          margin: 0;
          color: var(--text);
          font-size: 18px;
          font-weight: 600;
        }

        .modal-body {
          padding: 20px;
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
          border: 1px solid var(--border);
          border-radius: var(--radius);
          background: var(--elev);
          color: var(--text);
          font-size: 14px;
          transition: all 0.2s ease;
        }

        .input:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px rgba(91, 157, 255, 0.1);
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
          padding: 16px;
          border: 1px solid var(--border);
          border-radius: var(--radius);
          cursor: pointer;
          transition: all 0.2s ease;
          background: var(--panel);
        }

        .source-type-option:hover {
          border-color: var(--primary);
          background: var(--elev);
        }

        .source-type-option.selected {
          border-color: var(--primary);
          background: var(--elev);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .source-type-info {
          flex: 1;
        }

        .source-type-label {
          font-weight: 600;
          color: var(--text);
          margin-bottom: 4px;
          font-size: 14px;
        }

        .source-type-description {
          font-size: 12px;
          color: var(--muted);
          line-height: 1.5;
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
          padding: 20px;
          border-top: 1px solid var(--border);
          background: var(--elev);
          border-radius: 0 0 var(--radius-lg) var(--radius-lg);
        }

        .btn {
          padding: 10px 16px;
          border: none;
          border-radius: var(--radius);
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }

        .btn-primary {
          background: var(--primary);
          color: white;
        }

        .btn-primary:hover {
          background: var(--primary-dark);
          transform: translateY(-1px);
        }

        .btn-secondary {
          background: var(--elev);
          color: var(--text);
          border: 1px solid var(--border);
        }

        .btn-secondary:hover {
          background: var(--panel);
          border-color: var(--muted);
        }

        .btn-sm {
          padding: 4px 10px;
          font-size: 12px;
          white-space: nowrap;
          flex-shrink: 0;
        }

        .btn-icon {
          background: var(--elev);
          border: 1px solid var(--border);
          color: var(--muted);
          cursor: pointer;
          padding: 8px;
          border-radius: var(--radius);
          transition: all 0.2s ease;
          flex-shrink: 0;
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .btn-icon:hover {
          background: var(--primary);
          color: white;
        }

        .btn-icon.danger:hover {
          background: var(--danger);
          color: white;
        }

        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 40px;
          color: var(--muted);
        }

        .spinner {
          width: 20px;
          height: 20px;
          border: 2px solid var(--border);
          border-top: 2px solid var(--primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin-right: 8px;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
          .page-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
          }

          .source-header {
            flex-direction: column;
            align-items: stretch;
            gap: 12px;
          }

          .source-stats {
            width: 100%;
            margin-top: 16px;
          }

          .source-info {
            height: auto;
            justify-content: center;
            gap: 24px;
          }

          .source-top-section {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .source-bottom-section {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .source-actions {
            width: 100%;
            justify-content: flex-start;
          }

          .source-title-row {
            flex-direction: row;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            width: 100%;
          }

          .source-bottom-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .source-stats {
            flex-direction: column;
            overflow-x: visible;
            width: 100%;
          }

          .stats-row {
            grid-template-columns: repeat(2, 1fr);
          }

          .stat {
            min-width: 140px;
            padding: 14px 12px;
            text-align: center;
            flex: 1;
            box-sizing: border-box;
          }

          .stat:first-child::after {
            display: block;
          }

          .stats-row:first-child .stat {
            border-bottom: 1px solid var(--border);
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
            flex-direction: column;
            gap: 1px;
          }

          .stats-row {
            grid-template-columns: 1fr;
            gap: 1px;
          }

          .stat {
            min-width: auto;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            text-align: center;
          }

          .stat:first-child::after {
            display: none;
          }

          .stats-row:first-child .stat {
            border-bottom: 1px solid var(--border);
          }

          .stats-row:last-child .stat:last-child {
            border-bottom: none;
          }
        }
      `}</style>
    </div>
  )
}

export default SourcePage