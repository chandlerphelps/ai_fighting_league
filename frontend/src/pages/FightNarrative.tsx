import { useParams } from 'react-router-dom'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useMatch } from '../hooks/useData'
import FighterLink from '../components/FighterLink'
import StatBar from '../components/StatBar'
import NoData from '../components/NoData'

export default function FightNarrative() {
  const { id } = useParams<{ id: string }>()
  const { data: match, loading } = useMatch(id ?? '')

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (!match) return <NoData />

  const outcome = match.outcome
  const isDrawResult = outcome?.is_draw

  const winnerName = isDrawResult ? null
    : outcome?.winner_id === match.fighter1_id ? match.fighter1_name
    : match.fighter2_name

  const methodDisplay = outcome?.method?.replace(/_/g, ' ').toUpperCase() ?? ''

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      <div style={{ textAlign: 'center' }}>
        <p style={{ color: colors.textMuted, fontSize: fontSizes.sm, marginBottom: spacing.xs }}>
          {match.date}
        </p>
        <h1 style={{ fontSize: fontSizes.xxl, color: colors.text }}>
          <FighterLink id={match.fighter1_id} name={match.fighter1_name} />
          <span style={{ color: colors.textDim, margin: `0 ${spacing.md}` }}>vs</span>
          <FighterLink id={match.fighter2_id} name={match.fighter2_name} />
        </h1>
      </div>

      {outcome && (
        <div style={{
          textAlign: 'center',
          padding: spacing.lg,
          backgroundColor: isDrawResult ? withAlpha(colors.draw, 0.1) : withAlpha(colors.accent, 0.1),
          borderRadius: '4px',
          border: `1px solid ${isDrawResult ? withAlpha(colors.draw, 0.3) : withAlpha(colors.accent, 0.3)}`,
        }}>
          {isDrawResult ? (
            <div>
              <p style={{ fontSize: fontSizes.xl, color: colors.draw, fontWeight: 'bold' }}>DRAW</p>
              <p style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
                After {outcome.round_ended} rounds
              </p>
            </div>
          ) : (
            <div>
              <p style={{ fontSize: fontSizes.xl, color: colors.accent, fontWeight: 'bold' }}>
                {winnerName} wins
              </p>
              <p style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
                by {methodDisplay} — Round {outcome.round_ended}
              </p>
            </div>
          )}
        </div>
      )}

      {match.analysis && match.analysis.key_factors.length > 0 && (
        <section>
          <h2 style={sectionHeader}>Key Matchup Factors</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {match.analysis.key_factors.map((factor, i) => (
              <li key={i} style={{
                padding: `${spacing.xs} ${spacing.md}`,
                color: colors.textMuted,
                fontSize: fontSizes.sm,
                borderLeft: `2px solid ${colors.accent}`,
                marginBottom: '4px',
              }}>
                {factor}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section>
        <h2 style={sectionHeader}>Stat Comparison</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
          <StatSnapshot label={match.fighter1_name} snapshot={match.fighter1_snapshot} fighterId={match.fighter1_id} winnerId={outcome?.winner_id} />
          <StatSnapshot label={match.fighter2_name} snapshot={match.fighter2_snapshot} fighterId={match.fighter2_id} winnerId={outcome?.winner_id} />
        </div>
      </section>

      <section>
        <h2 style={sectionHeader}>Key Moments</h2>
        {match.moments && match.moments.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md, maxWidth: '750px' }}>
            {match.moments.map((moment, i) => {
              const isAttackerF1 = moment.attacker_id === match.fighter1_id
              const attackerName = isAttackerF1 ? match.fighter1_name : match.fighter2_name
              return (
                <div key={i} style={{
                  display: 'flex', alignItems: 'flex-start', gap: spacing.md,
                  padding: spacing.md,
                  backgroundColor: colors.surfaceLight,
                  borderRadius: '4px',
                  border: `1px solid ${colors.border}`,
                  borderLeft: `3px solid ${colors.accent}`,
                }}>
                  <span style={{
                    color: colors.accentDim, fontSize: fontSizes.lg,
                    fontWeight: 'bold', minWidth: '24px',
                  }}>
                    {moment.moment_number}
                  </span>
                  <p style={{ color: colors.text, fontSize: fontSizes.md, margin: 0, lineHeight: '1.6' }}>
                    {moment.description.split(attackerName).map((part, j, arr) =>
                      j < arr.length - 1 ? (
                        <span key={j}>
                          {part}
                          <span style={{ color: colors.accent, fontWeight: 'bold' }}>{attackerName}</span>
                        </span>
                      ) : part
                    )}
                  </p>
                </div>
              )
            })}
          </div>
        ) : match.narrative ? (
          <div style={{
            padding: spacing.lg,
            backgroundColor: colors.surfaceLight,
            borderRadius: '4px',
            border: `1px solid ${colors.border}`,
            lineHeight: '1.9',
            fontSize: fontSizes.md,
            maxWidth: '750px',
            whiteSpace: 'pre-wrap',
          }}>
            {match.narrative}
          </div>
        ) : (
          <p style={{ color: colors.textMuted }}>No fight data available.</p>
        )}
      </section>

      {match.post_fight_updates && Object.keys(match.post_fight_updates).length > 0 && (
        <section>
          <h2 style={sectionHeader}>Post-Fight Updates</h2>
          <div style={{
            padding: spacing.md,
            backgroundColor: colors.surfaceLight,
            borderRadius: '4px',
            border: `1px solid ${colors.border}`,
            fontSize: fontSizes.sm,
            whiteSpace: 'pre-wrap',
          }}>
            {JSON.stringify(match.post_fight_updates, null, 2)}
          </div>
        </section>
      )}
    </div>
  )
}

function StatSnapshot({ label, snapshot, fighterId, winnerId }: {
  label: string
  snapshot: Record<string, unknown>
  fighterId: string
  winnerId?: string
}) {
  const isWinner = winnerId === fighterId
  const stats = snapshot.stats as Record<string, number> | undefined

  return (
    <div style={{
      padding: spacing.md,
      backgroundColor: colors.surfaceLight,
      borderRadius: '4px',
      border: `1px solid ${isWinner ? withAlpha(colors.accent, 0.5) : colors.border}`,
    }}>
      <h3 style={{
        fontSize: fontSizes.sm,
        color: isWinner ? colors.accent : colors.text,
        marginBottom: spacing.sm,
      }}>
        {label} {isWinner && '(W)'}
      </h3>
      {stats && Object.entries(stats)
        .filter(([k, v]) => k !== 'supernatural' || v > 0)
        .map(([k, v]) => (
          <StatBar key={k} name={k} value={v} />
        ))}
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
