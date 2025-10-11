import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Button, Box, Typography, Paper, Alert } from '@mui/material'
import { Refresh, BugReport } from '@mui/icons-material'

interface Props {
    children: ReactNode
    fallback?: ReactNode
    onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface State {
    hasError: boolean
    error: Error | null
    errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props)
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        }
    }

    static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null,
        }
    }

    componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        this.setState({
            error,
            errorInfo,
        })

        // Log error to console in development
        if (process.env.NODE_ENV === 'development') {
            console.error('ErrorBoundary caught an error:', error, errorInfo)
        }

        // Call custom error handler if provided
        if (this.props.onError) {
            this.props.onError(error, errorInfo)
        }

        // In production, you might want to send error to a logging service
        // Example: errorReportingService.captureException(error, { extra: errorInfo })
    }

    handleRetry = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null,
        })
    }

    handleReload = () => {
        window.location.reload()
    }

    render() {
        if (this.state.hasError) {
            // Custom fallback UI
            if (this.props.fallback) {
                return this.props.fallback
            }

            // Default error UI
            return (
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minHeight: '100vh',
                        padding: 3,
                        backgroundColor: 'background.default',
                    }}
                >
                    <Paper
                        elevation={3}
                        sx={{
                            padding: 4,
                            maxWidth: 600,
                            width: '100%',
                            textAlign: 'center',
                        }}
                    >
                        <Box sx={{ mb: 3 }}>
                            <BugReport
                                sx={{
                                    fontSize: 64,
                                    color: 'error.main',
                                    mb: 2,
                                }}
                            />
                            <Typography variant="h4" component="h1" gutterBottom>
                                出错了
                            </Typography>
                            <Typography variant="body1" color="text.secondary" paragraph>
                                很抱歉，应用程序遇到了一个意外错误。我们已经记录了这个问题，并会尽快修复。
                            </Typography>
                        </Box>

                        {process.env.NODE_ENV === 'development' && this.state.error && (
                            <Alert severity="error" sx={{ mb: 3, textAlign: 'left' }}>
                                <Typography variant="subtitle2" gutterBottom>
                                    错误详情（开发模式）:
                                </Typography>
                                <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem' }}>
                                    {this.state.error.toString()}
                                </Typography>
                                {this.state.errorInfo && (
                                    <Typography variant="body2" component="pre" sx={{ fontSize: '0.75rem', mt: 1 }}>
                                        {this.state.errorInfo.componentStack}
                                    </Typography>
                                )}
                            </Alert>
                        )}

                        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <Button
                                variant="contained"
                                startIcon={<Refresh />}
                                onClick={this.handleRetry}
                                sx={{ minWidth: 120 }}
                            >
                                重试
                            </Button>
                            <Button
                                variant="outlined"
                                onClick={this.handleReload}
                                sx={{ minWidth: 120 }}
                            >
                                刷新页面
                            </Button>
                        </Box>

                        <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
                            如果问题持续存在，请联系技术支持。
                        </Typography>
                    </Paper>
                </Box>
            )
        }

        return this.props.children
    }
}

export default ErrorBoundary
