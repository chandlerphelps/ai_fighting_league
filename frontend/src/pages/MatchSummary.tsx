import { useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState, useFighter } from '../hooks/useData'
import FighterPortrait from '../components/FighterPortrait'
import { getStatColor } from '../components/StatBar'
import type { MatchResult } from '../types/world_state'
import type { Fighter } from '../types/fighter'

const METHOD_COLORS: Record<string, string> = {
  ko: colors.ko,
  tko: colors.ko,
  submission: colors.submission,
  decision: colors.decision,
}

const METHOD_LABELS: Record<string, string> = {
  ko: 'Knockout',
  tko: 'Technical Knockout',
  submission: 'Submission',
  decision: 'Decision',
}

const TIER_LOGOS: Record<string, string> = {
  apex: '/logo_apex_mid.png',
  contender: '/logo_contender_mid.png',
  underground: '/logo_underground_mid.png',
}

const TIER_LABELS: Record<string, string> = {
  apex: 'Apex',
  contender: 'Contender',
  underground: 'Underground',
}

const STAT_NAMES = ['power', 'speed', 'technique', 'toughness', 'supernatural', 'guile'] as const

function formatTime(time24: string): string {
  if (!time24) return ''
  const [hStr, mStr] = time24.split(':')
  let h = parseInt(hStr || '0')
  const m = mStr || '00'
  const period = h >= 12 ? 'PM' : 'AM'
  if (h === 0) h = 12
  else if (h > 12) h -= 12
  return `${h}:${m} ${period}`
}

function formatDate(dateStr: string): string {
  const MONTHS = ['', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December']
  if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
    const parts = dateStr.split('-').map(Number)
    return `${MONTHS[parts[1] ?? 0]} ${parts[2]}, ${parts[0]}`
  }
  return dateStr
}

function formatRecord(f: Fighter): string {
  const r = f.record
  return `${r.wins}-${r.losses}-${r.draws}`
}

export default function MatchSummary() {
  const { matchKey } = useParams<{ matchKey: string }>()
  const { data: ws, loading: wsLoading } = useWorldState()

  const match = useMemo<MatchResult | null>(() => {
    if (!ws?.recent_matches || !matchKey) return null
    return ws.recent_matches.find(m =>
      `${m.fighter1_id}_${m.fighter2_id}_${m.date}` === matchKey
    ) || null
  }, [ws?.recent_matches, matchKey])

  const { data: fighter1 } = useFighter(match?.fighter1_id || '')
  const { data: fighter2 } = useFighter(match?.fighter2_id || '')

  if (wsLoading) {
    return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  }

  if (!match) {
    return (
      <div style={{ color: colors.textMuted, padding: spacing.lg, textAlign: 'center' }}>
        <div style={{ fontSize: fontSizes.lg, marginBottom: spacing.md }}>Match not found</div>
        <Link to="/" style={{ color: colors.accent }}>Back to Dashboard</Link>
      </div>
    )
  }

  const isF1Winner = match.winner_id === match.fighter1_id
  const methodColor = METHOD_COLORS[match.method] || colors.textMuted
  const methodLabel = METHOD_LABELS[match.method] || match.method.toUpperCase()

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <FightHeader
        match={match}
        fighter1={fighter1}
        fighter2={fighter2}
        isF1Winner={isF1Winner}
        methodColor={methodColor}
        methodLabel={methodLabel}
      />

      <TabBar />

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 320px',
        gap: spacing.lg,
        marginTop: spacing.lg,
      }}>
        <LeftColumn
          match={match}
          isF1Winner={isF1Winner}
        />
        <RightColumn
          match={match}
          fighter1={fighter1}
          fighter2={fighter2}
          isF1Winner={isF1Winner}
        />
      </div>
    </div>
  )
}

