import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'
import StatBar from '../components/StatBar'
import FighterPortrait from '../components/FighterPortrait'
import type { Fighter } from '../types/fighter'
import { loadAllFighterFiles } from '../lib/data'
import {
  updateFighter,
  deleteFighter,
  generateFighter,
  regenerateCharacter,
  regenerateOutfits,
  regenerateImages,
  pollUntilDone,
  fighterImageUrl,
  type GenerateOptions,
  type TaskResponse,
} from '../lib/api'

type ActiveTask = {
  fighterId?: string
  type: string
  taskId: string
  label: string
}

export default function RosterManager() {
  const [fighters, setFighters] = useState<Fighter[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editData, setEditData] = useState<Partial<Fighter>>({})
  const [showGenerate, setShowGenerate] = useState(false)
  const [activeTasks, setActiveTasks] = useState<ActiveTask[]>([])
  const [regenMenuId, setRegenMenuId] = useState<string | null>(null)
  const [imageViewId, setImageViewId] = useState<string | null>(null)
  const [imageTier, setImageTier] = useState<string>('sfw')

  useEffect(() => {
    const handleClick = () => setRegenMenuId(null)
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  const loadFighters = useCallback(async () => {
    try {
      setLoading(true)
      const data = await loadAllFighterFiles()
      setFighters(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load fighters')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { loadFighters() }, [loadFighters])

  const handleTask = async (task: TaskResponse, activeTask: ActiveTask) => {
    setActiveTasks(prev => [...prev, activeTask])
    try {
      const result = await pollUntilDone(task.task_id)
      if (result.status === 'failed') {
        setError(result.error || 'Task failed')
      }
      await loadFighters()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Task error')
    } finally {
      setActiveTasks(prev => prev.filter(t => t.taskId !== activeTask.taskId))
    }
  }

  const handleGenerate = async (options: GenerateOptions) => {
    try {
      const task = await generateFighter(options)
      setShowGenerate(false)
      handleTask(task, { type: 'generate', taskId: task.task_id, label: 'Generating new fighter...' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Generate failed')
    }
  }

  const handleRegenCharacter = async (fighterId: string) => {
    setRegenMenuId(null)
    try {
      const task = await regenerateCharacter(fighterId)
      handleTask(task, { fighterId, type: 'regen-char', taskId: task.task_id, label: 'Regenerating character...' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Regenerate failed')
    }
  }

  const handleRegenOutfits = async (fighterId: string) => {
    setRegenMenuId(null)
    try {
      const task = await regenerateOutfits(fighterId)
      handleTask(task, { fighterId, type: 'regen-outfits', taskId: task.task_id, label: 'Regenerating outfits...' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Regenerate failed')
    }
  }

  const handleRegenImages = async (fighterId: string, tiers?: string[]) => {
    setRegenMenuId(null)
    try {
      const task = await regenerateImages(fighterId, { tiers })
      handleTask(task, { fighterId, type: 'regen-images', taskId: task.task_id, label: 'Regenerating images...' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Regenerate failed')
    }
  }

  const handleDelete = async (fighterId: string) => {
    try {
      await deleteFighter(fighterId)
      setFighters(prev => prev.filter(f => f.id !== fighterId))
      if (expandedId === fighterId) setExpandedId(null)
      if (editingId === fighterId) setEditingId(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    }
  }

  const startEdit = (fighter: Fighter) => {
    setEditingId(fighter.id)
    setEditData({
      ring_name: fighter.ring_name,
      real_name: fighter.real_name,
      age: fighter.age,
      origin: fighter.origin,
      height: fighter.height,
      weight: fighter.weight,
      build: fighter.build,
      distinguishing_features: fighter.distinguishing_features,
      iconic_features: fighter.iconic_features,
      personality: fighter.personality,
      ring_attire: fighter.ring_attire,
      ring_attire_sfw: fighter.ring_attire_sfw,
      ring_attire_nsfw: fighter.ring_attire_nsfw,
      skimpiness_level: fighter.skimpiness_level,
      stats: { ...fighter.stats },
    })
  }

  const saveEdit = async () => {
    if (!editingId) return
    try {
      await updateFighter(editingId, editData)
      await loadFighters()
      setEditingId(null)
      setEditData({})
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed')
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditData({})
  }

  const isTaskActive = (fighterId?: string) =>
    activeTasks.some(t => t.fighterId === fighterId)

  const globalTaskActive = activeTasks.some(t => !t.fighterId)

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: spacing.lg }}>
        <h1 style={{ fontSize: fontSizes.xxl, color: colors.accent, margin: 0 }}>Roster Manager</h1>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <button
            onClick={() => setShowGenerate(!showGenerate)}
            disabled={globalTaskActive}
            style={btnStyle(colors.accent)}
          >
            + Generate Fighter
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          padding: spacing.md,
          marginBottom: spacing.md,
          backgroundColor: withAlpha(colors.loss, 0.15),
          border: `1px solid ${colors.loss}`,
          borderRadius: '4px',
          color: colors.loss,
          fontSize: fontSizes.sm,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <span>{error}</span>
          <button onClick={() => setError(null)} style={{ ...btnStyleSmall(colors.loss), marginLeft: spacing.md }}>Dismiss</button>
        </div>
      )}

      {activeTasks.length > 0 && (
        <div style={{ marginBottom: spacing.md }}>
          {activeTasks.map(task => (
            <div key={task.taskId} style={{
              padding: `${spacing.sm} ${spacing.md}`,
              marginBottom: spacing.xs,
              backgroundColor: withAlpha(colors.accent, 0.1),
              border: `1px solid ${withAlpha(colors.accent, 0.3)}`,
              borderRadius: '4px',
              color: colors.accent,
              fontSize: fontSizes.sm,
              display: 'flex',
              alignItems: 'center',
              gap: spacing.sm,
            }}>
              <Spinner />
              <span>{task.label}</span>
            </div>
          ))}
        </div>
      )}

      {showGenerate && <GeneratePanel onGenerate={handleGenerate} onCancel={() => setShowGenerate(false)} />}

      {loading && fighters.length === 0 && (
        <div style={{ textAlign: 'center', padding: spacing.xxl, color: colors.textMuted }}>Loading roster...</div>
      )}

      {!loading && fighters.length === 0 && !showGenerate && (
        <div style={{
          textAlign: 'center',
          padding: spacing.xxl,
          color: colors.textMuted,
          border: `1px dashed ${colors.border}`,
          borderRadius: '8px',
        }}>
          <div style={{ fontSize: fontSizes.lg, marginBottom: spacing.sm }}>No fighters in roster</div>
          <div style={{ fontSize: fontSizes.sm }}>Click "Generate Fighter" to create your first roster member</div>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {fighters.map(fighter => {
          const isExpanded = expandedId === fighter.id
          const isEditing = editingId === fighter.id
          const busy = isTaskActive(fighter.id)
          const regenOpen = regenMenuId === fighter.id
          const viewingImages = imageViewId === fighter.id

          return (
            <div
              key={fighter.id}
              style={{
                backgroundColor: colors.surface,
                border: `1px solid ${busy ? withAlpha(colors.accent, 0.5) : colors.border}`,
                borderRadius: '6px',
                overflow: 'hidden',
                opacity: busy ? 0.7 : 1,
                transition: 'opacity 0.3s',
              }}
            >
              {/* Card Header */}
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: spacing.md,
                  padding: spacing.md,
                  cursor: 'pointer',
                }}
                onClick={() => {
                  if (!isEditing) setExpandedId(isExpanded ? null : fighter.id)
                }}
              >
                <FighterPortrait fighterId={fighter.id} name={fighter.ring_name} size={56} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: spacing.sm }}>
                    <span style={{ fontSize: fontSizes.lg, color: colors.accent, fontWeight: 'bold' }}>
                      {fighter.ring_name}
                    </span>
                    <span style={{ fontSize: fontSizes.sm, color: colors.textMuted }}>
                      {fighter.real_name}
                    </span>
                  </div>
                  <div style={{ fontSize: fontSizes.xs, color: colors.textDim, marginTop: '2px' }}>
                    {fighter.gender} · {fighter.age} · {fighter.origin} · {fighter.build}
                  </div>
                </div>
                <div style={{ display: 'flex', gap: spacing.xs, flexWrap: 'nowrap' }}>
                  {Object.entries(fighter.stats).map(([key, val]) => (
                    <div key={key} style={{
                      textAlign: 'center',
                      padding: `${spacing.xs} ${spacing.sm}`,
                      backgroundColor: withAlpha(colors.surfaceLight, 0.5),
                      borderRadius: '4px',
                      minWidth: '44px',
                    }}>
                      <div style={{ fontSize: '0.6rem', color: colors.textDim, textTransform: 'uppercase' }}>
                        {key.slice(0, 3)}
                      </div>
                      <div style={{ fontSize: fontSizes.sm, color: colors.text, fontWeight: 'bold' }}>
                        {val}
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{ display: 'flex', gap: spacing.xs, flexShrink: 0 }} onClick={e => e.stopPropagation()}>
                  <Link to={`/fighter/${fighter.id}`} style={btnStyleSmall(colors.textMuted)} title="View Profile">
                    View
                  </Link>
                  <button onClick={() => startEdit(fighter)} disabled={busy} style={btnStyleSmall(colors.accent)} title="Edit">
                    Edit
                  </button>
                  <div style={{ position: 'relative' }}>
                    <button
                      onClick={e => { e.stopPropagation(); setRegenMenuId(regenOpen ? null : fighter.id) }}
                      disabled={busy}
                      style={btnStyleSmall(colors.face)}
                      title="Regenerate"
                    >
                      Redo ▾
                    </button>
                    {regenOpen && (
                      <div style={{
                        position: 'absolute',
                        top: '100%',
                        right: 0,
                        marginTop: '4px',
                        backgroundColor: colors.surfaceLight,
                        border: `1px solid ${colors.border}`,
                        borderRadius: '4px',
                        zIndex: 100,
                        minWidth: '180px',
                        overflow: 'hidden',
                      }}>
                        <button onClick={() => handleRegenCharacter(fighter.id)} style={dropdownItem}>
                          Redo Character
                        </button>
                        <button onClick={() => handleRegenOutfits(fighter.id)} style={dropdownItem}>
                          Redo Outfits
                        </button>
                        <button onClick={() => handleRegenImages(fighter.id)} style={dropdownItem}>
                          Redo All Images
                        </button>
                        <button onClick={() => handleRegenImages(fighter.id, ['sfw'])} style={dropdownItem}>
                          Redo SFW Image
                        </button>
                        <button onClick={() => handleRegenImages(fighter.id, ['barely'])} style={dropdownItem}>
                          Redo Barely Image
                        </button>
                        <button onClick={() => handleRegenImages(fighter.id, ['nsfw'])} style={dropdownItem}>
                          Redo NSFW Image
                        </button>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={() => setImageViewId(viewingImages ? null : fighter.id)}
                    style={btnStyleSmall(colors.submission)}
                    title="View Images"
                  >
                    Img
                  </button>
                  <button onClick={() => handleDelete(fighter.id)} disabled={busy} style={btnStyleSmall(colors.loss)} title="Delete">
                    Del
                  </button>
                </div>
              </div>

              {/* Image Viewer */}
              {viewingImages && (
                <div style={{ padding: `0 ${spacing.md} ${spacing.md}`, borderTop: `1px solid ${colors.border}` }}>
                  <div style={{ display: 'flex', gap: spacing.sm, marginTop: spacing.md, marginBottom: spacing.sm }}>
                    {['sfw', 'barely', 'nsfw'].map(tier => (
                      <button
                        key={tier}
                        onClick={() => setImageTier(tier)}
                        style={{
                          ...btnStyleSmall(imageTier === tier ? colors.accent : colors.textDim),
                          backgroundColor: imageTier === tier ? withAlpha(colors.accent, 0.2) : 'transparent',
                        }}
                      >
                        {tier.toUpperCase()}
                      </button>
                    ))}
                  </div>
                  <div style={{
                    backgroundColor: colors.background,
                    borderRadius: '4px',
                    padding: spacing.sm,
                    textAlign: 'center',
                    minHeight: '200px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <FighterImage fighterId={fighter.id} tier={imageTier} />
                  </div>
                </div>
              )}

              {/* Edit Mode */}
              {isEditing && (
                <div style={{ padding: `0 ${spacing.md} ${spacing.md}`, borderTop: `1px solid ${colors.border}` }}>
                  <EditPanel
                    data={editData}
                    onChange={setEditData}
                    onSave={saveEdit}
                    onCancel={cancelEdit}
                  />
                </div>
              )}

              {/* Expanded Details */}
              {isExpanded && !isEditing && (
                <div style={{ padding: `0 ${spacing.md} ${spacing.md}`, borderTop: `1px solid ${colors.border}` }}>
                  <ExpandedDetails fighter={fighter} />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

function FighterImage({ fighterId, tier }: { fighterId: string; tier: string }) {
  const [failed, setFailed] = useState(false)
  const [key, setKey] = useState(0)
  const url = fighterImageUrl(fighterId, tier)

  useEffect(() => {
    setFailed(false)
    setKey(k => k + 1)
  }, [fighterId, tier])

  if (failed) {
    return (
      <div style={{ color: colors.textDim, fontSize: fontSizes.sm, padding: spacing.lg }}>
        No {tier} image available
      </div>
    )
  }

  return (
    <img
      key={key}
      src={url}
      alt={`${tier} charsheet`}
      onError={() => setFailed(true)}
      style={{ maxWidth: '100%', maxHeight: '500px', borderRadius: '4px' }}
    />
  )
}

function GeneratePanel({ onGenerate, onCancel }: { onGenerate: (o: GenerateOptions) => void; onCancel: () => void }) {
  const [archetype, setArchetype] = useState('')
  const [hasSupernatural, setHasSupernatural] = useState(false)
  const [conceptHook, setConceptHook] = useState('')
  const [ringName, setRingName] = useState('')
  const [origin, setOrigin] = useState('')

  const archetypes = [
    '', 'The Siren', 'The Witch', 'The Viper', 'The Prodigy',
    'The Doll', 'The Huntress', 'The Empress', 'The Experiment',
  ]

  return (
    <div style={{
      backgroundColor: colors.surface,
      border: `1px solid ${colors.accent}`,
      borderRadius: '6px',
      padding: spacing.lg,
      marginBottom: spacing.lg,
    }}>
      <h2 style={{ fontSize: fontSizes.lg, color: colors.accent, margin: `0 0 ${spacing.md} 0` }}>
        Generate New Fighter
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.md }}>
        <Field label="Archetype">
          <select
            value={archetype}
            onChange={e => setArchetype(e.target.value)}
            style={inputStyle}
          >
            {archetypes.map(a => (
              <option key={a} value={a}>{a || '(Random)'}</option>
            ))}
          </select>
        </Field>
        <Field label="Ring Name (optional)">
          <input value={ringName} onChange={e => setRingName(e.target.value)} style={inputStyle} placeholder="Leave empty for AI to decide" />
        </Field>
        <Field label="Origin (optional)">
          <input value={origin} onChange={e => setOrigin(e.target.value)} style={inputStyle} placeholder="e.g. Tokyo, Japan" />
        </Field>
        <Field label="Supernatural">
          <label style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, color: colors.text, fontSize: fontSizes.sm, cursor: 'pointer' }}>
            <input type="checkbox" checked={hasSupernatural} onChange={e => setHasSupernatural(e.target.checked)} />
            Has supernatural abilities
          </label>
        </Field>
        <div style={{ gridColumn: '1 / -1' }}>
          <Field label="Concept Hook (optional)">
            <textarea
              value={conceptHook}
              onChange={e => setConceptHook(e.target.value)}
              style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }}
              placeholder="e.g. A cybernetic ballerina who fights with grace and hidden blades"
            />
          </Field>
        </div>
      </div>
      <div style={{ display: 'flex', gap: spacing.sm, marginTop: spacing.md, justifyContent: 'flex-end' }}>
        <button onClick={onCancel} style={btnStyle(colors.textMuted)}>Cancel</button>
        <button
          onClick={() => onGenerate({
            archetype: archetype || undefined,
            has_supernatural: hasSupernatural,
            concept_hook: conceptHook || undefined,
            ring_name: ringName || undefined,
            origin: origin || undefined,
          })}
          style={btnStyle(colors.accent)}
        >
          Generate
        </button>
      </div>
    </div>
  )
}

function EditPanel({
  data,
  onChange,
  onSave,
  onCancel,
}: {
  data: Partial<Fighter>
  onChange: (d: Partial<Fighter>) => void
  onSave: () => void
  onCancel: () => void
}) {
  const updateField = (key: string, value: unknown) => {
    onChange({ ...data, [key]: value })
  }

  const updateStat = (key: string, value: number) => {
    onChange({ ...data, stats: { ...data.stats!, [key]: value } })
  }

  return (
    <div style={{ paddingTop: spacing.md }}>
      <h3 style={{ fontSize: fontSizes.md, color: colors.accent, margin: `0 0 ${spacing.md} 0` }}>Edit Fighter</h3>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm }}>
        <Field label="Ring Name">
          <input value={data.ring_name || ''} onChange={e => updateField('ring_name', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Real Name">
          <input value={data.real_name || ''} onChange={e => updateField('real_name', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Age">
          <input type="number" value={data.age || 25} onChange={e => updateField('age', parseInt(e.target.value) || 25)} style={inputStyle} />
        </Field>
        <Field label="Origin">
          <input value={data.origin || ''} onChange={e => updateField('origin', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Height">
          <input value={data.height || ''} onChange={e => updateField('height', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Weight">
          <input value={data.weight || ''} onChange={e => updateField('weight', e.target.value)} style={inputStyle} />
        </Field>
        <div style={{ gridColumn: '1 / -1' }}>
          <Field label="Build">
            <input value={data.build || ''} onChange={e => updateField('build', e.target.value)} style={inputStyle} />
          </Field>
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <Field label="Distinguishing Features">
            <input value={data.distinguishing_features || ''} onChange={e => updateField('distinguishing_features', e.target.value)} style={inputStyle} />
          </Field>
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <Field label="Iconic Features">
            <input value={data.iconic_features || ''} onChange={e => updateField('iconic_features', e.target.value)} style={inputStyle} />
          </Field>
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <Field label="Personality">
            <input value={data.personality || ''} onChange={e => updateField('personality', e.target.value)} style={inputStyle} />
          </Field>
        </div>
      </div>

      <h4 style={{ fontSize: fontSizes.sm, color: colors.textMuted, margin: `${spacing.md} 0 ${spacing.sm} 0` }}>Stats</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm }}>
        {(['power', 'speed', 'technique', 'toughness', 'supernatural'] as const).map(stat => (
          <Field key={stat} label={stat.charAt(0).toUpperCase() + stat.slice(1)}>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
              <input
                type="range"
                min={stat === 'supernatural' ? 0 : 15}
                max={stat === 'supernatural' ? 50 : 95}
                value={data.stats?.[stat] ?? 50}
                onChange={e => updateStat(stat, parseInt(e.target.value))}
                style={{ flex: 1 }}
              />
              <span style={{ color: colors.text, fontSize: fontSizes.sm, width: '32px', textAlign: 'right' }}>
                {data.stats?.[stat] ?? 50}
              </span>
            </div>
          </Field>
        ))}
      </div>

      <h4 style={{ fontSize: fontSizes.sm, color: colors.textMuted, margin: `${spacing.md} 0 ${spacing.sm} 0` }}>Outfits</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: spacing.sm }}>
        <Field label="Ring Attire (SFW)">
          <textarea value={data.ring_attire_sfw || ''} onChange={e => updateField('ring_attire_sfw', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
        </Field>
        <Field label="Ring Attire (Barely)">
          <textarea value={data.ring_attire || ''} onChange={e => updateField('ring_attire', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
        </Field>
        <Field label="Ring Attire (NSFW)">
          <textarea value={data.ring_attire_nsfw || ''} onChange={e => updateField('ring_attire_nsfw', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
        </Field>
        <Field label="Skimpiness Level (1-4)">
          <input type="number" min={1} max={4} value={data.skimpiness_level || 2} onChange={e => updateField('skimpiness_level', parseInt(e.target.value) || 2)} style={inputStyle} />
        </Field>
      </div>

      <div style={{ display: 'flex', gap: spacing.sm, marginTop: spacing.md, justifyContent: 'flex-end' }}>
        <button onClick={onCancel} style={btnStyle(colors.textMuted)}>Cancel</button>
        <button onClick={onSave} style={btnStyle(colors.accent)}>Save Changes</button>
      </div>
    </div>
  )
}

function ExpandedDetails({ fighter }: { fighter: Fighter }) {
  return (
    <div style={{ paddingTop: spacing.md }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
        <div>
          <SectionLabel>Stats</SectionLabel>
          {Object.entries(fighter.stats).map(([key, val]) => (
            <StatBar key={key} name={key} value={val} />
          ))}
          <div style={{ fontSize: fontSizes.xs, color: colors.textDim, marginTop: spacing.xs }}>
            Core total: {fighter.stats.power + fighter.stats.speed + fighter.stats.technique + fighter.stats.toughness}
          </div>
        </div>
        <div>
          <SectionLabel>Identity</SectionLabel>
          <DetailRow label="ID" value={fighter.id} />
          <DetailRow label="Height" value={fighter.height} />
          <DetailRow label="Weight" value={fighter.weight} />
          <DetailRow label="Build" value={fighter.build} />
          <DetailRow label="Skimpiness" value={String(fighter.skimpiness_level || '?')} />
          <DetailRow label="Features" value={fighter.distinguishing_features} />
          <DetailRow label="Iconic" value={fighter.iconic_features || '—'} />
        </div>
      </div>
      <div style={{ marginTop: spacing.md }}>
        <SectionLabel>Personality</SectionLabel>
        <div style={{ fontSize: fontSizes.sm, color: colors.text }}>{fighter.personality || '—'}</div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: spacing.md, marginTop: spacing.md }}>
        <div>
          <SectionLabel>SFW Attire</SectionLabel>
          <div style={{ fontSize: fontSizes.xs, color: colors.textMuted }}>{fighter.ring_attire_sfw || '—'}</div>
        </div>
        <div>
          <SectionLabel>Barely Attire</SectionLabel>
          <div style={{ fontSize: fontSizes.xs, color: colors.textMuted }}>{fighter.ring_attire || '—'}</div>
        </div>
        <div>
          <SectionLabel>NSFW Attire</SectionLabel>
          <div style={{ fontSize: fontSizes.xs, color: colors.textMuted }}>{fighter.ring_attire_nsfw || '—'}</div>
        </div>
      </div>
      {fighter.rivalries.length > 0 && (
        <div style={{ marginTop: spacing.md }}>
          <SectionLabel>Rivalries</SectionLabel>
          <div style={{ fontSize: fontSizes.sm, color: colors.text }}>{fighter.rivalries.join(', ')}</div>
        </div>
      )}
      {fighter.image_prompt?.full_prompt && (
        <div style={{ marginTop: spacing.md }}>
          <SectionLabel>Image Prompt (Barely)</SectionLabel>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textDim,
            backgroundColor: colors.background,
            padding: spacing.sm,
            borderRadius: '4px',
            maxHeight: '100px',
            overflow: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}>
            {fighter.image_prompt.full_prompt}
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={{ display: 'block', fontSize: fontSizes.xs, color: colors.textDim, marginBottom: '2px' }}>
        {label}
      </label>
      {children}
    </div>
  )
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontSize: fontSizes.xs,
      color: colors.accent,
      textTransform: 'uppercase',
      letterSpacing: '0.05em',
      marginBottom: spacing.sm,
      fontWeight: 'bold',
    }}>
      {children}
    </div>
  )
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div style={{ display: 'flex', fontSize: fontSizes.xs, marginBottom: '3px' }}>
      <span style={{ color: colors.textDim, width: '90px', flexShrink: 0 }}>{label}</span>
      <span style={{ color: colors.text }}>{value || '—'}</span>
    </div>
  )
}

function Spinner() {
  return (
    <span style={{
      display: 'inline-block',
      width: '12px',
      height: '12px',
      border: `2px solid ${withAlpha(colors.accent, 0.3)}`,
      borderTopColor: colors.accent,
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite',
    }} />
  )
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: `${spacing.xs} ${spacing.sm}`,
  backgroundColor: colors.background,
  border: `1px solid ${colors.border}`,
  borderRadius: '4px',
  color: colors.text,
  fontFamily: fonts.body,
  fontSize: fontSizes.sm,
  boxSizing: 'border-box',
}

function btnStyle(color: string): React.CSSProperties {
  return {
    padding: `${spacing.xs} ${spacing.md}`,
    backgroundColor: withAlpha(color, 0.15),
    border: `1px solid ${withAlpha(color, 0.4)}`,
    borderRadius: '4px',
    color,
    fontFamily: fonts.body,
    fontSize: fontSizes.sm,
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'inline-block',
  }
}

function btnStyleSmall(color: string): React.CSSProperties {
  return {
    padding: `2px ${spacing.sm}`,
    backgroundColor: 'transparent',
    border: `1px solid ${withAlpha(color, 0.3)}`,
    borderRadius: '3px',
    color,
    fontFamily: fonts.body,
    fontSize: fontSizes.xs,
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'inline-block',
    whiteSpace: 'nowrap',
  }
}

const dropdownItem: React.CSSProperties = {
  display: 'block',
  width: '100%',
  padding: `${spacing.sm} ${spacing.md}`,
  backgroundColor: 'transparent',
  border: 'none',
  borderBottom: `1px solid ${colors.border}`,
  color: colors.text,
  fontFamily: fonts.body,
  fontSize: fontSizes.xs,
  cursor: 'pointer',
  textAlign: 'left',
}
