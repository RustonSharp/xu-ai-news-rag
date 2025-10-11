import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { Snackbar, Alert, AlertColor, Slide, SlideProps } from '@mui/material'

interface ToastMessage {
    id: string
    message: string
    severity: AlertColor
    duration?: number
    action?: React.ReactNode
}

interface ToastContextType {
    showToast: (message: string, severity?: AlertColor, duration?: number, action?: React.ReactNode) => void
    showSuccess: (message: string, duration?: number) => void
    showError: (message: string, duration?: number) => void
    showWarning: (message: string, duration?: number) => void
    showInfo: (message: string, duration?: number) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const useToast = (): ToastContextType => {
    const context = useContext(ToastContext)
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider')
    }
    return context
}

interface ToastProviderProps {
    children: ReactNode
}

// Slide transition component
function SlideTransition(props: SlideProps) {
    return <Slide {...props} direction="up" />
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
    const [toasts, setToasts] = useState<ToastMessage[]>([])
    const [currentToast, setCurrentToast] = useState<ToastMessage | null>(null)
    const [open, setOpen] = useState(false)

    const showToast = useCallback((
        message: string,
        severity: AlertColor = 'info',
        duration: number = 4000,
        action?: React.ReactNode
    ) => {
        const id = Date.now().toString()
        const newToast: ToastMessage = {
            id,
            message,
            severity,
            duration,
            action,
        }

        setToasts(prev => [...prev, newToast])

        // Show the first toast in queue
        if (!currentToast) {
            setCurrentToast(newToast)
            setOpen(true)
        }
    }, [currentToast])

    const showSuccess = useCallback((message: string, duration?: number) => {
        showToast(message, 'success', duration)
    }, [showToast])

    const showError = useCallback((message: string, duration?: number) => {
        showToast(message, 'error', duration)
    }, [showToast])

    const showWarning = useCallback((message: string, duration?: number) => {
        showToast(message, 'warning', duration)
    }, [showToast])

    const showInfo = useCallback((message: string, duration?: number) => {
        showToast(message, 'info', duration)
    }, [showToast])

    const handleClose = useCallback((event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') {
            return
        }

        setOpen(false)

        // Show next toast in queue after a short delay
        setTimeout(() => {
            setToasts(prev => {
                const remaining = prev.slice(1)
                if (remaining.length > 0) {
                    setCurrentToast(remaining[0])
                    setOpen(true)
                } else {
                    setCurrentToast(null)
                }
                return remaining
            })
        }, 300)
    }, [])

    const handleExited = useCallback(() => {
        setCurrentToast(null)
    }, [])

    const contextValue: ToastContextType = {
        showToast,
        showSuccess,
        showError,
        showWarning,
        showInfo,
    }

    return (
        <ToastContext.Provider value={contextValue}>
            {children}

            <Snackbar
                open={open}
                autoHideDuration={currentToast?.duration}
                onClose={handleClose}
                onExited={handleExited}
                TransitionComponent={SlideTransition}
                anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                sx={{
                    '& .MuiSnackbarContent-root': {
                        minWidth: 300,
                    },
                }}
            >
                {currentToast && (
                    <Alert
                        onClose={handleClose}
                        severity={currentToast.severity}
                        variant="filled"
                        action={currentToast.action}
                        sx={{
                            width: '100%',
                            '& .MuiAlert-message': {
                                width: '100%',
                            },
                        }}
                    >
                        {currentToast.message}
                    </Alert>
                )}
            </Snackbar>
        </ToastContext.Provider>
    )
}

// Hook for easy access to toast functions
export const useToastNotifications = () => {
    const { showSuccess, showError, showWarning, showInfo } = useToast()

    return {
        success: showSuccess,
        error: showError,
        warning: showWarning,
        info: showInfo,
    }
}
