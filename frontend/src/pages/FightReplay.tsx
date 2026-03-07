import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import { colors, fontSizes, spacing, withAlpha } from '../design-system'
import FighterPortrait from '../components/FighterPortrait'
import type { MatchResult } from '../types/world_state'
import type { FightMoment, Match } from '../types/match'
import type { Fighter } from '../types/fighter'

const METHOD_COLORS: Record<string, string> = {
  ko: colors.ko,
  tko: colors.ko,
  submission: colors.submission,
  decision: colors.decision,
}

const METHOD_LABELS: Record<string, string> = {
  ko: 'KNOCKOUT',
  tko: 'TKO',
  submission: 'SUBMISSION',
  decision: 'DECISION',
}

const DAMAGE_VERBS = [
  'SMASHES', 'CRUSHES', 'SLAMS', 'BLASTS', 'ROCKS',
  'HAMMERS', 'NAILS', 'CRACKS', 'DRILLS', 'WRECKS',
]

const BLOCK_VERBS = [
  'BLOCKS', 'DEFLECTS', 'PARRIES', 'ABSORBS', 'TANKS',
]

const MISS_VERBS = [
  'DODGES', 'EVADES', 'SLIPS', 'WEAVES', 'DUCKS',
]

function generateMockMoments(match: MatchResult): FightMoment[] {
  const moments: FightMoment[] = []
  const totalRounds = match.method === 'decision' ? 3 : match.round_ended
  const isF1Winner = match.winner_id === match.fighter1_id

  let f1Hp = 100
  let f2Hp = 100
  let momentNum = 0

  for (let round = 1; round <= totalRounds; round++) {
    const isLastRound = round === totalRounds
    const momentsInRound = isLastRound && match.method !== 'decision'
      ? 3 + Math.floor(Math.random() * 3)
      : 4 + Math.floor(Math.random() * 4)

    for (let i = 0; i < momentsInRound; i++) {
      momentNum++
      const isF1Attacking = Math.random() > 0.45
      const attackerId = isF1Attacking ? match.fighter1_id : match.fighter2_id
      const defenderId = isF1Attacking ? match.fighter2_id : match.fighter1_id
      const isFinisher = isLastRound && i === momentsInRound - 1 && match.method !== 'decision'

      let damage: number
      let result: string
      let action: string
      let defenderAction: string

      if (isFinisher) {
        damage = 15 + Math.floor(Math.random() * 25)
        result = match.method === 'submission' ? 'submission' : 'knockout'
        action = match.method === 'submission' ? 'Submission Lock' : 'Devastating Strike'
        defenderAction = match.method === 'submission' ? 'Taps Out' : 'Knocked Down'
        if (isF1Winner) {
          f2Hp = Math.max(0, f2Hp - damage)
        } else {
          f1Hp = Math.max(0, f1Hp - damage)
        }
      } else {
        const roll = Math.random()
        if (roll < 0.55) {
          damage = 3 + Math.floor(Math.random() * 12)
          result = 'hit'
          const attacks = ['Straight Right', 'Left Hook', 'Body Shot', 'Uppercut', 'Knee Strike',
            'Spinning Elbow', 'Leg Kick', 'Jab', 'Cross', 'Overhand Right']
          action = attacks[Math.floor(Math.random() * attacks.length)]
          defenderAction = 'Hit'
        } else if (roll < 0.8) {
          damage = 1
          result = 'blocked'
          action = 'Combination'
          defenderAction = 'Blocked'
        } else {
          damage = 0
          result = 'miss'
          action = 'Wild Swing'
          defenderAction = 'Dodged'
        }

        if (isF1Attacking) {
          f2Hp = Math.max(5, f2Hp - damage)
        } else {
          f1Hp = Math.max(5, f1Hp - damage)
        }
      }

      const winnerBias = isLastRound && i > momentsInRound / 2

      moments.push({
        moment_number: momentNum,
        description: `${isF1Attacking ? match.fighter1_name : match.fighter2_name} attacks with ${action}`,
        attacker_id: winnerBias && !isFinisher
          ? (isF1Winner ? match.fighter1_id : match.fighter2_id)
          : attackerId,
        defender_id: winnerBias && !isFinisher
          ? (isF1Winner ? match.fighter2_id : match.fighter1_id)
          : defenderId,
        action,
        defender_action: defenderAction,
        result,
        damage_dealt: damage,
        tick_number: momentNum,
        round_number: round,
        attacker_hp: isF1Attacking ? f1Hp : f2Hp,
        attacker_stamina: 60 + Math.floor(Math.random() * 40),
        attacker_mana: 40 + Math.floor(Math.random() * 60),
        defender_hp: isF1Attacking ? f2Hp : f1Hp,
        defender_stamina: 50 + Math.floor(Math.random() * 40),
        defender_mana: 30 + Math.floor(Math.random() * 60),
        attacker_emotions: {},
        defender_emotions: {},
        image_prompt: '',
        image_path: '',
      })
    }
  }

  return moments
}

