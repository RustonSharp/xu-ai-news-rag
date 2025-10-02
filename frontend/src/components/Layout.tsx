import React, { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import {
  Database,
  Upload,
  Rss,
  Search,
  BarChart3,
  LogOut,
  User,
  Sun,
  Moon,
  Monitor,
  LucideIcon
} from 'lucide-react'

// 导航项类型定义
interface NavItem {
  path: string
  label: string
  icon: LucideIcon
  description: string
}

// Layout Props 类型
interface LayoutProps {
  children: ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth()
  const { theme, toggleTheme, isDark } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = (): void => {
    logout()
    navigate('/login')
  }

  const navItems: NavItem[] = [
    {
      path: '/knowledge',
      label: '知识库',
      icon: Database,
      description: '管理文档和知识库内容'
    },
    {
      path: '/upload',
      label: '数据导入',
      icon: Upload,
      description: '上传文档到知识库'
    },
    {
      path: '/collection',
      label: '采集',
      icon: Rss,
      description: '配置RSS和网页采集'
    },
    {
      path: '/search',
      label: '检索',
      icon: Search,
      description: '智能搜索和问答'
    },
    {
      path: '/analytics',
      label: '分析',
      icon: BarChart3,
      description: '数据分析和报表'
    }
  ]

  return (
    <div className="app">
      <nav className="nav">
        <div className="nav-brand">
          <Link to="/">
            XU AI News RAG
          </Link>
        </div>

        <div className="nav-links">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
                title={item.description}
              >
                <Icon size={16} />
                {item.label}
              </Link>
            )
          })}
        </div>

        <div className="nav-user">
          <div className="user-info">
            <User size={16} />
            <span className="user-email">{user?.email}</span>
          </div>
          
          <button
            onClick={toggleTheme}
            className="btn btn-secondary btn-sm theme-toggle"
            title={`当前: ${theme === 'light' ? '浅色' : theme === 'dark' ? '深色' : '跟随系统'} - 点击切换`}
          >
            {theme === 'light' && <Sun size={14} />}
            {theme === 'dark' && <Moon size={14} />}
            {theme === 'system' && <Monitor size={14} />}
          </button>
          
          <button
            onClick={handleLogout}
            className="btn btn-secondary btn-sm"
            title="退出登录"
          >
            <LogOut size={14} />
            退出
          </button>
        </div>
      </nav>

      <main className="main">
        {children}
      </main>

      <style>{`
        .nav {
          display: flex;
          align-items: center;
          gap: 24px;
          padding: 16px 24px;
          background: var(--bg-secondary);
          backdrop-filter: blur(10px);
          border-bottom: 1px solid var(--border);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .nav-brand {
          font-size: 18px;
          font-weight: 600;
          color: var(--primary);
        }

        .nav-brand a {
          color: inherit;
          text-decoration: none;
        }

        .nav-links {
          display: flex;
          gap: 20px;
          flex: 1;
          margin-left: 40px;
        }

        .nav-link {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 16px;
          border-radius: var(--radius);
          color: var(--muted);
          transition: all 0.2s ease;
          font-weight: 500;
          text-decoration: none;
        }

        .nav-link:hover {
          color: var(--text);
          background: var(--elev);
        }

        .nav-link.active {
          color: var(--primary);
          background: rgba(91, 157, 255, 0.1);
        }

        .nav-user {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-left: auto;
        }

        .user-info {
          display: flex;
          align-items: center;
          gap: 8px;
          color: var(--muted);
          font-size: 14px;
        }

        .user-email {
          max-width: 150px;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        @media (max-width: 768px) {
          .nav {
            padding: 12px 16px;
            gap: 16px;
            flex-wrap: wrap;
          }

          .nav-links {
            gap: 12px;
            margin-left: 0;
            order: 3;
            width: 100%;
            justify-content: center;
          }

          .nav-link {
            padding: 6px 12px;
            font-size: 14px;
          }

          .user-info {
            display: none;
          }
        }

        @media (max-width: 480px) {
          .nav-links {
            gap: 8px;
          }

          .nav-link {
            padding: 6px 8px;
            font-size: 12px;
          }

          .nav-link span {
            display: none;
          }
        }
      `}</style>
    </div>
  )
}

export default Layout