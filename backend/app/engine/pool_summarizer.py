from collections import Counter

from app.engine.fighter_config import (
    ARCHETYPES_FEMALE,
    ARCHETYPES_MALE,
    OUTFIT_COLOR_PALETTE,
    HAIR_COLOR_BUCKETS,
    classify_hair_color,
)

REGION_MAP = {
    "East Asia": ["Japan", "China", "Korea", "Taiwan", "Mongolia"],
    "Southeast Asia": ["Thailand", "Vietnam", "Philippines", "Indonesia", "Myanmar", "Cambodia", "Malaysia", "Singapore"],
    "South Asia": ["India", "Pakistan", "Bangladesh", "Nepal", "Sri Lanka"],
    "Central Asia": ["Kazakhstan", "Uzbekistan"],
    "Middle East": ["Iran", "Turkey", "Iraq", "Saudi Arabia", "UAE", "Israel", "Lebanon", "Egypt"],
    "Eastern Europe": ["Russia", "Ukraine", "Poland", "Romania", "Czech", "Serbia", "Croatia", "Hungary", "Bulgaria"],
    "Western Europe": ["UK", "England", "France", "Germany", "Spain", "Italy", "Netherlands", "Belgium", "Portugal", "Switzerland", "Austria", "Ireland", "Scotland"],
    "Scandinavia": ["Sweden", "Norway", "Denmark", "Finland", "Iceland"],
    "North America": ["USA", "United States", "Canada", "Mexico"],
    "Central America": ["Guatemala", "Honduras", "Costa Rica", "Panama", "Cuba", "Puerto Rico", "Jamaica", "Dominican", "Haiti"],
    "South America": ["Brazil", "Argentina", "Colombia", "Chile", "Peru", "Venezuela", "Ecuador", "Bolivia", "Uruguay"],
    "Africa": ["Nigeria", "Kenya", "South Africa", "Ethiopia", "Ghana", "Senegal", "Morocco", "Congo", "Tanzania", "Cameroon"],
    "Oceania": ["Australia", "New Zealand", "Fiji", "Samoa", "Papua"],
}


def _classify_region(origin: str) -> str:
    if not origin:
        return "Unknown"
    origin_upper = origin.upper()
    for region, keywords in REGION_MAP.items():
        for kw in keywords:
            if kw.upper() in origin_upper:
                return region
    return "Other"


def _age_bracket(age: int) -> str:
    if age <= 22:
        return "18-22"
    if age <= 27:
        return "23-27"
    if age <= 32:
        return "28-32"
    return "33+"


def summarize_fighter_pool(fighters: list[dict], for_display: bool = False) -> str:
    if not fighters:
        return "No existing fighters in the roster."

    total = len(fighters)
    gender_counts = Counter(f.get("gender", "unknown") for f in fighters)
    archetype_counts = Counter(f.get("primary_archetype", "Unknown") for f in fighters)
    region_counts = Counter(_classify_region(f.get("origin", "")) for f in fighters)
    age_counts = Counter(_age_bracket(f.get("age", 25)) for f in fighters)

    outfit_colors = Counter(f.get("primary_outfit_color", "") for f in fighters if f.get("primary_outfit_color"))
    hair_buckets = Counter()
    for f in fighters:
        bucket = f.get("hair_color_bucket", "") or classify_hair_color(f.get("hair_color", ""))
        if bucket:
            hair_buckets[bucket] += 1
    hair_combos = Counter(
        f"{f.get('hair_style', '')} [{f.get('hair_color_bucket', '') or classify_hair_color(f.get('hair_color', ''))}]".strip()
        for f in fighters
        if f.get("hair_style") or f.get("hair_color")
    )
    face_adornments = Counter(
        f.get("face_adornment", "")
        for f in fighters
        if f.get("face_adornment") and f.get("face_adornment") != "none"
    )

    lines = [f"CURRENT ROSTER: {total} fighters"]
    lines.append(f"Gender: {', '.join(f'{g}: {c}' for g, c in gender_counts.most_common())}")

    lines.append("\nArchetype Distribution:")
    all_archetypes = set(ARCHETYPES_FEMALE + ARCHETYPES_MALE)
    for arch in sorted(all_archetypes):
        count = archetype_counts.get(arch, 0)
        lines.append(f"  {arch}: {count}")
    missing_archetypes = [a for a in all_archetypes if archetype_counts.get(a, 0) == 0]
    if missing_archetypes:
        lines.append(f"  MISSING: {', '.join(sorted(missing_archetypes))}")

    lines.append("\nGeographic Spread:")
    for region, count in region_counts.most_common():
        lines.append(f"  {region}: {count}")
    missing_regions = [r for r in REGION_MAP if region_counts.get(r, 0) == 0]
    if missing_regions:
        lines.append(f"  UNDERREPRESENTED: {', '.join(missing_regions)}")

    lines.append(f"\nAge Distribution: {', '.join(f'{b}: {c}' for b, c in sorted(age_counts.items()))}")

    lines.append("\n--- SIGNATURE VISUAL IDENTITY REGISTRY (DO NOT DUPLICATE) ---")

    if outfit_colors:
        lines.append("\nOutfit Colors Already Taken:")
        for color, count in outfit_colors.most_common():
            lines.append(f"  {color} ({count}x)")
        taken_lower = {c.lower() for c in outfit_colors}
        available = [c for c in OUTFIT_COLOR_PALETTE if c.lower() not in taken_lower]
        if available:
            lines.append(f"\nAvailable Palette Colors: {', '.join(available)}")

    if hair_buckets:
        lines.append("\nHair Color Buckets:")
        for bucket in HAIR_COLOR_BUCKETS:
            count = hair_buckets.get(bucket, 0)
            lines.append(f"  {bucket}: {count}")

    if hair_combos:
        lines.append("\nHair Style+Bucket Combos Already Taken:")
        for combo, count in hair_combos.most_common():
            lines.append(f"  {combo} ({count}x)")

    if face_adornments:
        lines.append("\nFace Adornments Already Taken:")
        for adorn, count in face_adornments.most_common():
            lines.append(f"  {adorn} ({count}x)")

    if not outfit_colors and not hair_combos and not face_adornments:
        lines.append("  (No signature data yet - first generation)")

    if for_display:
        lines.append("\n--- EXISTING FIGHTERS ---")
        for f in fighters:
            sig_parts = []
            if f.get("primary_outfit_color"):
                sig_parts.append(f"color:{f['primary_outfit_color']}")
            if f.get("hair_style") or f.get("hair_color"):
                bucket = f.get("hair_color_bucket", "") or classify_hair_color(f.get("hair_color", ""))
                sig_parts.append(f"hair:{f.get('hair_style', '')} [{bucket}]".strip())
            if f.get("face_adornment") and f.get("face_adornment") != "none":
                sig_parts.append(f"face:{f['face_adornment']}")
            sig = f" [{', '.join(sig_parts)}]" if sig_parts else ""
            lines.append(
                f"  {f.get('ring_name', '?')} - {f.get('gender', '?')} "
                f"{f.get('primary_archetype', '?')}/{f.get('subtype', '?')} "
                f"from {f.get('origin', '?')}{sig}"
            )

    return "\n".join(lines)
