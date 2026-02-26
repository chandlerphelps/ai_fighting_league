# Frontend - Design Philosophy

## Aesthetic

- Dark theme — matches the league's gritty, underground fight aesthetic
- Minimal and clean — text and stats only, no images for v0
- Information-dense but scannable

## Principles

- All colors and fonts from `src/design-system.ts` — no hex codes
- Use `withAlpha(color, alpha)` for transparency
- No popup modals — keep everything on the page
- Read-only viewer — no forms, no user input, just navigation and display
- Mobile-friendly but desktop-first

## Page Hierarchy

1. **Dashboard** — today's fights, quick roster status, next event
2. **Fighter Profile** — deep dive on a single fighter
3. **Rankings** — ordered list with records and streaks
4. **Schedule/History** — navigate by date
5. **Fight Narrative** — full story for a single match
