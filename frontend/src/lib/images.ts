export function slugify(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
}

export function fighterImagePath(fighterId: string, ringName: string, tier: string): string {
  const slug = slugify(ringName)
  const base = slug ? `${fighterId}_${slug}` : fighterId
  return `/data/fighters/${base}_${tier}.png`
}
