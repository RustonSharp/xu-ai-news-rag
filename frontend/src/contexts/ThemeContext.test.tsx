import { renderHook, act } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { ThemeProvider, useTheme } from './ThemeContext'

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <ThemeProvider>{children}</ThemeProvider>
)

describe('ThemeContext', () => {
    beforeEach(() => {
        localStorage.clear()
        vi.clearAllMocks()
    })

    it('should provide initial theme state', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        expect(result.current.theme).toBe('system')
        expect(typeof result.current.toggleTheme).toBe('function')
    })

    it('should load theme from localStorage on mount', () => {
        // Set localStorage before creating the component
        localStorage.setItem('theme', 'dark')

        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        expect(result.current.theme).toBe('dark')
    })

    it('should toggle theme from light to dark', () => {
        localStorage.setItem('theme', 'light')

        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        expect(result.current.theme).toBe('light')

        act(() => {
            result.current.toggleTheme()
        })

        expect(result.current.theme).toBe('dark')
        expect(localStorage.getItem('theme')).toBe('dark')
    })

    it('should toggle theme from dark to light', () => {
        localStorage.setItem('theme', 'dark')

        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        expect(result.current.theme).toBe('dark')

        act(() => {
            result.current.toggleTheme()
        })

        expect(result.current.theme).toBe('light')
        expect(localStorage.getItem('theme')).toBe('light')
    })

    it('should handle invalid theme in localStorage', () => {
        localStorage.setItem('theme', 'invalid-theme')

        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        // Should default to system theme
        expect(result.current.theme).toBe('system')
    })

    it('should update document class when theme changes', () => {
        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        act(() => {
            result.current.toggleTheme()
        })

        expect(document.documentElement.className).toContain('dark')
    })

    it('should remove dark class when switching to light theme', () => {
        localStorage.setItem('theme', 'dark')

        const { result } = renderHook(() => useTheme(), {
            wrapper: TestWrapper,
        })

        act(() => {
            result.current.toggleTheme()
        })

        expect(document.documentElement.className).not.toContain('dark')
    })
})
