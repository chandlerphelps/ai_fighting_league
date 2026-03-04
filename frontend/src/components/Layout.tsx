import { type ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState } from '../hooks/useData'
import TierBadge from './TierBadge'
import type { MatchResult } from '../types/world_state'

interface LayoutProps {
  children: ReactNode
}

const METHOD_COLORS: Record<string, string> = {
  ko: colors.ko,
  tko: colors.ko,
  submission: colors.submission,
  decision: colors.decision,
}

function TickerItem({ match }: { match: MatchResult }) {
  const winnerName = match.winner_id === match.fighter1_id ? match.fighter1_name : match.fighter2_name
  const loserName = match.winner_id === match.fighter1_id ? match.fighter2_name : match.fighter1_name
  const methodCol = METHOD_COLORS[match.method] || colors.textMuted

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: spacing.xs,
      whiteSpace: 'nowrap',
      padding: `0 ${spacing.md}`,
      fontSize: fontSizes.xs,
      borderRight: `1px solid ${colors.border}`,
    }}>
      <TierBadge tier={match.tier} size={12} />
      <span style={{ color: colors.text, fontWeight: 'bold' }}>{winnerName}</span>
      <span style={{ color: colors.textDim }}>def.</span>
      <span style={{ color: colors.textMuted }}>{loserName}</span>
      <span style={{ color: methodCol, fontWeight: 'bold' }}>
        {match.method.toUpperCase()} R{match.round_ended}
      </span>
    </span>
  )
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { data: worldState } = useWorldState()

  const navItems = [
    { path: '/', label: 'Home' },
    { path: '/rankings', label: 'Rankings' },
    { path: '/roster', label: 'Roster' },
  ]

  const recentMatches = worldState?.recent_matches?.slice(0, 10) || []

  return (
    <div style={{ minHeight: '100vh', fontFamily: fonts.body }}>
      {recentMatches.length > 0 && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          height: '28px',
          backgroundColor: colors.background,
          borderBottom: `1px solid ${colors.border}`,
          overflowX: 'auto',
          overflowY: 'hidden',
          scrollbarWidth: 'none',
        }}>
          <span style={{
            padding: `0 ${spacing.sm}`,
            fontSize: fontSizes.xs,
            color: colors.accent,
            fontWeight: 'bold',
            whiteSpace: 'nowrap',
            borderRight: `1px solid ${colors.border}`,
          }}>
            RESULTS
          </span>
          {recentMatches.map((m, i) => (
            <TickerItem key={`${m.fighter1_id}-${m.fighter2_id}-${i}`} match={m} />
          ))}
        </div>
      )}
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
            display: 'flex',
            alignItems: 'center',
            gap: spacing.sm,
            fontSize: fontSizes.lg,
            fontWeight: 'bold',
            color: colors.accent,
            letterSpacing: '0.05em',
          }}>
            <img src="/logo_apex_mid.png" alt="AFL" style={{ height: '32px', objectFit: 'contain' }} />
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
            S{worldState.season_number} — {worldState.current_date || `M${worldState.season_month} D${worldState.season_day_in_month}`}
          </div>
        )}
      </nav>
      <main style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: spacing.lg,
      }}>
        {children}
      </main>
    </div>
  )
}
