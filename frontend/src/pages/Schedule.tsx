import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useAllEvents } from '../hooks/useData'
import FightCard from '../components/FightCard'
import NoData from '../components/NoData'

export default function Schedule() {
  const { data: events, loading } = useAllEvents()

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (!events) return <NoData />

  const upcoming = events
    .filter(e => !e.completed)
    .sort((a, b) => a.date.localeCompare(b.date))

  const past = events
    .filter(e => e.completed)
    .sort((a, b) => b.date.localeCompare(a.date))

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      <h1 style={{ fontSize: fontSizes.xxl, color: colors.accent }}>
        Schedule
      </h1>

      <section>
        <h2 style={sectionHeader}>Upcoming Events</h2>
        {upcoming.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
            {upcoming.map(event => (
              <div key={event.id} style={{
                padding: spacing.md,
                backgroundColor: colors.surfaceLight,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm }}>
                  <span style={{ color: colors.accent, fontWeight: 'bold' }}>{event.name}</span>
                  <span style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>{event.date}</span>
                </div>
                <FightCard matches={event.matches} />
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: colors.textDim }}>No upcoming events scheduled</p>
        )}
      </section>

      <section>
        <h2 style={sectionHeader}>Past Events</h2>
        {past.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
            {past.map(event => (
              <div key={event.id} style={{
                padding: spacing.md,
                backgroundColor: colors.surfaceLight,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.sm }}>
                  <span style={{ color: colors.text, fontWeight: 'bold' }}>{event.name}</span>
                  <span style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>{event.date}</span>
                </div>
                <FightCard matches={event.matches} />
                {event.summary && (
                  <p style={{
                    marginTop: spacing.sm,
                    fontSize: fontSizes.xs,
                    color: colors.textDim,
                    padding: `${spacing.xs} ${spacing.sm}`,
                    backgroundColor: withAlpha(colors.surface, 0.5),
                    borderRadius: '3px',
                  }}>
                    {event.summary}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p style={{ color: colors.textDim }}>No past events yet</p>
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
