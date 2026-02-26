export const colors = {
  background: '#0a0a0f',
  surface: '#14141f',
  surfaceLight: '#1e1e2e',
  surfaceHover: '#25253a',
  text: '#e8e6e3',
  textMuted: '#8a8a9a',
  textDim: '#5a5a6a',
  accent: '#d4a843',
  accentDim: '#9a7a30',
  accentBright: '#f0c050',
  border: '#2a2a3a',
  borderLight: '#3a3a4a',

  healthy: '#4caf50',
  injured: '#ef5350',
  rivalry: '#ff9800',
  win: '#4caf50',
  loss: '#ef5350',
  draw: '#8a8a9a',

  face: '#5b9bd5',
  heel: '#e74c3c',
  tweener: '#9b59b6',

  statLow: '#ef5350',
  statMid: '#d4a843',
  statHigh: '#4caf50',

  ko: '#ff6b35',
  submission: '#7c4dff',
  decision: '#5b9bd5',
}

export function withAlpha(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

export const fonts = {
  body: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', 'Monaco', monospace",
  heading: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', 'Monaco', monospace",
}

export const fontSizes = {
  xs: '0.7rem',
  sm: '0.8rem',
  md: '0.9rem',
  lg: '1.1rem',
  xl: '1.3rem',
  xxl: '1.6rem',
  xxxl: '2rem',
}

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
}
