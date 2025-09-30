import request from '../request'
import { API_ENDPOINTS } from '../endpoints'
import type { ApiResponse, User } from '@/types'

// 认证相关类型定义
export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  name?: string
}

export interface LoginResponse {
  user: User
  token: string
  refreshToken: string
}

export interface RefreshTokenResponse {
  token: string
  refreshToken: string
}

export interface UpdateProfileData {
  name?: string
  email?: string
  avatar?: string
  preferences?: Record<string, any>
}

/**
 * 认证相关 API
 */
export const authAPI = {
  /**
   * 用户登录
   */
  login: (email: string, password: string): Promise<ApiResponse<LoginResponse>> => {
    return request.post(API_ENDPOINTS.AUTH.LOGIN, {
      email,
      password
    })
  },
  
  /**
   * 用户注册
   */
  register: (email: string, password: string): Promise<ApiResponse<{ message: string }>> => {
    return request.post(API_ENDPOINTS.AUTH.REGISTER, {
      email,
      password
    })
  },
  
  /**
   * 刷新 token
   */
  refreshToken: (): Promise<ApiResponse<RefreshTokenResponse>> => {
    return request.post(API_ENDPOINTS.AUTH.REFRESH)
  },
  
  /**
   * 用户登出
   */
  logout: (): Promise<ApiResponse<{ message: string }>> => {
    return request.post(API_ENDPOINTS.AUTH.LOGOUT)
  },
  
  /**
   * 获取用户信息
   */
  getProfile: (): Promise<ApiResponse<User>> => {
    return request.get(API_ENDPOINTS.AUTH.PROFILE)
  },
  
  /**
   * 更新用户信息
   */
  updateProfile: (userData: UpdateProfileData): Promise<ApiResponse<User>> => {
    return request.put(API_ENDPOINTS.AUTH.PROFILE, userData)
  }
}