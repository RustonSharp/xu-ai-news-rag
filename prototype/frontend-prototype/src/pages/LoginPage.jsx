import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Navigate } from 'react-router-dom'
import { LogIn, Mail, Lock, UserPlus } from 'lucide-react'

const Login = () => {
  const { login, register, isAuthenticated } = useAuth()
  const [isLogin, setIsLogin] = useState(true)
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // If logged in, redirect to the homepage
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
    setError('')
    setSuccess('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    if (!formData.email || !formData.password) {
      setError('Please fill in all fields')
      setLoading(false)
      return
    }

    try {
      if (isLogin) {
        const result = await login(formData.email, formData.password)
        if (!result.success) {
          setError(result.message)
        }
      } else {
        const result = await register(formData.email, formData.password)
        if (result.success) {
          setSuccess(result.message)
          setIsLogin(true)
          setFormData({ email: '', password: '' })
        } else {
          setError(result.message)
        }
      }
    } catch (error) {
      setError('Operation failed, please try again later')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1 className="login-title">
            XU AI News RAG
          </h1>
          <p className="login-subtitle">
            Intelligent News Knowledge Base System
          </p>
        </div>

        <div className="login-tabs">
          <button
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(true)
              setError('')
              setSuccess('')
            }}
          >
            <LogIn size={16} />
            Login
          </button>
          <button
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => {
              setIsLogin(false)
              setError('')
              setSuccess('')
            }}
          >
            <UserPlus size={16} />
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label className="form-label">
              <Mail size={16} />
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="input"
              placeholder="Enter your email address"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              <Lock size={16} />
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="input"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {success && (
            <div className="success-message">
              {success}
            </div>
          )}

          <button
            type="submit"
            className="btn btn-primary btn-lg login-submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="spinner" />
                {isLogin ? 'Logging in...' : 'Registering...'}
              </>
            ) : (
              <>
                {isLogin ? <LogIn size={16} /> : <UserPlus size={16} />}
                {isLogin ? 'Login' : 'Register'}
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <p className="login-demo-note">
            💡 Demo Mode: When the backend service is not started, you can use any email and password for demonstration.
          </p>
        </div>
      </div>

      <style>{`
        .login-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, var(--bg) 0%, var(--panel) 100%);
          padding: 20px;
        }

        .login-card {
          width: 100%;
          max-width: 400px;
          background: var(--panel);
          border: 1px solid var(--border);
          border-radius: 16px;
          padding: 32px;
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }

        .login-header {
          text-align: center;
          margin-bottom: 32px;
        }

        .login-title {
          font-size: 24px;
          font-weight: 700;
          color: var(--primary);
          margin-bottom: 8px;
        }

        .login-subtitle {
          color: var(--muted);
          font-size: 14px;
        }

        .login-tabs {
          display: flex;
          background: var(--elev);
          border-radius: var(--radius);
          padding: 4px;
          margin-bottom: 24px;
        }

        .tab {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 10px 16px;
          border-radius: calc(var(--radius) - 2px);
          background: transparent;
          color: var(--muted);
          font-weight: 500;
          transition: all 0.2s ease;
          cursor: pointer;
        }

        .tab.active {
          background: var(--primary);
          color: white;
        }

        .login-form {
          margin-bottom: 24px;
        }

        .form-label {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          font-weight: 500;
          color: var(--text);
          font-size: 14px;
        }

        .login-submit {
          width: 100%;
          justify-content: center;
        }

        .error-message {
          background: rgba(239, 85, 82, 0.1);
          color: var(--danger);
          padding: 12px 16px;
          border-radius: var(--radius);
          margin-bottom: 16px;
          font-size: 14px;
          border: 1px solid rgba(239, 85, 82, 0.2);
        }

        .success-message {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success);
          padding: 12px 16px;
          border-radius: var(--radius);
          margin-bottom: 16px;
          font-size: 14px;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }

        .login-footer {
          text-align: center;
        }

        .login-demo-note {
          color: var(--muted);
          font-size: 12px;
          line-height: 1.5;
          background: var(--elev);
          padding: 12px;
          border-radius: var(--radius);
          border: 1px solid var(--border);
        }
      `}</style>
    </div>
  )
}

export default Login