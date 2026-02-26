import { useState, useEffect } from 'react'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState, useAllFighters } from '../hooks/useData'
import { loadAllMatches } from '../lib/data'
import type { Fighter } from '../types/fighter'
import type { Match } from '../types/match'
import FighterLink from '../components/FighterLink'
import InjuryBadge from '../components/InjuryBadge'
import NoData from '../components/NoData'

export default function Rankings() {
  const { data: worldState, loading: wsLoading } = useWorldState()
  const { data: fighters } = useAllFighters()
  const [matches, setMatches] = useState<Match[]>([])

  useEffect(() => {
    loadAllMatches().then(setMatches)
  }, [])

  if (wsLoading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (!worldState || !fighters) return <NoData />

  const rankedFighters = worldState.rankings
    .map(id => fighters.find(f => f.id === id))
    .filter((f): f is Fighter => f !== undefined)

  return (
    <div>
      <h1 style={{ fontSize: fontSizes.xxl, color: colors.accent, marginBottom: spacing.lg }}>
        Rankings
      </h1>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '50px 1fr 100px 80px 140px',
        gap: spacing.xs,
        padding: `${spacing.sm} ${spacing.md}`,
        backgroundColor: colors.surface,
        borderBottom: `1px solid ${colors.border}`,
        fontSize: fontSizes.xs,
        color: colors.textDim,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
      }}>
        <span>#</span>
        <span>Fighter</span>
        <span>Record</span>
        <span>Streak</span>
        <span>Recent Form</span>
      </div>

      {rankedFighters.map((fighter, i) => {
        const rank = i + 1
        const isInjured = fighter.condition.health_status === 'injured'
        const streak = getStreak(matches, fighter.id)
        const recentForm = getRecentForm(matches, fighter.id, 5)

        return (
          <div
            key={fighter.id}
            style={{
              display: 'grid',
              gridTemplateColumns: '50px 1fr 100px 80px 140px',
              gap: spacing.xs,
              padding: `${spacing.sm} ${spacing.md}`,
              backgroundColor: rank % 2 === 0 ? colors.surfaceLight : 'transparent',
              borderBottom: `1px solid ${colors.border}`,
              opacity: isInjured ? 0.6 : 1,
              fontSize: fontSizes.sm,
              alignItems: 'center',
            }}
          >
            <span style={{ color: colors.accent, fontWeight: 'bold' }}>
              {rank}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
              <FighterLink id={fighter.id} name={fighter.ring_name} />
              {isInjured && <InjuryBadge daysRemaining={fighter.condition.recovery_days_remaining} />}
            </div>
            <span>
              <span style={{ color: colors.win }}>{fighter.record.wins}</span>
              <span style={{ color: colors.textDim }}>-</span>
              <span style={{ color: colors.loss }}>{fighter.record.losses}</span>
              <span style={{ color: colors.textDim }}>-</span>
              <span style={{ color: colors.draw }}>{fighter.record.draws}</span>
            </span>
            <span style={{
              color: streak.startsWith('W') ? colors.win : streak.startsWith('L') ? colors.loss : colors.textMuted,
              fontWeight: 'bold',
            }}>
              {streak}
            </span>
            <div style={{ display: 'flex', gap: '3px' }}>
              {recentForm.map((result, j) => (
                <span
                  key={j}
                  style={{
                    display: 'inline-block',
                    width: '22px',
                    height: '22px',
                    lineHeight: '22px',
                    textAlign: 'center',
                    fontSize: fontSizes.xs,
                    borderRadius: '3px',
                    fontWeight: 'bold',
                    color: colors.text,
                    backgroundColor: result === 'W' ? withAlpha(colors.win, 0.3)
                      : result === 'L' ? withAlpha(colors.loss, 0.3)
                      : withAlpha(colors.draw, 0.3),
                  }}
                >
                  {result}
                </span>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function getStreak(matches: Match[], fighterId: string): string {
  const fighterMatches = matches
    .filter(m => m.fighter1_id === fighterId || m.fighter2_id === fighterId)
    .filter(m => m.outcome)
    .sort((a, b) => b.date.localeCompare(a.date))

  if (fighterMatches.length === 0) return '-'

  let streakType = ''
  let streakCount = 0

  for (const match of fighterMatches) {
    const outcome = match.outcome!
    let result: string
    if (outcome.is_draw) result = 'D'
    else if (outcome.winner_id === fighterId) result = 'W'
    else result = 'L'

    if (streakType === '') {
      streakType = result
      streakCount = 1
    } else if (result === streakType) {
      streakCount++
    } else {
      break
    }
  }

  return `${streakType}${streakCount}`
}

function getRecentForm(matches: Match[], fighterId: string, count: number): string[] {
  return matches
    .filter(m => m.fighter1_id === fighterId || m.fighter2_id === fighterId)
    .filter(m => m.outcome)
    .sort((a, b) => b.date.localeCompare(a.date))
    .slice(0, count)
    .map(m => {
      if (m.outcome!.is_draw) return 'D'
      return m.outcome!.winner_id === fighterId ? 'W' : 'L'
    })
}
