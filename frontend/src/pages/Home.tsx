import { useState, useCallback, useMemo } from 'react'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState } from '../hooks/useData'
import { simulateDay } from '../lib/data'
import type { DaySimulationResult, MatchResult, ScheduledFight } from '../types/world_state'

const TIER_LABELS: Record<string, string> = {
  championship: 'Championship',
  contender: 'Contender',
  underground: 'Underground',
}

const TIER_ORDER = ['championship', 'contender', 'underground']

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

function parseDateKey(d: string): number {
  if (d.match(/^\d{4}-\d{2}-\d{2}$/)) {
    return parseInt(d.replace(/-/g, ''))
  }
  const m = d.match(/^s(\d+)m(\d+)(?:d(\d+))?$/)
  if (!m) return 0
  const season = parseInt(m[1])
  const month = parseInt(m[2])
  const day = m[3] ? parseInt(m[3]) : 0
  return season * 10000 + month * 100 + day
}

function formatDateLabel(d: string): string {
  if (d.match(/^\d{4}-\d{2}-\d{2}$/)) {
    const [y, m, day] = d.split('-').map(Number)
    return `${MONTH_NAMES[m]} ${day}, ${y}`
  }
  const m = d.match(/^s(\d+)m(\d+)(?:d(\d+))?$/)
  if (!m) return d
  const season = m[1]
  const month = m[2]
  const day = m[3]
  if (day) return `Season ${season} — Month ${month}, Day ${day}`
  return `Season ${season} — Month ${month}`
}

