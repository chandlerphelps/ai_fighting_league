import { useState, useCallback, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState } from '../hooks/useData'
import TierBadge from '../components/TierBadge'
import { simulateDay } from '../lib/data'
import type { DaySimulationResult, MatchResult, ScheduledFight } from '../types/world_state'

const TIER_LABELS: Record<string, string> = {
  apex: 'Apex',
  contender: 'Contender',
  underground: 'Underground',
}

const TIER_LOGOS: Record<string, string> = {
  apex: '/logo_apex_mid.png',
  contender: '/logo_contender_mid.png',
  underground: '/logo_underground_mid.png',
}

const TIER_ORDER = ['apex', 'contender', 'underground']

const METHOD_COLORS: Record<string, string> = {
  ko: colors.ko,
  tko: colors.ko,
  submission: colors.submission,
  decision: colors.decision,
}

function methodColor(method: string): string {
  return METHOD_COLORS[method] || colors.textMuted
}

const MONTH_NAMES = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

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

function parseDateKey(d: string): number {
  if (d.match(/^\d{4}-\d{2}-\d{2}$/)) {
    return parseInt(d.replace(/-/g, ''))
  }
  const m = d.match(/^s(\d+)m(\d+)(?:d(\d+))?$/)
  if (!m) return 0
  const season = parseInt(m[1] || '0')
  const month = parseInt(m[2] || '0')
  const day = m[3] ? parseInt(m[3]) : 0
  return season * 10000 + month * 100 + day
}

function formatDateLabel(d: string): string {
  if (d.match(/^\d{4}-\d{2}-\d{2}$/)) {
    const parts = d.split('-').map(Number)
    return `${MONTH_NAMES[parts[1] ?? 0]} ${parts[2]}, ${parts[0]}`
  }
  const m = d.match(/^s(\d+)m(\d+)(?:d(\d+))?$/)
  if (!m) return d
  const season = m[1] ?? ''
  const month = m[2] ?? ''
  const day = m[3]
  if (day) return `Season ${season} — Month ${month}, Day ${day}`
  return `Season ${season} — Month ${month}`
}

function formatCurrentDate(dateStr: string): string {
  if (dateStr && dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
    const parts = dateStr.split('-').map(Number)
    return `${MONTH_NAMES[parts[1] ?? 0]} ${parts[2]}, ${parts[0]}`
  }
  return dateStr
}

