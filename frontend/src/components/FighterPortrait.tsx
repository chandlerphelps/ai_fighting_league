import { useState } from 'react'
import { colors, fontSizes, withAlpha } from '../design-system'

interface FighterPortraitProps {
  fighterId: string
  name: string
  size?: number
}

export default function FighterPortrait({ fighterId, name, size = 48 }: FighterPortraitProps) {
  const [failed, setFailed] = useState(false)

  if (failed) {
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
      src={`/fighters/${fighterId}.png`}
      alt={name}
      onError={() => setFailed(true)}
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
