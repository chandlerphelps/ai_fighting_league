import random

from app.engine.fighter_config import (
    _roll_body_traits,
    _build_body_directive,
    _build_body_shape_line,
    _build_nsfw_anatomy_line,
    _roll_subtype,
    _find_subtype,
)
from app.prompts.fighter_prompts import (
    build_generate_fighter_prompt,
    build_plan_roster_prompt,
)
from app.prompts.outfit_prompts import build_tier_prompt
from app.prompts.image_builders import (
    _build_charsheet_prompt,
    build_body_reference_prompt,
)


SAMPLE_FEMALE_TRAITS = {
    "height_inches": 65,
    "body_profile": "Athletic",
    "waist": "narrow",
    "abs_tone": "toned and defined",
    "body_fat_pct": "athletic 17-20%",
    "butt_size": "medium round",
    "breast_size": "medium",
    "face_shape": "sharp angular",
    "eye_shape": "almond",
    "makeup_level": "light",
    "nipple_size": "medium",
    "vulva_type": "tucked pussy, small labia",
    "subtype": "Femme Fatale",
    "height": "5'5\"",
    "weight": "128 lbs",
}

SAMPLE_FEMALE_CHARACTER_SUMMARY = {
    "ring_name": "Scarlet",
    "primary_archetype": "Siren",
    "subtype": "Femme Fatale",
    "personality": "cold, calculating predator",
    "iconic_features": "red scar across left cheek, gold choker, crimson nails",
    "image_prompt_body_parts": "athletic build, fair skin, long black hair, sharp angular face",
    "image_prompt_expression": "predatory smile with cold blue eyes",
    "body_type_details": SAMPLE_FEMALE_TRAITS,
}


