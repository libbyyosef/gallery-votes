// src/test/testUtils.tsx
import React, { PropsWithChildren } from 'react'
import { render } from '@testing-library/react'
import { ChakraProvider, extendTheme } from '@chakra-ui/react'
import { Provider as JotaiProvider } from 'jotai'

// Minimal theme tokens your components expect
const testTheme = extendTheme({
  colors: {
    app: {
      bg: '#0b0f14',
      text: '#e7e7ea',
      muted: '#8a8f98',
      card: '#121821',
      like: '#a3ffa4',
      dislike: '#ffc2c2',
    },
  },
  shadows: {
    elev: '0 2px 10px rgba(0,0,0,0.3)',
  },
})

export const AllProviders: React.FC<PropsWithChildren> = ({ children }) => (
  <ChakraProvider theme={testTheme}>
    <JotaiProvider>{children}</JotaiProvider>
  </ChakraProvider>
)

// Alias used by tests
export function renderWithUI(
  ui: React.ReactElement,
  options?: Parameters<typeof render>[1]
) {
  return render(ui, { wrapper: AllProviders, ...options })
}
