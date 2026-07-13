export const colors = {
  light: {
    bg: {
      surface: '#faf9f7',
      sidebar: '#f3f1ed',
      card: '#ffffff',
      input: '#ffffff',
      hover: '#faf8f5',
      active: '#f3f1ed',
    },
    text: {
      primary: '#1a1a1a',
      secondary: '#555555',
      muted: '#888888',
      inverse: '#ffffff',
    },
    border: {
      default: '#e8e5e1',
      focus: '#d4cfc6',
      hover: '#d4cfc6',
    },
    accent: {
      primary: '#d97706',
      hover: '#b8610a',
      active: '#92400e',
      light: '#f5efe6',
      text: '#d97706',
    },
    semantic: {
      success: '#059669',
      successLight: '#d1fae5',
      warning: '#d97706',
      warningLight: '#fef3c7',
      danger: '#dc2626',
      dangerLight: '#fee2e2',
      info: '#2563eb',
      infoLight: '#dbeafe',
    },
  },
  dark: {
    bg: {
      surface: '#1a1b1e',
      sidebar: '#141517',
      card: '#212226',
      input: '#212226',
      hover: '#323336',
      active: '#252629',
    },
    text: {
      primary: '#e4e4e4',
      secondary: '#aaaaaa',
      muted: '#777777',
      inverse: '#1a1a1a',
    },
    border: {
      default: '#2a2b2e',
      focus: '#3d3e42',
      hover: '#3d3e42',
    },
    accent: {
      primary: '#f0c070',
      hover: '#f59b1e',
      active: '#b8610a',
      light: '#3d2e18',
      text: '#f0c070',
    },
    semantic: {
      success: '#10b981',
      successLight: '#064e3b',
      warning: '#f59e0b',
      warningLight: '#78350f',
      danger: '#f43f5e',
      dangerLight: '#4c0519',
      info: '#3b82f6',
      infoLight: '#1e3a5f',
    },
  },
}

export const fontFamily = {
  sans: [
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    'Roboto',
    '"Helvetica Neue"',
    'Arial',
    '"Noto Sans"',
    'sans-serif',
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"',
    '"Noto Color Emoji"',
  ].join(', '),
  mono: [
    'ui-monospace',
    'SFMono-Regular',
    'Menlo',
    'Monaco',
    'Consolas',
    '"Liberation Mono"',
    '"Courier New"',
    'monospace',
  ].join(', '),
}

export const fontSize = {
  xs: '0.75rem',
  sm: '0.875rem',
  base: '1rem',
  lg: '1.125rem',
  xl: '1.25rem',
  '2xl': '1.5rem',
  '3xl': '1.875rem',
  '4xl': '2.25rem',
  '5xl': '3rem',
  '6xl': '3.75rem',
}

export const fontWeight = {
  normal: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
}

export const spacing = {
  0: '0',
  1: '4px',
  2: '8px',
  3: '12px',
  4: '16px',
  5: '20px',
  6: '24px',
  8: '32px',
  10: '40px',
  12: '48px',
  16: '64px',
}

export const borderRadius = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  full: '9999px',
}

export const boxShadow = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
}

export const transition = {
  duration: {
    fast: '150ms',
    normal: '200ms',
    slow: '300ms',
  },
  easing: {
    default: 'cubic-bezier(0.4, 0, 0.2, 1)',
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  },
}

export const layout = {
  sidebarWidth: '260px',
  sidebarCollapsedWidth: '64px',
  headerHeight: '64px',
  maxContentWidth: '1200px',
}
