/**
 * Theme types for OAuth SDK
 */

export type ThemeMode = 'light' | 'dark' | 'auto'

export type ThemeVariant = 'default' | 'compact' | 'minimal' | 'full'

export interface ThemeColors {
  // Primary colors
  primary?: string
  primaryHover?: string
  primaryActive?: string
  
  // Secondary colors
  secondary?: string
  secondaryHover?: string
  
  // Background colors
  background?: string
  surface?: string
  surfaceHover?: string
  
  // Text colors
  text?: string
  textSecondary?: string
  textMuted?: string
  
  // Border colors
  border?: string
  borderHover?: string
  
  // Status colors
  success?: string
  error?: string
  warning?: string
  info?: string
  
  // Status backgrounds
  successBg?: string
  errorBg?: string
  warningBg?: string
  infoBg?: string
}

export interface ThemeTypography {
  fontFamily?: string
  fontSize?: {
    xs?: string
    sm?: string
    base?: string
    lg?: string
    xl?: string
    '2xl'?: string
  }
  fontWeight?: {
    normal?: number
    medium?: number
    semibold?: number
    bold?: number
  }
  lineHeight?: {
    tight?: number
    normal?: number
    relaxed?: number
  }
}

export interface ThemeSpacing {
  borderRadius?: string
  padding?: {
    xs?: string
    sm?: string
    md?: string
    lg?: string
    xl?: string
  }
  gap?: {
    xs?: string
    sm?: string
    md?: string
    lg?: string
    xl?: string
  }
}

export interface ThemeShadows {
  sm?: string
  md?: string
  lg?: string
  xl?: string
}

export interface ThemeAnimations {
  duration?: {
    fast?: string
    normal?: string
    slow?: string
  }
  easing?: {
    linear?: string
    easeIn?: string
    easeOut?: string
    easeInOut?: string
  }
}

export interface ThemeBranding {
  logo?: string
  logoAlt?: string
  showPoweredBy?: boolean
  customFooter?: string
}

export interface Theme {
  mode?: ThemeMode
  variant?: ThemeVariant
  colors?: ThemeColors
  typography?: ThemeTypography
  spacing?: ThemeSpacing
  shadows?: ThemeShadows
  animations?: ThemeAnimations
  branding?: ThemeBranding
  
  // Custom CSS variables
  customCSS?: Record<string, string>
}

export interface ThemePreset {
  name: string
  description: string
  theme: Theme
}

// Default theme values
export const defaultLightTheme: Theme = {
  mode: 'light',
  variant: 'default',
  colors: {
    primary: '#007bff',
    primaryHover: '#0056b3',
    primaryActive: '#004085',
    secondary: '#6c757d',
    secondaryHover: '#5a6268',
    background: '#ffffff',
    surface: '#f8f9fa',
    surfaceHover: '#e9ecef',
    text: '#212529',
    textSecondary: '#6c757d',
    textMuted: '#adb5bd',
    border: '#dee2e6',
    borderHover: '#adb5bd',
    success: '#28a745',
    error: '#dc3545',
    warning: '#ffc107',
    info: '#17a2b8',
    successBg: '#d4edda',
    errorBg: '#f8d7da',
    warningBg: '#fff3cd',
    infoBg: '#d1ecf1'
  },
  typography: {
    fontFamily: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem'
    },
    fontWeight: {
      normal: 400,
      medium: 500,
      semibold: 600,
      bold: 700
    },
    lineHeight: {
      tight: 1.25,
      normal: 1.5,
      relaxed: 1.75
    }
  },
  spacing: {
    borderRadius: '0.5rem',
    padding: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    },
    gap: {
      xs: '0.25rem',
      sm: '0.5rem',
      md: '1rem',
      lg: '1.5rem',
      xl: '2rem'
    }
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
  },
  animations: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms'
    },
    easing: {
      linear: 'linear',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)'
    }
  },
  branding: {
    showPoweredBy: true
  }
}

export const defaultDarkTheme: Theme = {
  ...defaultLightTheme,
  mode: 'dark',
  colors: {
    primary: '#4dabf7',
    primaryHover: '#339af0',
    primaryActive: '#1c7ed6',
    secondary: '#868e96',
    secondaryHover: '#adb5bd',
    background: '#1a1a1a',
    surface: '#2d2d2d',
    surfaceHover: '#3d3d3d',
    text: '#f8f9fa',
    textSecondary: '#adb5bd',
    textMuted: '#6c757d',
    border: '#495057',
    borderHover: '#6c757d',
    success: '#51cf66',
    error: '#ff6b6b',
    warning: '#ffd43b',
    info: '#4dabf7',
    successBg: '#2b8a3e',
    errorBg: '#c92a2a',
    warningBg: '#e67700',
    infoBg: '#1864ab'
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.4)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.5)'
  }
}

// Theme presets
export const themePresets: ThemePreset[] = [
  {
    name: 'Light',
    description: 'Clean and bright theme',
    theme: defaultLightTheme
  },
  {
    name: 'Dark',
    description: 'Easy on the eyes',
    theme: defaultDarkTheme
  },
  {
    name: 'Ocean',
    description: 'Cool blue tones',
    theme: {
      ...defaultLightTheme,
      colors: {
        ...defaultLightTheme.colors,
        primary: '#0ea5e9',
        primaryHover: '#0284c7',
        primaryActive: '#0369a1',
        background: '#f0f9ff',
        surface: '#e0f2fe'
      }
    }
  },
  {
    name: 'Forest',
    description: 'Natural green theme',
    theme: {
      ...defaultLightTheme,
      colors: {
        ...defaultLightTheme.colors,
        primary: '#10b981',
        primaryHover: '#059669',
        primaryActive: '#047857',
        background: '#f0fdf4',
        surface: '#dcfce7'
      }
    }
  },
  {
    name: 'Sunset',
    description: 'Warm orange and purple',
    theme: {
      ...defaultLightTheme,
      colors: {
        ...defaultLightTheme.colors,
        primary: '#f59e0b',
        primaryHover: '#d97706',
        primaryActive: '#b45309',
        secondary: '#8b5cf6',
        background: '#fffbeb',
        surface: '#fef3c7'
      }
    }
  },
  {
    name: 'Midnight',
    description: 'Deep dark theme',
    theme: {
      ...defaultDarkTheme,
      colors: {
        ...defaultDarkTheme.colors,
        background: '#0f172a',
        surface: '#1e293b',
        surfaceHover: '#334155'
      }
    }
  }
]
