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
  // Get saved theme from local storage, default to 'system'
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme')
    return savedTheme || 'system'
  })

  // Calculate the actual applied theme
  const [actualTheme, setActualTheme] = useState('light')

  useEffect(() => {
    const updateActualTheme = () => {
      if (theme === 'system') {
        // System theme: based on system preferences
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        setActualTheme(systemPrefersDark ? 'dark' : 'light')
      } else {
        // Manually set theme
        setActualTheme(theme)
      }
    }

    updateActualTheme()

    // Listen for system theme changes
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
    // Apply theme to document root element
    document.documentElement.setAttribute('data-theme', actualTheme)
    
    // Save theme to local storage
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