function FightHeader({ match, fighter1, fighter2, isF1Winner, methodColor, methodLabel }: {
  match: MatchResult
  fighter1: Fighter | null
  fighter2: Fighter | null
  isF1Winner: boolean
  methodColor: string
  methodLabel: string
}) {
  return (
    <div style={{
      backgroundColor: colors.surface,
      borderRadius: '8px',
      border: match.is_title_fight
        ? `2px solid ${colors.accent}`
        : `1px solid ${colors.border}`,
      overflow: 'hidden',
    }}>
      {match.is_title_fight && (
        <div style={{
          height: '3px',
          background: `linear-gradient(90deg, ${colors.accentDim}, ${colors.accent}, ${colors.accentBright}, ${colors.accent}, ${colors.accentDim})`,
        }} />
      )}

      <div style={{ padding: spacing.md, paddingBottom: 0 }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
            fontSize: fontSizes.xs,
            color: match.is_title_fight ? colors.accent : colors.textMuted,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontWeight: 'bold',
          }}>
            {TIER_LOGOS[match.tier] && (
              <img src={TIER_LOGOS[match.tier]} alt={match.tier} style={{ height: '20px', objectFit: 'contain' }} />
            )}
            {match.is_title_fight ? 'Title Fight' : TIER_LABELS[match.tier] || match.tier}
          </div>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textDim,
          }}>
            {formatDate(match.date)}
            {match.start_time && ` — ${formatTime(match.start_time)}`}
          </div>
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: `${spacing.lg} ${spacing.xl}`,
        gap: spacing.xl,
      }}>
        <FighterSide
          fighter={fighter1}
          name={match.fighter1_name}
          id={match.fighter1_id}
          isWinner={isF1Winner}
          side="left"
        />

        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: spacing.sm,
          flexShrink: 0,
        }}>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textDim,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
          }}>
            FINAL
          </div>
          <div style={{
            padding: `${spacing.sm} ${spacing.lg}`,
            backgroundColor: withAlpha(methodColor, 0.15),
            border: `2px solid ${withAlpha(methodColor, 0.4)}`,
            borderRadius: '6px',
            textAlign: 'center',
          }}>
            <div style={{
              fontSize: fontSizes.lg,
              fontWeight: 'bold',
              color: methodColor,
            }}>
              {methodLabel}
            </div>
            <div style={{
              fontSize: fontSizes.sm,
              color: colors.textMuted,
              marginTop: '2px',
            }}>
              Round {match.round_ended}
            </div>
          </div>
        </div>

        <FighterSide
          fighter={fighter2}
          name={match.fighter2_name}
          id={match.fighter2_id}
          isWinner={!isF1Winner}
          side="right"
        />
      </div>
    </div>
  )
}

function FighterSide({ fighter, name, id, isWinner, side }: {
  fighter: Fighter | null
  name: string
  id: string
  isWinner: boolean
  side: 'left' | 'right'
}) {
  const align = side === 'left' ? 'right' : 'left'
  const flexDir = side === 'left' ? 'row' : 'row-reverse'

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      alignItems: 'center',
      gap: spacing.md,
      flexDirection: flexDir,
    }}>
      <FighterPortrait fighterId={id} name={name} size={100} />
      <div style={{ textAlign: align, flex: 1, minWidth: 0 }}>
        <Link to={`/fighter/${id}`} style={{
          fontSize: fontSizes.xxl,
          fontWeight: 'bold',
          color: isWinner ? colors.win : colors.loss,
          textDecoration: 'none',
        }}>
          {name}
        </Link>
        {fighter && (
          <div style={{ fontSize: fontSizes.xs, color: colors.textDim, marginTop: '2px' }}>
            {formatRecord(fighter)}
          </div>
        )}
        <div style={{
          fontSize: fontSizes.xs,
          color: isWinner ? colors.win : colors.textDim,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginTop: spacing.xs,
          fontWeight: 'bold',
        }}>
          {isWinner ? 'WINNER' : ''}
        </div>
      </div>
    </div>
  )
}

function TabBar() {
  return (
    <div style={{
      display: 'flex',
      gap: 0,
      marginTop: spacing.md,
      borderBottom: `2px solid ${colors.border}`,
    }}>
      <div style={{
        padding: `${spacing.sm} ${spacing.lg}`,
        fontSize: fontSizes.sm,
        fontWeight: 'bold',
        color: colors.accent,
        borderBottom: `2px solid ${colors.accent}`,
        marginBottom: '-2px',
        cursor: 'default',
      }}>
        Summary
      </div>
      <div style={{
        padding: `${spacing.sm} ${spacing.lg}`,
        fontSize: fontSizes.sm,
        color: colors.textDim,
        cursor: 'not-allowed',
      }}>
        Replay
      </div>
    </div>
  )
}

function LeftColumn({ match, isF1Winner }: {
  match: MatchResult
  isF1Winner: boolean
}) {
  const winnerName = isF1Winner ? match.fighter1_name : match.fighter2_name
  const loserName = isF1Winner ? match.fighter2_name : match.fighter1_name

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
      <RoundByRound match={match} />

      <KeyMomentsPlaceholder match={match} />

      <div style={{
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
        padding: spacing.md,
      }}>
        <SectionLabel>Result</SectionLabel>
        <div style={{ fontSize: fontSizes.sm, color: colors.text, lineHeight: 1.6 }}>
          <span style={{ fontWeight: 'bold', color: colors.win }}>{winnerName}</span>
          <span style={{ color: colors.textMuted }}> defeated </span>
          <span style={{ color: colors.loss }}>{loserName}</span>
          <span style={{ color: colors.textMuted }}> via </span>
          <span style={{
            color: METHOD_COLORS[match.method] || colors.textMuted,
            fontWeight: 'bold',
          }}>
            {(METHOD_LABELS[match.method] || match.method).toLowerCase()}
          </span>
          <span style={{ color: colors.textMuted }}> in round {match.round_ended}.</span>
        </div>
      </div>
    </div>
  )
}

