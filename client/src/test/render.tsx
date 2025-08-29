// src/test/render.tsx
import React from 'react'
import { render } from '@testing-library/react'
import { AllProviders } from './testUtils'

export function renderWithProviders(ui: React.ReactElement, options?: Parameters<typeof render>[1]) {
  return render(ui, { wrapper: AllProviders, ...options })
}