export default function Home() {
  const { data: ws, loading, error, refresh } = useWorldState()
  const [simulating, setSimulating] = useState(false)
  const [lastResult, setLastResult] = useState<DaySimulationResult | null>(null)
  const [multiDayCount, setMultiDayCount] = useState(7)
  const [multiSimulating, setMultiSimulating] = useState(false)

  const handleSimulateDay = useCallback(async () => {
    setSimulating(true)
    const result = await simulateDay()
    setLastResult(result)
    refresh()
    setSimulating(false)
  }, [refresh])

  const handleSimulateMultiple = useCallback(async () => {
    setMultiSimulating(true)
    let lastRes: DaySimulationResult | null = null
    for (let i = 0; i < multiDayCount; i++) {
      lastRes = await simulateDay()
      if (!lastRes) break
    }
    setLastResult(lastRes)
    refresh()
    setMultiSimulating(false)
  }, [multiDayCount, refresh])

  const matchesByDay = useMemo(() => {
    if (!ws?.recent_matches) return []
    const grouped: Record<string, MatchResult[]> = {}
    for (const m of ws.recent_matches) {
      const key = m.date || 'unknown'
      if (!grouped[key]) grouped[key] = []
      grouped[key].push(m)
    }
    return Object.entries(grouped)
      .sort(([a], [b]) => parseDateKey(b) - parseDateKey(a))
      .map(([date, matches]) => ({
        date,
        label: formatDateLabel(date),
        matches: [...matches].sort(
          (a, b) => TIER_ORDER.indexOf(a.tier) - TIER_ORDER.indexOf(b.tier)
            || (a.start_time || '').localeCompare(b.start_time || '')
        ),
      }))
  }, [ws?.recent_matches])

  const heroFight = useMemo(() => {
    if (!ws?.recent_matches?.length) return null
    const titleFight = ws.recent_matches.find(m => m.is_title_fight)
    if (titleFight) return titleFight
    const champFight = ws.recent_matches.find(m => m.tier === 'apex')
    if (champFight) return champFight
    return ws.recent_matches[0]
  }, [ws?.recent_matches])

  const headlines = useMemo(() => {
    if (!ws) return []
    const items: { text: string; color: string }[] = []
    const titleFights = ws.recent_matches?.filter(m => m.is_title_fight) || []
    for (const tf of titleFights) {
      const winnerName = tf.winner_id === tf.fighter1_id ? tf.fighter1_name : tf.fighter2_name
      items.push({
        text: `${winnerName} wins title fight`,
        color: colors.accent,
      })
    }
    const kos = ws.recent_matches?.filter(m => m.method === 'ko' || m.method === 'tko') || []
    for (const ko of kos.slice(0, 3)) {
      const winnerName = ko.winner_id === ko.fighter1_id ? ko.fighter1_name : ko.fighter2_name
      const loserName = ko.winner_id === ko.fighter1_id ? ko.fighter2_name : ko.fighter1_name
      items.push({
        text: `${winnerName} stops ${loserName} with ${ko.method.toUpperCase()} in round ${ko.round_ended}`,
        color: colors.ko,
      })
    }
    const subs = ws.recent_matches?.filter(m => m.method === 'submission') || []
    for (const sub of subs.slice(0, 2)) {
      const winnerName = sub.winner_id === sub.fighter1_id ? sub.fighter1_name : sub.fighter2_name
      items.push({
        text: `${winnerName} earns submission victory`,
        color: colors.submission,
      })
    }
    const hlMonth = ws.current_date ? parseInt(ws.current_date.split('-')[1] || '0') : ws.season_month
    if (hlMonth === 6 || ws.promotion_fights?.length) {
      items.push({
        text: 'Promotion month — relegation matchups announced',
        color: colors.rivalry,
      })
    }
    if (ws.season_champions?.length) {
      const lastChamp = ws.season_champions[ws.season_champions.length - 1]
      if (lastChamp) {
        items.push({
          text: `Reigning champion: ${lastChamp.ring_name} (Season ${lastChamp.season})`,
          color: colors.accentBright,
        })
      }
    }
    return items.slice(0, 8)
  }, [ws])

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (error || !ws) return <div style={{ color: colors.injured, padding: spacing.lg }}>No league data. Run initialize_league first.</div>

  const latestChampion = ws.season_champions?.length
    ? ws.season_champions[ws.season_champions.length - 1] ?? null
    : null

  const tierCounts = {
    apex: ws.tier_rankings?.apex?.length ?? 0,
    contender: ws.tier_rankings?.contender?.length ?? 0,
    underground: ws.tier_rankings?.underground?.length ?? 0,
  }

  const currentMonth = ws.current_date ? parseInt(ws.current_date.split('-')[1] || '0') : ws.season_month

  const recentDays = matchesByDay.slice(0, 3)

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '200px 1fr 280px',
      gap: spacing.lg,
    }}>
      <LeftSidebar
        ws={ws}
        latestChampion={latestChampion}
        tierCounts={tierCounts}
        currentMonth={currentMonth}
        simulating={simulating}
        multiSimulating={multiSimulating}
        multiDayCount={multiDayCount}
        setMultiDayCount={setMultiDayCount}
        onSimulateDay={handleSimulateDay}
        onSimulateMultiple={handleSimulateMultiple}
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg, minWidth: 0 }}>
        {heroFight && <HeroFight match={heroFight} />}

        {lastResult && lastResult.matches.length > 0 && (
          <div>
            <SectionHeader>Today's Results</SectionHeader>
            <TieredMatchList matches={lastResult.matches} />
            {lastResult.recoveries.length > 0 && (
              <div style={{ marginTop: spacing.sm, color: colors.healthy, fontSize: fontSizes.sm }}>
                Recovered: {lastResult.recoveries.map(r => r.fighter_name).join(', ')}
              </div>
            )}
            {lastResult.season_end && (
              <div style={{
                marginTop: spacing.sm,
                padding: spacing.sm,
                backgroundColor: withAlpha(colors.accent, 0.1),
                borderRadius: '4px',
                color: colors.accent,
                fontSize: fontSizes.sm,
              }}>
                Season ended — {lastResult.season_end.retirements} retirements, {lastResult.season_end.new_fighters} new fighters, {lastResult.season_end.backfill_promotions} promotions
              </div>
            )}
          </div>
        )}

        <div>
          <SectionHeader accent>AFL SCOREBOARD</SectionHeader>
          {recentDays.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
              {recentDays.map(day => (
                <div key={day.date}>
                  <div style={{
                    color: colors.textMuted,
                    fontSize: fontSizes.xs,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    marginBottom: spacing.sm,
                    paddingBottom: spacing.xs,
                    borderBottom: `1px solid ${colors.border}`,
                  }}>
                    {day.label}
                  </div>
                  <TieredMatchList matches={day.matches} />
                </div>
              ))}
            </div>
          ) : (
            <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
              No matches yet. Click "Next Day" to start the season.
            </div>
          )}
        </div>

        <UpcomingDay
          month={currentMonth}
          day={ws.season_day_in_month}
          season={ws.season_number}
          currentDate={ws.current_date}
          promotionFights={ws.promotion_fights}
          titleFight={ws.title_fight}
          scheduledFights={ws.scheduled_fights}
        />
      </div>

      <RightSidebar
        headlines={headlines}
        seasonLogs={ws.season_logs}
      />
    </div>
  )
}

