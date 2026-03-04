import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { colors, fonts, fontSizes, spacing, withAlpha } from '../design-system'
import StatBar from '../components/StatBar'
import PlanView from '../components/PlanView'
import StageFilter, { filterByStage, type StageTab } from '../components/StageFilter'
import DirtyWarning from '../components/DirtyWarning'
import type { Fighter, RosterPlan } from '../types/fighter'
import { loadAllFighterFiles } from '../lib/data'
import { fighterImagePath, moveImagePath } from '../lib/images'
import {
  updateFighter,
  deleteFighter,
  generateFighter,
  regenerateCharacter,
  regenerateOutfits,
  regenerateImages,
  regenerateMoveImage,
  pollUntilDone,
  fetchOutfitOptions,
  saveOutfitOptions,
  fetchRosterPlan,
  createRosterPlan,
  advanceStage,
  batchAdvance,
  type GenerateOptions,
  type TaskResponse,
  type OutfitOptions,
  type OutfitItem,
} from '../lib/api'

type ActiveTask = {
  fighterId?: string
  type: string
  taskId: string
  label: string
}

type Tier = 'sfw' | 'barely' | 'nsfw' | 'body_ref'

const TIERS: { key: Tier; label: string }[] = [
  { key: 'sfw', label: 'SFW' },
  { key: 'barely', label: 'BARELY' },
  { key: 'nsfw', label: 'NSFW' },
  { key: 'body_ref', label: 'BODY REF' },
]

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
  const [globalTier, setGlobalTier] = useState<Tier>('sfw')
  const [movesViewId, setMovesViewId] = useState<string | null>(null)
  const [lightbox, setLightbox] = useState<{
    fighterId: string
    ringName: string
    tier: Tier
    label: string
    onRedo?: (tier: Tier) => void
  } | null>(null)
  const [imageVersion, setImageVersion] = useState(0)
  const [showOutfitOptions, setShowOutfitOptions] = useState(false)
  const [plan, setPlan] = useState<RosterPlan | null>(null)
  const [stageTab, setStageTab] = useState<StageTab>('all')

  useEffect(() => {
    const handleClick = () => setRegenMenuId(null)
    document.addEventListener('click', handleClick)
    return () => document.removeEventListener('click', handleClick)
  }, [])

  const loadPlan = useCallback(async () => {
    try {
      const p = await fetchRosterPlan()
      setPlan(p)
    } catch {
      setPlan(null)
    }
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

  useEffect(() => { loadFighters(); loadPlan() }, [loadFighters, loadPlan])

  const handleTask = async (task: TaskResponse, activeTask: ActiveTask) => {
    setActiveTasks(prev => [...prev, activeTask])
    try {
      const result = await pollUntilDone(task.task_id)
      if (result.status === 'failed') {
        setError(result.error || 'Task failed')
      } else {
        setImageVersion(v => v + 1)
      }
      await loadFighters()
      await loadPlan()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Task error')
    } finally {
      setActiveTasks(prev => prev.filter(t => t.taskId !== activeTask.taskId))
    }
  }

  const handleCreatePlan = async (count: number) => {
    try {
      const task = await createRosterPlan(count, fighters.length > 0 ? 'addition' : 'initial')
      handleTask(task, { type: 'plan', taskId: task.task_id, label: `Planning ${count} fighters...` })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Plan creation failed')
    }
  }

  const handlePlanTask = async (task: TaskResponse, label: string) => {
    handleTask(task, { type: 'plan-gen', taskId: task.task_id, label })
  }

  const handleAdvanceStage = async (fighterId: string) => {
    try {
      const task = await advanceStage(fighterId)
      handleTask(task, { fighterId, type: 'advance', taskId: task.task_id, label: 'Advancing stage...' })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Advance failed')
    }
  }

  const handleBatchAdvance = async (targetStage: number) => {
    const prevStage = targetStage - 1
    const eligible = fighters.filter(f => (f.generation_stage ?? 3) === prevStage)
    if (eligible.length === 0) return
    try {
      const task = await batchAdvance(eligible.map(f => f.id), targetStage)
      handleTask(task, { type: 'batch-advance', taskId: task.task_id, label: `Advancing ${eligible.length} fighters to Stage ${targetStage}...` })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Batch advance failed')
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
      if (movesViewId === fighterId) setMovesViewId(null)
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
      image_prompt_personality_pose: fighter.image_prompt_personality_pose,
      ring_attire: fighter.ring_attire,
      ring_attire_sfw: fighter.ring_attire_sfw,
      ring_attire_nsfw: fighter.ring_attire_nsfw,
      skimpiness_level: fighter.skimpiness_level,
      primary_outfit_color: fighter.primary_outfit_color,
      hair_style: fighter.hair_style,
      hair_color: fighter.hair_color,
      face_adornment: fighter.face_adornment,
      image_prompt: fighter.image_prompt ? { ...fighter.image_prompt } : undefined,
      image_prompt_sfw: fighter.image_prompt_sfw ? { ...fighter.image_prompt_sfw } : undefined,
      image_prompt_nsfw: fighter.image_prompt_nsfw ? { ...fighter.image_prompt_nsfw } : undefined,
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
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: spacing.lg,
        flexWrap: 'wrap',
        gap: spacing.md,
      }}>
        <h1 style={{
          fontSize: fontSizes.xxl,
          color: colors.accent,
          margin: 0,
          fontFamily: fonts.heading,
        }}>
          Roster Gallery
        </h1>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <button
            onClick={() => setShowOutfitOptions(!showOutfitOptions)}
            style={btnStyle(showOutfitOptions ? colors.accentBright : colors.textMuted)}
          >
            Outfit Options
          </button>
          {!plan && (
            <button
              onClick={() => handleCreatePlan(8)}
              disabled={globalTaskActive}
              style={btnStyle(colors.face)}
            >
              Plan Roster
            </button>
          )}
          <button
            onClick={() => setShowGenerate(!showGenerate)}
            disabled={globalTaskActive}
            style={btnStyle(colors.accent)}
          >
            + Generate Fighter
          </button>
        </div>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: spacing.sm,
        marginBottom: spacing.lg,
        padding: `${spacing.sm} ${spacing.md}`,
        backgroundColor: colors.surface,
        borderRadius: '6px',
        border: `1px solid ${colors.border}`,
      }}>
        <span style={{
          fontSize: fontSizes.sm,
          color: colors.textMuted,
          fontFamily: fonts.body,
          marginRight: spacing.sm,
        }}>
          Tier:
        </span>
        {TIERS.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setGlobalTier(key)}
            style={{
              padding: `${spacing.xs} ${spacing.lg}`,
              backgroundColor: globalTier === key ? withAlpha(colors.accent, 0.25) : 'transparent',
              border: `2px solid ${globalTier === key ? colors.accent : withAlpha(colors.textDim, 0.3)}`,
              borderRadius: '4px',
              color: globalTier === key ? colors.accent : colors.textMuted,
              fontFamily: fonts.body,
              fontSize: fontSizes.md,
              fontWeight: globalTier === key ? 'bold' : 'normal',
              cursor: 'pointer',
              letterSpacing: '0.05em',
              transition: 'all 0.15s ease',
            }}
          >
            {label}
          </button>
        ))}
        <span style={{
          fontSize: fontSizes.xs,
          color: colors.textDim,
          fontFamily: fonts.body,
          marginLeft: 'auto',
        }}>
          {fighters.length} fighter{fighters.length !== 1 ? 's' : ''}
        </span>
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
          fontFamily: fonts.body,
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
              fontFamily: fonts.body,
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

      {showOutfitOptions && <OutfitOptionsPanel onClose={() => setShowOutfitOptions(false)} />}

      {showGenerate && <GeneratePanel onGenerate={handleGenerate} onCancel={() => setShowGenerate(false)} />}

      <StageFilter
        fighters={fighters}
        hasPlan={!!plan}
        planCount={plan?.entries?.length ?? 0}
        activeTab={stageTab}
        onTabChange={setStageTab}
      />

      {stageTab === 'plan' && plan && (
        <PlanView
          plan={plan}
          onPlanChange={() => { loadPlan(); loadFighters() }}
          onTask={handlePlanTask}
          onError={(msg) => setError(msg)}
        />
      )}

      {(stageTab === 'stage1' || stageTab === 'stage2') && (
        <div style={{
          display: 'flex', gap: spacing.sm, marginBottom: spacing.md,
          padding: `${spacing.sm} ${spacing.md}`,
          backgroundColor: colors.surface, borderRadius: '6px',
          border: `1px solid ${colors.border}`,
        }}>
          {stageTab === 'stage1' && (
            <button
              onClick={() => handleBatchAdvance(2)}
              disabled={globalTaskActive}
              style={{
                padding: `${spacing.xs} ${spacing.md}`,
                backgroundColor: withAlpha(colors.accent, 0.2),
                border: `1px solid ${colors.accent}`,
                borderRadius: '4px', color: colors.accent,
                fontFamily: fonts.body, fontSize: fontSizes.sm,
                cursor: globalTaskActive ? 'not-allowed' : 'pointer',
              }}
            >
              Advance All to Stage 2 (Generate Portraits)
            </button>
          )}
          {stageTab === 'stage2' && (
            <button
              onClick={() => handleBatchAdvance(3)}
              disabled={globalTaskActive}
              style={{
                padding: `${spacing.xs} ${spacing.md}`,
                backgroundColor: withAlpha(colors.accent, 0.2),
                border: `1px solid ${colors.accent}`,
                borderRadius: '4px', color: colors.accent,
                fontFamily: fonts.body, fontSize: fontSizes.sm,
                cursor: globalTaskActive ? 'not-allowed' : 'pointer',
              }}
            >
              Advance All to Stage 3 (Full Images)
            </button>
          )}
        </div>
      )}

      {loading && fighters.length === 0 && (
        <div style={{
          textAlign: 'center',
          padding: spacing.xxl,
          color: colors.textMuted,
          fontFamily: fonts.body,
        }}>
          Loading roster...
        </div>
      )}

      {!loading && fighters.length === 0 && !showGenerate && (
        <div style={{
          textAlign: 'center',
          padding: spacing.xxl,
          color: colors.textMuted,
          border: `1px dashed ${colors.border}`,
          borderRadius: '8px',
          fontFamily: fonts.body,
        }}>
          <div style={{ fontSize: fontSizes.lg, marginBottom: spacing.sm }}>No fighters in roster</div>
          <div style={{ fontSize: fontSizes.sm }}>Click "Generate Fighter" to create your first roster member</div>
        </div>
      )}

      {stageTab !== 'plan' && <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: spacing.lg,
      }}>
        {filterByStage(fighters, stageTab).map(fighter => {
          const isExpanded = expandedId === fighter.id
          const isEditing = editingId === fighter.id
          const busy = isTaskActive(fighter.id)
          const regenOpen = regenMenuId === fighter.id
          const showMoves = movesViewId === fighter.id
          const hasInlinePanel = isEditing || isExpanded || showMoves

          return (
            <div
              key={fighter.id}
              style={{
                backgroundColor: colors.surface,
                border: `1px solid ${busy ? withAlpha(colors.accent, 0.5) : colors.border}`,
                borderRadius: '8px',
                overflow: 'hidden',
                opacity: busy ? 0.7 : 1,
                transition: 'opacity 0.3s',
                gridColumn: hasInlinePanel ? '1 / -1' : undefined,
                display: hasInlinePanel ? 'grid' : 'flex',
                gridTemplateColumns: hasInlinePanel ? 'minmax(320px, 400px) 1fr' : undefined,
                flexDirection: hasInlinePanel ? undefined : 'column',
              }}
            >
              <div style={{
                display: 'flex',
                flexDirection: 'column',
              }}>
                <div
                  style={{
                    position: 'relative',
                    cursor: 'pointer',
                    overflow: 'hidden',
                  }}
                  onClick={() => {
                    if (!isEditing) setExpandedId(isExpanded ? null : fighter.id)
                  }}
                >
                  <FighterImage fighterId={fighter.id} ringName={fighter.ring_name} tier={(fighter.generation_stage ?? 3) <= 2 ? 'portrait' : globalTier} version={imageVersion} />
                  <ImageOverlayButtons
                    onExpand={() => setLightbox({
                      fighterId: fighter.id,
                      ringName: fighter.ring_name,
                      tier: globalTier,
                      label: fighter.ring_name,
                      onRedo: (tier: Tier) => handleRegenImages(fighter.id, [tier]),
                    })}
                    onRedo={busy ? undefined : () => handleRegenImages(fighter.id, [globalTier])}
                  />
                  <div style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: `linear-gradient(transparent, ${withAlpha(colors.background, 0.95)})`,
                    padding: `${spacing.xl} ${spacing.md} ${spacing.md}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'flex-end',
                  }}>
                    <div>
                      <div style={{
                        fontSize: fontSizes.lg,
                        fontFamily: fonts.heading,
                        color: colors.accent,
                        fontWeight: 'bold',
                        lineHeight: 1.2,
                      }}>
                        {fighter.ring_name}
                      </div>
                      <div style={{
                        fontSize: fontSizes.xs,
                        fontFamily: fonts.body,
                        color: colors.textMuted,
                        marginTop: '2px',
                      }}>
                        {fighter.origin}
                      </div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
                      {(fighter.generation_stage ?? 3) < 3 && (
                        <span style={{
                          fontSize: fontSizes.xs,
                          fontFamily: fonts.body,
                          padding: `1px ${spacing.xs}`,
                          backgroundColor: withAlpha(colors.rivalry, 0.15),
                          border: `1px solid ${colors.rivalry}`,
                          borderRadius: '3px',
                          color: colors.rivalry,
                        }}>
                          S{fighter.generation_stage ?? 0}
                        </span>
                      )}
                      {fighter.skimpiness_level && (
                        <span style={{
                          fontSize: fontSizes.sm,
                          fontFamily: fonts.body,
                          color: colors.textDim,
                        }}>
                          {fighter.skimpiness_level}
                        </span>
                      )}
                    </div>
                  </div>
                  {fighter.generation_dirty && fighter.generation_dirty.length > 0 && (
                    <div style={{ padding: `0 ${spacing.sm} ${spacing.xs}` }}>
                      <DirtyWarning
                        dirty={fighter.generation_dirty}
                        onRegenerateOutfits={() => handleRegenOutfits(fighter.id)}
                        onRegenerateImages={() => handleRegenImages(fighter.id)}
                      />
                    </div>
                  )}
                  {busy && (
                    <div style={{
                      position: 'absolute',
                      top: spacing.sm,
                      right: spacing.sm,
                      backgroundColor: withAlpha(colors.background, 0.8),
                      borderRadius: '4px',
                      padding: spacing.xs,
                      display: 'flex',
                      alignItems: 'center',
                      gap: spacing.xs,
                    }}>
                      <Spinner />
                    </div>
                  )}
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: spacing.xs,
                  padding: `${spacing.sm} ${spacing.sm}`,
                  backgroundColor: withAlpha(colors.background, 0.5),
                  borderTop: `1px solid ${colors.border}`,
                  flexWrap: 'wrap',
                }}
                  onClick={e => e.stopPropagation()}
                >
                  <Link
                    to={`/fighter/${fighter.id}`}
                    style={actionBtn(colors.textMuted)}
                    title="View Profile"
                  >
                    View
                  </Link>
                  {(fighter.generation_stage ?? 3) < 3 && (
                    <button
                      onClick={() => handleAdvanceStage(fighter.id)}
                      disabled={busy}
                      style={{
                        ...actionBtn(colors.healthy),
                        fontWeight: 'bold',
                      }}
                      title={`Advance to Stage ${(fighter.generation_stage ?? 0) + 1}`}
                    >
                      {(fighter.generation_stage ?? 0) === 1 ? 'Portrait' : 'Full Images'}
                    </button>
                  )}
                  <button
                    onClick={() => startEdit(fighter)}
                    disabled={busy}
                    style={actionBtn(colors.accent)}
                    title="Edit"
                  >
                    Edit
                  </button>
                  <div style={{ position: 'relative' }}>
                    <button
                      onClick={e => { e.stopPropagation(); setRegenMenuId(regenOpen ? null : fighter.id) }}
                      disabled={busy}
                      style={actionBtn(colors.face)}
                      title="Regenerate"
                    >
                      Redo
                    </button>
                    {regenOpen && (
                      <div style={{
                        position: 'absolute',
                        bottom: '100%',
                        left: 0,
                        marginBottom: '4px',
                        backgroundColor: colors.surfaceLight,
                        border: `1px solid ${colors.border}`,
                        borderRadius: '4px',
                        zIndex: 100,
                        minWidth: '180px',
                        overflow: 'hidden',
                        boxShadow: `0 4px 12px ${withAlpha(colors.background, 0.6)}`,
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
                  {fighter.moves && fighter.moves.length > 0 && (
                    <button
                      onClick={() => setMovesViewId(showMoves ? null : fighter.id)}
                      style={{
                        ...actionBtn(showMoves ? colors.accent : colors.submission),
                        backgroundColor: showMoves ? withAlpha(colors.accent, 0.15) : 'transparent',
                      }}
                      title="View Moves"
                    >
                      Moves
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(fighter.id)}
                    disabled={busy}
                    style={actionBtn(colors.loss)}
                    title="Delete"
                  >
                    Del
                  </button>
                  <button
                    onClick={() => {
                      if (!isEditing) setExpandedId(isExpanded ? null : fighter.id)
                    }}
                    style={{
                      ...actionBtn(colors.textDim),
                      marginLeft: 'auto',
                    }}
                    title={isExpanded ? 'Collapse' : 'Details'}
                  >
                    {isExpanded ? 'Less' : 'More'}
                  </button>
                </div>
              </div>

              {isEditing && (
                <div style={{
                  padding: spacing.md,
                  borderLeft: `1px solid ${colors.border}`,
                  overflowY: 'auto',
                  maxHeight: '700px',
                }}>
                  <EditPanel
                    data={editData}
                    onChange={setEditData}
                    onSave={saveEdit}
                    onCancel={cancelEdit}
                  />
                </div>
              )}

              {isExpanded && !isEditing && !showMoves && (
                <div style={{
                  padding: spacing.md,
                  borderLeft: `1px solid ${colors.border}`,
                  overflowY: 'auto',
                  maxHeight: '700px',
                }}>
                  <ExpandedDetails fighter={fighter} />
                </div>
              )}

              {showMoves && !isEditing && (
                <div style={{
                  padding: spacing.md,
                  borderLeft: `1px solid ${colors.border}`,
                  overflowY: 'auto',
                  maxHeight: '700px',
                }}>
                  <MovesGallery
                    fighter={fighter}
                    tier={globalTier}
                    imageVersion={imageVersion}
                    onExpand={() => setLightbox({
                      fighterId: fighter.id,
                      ringName: fighter.ring_name,
                      tier: globalTier,
                      label: fighter.ring_name,
                      onRedo: (tier: Tier) => handleRegenImages(fighter.id, [tier]),
                    })}
                    onRedoMove={(moveIndex, tier) => {
                      const task_promise = regenerateMoveImage(fighter.id, moveIndex, tier)
                      task_promise.then(task => {
                        handleTask(task, {
                          fighterId: fighter.id,
                          type: 'regen-move-img',
                          taskId: task.task_id,
                          label: `Redoing move ${moveIndex + 1} image...`,
                        })
                      }).catch(err => {
                        setError(err instanceof Error ? err.message : 'Redo move image failed')
                      })
                    }}
                    busy={busy}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>}

      {lightbox && (
        <Lightbox
          fighterId={lightbox.fighterId}
          ringName={lightbox.ringName}
          initialTier={lightbox.tier}
          label={lightbox.label}
          imageVersion={imageVersion}
          onRedo={lightbox.onRedo}
          onClose={() => setLightbox(null)}
        />
      )}
    </div>
  )
}

function FighterImage({ fighterId, ringName, tier, version = 0 }: { fighterId: string; ringName: string; tier: string; version?: number }) {
  const [failed, setFailed] = useState(false)
  const [imgLoaded, setImgLoaded] = useState(false)
  const [key, setKey] = useState(0)
  const url = `${fighterImagePath(fighterId, ringName, tier)}?v=${version}`

  useEffect(() => {
    setFailed(false)
    setImgLoaded(false)
    setKey(k => k + 1)
  }, [fighterId, tier, version])

  if (failed) {
    return (
      <div style={{
        width: '100%',
        aspectRatio: '2 / 3',
        backgroundColor: withAlpha(colors.surfaceLight, 0.5),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: spacing.sm,
      }}>
        <div style={{
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          backgroundColor: withAlpha(colors.accent, 0.15),
          border: `2px solid ${withAlpha(colors.accent, 0.3)}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <span style={{
            fontSize: fontSizes.xxl,
            fontFamily: fonts.heading,
            color: colors.accent,
            fontWeight: 'bold',
          }}>
            {ringName.charAt(0).toUpperCase()}
          </span>
        </div>
        <div style={{
          color: colors.textDim,
          fontSize: fontSizes.xs,
          fontFamily: fonts.body,
        }}>
          No {tier} image
        </div>
      </div>
    )
  }

  return (
    <div style={{
      width: '100%',
      position: 'relative',
      backgroundColor: withAlpha(colors.surfaceLight, 0.3),
    }}>
      {!imgLoaded && (
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '300px',
        }}>
          <Spinner />
        </div>
      )}
      <img
        key={key}
        src={url}
        alt={`${ringName} - ${tier}`}
        onError={() => setFailed(true)}
        onLoad={() => setImgLoaded(true)}
        style={{
          width: '100%',
          display: imgLoaded ? 'block' : 'none',
          borderRadius: 0,
        }}
      />
    </div>
  )
}

