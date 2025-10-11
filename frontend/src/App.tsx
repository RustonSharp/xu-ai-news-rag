import React, { Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, StyledEngineProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { Box, CircularProgress, Typography } from '@mui/material'
import { AuthProvider } from './contexts/AuthContext'
import { ThemeProvider as CustomThemeProvider } from './contexts/ThemeContext'
import { ToastProvider } from './components/Toast'
import ErrorBoundary from './components/ErrorBoundary'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import { muiTheme } from './theme/muiTheme'
import './App.css'

// 懒加载页面组件
const LoginPage = lazy(() => import('./pages/LoginPage'))
const KnowledgePage = lazy(() => import('./pages/KnowledgePage'))
const CollectionPage = lazy(() => import('./pages/SourcePage'))
const SearchPage = lazy(() => import('./pages/AssistantPage'))
const AnalyticsPage = lazy(() => import('./pages/AnalyticsPage'))
const UploadPage = lazy(() => import('./pages/UploadPage'))

// 页面加载组件
const PageLoader = () => (
    <Box
        sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            gap: 2,
        }}
    >
        <CircularProgress size={48} />
        <Typography variant="body1" color="text.secondary">
            正在加载页面...
        </Typography>
    </Box>
)

const App: React.FC = () => {
    return (
        <ErrorBoundary>
            <StyledEngineProvider injectFirst>
                <ThemeProvider theme={muiTheme}>
                    <CssBaseline />
                    <CustomThemeProvider>
                        <ToastProvider>
                            <AuthProvider>
                                <Router>
                                    <Routes>
                                        {/* 登录页面 */}
                                        <Route
                                            path="/login"
                                            element={
                                                <Suspense fallback={<PageLoader />}>
                                                    <LoginPage />
                                                </Suspense>
                                            }
                                        />

                                        {/* 受保护的页面 */}
                                        <Route path="/" element={
                                            <ProtectedRoute>
                                                <Layout>
                                                    <Navigate to="/knowledge" replace />
                                                </Layout>
                                            </ProtectedRoute>
                                        } />

                                        <Route
                                            path="/knowledge"
                                            element={
                                                <ProtectedRoute>
                                                    <Layout>
                                                        <Suspense fallback={<PageLoader />}>
                                                            <KnowledgePage />
                                                        </Suspense>
                                                    </Layout>
                                                </ProtectedRoute>
                                            }
                                        />

                                        <Route
                                            path="/collection"
                                            element={
                                                <ProtectedRoute>
                                                    <Layout>
                                                        <Suspense fallback={<PageLoader />}>
                                                            <CollectionPage />
                                                        </Suspense>
                                                    </Layout>
                                                </ProtectedRoute>
                                            }
                                        />

                                        <Route
                                            path="/search"
                                            element={
                                                <ProtectedRoute>
                                                    <Layout>
                                                        <Suspense fallback={<PageLoader />}>
                                                            <SearchPage />
                                                        </Suspense>
                                                    </Layout>
                                                </ProtectedRoute>
                                            }
                                        />

                                        <Route
                                            path="/analytics"
                                            element={
                                                <ProtectedRoute>
                                                    <Layout>
                                                        <Suspense fallback={<PageLoader />}>
                                                            <AnalyticsPage />
                                                        </Suspense>
                                                    </Layout>
                                                </ProtectedRoute>
                                            }
                                        />

                                        <Route
                                            path="/upload"
                                            element={
                                                <ProtectedRoute>
                                                    <Layout>
                                                        <Suspense fallback={<PageLoader />}>
                                                            <UploadPage />
                                                        </Suspense>
                                                    </Layout>
                                                </ProtectedRoute>
                                            }
                                        />

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
                        </ToastProvider>
                    </CustomThemeProvider>
                </ThemeProvider>
            </StyledEngineProvider>
        </ErrorBoundary>
    )
}

export default App
