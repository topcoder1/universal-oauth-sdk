import React, { createContext, useContext, useEffect, useState, useMemo } from 'react'
import type { Theme, ThemeMode } from '../types/theme'
import { mergeTheme, resolveThemeMode, themeToCSSVariables } from '../utils/theme'

interface ThemeContextValue {
  theme: Theme
  setTheme: (theme: Partial<Theme>) => void
  toggleMode: () => void
  resolvedMode: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

export interface ThemeProviderProps {
  children: React.ReactNode
  theme?: Partial<Theme>
  onChange?: (theme: Theme) => void
}

export function ThemeProvider({ children, theme: initialTheme, onChange }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(() => mergeTheme(initialTheme))

  const resolvedMode = useMemo(() => resolveThemeMode(theme.mode), [theme.mode])

  const setTheme = (newTheme: Partial<Theme>) => {
    const merged = mergeTheme({ ...theme, ...newTheme })
    setThemeState(merged)
    onChange?.(merged)
  }

  const toggleMode = () => {
    const newMode: ThemeMode = resolvedMode === 'light' ? 'dark' : 'light'
    setTheme({ mode: newMode })
  }

  // Listen for system theme changes if mode is 'auto'
  useEffect(() => {
    if (theme.mode !== 'auto') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => {
      setThemeState(prev => ({ ...prev })) // Trigger re-render
    }

    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [theme.mode])

  const value: ThemeContextValue = {
    theme,
    setTheme,
    toggleMode,
    resolvedMode
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}

/**
 * Hook to get theme CSS variables
 */
export function useThemeVariables(): Record<string, string> {
  const { theme } = useTheme()
  return useMemo(() => themeToCSSVariables(theme), [theme])
}

/**
 * Hook to apply theme to an element ref
 */
export function useThemeElement(ref: React.RefObject<HTMLElement>) {
  const { theme } = useTheme()
  const cssVars = useThemeVariables()

  useEffect(() => {
    if (!ref.current) return

    Object.entries(cssVars).forEach(([key, value]) => {
      ref.current!.style.setProperty(key, value)
    })
  }, [ref, cssVars])
}
