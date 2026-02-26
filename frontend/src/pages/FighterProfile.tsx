import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Link } from 'react-router-dom'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useFighter } from '../hooks/useData'
import { loadAllMatches, loadFighter } from '../lib/data'
import type { Match } from '../types/match'
import type { Fighter } from '../types/fighter'
import StatBar from '../components/StatBar'
import InjuryBadge from '../components/InjuryBadge'
import FighterLink from '../components/FighterLink'
import NoData from '../components/NoData'

export default function FighterProfile() {
  const { id } = useParams<{ id: string }>()
  const { data: fighter, loading } = useFighter(id ?? '')
  const [fightHistory, setFightHistory] = useState<Match[]>([])
  const [rivalFighters, setRivalFighters] = useState<Record<string, Fighter>>({})

  useEffect(() => {
    if (!fighter) return

    loadAllMatches().then(matches => {
      const history = matches
        .filter(m => m.fighter1_id === fighter.id || m.fighter2_id === fighter.id)
        .sort((a, b) => b.date.localeCompare(a.date))
      setFightHistory(history)
    })

    if (fighter.rivalries.length > 0) {
      Promise.all(fighter.rivalries.map(rid => loadFighter(rid))).then(rivals => {
        const map: Record<string, Fighter> = {}
        for (const r of rivals) {
          if (r) map[r.id] = r
        }
        setRivalFighters(map)
      })
    }
  }, [fighter])

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (!fighter) return <NoData />

  const alignmentColor = fighter.alignment === 'face' ? colors.face
    : fighter.alignment === 'heel' ? colors.heel
    : colors.tweener

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md, marginBottom: spacing.xs }}>
          <h1 style={{ fontSize: fontSizes.xxl, color: colors.accent }}>{fighter.ring_name}</h1>
          <span style={{
            fontSize: fontSizes.xs,
            color: alignmentColor,
            padding: `2px ${spacing.sm}`,
            border: `1px solid ${withAlpha(alignmentColor, 0.5)}`,
            borderRadius: '3px',
            textTransform: 'uppercase',
          }}>
            {fighter.alignment}
          </span>
        </div>
        <p style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
          {fighter.real_name}{fighter.gender ? ` — ${fighter.gender.charAt(0).toUpperCase() + fighter.gender.slice(1)}` : ''}, Age {fighter.age} — {fighter.origin}
        </p>
      </div>

      <section>
        <h2 style={sectionHeader}>Physical Description</h2>
        <div style={cardStyle}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm, fontSize: fontSizes.sm }}>
            <div><span style={labelStyle}>Height:</span> {fighter.height}</div>
            <div><span style={labelStyle}>Weight:</span> {fighter.weight}</div>
            <div><span style={labelStyle}>Build:</span> {fighter.build}</div>
          </div>
          {fighter.distinguishing_features && (
            <p style={{ marginTop: spacing.sm, fontSize: fontSizes.sm, color: colors.textMuted }}>
              {fighter.distinguishing_features}
            </p>
          )}
          {fighter.ring_attire && (
            <p style={{ marginTop: spacing.xs, fontSize: fontSizes.sm, color: colors.textMuted }}>
              <span style={labelStyle}>Attire:</span> {fighter.ring_attire}
            </p>
          )}
        </div>
      </section>

      <section>
        <h2 style={sectionHeader}>Stats</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: spacing.lg }}>
          <div style={cardStyle}>
            <h3 style={subHeader}>Physical</h3>
            {Object.entries(fighter.physical_stats).map(([key, val]) => (
              <StatBar key={key} name={key} value={val} />
            ))}
          </div>
          <div style={cardStyle}>
            <h3 style={subHeader}>Combat</h3>
            {Object.entries(fighter.combat_stats).map(([key, val]) => (
              <StatBar key={key} name={key} value={val} />
            ))}
          </div>
          <div style={cardStyle}>
            <h3 style={subHeader}>Psychological</h3>
            {Object.entries(fighter.psychological_stats).map(([key, val]) => (
              <StatBar key={key} name={key} value={val} />
            ))}
          </div>
          {hasSupernaturalStats(fighter.supernatural_stats) && (
            <div style={cardStyle}>
              <h3 style={{ ...subHeader, color: colors.tweener }}>Supernatural</h3>
              {Object.entries(fighter.supernatural_stats)
                .filter(([_, val]) => val > 0)
                .map(([key, val]) => (
                  <StatBar key={key} name={key} value={val} />
                ))}
            </div>
          )}
        </div>
      </section>

      <section>
        <h2 style={sectionHeader}>Fighting Style</h2>
        <div style={cardStyle}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm, fontSize: fontSizes.sm }}>
            <div><span style={labelStyle}>Primary:</span> {fighter.fighting_style.primary_style}</div>
            <div><span style={labelStyle}>Secondary:</span> {fighter.fighting_style.secondary_style}</div>
            <div><span style={labelStyle}>Signature:</span> {fighter.fighting_style.signature_move}</div>
            <div><span style={labelStyle}>Finisher:</span> {fighter.fighting_style.finishing_move}</div>
          </div>
          {fighter.fighting_style.known_weaknesses.length > 0 && (
            <div style={{ marginTop: spacing.sm, fontSize: fontSizes.sm }}>
              <span style={labelStyle}>Weaknesses:</span>{' '}
              <span style={{ color: colors.injured }}>{fighter.fighting_style.known_weaknesses.join(', ')}</span>
            </div>
          )}
        </div>
      </section>

      <section>
        <h2 style={sectionHeader}>Backstory</h2>
        <div style={{ ...cardStyle, lineHeight: '1.8', whiteSpace: 'pre-wrap' }}>
          {fighter.backstory}
        </div>
      </section>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
        <section>
          <h2 style={sectionHeader}>Record</h2>
          <div style={cardStyle}>
            <div style={{ fontSize: fontSizes.xl, fontWeight: 'bold', marginBottom: spacing.sm }}>
              <span style={{ color: colors.win }}>{fighter.record.wins}</span>
              <span style={{ color: colors.textDim }}> - </span>
              <span style={{ color: colors.loss }}>{fighter.record.losses}</span>
              <span style={{ color: colors.textDim }}> - </span>
              <span style={{ color: colors.draw }}>{fighter.record.draws}</span>
            </div>
            <div style={{ fontSize: fontSizes.sm, color: colors.textMuted }}>
              {fighter.record.kos} KO/TKO — {fighter.record.submissions} Submissions
            </div>
          </div>
        </section>

        <section>
          <h2 style={sectionHeader}>Condition</h2>
          <div style={cardStyle}>
            {fighter.condition.health_status === 'healthy' ? (
              <span style={{ color: colors.healthy, fontWeight: 'bold' }}>Healthy</span>
            ) : (
              <div>
                <InjuryBadge daysRemaining={fighter.condition.recovery_days_remaining} />
                {fighter.condition.injuries.map((inj, i) => (
                  <p key={i} style={{ fontSize: fontSizes.sm, color: colors.textMuted, marginTop: spacing.xs }}>
                    {inj.type} ({inj.severity})
                  </p>
                ))}
              </div>
            )}
            <div style={{ marginTop: spacing.sm, fontSize: fontSizes.sm, color: colors.textMuted }}>
              Morale: {fighter.condition.morale} — Momentum: {fighter.condition.momentum}
            </div>
          </div>
        </section>
      </div>

      <section>
        <h2 style={sectionHeader}>Fight History</h2>
        {fightHistory.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {fightHistory.map(match => {
              const isWinner = match.outcome?.winner_id === fighter.id
              const isDraw = match.outcome?.is_draw
              const opponentId = match.fighter1_id === fighter.id ? match.fighter2_id : match.fighter1_id
              const opponentName = match.fighter1_id === fighter.id ? match.fighter2_name : match.fighter1_name
              const resultColor = isDraw ? colors.draw : isWinner ? colors.win : colors.loss
              const resultText = isDraw ? 'D' : isWinner ? 'W' : 'L'

              return (
                <div
                  key={match.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: spacing.sm,
                    padding: `${spacing.xs} ${spacing.md}`,
                    backgroundColor: colors.surfaceLight,
                    borderRadius: '4px',
                    borderLeft: `3px solid ${resultColor}`,
                    fontSize: fontSizes.sm,
                  }}
                >
                  <span style={{ color: colors.textDim, width: '80px' }}>{match.date}</span>
                  <span style={{ color: resultColor, fontWeight: 'bold', width: '20px' }}>{resultText}</span>
                  <span style={{ color: colors.textDim }}>vs</span>
                  <FighterLink id={opponentId} name={opponentName} />
                  {match.outcome?.method && (
                    <span style={{ color: colors.textMuted, fontSize: fontSizes.xs }}>
                      ({match.outcome.method.replace(/_/g, ' ')} R{match.outcome.round_ended})
                    </span>
                  )}
                  <Link to={`/match/${match.id}`} style={{ marginLeft: 'auto', color: colors.accent, fontSize: fontSizes.xs }}>
                    Narrative
                  </Link>
                </div>
              )
            })}
          </div>
        ) : (
          <p style={{ color: colors.textDim }}>No fight history yet</p>
        )}
      </section>

      {fighter.storyline_log.length > 0 && (
        <section>
          <h2 style={sectionHeader}>Storyline</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
            {fighter.storyline_log.map((entry, i) => (
              <div key={i} style={{
                padding: spacing.md,
                backgroundColor: colors.surfaceLight,
                borderRadius: '4px',
                borderLeft: `2px solid ${colors.accent}`,
                fontSize: fontSizes.sm,
                lineHeight: '1.7',
              }}>
                {entry}
              </div>
            ))}
          </div>
        </section>
      )}

      {fighter.rivalries.length > 0 && (
        <section>
          <h2 style={sectionHeader}>Rivalries</h2>
          <div style={{ display: 'flex', gap: spacing.md, flexWrap: 'wrap' }}>
            {fighter.rivalries.map(rid => {
              const rival = rivalFighters[rid]
              return (
                <div key={rid} style={{
                  padding: spacing.md,
                  backgroundColor: colors.surfaceLight,
                  borderRadius: '4px',
                  border: `1px solid ${withAlpha(colors.rivalry, 0.3)}`,
                }}>
                  {rival ? (
                    <FighterLink id={rid} name={rival.ring_name} record={rival.record} />
                  ) : (
                    <FighterLink id={rid} name={rid} />
                  )}
                </div>
              )
            })}
          </div>
        </section>
      )}
    </div>
  )
}

function hasSupernaturalStats(stats: { arcane_power: number; chi_mastery: number; elemental_affinity: number; dark_arts: number }): boolean {
  return stats.arcane_power > 0 || stats.chi_mastery > 0 || stats.elemental_affinity > 0 || stats.dark_arts > 0
}

const sectionHeader: React.CSSProperties = {
  fontSize: fontSizes.md,
  color: colors.text,
  marginBottom: spacing.sm,
  paddingBottom: spacing.xs,
  borderBottom: `1px solid ${colors.border}`,
}

const subHeader: React.CSSProperties = {
  fontSize: fontSizes.sm,
  color: colors.accent,
  marginBottom: spacing.sm,
}

const cardStyle: React.CSSProperties = {
  padding: spacing.md,
  backgroundColor: colors.surfaceLight,
  borderRadius: '4px',
  border: `1px solid ${colors.border}`,
}

const labelStyle: React.CSSProperties = {
  color: colors.textMuted,
}
