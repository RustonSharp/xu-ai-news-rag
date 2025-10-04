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

// Navigation item type definition
interface NavItem {
  path: string
  label: string
  icon: LucideIcon
  description: string
}

// Layout Props type
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
      label: 'Knowledge Base',
      icon: Database,
      description: 'Manage documents and knowledge base content'
    },
    {
      path: '/upload',
      label: 'Data Import',
      icon: Upload,
      description: 'Upload documents to knowledge base'
    },
    {
      path: '/collection',
      label: 'Collection',
      icon: Rss,
      description: 'Configure RSS and web collection'
    },
    {
      path: '/search',
      label: 'Search',
      icon: Search,
      description: 'Intelligent search and Q&A'
    },
    {
      path: '/analytics',
      label: 'Analysis',
      icon: BarChart3,
      description: 'Data analysis and reports'
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
            title={`Current: ${theme === 'light' ? 'Light' : theme === 'dark' ? 'Dark' : 'System'} - Click to switch`}
          >
            {theme === 'light' && <Sun size={14} />}
            {theme === 'dark' && <Moon size={14} />}
            {theme === 'system' && <Monitor size={14} />}
          </button>

          <button
            onClick={handleLogout}
            className="btn btn-secondary btn-sm"
            title="Logout"
          >
            <LogOut size={14} />
            Logout
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