function getActionVerb(result: string): string {
  if (result === 'hit' || result === 'knockout') {
    return DAMAGE_VERBS[Math.floor(Math.random() * DAMAGE_VERBS.length)]
  }
  if (result === 'blocked') {
    return BLOCK_VERBS[Math.floor(Math.random() * BLOCK_VERBS.length)]
  }
  return MISS_VERBS[Math.floor(Math.random() * MISS_VERBS.length)]
}

function getImpactColor(result: string, damage: number): string {
  if (result === 'knockout' || result === 'submission') return colors.ko
  if (result === 'miss') return colors.textDim
  if (result === 'blocked') return colors.decision
  if (damage > 15) return colors.ko
  if (damage > 8) return colors.rivalry
  return colors.win
}

interface FightReplayProps {
  match: MatchResult
  fullMatch: Match | null
  fighter1: Fighter | null
  fighter2: Fighter | null
}

export default function FightReplay({ match, fullMatch, fighter1, fighter2 }: FightReplayProps) {
  const moments = useMemo(() => {
    if (fullMatch?.moments && fullMatch.moments.length > 0) {
      return fullMatch.moments
    }
    return generateMockMoments(match)
  }, [fullMatch, match])

  const [currentMomentIndex, setCurrentMomentIndex] = useState(-1)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const [f1Hp, setF1Hp] = useState(100)
  const [f2Hp, setF2Hp] = useState(100)
  const [f1Stamina, setF1Stamina] = useState(100)
  const [f2Stamina, setF2Stamina] = useState(100)
  const [f1Mana, setF1Mana] = useState(100)
  const [f2Mana, setF2Mana] = useState(100)
  const [currentRound, setCurrentRound] = useState(1)
  const [shakeLeft, setShakeLeft] = useState(false)
  const [shakeRight, setShakeRight] = useState(false)
  const [lungeLeft, setLungeLeft] = useState(false)
  const [lungeRight, setLungeRight] = useState(false)
  const [showFlash, setShowFlash] = useState(false)
  const [flashColor, setFlashColor] = useState(colors.ko)
  const [showFinisher, setShowFinisher] = useState(false)
  const [actionText, setActionText] = useState<{ text: string; color: string; big: boolean } | null>(null)
  const [combatLog, setCombatLog] = useState<Array<{ text: string; color: string; round: number }>>([])
  const [isComplete, setIsComplete] = useState(false)
  const logRef = useRef<HTMLDivElement>(null)

  const isF1Winner = match.winner_id === match.fighter1_id

  const resetState = useCallback(() => {
    setCurrentMomentIndex(-1)
    setF1Hp(100)
    setF2Hp(100)
    setF1Stamina(100)
    setF2Stamina(100)
    setF1Mana(100)
    setF2Mana(100)
    setCurrentRound(1)
    setShakeLeft(false)
    setShakeRight(false)
    setLungeLeft(false)
    setLungeRight(false)
    setShowFlash(false)
    setShowFinisher(false)
    setActionText(null)
    setCombatLog([])
    setIsComplete(false)
  }, [])

  const processMoment = useCallback((moment: FightMoment) => {
    const isF1Attacker = moment.attacker_id === match.fighter1_id
    const attackerName = isF1Attacker ? match.fighter1_name : match.fighter2_name
    const defenderName = isF1Attacker ? match.fighter2_name : match.fighter1_name

    setCurrentRound(moment.round_number)

    if (isF1Attacker) {
      setF1Hp(moment.attacker_hp)
      setF2Hp(moment.defender_hp)
      setF1Stamina(moment.attacker_stamina)
      setF2Stamina(moment.defender_stamina)
      setF1Mana(moment.attacker_mana)
      setF2Mana(moment.defender_mana)
    } else {
      setF2Hp(moment.attacker_hp)
      setF1Hp(moment.defender_hp)
      setF2Stamina(moment.attacker_stamina)
      setF1Stamina(moment.defender_stamina)
      setF2Mana(moment.attacker_mana)
      setF1Mana(moment.defender_mana)
    }

    const verb = getActionVerb(moment.result)
    const impactColor = getImpactColor(moment.result, moment.damage_dealt)
    const isFinisher = moment.result === 'knockout' || moment.result === 'submission'
    const isBigHit = moment.damage_dealt > 12

    if (isF1Attacker) {
      setLungeLeft(true)
      setTimeout(() => setLungeLeft(false), 300)
      if (moment.result === 'hit' || isFinisher) {
        setTimeout(() => {
          setShakeRight(true)
          setTimeout(() => setShakeRight(false), 400)
        }, 150)
      }
    } else {
      setLungeRight(true)
      setTimeout(() => setLungeRight(false), 300)
      if (moment.result === 'hit' || isFinisher) {
        setTimeout(() => {
          setShakeLeft(true)
          setTimeout(() => setShakeLeft(false), 400)
        }, 150)
      }
    }

    if (isBigHit || isFinisher) {
      setFlashColor(isFinisher ? colors.ko : impactColor)
      setShowFlash(true)
      setTimeout(() => setShowFlash(false), isFinisher ? 500 : 200)
    }

    let actionLine: string
    if (isFinisher) {
      actionLine = `${attackerName} ${moment.action}!`
    } else if (moment.result === 'miss') {
      actionLine = `${defenderName} ${verb} ${attackerName}'s ${moment.action}`
    } else if (moment.result === 'blocked') {
      actionLine = `${defenderName} ${verb} ${attackerName}'s ${moment.action}`
    } else {
      actionLine = `${attackerName} ${verb} with ${moment.action}`
    }

    setActionText({
      text: actionLine,
      color: impactColor,
      big: isBigHit || isFinisher,
    })

    setCombatLog(prev => [...prev, {
      text: actionLine + (moment.damage_dealt > 0 ? ` [-${moment.damage_dealt} HP]` : ''),
      color: impactColor,
      round: moment.round_number,
    }])

    if (isFinisher) {
      setTimeout(() => {
        setShowFinisher(true)
        setIsPlaying(false)
        setIsComplete(true)
      }, 800)
    }
  }, [match])

  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight
    }
  }, [combatLog])

  useEffect(() => {
    if (!isPlaying || currentMomentIndex >= moments.length - 1) return

    const baseDelay = 1800
    const delay = baseDelay / speed

    const timer = setTimeout(() => {
      const nextIndex = currentMomentIndex + 1
      setCurrentMomentIndex(nextIndex)
      processMoment(moments[nextIndex])
    }, delay)

    return () => clearTimeout(timer)
  }, [isPlaying, currentMomentIndex, moments, speed, processMoment])

  const handlePlay = () => {
    if (isComplete) {
      resetState()
      setTimeout(() => setIsPlaying(true), 50)
    } else {
      setIsPlaying(true)
    }
  }

  const handlePause = () => setIsPlaying(false)

  const handleRestart = () => {
    setIsPlaying(false)
    resetState()
  }

  const handleSpeedChange = () => {
    const speeds = [0.5, 1, 1.5, 2, 3]
    const currentIdx = speeds.indexOf(speed)
    setSpeed(speeds[(currentIdx + 1) % speeds.length])
  }

  const totalRounds = match.method === 'decision' ? 3 : match.round_ended

  return (
    <div style={{ position: 'relative', overflow: 'hidden' }}>
      <style>{REPLAY_KEYFRAMES}</style>

      {showFlash && (
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: withAlpha(flashColor, 0.15),
          zIndex: 10,
          pointerEvents: 'none',
          animation: 'flashFade 0.4s ease-out forwards',
          borderRadius: '8px',
        }} />
      )}

      <div style={{
        backgroundColor: colors.surface,
        borderRadius: '8px',
        border: `1px solid ${colors.border}`,
        overflow: 'hidden',
      }}>
        <RoundIndicator currentRound={currentRound} totalRounds={totalRounds} />

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1.2fr 1fr',
          gap: 0,
          minHeight: '420px',
          position: 'relative',
        }}>
          <FighterPanel
            fighterId={match.fighter1_id}
            name={match.fighter1_name}
            fighter={fighter1}
            hp={f1Hp}
            stamina={f1Stamina}
            mana={f1Mana}
            side="left"
            isShaking={shakeLeft}
            isLunging={lungeLeft}
            isWinner={isF1Winner}
            showFinisher={showFinisher}
          />

          <CenterArena
            actionText={actionText}
            showFinisher={showFinisher}
            match={match}
            isF1Winner={isF1Winner}
            currentMomentIndex={currentMomentIndex}
            totalMoments={moments.length}
          />

          <FighterPanel
            fighterId={match.fighter2_id}
            name={match.fighter2_name}
            fighter={fighter2}
            hp={f2Hp}
            stamina={f2Stamina}
            mana={f2Mana}
            side="right"
            isShaking={shakeRight}
            isLunging={lungeRight}
            isWinner={!isF1Winner}
            showFinisher={showFinisher}
          />
        </div>

        <CombatLog log={combatLog} logRef={logRef} />

        <PlaybackControls
          isPlaying={isPlaying}
          speed={speed}
          isComplete={isComplete}
          currentMomentIndex={currentMomentIndex}
          totalMoments={moments.length}
          onPlay={handlePlay}
          onPause={handlePause}
          onRestart={handleRestart}
          onSpeedChange={handleSpeedChange}
        />
      </div>
    </div>
  )
}

