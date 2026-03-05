import { useState } from 'react'
import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'
import type { RosterPlan, PlanEntry } from '../types/fighter'
import {
  updatePlanEntry,
  deletePlanEntry,
  regeneratePlanEntry,
  addPlanEntries,
  generateFromPlan,
  deleteRosterPlan,
  pollUntilDone,
  type TaskResponse,
} from '../lib/api'

interface Props {
  plan: RosterPlan
  onPlanChange: () => void
  onTask: (task: TaskResponse, label: string) => void
  onError: (msg: string) => void
}

export default function PlanView({ plan, onPlanChange, onTask, onError }: Props) {
  const [editIndex, setEditIndex] = useState<number | null>(null)
  const [editData, setEditData] = useState<Partial<PlanEntry>>({})
  const [busy, setBusy] = useState(false)
  const [addCount, setAddCount] = useState(4)

  const entries = plan.entries || []
  const approvedCount = entries.filter(e => e.status === 'approved').length
  const pendingCount = entries.filter(e => e.status === 'pending').length

  const startEdit = (index: number) => {
    setEditIndex(index)
    setEditData({ ...entries[index] })
  }

  const saveEdit = async () => {
    if (editIndex === null) return
    try {
      await updatePlanEntry(editIndex, editData)
      setEditIndex(null)
      setEditData({})
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Save failed')
    }
  }

  const handleApprove = async (index: number) => {
    try {
      await updatePlanEntry(index, { status: 'approved' })
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Approve failed')
    }
  }

  const handleApproveAll = async () => {
    try {
      for (let i = 0; i < entries.length; i++) {
        if (entries[i]?.status === 'pending') {
          await updatePlanEntry(i, { status: 'approved' })
        }
      }
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Approve all failed')
    }
  }

  const handleReject = async (index: number) => {
    try {
      await deletePlanEntry(index)
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  const handleReroll = async (index: number) => {
    setBusy(true)
    try {
      const task = await regeneratePlanEntry(index)
      await pollUntilDone(task.task_id)
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Reroll failed')
    } finally {
      setBusy(false)
    }
  }

  const handleAddMore = async () => {
    setBusy(true)
    try {
      const task = await addPlanEntries(addCount)
      await pollUntilDone(task.task_id)
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Add failed')
    } finally {
      setBusy(false)
    }
  }

  const handleGenerate = async () => {
    try {
      const task = await generateFromPlan()
      onTask(task, `Generating ${approvedCount} fighters (Stage 1)...`)
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Generate failed')
    }
  }

  const handleDeletePlan = async () => {
    try {
      await deleteRosterPlan()
      onPlanChange()
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Delete plan failed')
    }
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'approved': return colors.healthy
      case 'rejected': return colors.injured
      case 'generating': return colors.accent
      default: return colors.textMuted
    }
  }

  const btn = (color: string, disabled = false): React.CSSProperties => ({
    padding: `${spacing.xs} ${spacing.sm}`,
    backgroundColor: disabled ? withAlpha(color, 0.1) : withAlpha(color, 0.2),
    border: `1px solid ${disabled ? withAlpha(color, 0.2) : color}`,
    borderRadius: '4px',
    color: disabled ? withAlpha(color, 0.4) : color,
    fontFamily: fonts.body,
    fontSize: fontSizes.xs,
    cursor: disabled ? 'not-allowed' : 'pointer',
  })

  return (
    <div style={{ marginBottom: spacing.xl }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: spacing.md,
        padding: `${spacing.sm} ${spacing.md}`,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: spacing.md }}>
          <span style={{ color: colors.accent, fontFamily: fonts.heading, fontSize: fontSizes.lg }}>
            Roster Plan
          </span>
          <span style={{ color: colors.textMuted, fontFamily: fonts.body, fontSize: fontSizes.sm }}>
            {entries.length} entries ({approvedCount} approved, {pendingCount} pending)
          </span>
        </div>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <button onClick={handleApproveAll} disabled={busy || pendingCount === 0} style={btn(colors.healthy, busy || pendingCount === 0)}>
            Approve All
          </button>
          <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
            <input
              type="number"
              min={1}
              max={200}
              value={addCount}
              onChange={e => setAddCount(Math.max(1, parseInt(e.target.value) || 1))}
              style={{
                width: '52px',
                padding: spacing.xs,
                backgroundColor: colors.surfaceLight,
                border: `1px solid ${colors.border}`,
                borderRadius: '4px',
                color: colors.text,
                fontFamily: fonts.body,
                fontSize: fontSizes.xs,
                textAlign: 'center',
              }}
            />
            <button onClick={handleAddMore} disabled={busy} style={btn(colors.accent, busy)}>
              + Add More
            </button>
          </div>
          <button onClick={handleGenerate} disabled={busy || approvedCount === 0} style={btn(colors.accentBright, busy || approvedCount === 0)}>
            Generate Approved (Stage 1)
          </button>
          <button onClick={handleDeletePlan} disabled={busy || pendingCount === 0} style={btn(colors.injured, busy || pendingCount === 0)}>
            Discard Pending ({pendingCount})
          </button>
        </div>
      </div>

      {plan.pool_summary && (
        <details style={{ marginBottom: spacing.md }}>
          <summary style={{
            color: colors.textMuted, fontFamily: fonts.body, fontSize: fontSizes.sm,
            cursor: 'pointer', padding: spacing.xs,
          }}>
            Pool Summary
          </summary>
          <pre style={{
            whiteSpace: 'pre-wrap', fontSize: fontSizes.xs, color: colors.textDim,
            fontFamily: fonts.body, padding: spacing.md,
            backgroundColor: colors.surface, borderRadius: '4px',
            border: `1px solid ${colors.border}`, maxHeight: '300px', overflow: 'auto',
          }}>
            {plan.pool_summary}
          </pre>
        </details>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
        gap: spacing.md,
      }}>
        {entries.map((entry, index) => {
          const isEditing = editIndex === index

          return (
            <div key={index} style={{
              backgroundColor: colors.surface,
              border: `1px solid ${entry.status === 'approved' ? withAlpha(colors.healthy, 0.4) : colors.border}`,
              borderRadius: '8px',
              padding: spacing.md,
              gridColumn: isEditing ? '1 / -1' : undefined,
              display: isEditing ? 'grid' : 'block',
              gridTemplateColumns: isEditing ? '1fr 1fr' : undefined,
              gap: isEditing ? spacing.lg : undefined,
            }}>
              {isEditing ? (
                <>
                  <div>
                    <PlanCardContent entry={entry} index={index} statusColor={statusColor} />
                  </div>
                  <div>
                    <PlanEntryEditor
                      data={editData}
                      onChange={setEditData}
                      onSave={saveEdit}
                      onCancel={() => { setEditIndex(null); setEditData({}) }}
                    />
                  </div>
                </>
              ) : (
                <>
                  <PlanCardContent entry={entry} index={index} statusColor={statusColor} />
                  <div style={{ display: 'flex', gap: spacing.xs, marginTop: spacing.sm, flexWrap: 'wrap' }}>
                    {entry.status === 'pending' && (
                      <button onClick={() => handleApprove(index)} style={btn(colors.healthy)}>Approve</button>
                    )}
                    <button onClick={() => startEdit(index)} style={btn(colors.accent)}>Edit</button>
                    <button onClick={() => handleReroll(index)} disabled={busy} style={btn(colors.face, busy)}>Reroll</button>
                    <button onClick={() => handleReject(index)} style={btn(colors.injured)}>Remove</button>
                  </div>
                </>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function PlanCardContent({ entry, index, statusColor }: { entry: PlanEntry; index: number; statusColor: (s: string) => string }) {
  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.xs }}>
        <span style={{ color: colors.text, fontFamily: fonts.heading, fontSize: fontSizes.md, fontWeight: 'bold' }}>
          {entry.ring_name || `Entry #${index + 1}`}
        </span>
        <span style={{
          padding: `2px ${spacing.sm}`,
          backgroundColor: withAlpha(statusColor(entry.status), 0.15),
          border: `1px solid ${statusColor(entry.status)}`,
          borderRadius: '3px',
          color: statusColor(entry.status),
          fontFamily: fonts.body,
          fontSize: fontSizes.xs,
          textTransform: 'uppercase',
        }}>
          {entry.status}
        </span>
      </div>

      <div style={{ fontSize: fontSizes.sm, color: colors.textMuted, fontFamily: fonts.body, lineHeight: 1.5 }}>
        <div>{entry.gender} {entry.primary_archetype}{entry.subtype ? ` / ${entry.subtype}` : ''}</div>
        {entry.origin && <div>From {entry.origin}</div>}
        {entry.concept_hook && <div style={{ color: colors.textDim, fontStyle: 'italic' }}>{entry.concept_hook}</div>}
        {entry.power_tier && <div>Tier: {entry.power_tier}</div>}
      </div>

      <div style={{
        display: 'flex', gap: spacing.sm, marginTop: spacing.sm, flexWrap: 'wrap',
        alignItems: 'center',
      }}>
        {entry.primary_outfit_color && (
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: '4px',
            padding: `2px ${spacing.sm}`,
            backgroundColor: withAlpha(colors.surfaceLight, 0.5),
            borderRadius: '3px', fontSize: fontSizes.xs, color: colors.text,
            fontFamily: fonts.body,
          }}>
            <span style={{
              width: '10px', height: '10px', borderRadius: '50%',
              backgroundColor: colors.accent,
              border: `1px solid ${colors.border}`,
            }} />
            {entry.primary_outfit_color}
          </span>
        )}
        {entry.hair_style && (
          <span style={{
            padding: `2px ${spacing.sm}`,
            backgroundColor: withAlpha(colors.surfaceLight, 0.5),
            borderRadius: '3px', fontSize: fontSizes.xs, color: colors.text,
            fontFamily: fonts.body,
          }}>
            {entry.hair_style} {entry.hair_color}
          </span>
        )}
        {entry.face_adornment && entry.face_adornment !== 'none' && (
          <span style={{
            padding: `2px ${spacing.sm}`,
            backgroundColor: withAlpha(colors.surfaceLight, 0.5),
            borderRadius: '3px', fontSize: fontSizes.xs, color: colors.text,
            fontFamily: fonts.body,
          }}>
            {entry.face_adornment}
          </span>
        )}
      </div>
    </>
  )
}

function PlanEntryEditor({
  data, onChange, onSave, onCancel,
}: {
  data: Partial<PlanEntry>
  onChange: (d: Partial<PlanEntry>) => void
  onSave: () => void
  onCancel: () => void
}) {
  const field = (label: string, key: keyof PlanEntry) => (
    <div style={{ marginBottom: spacing.sm }}>
      <label style={{ fontSize: fontSizes.xs, color: colors.textMuted, fontFamily: fonts.body, display: 'block', marginBottom: '2px' }}>
        {label}
      </label>
      <input
        value={String(data[key] || '')}
        onChange={e => onChange({ ...data, [key]: e.target.value })}
        style={{
          width: '100%', padding: spacing.xs,
          backgroundColor: colors.surfaceLight,
          border: `1px solid ${colors.border}`,
          borderRadius: '4px', color: colors.text,
          fontFamily: fonts.body, fontSize: fontSizes.sm,
        }}
      />
    </div>
  )

  return (
    <div>
      <div style={{ fontSize: fontSizes.sm, color: colors.accent, fontFamily: fonts.heading, marginBottom: spacing.sm }}>
        Edit Plan Entry
      </div>
      {field('Ring Name', 'ring_name')}
      {field('Gender', 'gender')}
      {field('Origin', 'origin')}
      {field('Archetype', 'primary_archetype')}
      {field('Subtype', 'subtype')}
      {field('Concept Hook', 'concept_hook')}
      {field('Power Tier', 'power_tier')}
      {field('Outfit Color', 'primary_outfit_color')}
      {field('Hair Style', 'hair_style')}
      {field('Hair Color', 'hair_color')}
      {field('Face Adornment', 'face_adornment')}
      <div style={{ display: 'flex', gap: spacing.sm, marginTop: spacing.md }}>
        <button onClick={onSave} style={{
          padding: `${spacing.xs} ${spacing.md}`,
          backgroundColor: withAlpha(colors.healthy, 0.2),
          border: `1px solid ${colors.healthy}`,
          borderRadius: '4px', color: colors.healthy,
          fontFamily: fonts.body, fontSize: fontSizes.sm, cursor: 'pointer',
        }}>
          Save
        </button>
        <button onClick={onCancel} style={{
          padding: `${spacing.xs} ${spacing.md}`,
          backgroundColor: 'transparent',
          border: `1px solid ${colors.textMuted}`,
          borderRadius: '4px', color: colors.textMuted,
          fontFamily: fonts.body, fontSize: fontSizes.sm, cursor: 'pointer',
        }}>
          Cancel
        </button>
      </div>
    </div>
  )
}
