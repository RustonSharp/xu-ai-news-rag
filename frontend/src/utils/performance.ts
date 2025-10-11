/**
 * 性能监控工具
 */

interface PerformanceMetric {
    name: string
    value: number
    delta: number
    id: string
    navigationType: string
}

interface WebVitalsMetric {
    name: 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB'
    value: number
    delta: number
    id: string
    navigationType: string
}

/**
 * 测量性能指标
 */
export const measurePerformance = (metricName: string, startTime?: number) => {
    if (!('performance' in window)) {
        console.warn('Performance API not supported')
        return
    }

    if (startTime) {
        const endTime = performance.now()
        const duration = endTime - startTime
        console.log(`${metricName}: ${duration.toFixed(2)}ms`)
        return duration
    } else {
        performance.mark(metricName)
        return performance.now()
    }
}

/**
 * 测量函数执行时间
 */
export const measureFunction = <T extends any[], R>(
    fn: (...args: T) => R,
    functionName: string
) => {
    return (...args: T): R => {
        const startTime = performance.now()
        const result = fn(...args)
        const endTime = performance.now()

        console.log(`${functionName} execution time: ${(endTime - startTime).toFixed(2)}ms`)
        return result
    }
}

/**
 * 测量异步函数执行时间
 */
export const measureAsyncFunction = <T extends any[], R>(
    fn: (...args: T) => Promise<R>,
    functionName: string
) => {
    return async (...args: T): Promise<R> => {
        const startTime = performance.now()
        const result = await fn(...args)
        const endTime = performance.now()

        console.log(`${functionName} execution time: ${(endTime - startTime).toFixed(2)}ms`)
        return result
    }
}

/**
 * 报告Web Vitals指标
 */
export const reportWebVitals = (onPerfEntry?: (metric: WebVitalsMetric) => void) => {
    if (onPerfEntry && onPerfEntry instanceof Function) {
        import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
            getCLS(onPerfEntry)
            getFID(onPerfEntry)
            getFCP(onPerfEntry)
            getLCP(onPerfEntry)
            getTTFB(onPerfEntry)
        }).catch((error) => {
            console.warn('Failed to load web-vitals:', error)
        })
    }
}

/**
 * 自定义性能指标收集器
 */
class PerformanceCollector {
    private metrics: Map<string, number[]> = new Map()

    recordMetric(name: string, value: number) {
        if (!this.metrics.has(name)) {
            this.metrics.set(name, [])
        }
        this.metrics.get(name)!.push(value)
    }

    getAverageMetric(name: string): number {
        const values = this.metrics.get(name)
        if (!values || values.length === 0) return 0

        return values.reduce((sum, value) => sum + value, 0) / values.length
    }

    getMetricStats(name: string) {
        const values = this.metrics.get(name)
        if (!values || values.length === 0) return null

        const sorted = [...values].sort((a, b) => a - b)
        const min = sorted[0]
        const max = sorted[sorted.length - 1]
        const avg = this.getAverageMetric(name)
        const median = sorted.length % 2 === 0
            ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
            : sorted[Math.floor(sorted.length / 2)]

        return {
            count: values.length,
            min,
            max,
            avg,
            median,
            values: sorted
        }
    }

    getAllMetrics() {
        const result: Record<string, any> = {}
        for (const [name] of this.metrics) {
            result[name] = this.getMetricStats(name)
        }
        return result
    }

    clear() {
        this.metrics.clear()
    }
}

export const performanceCollector = new PerformanceCollector()

/**
 * 页面加载性能监控
 */
export const monitorPageLoad = () => {
    if (!('performance' in window)) return

    window.addEventListener('load', () => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming

        if (navigation) {
            const metrics = {
                'DNS查询时间': navigation.domainLookupEnd - navigation.domainLookupStart,
                'TCP连接时间': navigation.connectEnd - navigation.connectStart,
                '请求响应时间': navigation.responseEnd - navigation.requestStart,
                'DOM解析时间': navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                '页面完全加载时间': navigation.loadEventEnd - navigation.loadEventStart,
                '总加载时间': navigation.loadEventEnd - navigation.navigationStart,
            }

            console.group('页面加载性能指标')
            Object.entries(metrics).forEach(([name, value]) => {
                console.log(`${name}: ${value.toFixed(2)}ms`)
                performanceCollector.recordMetric(name, value)
            })
            console.groupEnd()
        }
    })
}

/**
 * 资源加载性能监控
 */
export const monitorResourceLoad = () => {
    if (!('performance' in window)) return

    const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
            if (entry.entryType === 'resource') {
                const resource = entry as PerformanceResourceTiming
                const loadTime = resource.responseEnd - resource.startTime

                console.log(`资源加载: ${resource.name} - ${loadTime.toFixed(2)}ms`)
                performanceCollector.recordMetric('资源加载时间', loadTime)
            }
        })
    })

    observer.observe({ entryTypes: ['resource'] })
}

/**
 * 内存使用监控
 */
export const monitorMemoryUsage = () => {
    if (!('memory' in performance)) return

    const logMemoryUsage = () => {
        const memory = (performance as any).memory
        const usage = {
            '已使用内存': `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
            '总内存限制': `${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)} MB`,
            '内存限制': `${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)} MB`,
        }

        console.log('内存使用情况:', usage)
    }

    // 每30秒记录一次内存使用情况
    setInterval(logMemoryUsage, 30000)
    logMemoryUsage() // 立即记录一次
}

/**
 * 初始化性能监控
 */
export const initPerformanceMonitoring = () => {
    if (process.env.NODE_ENV === 'development') {
        monitorPageLoad()
        monitorResourceLoad()
        monitorMemoryUsage()

            // 在控制台暴露性能收集器，方便调试
            ; (window as any).performanceCollector = performanceCollector
    }
}

/**
 * 组件渲染性能监控Hook
 */
export const useRenderPerformance = (componentName: string) => {
    const startTime = performance.now()

    React.useEffect(() => {
        const endTime = performance.now()
        const renderTime = endTime - startTime

        console.log(`${componentName} 渲染时间: ${renderTime.toFixed(2)}ms`)
        performanceCollector.recordMetric(`${componentName}渲染时间`, renderTime)
    })
}

// 导入React用于Hook
import React from 'react'
