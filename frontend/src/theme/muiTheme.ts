import { createTheme } from '@mui/material/styles';

// 创建自定义主题
export const muiTheme = createTheme({
    palette: {
        mode: 'light',
        primary: {
            main: '#3b82f6', // 与Tailwind primary-500一致
            light: '#60a5fa',
            dark: '#1d4ed8',
            contrastText: '#ffffff',
        },
        secondary: {
            main: '#64748b', // 与Tailwind secondary-500一致
            light: '#94a3b8',
            dark: '#334155',
            contrastText: '#ffffff',
        },
        background: {
            default: '#f8fafc', // 与Tailwind secondary-50一致
            paper: '#ffffff',
        },
        text: {
            primary: '#0f172a', // 与Tailwind secondary-900一致
            secondary: '#64748b',
        },
        error: {
            main: '#ef4444',
            light: '#fca5a5',
            dark: '#dc2626',
        },
        warning: {
            main: '#f59e0b',
            light: '#fbbf24',
            dark: '#d97706',
        },
        success: {
            main: '#10b981',
            light: '#34d399',
            dark: '#059669',
        },
        info: {
            main: '#3b82f6',
            light: '#60a5fa',
            dark: '#1d4ed8',
        },
    },
    typography: {
        fontFamily: [
            'Inter',
            '-apple-system',
            'BlinkMacSystemFont',
            '"Segoe UI"',
            'Roboto',
            '"Helvetica Neue"',
            'Arial',
            'sans-serif',
        ].join(','),
        h1: {
            fontSize: '2.5rem',
            fontWeight: 700,
            lineHeight: 1.2,
        },
        h2: {
            fontSize: '2rem',
            fontWeight: 600,
            lineHeight: 1.3,
        },
        h3: {
            fontSize: '1.5rem',
            fontWeight: 600,
            lineHeight: 1.4,
        },
        h4: {
            fontSize: '1.25rem',
            fontWeight: 600,
            lineHeight: 1.4,
        },
        h5: {
            fontSize: '1.125rem',
            fontWeight: 600,
            lineHeight: 1.4,
        },
        h6: {
            fontSize: '1rem',
            fontWeight: 600,
            lineHeight: 1.4,
        },
        body1: {
            fontSize: '1rem',
            lineHeight: 1.6,
        },
        body2: {
            fontSize: '0.875rem',
            lineHeight: 1.6,
        },
    },
    shape: {
        borderRadius: 8,
    },
    spacing: 8,
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 500,
                    borderRadius: 8,
                    padding: '8px 16px',
                },
                contained: {
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                    '&:hover': {
                        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                    borderRadius: 12,
                },
            },
        },
        MuiTextField: {
            styleOverrides: {
                root: {
                    '& .MuiOutlinedInput-root': {
                        borderRadius: 8,
                    },
                },
            },
        },
        MuiAppBar: {
            styleOverrides: {
                root: {
                    boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
                },
            },
        },
    },
});

// 深色主题
export const darkMuiTheme = createTheme({
    ...muiTheme,
    palette: {
        mode: 'dark',
        primary: {
            main: '#60a5fa',
            light: '#93c5fd',
            dark: '#3b82f6',
            contrastText: '#0f172a',
        },
        secondary: {
            main: '#94a3b8',
            light: '#cbd5e1',
            dark: '#64748b',
            contrastText: '#0f172a',
        },
        background: {
            default: '#0f172a',
            paper: '#1e293b',
        },
        text: {
            primary: '#f8fafc',
            secondary: '#cbd5e1',
        },
        error: {
            main: '#f87171',
            light: '#fca5a5',
            dark: '#ef4444',
        },
        warning: {
            main: '#fbbf24',
            light: '#fde047',
            dark: '#f59e0b',
        },
        success: {
            main: '#34d399',
            light: '#6ee7b7',
            dark: '#10b981',
        },
        info: {
            main: '#60a5fa',
            light: '#93c5fd',
            dark: '#3b82f6',
        },
    },
});