function RoundIndicator({ currentRound, totalRounds }: { currentRound: number; totalRounds: number }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: spacing.md,
      padding: `${spacing.sm} ${spacing.md}`,
      backgroundColor: colors.surfaceLight,
      borderBottom: `1px solid ${colors.border}`,
    }}>
      {Array.from({ length: totalRounds }, (_, i) => {
        const round = i + 1
        const isActive = round === currentRound
        const isPast = round < currentRound
        return (
          <div key={round} style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.xs,
          }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: fontSizes.xs,
              fontWeight: 'bold',
              backgroundColor: isActive
                ? withAlpha(colors.accent, 0.3)
                : isPast
                  ? withAlpha(colors.win, 0.2)
                  : withAlpha(colors.border, 0.5),
              border: isActive
                ? `2px solid ${colors.accent}`
                : isPast
                  ? `1px solid ${withAlpha(colors.win, 0.4)}`
                  : `1px solid ${colors.border}`,
              color: isActive ? colors.accent : isPast ? colors.win : colors.textDim,
              transition: 'all 0.3s ease',
              ...(isActive ? { boxShadow: `0 0 12px ${withAlpha(colors.accent, 0.4)}` } : {}),
            }}>
              {round}
            </div>
            {i < totalRounds - 1 && (
              <div style={{
                width: '24px',
                height: '2px',
                backgroundColor: isPast ? withAlpha(colors.win, 0.4) : colors.border,
              }} />
            )}
          </div>
        )
      })}
      <div style={{
        marginLeft: spacing.sm,
        fontSize: fontSizes.xs,
        color: colors.textMuted,
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
      }}>
        Round {currentRound}
      </div>
    </div>
  )
}

