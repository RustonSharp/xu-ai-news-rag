import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider } from './contexts/ThemeContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import KnowledgePage from './pages/KnowledgePage'
import CollectionPage from './pages/CollectionPage'
import SearchPage from './pages/SearchPage'
import AnalyticsPage from './pages/AnalyticsPage'
import UploadPage from './pages/UploadPage'
import './App.css'

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
      <Router>
        <Routes>
          {/* 登录页面 */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* 受保护的页面 */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout>
                <Navigate to="/knowledge" replace />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/knowledge" element={
            <ProtectedRoute>
              <Layout>
                <KnowledgePage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/collection" element={
            <ProtectedRoute>
              <Layout>
                <CollectionPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/search" element={
            <ProtectedRoute>
              <Layout>
                <SearchPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/analytics" element={
            <ProtectedRoute>
              <Layout>
                <AnalyticsPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/upload" element={
            <ProtectedRoute>
              <Layout>
                <UploadPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          {/* 404页面 */}
          <Route path="*" element={
            <ProtectedRoute>
              <Layout>
                <div className="page-404">
                  <h1>404 - 页面未找到</h1>
                  <p>您访问的页面不存在</p>
                  <a href="/knowledge" className="btn btn-primary">返回首页</a>
                </div>
              </Layout>
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App