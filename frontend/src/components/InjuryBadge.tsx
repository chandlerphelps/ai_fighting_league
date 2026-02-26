import { colors, fontSizes, spacing, withAlpha } from '../design-system'

interface InjuryBadgeProps {
  daysRemaining?: number
  severity?: string
}

export default function InjuryBadge({ daysRemaining, severity }: InjuryBadgeProps) {
  const label = daysRemaining
    ? `Injured — ${daysRemaining}d`
    : severity
      ? `Injured (${severity})`
      : 'Injured'

  return (
    <span style={{
      display: 'inline-block',
      padding: `2px ${spacing.sm}`,
      fontSize: fontSizes.xs,
      color: colors.injured,
      backgroundColor: withAlpha(colors.injured, 0.15),
      borderRadius: '3px',
      border: `1px solid ${withAlpha(colors.injured, 0.3)}`,
    }}>
      {label}
    </span>
  )
}
