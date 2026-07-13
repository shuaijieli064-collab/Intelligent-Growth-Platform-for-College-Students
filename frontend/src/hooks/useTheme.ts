import { useEffect } from 'react'
import { useThemeStore, type Theme } from '@/store/themeStore'

export function useTheme() {
  const { theme, setTheme, toggleTheme } = useThemeStore()

  useEffect(() => {
    const storedTheme = useThemeStore.getState().theme
    if (storedTheme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [])

  return {
    theme,
    setTheme: (newTheme: Theme) => {
      setTheme(newTheme)
    },
    toggleTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light',
  }
}
