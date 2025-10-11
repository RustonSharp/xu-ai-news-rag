import './contexts/AuthContext'  // 先执行拦截器注册
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'
import { initPerformanceMonitoring, reportWebVitals } from './utils/performance'

// 初始化性能监控
initPerformanceMonitoring()

// 报告Web Vitals
reportWebVitals((metric) => {
  console.log('Web Vitals:', metric)
})

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)