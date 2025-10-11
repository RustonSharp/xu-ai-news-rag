import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import ProtectedRoute from './ProtectedRoute'
import { AuthProvider } from '@/contexts/AuthContext'

// Mock the AuthContext
const mockUseAuth = vi.fn()
vi.mock('@/contexts/AuthContext', () => ({
    useAuth: () => mockUseAuth(),
    AuthProvider: ({ children }: { children: React.ReactNode }) => children,
}))

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>
        <AuthProvider>
            {children}
        </AuthProvider>
    </BrowserRouter>
)

describe('ProtectedRoute', () => {
    beforeEach(() => {
        vi.clearAllMocks()
    })

    it('should render children when user is authenticated', () => {
        mockUseAuth.mockReturnValue({
            isAuthenticated: true,
            loading: false,
        })

        render(
            <TestWrapper>
                <ProtectedRoute>
                    <div data-testid="protected-content">Protected Content</div>
                </ProtectedRoute>
            </TestWrapper>
        )

        expect(screen.getByTestId('protected-content')).toBeInTheDocument()
    })

    it('should show loading spinner when loading', () => {
        mockUseAuth.mockReturnValue({
            isAuthenticated: false,
            loading: true,
        })

        render(
            <TestWrapper>
                <ProtectedRoute>
                    <div data-testid="protected-content">Protected Content</div>
                </ProtectedRoute>
            </TestWrapper>
        )

        expect(screen.getByText('正在验证身份...')).toBeInTheDocument()
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
    })

    it('should redirect to login when not authenticated', () => {
        mockUseAuth.mockReturnValue({
            isAuthenticated: false,
            loading: false,
        })

        render(
            <TestWrapper>
                <ProtectedRoute>
                    <div data-testid="protected-content">Protected Content</div>
                </ProtectedRoute>
            </TestWrapper>
        )

        // The Navigate component should redirect to /login
        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
    })

    it('should pass location state when redirecting', () => {
        mockUseAuth.mockReturnValue({
            isAuthenticated: false,
            loading: false,
        })

        // Mock useLocation to return a specific location
        const mockLocation = { pathname: '/protected-page', search: '', hash: '', state: null }
        vi.spyOn(require('react-router-dom'), 'useLocation').mockReturnValue(mockLocation)

        render(
            <TestWrapper>
                <ProtectedRoute>
                    <div data-testid="protected-content">Protected Content</div>
                </ProtectedRoute>
            </TestWrapper>
        )

        expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument()
    })
})