function formatCurrentDate(dateStr: string): string {
  if (dateStr && dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
    const [y, m, day] = dateStr.split('-').map(Number)
    return `${MONTH_NAMES[m]} ${day}, ${y}`
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
        ),
      }))
  }, [ws?.recent_matches])

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (error || !ws) return <div style={{ color: colors.injured, padding: spacing.lg }}>No league data. Run initialize_league first.</div>

  const latestChampion = ws.season_champions?.length
    ? ws.season_champions[ws.season_champions.length - 1]
    : null

  const tierCounts = {
    championship: ws.tier_rankings?.championship?.length ?? 0,
    contender: ws.tier_rankings?.contender?.length ?? 0,
    underground: ws.tier_rankings?.underground?.length ?? 0,
  }

  const currentMonth = ws.current_date ? parseInt(ws.current_date.split('-')[1]) : ws.season_month
  const monthLabel = currentMonth === 6 ? 'Promotion Month' :
    ws.promotion_fights?.length ? 'Promotions Announced' : formatCurrentDate(ws.current_date)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: spacing.md,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <div>
          <div style={{ fontSize: fontSizes.xxl, color: colors.accent, fontWeight: 'bold' }}>
            Season {ws.season_number}
          </div>
          <div style={{ fontSize: fontSizes.md, color: colors.textMuted, marginTop: spacing.xs }}>
            {monthLabel}
          </div>
        </div>

        <div style={{ display: 'flex', gap: spacing.sm, alignItems: 'center' }}>
          <button
            onClick={handleSimulateDay}
            disabled={simulating || multiSimulating}
            style={{
              padding: `${spacing.sm} ${spacing.lg}`,
              backgroundColor: simulating ? colors.surfaceLight : colors.accent,
              color: simulating ? colors.textMuted : colors.background,
              border: 'none',
              borderRadius: '4px',
              fontSize: fontSizes.md,
              fontWeight: 'bold',
              cursor: simulating ? 'not-allowed' : 'pointer',
            }}
          >
            {simulating ? 'Simulating...' : 'Next Day'}
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
            <input
              type="number"
              min={1}
              max={365}
              value={multiDayCount}
              onChange={e => setMultiDayCount(Math.max(1, Math.min(365, parseInt(e.target.value) || 1)))}
              style={{
                width: '50px',
                padding: spacing.xs,
                backgroundColor: colors.surfaceLight,
                color: colors.text,
                border: `1px solid ${colors.border}`,
                borderRadius: '4px',
                fontSize: fontSizes.sm,
                textAlign: 'center',
              }}
            />
            <button
              onClick={handleSimulateMultiple}
              disabled={simulating || multiSimulating}
              style={{
                padding: `${spacing.sm} ${spacing.md}`,
                backgroundColor: multiSimulating ? colors.surfaceLight : colors.surfaceHover,
                color: multiSimulating ? colors.textMuted : colors.text,
                border: `1px solid ${colors.border}`,
                borderRadius: '4px',
                fontSize: fontSizes.sm,
                cursor: multiSimulating ? 'not-allowed' : 'pointer',
              }}
            >
              {multiSimulating ? `Simulating...` : `Skip ${multiDayCount}d`}
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: spacing.md }}>
        <InfoCard label="Season Champion">
          {latestChampion ? (
            <div>
              <div style={{ color: colors.accentBright, fontSize: fontSizes.md }}>
                {latestChampion.ring_name}
              </div>
              <div style={{ color: colors.textMuted, fontSize: fontSizes.xs }}>
                S{latestChampion.season} — def. {latestChampion.defeated_name}
              </div>
            </div>
          ) : (
            <div style={{ color: colors.textMuted, fontSize: fontSizes.md }}>TBD</div>
          )}
        </InfoCard>
        {(['championship', 'contender', 'underground'] as const).map(tier => (
          <InfoCard key={tier} label={TIER_LABELS[tier] || tier} value={`${tierCounts[tier]} fighters`} />
        ))}
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
        <SectionHeader>Recent Results</SectionHeader>
        {matchesByDay.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.lg }}>
            {matchesByDay.map(day => (
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
          <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>No matches yet. Click "Next Day" to start the season.</div>
        )}
      </div>

      {ws.season_logs && ws.season_logs.length > 0 && (
        <div>
          <SectionHeader>Season History</SectionHeader>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: spacing.sm,
          }}>
            {ws.season_logs.slice(-10).reverse().map(log => (
              <div key={log.season} style={{
                padding: spacing.sm,
                backgroundColor: colors.surface,
                borderRadius: '4px',
                border: `1px solid ${colors.border}`,
              }}>
                <div style={{ color: colors.textMuted, fontSize: fontSizes.xs }}>Season {log.season}</div>
                <div style={{ color: colors.accent, fontSize: fontSizes.sm }}>{log.champion_name || 'No champion'}</div>
                <div style={{ color: colors.textDim, fontSize: fontSizes.xs }}>
                  {log.retirements} retired / {log.new_fighters} new
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function UpcomingDay({ month, day, season, currentDate, promotionFights, titleFight, scheduledFights }: {
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
    grouped[f.tier].push(f)
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
              color: tier === 'championship' ? colors.accent : colors.textDim,
              fontSize: fontSizes.xs,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              marginBottom: spacing.xs,
            }}>
              {TIER_LABELS[tier] || tier}
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              {grouped[tier].map((f, i) => (
                <div key={i} style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr auto 1fr',
                  gap: spacing.sm,
                  alignItems: 'center',
                  padding: `${spacing.xs} ${spacing.sm}`,
                  backgroundColor: colors.surfaceLight,
                  borderRadius: '3px',
                  fontSize: fontSizes.sm,
                }}>
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

function InfoCard({ label, value, children }: { label: string; value?: string; children?: React.ReactNode }) {
  return (
    <div style={{
      padding: spacing.md,
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
    }}>
      <div style={{ color: colors.textMuted, fontSize: fontSizes.xs, marginBottom: spacing.xs }}>{label}</div>
      {children || <div style={{ color: colors.text, fontSize: fontSizes.md }}>{value}</div>}
    </div>
  )
}

function SectionHeader({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontSize: fontSizes.lg,
      color: colors.text,
      fontWeight: 'bold',
      marginBottom: spacing.sm,
      paddingBottom: spacing.xs,
      borderBottom: `1px solid ${colors.border}`,
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
            color: tier === 'championship' ? colors.accent : colors.textDim,
            fontSize: fontSizes.xs,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: spacing.xs,
          }}>
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

function MatchRow({ match }: { match: MatchResult }) {
  const isF1Winner = match.winner_id === match.fighter1_id
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr auto 1fr auto',
      gap: spacing.sm,
      alignItems: 'center',
      padding: `${spacing.xs} ${spacing.sm}`,
      backgroundColor: colors.surface,
      borderRadius: '3px',
      fontSize: fontSizes.sm,
      borderLeft: match.is_title_fight ? `3px solid ${colors.accent}` : 'none',
    }}>
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
  )
}
