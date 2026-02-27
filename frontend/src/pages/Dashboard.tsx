import { useState, useEffect } from 'react'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState, useAllFighters } from '../hooks/useData'
import { loadEvent, loadMatch } from '../lib/data'
import type { Event } from '../types/event'
import type { Match } from '../types/match'
import FightCard from '../components/FightCard'
import FighterLink from '../components/FighterLink'
import FighterPortrait from '../components/FighterPortrait'
import InjuryBadge from '../components/InjuryBadge'
import NoData from '../components/NoData'

export default function Dashboard() {
  const { data: worldState, loading: wsLoading } = useWorldState()
  const { data: fighters } = useAllFighters()
  const [todaysEvent, setTodaysEvent] = useState<Event | null>(null)
  const [nextEvent, setNextEvent] = useState<Event | null>(null)
  const [recentMatches, setRecentMatches] = useState<Match[]>([])

  useEffect(() => {
    if (!worldState) return

    const loadEvents = async () => {
      const allEventIds = [...worldState.completed_events, ...worldState.upcoming_events]
      for (const eid of allEventIds) {
        const event = await loadEvent(eid)
        if (!event) continue
        if (event.date === worldState.current_date && event.completed) {
          setTodaysEvent(event)
        }
        if (!event.completed && !nextEvent) {
          setNextEvent(prev => prev ?? event)
        }
      }

      for (const eid of [...worldState.upcoming_events]) {
        const event = await loadEvent(eid)
        if (event && !event.completed) {
          setNextEvent(event)
          break
        }
      }

      const matches: Match[] = []
      for (const eid of [...worldState.completed_events].reverse().slice(0, 3)) {
        const event = await loadEvent(eid)
        if (!event) continue
        for (const em of event.matches) {
          if (em.match_id) {
            const match = await loadMatch(em.match_id)
            if (match) matches.push(match)
          }
        }
      }
      setRecentMatches(matches.slice(0, 5))
    }

    loadEvents()
  }, [worldState])

  if (wsLoading) {
    return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  }

  if (!worldState) {
    return <NoData />
  }

  const healthyCount = fighters?.filter(f => f.condition.health_status === 'healthy').length ?? 0
  const injuredFighters = fighters?.filter(f => f.condition.health_status === 'injured') ?? []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      <div>
        <h1 style={{ fontSize: fontSizes.xxl, color: colors.accent, marginBottom: spacing.xs }}>
          Dashboard
        </h1>
        <p style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
          Day {worldState.day_number} — {worldState.current_date}
        </p>
      </div>

      <section>
        <h2 style={sectionHeader}>Today's Fights</h2>
        {todaysEvent ? (
          <div>
            <p style={{ color: colors.textMuted, fontSize: fontSizes.sm, marginBottom: spacing.sm }}>
              {todaysEvent.name}
            </p>
            <FightCard matches={todaysEvent.matches} />
          </div>
        ) : (
          <p style={{ color: colors.textDim }}>No fights today</p>
        )}
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
        <section>
          <h2 style={sectionHeader}>Roster Health</h2>
          <div style={{
            padding: spacing.md,
            backgroundColor: colors.surfaceLight,
            borderRadius: '4px',
            border: `1px solid ${colors.border}`,
          }}>
            <div style={{ display: 'flex', gap: spacing.lg, marginBottom: spacing.md }}>
              <div>
                <span style={{ fontSize: fontSizes.xl, color: colors.healthy, fontWeight: 'bold' }}>
                  {healthyCount}
                </span>
                <span style={{ color: colors.textMuted, fontSize: fontSizes.xs, marginLeft: spacing.xs }}>
                  Active
                </span>
              </div>
              <div>
                <span style={{ fontSize: fontSizes.xl, color: colors.injured, fontWeight: 'bold' }}>
                  {injuredFighters.length}
                </span>
                <span style={{ color: colors.textMuted, fontSize: fontSizes.xs, marginLeft: spacing.xs }}>
                  Injured
                </span>
              </div>
            </div>
            {injuredFighters.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {injuredFighters.map(f => (
                  <div key={f.id} style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, fontSize: fontSizes.sm }}>
                    <FighterLink id={f.id} name={f.ring_name} />
                    <InjuryBadge daysRemaining={f.condition.recovery_days_remaining} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        <section>
          <h2 style={sectionHeader}>Next Event</h2>
          {nextEvent ? (
            <div style={{
              padding: spacing.md,
              backgroundColor: colors.surfaceLight,
              borderRadius: '4px',
              border: `1px solid ${colors.border}`,
            }}>
              <p style={{ color: colors.accent, fontWeight: 'bold', marginBottom: spacing.xs }}>
                {nextEvent.name}
              </p>
              <p style={{ color: colors.textMuted, fontSize: fontSizes.sm, marginBottom: spacing.md }}>
                {nextEvent.date}
              </p>
              <FightCard matches={nextEvent.matches} />
            </div>
          ) : (
            <p style={{ color: colors.textDim }}>No upcoming events</p>
          )}
        </section>
      </div>

      <section>
        <h2 style={sectionHeader}>Recent Results</h2>
        {recentMatches.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
            {recentMatches.map(match => (
              <div
                key={match.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: spacing.sm,
                  backgroundColor: colors.surfaceLight,
                  borderRadius: '4px',
                  border: `1px solid ${colors.border}`,
                  fontSize: fontSizes.sm,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                  <span style={{ color: colors.textDim, width: '80px' }}>{match.date}</span>
                  <FighterPortrait fighterId={match.fighter1_id} name={match.fighter1_name} size={24} />
                  <FighterLink id={match.fighter1_id} name={match.fighter1_name} />
                  <span style={{ color: colors.textDim }}>vs</span>
                  <FighterLink id={match.fighter2_id} name={match.fighter2_name} />
                  <FighterPortrait fighterId={match.fighter2_id} name={match.fighter2_name} size={24} />
                </div>
                {match.outcome && (
                  <span style={{
                    fontSize: fontSizes.xs,
                    color: colors.textMuted,
                    padding: `2px ${spacing.xs}`,
                    backgroundColor: withAlpha(colors.accent, 0.1),
                    borderRadius: '3px',
                  }}>
                    {match.outcome.is_draw
                      ? 'DRAW'
                      : `${match.outcome.winner_id === match.fighter1_id ? match.fighter1_name : match.fighter2_name} — ${match.outcome.method.replace(/_/g, ' ').toUpperCase()}`}
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: colors.textDim }}>No recent results</p>
        )}
      </section>
    </div>
  )
}

const sectionHeader: React.CSSProperties = {
  fontSize: fontSizes.md,
  color: colors.text,
  marginBottom: spacing.sm,
  paddingBottom: spacing.xs,
  borderBottom: `1px solid ${colors.border}`,
}
