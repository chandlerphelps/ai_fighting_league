import { Link } from 'react-router-dom'
import { colors, fontSizes } from '../design-system'

interface FighterLinkProps {
  id: string
  name: string
  record?: { wins: number; losses: number; draws: number }
}

export default function FighterLink({ id, name, record }: FighterLinkProps) {
  return (
    <span>
      <Link to={`/fighter/${id}`} style={{ color: colors.accent }}>
        {name}
      </Link>
      {record && (
        <span style={{ color: colors.textMuted, fontSize: fontSizes.xs, marginLeft: '6px' }}>
          ({record.wins}-{record.losses}-{record.draws})
        </span>
      )}
    </span>
  )
}
