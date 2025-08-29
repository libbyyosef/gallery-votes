import { extendTheme, type ThemeConfig } from '@chakra-ui/react'

export const colorModeConfig: ThemeConfig = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
}

export const theme = extendTheme({
  config: colorModeConfig,
  styles: {
    global: {
      'html, body, #root': { height: '100%' },
      body: { bg: 'app.bg', color: 'app.text' },
    },
  },
  colors: {
    app: {
      bg: '#607D8B',        
      surface: '#263238',
      card: '#90A4AE',
      text: '#e5e7eb',
      muted: '#9ca3af',
      like: '#22c55e',
      dislike: '#ef4444',
      accent: '#90A4AE',
      overlay: 'rgba(0,0,0,0.7)',
    },
  },
  radii: { sm: '8px', md: '12px', lg: '16px', xl: '24px' },
  shadows: { elev: '0 10px 30px rgba(0,0,0,0.35)' },
})
