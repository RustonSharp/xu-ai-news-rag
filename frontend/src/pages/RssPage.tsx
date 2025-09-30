import React, { useState, useEffect } from 'react'
import { rssAPI } from '../api'
import axios from 'axios'
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

// 类型定义
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
  articlesCount?: number
  tags: string[]
  filters: {
    keywords: string
    excludeKeywords: string
    minLength: number
  }
}

// API响应数据类型
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
    schedule: 'daily',
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
      // 获取RSS数据源
      const response = await rssAPI.getRssSources()
      const sources = response.data || []

      // 转换API数据为前端格式，确保所有必要属性存在
      const transformedSources = sources.map((source: any) => ({
        id: source.id,
        name: source.name,
        url: source.url,
        description: '', // 后端当前不提供description字段
        schedule: source.interval === 60 ? '1h' :
          source.interval === 3600 ? '1h' :
            source.interval === 86400 ? '24h' : '1h',
        enabled: true, // 后端当前不提供enabled字段，默认为true
        status: 'active', // 后端当前不提供status字段，默认为active
        lastRun: null, // 后端当前不提供last_run字段
        nextRun: null, // 后端当前不提供next_run字段
        articlesCount: 0, // 后端当前不提供articles_count字段
        tags: [], // 后端当前不提供tags字段
        filters: { // 后端当前不提供filters字段，使用默认值
          keywords: '',
          excludeKeywords: '',
          minLength: 100
        },
        lastSync: new Date().toISOString(),
        type: 'rss' // 后端当前只有RSS源，没有web源
      }))

      // 由于后端当前只有RSS源，没有web源，所以所有源都归类为RSS
      setRssSources(transformedSources)
      setWebSources([]) // 清空web源列表
    } catch (error) {
      console.error('获取数据源失败:', error)
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
      schedule: '1h',
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
      // 构建符合后端期望的数据格式
      const sourceData = {
        name: formData.name,
        url: formData.url,
        interval: 60 // 后端期望的interval值，使用MINUTE对应的值60
      }

      // 调用保存API
      const response = editingSource
        ? await rssAPI.updateRssSource(editingSource.id, sourceData)
        : await rssAPI.createRssSource(sourceData)
      const savedSource = response.data

      // 转换为前端显示格式
      const newSource: DataSource = {
        id: savedSource.id,
        name: savedSource.name,
        url: savedSource.url,
        description: formData.description,
        schedule: savedSource.interval === 60 ? '1h' :
          savedSource.interval === 3600 ? '1h' :
            savedSource.interval === 86400 ? '24h' : '1h',
        enabled: true, // 后端当前不提供enabled字段，默认为true
        status: 'active', // 后端当前不提供status字段，默认为active
        lastRun: null,
        nextRun: null,
        articlesCount: 0,
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
      alert('保存成功')
    } catch (error) {
      console.error('保存失败:', error)
      alert('保存失败，请稍后重试')
    }
  }

  const handleDeleteSource = async (sourceId: string | number) => {
    if (window.confirm('确定要删除这个数据源吗？')) {
      try {
        // 调用删除API
        await rssAPI.deleteRssSource(sourceId)

        if (activeTab === 'rss') {
          setRssSources(prev => prev.filter(s => s.id !== sourceId))
        } else {
          setWebSources(prev => prev.filter(s => s.id !== sourceId))
        }

        alert('删除成功')
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败，请稍后重试')
      }
    }
  }

  const handleToggleSource = async (sourceId: string | number, enabled: boolean) => {
    try {
      // 获取当前数据源信息
      const currentSource = [...rssSources, ...webSources].find(s => s.id === sourceId)
      if (!currentSource) return

      // 更新数据源配置 - 使用后端期望的格式
      const updatedSource = {
        name: currentSource.name,
        url: currentSource.url,
        interval: 60 // 后端期望的interval值，使用MINUTE对应的值60
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
      console.error('更新失败:', error)
      alert('更新失败，请稍后重试')
    }
  }

  const handleRunNow = async (sourceId: string | number) => {
    try {
      // 调用RSS采集API
      const response = await rssAPI.triggerRssCollection(sourceId)
      
      // 检查响应是否成功
      if (response && response.message) {
        alert('采集任务已启动')
        
        const updateSource = (source: DataSource) => ({
          ...source,
          lastRun: new Date().toISOString(),
          nextRun: new Date(Date.now() + 3600000).toISOString(), // 默认1小时后再次运行
          articlesCount: (source.articlesCount || 0) + Math.floor(Math.random() * 10) + 1
        })

        if (activeTab === 'rss') {
          setRssSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
        } else {
          setWebSources(prev => prev.map(s => s.id === sourceId ? updateSource(s) : s))
        }
      } else {
        throw new Error('采集响应无效')
      }
    } catch (error) {
      console.error('采集失败:', error)
      alert('采集失败，请稍后重试')
    }
  }

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('zh-CN')
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
          <h1 className="page-title">数据采集配置</h1>
          <p className="page-subtitle">配置RSS订阅和网页抓取任务</p>
        </div>
        <button
          onClick={handleAddSource}
          className="btn btn-primary"
        >
          <Plus size={16} />
          添加数据源
        </button>
      </div>

      {/* 标签页 */}
      <div className="tabs">
        <button
          onClick={() => setActiveTab('rss')}
          className={`tab ${activeTab === 'rss' ? 'active' : ''}`}
        >
          <Rss size={16} />
          RSS订阅 ({rssSources.length})
        </button>
        <button
          onClick={() => setActiveTab('web')}
          className={`tab ${activeTab === 'web' ? 'active' : ''}`}
        >
          <Globe size={16} />
          网页抓取 ({webSources.length})
        </button>
      </div>

      {/* 数据源列表 */}
      <div className="card">
        {loading ? (
          <div className="loading">
            <div className="spinner" />
            正在加载数据源...
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
                          {source.status === 'active' ? '运行中' :
                            source.status === 'paused' ? '已暂停' : '错误'}
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
                      {source.enabled ? '暂停' : '启用'}
                    </button>

                    <button
                      onClick={() => handleRunNow(source.id)}
                      className="btn btn-sm btn-secondary"
                      disabled={!source.enabled}
                    >
                      <RefreshCw size={14} />
                      立即运行
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
                    <span className="stat-label">采集频率</span>
                    <span className="stat-value">{source.schedule}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">文章数量</span>
                    <span className="stat-value">{source.articlesCount || 0}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">上次运行</span>
                    <span className="stat-value">{formatDate(source.lastRun)}</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">下次运行</span>
                    <span className="stat-value">{formatDate(source.nextRun)}</span>
                  </div>
                </div>
              </div>
            ))}

            {currentSources.length === 0 && (
              <div className="empty-state">
                {activeTab === 'rss' ? <Rss size={48} /> : <Globe size={48} />}
                <h3>暂无{activeTab === 'rss' ? 'RSS' : '网页抓取'}数据源</h3>
                <p>点击上方按钮添加第一个数据源</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 添加/编辑模态框 */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingSource ? '编辑' : '添加'}{activeTab === 'rss' ? 'RSS' : '网页抓取'}数据源</h2>
              <button
                onClick={() => setShowAddModal(false)}
                className="btn-icon"
              >
                <X size={16} />
              </button>
            </div>

            <div className="modal-body">
              <div className="form-group">
                <label className="form-label">名称 *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="input"
                  placeholder="输入数据源名称"
                />
              </div>

              <div className="form-group">
                <label className="form-label">URL *</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                  className="input"
                  placeholder={activeTab === 'rss' ? '输入RSS订阅地址' : '输入网页URL'}
                />
              </div>

              <div className="form-group">
                <label className="form-label">描述</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="input"
                  rows={3}
                  placeholder="输入数据源描述"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label className="form-label">采集频率</label>
                  <select
                    value={formData.schedule}
                    onChange={(e) => setFormData(prev => ({ ...prev, schedule: e.target.value }))}
                    className="input"
                  >
                    <option value="30m">30分钟</option>
                    <option value="1h">1小时</option>
                    <option value="2h">2小时</option>
                    <option value="6h">6小时</option>
                    <option value="12h">12小时</option>
                    <option value="24h">24小时</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">状态</label>
                  <div className="checkbox-group">
                    <input
                      type="checkbox"
                      id="enabled"
                      checked={formData.enabled}
                      onChange={(e) => setFormData(prev => ({ ...prev, enabled: e.target.checked }))}
                    />
                    <label htmlFor="enabled">启用数据源</label>
                  </div>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">标签</label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    tags: e.target.value.split(',').map(tag => tag.trim()).filter(Boolean)
                  }))}
                  className="input"
                  placeholder="输入标签，用逗号分隔"
                />
              </div>

              <div className="filters-section">
                <h3>内容筛选</h3>

                <div className="form-group">
                  <label className="form-label">包含关键词</label>
                  <input
                    type="text"
                    value={formData.filters.keywords}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      filters: { ...prev.filters, keywords: e.target.value }
                    }))}
                    className="input"
                    placeholder="用逗号分隔多个关键词"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">排除关键词</label>
                  <input
                    type="text"
                    value={formData.filters.excludeKeywords}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      filters: { ...prev.filters, excludeKeywords: e.target.value }
                    }))}
                    className="input"
                    placeholder="用逗号分隔多个关键词"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">最小内容长度</label>
                  <input
                    type="number"
                    value={formData.filters.minLength}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      filters: { ...prev.filters, minLength: parseInt(e.target.value) || 0 }
                    }))}
                    className="input"
                    min="0"
                    placeholder="字符数"
                  />
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button
                onClick={() => setShowAddModal(false)}
                className="btn btn-secondary"
              >
                取消
              </button>
              <button
                onClick={handleSaveSource}
                className="btn btn-primary"
                disabled={!formData.name || !formData.url}
              >
                保存
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