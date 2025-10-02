import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI, setAuthToken, clearAuth } from '../api'
import type { User } from '@/types'

// AuthContext 类型定义
interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; message?: string }>
  register: (email: string, password: string) => Promise<{ success: boolean; message?: string }>
  logout: () => Promise<void>
  isAuthenticated: boolean
}

// Provider Props 类型
interface AuthProviderProps {
  children: ReactNode
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}



export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    // 检查本地存储的token和用户信息
    const token = localStorage.getItem('token')
    const userData = localStorage.getItem('user')

    if (token && userData) {
      try {
        setUser(JSON.parse(userData))
      } catch (error) {
        console.error('解析用户数据失败:', error)
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }

    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login(email, password)

      console.log('登录响应', response.data)
      const { token, user: userData } = response.data as { token: string; user: User }

      // 保存token和用户信息
      console.log('准备写入token', token)
      setAuthToken(token)
      localStorage.setItem('user', JSON.stringify(userData))

      setUser(userData)

      return { success: true }
    } catch (error: any) {
      console.error('登录失败:', error)
      return {
        success: false,
        message: error.response?.data?.message || '登录失败，请检查邮箱和密码'
      }
    }
  }

  const logout = async (): Promise<void> => {
    try {
      // 调用后端登出接口
      await authAPI.logout()
    } catch (error) {
      console.warn('后端登出失败:', error)
    } finally {
      // 无论后端是否成功，都清除本地数据
      clearAuth()
      setUser(null)
    }
  }

  const register = async (email: string, password: string) => {
    try {
      const response = await authAPI.register(email, password)

      return { success: true, message: '注册成功，请登录' }
    } catch (error: any) {
      console.error('注册失败:', error)
      return {
        success: false,
        message: error.response?.data?.message || '注册失败，请稍后重试'
      }
    }
  }

  const value = {
    user,
    login,
    logout,
    register,
    loading,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}