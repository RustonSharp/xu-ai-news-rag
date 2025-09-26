import React, { createContext, useContext, useState, useEffect } from 'react'

const ThemeContext = createContext()

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

export const ThemeProvider = ({ children }) => {
  // 从本地存储获取保存的主题，默认为 'system'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme')
    return savedTheme || 'system'
  })

  // 计算实际应用的主题
  const [actualTheme, setActualTheme] = useState('light')

  useEffect(() => {
    const updateActualTheme = () => {
      if (theme === 'system') {
        // 系统主题：根据系统偏好设置
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        setActualTheme(systemPrefersDark ? 'dark' : 'light')
      } else {
        // 手动设置的主题
        setActualTheme(theme)
      }
    }

    updateActualTheme()

    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      if (theme === 'system') {
        updateActualTheme()
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [theme])

  useEffect(() => {
    // 应用主题到文档根元素
    document.documentElement.setAttribute('data-theme', actualTheme)
    
    // 保存主题到本地存储
    localStorage.setItem('theme', theme)
  }, [theme, actualTheme])

  const toggleTheme = () => {
    setTheme(prev => {
      if (prev === 'light') return 'dark'
      if (prev === 'dark') return 'system'
      return 'light' // system -> light
    })
  }

  const setThemeMode = (mode) => {
    if (['light', 'dark', 'system'].includes(mode)) {
      setTheme(mode)
    }
  }

  const value = {
    theme, // 用户设置的主题模式 ('light', 'dark', 'system')
    actualTheme, // 实际应用的主题 ('light', 'dark')
    toggleTheme,
    setThemeMode,
    isDark: actualTheme === 'dark'
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}