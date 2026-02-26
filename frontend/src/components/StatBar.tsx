import { colors, fontSizes, spacing, withAlpha } from '../design-system'

interface StatBarProps {
  name: string
  value: number
}

function getStatColor(value: number): string {
  if (value <= 35) return colors.statLow
  if (value <= 65) return colors.statMid
  return colors.statHigh
}

function formatStatName(name: string): string {
  return name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

export default function StatBar({ name, value }: StatBarProps) {
  const barColor = getStatColor(value)

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
        color: colors.textMuted,
        textTransform: 'capitalize',
      }}>
        {formatStatName(name)}
      </span>
      <div style={{
        flex: 1,
        height: '12px',
        backgroundColor: withAlpha(colors.border, 0.5),
        borderRadius: '2px',
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${value}%`,
          height: '100%',
          backgroundColor: barColor,
          borderRadius: '2px',
          transition: 'width 0.3s ease',
        }} />
      </div>
      <span style={{
        width: '32px',
        textAlign: 'right',
        fontSize: fontSizes.xs,
        color: barColor,
        fontWeight: 'bold',
      }}>
        {value}
      </span>
    </div>
  )
}