function FighterPanel({ fighterId, name, fighter, hp, stamina, mana, side, isShaking, isLunging, isWinner, showFinisher }: {
  fighterId: string
  name: string
  fighter: Fighter | null
  hp: number
  stamina: number
  mana: number
  side: 'left' | 'right'
  isShaking: boolean
  isLunging: boolean
  isWinner: boolean
  showFinisher: boolean
}) {
  const isLeft = side === 'left'
  const isLoser = showFinisher && !isWinner

  let transform = ''
  if (isShaking) {
    transform = 'translateX(0px)'
  } else if (isLunging) {
    transform = isLeft ? 'translateX(20px) scale(1.05)' : 'translateX(-20px) scale(1.05)'
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: spacing.lg,
      position: 'relative',
      background: isLeft
        ? `linear-gradient(135deg, ${withAlpha(colors.face, 0.05)}, transparent)`
        : `linear-gradient(225deg, ${withAlpha(colors.heel, 0.05)}, transparent)`,
    }}>
      {showFinisher && isWinner && (
        <div style={{
          position: 'absolute',
          top: spacing.sm,
          fontSize: fontSizes.xs,
          color: colors.accent,
          fontWeight: 'bold',
          textTransform: 'uppercase',
          letterSpacing: '0.15em',
          animation: 'pulseGlow 1.5s ease-in-out infinite',
        }}>
          WINNER
        </div>
      )}

      <div style={{
        animation: isShaking
          ? 'hitShake 0.4s ease-out'
          : undefined,
        transform: transform || undefined,
        transition: isLunging ? 'transform 0.2s ease-out' : 'transform 0.3s ease',
        filter: isLoser ? 'grayscale(0.6) brightness(0.5)' : undefined,
        ...(isLoser ? { transform: `rotate(${isLeft ? '-8' : '8'}deg) translateY(15px)` } : {}),
      }}>
        <div style={{
          position: 'relative',
          border: `3px solid ${isLoser ? colors.loss : isWinner && showFinisher ? colors.accent : withAlpha(colors.accent, 0.4)}`,
          borderRadius: '8px',
          overflow: 'hidden',
          ...(isWinner && showFinisher ? {
            boxShadow: `0 0 20px ${withAlpha(colors.accent, 0.5)}, 0 0 40px ${withAlpha(colors.accent, 0.2)}`,
          } : {}),
        }}>
          <FighterPortrait fighterId={fighterId} name={name} size={180} />
        </div>
      </div>

      <div style={{
        marginTop: spacing.sm,
        fontSize: fontSizes.md,
        fontWeight: 'bold',
        color: isLoser ? colors.textDim : colors.text,
        textAlign: 'center',
        textShadow: isWinner && showFinisher
          ? `0 0 10px ${withAlpha(colors.accent, 0.5)}`
          : undefined,
      }}>
        {name}
      </div>

      {fighter && (
        <div style={{
          fontSize: fontSizes.xs,
          color: colors.textDim,
          marginTop: '2px',
        }}>
          {fighter.record.wins}-{fighter.record.losses}-{fighter.record.draws}
        </div>
      )}

      <div style={{
        width: '100%',
        maxWidth: '200px',
        marginTop: spacing.md,
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        opacity: isLoser ? 0.4 : 1,
      }}>
        <ResourceBar label="HP" value={hp} max={100} color={hp > 60 ? colors.win : hp > 30 ? colors.rivalry : colors.loss} />
        <ResourceBar label="STA" value={stamina} max={100} color={colors.decision} />
        <ResourceBar label="MP" value={mana} max={100} color={colors.submission} />
      </div>
    </div>
  )
}