function LeftSidebar({ ws, latestChampion, tierCounts, currentMonth, simulating, multiSimulating, multiDayCount, setMultiDayCount, onSimulateDay, onSimulateMultiple }: {
  ws: { season_number: number; current_date: string; season_month: number; season_day_in_month: number; promotion_fights: unknown[]; belt_holder_id: string }
  latestChampion: { ring_name: string; season: number; defeated_name: string; fighter_id: string } | null
  tierCounts: { apex: number; contender: number; underground: number }
  currentMonth: number
  simulating: boolean
  multiSimulating: boolean
  multiDayCount: number
  setMultiDayCount: (n: number) => void
  onSimulateDay: () => void
  onSimulateMultiple: () => void
}) {
  const monthLabel = currentMonth === 6 ? 'Promotion Month' :
    ws.promotion_fights?.length ? 'Promotions Announced' : formatCurrentDate(ws.current_date)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
      <div style={{
        padding: spacing.md,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.sm,
        }}>
          Simulation
        </div>
        <button
          onClick={onSimulateDay}
          disabled={simulating || multiSimulating}
          style={{
            width: '100%',
            padding: `${spacing.sm} ${spacing.sm}`,
            backgroundColor: simulating ? colors.surfaceLight : colors.accent,
            color: simulating ? colors.textMuted : colors.background,
            border: 'none',
            borderRadius: '4px',
            fontSize: fontSizes.sm,
            fontWeight: 'bold',
            cursor: simulating ? 'not-allowed' : 'pointer',
            marginBottom: spacing.xs,
          }}
        >
          {simulating ? 'Simulating...' : 'Next Day'}
        </button>
        <div style={{ display: 'flex', gap: spacing.xs }}>
          <input
            type="number"
            min={1}
            max={365}
            value={multiDayCount}
            onChange={e => setMultiDayCount(Math.max(1, Math.min(365, parseInt(e.target.value) || 1)))}
            style={{
              width: '45px',
              padding: spacing.xs,
              backgroundColor: colors.surfaceLight,
              color: colors.text,
              border: `1px solid ${colors.border}`,
              borderRadius: '4px',
              fontSize: fontSizes.xs,
              textAlign: 'center',
            }}
          />
          <button
            onClick={onSimulateMultiple}
            disabled={simulating || multiSimulating}
            style={{
              flex: 1,
              padding: `${spacing.xs} ${spacing.xs}`,
              backgroundColor: multiSimulating ? colors.surfaceLight : colors.surfaceHover,
              color: multiSimulating ? colors.textMuted : colors.text,
              border: `1px solid ${colors.border}`,
              borderRadius: '4px',
              fontSize: fontSizes.xs,
              cursor: multiSimulating ? 'not-allowed' : 'pointer',
            }}
          >
            {multiSimulating ? 'Simulating...' : `Skip ${multiDayCount}d`}
          </button>
        </div>
      </div>

      <div style={{
        padding: spacing.md,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.sm,
        }}>
          Season {ws.season_number}
        </div>
        <div style={{ color: colors.text, fontSize: fontSizes.sm, marginBottom: spacing.xs }}>
          {monthLabel}
        </div>
        <div style={{ color: colors.textDim, fontSize: fontSizes.xs }}>
          Day {ws.season_day_in_month}
        </div>
      </div>

      <div style={{
        padding: spacing.md,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.sm,
        }}>
          Champion
        </div>
        {latestChampion ? (
          <div>
            <Link to={`/fighter/${latestChampion.fighter_id}`} style={{
              color: colors.accentBright,
              fontSize: fontSizes.sm,
              fontWeight: 'bold',
            }}>
              {latestChampion.ring_name}
            </Link>
            <div style={{ color: colors.textDim, fontSize: fontSizes.xs, marginTop: '2px' }}>
              S{latestChampion.season} — def. {latestChampion.defeated_name}
            </div>
          </div>
        ) : (
          <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>TBD</div>
        )}
      </div>

      <div style={{
        padding: spacing.md,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textMuted,
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.sm,
        }}>
          League
        </div>
        {(['apex', 'contender', 'underground'] as const).map(tier => (
          <div key={tier} style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: `2px 0`,
            fontSize: fontSizes.xs,
          }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: spacing.xs, color: tier === 'apex' ? colors.accent : colors.textMuted }}>
              {TIER_LOGOS[tier] && (
                <img src={TIER_LOGOS[tier]} alt={tier} style={{ height: '16px', objectFit: 'contain' }} />
              )}
              {TIER_LABELS[tier]}
            </span>
            <span style={{ color: colors.text }}>{tierCounts[tier]}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function HeroFight({ match }: { match: MatchResult }) {
  const isF1Winner = match.winner_id === match.fighter1_id
  const winnerName = isF1Winner ? match.fighter1_name : match.fighter2_name
  const loserName = isF1Winner ? match.fighter2_name : match.fighter1_name
  const isTitle = match.is_title_fight

  return (
    <Link to={matchUrl(match)} style={{ textDecoration: 'none', display: 'block' }}>
    <div style={{
      padding: spacing.lg,
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `2px solid ${isTitle ? colors.accent : colors.border}`,
      position: 'relative',
      overflow: 'hidden',
    }}>
      {isTitle && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: `linear-gradient(90deg, ${colors.accentDim}, ${colors.accent}, ${colors.accentBright}, ${colors.accent}, ${colors.accentDim})`,
        }} />
      )}
      <div style={{
        fontSize: fontSizes.xs,
        color: isTitle ? colors.accent : colors.textMuted,
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        marginBottom: spacing.sm,
        fontWeight: 'bold',
        display: 'flex',
        alignItems: 'center',
        gap: spacing.xs,
      }}>
        {TIER_LOGOS[match.tier] && (
          <img src={TIER_LOGOS[match.tier]} alt={match.tier} style={{ height: '22px', objectFit: 'contain' }} />
        )}
        {isTitle ? 'Title Fight' : 'Featured Fight'} — {TIER_LABELS[match.tier] || match.tier}
      </div>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: spacing.lg,
      }}>
        <div style={{ textAlign: 'right', flex: 1 }}>
          <div style={{
            fontSize: fontSizes.xxl,
            fontWeight: 'bold',
            color: isF1Winner ? colors.win : colors.loss,
          }}>
            {match.fighter1_name}
          </div>
          <div style={{ fontSize: fontSizes.xs, color: colors.textDim }}>
            {isF1Winner ? 'WINNER' : ''}
          </div>
        </div>
        <div style={{
          fontSize: fontSizes.md,
          color: colors.textDim,
          padding: `${spacing.xs} ${spacing.sm}`,
        }}>
          vs
        </div>
        <div style={{ textAlign: 'left', flex: 1 }}>
          <div style={{
            fontSize: fontSizes.xxl,
            fontWeight: 'bold',
            color: !isF1Winner ? colors.win : colors.loss,
          }}>
            {match.fighter2_name}
          </div>
          <div style={{ fontSize: fontSizes.xs, color: colors.textDim }}>
            {!isF1Winner ? 'WINNER' : ''}
          </div>
        </div>
      </div>
      <div style={{
        textAlign: 'center',
        marginTop: spacing.md,
        fontSize: fontSizes.sm,
      }}>
        <span style={{ fontWeight: 'bold', color: colors.text }}>{winnerName}</span>
        <span style={{ color: colors.textDim }}> def. </span>
        <span style={{ color: colors.textMuted }}>{loserName}</span>
        <span style={{ color: colors.textDim }}> — </span>
        <span style={{ color: methodColor(match.method), fontWeight: 'bold' }}>
          {match.method.toUpperCase()} R{match.round_ended}
        </span>
      </div>
    </div>
    </Link>
  )
}

