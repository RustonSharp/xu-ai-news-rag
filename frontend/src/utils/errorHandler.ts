/**
 * 统一错误处理工具
 */

export class AppError extends Error {
    constructor(
        message: string,
        public code?: string,
        public statusCode?: number,
        public details?: any
    ) {
        super(message)
        this.name = 'AppError'
    }
}

export interface ErrorResponse {
    message: string
    code?: string
    statusCode?: number
    details?: any
}

/**
 * 处理API错误
 */
export const handleAPIError = (error: any): AppError => {
    if (error.response) {
        // 服务器响应错误
        const { status, data } = error.response
        const message = data?.message || data?.error || `请求失败 (${status})`
        const code = data?.code || `HTTP_${status}`

        return new AppError(message, code, status, data)
    } else if (error.request) {
        // 网络错误
        return new AppError(
            '网络连接失败，请检查网络连接',
            'NETWORK_ERROR',
            0,
            { originalError: error.message }
        )
    } else {
        // 其他错误
        return new AppError(
            error.message || '未知错误',
            'UNKNOWN_ERROR',
            undefined,
            { originalError: error }
        )
    }
}

/**
 * 处理异步操作错误
 */
export const handleAsyncError = async <T>(
    asyncFn: () => Promise<T>,
    errorMessage?: string
): Promise<T> => {
    try {
        return await asyncFn()
    } catch (error) {
        if (error instanceof AppError) {
            throw error
        }

        const appError = handleAPIError(error)
        if (errorMessage) {
            appError.message = errorMessage
        }

        throw appError
    }
}

/**
 * 错误日志记录
 */
export const logError = (error: Error, context?: string) => {
    const errorInfo = {
        message: error.message,
        name: error.name,
        stack: error.stack,
        context,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
    }

    // 在开发环境下打印到控制台
    if (process.env.NODE_ENV === 'development') {
        console.error('Error logged:', errorInfo)
    }

    // 在生产环境下，可以发送到错误监控服务
    // 例如：Sentry, LogRocket, Bugsnag 等
    if (process.env.NODE_ENV === 'production') {
        // 示例：发送到错误监控服务
        // errorReportingService.captureException(error, { extra: errorInfo })
    }
}

/**
 * 创建错误边界错误处理器
 */
export const createErrorBoundaryHandler = () => {
    return (error: Error, errorInfo: any) => {
        logError(error, 'ErrorBoundary')

        // 可以在这里添加额外的错误处理逻辑
        // 例如：发送错误报告、显示用户友好的错误消息等
    }
}

/**
 * 验证错误类型
 */
export const isAppError = (error: any): error is AppError => {
    return error instanceof AppError
}

/**
 * 获取用户友好的错误消息
 */
export const getUserFriendlyMessage = (error: Error): string => {
    if (isAppError(error)) {
        switch (error.code) {
            case 'NETWORK_ERROR':
                return '网络连接失败，请检查网络设置'
            case 'HTTP_401':
                return '登录已过期，请重新登录'
            case 'HTTP_403':
                return '没有权限访问此资源'
            case 'HTTP_404':
                return '请求的资源不存在'
            case 'HTTP_500':
                return '服务器内部错误，请稍后重试'
            default:
                return error.message
        }
    }

    return error.message || '发生了未知错误'
}

/**
 * 错误重试机制
 */
export const withRetry = <T extends any[], R>(
    fn: (...args: T) => Promise<R>,
    maxRetries: number = 3,
    delay: number = 1000
) => {
    return async (...args: T): Promise<R> => {
        let lastError: Error

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await fn(...args)
            } catch (error) {
                lastError = error as Error

                // 如果是最后一次尝试，直接抛出错误
                if (attempt === maxRetries) {
                    throw lastError
                }

                // 等待指定时间后重试
                await new Promise(resolve => setTimeout(resolve, delay * attempt))
            }
        }

        throw lastError!
    }
}
