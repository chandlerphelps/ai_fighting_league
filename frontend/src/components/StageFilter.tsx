import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'
import type { Fighter } from '../types/fighter'

export type StageTab = 'all' | 'plan' | 'stage1' | 'stage2' | 'stage3'

interface Props {
  fighters: Fighter[]
  planCount: number
  activeTab: StageTab
  onTabChange: (tab: StageTab) => void
}

export default function StageFilter({ fighters, planCount, activeTab, onTabChange }: Props) {
  const stage1 = fighters.filter(f => (f.generation_stage ?? 3) === 1).length
  const stage2 = fighters.filter(f => (f.generation_stage ?? 3) === 2).length
  const stage3 = fighters.filter(f => (f.generation_stage ?? 3) >= 3 || f.generation_stage === undefined).length

  const tabs: { key: StageTab; label: string; count: number; show: boolean }[] = [
    { key: 'all', label: 'All', count: fighters.length, show: true },
    { key: 'plan', label: 'Plan', count: planCount, show: true },
    { key: 'stage1', label: 'Stage 1: JSON', count: stage1, show: stage1 > 0 },
    { key: 'stage2', label: 'Stage 2: Portrait', count: stage2, show: stage2 > 0 },
    { key: 'stage3', label: 'Stage 3: Ready', count: stage3, show: stage3 > 0 || (stage1 === 0 && stage2 === 0) },
  ]

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: spacing.xs,
      marginBottom: spacing.md,
      padding: `${spacing.xs} ${spacing.sm}`,
      backgroundColor: colors.surface,
      borderRadius: '6px',
      border: `1px solid ${colors.border}`,
      overflowX: 'auto',
    }}>
      {tabs.filter(t => t.show).map(({ key, label, count }) => (
        <button
          key={key}
          onClick={() => onTabChange(key)}
          style={{
            padding: `${spacing.xs} ${spacing.md}`,
            backgroundColor: activeTab === key ? withAlpha(colors.accent, 0.2) : 'transparent',
            border: `1px solid ${activeTab === key ? colors.accent : 'transparent'}`,
            borderRadius: '4px',
            color: activeTab === key ? colors.accent : colors.textMuted,
            fontFamily: fonts.body,
            fontSize: fontSizes.sm,
            cursor: 'pointer',
            whiteSpace: 'nowrap',
            transition: 'all 0.15s ease',
          }}
        >
          {label} ({count})
        </button>
      ))}
    </div>
  )
}

export function filterByStage(fighters: Fighter[], tab: StageTab): Fighter[] {
  switch (tab) {
    case 'stage1': return fighters.filter(f => (f.generation_stage ?? 3) === 1)
    case 'stage2': return fighters.filter(f => (f.generation_stage ?? 3) === 2)
    case 'stage3': return fighters.filter(f => (f.generation_stage ?? 3) >= 3 || f.generation_stage === undefined)
    default: return fighters
  }
}
