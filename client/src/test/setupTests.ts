// src/test/setupTests.ts
import '@testing-library/jest-dom/vitest'

// Chakra & layout shims for JSDOM
class RO {
  observe() {}
  unobserve() {}
  disconnect() {}
}

const g = globalThis as any;

g.ResizeObserver = g.ResizeObserver || RO;

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},          // deprecated but some libs still call it
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => false,
  }),
});

// no-op scroll for JSDOM
if (!window.scrollTo) {
  window.scrollTo = () => {};
}