function ResourceBar({ label, value, max, color }: {
  label: string
  value: number
  max: number
  color: string
}) {
  const pct = Math.max(0, Math.min(100, (value / max) * 100))
  const isLow = pct < 25

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
      <span style={{
        fontSize: '0.6rem',
        color: colors.textDim,
        width: '24px',
        textAlign: 'right',
        fontWeight: 'bold',
        letterSpacing: '0.05em',
      }}>
        {label}
      </span>
      <div style={{
        flex: 1,
        height: '10px',
        backgroundColor: withAlpha(colors.border, 0.6),
        borderRadius: '3px',
        overflow: 'hidden',
        position: 'relative',
      }}>
        <div style={{
          width: `${pct}%`,
          height: '100%',
          backgroundColor: color,
          borderRadius: '3px',
          transition: 'width 0.5s ease, background-color 0.3s ease',
          boxShadow: isLow ? `0 0 6px ${withAlpha(color, 0.8)}` : undefined,
          animation: isLow ? 'barPulse 1s ease-in-out infinite' : undefined,
        }} />
        {isLow && (
          <div style={{
            position: 'absolute',
            inset: 0,
            background: `repeating-linear-gradient(90deg, transparent, transparent 4px, ${withAlpha(colors.loss, 0.1)} 4px, ${withAlpha(colors.loss, 0.1)} 8px)`,
            animation: 'dangerStripes 0.5s linear infinite',
          }} />
        )}
      </div>
      <span style={{
        fontSize: '0.6rem',
        color: isLow ? color : colors.textDim,
        width: '24px',
        fontWeight: 'bold',
        ...(isLow ? { animation: 'pulseGlow 1s ease-in-out infinite' } : {}),
      }}>
        {Math.round(value)}
      </span>
    </div>
  )
}

