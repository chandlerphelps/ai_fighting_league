import { useState, useRef, useCallback, type ReactNode } from 'react'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import { loadFighter } from '../lib/data'
import FighterPortrait from './FighterPortrait'
import type { Fighter } from '../types/fighter'

const fighterCache = new Map<string, Fighter>()

interface FighterHoverCardProps {
  fighterId: string
  fighterName: string
  fighter?: Fighter
  children: ReactNode
}

const STAT_KEYS: { key: keyof Fighter['stats']; label: string }[] = [
  { key: 'power', label: 'PWR' },
  { key: 'speed', label: 'SPD' },
  { key: 'technique', label: 'TEC' },
  { key: 'toughness', label: 'TGH' },
  { key: 'supernatural', label: 'SPN' },
  { key: 'guile', label: 'GLE' },
]

function getStatColor(value: number): string {
  if (value <= 35) return colors.statLow
  if (value <= 65) return colors.statMid
  return colors.statHigh
}

export default function FighterHoverCard({ fighterId, fighterName, fighter: preloaded, children }: FighterHoverCardProps) {
  const [visible, setVisible] = useState(false)
  const [fighterData, setFighterData] = useState<Fighter | null>(preloaded ?? null)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const handleMouseEnter = useCallback(() => {
    timerRef.current = setTimeout(() => {
      setVisible(true)
      if (preloaded) {
        setFighterData(preloaded)
        return
      }
      const cached = fighterCache.get(fighterId)
      if (cached) {
        setFighterData(cached)
        return
      }
      loadFighter(fighterId).then(f => {
        if (f) {
          fighterCache.set(fighterId, f)
          setFighterData(f)
        }
      })
    }, 150)
  }, [fighterId, preloaded])

  const handleMouseLeave = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    setVisible(false)
  }, [])

  return (
    <span
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      style={{ position: 'relative', display: 'inline' }}
    >
      {children}
      {visible && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          zIndex: 1000,
          width: 240,
          padding: spacing.sm,
          backgroundColor: colors.surface,
          border: `1px solid ${colors.border}`,
          borderRadius: '6px',
          boxShadow: `0 4px 12px ${withAlpha(colors.background, 0.8)}`,
          marginTop: '4px',
          pointerEvents: 'none',
        }}>
          {fighterData ? (
            <>
              <div style={{ display: 'flex', gap: spacing.sm, marginBottom: spacing.sm }}>
                <FighterPortrait fighterId={fighterId} name={fighterData.ring_name} size={56} />
                <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', minWidth: 0 }}>
                  <div style={{
                    color: colors.text,
                    fontSize: fontSizes.sm,
                    fontWeight: 'bold',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                  }}>
                    {fighterData.ring_name}
                  </div>
                  <div style={{ color: colors.textMuted, fontSize: fontSizes.xs }}>
                    <span style={{ color: colors.win }}>{fighterData.record.wins}</span>
                    <span style={{ color: colors.textDim }}>-</span>
                    <span style={{ color: colors.loss }}>{fighterData.record.losses}</span>
                    <span style={{ color: colors.textDim }}>-</span>
                    <span>{fighterData.record.draws}</span>
                  </div>
                </div>
              </div>
              <div style={{
                borderTop: `1px solid ${colors.border}`,
                paddingTop: spacing.xs,
                display: 'flex',
                flexDirection: 'column',
                gap: '2px',
              }}>
                {STAT_KEYS.map(({ key, label }) => {
                  const val = fighterData.stats[key]
                  const barColor = getStatColor(val)
                  return (
                    <div key={key} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <span style={{
                        width: 28,
                        fontSize: fontSizes.xs,
                        color: colors.textDim,
                        flexShrink: 0,
                      }}>
                        {label}
                      </span>
                      <div style={{
                        flex: 1,
                        height: 8,
                        backgroundColor: withAlpha(colors.border, 0.5),
                        borderRadius: '2px',
                        overflow: 'hidden',
                      }}>
                        <div style={{
                          width: `${val}%`,
                          height: '100%',
                          backgroundColor: barColor,
                          borderRadius: '2px',
                        }} />
                      </div>
                      <span style={{
                        width: 24,
                        textAlign: 'right',
                        fontSize: fontSizes.xs,
                        color: barColor,
                        fontWeight: 'bold',
                      }}>
                        {val}
                      </span>
                    </div>
                  )
                })}
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, padding: spacing.xs }}>
              <FighterPortrait fighterId={fighterId} name={fighterName} size={40} />
              <div style={{ color: colors.textMuted, fontSize: fontSizes.xs }}>{fighterName}</div>
            </div>
          )}
        </div>
      )}
    </span>
  )
}