function MoveImage({ fighterId, ringName, moveIndex, tier, version = 0 }: {
  fighterId: string
  ringName: string
  moveIndex: number
  tier: string
  version?: number
}) {
  const [failed, setFailed] = useState(false)
  const [imgLoaded, setImgLoaded] = useState(false)
  const [key, setKey] = useState(0)
  const url = `${moveImagePath(fighterId, ringName, moveIndex, tier)}?v=${version}`

  useEffect(() => {
    setFailed(false)
    setImgLoaded(false)
    setKey(k => k + 1)
  }, [fighterId, moveIndex, tier, version])

  if (failed) {
    return (
      <div style={{
        width: '100%',
        aspectRatio: '1 / 1',
        backgroundColor: withAlpha(colors.surfaceLight, 0.5),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: spacing.sm,
        borderRadius: '6px',
      }}>
        <div style={{
          color: colors.textDim,
          fontSize: fontSizes.xs,
          fontFamily: fonts.body,
        }}>
          No image
        </div>
      </div>
    )
  }

  return (
    <div style={{
      width: '100%',
      position: 'relative',
      backgroundColor: withAlpha(colors.surfaceLight, 0.3),
      borderRadius: '6px',
      overflow: 'hidden',
    }}>
      {!imgLoaded && (
        <div style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '200px',
        }}>
          <Spinner />
        </div>
      )}
      <img
        key={key}
        src={url}
        alt={`Move ${moveIndex + 1}`}
        onError={() => setFailed(true)}
        onLoad={() => setImgLoaded(true)}
        style={{
          width: '100%',
          display: imgLoaded ? 'block' : 'none',
          borderRadius: '6px',
        }}
      />
    </div>
  )
}

