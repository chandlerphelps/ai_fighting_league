import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState } from '../hooks/useData'
import { loadFightersForTier } from '../lib/data'
import type { Fighter } from '../types/fighter'
import type { PromotionFight, TitleFight } from '../types/world_state'

interface NextMatchInfo {
  opponentId: string
  opponentName: string
  date?: string
}

const TIER_LOGOS: Record<string, string> = {
  apex: '/logo_apex_mid.png',
  contender: '/logo_contender_mid.png',
  underground: '/logo_underground_mid.png',
}

const TIER_CONFIG = [
  { key: 'apex' as const, label: 'Apex', color: colors.accent },
  { key: 'contender' as const, label: 'Contender', color: colors.face },
  { key: 'underground' as const, label: 'Underground', color: colors.textMuted },
]

export default function Rankings() {
  const { data: ws, loading, error } = useWorldState()
  const [fighters, setFighters] = useState<Record<string, Fighter>>({})
  const [loadingFighters, setLoadingFighters] = useState(false)

  useEffect(() => {
    if (!ws?.tier_rankings) return
    setLoadingFighters(true)

    const allIds = [
      ...ws.tier_rankings.apex,
      ...ws.tier_rankings.contender,
      ...ws.tier_rankings.underground,
    ]
    loadFightersForTier(allIds).then(loaded => {
      const map: Record<string, Fighter> = {}
      for (const f of loaded) map[f.id] = f
      setFighters(map)
      setLoadingFighters(false)
    })
  }, [ws?.tier_rankings])

  const nextMatchMap = useMemo(() => {
    const map: Record<string, NextMatchInfo> = {}
    const matchups = ws?.next_matchups
    if (matchups) {
      for (const [fighterId, m] of Object.entries(matchups)) {
        map[fighterId] = { opponentId: m.opponent_id, opponentName: m.opponent_name, date: m.date }
      }
    }
    if (ws?.scheduled_fights) {
      for (const sf of ws.scheduled_fights) {
        if (!map[sf.fighter1_id]) {
          map[sf.fighter1_id] = { opponentId: sf.fighter2_id, opponentName: sf.fighter2_name }
        }
        if (!map[sf.fighter2_id]) {
          map[sf.fighter2_id] = { opponentId: sf.fighter1_id, opponentName: sf.fighter1_name }
        }
      }
    }
    return map
  }, [ws?.next_matchups, ws?.scheduled_fights])

  const promotionFighterIds = useMemo(() => {
    const ids = new Set<string>()
    for (const pf of (ws?.promotion_fights ?? [])) {
      ids.add(pf.upper_fighter_id)
      ids.add(pf.lower_fighter_id)
    }
    const tf = ws?.title_fight as TitleFight | undefined
    if (tf?.champion_id) {
      ids.add(tf.champion_id)
      ids.add(tf.challenger_id)
    }
    return ids
  }, [ws?.promotion_fights, ws?.title_fight])

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (error || !ws) return <div style={{ color: colors.injured, padding: spacing.lg }}>No data available.</div>

  const hasPromos = ws.promotion_fights && ws.promotion_fights.length > 0
  const tf = ws.title_fight as TitleFight
  const hasTitle = tf && tf.champion_id
  const showFinale = hasPromos || hasTitle

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {loadingFighters && (
        <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>Loading fighters...</div>
      )}

      {showFinale && (
        <SeasonFinale
          promotionFights={ws.promotion_fights}
          promotionFightDate={ws.promotion_fight_date}
          titleFight={hasTitle ? tf : undefined}
        />
      )}

      {TIER_CONFIG.map(tier => {
        const ids = ws.tier_rankings?.[tier.key] || []
        return (
          <TierSection
            key={tier.key}
            tierKey={tier.key}
            label={tier.label}
            color={tier.color}
            ids={ids}
            fighters={fighters}
            beltHolderId={tier.key === 'apex' ? ws.belt_holder_id : undefined}
            nextMatchMap={nextMatchMap}
            promotionFighterIds={promotionFighterIds}
          />
        )
      })}
    </div>
  )
}

