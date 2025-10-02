import React, { useState, useRef } from 'react'
import { documentAPI } from '../api'
import {
  Upload,
  FileText,
  File,
  X,
  Check,
  AlertCircle,
  Trash2,
  Tag,
  Folder
} from 'lucide-react'

// 类型定义
interface UploadFile {
  id: string
  file: File
  name: string
  size: number
  type: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
  uploadedId?: string
}

const UploadPage: React.FC = () => {
  const [files, setFiles] = useState<UploadFile[]>([])
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [tags, setTags] = useState('')
  const [source, setSource] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 支持的文件类型
  const supportedTypes = {
    'application/pdf': { icon: FileText, label: 'PDF', color: '#ef4444' },
    'application/vnd.ms-excel': { icon: File, label: 'Excel', color: '#10b981' },
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': { icon: File, label: 'Excel', color: '#10b981' },
    'text/csv': { icon: File, label: 'CSV', color: '#f59e0b' },
    'text/markdown': { icon: FileText, label: 'Markdown', color: '#6366f1' },
    'text/plain': { icon: FileText, label: 'Text', color: '#6b7280' },
    'text/html': { icon: FileText, label: 'HTML', color: '#f97316' }
  }

  // 处理文件拖拽
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  // 处理文件放置
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }

  // 处理文件选择
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(e.target.files || [])
    addFiles(selectedFiles)
  }

  // 添加文件到列表
  const addFiles = (newFiles: File[]) => {
    const processedFiles = newFiles.map((file: File): UploadFile => ({
      id: (Date.now() + Math.random()).toString(),
      file,
      name: file.name,
      size: file.size,
      type: file.type,
      status: 'pending', // pending, uploading, success, error
      progress: 0
    }))

    setFiles(prev => [...prev, ...processedFiles])
  }

  // 移除文件
  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }

  // 清空所有文件
  const clearAllFiles = () => {
    setFiles([])
  }

  // 格式化文件大小
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 获取文件图标
  const getFileIcon = (fileType: string) => {
    const typeInfo = (supportedTypes as any)[fileType]
    if (typeInfo) {
      const IconComponent = typeInfo.icon
      return <IconComponent size={20} style={{ color: typeInfo.color }} />
    }
    return <File size={20} style={{ color: '#6b7280' }} />
  }

  // 获取文件类型标签
  const getFileTypeLabel = (fileType: string) => {
    const typeInfo = (supportedTypes as any)[fileType]
    return typeInfo ? typeInfo.label : '未知类型'
  }

  // 真实文件上传过程
  const uploadFiles = async () => {
    setUploading(true)

    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (file.status !== 'pending') continue

      // 更新状态为上传中
      setFiles(prev => prev.map(f =>
        f.id === file.id ? { ...f, status: 'uploading', progress: 0 } : f
      ))

      try {
        // 检查是否为Excel文件
        const isExcelFile = file.type === 'application/vnd.ms-excel' ||
          file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        let response
        if (isExcelFile) {
          // 使用Excel上传API
          response = await documentAPI.uploadExcel(file.file)

          // Excel文件上传成功后立即设置为100%进度
          setFiles(prev => prev.map(f =>
            f.id === file.id ? { ...f, progress: 100 } : f
          ))
        } else {
          // 创建FormData
          const formData = new FormData()
          formData.append('file', file.file)
          if (tags) formData.append('tags', tags)
          if (source) formData.append('source', source)

          // 调用上传API
          response = await documentAPI.uploadDocument(formData, (progressEvent: ProgressEvent) => {
            const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
            setFiles(prev => prev.map(f =>
              f.id === file.id ? { ...f, progress } : f
            ))
          })
        }

        // 上传成功
        setFiles(prev => prev.map(f =>
          f.id === file.id ? {
            ...f,
            status: 'success',
            progress: 100,
            uploadedId: 'id' in response.data ? response.data.id : 'success'
          } : f
        ))
      } catch (error: any) {
        console.error('上传失败:', error)
        setFiles(prev => prev.map(f =>
          f.id === file.id ? {
            ...f,
            status: 'error',
            error: error.response?.data?.message || error.response?.data?.error || '上传失败，请重试'
          } : f
        ))
      }
    }

    setUploading(false)
  }

  // 处理上传
  const handleUpload = () => {
    if (files.length === 0) {
      alert('请先选择要上传的文件')
      return
    }

    uploadFiles()
  }

  // 统计信息
  const stats = {
    total: files.length,
    pending: files.filter(f => f.status === 'pending').length,
    uploading: files.filter(f => f.status === 'uploading').length,
    success: files.filter(f => f.status === 'success').length,
    error: files.filter(f => f.status === 'error').length
  }

  return (
    <div className="upload-page">
      <div className="page-header">
        <h1 className="page-title">
          <Upload size={24} />
          数据导入
        </h1>
        <p className="page-subtitle">
          支持上传 PDF、Excel、CSV、Markdown、HTML 等多种格式的文档到知识库
        </p>
      </div>

      <div className="upload-container">
        {/* 文件拖拽区域 */}
        <div
          className={`upload-dropzone ${dragActive ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="dropzone-content">
            <Upload size={48} className="dropzone-icon" />
            <h3>拖拽文件到此处或点击选择</h3>
            <p>支持 PDF、Excel、CSV、Markdown、HTML、TXT 格式</p>
            <p className="file-limit">单个文件最大 50MB，最多同时上传 20 个文件</p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.xlsx,.xls,.csv,.md,.html,.txt"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
        </div>

        {/* 上传配置 */}
        <div className="upload-config">
          <div className="config-row">
            <div className="form-group">
              <label className="form-label">
                <Tag size={16} />
                标签（可选）
              </label>
              <input
                type="text"
                value={tags}
                onChange={(e) => setTags(e.target.value)}
                placeholder="输入标签，用逗号分隔"
                className="input"
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                <Folder size={16} />
                数据源（可选）
              </label>
              <input
                type="text"
                value={source}
                onChange={(e) => setSource(e.target.value)}
                placeholder="输入数据源名称"
                className="input"
              />
            </div>
          </div>
        </div>

        {/* 文件列表 */}
        {files.length > 0 && (
          <div className="files-section">
            <div className="files-header">
              <h3>待上传文件 ({files.length})</h3>
              <div className="files-actions">
                <button
                  onClick={clearAllFiles}
                  className="btn btn-secondary btn-sm"
                  disabled={uploading}
                >
                  <Trash2 size={14} />
                  清空
                </button>
                <button
                  onClick={handleUpload}
                  className="btn btn-primary btn-sm"
                  disabled={uploading || stats.pending === 0}
                >
                  {uploading ? '上传中...' : `上传 ${stats.pending} 个文件`}
                </button>
              </div>
            </div>

            {/* 上传统计 */}
            {(stats.uploading > 0 || stats.success > 0 || stats.error > 0) && (
              <div className="upload-stats">
                <div className="stat-item">
                  <span className="stat-label">待上传:</span>
                  <span className="stat-value">{stats.pending}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">上传中:</span>
                  <span className="stat-value uploading">{stats.uploading}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">已完成:</span>
                  <span className="stat-value success">{stats.success}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">失败:</span>
                  <span className="stat-value error">{stats.error}</span>
                </div>
              </div>
            )}

            <div className="files-list">
              {files.map((file) => (
                <div key={file.id} className={`file-item ${file.status}`}>
                  <div className="file-info">
                    <div className="file-icon">
                      {getFileIcon(file.type)}
                    </div>
                    <div className="file-details">
                      <div className="file-name">{file.name}</div>
                      <div className="file-meta">
                        <span className="file-size">{formatFileSize(file.size)}</span>
                        <span className="file-type">{getFileTypeLabel(file.type)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="file-status">
                    {file.status === 'pending' && (
                      <span className="status-badge pending">待上传</span>
                    )}
                    {file.status === 'uploading' && (
                      <div className="upload-progress">
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{ width: `${file.progress}%` }}
                          />
                        </div>
                        <span className="progress-text">{file.progress}%</span>
                      </div>
                    )}
                    {file.status === 'success' && (
                      <span className="status-badge success">
                        <Check size={14} />
                        上传成功
                      </span>
                    )}
                    {file.status === 'error' && (
                      <span className="status-badge error">
                        <AlertCircle size={14} />
                        {file.error}
                      </span>
                    )}
                  </div>

                  <div className="file-actions">
                    {file.status === 'pending' && (
                      <button
                        onClick={() => removeFile(file.id)}
                        className="btn-icon"
                        title="移除"
                      >
                        <X size={16} />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 使用说明 */}
        <div className="upload-help">
          <h4>使用说明</h4>
          <ul>
            <li><strong>支持格式：</strong>PDF、Excel (.xlsx/.xls)、CSV、Markdown (.md)、HTML、TXT</li>
            <li><strong>文件大小：</strong>单个文件最大 50MB</li>
            <li><strong>批量上传：</strong>最多同时上传 20 个文件</li>
            <li><strong>标签功能：</strong>为上传的文档添加标签，便于后续分类和检索</li>
            <li><strong>数据源：</strong>指定文档来源，有助于数据管理和溯源</li>
            <li><strong>Excel文件：</strong>Excel文件将直接导入为知识库文档，支持批量导入。Excel文件应包含以下列：title（标题）、link（链接）、description（描述）、pub_date（发布日期）、author（作者）、tags（标签）、rss_source_id（RSS源ID）、crawled_at（爬取时间）。</li>
          </ul>
        </div>
      </div>

      <style>{`
        .upload-page {
          max-width: 1000px;
          margin: 0 auto;
          padding: 24px;
        }

        .page-header {
          margin-bottom: 32px;
        }

        .page-title {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 28px;
          font-weight: 600;
          color: var(--text);
          margin-bottom: 8px;
        }

        .page-subtitle {
          color: var(--muted);
          font-size: 16px;
          line-height: 1.5;
        }

        .upload-container {
          display: flex;
          flex-direction: column;
          gap: 24px;
        }

        .upload-dropzone {
          border: 2px dashed var(--border);
          border-radius: var(--radius-lg);
          padding: 48px 24px;
          text-align: center;
          cursor: pointer;
          transition: var(--transition);
          background: var(--bg-secondary);
        }

        .upload-dropzone:hover,
        .upload-dropzone.active {
          border-color: var(--primary);
          background: var(--primary-light);
        }

        .dropzone-content {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
        }

        .dropzone-icon {
          color: var(--muted);
        }

        .upload-dropzone.active .dropzone-icon {
          color: var(--primary);
        }

        .dropzone-content h3 {
          font-size: 18px;
          font-weight: 600;
          color: var(--text);
          margin: 0;
        }

        .dropzone-content p {
          color: var(--muted);
          margin: 0;
        }

        .file-limit {
          font-size: 14px;
          color: var(--muted-light) !important;
        }

        .upload-config {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 24px;
        }

        .config-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .form-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          color: var(--text);
          font-size: 14px;
        }

        .input {
          padding: 12px 16px;
          border: 1px solid var(--border);
          border-radius: var(--radius);
          background: var(--bg);
          color: var(--text);
          font-size: 14px;
          transition: var(--transition);
        }

        .input:focus {
          outline: none;
          border-color: var(--primary);
          box-shadow: 0 0 0 3px var(--primary-light);
        }

        .files-section {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          overflow: hidden;
        }

        .files-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 24px;
          border-bottom: 1px solid var(--border);
          background: var(--bg-secondary);
        }

        .files-header h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
        }

        .files-actions {
          display: flex;
          gap: 12px;
        }

        .btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          border: none;
          border-radius: var(--radius);
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: var(--transition);
          text-decoration: none;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 13px;
        }

        .btn-primary {
          background: var(--primary);
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: var(--primary-dark);
        }

        .btn-secondary {
          background: var(--bg);
          color: var(--text);
          border: 1px solid var(--border);
        }

        .btn-secondary:hover:not(:disabled) {
          background: var(--bg-secondary);
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .upload-stats {
          display: flex;
          gap: 24px;
          padding: 16px 24px;
          background: var(--elev);
          border-bottom: 1px solid var(--border);
        }

        .stat-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
        }

        .stat-label {
          color: var(--muted);
        }

        .stat-value {
          font-weight: 600;
          color: var(--text);
        }

        .stat-value.uploading {
          color: var(--info);
        }

        .stat-value.success {
          color: var(--success);
        }

        .stat-value.error {
          color: var(--danger);
        }

        .files-list {
          max-height: 400px;
          overflow-y: auto;
        }

        .file-item {
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 16px 24px;
          border-bottom: 1px solid var(--border-light);
          transition: var(--transition);
        }

        .file-item:last-child {
          border-bottom: none;
        }

        .file-item:hover {
          background: var(--bg-secondary);
        }

        .file-info {
          display: flex;
          align-items: center;
          gap: 12px;
          flex: 1;
        }

        .file-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 40px;
          height: 40px;
          border-radius: var(--radius);
          background: var(--bg-secondary);
        }

        .file-details {
          flex: 1;
        }

        .file-name {
          font-weight: 500;
          color: var(--text);
          margin-bottom: 4px;
        }

        .file-meta {
          display: flex;
          gap: 12px;
          font-size: 13px;
          color: var(--muted);
        }

        .file-status {
          display: flex;
          align-items: center;
          min-width: 120px;
        }

        .status-badge {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 4px 8px;
          border-radius: var(--radius-sm);
          font-size: 12px;
          font-weight: 500;
        }

        .status-badge.pending {
          background: var(--elev);
          color: var(--muted);
        }

        .status-badge.success {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success);
        }

        .status-badge.error {
          background: rgba(239, 68, 68, 0.1);
          color: var(--danger);
        }

        .upload-progress {
          display: flex;
          align-items: center;
          gap: 8px;
          width: 100%;
        }

        .progress-bar {
          flex: 1;
          height: 6px;
          background: var(--elev);
          border-radius: 3px;
          overflow: hidden;
        }

        .progress-fill {
          height: 100%;
          background: var(--primary);
          transition: width 0.3s ease;
        }

        .progress-text {
          font-size: 12px;
          font-weight: 500;
          color: var(--primary);
          min-width: 35px;
        }

        .file-actions {
          display: flex;
          gap: 8px;
        }

        .btn-icon {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 32px;
          height: 32px;
          border: none;
          border-radius: var(--radius);
          background: transparent;
          color: var(--muted);
          cursor: pointer;
          transition: var(--transition);
        }

        .btn-icon:hover {
          background: var(--elev);
          color: var(--text);
        }

        .upload-help {
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 24px;
        }

        .upload-help h4 {
          margin: 0 0 16px 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--text);
        }

        .upload-help ul {
          margin: 0;
          padding-left: 20px;
          color: var(--text-light);
          line-height: 1.6;
        }

        .upload-help li {
          margin-bottom: 8px;
        }

        .upload-help strong {
          color: var(--text);
        }

        @media (max-width: 768px) {
          .config-row {
            grid-template-columns: 1fr;
          }
          
          .files-header {
            flex-direction: column;
            gap: 16px;
            align-items: stretch;
          }
          
          .upload-stats {
            flex-wrap: wrap;
            gap: 12px;
          }
        }
      `}</style>
    </div>
  )
}

export default UploadPage