function RightSidebar({ headlines, seasonLogs }: {
  headlines: { text: string; color: string }[]
  seasonLogs: { season: number; champion_name: string; champion_id: string; retirements: number; new_fighters: number }[]
}) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
      {headlines.length > 0 && (
        <div style={{
          padding: spacing.md,
          backgroundColor: colors.surface,
          borderRadius: '6px',
          border: `1px solid ${colors.border}`,
        }}>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textMuted,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: spacing.sm,
            fontWeight: 'bold',
          }}>
            Top Headlines
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
            {headlines.map((h, i) => (
              <div key={i} style={{
                padding: `${spacing.xs} ${spacing.sm}`,
                borderLeft: `3px solid ${h.color}`,
                fontSize: fontSizes.xs,
                color: colors.text,
                backgroundColor: withAlpha(h.color, 0.05),
                borderRadius: '0 3px 3px 0',
              }}>
                {h.text}
              </div>
            ))}
          </div>
        </div>
      )}

      {seasonLogs && seasonLogs.length > 0 && (
        <div style={{
          padding: spacing.md,
          backgroundColor: colors.surface,
          borderRadius: '6px',
          border: `1px solid ${colors.border}`,
        }}>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textMuted,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: spacing.sm,
            fontWeight: 'bold',
          }}>
            Season History
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
            {seasonLogs.slice(-6).reverse().map(log => (
              <div key={log.season} style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: `${spacing.xs} 0`,
                borderBottom: `1px solid ${colors.border}`,
                fontSize: fontSizes.xs,
              }}>
                <span style={{ color: colors.textDim }}>S{log.season}</span>
                {log.champion_id ? (
                  <Link to={`/fighter/${log.champion_id}`} style={{
                    color: colors.accent,
                    fontWeight: 'bold',
                  }}>
                    {log.champion_name || 'No champion'}
                  </Link>
                ) : (
                  <span style={{ color: colors.textMuted }}>{log.champion_name || 'No champion'}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function UpcomingDay({ month, currentDate, promotionFights, titleFight, scheduledFights }: {
  month: number
  day: number
  season: number
  currentDate: string
  promotionFights: unknown[]
  titleFight: Record<string, string>
  scheduledFights: ScheduledFight[]
}) {
  const isPromotionMonth = month === 6
  const fights = scheduledFights || []

  if (isPromotionMonth) {
    const hasPromos = promotionFights && promotionFights.length > 0
    const hasTitle = titleFight && titleFight.champion_id
    if (!hasPromos && !hasTitle) return null

    return (
      <div style={{
        padding: spacing.md,
        backgroundColor: withAlpha(colors.rivalry, 0.08),
        borderRadius: '6px',
        border: `1px solid ${withAlpha(colors.rivalry, 0.25)}`,
      }}>
        <div style={{
          color: colors.rivalry,
          fontSize: fontSizes.sm,
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          marginBottom: spacing.sm,
        }}>
          Coming Up — Promotion Month
        </div>
        {hasTitle && (
          <div style={{
            padding: `${spacing.xs} ${spacing.sm}`,
            marginBottom: hasPromos ? spacing.xs : 0,
            backgroundColor: withAlpha(colors.accent, 0.1),
            borderRadius: '3px',
            borderLeft: `3px solid ${colors.accent}`,
            color: colors.accent,
            fontSize: fontSizes.sm,
          }}>
            Title Fight — Champion vs #1 Challenger
          </div>
        )}
        {hasPromos && (
          <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
            {promotionFights.length} promotion/relegation matchup{promotionFights.length !== 1 ? 's' : ''} pending
          </div>
        )}
      </div>
    )
  }

  if (fights.length === 0) return null

  const grouped: Record<string, ScheduledFight[]> = {}
  for (const f of fights) {
    if (!grouped[f.tier]) grouped[f.tier] = []
    grouped[f.tier]!.push(f)
  }
  const sortedTiers = Object.keys(grouped).sort(
    (a, b) => TIER_ORDER.indexOf(a) - TIER_ORDER.indexOf(b)
  )

  return (
    <div style={{
      padding: spacing.md,
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
    }}>
      <div style={{
        color: colors.textMuted,
        fontSize: fontSizes.sm,
        fontWeight: 'bold',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        marginBottom: spacing.sm,
      }}>
        Coming Up — {formatCurrentDate(currentDate)}
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
        {sortedTiers.map(tier => (
          <div key={tier}>
            <div style={{
              color: tier === 'apex' ? colors.accent : colors.textDim,
              fontSize: fontSizes.xs,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: spacing.xs,
              display: 'flex',
              alignItems: 'center',
              gap: spacing.xs,
            }}>
              {TIER_LOGOS[tier] && (
                <img src={TIER_LOGOS[tier]} alt={tier} style={{ height: '18px', objectFit: 'contain' }} />
              )}
              {TIER_LABELS[tier] || tier}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {(grouped[tier] || []).map((f, i) => (
                <div key={i} style={{
                  display: 'grid',
                  gridTemplateColumns: 'auto 1fr auto 1fr',
                  gap: spacing.sm,
                  alignItems: 'center',
                  padding: `${spacing.xs} ${spacing.sm}`,
                  backgroundColor: colors.surfaceLight,
                  borderRadius: '3px',
                  fontSize: fontSizes.sm,
                }}>
                  <span style={{ color: colors.textDim, fontSize: fontSizes.xs, minWidth: '52px' }}>
                    {formatTime(f.start_time || '')}
                  </span>
                  <span style={{ color: colors.text, textAlign: 'right' }}>{f.fighter1_name}</span>
                  <span style={{ color: colors.textDim, fontSize: fontSizes.xs }}>vs</span>
                  <span style={{ color: colors.text }}>{f.fighter2_name}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function SectionHeader({ children, accent }: { children: React.ReactNode; accent?: boolean }) {
  return (
    <div style={{
      fontSize: fontSizes.lg,
      color: accent ? colors.accent : colors.text,
      fontWeight: 'bold',
      marginBottom: spacing.sm,
      paddingBottom: spacing.xs,
      borderBottom: `2px solid ${accent ? colors.accent : colors.border}`,
      textTransform: accent ? 'uppercase' : undefined,
      letterSpacing: accent ? '0.05em' : undefined,
    }}>
      {children}
    </div>
  )
}

function TieredMatchList({ matches }: { matches: MatchResult[] }) {
  const grouped: Record<string, MatchResult[]> = {}
  for (const m of matches) {
    const tier = m.tier || 'unknown'
    if (!grouped[tier]) grouped[tier] = []
    grouped[tier].push(m)
  }

  const sortedTiers = Object.keys(grouped).sort(
    (a, b) => TIER_ORDER.indexOf(a) - TIER_ORDER.indexOf(b)
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.sm }}>
      {sortedTiers.map(tier => (
        <div key={tier}>
          <div style={{
            color: tier === 'apex' ? colors.accent : colors.textDim,
            fontSize: fontSizes.xs,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: spacing.xs,
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
          }}>
            {TIER_LOGOS[tier] && (
              <img src={TIER_LOGOS[tier]} alt={tier} style={{ height: '18px', objectFit: 'contain' }} />
            )}
            {TIER_LABELS[tier] || tier}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
            {(grouped[tier] || []).map((m, i) => (
              <MatchRow key={`${m.fighter1_id}-${m.fighter2_id}-${i}`} match={m} />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function matchUrl(match: MatchResult): string {
  return `/match/${match.fighter1_id}_${match.fighter2_id}_${match.date}`
}

function MatchRow({ match }: { match: MatchResult }) {
  const isF1Winner = match.winner_id === match.fighter1_id
  const timeStr = formatTime(match.start_time || '')
  return (
    <Link to={matchUrl(match)} style={{ textDecoration: 'none' }}>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'auto auto 1fr auto 1fr auto',
        gap: spacing.sm,
        alignItems: 'center',
        padding: `${spacing.xs} ${spacing.sm}`,
        backgroundColor: colors.surface,
        borderRadius: '3px',
        fontSize: fontSizes.sm,
        borderLeft: match.is_title_fight ? `3px solid ${colors.accent}` : 'none',
        cursor: 'pointer',
      }}>
        <TierBadge tier={match.tier} size={14} />
        <span style={{
          color: colors.textDim,
          fontSize: fontSizes.xs,
          minWidth: '52px',
        }}>
          {timeStr}
        </span>
        <span style={{
          color: isF1Winner ? colors.win : colors.loss,
          fontWeight: isF1Winner ? 'bold' : 'normal',
          textAlign: 'right',
        }}>
          {match.fighter1_name}
        </span>
        <span style={{ color: colors.textDim, fontSize: fontSizes.xs }}>vs</span>
        <span style={{
          color: !isF1Winner ? colors.win : colors.loss,
          fontWeight: !isF1Winner ? 'bold' : 'normal',
        }}>
          {match.fighter2_name}
        </span>
        <span style={{
          color: methodColor(match.method),
          fontSize: fontSizes.xs,
          minWidth: '70px',
          textAlign: 'right',
        }}>
          {match.method.toUpperCase()} R{match.round_ended}
        </span>
      </div>
    </Link>
  )
}
