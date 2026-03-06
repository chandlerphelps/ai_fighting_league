import { useState } from 'react'
import { colors, fontSizes, withAlpha } from '../design-system'
import { fighterImagePath } from '../lib/images'

const IMAGE_TIERS = ['sfw', 'headshot', 'portrait']

interface FighterPortraitProps {
  fighterId: string
  name: string
  size?: number
}

export default function FighterPortrait({ fighterId, name, size = 48 }: FighterPortraitProps) {
  const [tierIndex, setTierIndex] = useState(0)

  const handleError = () => {
    setTierIndex(prev => prev + 1)
  }

  if (tierIndex >= IMAGE_TIERS.length) {
    return (
      <div style={{
        width: size,
        height: size,
        borderRadius: '4px',
        backgroundColor: withAlpha(colors.accent, 0.15),
        border: `1px solid ${withAlpha(colors.accent, 0.3)}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        <span style={{
          fontSize: size > 40 ? fontSizes.md : fontSizes.xs,
          color: colors.accent,
          fontWeight: 'bold',
          userSelect: 'none',
        }}>
          {name.charAt(0).toUpperCase()}
        </span>
      </div>
    )
  }

  return (
    <img
      src={fighterImagePath(fighterId, name, IMAGE_TIERS[tierIndex])}
      alt={name}
      onError={handleError}
      style={{
        width: size,
        height: size,
        borderRadius: '4px',
        objectFit: 'cover',
        flexShrink: 0,
        border: `1px solid ${withAlpha(colors.accent, 0.3)}`,
      }}
    />
  )
}
