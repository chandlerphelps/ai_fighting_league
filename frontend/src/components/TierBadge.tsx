const TIER_LOGOS: Record<string, string> = {
  apex: '/logo_apex_mini.png',
  contender: '/logo_contender_mini.png',
  underground: '/logo_underground_mini.png',
}

interface TierBadgeProps {
  tier: string
  size?: number
}

export default function TierBadge({ tier, size = 14 }: TierBadgeProps) {
  const src = TIER_LOGOS[tier]
  if (!src) return null

  return (
    <img
      src={src}
      alt={tier}
      style={{
        width: size,
        height: size,
        objectFit: 'contain',
        verticalAlign: 'middle',
        flexShrink: 0,
      }}
    />
  )
}
