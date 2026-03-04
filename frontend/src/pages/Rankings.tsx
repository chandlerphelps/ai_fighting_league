import { useState, useEffect } from 'react'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { useWorldState } from '../hooks/useData'
import { loadFightersForTier } from '../lib/data'
import type { Fighter } from '../types/fighter'

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

  if (loading) return <div style={{ color: colors.textMuted, padding: spacing.lg }}>Loading...</div>
  if (error || !ws) return <div style={{ color: colors.injured, padding: spacing.lg }}>No data available.</div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {loadingFighters && (
        <div style={{ color: colors.textMuted, fontSize: fontSizes.sm }}>Loading fighters...</div>
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
          />
        )
      })}
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
}: {
  tierKey: string
  label: string
  color: string
  ids: string[]
  fighters: Record<string, Fighter>
  beltHolderId?: string
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
        gridTemplateColumns: '40px 1fr 100px 80px 80px 80px 100px 80px 60px 80px',
        gap: '0',
        fontSize: fontSizes.sm,
      }}>
        <HeaderCell>#</HeaderCell>
        <HeaderCell>Fighter</HeaderCell>
        <HeaderCell align="center">Record</HeaderCell>
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

        {ids.map((id, idx) => {
          const f = fighters[id]
          if (!f) return null
          const isBeltHolder = beltHolderId === id
          return <FighterRow key={id} fighter={f} rank={idx + 1} isBeltHolder={isBeltHolder} />
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

function FighterRow({ fighter, rank, isBeltHolder }: { fighter: Fighter; rank: number; isBeltHolder: boolean }) {
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
      </Cell>
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
    </>
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
