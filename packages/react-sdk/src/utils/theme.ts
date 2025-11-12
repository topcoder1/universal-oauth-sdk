import type { Theme, ThemeMode } from '../types/theme'
import { defaultLightTheme, defaultDarkTheme } from '../types/theme'

/**
 * Merge theme with defaults
 */
export function mergeTheme(customTheme?: Partial<Theme>): Theme {
  if (!customTheme) return defaultLightTheme

  const baseTheme = customTheme.mode === 'dark' ? defaultDarkTheme : defaultLightTheme

  return {
    ...baseTheme,
    ...customTheme,
    colors: {
      ...baseTheme.colors,
      ...customTheme.colors
    },
    typography: {
      ...baseTheme.typography,
      ...customTheme.typography,
      fontSize: {
        ...baseTheme.typography?.fontSize,
        ...customTheme.typography?.fontSize
      },
      fontWeight: {
        ...baseTheme.typography?.fontWeight,
        ...customTheme.typography?.fontWeight
      },
      lineHeight: {
        ...baseTheme.typography?.lineHeight,
        ...customTheme.typography?.lineHeight
      }
    },
    spacing: {
      ...baseTheme.spacing,
      ...customTheme.spacing,
      padding: {
        ...baseTheme.spacing?.padding,
        ...customTheme.spacing?.padding
      },
      gap: {
        ...baseTheme.spacing?.gap,
        ...customTheme.spacing?.gap
      }
    },
    shadows: {
      ...baseTheme.shadows,
      ...customTheme.shadows
    },
    animations: {
      ...baseTheme.animations,
      ...customTheme.animations,
      duration: {
        ...baseTheme.animations?.duration,
        ...customTheme.animations?.duration
      },
      easing: {
        ...baseTheme.animations?.easing,
        ...customTheme.animations?.easing
      }
    },
    branding: {
      ...baseTheme.branding,
      ...customTheme.branding
    },
    customCSS: {
      ...baseTheme.customCSS,
      ...customTheme.customCSS
    }
  }
}

/**
 * Convert theme to CSS variables
 */
export function themeToCSSVariables(theme: Theme): Record<string, string> {
  const vars: Record<string, string> = {}

  // Colors
  if (theme.colors) {
    Object.entries(theme.colors).forEach(([key, value]) => {
      if (value) {
        vars[`--oauth-${camelToKebab(key)}`] = value
      }
    })
  }

  // Typography
  if (theme.typography) {
    if (theme.typography.fontFamily) {
      vars['--oauth-font-family'] = theme.typography.fontFamily
    }
    if (theme.typography.fontSize) {
      Object.entries(theme.typography.fontSize).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-font-size-${key}`] = value
        }
      })
    }
    if (theme.typography.fontWeight) {
      Object.entries(theme.typography.fontWeight).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-font-weight-${key}`] = value.toString()
        }
      })
    }
    if (theme.typography.lineHeight) {
      Object.entries(theme.typography.lineHeight).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-line-height-${key}`] = value.toString()
        }
      })
    }
  }

  // Spacing
  if (theme.spacing) {
    if (theme.spacing.borderRadius) {
      vars['--oauth-border-radius'] = theme.spacing.borderRadius
    }
    if (theme.spacing.padding) {
      Object.entries(theme.spacing.padding).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-padding-${key}`] = value
        }
      })
    }
    if (theme.spacing.gap) {
      Object.entries(theme.spacing.gap).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-gap-${key}`] = value
        }
      })
    }
  }

  // Shadows
  if (theme.shadows) {
    Object.entries(theme.shadows).forEach(([key, value]) => {
      if (value) {
        vars[`--oauth-shadow-${key}`] = value
      }
    })
  }

  // Animations
  if (theme.animations) {
    if (theme.animations.duration) {
      Object.entries(theme.animations.duration).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-duration-${key}`] = value
        }
      })
    }
    if (theme.animations.easing) {
      Object.entries(theme.animations.easing).forEach(([key, value]) => {
        if (value) {
          vars[`--oauth-easing-${camelToKebab(key)}`] = value
        }
      })
    }
  }

  // Custom CSS
  if (theme.customCSS) {
    Object.entries(theme.customCSS).forEach(([key, value]) => {
      vars[key] = value
    })
  }

  return vars
}

/**
 * Detect system theme preference
 */
export function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light'
  
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

/**
 * Resolve theme mode (handle 'auto')
 */
export function resolveThemeMode(mode?: ThemeMode): 'light' | 'dark' {
  if (mode === 'auto' || !mode) {
    return mode === 'auto' ? getSystemTheme() : 'light'
  }
  return mode
}

/**
 * Convert camelCase to kebab-case
 */
function camelToKebab(str: string): string {
  return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
}

/**
 * Get contrast color (black or white) for a background color
 */
export function getContrastColor(hexColor: string): string {
  // Remove # if present
  const hex = hexColor.replace('#', '')
  
  // Convert to RGB
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  
  // Calculate relative luminance
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  
  // Return black or white based on luminance
  return luminance > 0.5 ? '#000000' : '#ffffff'
}

/**
 * Lighten a color by a percentage
 */
export function lightenColor(hexColor: string, percent: number): string {
  const hex = hexColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  
  const newR = Math.min(255, Math.floor(r + (255 - r) * (percent / 100)))
  const newG = Math.min(255, Math.floor(g + (255 - g) * (percent / 100)))
  const newB = Math.min(255, Math.floor(b + (255 - b) * (percent / 100)))
  
  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`
}

/**
 * Darken a color by a percentage
 */
export function darkenColor(hexColor: string, percent: number): string {
  const hex = hexColor.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)
  
  const newR = Math.max(0, Math.floor(r * (1 - percent / 100)))
  const newG = Math.max(0, Math.floor(g * (1 - percent / 100)))
  const newB = Math.max(0, Math.floor(b * (1 - percent / 100)))
  
  return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`
}

/**
 * Generate hover and active colors from primary color
 */
export function generateColorVariants(primaryColor: string): {
  hover: string
  active: string
} {
  return {
    hover: darkenColor(primaryColor, 15),
    active: darkenColor(primaryColor, 25)
  }
}

/**
 * Apply theme to element
 */
export function applyThemeToElement(element: HTMLElement, theme: Theme): void {
  const cssVars = themeToCSSVariables(theme)
  
  Object.entries(cssVars).forEach(([key, value]) => {
    element.style.setProperty(key, value)
  })
  
  // Add theme mode class
  const mode: 'light' | 'dark' = resolveThemeMode(theme.mode)
  element.classList.add(`oauth-theme-${mode}`)
  element.classList.remove(`oauth-theme-${mode === 'light' ? 'dark' : 'light'}`)
  
  // Add variant class
  if (theme.variant) {
    element.classList.add(`oauth-variant-${theme.variant}`)
  }
}
