import { colors, fontSizes, spacing } from '../design-system'

export default function NoData() {
  return (
    <div style={{
      textAlign: 'center',
      padding: spacing.xxl,
      color: colors.textMuted,
    }}>
      <p style={{ fontSize: fontSizes.lg, marginBottom: spacing.md }}>
        No data found
      </p>
      <p style={{ fontSize: fontSizes.sm }}>
        Run the backend engine to generate league data:
      </p>
      <code style={{
        display: 'block',
        marginTop: spacing.md,
        padding: spacing.md,
        backgroundColor: colors.surfaceLight,
        borderRadius: '4px',
        color: colors.accent,
        fontSize: fontSizes.sm,
      }}>
        cd backend && python -m app.run_day --init --days 14
      </code>
    </div>
  )
}