const MONTH_NAMES = [
  '', 'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

function formatDate(d: string): string {
  if (!d || !d.match(/^\d{4}-\d{2}-\d{2}$/)) return d
  const parts = d.split('-').map(Number)
  return `${MONTH_NAMES[parts[1] ?? 0]} ${parts[2]}, ${parts[0]}`
}

function SeasonFinale({ promotionFights, promotionFightDate, titleFight }: {
  promotionFights: PromotionFight[]
  promotionFightDate?: string
  titleFight?: TitleFight
}) {
  const champContender = promotionFights.filter(p => p.tier_boundary === 'champ_contender')
  const contenderUnderground = promotionFights.filter(p => p.tier_boundary === 'contender_underground')

  return (
    <div style={{
      padding: spacing.lg,
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${withAlpha(colors.rivalry, 0.3)}`,
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: spacing.md,
        paddingBottom: spacing.xs,
        borderBottom: `2px solid ${withAlpha(colors.rivalry, 0.3)}`,
      }}>
        <span style={{
          fontSize: fontSizes.lg,
          color: colors.rivalry,
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: '0.1em',
        }}>
          Season Finale
        </span>
        {promotionFightDate && (
          <span style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>
            {formatDate(promotionFightDate)}
          </span>
        )}
      </div>

      {titleFight && (
        <div style={{
          padding: spacing.md,
          marginBottom: spacing.md,
          backgroundColor: withAlpha(colors.accent, 0.08),
          borderRadius: '6px',
          border: `1px solid ${withAlpha(colors.accent, 0.3)}`,
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '3px',
            background: `linear-gradient(90deg, ${colors.accentDim}, ${colors.accent}, ${colors.accentBright}, ${colors.accent}, ${colors.accentDim})`,
          }} />
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.accent,
            textTransform: 'uppercase',
            letterSpacing: '0.1em',
            fontWeight: 'bold',
            marginBottom: spacing.sm,
          }}>
            Title Fight
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: spacing.lg,
          }}>
            <div style={{ textAlign: 'right', flex: 1 }}>
              <Link to={`/fighter/${titleFight.champion_id}`} style={{
                color: colors.accentBright,
                fontSize: fontSizes.xl,
                fontWeight: 'bold',
                textDecoration: 'none',
              }}>
                {titleFight.champion_name}
              </Link>
              <div style={{ fontSize: fontSizes.xs, color: colors.textDim }}>CHAMPION</div>
            </div>
            <span style={{ color: colors.textDim, fontSize: fontSizes.md }}>vs</span>
            <div style={{ textAlign: 'left', flex: 1 }}>
              <Link to={`/fighter/${titleFight.challenger_id}`} style={{
                color: colors.text,
                fontSize: fontSizes.xl,
                fontWeight: 'bold',
                textDecoration: 'none',
              }}>
                {titleFight.challenger_name}
              </Link>
              <div style={{ fontSize: fontSizes.xs, color: colors.textDim }}>CHALLENGER</div>
            </div>
          </div>
        </div>
      )}

      {champContender.length > 0 && (
        <div style={{ marginBottom: contenderUnderground.length > 0 ? spacing.md : 0 }}>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textDim,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: spacing.xs,
          }}>
            Apex / Contender Promotion Fights
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
            {champContender.map((p, i) => (
              <PromotionCard key={i} matchup={p} />
            ))}
          </div>
        </div>
      )}

      {contenderUnderground.length > 0 && (
        <div>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textDim,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            marginBottom: spacing.xs,
          }}>
            Contender / Underground Promotion Fights
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
            {contenderUnderground.map((p, i) => (
              <PromotionCard key={i} matchup={p} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function PromotionCard({ matchup }: { matchup: PromotionFight }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      padding: `${spacing.sm} ${spacing.md}`,
      backgroundColor: withAlpha(colors.rivalry, 0.06),
      borderRadius: '4px',
      borderLeft: `3px solid ${colors.rivalry}`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, flex: 1 }}>
        <Link to={`/fighter/${matchup.upper_fighter_id}`} style={{
          color: colors.text,
          fontWeight: 'bold',
          fontSize: fontSizes.sm,
          textDecoration: 'none',
        }}>
          {matchup.upper_fighter_name}
        </Link>
        <span style={{ color: colors.loss, fontSize: fontSizes.xs }}>&#9660;</span>
      </div>
      <span style={{ color: colors.textDim, fontSize: fontSizes.xs, padding: `0 ${spacing.sm}` }}>vs</span>
      <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, flex: 1, justifyContent: 'flex-end' }}>
        <span style={{ color: colors.win, fontSize: fontSizes.xs }}>&#9650;</span>
        <Link to={`/fighter/${matchup.lower_fighter_id}`} style={{
          color: colors.text,
          fontWeight: 'bold',
          fontSize: fontSizes.sm,
          textDecoration: 'none',
        }}>
          {matchup.lower_fighter_name}
        </Link>
      </div>
    </div>
  )
}

function TierSection({
  tierKey,
  label,
  color,
  ids,
  fighters,
  beltHolderId,
  nextMatchMap,
  promotionFighterIds,
}: {
  tierKey: string
  label: string
  color: string
  ids: string[]
  fighters: Record<string, Fighter>
  beltHolderId?: string
  nextMatchMap: Record<string, NextMatchInfo>
  promotionFighterIds: Set<string>
}) {
  const logoSrc = TIER_LOGOS[tierKey]
  return (
    <div>
      <div style={{
        fontSize: fontSizes.lg,
        color,
        fontWeight: 'bold',
        marginBottom: spacing.sm,
        paddingBottom: spacing.xs,
        borderBottom: `2px solid ${withAlpha(color, 0.3)}`,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
          {logoSrc && (
            <img src={logoSrc} alt={label} style={{ height: '36px', objectFit: 'contain' }} />
          )}
          {label}
        </span>
        <span style={{ fontSize: fontSizes.xs, color: colors.textDim }}>{ids.length} fighters</span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '40px 1fr 100px 100px 80px 80px 80px 100px 80px 60px 80px 1fr',
        gap: '0',
        fontSize: fontSizes.sm,
      }}>
        <HeaderCell>#</HeaderCell>
        <HeaderCell>Fighter</HeaderCell>
        <HeaderCell align="center">Season</HeaderCell>
        <HeaderCell align="center">Career</HeaderCell>
        <HeaderCell align="center">
          <span style={{ color: colors.accent }}>A</span>
        </HeaderCell>
        <HeaderCell align="center">
          <span style={{ color: colors.face }}>Co</span>
        </HeaderCell>
        <HeaderCell align="center">
          <span style={{ color: colors.textMuted }}>UG</span>
        </HeaderCell>
        <HeaderCell align="center">KO / Sub</HeaderCell>
        <HeaderCell align="center">Age</HeaderCell>
        <HeaderCell align="center">Peak</HeaderCell>
        <HeaderCell align="center">Status</HeaderCell>
        <HeaderCell>Next Match</HeaderCell>

        {ids.map((id, idx) => {
          const f = fighters[id]
          if (!f) return null
          const isBeltHolder = beltHolderId === id
          const inPromotion = promotionFighterIds.has(id)
          return <FighterRow key={id} fighter={f} rank={idx + 1} isBeltHolder={isBeltHolder} nextMatch={nextMatchMap[id]} inPromotion={inPromotion} />
        })}
      </div>
    </div>
  )
}

function HeaderCell({ children, align = 'left' }: { children: React.ReactNode; align?: string }) {
  return (
    <div style={{
      padding: `${spacing.xs} ${spacing.sm}`,
      color: colors.textDim,
      fontSize: fontSizes.xs,
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
      borderBottom: `1px solid ${colors.border}`,
      textAlign: align as 'left' | 'center' | 'right',
    }}>
      {children}
    </div>
  )
}

function FighterRow({ fighter, rank, isBeltHolder, nextMatch, inPromotion }: { fighter: Fighter; rank: number; isBeltHolder: boolean; nextMatch?: NextMatchInfo; inPromotion?: boolean }) {
  const rec = fighter.record
  const isInjured = fighter.condition?.health_status === 'injured'
  const totalFights = rec.wins + rec.losses + rec.draws
  const winPct = totalFights > 0 ? Math.round((rec.wins / totalFights) * 100) : 0

  const tierShort: Record<string, string> = {
    apex: 'A',
    contender: 'Co',
    underground: 'UG',
  }

  return (
    <>
      <Cell dim={isInjured}>
        <span style={{ color: colors.textDim }}>{rank}</span>
      </Cell>
      <Cell dim={isInjured}>
        <span style={{ color: isBeltHolder ? colors.accentBright : colors.text, fontWeight: isBeltHolder ? 'bold' : 'normal' }}>
          {isBeltHolder && <span style={{ color: colors.accent, marginRight: spacing.xs }}>&#9733;</span>}
          {fighter.ring_name}
        </span>
        {inPromotion && (
          <span style={{
            marginLeft: spacing.xs,
            fontSize: fontSizes.xs,
            color: colors.rivalry,
            fontWeight: 'bold',
          }}>
            P
          </span>
        )}
      </Cell>
      <SeasonRecordCell fighter={fighter} dim={isInjured} />
      <Cell dim={isInjured} align="center">
        <span style={{ color: colors.win }}>{rec.wins}</span>
        <span style={{ color: colors.textDim }}>-</span>
        <span style={{ color: colors.loss }}>{rec.losses}</span>
        <span style={{ color: colors.textDim, fontSize: fontSizes.xs, marginLeft: spacing.xs }}>
          ({winPct}%)
        </span>
      </Cell>
      <TierRecordCell fighter={fighter} tier="apex" dim={isInjured} />
      <TierRecordCell fighter={fighter} tier="contender" dim={isInjured} />
      <TierRecordCell fighter={fighter} tier="underground" dim={isInjured} />
      <Cell dim={isInjured} align="center">
        <span style={{ color: colors.ko }}>{rec.kos}</span>
        <span style={{ color: colors.textDim }}> / </span>
        <span style={{ color: colors.submission }}>{rec.submissions}</span>
      </Cell>
      <Cell dim={isInjured} align="center">
        {fighter.age}
      </Cell>
      <Cell dim={isInjured} align="center">
        <span style={{ color: colors.textDim, fontSize: fontSizes.xs }}>
          {tierShort[fighter.peak_tier ?? ''] ?? ''}
        </span>
      </Cell>
      <Cell dim={isInjured} align="center">
        {isInjured ? (
          <span style={{ color: colors.injured, fontSize: fontSizes.xs }}>
            INJ ({fighter.condition.recovery_days_remaining}d)
          </span>
        ) : (
          <span style={{ color: colors.healthy, fontSize: fontSizes.xs }}>OK</span>
        )}
      </Cell>
      <Cell dim={isInjured}>
        {nextMatch ? (
          <span style={{ fontSize: fontSizes.xs }}>
            {nextMatch.date && (
              <span style={{ color: colors.textMuted, marginRight: spacing.xs }}>
                {new Date(nextMatch.date + 'T00:00').toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
              </span>
            )}
            <span style={{ color: colors.textDim }}>vs </span>
            <Link to={`/fighter/${nextMatch.opponentId}`} style={{ color: colors.accent }}>
              {nextMatch.opponentName}
            </Link>
          </span>
        ) : (
          <span style={{ color: colors.textDim, fontSize: fontSizes.xs }}>—</span>
        )}
      </Cell>
    </>
  )
}

function SeasonRecordCell({ fighter, dim }: { fighter: Fighter; dim?: boolean }) {
  const sw = fighter.season_wins ?? 0
  const sl = fighter.season_losses ?? 0
  const total = sw + sl
  const pct = total > 0 ? Math.round((sw / total) * 100) : 0
  if (total === 0) {
    return (
      <Cell dim={dim} align="center">
        <span style={{ color: colors.textDim }}>—</span>
      </Cell>
    )
  }
  return (
    <Cell dim={dim} align="center">
      <span style={{ color: colors.win }}>{sw}</span>
      <span style={{ color: colors.textDim }}>-</span>
      <span style={{ color: colors.loss }}>{sl}</span>
      <span style={{ color: colors.textDim, fontSize: fontSizes.xs, marginLeft: spacing.xs }}>
        ({pct}%)
      </span>
    </Cell>
  )
}

function TierRecordCell({ fighter, tier, dim }: { fighter: Fighter; tier: string; dim?: boolean }) {
  const tr = fighter.tier_records?.[tier]
  if (!tr || (tr.wins === 0 && tr.losses === 0)) {
    return (
      <Cell dim={dim} align="center">
        <span style={{ color: colors.textDim }}>—</span>
      </Cell>
    )
  }
  return (
    <Cell dim={dim} align="center">
      <span style={{ color: colors.win }}>{tr.wins}</span>
      <span style={{ color: colors.textDim }}>-</span>
      <span style={{ color: colors.loss }}>{tr.losses}</span>
    </Cell>
  )
}

function Cell({ children, dim, align = 'left' }: { children: React.ReactNode; dim?: boolean; align?: string }) {
  return (
    <div style={{
      padding: `${spacing.xs} ${spacing.sm}`,
      borderBottom: `1px solid ${withAlpha(colors.border, 0.5)}`,
      opacity: dim ? 0.6 : 1,
      textAlign: align as 'left' | 'center' | 'right',
      display: 'flex',
      alignItems: 'center',
      justifyContent: align === 'center' ? 'center' : 'flex-start',
      gap: '2px',
    }}>
      {children}
    </div>
  )
}