class TestFemaleBodyDirective:
    def test_contains_breast_size(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "Breast size: medium" in result

    def test_contains_height_weight(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "5'5\"" in result
        assert "128 lbs" in result

    def test_contains_body_profile(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "Athletic" in result

    def test_contains_waist(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "narrow" in result

    def test_contains_abs_tone(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "toned and defined" in result

    def test_contains_butt_size(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "medium round" in result

    def test_contains_face_and_eyes(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "sharp angular" in result
        assert "almond" in result

    def test_contains_makeup(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "light" in result

    def test_contains_attractive_lens(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        assert "attractive" in result.lower()

    def test_full_snapshot(self):
        result = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        expected = (
            "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):\n"
            "- Build: Athletic\n"
            "- Height: 5'5\"\n"
            "- Weight: 128 lbs\n"
            "- Breast size: medium\n"
            "- Waist: narrow\n"
            "- Abs/core: toned and defined\n"
            "- Body fat: athletic 17-20%\n"
            "- Butt: medium round\n"
            "- Face: sharp angular, almond eyes\n"
            "- Makeup: light — subtle enhancement, lip tint, light mascara\n"
            "\nThe height and weight are EXACT — use these values directly.\n"
            "Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.\n"
            "IMPORTANT: Interpret ALL facial and body traits through an attractive lens. "
            "Every combination should result in a beautiful, appealing character."
        )
        assert result == expected


class TestFemaleBodyShapeLine:
    def test_contains_breasts_and_butt(self):
        result = _build_body_shape_line(SAMPLE_FEMALE_TRAITS)
        assert "breasts" in result
        assert "butt" in result

    def test_snapshot(self):
        result = _build_body_shape_line(SAMPLE_FEMALE_TRAITS)
        assert result == "medium breasts, medium round butt"


class TestFemaleNsfwAnatomyLine:
    def test_contains_all_parts(self):
        result = _build_nsfw_anatomy_line(SAMPLE_FEMALE_TRAITS)
        assert "breasts" in result
        assert "nipples" in result
        assert "butt" in result
        assert "pussy" in result

    def test_snapshot(self):
        result = _build_nsfw_anatomy_line(SAMPLE_FEMALE_TRAITS)
        expected = "medium breasts, medium nipples, medium round butt, tucked pussy, small labia"
        assert result == expected


class TestFemaleRollBodyTraits:
    def test_deterministic_with_seed(self):
        random.seed(42)
        traits1 = _roll_body_traits("Siren")
        random.seed(42)
        traits2 = _roll_body_traits("Siren")
        assert traits1 == traits2

    def test_has_female_traits(self):
        random.seed(42)
        traits = _roll_body_traits("Siren")
        assert "breast_size" in traits
        assert "nipple_size" in traits
        assert "vulva_type" in traits
        assert "butt_size" in traits
        assert "waist" in traits
        assert "height" in traits
        assert "weight" in traits

    def test_siren_seed_42_snapshot(self):
        random.seed(42)
        traits = _roll_body_traits("Siren")
        assert traits["body_profile"] in ("Petite", "Slim", "Athletic", "Curvy")
        assert traits["breast_size"] in ("barely there", "small perky", "medium", "large", "very large")


class TestFemaleCharsheetPrompt:
    def test_sfw_contains_body_parts(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build, fair skin",
            clothing="red crop top, black shorts",
            expression="predatory smile",
            personality_pose="hands on hips",
            tier="sfw",
            gender="female",
            skimpiness_level=2,
            body_type_details=SAMPLE_FEMALE_TRAITS,
        )
        assert "athletic build" in result["full_prompt"]
        assert "medium breasts" in result["full_prompt"]

    def test_nsfw_contains_anatomy(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build, fair skin",
            clothing="gold choker",
            expression="predatory smile",
            personality_pose="hands on hips",
            tier="nsfw",
            gender="female",
            skimpiness_level=2,
            body_type_details=SAMPLE_FEMALE_TRAITS,
        )
        assert "nipples" in result["full_prompt"]
        assert "pussy" in result["full_prompt"]

    def test_sfw_no_anatomy_section(self):
        result = _build_charsheet_prompt(
            body_parts="athletic build, fair skin",
            clothing="red crop top, black shorts",
            expression="predatory smile",
            tier="sfw",
            gender="female",
            skimpiness_level=2,
            body_type_details=SAMPLE_FEMALE_TRAITS,
        )
        assert "[ANATOMY]" not in result["full_prompt"]
        assert "[ANATOMY EMPHASIS]" not in result["full_prompt"]


class TestFemaleBodyReference:
    def test_contains_female_panels(self):
        result = build_body_reference_prompt(
            body_parts="athletic build, fair skin",
            expression="predatory smile",
            gender="female",
            body_type_details=SAMPLE_FEMALE_TRAITS,
        )
        assert "breasts" in result["full_prompt"]
        assert "nipples" in result["full_prompt"]
        assert "pussy" in result["full_prompt"]
        assert "FACE" in result["full_prompt"]
        assert "BUTT" in result["full_prompt"]
        assert "INTIMATE" in result["full_prompt"]

    def test_has_five_panels(self):
        result = build_body_reference_prompt(
            body_parts="athletic build, fair skin",
            expression="predatory smile",
            gender="female",
            body_type_details=SAMPLE_FEMALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "[TOP-LEFT: FACE]" in prompt
        assert "[TOP-CENTER: REAR ANGLED VIEW]" in prompt
        assert "[TOP-RIGHT: CHEST AND TORSO]" in prompt
        assert "[BOTTOM-LEFT: BUTT]" in prompt
        assert "[BOTTOM-RIGHT: INTIMATE]" in prompt


class TestFemaleOutfitPrompts:
    def test_sfw_tier_snapshot_structure(self):
        result = build_tier_prompt(
            tier="sfw",
            skimpiness_level=2,
            character_summary=SAMPLE_FEMALE_CHARACTER_SUMMARY,
        )
        assert "Sporty & Attractive" in result
        assert "ring_attire_sfw" in result
        assert "image_prompt_clothing_sfw" in result
        assert "Scarlet" in result

    def test_barely_tier_snapshot_structure(self):
        result = build_tier_prompt(
            tier="barely",
            skimpiness_level=2,
            character_summary=SAMPLE_FEMALE_CHARACTER_SUMMARY,
        )
        assert "Risqué" in result
        assert "ring_attire" in result
        assert "medium breasts" in result

    def test_nsfw_tier_snapshot_structure(self):
        result = build_tier_prompt(
            tier="nsfw",
            skimpiness_level=2,
            character_summary=SAMPLE_FEMALE_CHARACTER_SUMMARY,
        )
        assert "Confident" in result
        assert "ring_attire_nsfw" in result
        assert "nipples" in result
        assert "pussy" in result

    def test_sfw_no_nsfw_anatomy_line(self):
        result = build_tier_prompt(
            tier="sfw",
            skimpiness_level=2,
            character_summary=SAMPLE_FEMALE_CHARACTER_SUMMARY,
        )
        assert "medium nipples" not in result
        assert "tucked pussy, small labia" not in result


class TestFemaleGenerateFighterPrompt:
    def test_contains_philosophy(self):
        result = build_generate_fighter_prompt(
            archetype_text="Primary archetype: Siren",
            existing_roster_text="",
            blueprint_text="",
            body_directive=_build_body_directive(SAMPLE_FEMALE_TRAITS),
            supernatural_instruction="This fighter has NO supernatural abilities.",
            min_total_stats=180,
            max_total_stats=280,
        )
        assert "Female Characters Are Attractive" in result
        assert "Sex Appeal" in result

    def test_contains_body_directive(self):
        directive = _build_body_directive(SAMPLE_FEMALE_TRAITS)
        result = build_generate_fighter_prompt(
            archetype_text="Primary archetype: Siren",
            existing_roster_text="",
            blueprint_text="",
            body_directive=directive,
            supernatural_instruction="",
            min_total_stats=180,
            max_total_stats=280,
        )
        assert "Breast size: medium" in result
        assert "BODY TYPE DIRECTIVE" in result


class TestPlanRosterPrompt:
    def test_contains_all_female(self):
        random.seed(42)
        result = build_plan_roster_prompt(8)
        assert "ALL fighters must be female" in result

    def test_contains_archetype_list(self):
        random.seed(42)
        result = build_plan_roster_prompt(8)
        assert "Siren" in result
        assert "Witch" in result


class TestFemaleSubtypes:
    def test_roll_subtype_siren(self):
        random.seed(42)
        sub = _roll_subtype("Siren")
        assert sub is not None
        assert "name" in sub
        assert sub["name"] in ("Chanteuse", "Femme Fatale", "Temptress", "Enchantress", "Muse")

    def test_find_subtype_siren(self):
        sub = _find_subtype("Siren", "Femme Fatale")
        assert sub is not None
        assert sub["name"] == "Femme Fatale"


SAMPLE_MALE_TRAITS = {
    "height_inches": 74,
    "body_profile": "Muscular",
    "build_type": "thick and powerful",
    "muscle_definition": "heavily muscled",
    "body_fat_pct": "athletic 15-18%",
    "shoulder_width": "very broad",
    "chest_build": "barrel-chested",
    "waist": "thick core",
    "face_shape": "square jaw",
    "eye_expression": "predatory",
    "facial_hair": "stubble",
    "subtype": "Enforcer",
    "height": "6'2\"",
    "weight": "235 lbs",
}

SAMPLE_MALE_CHARACTER_SUMMARY = {
    "ring_name": "Ironjaw",
    "primary_archetype": "Brute",
    "subtype": "Enforcer",
    "personality": "silent enforcer who speaks with his fists",
    "iconic_features": "cauliflower ears, broken nose, knuckle tattoos",
    "image_prompt_body_parts": "massive build, pale skin, shaved head, square jaw, scar across bridge of nose",
    "image_prompt_expression": "dead-eyed stare with clenched jaw",
    "body_type_details": SAMPLE_MALE_TRAITS,
    "gender": "male",
}


class TestMaleBodyDirective:
    def test_no_breast_references(self):
        result = _build_body_directive(SAMPLE_MALE_TRAITS)
        assert "breast" not in result.lower()
        assert "nipple" not in result.lower()
        assert "vulva" not in result.lower()
        assert "pussy" not in result.lower()
        assert "makeup" not in result.lower()

    def test_contains_male_traits(self):
        result = _build_body_directive(SAMPLE_MALE_TRAITS)
        assert "barrel-chested" in result
        assert "very broad" in result
        assert "heavily muscled" in result
        assert "thick and powerful" in result
        assert "stubble" in result
        assert "predatory" in result

    def test_contains_dangerous_lens(self):
        result = _build_body_directive(SAMPLE_MALE_TRAITS)
        assert "DANGEROUS" in result
        assert "IMPOSING" in result
        assert "threatening" in result

    def test_contains_height_weight(self):
        result = _build_body_directive(SAMPLE_MALE_TRAITS)
        assert "6'2\"" in result
        assert "235 lbs" in result

    def test_full_snapshot(self):
        result = _build_body_directive(SAMPLE_MALE_TRAITS)
        expected = (
            "BODY TYPE DIRECTIVE (you MUST incorporate these exact physical traits):\n"
            "- Build: Muscular — thick and powerful\n"
            "- Height: 6'2\"\n"
            "- Weight: 235 lbs\n"
            "- Muscle definition: heavily muscled\n"
            "- Shoulders: very broad\n"
            "- Chest: barrel-chested\n"
            "- Waist: thick core\n"
            "- Body fat: athletic 15-18%\n"
            "- Face: square jaw, predatory eyes\n"
            "- Facial hair: stubble\n"
            "\nThe height and weight are EXACT — use these values directly.\n"
            "Work the other traits naturally into image_prompt_body_parts and image_prompt_expression.\n"
            "IMPORTANT: Interpret ALL traits through a DANGEROUS, IMPOSING lens. "
            "Every combination should result in a threatening, confident character who looks like "
            "someone you would cross the street to avoid."
        )
        assert result == expected


class TestMaleBodyShapeLine:
    def test_no_breast_references(self):
        result = _build_body_shape_line(SAMPLE_MALE_TRAITS)
        assert "breast" not in result.lower()

    def test_contains_chest_and_shoulders(self):
        result = _build_body_shape_line(SAMPLE_MALE_TRAITS)
        assert "barrel-chested" in result
        assert "very broad" in result

    def test_snapshot(self):
        result = _build_body_shape_line(SAMPLE_MALE_TRAITS)
        assert result == "barrel-chested chest, very broad shoulders"


class TestMaleNsfwAnatomyLine:
    def test_no_female_anatomy(self):
        result = _build_nsfw_anatomy_line(SAMPLE_MALE_TRAITS)
        assert "breast" not in result.lower()
        assert "nipple" not in result.lower()
        assert "vulva" not in result.lower()
        assert "pussy" not in result.lower()

    def test_contains_male_physique(self):
        result = _build_nsfw_anatomy_line(SAMPLE_MALE_TRAITS)
        assert "chest" in result
        assert "shoulders" in result


class TestMaleRollBodyTraits:
    def test_deterministic_with_seed(self):
        random.seed(42)
        traits1 = _roll_body_traits("Brute", gender="male")
        random.seed(42)
        traits2 = _roll_body_traits("Brute", gender="male")
        assert traits1 == traits2

    def test_has_male_traits_not_female(self):
        random.seed(42)
        traits = _roll_body_traits("Brute", gender="male")
        assert "chest_build" in traits
        assert "muscle_definition" in traits
        assert "shoulder_width" in traits
        assert "facial_hair" in traits
        assert "eye_expression" in traits
        assert "build_type" in traits
        assert "breast_size" not in traits
        assert "nipple_size" not in traits
        assert "vulva_type" not in traits
        assert "makeup_level" not in traits
        assert "eye_shape" not in traits

    def test_brute_body_profile(self):
        random.seed(42)
        traits = _roll_body_traits("Brute", gender="male")
        assert traits["body_profile"] in ("Lean", "Athletic", "Muscular", "Massive")

    def test_male_weight_heavier_than_female(self):
        random.seed(42)
        male_traits = _roll_body_traits("Brute", gender="male")
        random.seed(42)
        female_traits = _roll_body_traits("Siren", gender="female")
        male_weight = int(male_traits["weight"].split()[0])
        female_weight = int(female_traits["weight"].split()[0])
        assert male_weight > female_weight

    def test_male_height_taller_range(self):
        random.seed(42)
        traits = _roll_body_traits("Brute", gender="male")
        assert traits["height_inches"] >= 72
        assert traits["height_inches"] <= 78


class TestMaleSubtypes:
    def test_roll_subtype_brute(self):
        random.seed(42)
        sub = _roll_subtype("Brute", gender="male")
        assert sub is not None
        assert sub["name"] in ("Berserker", "Enforcer", "Juggernaut", "Brawler", "Mauler")

    def test_find_subtype_brute(self):
        sub = _find_subtype("Brute", "Enforcer", gender="male")
        assert sub is not None
        assert sub["name"] == "Enforcer"

    def test_male_subtype_not_in_female(self):
        sub = _find_subtype("Brute", "Enforcer", gender="female")
        assert sub is None

    def test_female_subtype_not_in_male(self):
        sub = _find_subtype("Siren", "Femme Fatale", gender="male")
        assert sub is None

    def test_all_male_archetypes_have_subtypes(self):
        from app.engine.fighter_config import ARCHETYPES_MALE, ARCHETYPE_SUBTYPES_MALE
        for arch in ARCHETYPES_MALE:
            assert arch in ARCHETYPE_SUBTYPES_MALE, f"Missing male subtypes for {arch}"
            assert len(ARCHETYPE_SUBTYPES_MALE[arch]) >= 4, f"Need at least 4 subtypes for {arch}"


class TestMaleCharsheetPrompt:
    def test_sfw_no_female_anatomy(self):
        result = _build_charsheet_prompt(
            body_parts="massive build, pale skin, shaved head",
            clothing="tactical vest, combat boots, cargo pants",
            expression="dead-eyed stare",
            personality_pose="cracking knuckles",
            tier="sfw",
            gender="male",
            skimpiness_level=2,
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "breast" not in prompt.lower()
        assert "nipple" not in prompt.lower()
        assert "pussy" not in prompt.lower()
        assert "vulva" not in prompt.lower()

    def test_sfw_contains_male_body(self):
        result = _build_charsheet_prompt(
            body_parts="massive build, pale skin, shaved head",
            clothing="tactical vest, combat boots, cargo pants",
            expression="dead-eyed stare",
            personality_pose="cracking knuckles",
            tier="sfw",
            gender="male",
            skimpiness_level=2,
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "barrel-chested" in prompt
        assert "very broad" in prompt

    def test_barely_tier_no_female_anatomy(self):
        result = _build_charsheet_prompt(
            body_parts="massive build, pale skin, shaved head",
            clothing="fight trunks, hand wraps",
            expression="dead-eyed stare",
            personality_pose="guard stance",
            tier="barely",
            gender="male",
            skimpiness_level=2,
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "breast" not in prompt.lower()
        assert "pussy" not in prompt.lower()


class TestMaleBodyReference:
    def test_three_panels_not_five(self):
        result = build_body_reference_prompt(
            body_parts="massive build, pale skin, shaved head",
            expression="dead-eyed stare",
            gender="male",
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "[LEFT: FACE]" in prompt
        assert "[CENTER: FRONT BODY]" in prompt
        assert "[RIGHT: BACK BODY]" in prompt
        assert "[BOTTOM-LEFT: BUTT]" not in prompt
        assert "[BOTTOM-RIGHT: INTIMATE]" not in prompt

    def test_no_female_anatomy(self):
        result = build_body_reference_prompt(
            body_parts="massive build, pale skin, shaved head",
            expression="dead-eyed stare",
            gender="male",
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "breast" not in prompt.lower()
        assert "pussy" not in prompt.lower()
        assert "vulva" not in prompt.lower()
        assert "nipple" not in prompt.lower()
        assert "spread" not in prompt.lower()

    def test_in_underwear(self):
        result = build_body_reference_prompt(
            body_parts="massive build, pale skin, shaved head",
            expression="dead-eyed stare",
            gender="male",
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"]
        assert "boxer briefs" in prompt.lower()

    def test_no_anatomy_line(self):
        result = build_body_reference_prompt(
            body_parts="massive build, pale skin, shaved head",
            expression="dead-eyed stare",
            gender="male",
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        assert result["anatomy"] == ""


class TestMaleOutfitPrompts:
    def test_sfw_uses_male_skimpiness(self):
        result = build_tier_prompt(
            tier="sfw",
            skimpiness_level=2,
            character_summary=SAMPLE_MALE_CHARACTER_SUMMARY,
        )
        assert "Combat Ready" in result
        assert "Ironjaw" in result
        assert "breast" not in result.lower()

    def test_barely_tier_shirtless(self):
        result = build_tier_prompt(
            tier="barely",
            skimpiness_level=2,
            character_summary=SAMPLE_MALE_CHARACTER_SUMMARY,
        )
        assert "Bare-Knuckle" in result
        assert "Shirtless" in result

    def test_nsfw_falls_back_to_barely(self):
        result = build_tier_prompt(
            tier="nsfw",
            skimpiness_level=2,
            character_summary=SAMPLE_MALE_CHARACTER_SUMMARY,
        )
        assert "Bare-Knuckle" in result
        assert "ring_attire" in result
        assert "pussy" not in result.lower()
        assert "nude" not in result.lower()

    def test_barely_pose_not_flirty(self):
        result = build_tier_prompt(
            tier="barely",
            skimpiness_level=2,
            character_summary=SAMPLE_MALE_CHARACTER_SUMMARY,
        )
        assert "flirty" not in result.lower()
        assert "intimidating" in result.lower() or "powerful" in result.lower()


class TestMaleGenerateFighterPrompt:
    def test_uses_male_philosophy(self):
        result = build_generate_fighter_prompt(
            archetype_text="Primary archetype: Brute",
            existing_roster_text="",
            blueprint_text="",
            body_directive=_build_body_directive(SAMPLE_MALE_TRAITS),
            supernatural_instruction="This fighter has NO supernatural abilities.",
            min_total_stats=180,
            max_total_stats=280,
            gender="male",
        )
        assert "Male Characters Are DANGEROUS" in result
        assert "Female Characters Are Attractive" not in result

    def test_no_female_body_directive_in_male(self):
        result = build_generate_fighter_prompt(
            archetype_text="Primary archetype: Brute",
            existing_roster_text="",
            blueprint_text="",
            body_directive=_build_body_directive(SAMPLE_MALE_TRAITS),
            supernatural_instruction="",
            min_total_stats=180,
            max_total_stats=280,
            gender="male",
        )
        assert "Breast size" not in result
        assert "barrel-chested" in result
        assert "DANGEROUS" in result

    def test_male_stat_hints(self):
        result = build_generate_fighter_prompt(
            archetype_text="Primary archetype: Brute",
            existing_roster_text="",
            blueprint_text="",
            body_directive=_build_body_directive(SAMPLE_MALE_TRAITS),
            supernatural_instruction="",
            min_total_stats=180,
            max_total_stats=280,
            gender="male",
        )
        assert "Brute has high power/toughness" in result


class TestNegativeMaleFemaleLeaks:
    FEMALE_ONLY_TERMS = ["breast", "nipple", "vulva", "pussy", "areola", "clitoris", "labia"]

    def test_male_body_directive_no_female_terms(self):
        result = _build_body_directive(SAMPLE_MALE_TRAITS).lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in result, f"Found '{term}' in male body directive"

    def test_male_body_shape_line_no_female_terms(self):
        result = _build_body_shape_line(SAMPLE_MALE_TRAITS).lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in result, f"Found '{term}' in male body shape line"

    def test_male_anatomy_line_no_female_terms(self):
        result = _build_nsfw_anatomy_line(SAMPLE_MALE_TRAITS).lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in result, f"Found '{term}' in male anatomy line"

    def test_male_body_ref_no_female_terms(self):
        result = build_body_reference_prompt(
            body_parts="massive build, pale skin",
            expression="dead stare",
            gender="male",
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"].lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in prompt, f"Found '{term}' in male body ref prompt"

    def test_male_charsheet_sfw_no_female_terms(self):
        result = _build_charsheet_prompt(
            body_parts="massive build, pale skin",
            clothing="tactical vest",
            expression="dead stare",
            tier="sfw",
            gender="male",
            skimpiness_level=2,
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"].lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in prompt, f"Found '{term}' in male SFW charsheet"

    def test_male_charsheet_barely_no_female_terms(self):
        result = _build_charsheet_prompt(
            body_parts="massive build, pale skin",
            clothing="fight trunks",
            expression="dead stare",
            tier="barely",
            gender="male",
            skimpiness_level=2,
            body_type_details=SAMPLE_MALE_TRAITS,
        )
        prompt = result["full_prompt"].lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in prompt, f"Found '{term}' in male barely charsheet"

    def test_male_generate_fighter_prompt_no_female_terms(self):
        result = build_generate_fighter_prompt(
            archetype_text="Primary archetype: Brute",
            existing_roster_text="",
            blueprint_text="",
            body_directive=_build_body_directive(SAMPLE_MALE_TRAITS),
            supernatural_instruction="",
            min_total_stats=180,
            max_total_stats=280,
            gender="male",
        ).lower()
        for term in self.FEMALE_ONLY_TERMS:
            assert term not in result, f"Found '{term}' in male generate fighter prompt"

    def test_rolled_male_traits_no_female_keys(self):
        random.seed(42)
        traits = _roll_body_traits("Brute", gender="male")
        female_keys = {"breast_size", "nipple_size", "vulva_type", "makeup_level", "eye_shape"}
        for key in female_keys:
            assert key not in traits, f"Found female key '{key}' in male traits"

    def test_all_male_archetypes_produce_clean_traits(self):
        from app.engine.fighter_config import ARCHETYPES_MALE
        for i, arch in enumerate(ARCHETYPES_MALE):
            random.seed(i)
            arch_name = arch.replace("The ", "")
            traits = _roll_body_traits(arch_name, gender="male")
            assert "breast_size" not in traits, f"{arch} produced breast_size"
            assert "nipple_size" not in traits, f"{arch} produced nipple_size"
            assert "vulva_type" not in traits, f"{arch} produced vulva_type"
            assert "chest_build" in traits, f"{arch} missing chest_build"
            assert "muscle_definition" in traits, f"{arch} missing muscle_definition"
