import React, { useState, useEffect } from 'react'
import { analyticsAPI } from '../api'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import {
  TrendingUp,
  TrendingDown,
  FileText,
  Users,
  Search,
  Download,
  RefreshCw,
  Eye,
  MessageSquare,
  Clock,
  Activity
} from 'lucide-react'

interface OverviewData {
  totalDocuments: number;
  documentGrowth: number;
  totalQueries: number;
  queryGrowth: number;
  activeUsers: number;
  userGrowth: number;
  avgResponseTime: number;
  responseTimeChange: number;
}

interface DocumentStat {
  date: string;
  documents: number;
  processed: number;
  uploads: number;
}

interface QueryStat {
  date: string;
  successful: number;
  failed: number;
}

interface UserActivity {
  hour: string;
  users: number;
}

interface DocumentType {
  name: string;
  value: number;
  color: string;
}

interface TopQuery {
  query: string;
  count: number;
  avgTime: number;
}

interface ResponseTimeDistribution {
  range: string;
  count: number;
}

interface AnalyticsApiResponse {
  overview: OverviewData;
  documentStats: DocumentStat[];
  queryStats: QueryStat[];
  userActivity: UserActivity[];
  documentTypes: DocumentType[];
  topQueries: TopQuery[];
  responseTimeDistribution: ResponseTimeDistribution[];
}

interface StatCardProps {
  title: string;
  value: number | string;
  change: number;
  icon: any;
  trend: 'up' | 'down';
}

