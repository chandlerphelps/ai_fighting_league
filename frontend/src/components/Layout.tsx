import { type ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState } from '../hooks/useData'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { data: worldState } = useWorldState()

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/rankings', label: 'Rankings' },
    { path: '/schedule', label: 'Schedule' },
  ]

  return (
    <div style={{ minHeight: '100vh', fontFamily: fonts.body }}>
      <nav style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: `${spacing.sm} ${spacing.lg}`,
        borderBottom: `1px solid ${colors.border}`,
        backgroundColor: colors.surface,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.lg }}>
          <Link to="/" style={{
            fontSize: fontSizes.lg,
            fontWeight: 'bold',
            color: colors.accent,
            letterSpacing: '0.05em',
          }}>
            AFL
          </Link>
          <div style={{ display: 'flex', gap: spacing.md }}>
            {navItems.map(item => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  style={{
                    color: isActive ? colors.accent : colors.textMuted,
                    fontSize: fontSizes.sm,
                    padding: `${spacing.xs} ${spacing.sm}`,
                    borderRadius: '4px',
                    backgroundColor: isActive ? withAlpha(colors.accent, 0.1) : 'transparent',
                  }}
                >
                  {item.label}
                </Link>
              )
            })}
          </div>
        </div>
        {worldState && (
          <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
            Day {worldState.day_number} — {worldState.current_date}
          </div>
        )}
      </nav>
      <main style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: spacing.lg,
      }}>
        {children}
      </main>
    </div>
  )
}