function CenterArena({ actionText, showFinisher, match, isF1Winner, currentMomentIndex, totalMoments }: {
  actionText: { text: string; color: string; big: boolean } | null
  showFinisher: boolean
  match: MatchResult
  isF1Winner: boolean
  currentMomentIndex: number
  totalMoments: number
}) {
  const winnerName = isF1Winner ? match.fighter1_name : match.fighter2_name
  const methodColor = METHOD_COLORS[match.method] || colors.ko
  const methodLabel = METHOD_LABELS[match.method] || match.method.toUpperCase()

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      borderLeft: `1px solid ${withAlpha(colors.border, 0.3)}`,
      borderRight: `1px solid ${withAlpha(colors.border, 0.3)}`,
      background: `radial-gradient(ellipse at center, ${withAlpha(colors.surfaceLight, 0.5)}, transparent)`,
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        left: '50%',
        transform: 'translateX(-50%)',
        width: '1px',
        height: '100%',
        background: `linear-gradient(to bottom, transparent, ${withAlpha(colors.accent, 0.1)}, transparent)`,
      }} />

      {currentMomentIndex < 0 && !showFinisher && (
        <div style={{
          textAlign: 'center',
          animation: 'fadeIn 0.5s ease',
        }}>
          <div style={{
            fontSize: fontSizes.lg,
            color: colors.accent,
            fontWeight: 'bold',
            textTransform: 'uppercase',
            letterSpacing: '0.15em',
            marginBottom: spacing.sm,
          }}>
            READY TO FIGHT
          </div>
          <div style={{
            fontSize: fontSizes.xs,
            color: colors.textDim,
          }}>
            Press play to start the replay
          </div>
        </div>
      )}

      {actionText && !showFinisher && (
        <div
          key={currentMomentIndex}
          style={{
            textAlign: 'center',
            padding: `${spacing.md} ${spacing.lg}`,
            maxWidth: '90%',
            animation: actionText.big ? 'bigHitText 0.6s ease-out' : 'actionPop 0.4s ease-out',
          }}
        >
          <div style={{
            fontSize: actionText.big ? fontSizes.xl : fontSizes.md,
            fontWeight: 'bold',
            color: actionText.color,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            textShadow: actionText.big
              ? `0 0 20px ${withAlpha(actionText.color, 0.6)}, 0 0 40px ${withAlpha(actionText.color, 0.3)}`
              : `0 0 8px ${withAlpha(actionText.color, 0.4)}`,
            lineHeight: 1.3,
          }}>
            {actionText.text}
          </div>
        </div>
      )}

      {showFinisher && (
        <div style={{
          textAlign: 'center',
          animation: 'finisherReveal 0.8s ease-out',
        }}>
          <div style={{
            fontSize: fontSizes.xxxl,
            fontWeight: 'bold',
            color: methodColor,
            textTransform: 'uppercase',
            letterSpacing: '0.2em',
            textShadow: `0 0 30px ${withAlpha(methodColor, 0.7)}, 0 0 60px ${withAlpha(methodColor, 0.4)}, 0 0 90px ${withAlpha(methodColor, 0.2)}`,
            marginBottom: spacing.md,
            animation: 'pulseGlow 2s ease-in-out infinite',
          }}>
            {methodLabel}
          </div>
          <div style={{
            fontSize: fontSizes.lg,
            color: colors.accent,
            fontWeight: 'bold',
            animation: 'fadeSlideUp 0.6s ease-out 0.4s both',
          }}>
            {winnerName} WINS
          </div>
        </div>
      )}

      <div style={{
        position: 'absolute',
        bottom: spacing.sm,
        fontSize: fontSizes.xs,
        color: colors.textDim,
      }}>
        {currentMomentIndex >= 0
          ? `${currentMomentIndex + 1} / ${totalMoments}`
          : `${totalMoments} moments`
        }
      </div>
    </div>
  )
}

function CombatLog({ log, logRef }: {
  log: Array<{ text: string; color: string; round: number }>
  logRef: React.RefObject<HTMLDivElement | null>
}) {
  if (log.length === 0) return null

  return (
    <div
      ref={logRef}
      style={{
        maxHeight: '120px',
        overflowY: 'auto',
        padding: `${spacing.sm} ${spacing.md}`,
        borderTop: `1px solid ${colors.border}`,
        backgroundColor: withAlpha(colors.background, 0.5),
      }}
    >
      {log.map((entry, i) => (
        <div key={i} style={{
          fontSize: fontSizes.xs,
          color: i === log.length - 1 ? entry.color : withAlpha(entry.color, 0.5),
          padding: '2px 0',
          display: 'flex',
          gap: spacing.sm,
          animation: i === log.length - 1 ? 'fadeIn 0.3s ease' : undefined,
        }}>
          <span style={{
            color: colors.textDim,
            flexShrink: 0,
            width: '24px',
          }}>
            R{entry.round}
          </span>
          <span>{entry.text}</span>
        </div>
      ))}
    </div>
  )
}

