import { renderHook, act, waitFor } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { AuthProvider, useAuth } from './AuthContext'
import { authAPI } from '@/api'

// Mock the authAPI
vi.mock('@/api', () => ({
    authAPI: {
        login: vi.fn(),
        register: vi.fn(),
        logout: vi.fn(),
    },
    setAuthToken: vi.fn(),
    clearAuth: vi.fn(),
}))

const mockAuthAPI = vi.mocked(authAPI)

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
)

describe('AuthContext', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        localStorage.clear()
    })

    it('should provide initial state', async () => {
        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        // Wait for initial loading to complete
        await waitFor(() => {
            expect(result.current.loading).toBe(false)
        })

        expect(result.current.user).toBeNull()
        expect(result.current.isAuthenticated).toBe(false)
    })

    it('should load user from localStorage on mount', async () => {
        const mockUser = {
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            is_active: true,
        }

        localStorage.setItem('token', 'mock-token')
        localStorage.setItem('user', JSON.stringify(mockUser))

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await waitFor(() => {
            expect(result.current.user).toEqual(mockUser)
            expect(result.current.isAuthenticated).toBe(true)
            expect(result.current.loading).toBe(false)
        })
    })

    it('should handle invalid user data in localStorage', async () => {
        localStorage.setItem('token', 'mock-token')
        localStorage.setItem('user', 'invalid-json')

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await waitFor(() => {
            expect(result.current.user).toBeNull()
            expect(result.current.isAuthenticated).toBe(false)
            expect(result.current.loading).toBe(false)
        })

        expect(localStorage.getItem('token')).toBeNull()
        expect(localStorage.getItem('user')).toBeNull()
    })

    it('should login successfully', async () => {
        const mockUser = {
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            is_active: true,
        }

        const mockResponse = {
            data: {
                success: true,
                token: 'mock-token',
                user: mockUser,
            }
        }

        mockAuthAPI.login.mockResolvedValue(mockResponse)

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await act(async () => {
            const response = await result.current.login('test@example.com', 'password')
            expect(response.success).toBe(true)
        })

        await waitFor(() => {
            expect(result.current.user).toEqual(mockUser)
            expect(result.current.isAuthenticated).toBe(true)
        })

        expect(localStorage.getItem('token')).toBe('mock-token')
        expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser))
    })

    it('should handle login failure', async () => {
        mockAuthAPI.login.mockResolvedValue({
            data: {
                success: false,
                message: 'Invalid credentials',
            }
        })

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await act(async () => {
            const response = await result.current.login('test@example.com', 'wrong-password')
            expect(response.success).toBe(false)
            expect(response.message).toBe('Invalid credentials')
        })

        expect(result.current.user).toBeNull()
        expect(result.current.isAuthenticated).toBe(false)
    })

    it('should register successfully', async () => {
        const mockUser = {
            id: 1,
            email: 'newuser@example.com',
            username: 'newuser',
            is_active: true,
        }

        const mockResponse = {
            data: {
                success: true,
                token: 'mock-token',
                user: mockUser,
            }
        }

        mockAuthAPI.register.mockResolvedValue(mockResponse)

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await act(async () => {
            const response = await result.current.register('newuser@example.com', 'password')
            expect(response.success).toBe(true)
        })

        await waitFor(() => {
            expect(result.current.user).toEqual(mockUser)
            expect(result.current.isAuthenticated).toBe(true)
        })
    })

    it('should handle registration failure', async () => {
        mockAuthAPI.register.mockResolvedValue({
            data: {
                success: false,
                message: 'Email already exists',
            }
        })

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await act(async () => {
            const response = await result.current.register('existing@example.com', 'password')
            expect(response.success).toBe(false)
            expect(response.message).toBe('Email already exists')
        })

        expect(result.current.user).toBeNull()
        expect(result.current.isAuthenticated).toBe(false)
    })

    it('should logout successfully', async () => {
        const mockUser = {
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            is_active: true,
        }

        // Set initial state
        localStorage.setItem('token', 'mock-token')
        localStorage.setItem('user', JSON.stringify(mockUser))

        mockAuthAPI.logout.mockResolvedValue({ data: {} })

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        // Wait for initial load
        await waitFor(() => {
            expect(result.current.isAuthenticated).toBe(true)
        })

        await act(async () => {
            await result.current.logout()
        })

        expect(result.current.user).toBeNull()
        expect(result.current.isAuthenticated).toBe(false)
        expect(localStorage.getItem('token')).toBeNull()
        expect(localStorage.getItem('user')).toBeNull()
    })

    it('should handle logout error', async () => {
        const mockUser = {
            id: 1,
            email: 'test@example.com',
            username: 'testuser',
            is_active: true,
        }

        localStorage.setItem('token', 'mock-token')
        localStorage.setItem('user', JSON.stringify(mockUser))

        mockAuthAPI.logout.mockRejectedValue(new Error('Logout failed'))

        const { result } = renderHook(() => useAuth(), {
            wrapper: TestWrapper,
        })

        await waitFor(() => {
            expect(result.current.isAuthenticated).toBe(true)
        })

        await act(async () => {
            await result.current.logout()
        })

        // Should still clear local state even if API call fails
        expect(result.current.user).toBeNull()
        expect(result.current.isAuthenticated).toBe(false)
    })

    it('should throw error when used outside provider', () => {
        // Suppress console.error for this test
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { })

        expect(() => {
            renderHook(() => useAuth())
        }).toThrow('useAuth must be used within an AuthProvider')

        consoleSpy.mockRestore()
    })
})
