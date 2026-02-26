import { Link } from 'react-router-dom'
import type { EventMatch } from '../types/event'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import FighterLink from './FighterLink'

interface FightCardProps {
  matches: EventMatch[]
}

function formatMethod(method: string): string {
  return method.replace(/_/g, ' ').toUpperCase()
}

export default function FightCard({ matches }: FightCardProps) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
      {matches.map((match, i) => (
        <div
          key={match.match_id || i}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: spacing.md,
            backgroundColor: colors.surfaceLight,
            borderRadius: '4px',
            border: `1px solid ${colors.border}`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, flex: 1 }}>
            <span style={{
              color: match.completed && match.winner_id === match.fighter1_id ? colors.win : colors.text,
              fontWeight: match.completed && match.winner_id === match.fighter1_id ? 'bold' : 'normal',
            }}>
              <FighterLink id={match.fighter1_id} name={match.fighter1_name} />
            </span>
            <span style={{ color: colors.textDim, fontSize: fontSizes.xs }}>vs</span>
            <span style={{
              color: match.completed && match.winner_id === match.fighter2_id ? colors.win : colors.text,
              fontWeight: match.completed && match.winner_id === match.fighter2_id ? 'bold' : 'normal',
            }}>
              <FighterLink id={match.fighter2_id} name={match.fighter2_name} />
            </span>
          </div>
          {match.completed && (
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
              {match.method && (
                <span style={{
                  fontSize: fontSizes.xs,
                  color: colors.textMuted,
                  padding: `2px ${spacing.xs}`,
                  backgroundColor: withAlpha(colors.accent, 0.1),
                  borderRadius: '3px',
                }}>
                  {formatMethod(match.method)}
                </span>
              )}
              {match.match_id && (
                <Link to={`/match/${match.match_id}`} style={{
                  fontSize: fontSizes.xs,
                  color: colors.accent,
                }}>
                  Read
                </Link>
              )}
            </div>
          )}
          {!match.completed && (
            <span style={{ fontSize: fontSizes.xs, color: colors.textDim }}>Upcoming</span>
          )}
        </div>
      ))}
    </div>
  )
}
