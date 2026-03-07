import { colors, fontSizes, spacing, withAlpha } from '../design-system'

interface StatBarProps {
  name: string
  value: number
}

export function getStatColor(value: number): string {
  if (value > 100) return colors.statOverclock
  if (value <= 35) return colors.statLow
  if (value <= 65) return colors.statMid
  return colors.statHigh
}

function formatStatName(name: string): string {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const overclockKeyframes = `
@keyframes overclock-pulse {
  0%, 100% { opacity: 0.85; }
  50% { opacity: 1; }
}
@keyframes overclock-glitch {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(1px); }
  75% { transform: translateX(-1px); }
}
`

let stylesInjected = false
function injectStyles() {
  if (stylesInjected) return
  const style = document.createElement('style')
  style.textContent = overclockKeyframes
  document.head.appendChild(style)
  stylesInjected = true
}

export default function StatBar({ name, value }: StatBarProps) {
  const isOverclocked = value > 100
  const barColor = getStatColor(value)
  const overflow = isOverclocked ? value - 100 : 0

  if (isOverclocked) injectStyles()

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: spacing.sm,
      marginBottom: '4px',
    }}>
      <span style={{
        width: '140px',
        flexShrink: 0,
        fontSize: fontSizes.xs,
        color: isOverclocked ? colors.statOverclock : colors.textMuted,
        textTransform: 'capitalize',
        ...(isOverclocked ? {
          animation: 'overclock-glitch 2s infinite',
        } : {}),
      }}>
        {formatStatName(name)}
      </span>
      <div style={{
        flex: 1,
        position: 'relative',
        height: '12px',
      }}>
        <div style={{
          width: '100%',
          height: '100%',
          backgroundColor: withAlpha(colors.border, 0.5),
          borderRadius: '2px',
          overflow: 'hidden',
        }}>
          <div style={{
            width: isOverclocked ? '100%' : `${value}%`,
            height: '100%',
            backgroundColor: isOverclocked ? colors.statHigh : barColor,
            borderRadius: '2px',
            transition: 'width 0.3s ease',
          }} />
        </div>
        {isOverclocked && (
          <div style={{
            position: 'absolute',
            top: -1,
            bottom: -1,
            right: `-${overflow * 0.6}%`,
            width: `${overflow * 0.6}%`,
            minWidth: '4px',
            background: `linear-gradient(90deg, ${colors.statOverclock}, ${withAlpha(colors.statOverclock, 0.4)})`,
            borderRadius: '0 2px 2px 0',
            boxShadow: `0 0 8px ${withAlpha(colors.statOverclock, 0.6)}, 0 0 16px ${withAlpha(colors.statOverclock, 0.3)}`,
            animation: 'overclock-pulse 1.5s ease-in-out infinite',
            border: `1px solid ${withAlpha(colors.statOverclock, 0.5)}`,
            borderLeft: 'none',
          }} />
        )}
      </div>
      <span style={{
        width: '32px',
        textAlign: 'right',
        fontSize: fontSizes.xs,
        color: barColor,
        fontWeight: 'bold',
        ...(isOverclocked ? {
          textShadow: `0 0 6px ${withAlpha(colors.statOverclock, 0.8)}`,
          animation: 'overclock-glitch 2s infinite',
        } : {}),
      }}>
        {value}
      </span>
    </div>
  )
}
