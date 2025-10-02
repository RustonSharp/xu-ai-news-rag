import React, { useState, useEffect } from 'react'
import { documentAPI } from '../api'
import {
  FileText,
  RefreshCw
} from 'lucide-react'

interface StatCardProps {
  title: string;
  value: number | string;
  icon: any;
}

interface ClusterItem {
  id: number;
  percentage: number;
  keyword: string;
}

const AnalyticsPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [totalDocuments, setTotalDocuments] = useState(0)
  const [clusters, setClusters] = useState<ClusterItem[]>([])
  const [clusterLoading, setClusterLoading] = useState(false)

  useEffect(() => {
    loadData()
    // 默认获取最新一次聚类分析结果
    loadLatestClusters()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      // 获取文档总数（使用分页接口仅获取总数）
      const docResp = await documentAPI.getDocumentsPage({ page: 1, size: 1 })
      const total = (docResp.data as any)?.total ?? 0
      setTotalDocuments(total)
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadClusters = async () => {
    setClusterLoading(true)
    try {
      const clusterResp = await documentAPI.getClusterAnalysis()
      const clusterData = (clusterResp.data as any)?.clusters ?? []
      setClusters(clusterData)
    } catch (error) {
      console.error('加载聚类数据失败:', error)
    } finally {
      setClusterLoading(false)
    }
  }

  const loadLatestClusters = async () => {
    try {
      const resp = await documentAPI.getLatestClusterAnalysis()
      const data = (resp.data as any)?.clusters ?? []
      setClusters(data)
    } catch (error) {
      console.error('加载最新聚类数据失败:', error)
    }
  }

  const formatNumber = (num: number): string => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  // 已移除未使用的辅助函数，保持文件整洁

  const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon }) => (
    <div className="stat-card">
      <div className="stat-header">
        <div className="stat-icon">
          <Icon size={20} />
        </div>
      </div>

      <div className="stat-content">
        <h3 className="stat-value">{typeof value === 'number' ? formatNumber(value) : value}</h3>
        <p className="stat-title">{title}</p>
      </div>
    </div>
  )

  return (
    <div className="analytics-page">
      <div className="page-header">
        <div>
          <h1 className="page-title">数据分析</h1>
          <p className="page-subtitle">文档统计与聚类分析</p>
        </div>

        <div className="header-actions">
          <button
            onClick={loadClusters}
            disabled={clusterLoading}
            className="btn btn-primary"
          >
            <RefreshCw size={16} className={clusterLoading ? 'spinning' : ''} />
            聚类分析
          </button>
          <button
            onClick={loadData}
            disabled={loading}
            className="btn btn-secondary"
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            刷新
          </button>
        </div>
      </div>

      {/* 移除多余的标签，仅展示必需信息 */}

      <div className="analytics-content">
        <div className="overview-tab">
          <div className="stats-grid">
            <StatCard
              title="总文档数"
              value={formatNumber(totalDocuments)}
              icon={FileText}
            />
          </div>

          <div className="charts-grid">
            <div className="chart-card full-width">
              <div className="chart-header">
                <h3>聚类分析（Top 10）</h3>
              </div>
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>聚类ID</th>
                      <th>代表关键词</th>
                      <th>占比</th>
                    </tr>
                  </thead>
                  <tbody>
                    {clusters.map((c) => (
                      <tr key={c.id}>
                        <td>{c.id}</td>
                        <td className="query-text">{c.keyword || '-'}</td>
                        <td><span className="count-badge">{(c.percentage || 0).toFixed(2)}%</span></td>
                      </tr>
                    ))}
                    {clusters.length === 0 && (
                      <tr>
                        <td colSpan={3} style={{ color: 'var(--muted)' }}>暂无聚类数据</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .analytics-page {
          max-width: 1200px;
          margin: 0 auto;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 24px;
        }

        .header-actions {
          display: flex;
          gap: 12px;
          align-items: center;
        }

        .time-range-selector select {
          min-width: 120px;
        }

        .analytics-tabs {
          display: flex;
          gap: 4px;
          background: var(--elev);
          border-radius: var(--radius);
          padding: 4px;
          margin-bottom: 24px;
        }

        .tab-btn {
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
        }

        .tab-btn:hover {
          color: var(--text);
        }

        .tab-btn.active {
          background: var(--bg);
          color: var(--primary);
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 24px;
        }

        .stat-card {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 20px;
          transition: all 0.2s ease;
        }

        .stat-card:hover {
          border-color: var(--primary);
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .stat-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .stat-icon {
          width: 40px;
          height: 40px;
          background: rgba(91, 157, 255, 0.1);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--primary);
        }

        .stat-trend {
          display: flex;
          align-items: center;
          gap: 4px;
        }

        .trend-up {
          color: var(--success);
        }

        .trend-down {
          color: var(--danger);
        }

        .trend-value.positive {
          color: var(--success);
        }

        .trend-value.negative {
          color: var(--danger);
        }

        .stat-value {
          font-size: 28px;
          font-weight: 700;
          color: var(--text);
          margin: 0 0 4px;
        }

        .stat-title {
          color: var(--muted);
          margin: 0;
          font-size: 14px;
        }

        .charts-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 20px;
        }

        .chart-card {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 20px;
        }

        .chart-card.full-width {
          grid-column: 1 / -1;
        }

        .chart-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .chart-header h3 {
          margin: 0;
          color: var(--text);
          font-size: 16px;
        }

        .chart-legend {
          display: flex;
          gap: 16px;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: var(--muted);
        }

        .legend-color {
          width: 12px;
          height: 12px;
          border-radius: 2px;
        }

        .chart-container {
          width: 100%;
          height: 300px;
        }

        .table-container {
          overflow-x: auto;
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
        }

        .data-table th,
        .data-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid var(--border);
        }

        .data-table th {
          background: var(--elev);
          color: var(--text);
          font-weight: 600;
          font-size: 14px;
        }

        .data-table td {
          color: var(--muted);
          font-size: 14px;
        }

        .query-text {
          max-width: 300px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          color: var(--text) !important;
        }

        .count-badge {
          background: rgba(91, 157, 255, 0.1);
          color: var(--primary);
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .time-badge {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .time-badge.fast {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success);
        }

        .time-badge.medium {
          background: rgba(245, 158, 11, 0.1);
          color: var(--warning);
        }

        .time-badge.slow {
          background: rgba(239, 68, 68, 0.1);
          color: var(--danger);
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

        .user-stats {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .user-stat-item {
          display: flex;
          gap: 12px;
          align-items: center;
          padding: 16px;
          background: var(--elev);
          border-radius: var(--radius);
        }

        .user-stat-item .stat-icon {
          width: 48px;
          height: 48px;
          background: rgba(91, 157, 255, 0.1);
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--primary);
        }

        .user-stat-item .stat-info h4 {
          margin: 0 0 4px;
          font-size: 14px;
          color: var(--text);
        }

        .user-stat-item .stat-info p {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: var(--primary);
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

          .header-actions {
            width: 100%;
            justify-content: space-between;
          }

          .analytics-tabs {
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
          }

          .analytics-tabs::-webkit-scrollbar {
            display: none;
          }

          .stats-grid {
            grid-template-columns: 1fr;
          }

          .charts-grid {
            grid-template-columns: 1fr;
          }

          .user-stats {
            grid-template-columns: 1fr;
          }

          .chart-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
          }

          .chart-legend {
            flex-wrap: wrap;
          }
        }
      `}</style>
    </div>
  )
}

export default AnalyticsPage