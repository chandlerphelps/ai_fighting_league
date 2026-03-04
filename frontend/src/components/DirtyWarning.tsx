import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'

interface Props {
  dirty: string[]
  onRegenerateOutfits?: () => void
  onRegenerateImages?: () => void
}

export default function DirtyWarning({ dirty, onRegenerateOutfits, onRegenerateImages }: Props) {
  if (!dirty || dirty.length === 0) return null

  const hasOutfits = dirty.includes('outfits')
  const hasPrompts = dirty.includes('image_prompts')
  const hasImages = dirty.includes('images')

  const parts: string[] = []
  if (hasOutfits) parts.push('outfits')
  if (hasPrompts) parts.push('image prompts')
  if (hasImages) parts.push('images')

  return (
    <div style={{
      padding: `${spacing.xs} ${spacing.sm}`,
      backgroundColor: withAlpha(colors.rivalry, 0.1),
      border: `1px solid ${withAlpha(colors.rivalry, 0.4)}`,
      borderRadius: '4px',
      display: 'flex',
      alignItems: 'center',
      gap: spacing.sm,
      flexWrap: 'wrap',
    }}>
      <span style={{
        fontSize: fontSizes.xs,
        color: colors.rivalry,
        fontFamily: fonts.body,
      }}>
        Outdated: {parts.join(', ')}
      </span>
      {hasOutfits && onRegenerateOutfits && (
        <button
          onClick={onRegenerateOutfits}
          style={{
            padding: `2px ${spacing.sm}`,
            backgroundColor: withAlpha(colors.rivalry, 0.15),
            border: `1px solid ${colors.rivalry}`,
            borderRadius: '3px',
            color: colors.rivalry,
            fontFamily: fonts.body,
            fontSize: fontSizes.xs,
            cursor: 'pointer',
          }}
        >
          Regen Outfits
        </button>
      )}
      {hasImages && onRegenerateImages && (
        <button
          onClick={onRegenerateImages}
          style={{
            padding: `2px ${spacing.sm}`,
            backgroundColor: withAlpha(colors.rivalry, 0.15),
            border: `1px solid ${colors.rivalry}`,
            borderRadius: '3px',
            color: colors.rivalry,
            fontFamily: fonts.body,
            fontSize: fontSizes.xs,
            cursor: 'pointer',
          }}
        >
          Regen Images
        </button>
      )}
    </div>
  )
}