function RoundByRound({ match }: { match: MatchResult }) {
  const totalRounds = match.method === 'decision' ? 3 : match.round_ended
  const isF1Winner = match.winner_id === match.fighter1_id

  return (
    <div style={{
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
      padding: spacing.md,
    }}>
      <SectionLabel>Round by Round</SectionLabel>
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        {Array.from({ length: totalRounds }, (_, i) => {
          const round = i + 1
          const isLastRound = round === match.round_ended
          const isFinalFinish = isLastRound && match.method !== 'decision'

          const f1Pct = isFinalFinish
            ? (isF1Winner ? 60 + Math.random() * 30 : 5 + Math.random() * 15)
            : 40 + Math.random() * 50
          const f2Pct = isFinalFinish
            ? (!isF1Winner ? 60 + Math.random() * 30 : 5 + Math.random() * 15)
            : 40 + Math.random() * 50

          return (
            <div key={round}>
              <div style={{
                fontSize: fontSizes.xs,
                color: colors.textMuted,
                marginBottom: spacing.xs,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}>
                Round {round}
                {isFinalFinish && (
                  <span style={{
                    marginLeft: spacing.sm,
                    color: METHOD_COLORS[match.method] || colors.textMuted,
                    fontWeight: 'bold',
                  }}>
                    {match.method.toUpperCase()}
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: spacing.sm, alignItems: 'center' }}>
                <span style={{
                  fontSize: fontSizes.xs,
                  color: colors.textDim,
                  width: '80px',
                  textAlign: 'right',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {match.fighter1_name}
                </span>
                <HpBar pct={f1Pct} />
                <HpBar pct={f2Pct} reverse />
                <span style={{
                  fontSize: fontSizes.xs,
                  color: colors.textDim,
                  width: '80px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap',
                }}>
                  {match.fighter2_name}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function HpBar({ pct, reverse }: { pct: number; reverse?: boolean }) {
  const barColor = pct > 60 ? colors.win : pct > 30 ? colors.rivalry : colors.loss
  return (
    <div style={{
      flex: 1,
      height: '14px',
      backgroundColor: withAlpha(colors.border, 0.5),
      borderRadius: '2px',
      overflow: 'hidden',
      display: 'flex',
      justifyContent: reverse ? 'flex-end' : 'flex-start',
    }}>
      <div style={{
        width: `${Math.max(pct, 3)}%`,
        height: '100%',
        backgroundColor: withAlpha(barColor, 0.7),
        borderRadius: '2px',
        transition: 'width 0.3s ease',
      }} />
    </div>
  )
}

function KeyMomentsPlaceholder({ match }: { match: MatchResult }) {
  const isF1Winner = match.winner_id === match.fighter1_id
  const winnerName = isF1Winner ? match.fighter1_name : match.fighter2_name
  const loserName = isF1Winner ? match.fighter2_name : match.fighter1_name
  const methodColor = METHOD_COLORS[match.method] || colors.textMuted

  const moments = useMemo(() => {
    const items: { round: number; text: string; highlight?: boolean; color?: string }[] = []

    items.push({
      round: 1,
      text: `${match.fighter1_name} and ${match.fighter2_name} touch gloves. The fight begins.`,
    })

    if (match.round_ended > 1) {
      items.push({
        round: 1,
        text: `Both fighters trade blows through round 1. Competitive opening round.`,
      })
    }

    if (match.round_ended > 2) {
      items.push({
        round: 2,
        text: `The pace intensifies in round 2. ${winnerName} starts finding range.`,
      })
    }

    if (match.method === 'decision') {
      items.push({
        round: 3,
        text: `After three rounds, the judges score it in favor of ${winnerName}.`,
        highlight: true,
        color: methodColor,
      })
    } else {
      items.push({
        round: match.round_ended,
        text: `${winnerName} finishes ${loserName} with a ${match.method.toUpperCase()} in round ${match.round_ended}!`,
        highlight: true,
        color: methodColor,
      })
    }

    return items
  }, [match, winnerName, loserName, methodColor])

  return (
    <div style={{
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
      padding: spacing.md,
    }}>
      <SectionLabel>Key Moments</SectionLabel>

      <div style={{
        padding: `${spacing.sm} ${spacing.md}`,
        backgroundColor: withAlpha(colors.accent, 0.08),
        borderRadius: '4px',
        border: `1px dashed ${withAlpha(colors.accent, 0.3)}`,
        marginBottom: spacing.md,
        fontSize: fontSizes.xs,
        color: colors.textDim,
        textAlign: 'center',
      }}>
        Snapshot images coming soon
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {moments.map((m, i) => (
          <div key={i} style={{
            display: 'flex',
            gap: spacing.md,
            padding: `${spacing.sm} 0`,
            borderBottom: i < moments.length - 1 ? `1px solid ${colors.border}` : 'none',
          }}>
            <div style={{
              width: '50px',
              flexShrink: 0,
              fontSize: fontSizes.xs,
              color: colors.textDim,
              textTransform: 'uppercase',
              paddingTop: '2px',
            }}>
              R{m.round}
            </div>
            <div style={{
              borderLeft: `3px solid ${m.color || colors.border}`,
              paddingLeft: spacing.sm,
              fontSize: fontSizes.sm,
              color: m.highlight ? colors.text : colors.textMuted,
              fontWeight: m.highlight ? 'bold' : 'normal',
              lineHeight: 1.5,
            }}>
              {m.text}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function RightColumn({ match, fighter1, fighter2, isF1Winner }: {
  match: MatchResult
  fighter1: Fighter | null
  fighter2: Fighter | null
  isF1Winner: boolean
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
      <FighterComparison
        match={match}
        fighter1={fighter1}
        fighter2={fighter2}
      />

      <PerformanceSummary match={match} isF1Winner={isF1Winner} />

      {fighter1?.moves && fighter2?.moves && (
        <MovesSummary fighter1={fighter1} fighter2={fighter2} match={match} />
      )}
    </div>
  )
}

function FighterComparison({ match, fighter1, fighter2 }: {
  match: MatchResult
  fighter1: Fighter | null
  fighter2: Fighter | null
}) {
  const f1Stats = fighter1?.stats
  const f2Stats = fighter2?.stats

  if (!f1Stats || !f2Stats) return null

  return (
    <div style={{
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
      padding: spacing.md,
    }}>
      <SectionLabel>Stats Comparison</SectionLabel>

      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        marginBottom: spacing.md,
        fontSize: fontSizes.xs,
        color: colors.textMuted,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
      }}>
        <span>{match.fighter1_name}</span>
        <span>{match.fighter2_name}</span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        {STAT_NAMES.map(stat => {
          const v1 = f1Stats[stat]
          const v2 = f2Stats[stat]
          if (v1 === 0 && v2 === 0) return null
          return (
            <ComparisonBar
              key={stat}
              label={stat}
              value1={v1}
              value2={v2}
            />
          )
        })}
      </div>
    </div>
  )
}

function ComparisonBar({ label, value1, value2 }: {
  label: string
  value1: number
  value2: number
}) {
  const c1 = getStatColor(value1)
  const c2 = getStatColor(value2)
  const over1 = value1 > 100
  const over2 = value2 > 100
  const overflow1 = over1 ? value1 - 100 : 0
  const overflow2 = over2 ? value2 - 100 : 0

  return (
    <div>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '3px',
      }}>
        <span style={{
          fontSize: fontSizes.xs,
          color: c1,
          fontWeight: 'bold',
          ...(over1 ? { textShadow: `0 0 4px ${withAlpha(colors.statOverclock, 0.7)}` } : {}),
        }}>{value1}</span>
        <span style={{
          fontSize: fontSizes.xs,
          color: colors.textDim,
          textTransform: 'capitalize',
        }}>
          {label}
        </span>
        <span style={{
          fontSize: fontSizes.xs,
          color: c2,
          fontWeight: 'bold',
          ...(over2 ? { textShadow: `0 0 4px ${withAlpha(colors.statOverclock, 0.7)}` } : {}),
        }}>{value2}</span>
      </div>
      <div style={{ display: 'flex', gap: '2px', height: '8px' }}>
        <div style={{
          flex: 1,
          position: 'relative',
        }}>
          <div style={{
            width: '100%',
            height: '100%',
            backgroundColor: withAlpha(colors.border, 0.5),
            borderRadius: '2px',
            overflow: 'hidden',
            display: 'flex',
            justifyContent: 'flex-end',
          }}>
            <div style={{
              width: over1 ? '100%' : `${value1}%`,
              height: '100%',
              backgroundColor: withAlpha(over1 ? colors.statHigh : c1, 0.6),
              borderRadius: '2px',
            }} />
          </div>
          {over1 && (
            <div style={{
              position: 'absolute',
              top: -1,
              bottom: -1,
              left: `-${overflow1 * 0.6}%`,
              width: `${overflow1 * 0.6}%`,
              minWidth: '3px',
              background: `linear-gradient(270deg, ${colors.statOverclock}, ${withAlpha(colors.statOverclock, 0.4)})`,
              borderRadius: '2px 0 0 2px',
              boxShadow: `0 0 6px ${withAlpha(colors.statOverclock, 0.5)}`,
            }} />
          )}
        </div>
        <div style={{
          flex: 1,
          position: 'relative',
        }}>
          <div style={{
            width: '100%',
            height: '100%',
            backgroundColor: withAlpha(colors.border, 0.5),
            borderRadius: '2px',
            overflow: 'hidden',
          }}>
            <div style={{
              width: over2 ? '100%' : `${value2}%`,
              height: '100%',
              backgroundColor: withAlpha(over2 ? colors.statHigh : c2, 0.6),
              borderRadius: '2px',
            }} />
          </div>
          {over2 && (
            <div style={{
              position: 'absolute',
              top: -1,
              bottom: -1,
              right: `-${overflow2 * 0.6}%`,
              width: `${overflow2 * 0.6}%`,
              minWidth: '3px',
              background: `linear-gradient(90deg, ${colors.statOverclock}, ${withAlpha(colors.statOverclock, 0.4)})`,
              borderRadius: '0 2px 2px 0',
              boxShadow: `0 0 6px ${withAlpha(colors.statOverclock, 0.5)}`,
            }} />
          )}
        </div>
      </div>
    </div>
  )
}

function PerformanceSummary({ match, isF1Winner }: {
  match: MatchResult
  isF1Winner: boolean
}) {
  const winnerName = isF1Winner ? match.fighter1_name : match.fighter2_name

  return (
    <div style={{
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
      padding: spacing.md,
    }}>
      <SectionLabel>Performance</SectionLabel>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        <PerformanceRow
          label="Winner"
          value={winnerName}
          color={colors.win}
        />
        <PerformanceRow
          label="Method"
          value={`${(METHOD_LABELS[match.method] || match.method)} R${match.round_ended}`}
          color={METHOD_COLORS[match.method] || colors.textMuted}
        />
        {match.is_title_fight && (
          <PerformanceRow
            label="Stakes"
            value="Title Fight"
            color={colors.accent}
          />
        )}
      </div>
    </div>
  )
}

function PerformanceRow({ label, value, color }: {
  label: string
  value: string
  color: string
}) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: `${spacing.xs} 0`,
      borderBottom: `1px solid ${colors.border}`,
    }}>
      <span style={{ fontSize: fontSizes.xs, color: colors.textDim, textTransform: 'uppercase' }}>
        {label}
      </span>
      <span style={{ fontSize: fontSizes.sm, color, fontWeight: 'bold' }}>
        {value}
      </span>
    </div>
  )
}

function MovesSummary({ fighter1, fighter2, match }: {
  fighter1: Fighter
  fighter2: Fighter
  match: MatchResult
}) {
  return (
    <div style={{
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
      padding: spacing.md,
    }}>
      <SectionLabel>Signature Moves</SectionLabel>

      <div style={{ marginBottom: spacing.md }}>
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.xs,
        }}>
          {match.fighter1_name}
        </div>
        {fighter1.moves?.slice(0, 3).map((move, i) => (
          <div key={i} style={{
            fontSize: fontSizes.xs,
            color: colors.text,
            padding: `2px 0`,
            borderLeft: `2px solid ${colors.accent}`,
            paddingLeft: spacing.sm,
            marginBottom: '2px',
          }}>
            {move.name}
          </div>
        ))}
      </div>

      <div>
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.xs,
        }}>
          {match.fighter2_name}
        </div>
        {fighter2.moves?.slice(0, 3).map((move, i) => (
          <div key={i} style={{
            fontSize: fontSizes.xs,
            color: colors.text,
            padding: `2px 0`,
            borderLeft: `2px solid ${colors.accent}`,
            paddingLeft: spacing.sm,
            marginBottom: '2px',
          }}>
            {move.name}
          </div>
        ))}
      </div>
    </div>
  )
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontSize: fontSizes.sm,
      color: colors.accent,
      fontWeight: 'bold',
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
      marginBottom: spacing.md,
      paddingBottom: spacing.xs,
      borderBottom: `2px solid ${colors.accent}`,
    }}>
      {children}
    </div>
  )
}