function PlaybackControls({ isPlaying, speed, isComplete, currentMomentIndex, totalMoments, onPlay, onPause, onRestart, onSpeedChange }: {
  isPlaying: boolean
  speed: number
  isComplete: boolean
  currentMomentIndex: number
  totalMoments: number
  onPlay: () => void
  onPause: () => void
  onRestart: () => void
  onSpeedChange: () => void
}) {
  const progress = totalMoments > 0 ? ((currentMomentIndex + 1) / totalMoments) * 100 : 0

  return (
    <div style={{
      padding: `${spacing.sm} ${spacing.md}`,
      borderTop: `1px solid ${colors.border}`,
      backgroundColor: colors.surfaceLight,
    }}>
      <div style={{
        height: '3px',
        backgroundColor: withAlpha(colors.border, 0.5),
        borderRadius: '2px',
        marginBottom: spacing.sm,
        overflow: 'hidden',
      }}>
        <div style={{
          width: `${progress}%`,
          height: '100%',
          backgroundColor: isComplete ? colors.accent : colors.win,
          borderRadius: '2px',
          transition: 'width 0.3s ease',
          ...(isComplete ? {
            background: `linear-gradient(90deg, ${colors.accentDim}, ${colors.accent}, ${colors.accentBright})`,
          } : {}),
        }} />
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: spacing.md,
      }}>
        <ControlButton onClick={onRestart} label="RESTART" />

        {isPlaying ? (
          <ControlButton onClick={onPause} label="PAUSE" primary />
        ) : (
          <ControlButton onClick={onPlay} label={isComplete ? 'REPLAY' : currentMomentIndex < 0 ? 'FIGHT' : 'RESUME'} primary />
        )}

        <ControlButton onClick={onSpeedChange} label={`${speed}x`} />
      </div>
    </div>
  )
}

function ControlButton({ onClick, label, primary }: {
  onClick: () => void
  label: string
  primary?: boolean
}) {
  const [hover, setHover] = useState(false)

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        padding: primary ? `${spacing.sm} ${spacing.xl}` : `${spacing.xs} ${spacing.md}`,
        backgroundColor: primary
          ? (hover ? colors.accent : withAlpha(colors.accent, 0.8))
          : (hover ? withAlpha(colors.border, 0.8) : withAlpha(colors.border, 0.4)),
        color: primary ? colors.background : colors.textMuted,
        border: primary ? `2px solid ${colors.accent}` : `1px solid ${colors.border}`,
        borderRadius: '4px',
        fontSize: primary ? fontSizes.sm : fontSizes.xs,
        fontWeight: 'bold',
        cursor: 'pointer',
        textTransform: 'uppercase',
        letterSpacing: '0.1em',
        fontFamily: 'inherit',
        transition: 'all 0.2s ease',
        ...(primary && hover ? {
          boxShadow: `0 0 15px ${withAlpha(colors.accent, 0.4)}`,
        } : {}),
      }}
    >
      {label}
    </button>
  )
}

const REPLAY_KEYFRAMES = `
@keyframes hitShake {
  0% { transform: translateX(0); }
  15% { transform: translateX(-12px) rotate(-2deg); }
  30% { transform: translateX(10px) rotate(1.5deg); }
  45% { transform: translateX(-6px) rotate(-1deg); }
  60% { transform: translateX(4px) rotate(0.5deg); }
  75% { transform: translateX(-2px); }
  100% { transform: translateX(0); }
}

@keyframes actionPop {
  0% { transform: scale(0.3); opacity: 0; }
  50% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}

@keyframes bigHitText {
  0% { transform: scale(0.1) rotate(-5deg); opacity: 0; }
  40% { transform: scale(1.4) rotate(2deg); opacity: 1; }
  60% { transform: scale(0.9) rotate(-1deg); }
  80% { transform: scale(1.1); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

@keyframes finisherReveal {
  0% { transform: scale(0) rotate(-10deg); opacity: 0; }
  50% { transform: scale(1.3) rotate(3deg); opacity: 1; }
  70% { transform: scale(0.9) rotate(-1deg); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}

@keyframes flashFade {
  0% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes pulseGlow {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes barPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes dangerStripes {
  from { transform: translateX(0); }
  to { transform: translateX(8px); }
}
`