const AnalyticsPage: React.FC = () => {
  const [timeRange, setTimeRange] = useState('7d')
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('overview')

  const [analyticsData, setAnalyticsData] = useState({
    overview: {
      totalDocuments: 0,
      documentGrowth: 0,
      totalQueries: 0,
      queryGrowth: 0,
      activeUsers: 0,
      userGrowth: 0,
      avgResponseTime: 0,
      responseTimeChange: 0
    } as OverviewData,
    documentStats: [] as DocumentStat[],
    queryStats: [] as QueryStat[],
    userActivity: [] as UserActivity[],
    documentTypes: [] as DocumentType[],
    topQueries: [] as TopQuery[],
    responseTimeDistribution: [] as ResponseTimeDistribution[]
  })

  useEffect(() => {
    loadAnalyticsData()
  }, [timeRange])

  const loadAnalyticsData = async () => {
    setLoading(true)
    try {
      // 调用分析数据API
      const response = await analyticsAPI.getOverview({
        period: timeRange as 'day' | 'week' | 'month' | 'year'
      })
      
      const data = response.data as unknown as AnalyticsApiResponse
      if (data) {
        setAnalyticsData({
          overview: data.overview || analyticsData.overview,
          documentStats: data.documentStats || analyticsData.documentStats,
          queryStats: data.queryStats || analyticsData.queryStats,
          userActivity: data.userActivity || analyticsData.userActivity,
          documentTypes: data.documentTypes || analyticsData.documentTypes,
          topQueries: data.topQueries || analyticsData.topQueries,
          responseTimeDistribution: data.responseTimeDistribution || analyticsData.responseTimeDistribution
        })
      }
    } catch (error) {
      console.error('获取分析数据失败:', error)
      // 如果API调用失败，保持使用现有的模拟数据
    } finally {
      setLoading(false)
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

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    })
  }

  const exportData = () => {
    // 模拟导出功能
    alert('数据导出功能开发中...')
  }

  const StatCard: React.FC<StatCardProps> = ({ title, value, change, icon: Icon, trend }) => (
    <div className="stat-card">
      <div className="stat-header">
        <div className="stat-icon">
          <Icon size={20} />
        </div>
        <div className="stat-trend">
          {trend === 'up' ? (
            <TrendingUp size={16} className="trend-up" />
          ) : (
            <TrendingDown size={16} className="trend-down" />
          )}
          <span className={`trend-value ${trend === 'up' ? 'positive' : 'negative'}`}>
            {Math.abs(change)}%
          </span>
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
          <p className="page-subtitle">系统使用情况和性能分析</p>
        </div>
        
        <div className="header-actions">
          <div className="time-range-selector">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="input"
            >
              <option value="1d">最近1天</option>
              <option value="7d">最近7天</option>
              <option value="30d">最近30天</option>
              <option value="90d">最近90天</option>
            </select>
          </div>
          
          <button
            onClick={loadAnalyticsData}
            disabled={loading}
            className="btn btn-secondary"
          >
            <RefreshCw size={16} className={loading ? 'spinning' : ''} />
            刷新
          </button>
          
          <button
            onClick={exportData}
            className="btn btn-primary"
          >
            <Download size={16} />
            导出报表
          </button>
        </div>
      </div>

      <div className="analytics-tabs">
        <button
          onClick={() => setActiveTab('overview')}
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
        >
          <Activity size={16} />
          概览
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
        >
          <FileText size={16} />
          文档分析
        </button>
        <button
          onClick={() => setActiveTab('queries')}
          className={`tab-btn ${activeTab === 'queries' ? 'active' : ''}`}
        >
          <Search size={16} />
          查询分析
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`tab-btn ${activeTab === 'users' ? 'active' : ''}`}
        >
          <Users size={16} />
          用户分析
        </button>
      </div>

      <div className="analytics-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {/* 关键指标卡片 */}
            <div className="stats-grid">
              <StatCard
                title="总文档数"
                value={formatNumber(analyticsData.overview.totalDocuments)}
                change={analyticsData.overview.documentGrowth}
                icon={FileText}
                trend="up"
              />
              <StatCard
                title="总查询数"
                value={formatNumber(analyticsData.overview.totalQueries)}
                change={analyticsData.overview.queryGrowth}
                icon={Search}
                trend="up"
              />
              <StatCard
                title="活跃用户"
                value={formatNumber(analyticsData.overview.activeUsers)}
                change={analyticsData.overview.userGrowth}
                icon={Users}
                trend="up"
              />
              <StatCard
                title="平均响应时间"
                value={`${analyticsData.overview.avgResponseTime}s`}
                change={analyticsData.overview.responseTimeChange}
                icon={Clock}
                trend="down"
              />
            </div>

            {/* 图表区域 */}
            <div className="charts-grid">
              <div className="chart-card">
                <div className="chart-header">
                  <h3>文档处理趋势</h3>
                  <div className="chart-legend">
                    <span className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#8884d8' }}></span>
                      新增文档
                    </span>
                    <span className="legend-item">
                      <span className="legend-color" style={{ backgroundColor: '#82ca9d' }}></span>
                      处理完成
                    </span>
                  </div>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analyticsData.documentStats}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate}
                        stroke="var(--muted)"
                      />
                      <YAxis stroke="var(--muted)" />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'var(--panel)',
                          border: '1px solid var(--border)',
                          borderRadius: 'var(--radius)'
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="documents" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        name="新增文档"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="processed" 
                        stroke="#82ca9d" 
                        strokeWidth={2}
                        name="处理完成"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="chart-card">
                <div className="chart-header">
                  <h3>查询成功率</h3>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analyticsData.queryStats}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate}
                        stroke="var(--muted)"
                      />
                      <YAxis stroke="var(--muted)" />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'var(--panel)',
                          border: '1px solid var(--border)',
                          borderRadius: 'var(--radius)'
                        }}
                      />
                      <Bar dataKey="successful" fill="#82ca9d" name="成功" />
                      <Bar dataKey="failed" fill="#ff7300" name="失败" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="documents-tab">
            <div className="charts-grid">
              <div className="chart-card">
                <div className="chart-header">
                  <h3>文档类型分布</h3>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={analyticsData.documentTypes}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {analyticsData.documentTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'var(--panel)',
                          border: '1px solid var(--border)',
                          borderRadius: 'var(--radius)'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="chart-card">
                <div className="chart-header">
                  <h3>文档上传趋势</h3>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analyticsData.documentStats}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis 
                        dataKey="date" 
                        tickFormatter={formatDate}
                        stroke="var(--muted)"
                      />
                      <YAxis stroke="var(--muted)" />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'var(--panel)',
                          border: '1px solid var(--border)',
                          borderRadius: 'var(--radius)'
                        }}
                      />
                      <Bar dataKey="uploads" fill="#8884d8" name="上传数量" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'queries' && (
          <div className="queries-tab">
            <div className="charts-grid">
              <div className="chart-card full-width">
                <div className="chart-header">
                  <h3>热门查询</h3>
                </div>
                <div className="table-container">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>查询内容</th>
                        <th>查询次数</th>
                        <th>平均响应时间</th>
                        <th>操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyticsData.topQueries.map((query, index) => (
                        <tr key={index}>
                          <td className="query-text">{query.query}</td>
                          <td>
                            <span className="count-badge">{query.count}</span>
                          </td>
                          <td>
                            <span className={`time-badge ${
                              query.avgTime < 1 ? 'fast' : 
                              query.avgTime < 2 ? 'medium' : 'slow'
                            }`}>
                              {query.avgTime}s
                            </span>
                          </td>
                          <td>
                            <button className="action-btn" title="查看详情">
                              <Eye size={14} />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="chart-card">
                <div className="chart-header">
                  <h3>响应时间分布</h3>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={analyticsData.responseTimeDistribution}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="range" stroke="var(--muted)" />
                      <YAxis stroke="var(--muted)" />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'var(--panel)',
                          border: '1px solid var(--border)',
                          borderRadius: 'var(--radius)'
                        }}
                      />
                      <Bar dataKey="count" fill="#8884d8" name="查询数量" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div className="users-tab">
            <div className="charts-grid">
              <div className="chart-card">
                <div className="chart-header">
                  <h3>用户活跃度（24小时）</h3>
                </div>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={analyticsData.userActivity}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="hour" stroke="var(--muted)" />
                      <YAxis stroke="var(--muted)" />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: 'var(--panel)',
                          border: '1px solid var(--border)',
                          borderRadius: 'var(--radius)'
                        }}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="users" 
                        stroke="#8884d8" 
                        strokeWidth={2}
                        name="活跃用户数"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="chart-card">
                <div className="chart-header">
                  <h3>用户行为统计</h3>
                </div>
                <div className="user-stats">
                  <div className="user-stat-item">
                    <div className="stat-icon">
                      <Search size={24} />
                    </div>
                    <div className="stat-info">
                      <h4>平均查询次数</h4>
                      <p>24.8 次/用户</p>
                    </div>
                  </div>
                  
                  <div className="user-stat-item">
                    <div className="stat-icon">
                      <Clock size={24} />
                    </div>
                    <div className="stat-info">
                      <h4>平均会话时长</h4>
                      <p>12.5 分钟</p>
                    </div>
                  </div>
                  
                  <div className="user-stat-item">
                    <div className="stat-icon">
                      <MessageSquare size={24} />
                    </div>
                    <div className="stat-info">
                      <h4>满意度评分</h4>
                      <p>4.6 / 5.0</p>
                    </div>
                  </div>
                  
                  <div className="user-stat-item">
                    <div className="stat-icon">
                      <TrendingUp size={24} />
                    </div>
                    <div className="stat-info">
                      <h4>用户留存率</h4>
                      <p>78.3%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
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