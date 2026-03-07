from .archetypes import (
    TECH_LEVELS,
    ARCHETYPE_DESCRIPTIONS,
    ARCHETYPES_FEMALE,
    ARCHETYPES_MALE,
    ARCHETYPE_SUBTYPES,
    ARCHETYPE_SUBTYPES_MALE,
)

from .body_data import (
    BODY_TRAIT_OPTIONS,
    MALE_BODY_TRAIT_OPTIONS,
    BODY_PROFILES,
    MALE_BODY_PROFILES,
    ARCHETYPE_BODY_PROFILE_WEIGHTS,
    MALE_ARCHETYPE_BODY_PROFILE_WEIGHTS,
    ARCHETYPE_HEIGHT_RANGES,
    MALE_ARCHETYPE_HEIGHT_RANGES,
    ARCHETYPE_BODY_WEIGHTS,
    MALE_ARCHETYPE_BODY_WEIGHTS,
    MAKEUP_DESCRIPTIONS,
)

from .body import (
    _roll_subtype,
    _find_subtype,
    _weighted_choice,
    _roll_body_profile,
    _roll_body_traits,
    _build_body_directive,
    _build_body_shape_line,
    _build_nsfw_anatomy_line,
    get_adornment_coverage,
    ADORNMENT_COVERAGE,
    build_clothing_coverage_annotations,
)

from .outfits import (
    load_outfit_options,
    filter_outfit_options,
    load_exotic_outfit_options,
    filter_exotic_for_fighter,
    SKIMPINESS_LEVELS,
    MALE_SKIMPINESS_LEVELS,
    FIT_STYLES,
    TRANSPARENCY_OPTIONS,
    _roll_fit_style,
    _roll_transparency,
    _roll_skimpiness,
    OUTFIT_COLOR_PALETTE,
    OUTFIT_COVERABLE_TRAITS_FEMALE,
    OUTFIT_COVERABLE_TRAITS_MALE,
    VALID_COVERAGE_STATES,
    validate_outfit_coverage,
)

from .hair import (
    HAIR_COLOR_BUCKETS,
    _HAIR_BUCKET_KEYWORDS,
    classify_hair_color,
)

from .stats import (
    ARCHETYPE_STAT_WEIGHTS,
    GENDER_FLAT_BONUS,
    GENDER_GUILE_RANGE,
    GENDER_SUPERNATURAL_RANGE,
    generate_archetype_stats,
)