function MovesGallery({ fighter, tier, imageVersion, onExpand, onRedoMove, busy }: {
  fighter: Fighter
  tier: string
  imageVersion: number
  onExpand: () => void
  onRedoMove: (moveIndex: number, tier: string) => void
  busy: boolean
}) {
  const moves = fighter.moves || []

  if (moves.length === 0) {
    return (
      <div style={{
        padding: spacing.lg,
        textAlign: 'center',
        color: colors.textDim,
        fontSize: fontSizes.sm,
        fontFamily: fonts.body,
      }}>
        No moves generated
      </div>
    )
  }

  return (
    <div>
      <SectionLabel>Moves ({moves.length})</SectionLabel>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: spacing.lg,
      }}>
        {moves.map((move, index) => {
          return (
            <div key={index}>
              <div style={{ position: 'relative' }}>
                <MoveImage
                  fighterId={fighter.id}
                  ringName={fighter.ring_name}
                  moveIndex={index}
                  tier={tier}
                  version={imageVersion}
                />
                <ImageOverlayButtons
                  onExpand={() => onExpand()}
                  onRedo={busy ? undefined : () => onRedoMove(index, tier)}
                />
              </div>
              <div style={{
                marginTop: spacing.sm,
                padding: `0 ${spacing.xs}`,
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'baseline',
                  gap: spacing.sm,
                }}>
                  <span style={{
                    fontSize: fontSizes.md,
                    fontFamily: fonts.heading,
                    color: colors.accent,
                    fontWeight: 'bold',
                  }}>
                    {move.name}
                  </span>
                  <span style={{
                    fontSize: fontSizes.xs,
                    fontFamily: fonts.body,
                    color: colors.textDim,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}>
                    {move.stat_affinity}
                  </span>
                </div>
                <div style={{
                  fontSize: fontSizes.xs,
                  fontFamily: fonts.body,
                  color: colors.textMuted,
                  marginTop: spacing.xs,
                  lineHeight: 1.4,
                }}>
                  {move.description}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

type OutfitTier = 'sfw' | 'barely' | 'nsfw'
type OutfitCategory = 'tops' | 'bottoms' | 'one_pieces'

function OutfitOptionsPanel({ onClose }: { onClose: () => void }) {
  const [options, setOptions] = useState<OutfitOptions | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [activeTier, setActiveTier] = useState<OutfitTier>('sfw')
  const [addInputs, setAddInputs] = useState<Record<string, string>>({})

  useEffect(() => {
    fetchOutfitOptions().then(data => {
      setOptions(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    if (!options) return
    setSaving(true)
    try {
      await saveOutfitOptions(options)
    } finally {
      setSaving(false)
    }
  }

  const removeItem = (tier: OutfitTier, category: OutfitCategory, index: number) => {
    if (!options) return
    const updated = { ...options }
    updated[tier] = { ...updated[tier] }
    updated[tier][category] = [...updated[tier][category]]
    updated[tier][category].splice(index, 1)
    setOptions(updated)
  }

  const addItem = (tier: OutfitTier, category: OutfitCategory) => {
    const nameKey = `${tier}_${category}`
    const levelKey = `${tier}_${category}_level`
    const name = (addInputs[nameKey] || '').trim()
    const level = (addInputs[levelKey] || '2').trim()
    if (!name || !options) return
    const newItem: OutfitItem = { name, skimpiness_level: level }
    const updated = { ...options }
    updated[tier] = { ...updated[tier] }
    updated[tier][category] = [...updated[tier][category], newItem]
    setOptions(updated)
    setAddInputs(prev => ({ ...prev, [nameKey]: '', [levelKey]: '' }))
  }

  if (loading) {
    return (
      <div style={{
        backgroundColor: colors.surface,
        border: `1px solid ${colors.border}`,
        borderRadius: '6px',
        padding: spacing.lg,
        marginBottom: spacing.lg,
        textAlign: 'center',
        color: colors.textMuted,
        fontFamily: fonts.body,
      }}>
        Loading outfit options...
      </div>
    )
  }

  if (!options) return null

  const tierData = options[activeTier]
  const categories: { key: OutfitCategory; label: string }[] = [
    { key: 'tops', label: 'Tops' },
    { key: 'bottoms', label: 'Bottoms' },
    { key: 'one_pieces', label: 'One-Pieces' },
  ]

  return (
    <div style={{
      backgroundColor: colors.surface,
      border: `1px solid ${colors.border}`,
      borderRadius: '6px',
      padding: spacing.lg,
      marginBottom: spacing.lg,
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: spacing.md,
      }}>
        <h2 style={{
          fontSize: fontSizes.lg,
          fontFamily: fonts.heading,
          color: colors.accent,
          margin: 0,
        }}>
          Outfit Options
        </h2>
        <div style={{ display: 'flex', gap: spacing.sm }}>
          <button onClick={handleSave} disabled={saving} style={btnStyle(colors.win)}>
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button onClick={onClose} style={btnStyle(colors.textMuted)}>Close</button>
        </div>
      </div>

      <div style={{
        display: 'flex',
        gap: spacing.sm,
        marginBottom: spacing.md,
      }}>
        {(['sfw', 'barely', 'nsfw'] as OutfitTier[]).map(tier => (
          <button
            key={tier}
            onClick={() => setActiveTier(tier)}
            style={{
              padding: `${spacing.xs} ${spacing.lg}`,
              backgroundColor: activeTier === tier ? withAlpha(colors.accent, 0.25) : 'transparent',
              border: `2px solid ${activeTier === tier ? colors.accent : withAlpha(colors.textDim, 0.3)}`,
              borderRadius: '4px',
              color: activeTier === tier ? colors.accent : colors.textMuted,
              fontFamily: fonts.body,
              fontSize: fontSizes.md,
              fontWeight: activeTier === tier ? 'bold' : 'normal',
              cursor: 'pointer',
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
            }}
          >
            {tier}
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.md }}>
        {categories.map(({ key, label }) => {
          return (
            <div key={key}>
              <div style={{
                fontSize: fontSizes.xs,
                fontFamily: fonts.body,
                color: colors.accent,
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
                marginBottom: spacing.xs,
                fontWeight: 'bold',
              }}>
                {label} ({tierData[key].length})
              </div>
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: spacing.xs,
                marginBottom: spacing.xs,
              }}>
                {tierData[key].map((item: OutfitItem, i: number) => (
                  <span
                    key={i}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: spacing.xs,
                      padding: `2px ${spacing.sm}`,
                      backgroundColor: withAlpha(colors.surfaceLight, 0.8),
                      border: `1px solid ${colors.border}`,
                      borderRadius: '3px',
                      color: colors.text,
                      fontFamily: fonts.body,
                      fontSize: fontSizes.xs,
                    }}
                  >
                    {item.name}
                    <span style={{ color: colors.textDim, fontSize: fontSizes.xs }}>
                      L{item.skimpiness_level}
                    </span>
                    <button
                      onClick={() => removeItem(activeTier, key, i)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: colors.loss,
                        cursor: 'pointer',
                        padding: 0,
                        fontFamily: fonts.body,
                        fontSize: fontSizes.xs,
                        lineHeight: 1,
                      }}
                    >
                      x
                    </button>
                  </span>
                ))}
              </div>
              <div style={{ display: 'flex', gap: spacing.xs, alignItems: 'center' }}>
                <input
                  value={addInputs[`${activeTier}_${key}`] || ''}
                  onChange={e => setAddInputs(prev => ({ ...prev, [`${activeTier}_${key}`]: e.target.value }))}
                  onKeyDown={e => { if (e.key === 'Enter') addItem(activeTier, key) }}
                  placeholder={`Add ${label.toLowerCase()}...`}
                  style={{ ...inputStyle, flex: 1 }}
                />
                <input
                  value={addInputs[`${activeTier}_${key}_level`] || ''}
                  onChange={e => setAddInputs(prev => ({ ...prev, [`${activeTier}_${key}_level`]: e.target.value }))}
                  onKeyDown={e => { if (e.key === 'Enter') addItem(activeTier, key) }}
                  placeholder="Lvl"
                  style={{ ...inputStyle, width: '50px', flex: 'none', textAlign: 'center' }}
                />
                <button
                  onClick={() => addItem(activeTier, key)}
                  style={btnStyleSmall(colors.accent)}
                >
                  Add
                </button>
              </div>
            </div>
          )
        })}
      </div>

      <div style={{
        marginTop: spacing.md,
        fontSize: fontSizes.xs,
        fontFamily: fonts.body,
        color: colors.textDim,
      }}>
        These are example attire pieces offered to the AI when generating outfits. Items chosen 2+ times across the roster are auto-removed. 50% of remaining items are randomly dropped each generation for variety.
      </div>
    </div>
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
      <h2 style={{
        fontSize: fontSizes.lg,
        fontFamily: fonts.heading,
        color: colors.accent,
        margin: `0 0 ${spacing.md} 0`,
      }}>
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
          <label style={{ display: 'flex', alignItems: 'center', gap: spacing.sm, color: colors.text, fontSize: fontSizes.sm, fontFamily: fonts.body, cursor: 'pointer' }}>
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

  const updatePromptField = (promptKey: 'image_prompt' | 'image_prompt_sfw' | 'image_prompt_nsfw', field: string, value: string) => {
    const current = (data as Record<string, unknown>)[promptKey] as Record<string, string> | undefined
    onChange({ ...data, [promptKey]: { ...current, [field]: value } })
  }

  return (
    <div>
      <h3 style={{
        fontSize: fontSizes.md,
        fontFamily: fonts.heading,
        color: colors.accent,
        margin: `0 0 ${spacing.md} 0`,
      }}>
        Edit Fighter
      </h3>
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

      <h4 style={{
        fontSize: fontSizes.sm,
        fontFamily: fonts.body,
        color: colors.textMuted,
        margin: `${spacing.md} 0 ${spacing.sm} 0`,
      }}>
        Signature Visual Identity
      </h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.sm }}>
        <Field label="Outfit Color">
          <input value={data.primary_outfit_color || ''} onChange={e => updateField('primary_outfit_color', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Hair Style">
          <input value={data.hair_style || ''} onChange={e => updateField('hair_style', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Hair Color">
          <input value={data.hair_color || ''} onChange={e => updateField('hair_color', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Face Adornment">
          <input value={data.face_adornment || ''} onChange={e => updateField('face_adornment', e.target.value)} style={inputStyle} />
        </Field>
      </div>

      <h4 style={{
        fontSize: fontSizes.sm,
        fontFamily: fonts.body,
        color: colors.textMuted,
        margin: `${spacing.md} 0 ${spacing.sm} 0`,
      }}>
        Stats
      </h4>
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
              <span style={{
                color: colors.text,
                fontSize: fontSizes.sm,
                fontFamily: fonts.body,
                width: '32px',
                textAlign: 'right',
              }}>
                {data.stats?.[stat] ?? 50}
              </span>
            </div>
          </Field>
        ))}
      </div>

      <h4 style={{
        fontSize: fontSizes.sm,
        fontFamily: fonts.body,
        color: colors.textMuted,
        margin: `${spacing.md} 0 ${spacing.sm} 0`,
      }}>
        Outfits
      </h4>
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

      <h4 style={{
        fontSize: fontSizes.sm,
        fontFamily: fonts.body,
        color: colors.textMuted,
        margin: `${spacing.md} 0 ${spacing.sm} 0`,
      }}>
        Image Prompt Components
      </h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: spacing.sm }}>
        <Field label="Body Parts (shared across all tiers)">
          <textarea value={data.image_prompt?.body_parts || ''} onChange={e => updatePromptField('image_prompt', 'body_parts', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
        </Field>
        <Field label="Expression (shared across all tiers)">
          <textarea value={data.image_prompt?.expression || ''} onChange={e => updatePromptField('image_prompt', 'expression', e.target.value)} style={{ ...inputStyle, minHeight: '36px', resize: 'vertical' }} />
        </Field>
        <Field label="Personality Pose">
          <input value={data.image_prompt_personality_pose || ''} onChange={e => updateField('image_prompt_personality_pose', e.target.value)} style={inputStyle} />
        </Field>
        <Field label="Clothing Prompt (SFW)">
          <textarea value={data.image_prompt_sfw?.clothing || ''} onChange={e => updatePromptField('image_prompt_sfw', 'clothing', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
        </Field>
        <Field label="Clothing Prompt (Barely)">
          <textarea value={data.image_prompt?.clothing || ''} onChange={e => updatePromptField('image_prompt', 'clothing', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
        </Field>
        <Field label="Clothing Prompt (NSFW)">
          <textarea value={data.image_prompt_nsfw?.clothing || ''} onChange={e => updatePromptField('image_prompt_nsfw', 'clothing', e.target.value)} style={{ ...inputStyle, minHeight: '48px', resize: 'vertical' }} />
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
    <div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: spacing.lg }}>
        <div>
          <SectionLabel>Stats</SectionLabel>
          {Object.entries(fighter.stats).map(([key, val]) => (
            <StatBar key={key} name={key} value={val} />
          ))}
          <div style={{
            fontSize: fontSizes.xs,
            fontFamily: fonts.body,
            color: colors.textDim,
            marginTop: spacing.xs,
          }}>
            Core total: {fighter.stats.power + fighter.stats.speed + fighter.stats.technique + fighter.stats.toughness}
          </div>
        </div>
        <div>
          <SectionLabel>Identity</SectionLabel>
          <DetailRow label="Real Name" value={fighter.real_name} />
          <DetailRow label="ID" value={fighter.id} />
          <DetailRow label="Age" value={String(fighter.age)} />
          <DetailRow label="Height" value={fighter.height || ''} />
          <DetailRow label="Weight" value={fighter.weight || ''} />
          <DetailRow label="Build" value={fighter.build || ''} />
          <DetailRow label="Gender" value={fighter.gender} />
          <DetailRow label="Skimpiness" value={String(fighter.skimpiness_level || '?')} />
          <DetailRow label="Features" value={fighter.distinguishing_features || ''} />
          <DetailRow label="Iconic" value={fighter.iconic_features || ''} />
        </div>
      </div>
      <div style={{ marginTop: spacing.md }}>
        <SectionLabel>Personality</SectionLabel>
        <div style={{
          fontSize: fontSizes.sm,
          fontFamily: fonts.body,
          color: colors.text,
        }}>
          {fighter.personality || '---'}
        </div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: spacing.md, marginTop: spacing.md }}>
        <div>
          <SectionLabel>SFW Attire</SectionLabel>
          <div style={{ fontSize: fontSizes.xs, fontFamily: fonts.body, color: colors.textMuted }}>
            {fighter.ring_attire_sfw || '---'}
          </div>
        </div>
        <div>
          <SectionLabel>Barely Attire</SectionLabel>
          <div style={{ fontSize: fontSizes.xs, fontFamily: fonts.body, color: colors.textMuted }}>
            {fighter.ring_attire || '---'}
          </div>
        </div>
        <div>
          <SectionLabel>NSFW Attire</SectionLabel>
          <div style={{ fontSize: fontSizes.xs, fontFamily: fonts.body, color: colors.textMuted }}>
            {fighter.ring_attire_nsfw || '---'}
          </div>
        </div>
      </div>
      {fighter.rivalries && fighter.rivalries.length > 0 && (
        <div style={{ marginTop: spacing.md }}>
          <SectionLabel>Rivalries</SectionLabel>
          <div style={{
            fontSize: fontSizes.sm,
            fontFamily: fonts.body,
            color: colors.text,
          }}>
            {(fighter.rivalries || []).join(', ')}
          </div>
        </div>
      )}
      {fighter.image_prompt?.full_prompt && (
        <div style={{ marginTop: spacing.md }}>
          <SectionLabel>Image Prompt (Barely)</SectionLabel>
          <div style={{
            fontSize: fontSizes.xs,
            fontFamily: fonts.body,
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
      <label style={{
        display: 'block',
        fontSize: fontSizes.xs,
        fontFamily: fonts.body,
        color: colors.textDim,
        marginBottom: '2px',
      }}>
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
      fontFamily: fonts.body,
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
    <div style={{ display: 'flex', fontSize: fontSizes.xs, fontFamily: fonts.body, marginBottom: '3px' }}>
      <span style={{ color: colors.textDim, width: '90px', flexShrink: 0 }}>{label}</span>
      <span style={{ color: colors.text }}>{value || '---'}</span>
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

function Lightbox({ fighterId, ringName, initialTier, label, imageVersion, onRedo, onClose }: {
  fighterId: string
  ringName: string
  initialTier: Tier
  label: string
  imageVersion: number
  onRedo?: (tier: Tier) => void
  onClose: () => void
}) {
  const [activeTier, setActiveTier] = useState<Tier>(initialTier)
  const tierKeys: Tier[] = ['sfw', 'barely', 'nsfw', 'body_ref']

  const cycleTier = useCallback((dir: 1 | -1) => {
    setActiveTier(prev => {
      const idx = tierKeys.indexOf(prev)
      const next = tierKeys[(idx + dir + tierKeys.length) % tierKeys.length]
      return next ?? prev
    })
  }, [])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
      else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); cycleTier(1) }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); cycleTier(-1) }
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose, cycleTier])

  const url = `${fighterImagePath(fighterId, ringName, activeTier)}?v=${imageVersion}`

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        backgroundColor: withAlpha(colors.background, 0.92),
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'zoom-out',
      }}
    >
      <div style={{
        position: 'absolute',
        top: spacing.md,
        left: spacing.lg,
        display: 'flex',
        alignItems: 'center',
        gap: spacing.md,
      }}>
        <span style={{
          fontSize: fontSizes.md,
          fontFamily: fonts.heading,
          color: colors.accent,
          fontWeight: 'bold',
        }}>
          {label} — {activeTier.toUpperCase()}
        </span>
        <div style={{ display: 'flex', gap: spacing.xs }} onClick={e => e.stopPropagation()}>
          {tierKeys.map(tier => (
            <button
              key={tier}
              onClick={() => setActiveTier(tier)}
              style={{
                padding: `${spacing.xs} ${spacing.md}`,
                backgroundColor: tier === activeTier ? withAlpha(colors.accent, 0.25) : withAlpha(colors.background, 0.6),
                border: `1px solid ${tier === activeTier ? colors.accent : withAlpha(colors.textDim, 0.3)}`,
                borderRadius: '4px',
                color: tier === activeTier ? colors.accent : colors.textMuted,
                fontFamily: fonts.body,
                fontSize: fontSizes.sm,
                fontWeight: tier === activeTier ? 'bold' : 'normal',
                cursor: 'pointer',
                textTransform: 'uppercase',
                letterSpacing: '0.05em',
              }}
            >
              {tier}
            </button>
          ))}
        </div>
      </div>
      <div style={{
        position: 'absolute',
        top: spacing.md,
        right: spacing.lg,
        display: 'flex',
        gap: spacing.sm,
      }}>
        {onRedo && (
          <button
            onClick={e => { e.stopPropagation(); onRedo(activeTier) }}
            style={{
              ...btnStyle(colors.face),
              padding: `${spacing.sm} ${spacing.lg}`,
              fontSize: fontSizes.md,
            }}
          >
            Redo
          </button>
        )}
        <button
          onClick={e => { e.stopPropagation(); onClose() }}
          style={{
            ...btnStyle(colors.textMuted),
            padding: `${spacing.sm} ${spacing.lg}`,
            fontSize: fontSizes.md,
          }}
        >
          Close
        </button>
      </div>
      <img
        src={url}
        alt={`${label} — ${activeTier}`}
        onClick={e => { e.stopPropagation(); cycleTier(1) }}
        style={{
          maxWidth: '90vw',
          maxHeight: '85vh',
          objectFit: 'contain',
          borderRadius: '8px',
          cursor: 'pointer',
        }}
      />
    </div>
  )
}

function ImageOverlayButtons({ onExpand, onRedo }: {
  onExpand: () => void
  onRedo?: () => void
}) {
  return (
    <div style={{
      position: 'absolute',
      top: spacing.sm,
      left: spacing.sm,
      display: 'flex',
      gap: spacing.xs,
      zIndex: 10,
    }}>
      <button
        onClick={e => { e.stopPropagation(); onExpand() }}
        style={overlayBtn}
        title="Expand"
      >
        Expand
      </button>
      {onRedo && (
        <button
          onClick={e => { e.stopPropagation(); onRedo() }}
          style={overlayBtn}
          title="Redo this image"
        >
          Redo
        </button>
      )}
    </div>
  )
}

const overlayBtn: React.CSSProperties = {
  padding: `2px ${spacing.sm}`,
  backgroundColor: withAlpha(colors.background, 0.75),
  border: `1px solid ${withAlpha(colors.textMuted, 0.3)}`,
  borderRadius: '3px',
  color: colors.text,
  fontFamily: fonts.body,
  fontSize: fontSizes.xs,
  cursor: 'pointer',
  backdropFilter: 'blur(4px)',
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

function actionBtn(color: string): React.CSSProperties {
  return {
    padding: `${spacing.xs} ${spacing.sm}`,
    backgroundColor: 'transparent',
    border: `1px solid ${withAlpha(color, 0.25)}`,
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
