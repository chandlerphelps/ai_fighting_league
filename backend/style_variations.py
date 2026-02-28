import json
from pathlib import Path

FIGHTER_FILE = (
    Path(__file__).parent.parent / "data" / "fighters" / "f_34d29b70_venom_kiss.json"
)

with open(FIGHTER_FILE) as f:
    fighter = json.load(f)

OLD_STYLE_HEAD = (
    "western action-cartoon style, bold shape design, clean linework, "
    "strong facial expression, graphic readability, low detail, "
    "strictly female character, feminine curves and anatomy, "
    "character design reference sheet, character model sheet, "
    "character reference sheet turnaround, three full-body views of the exact same character side by side: "
    "front-facing view on the left, three-quarter angle view in the center, rear view on the right, "
    "consistent pose and outfit across all three views, full body head to toe visible in each panel, "
    "standing tall at full height, plain flat color background, organized reference sheet layout"
)

OLD_STYLE_HEAD_NSFW = (
    "explicit uncensored NSFW, full frontal female nudity, fully naked woman, "
    "western action-cartoon style, bold shape design, clean linework, "
    "strong facial expression, graphic readability, low detail, "
    "strictly female character, feminine curves and anatomy, "
    "character design reference sheet, character model sheet, "
    "character reference sheet turnaround, three full-body views of the exact same character side by side: "
    "front-facing view on the left, three-quarter angle view in the center, rear view on the right, "
    "consistent pose and outfit across all three views, full body head to toe visible in each panel, "
    "standing tall at full height, plain flat color background, organized reference sheet layout"
)

OLD_STYLE_TAIL = (
    "strict western action-cartoon style, bold flat colors, clean ink outlines"
)
OLD_STYLE_TAIL_NSFW = "strict western action-cartoon style, bold flat colors, clean ink outlines, explicit full frontal female nudity, completely naked, bare breasts and perfectly drawn bare pussy visible"

LAYOUT_BLOCK = (
    "character design reference sheet, character model sheet, "
    "character reference sheet turnaround, three full-body views of the exact same character side by side: "
    "front-facing view on the left, three-quarter angle view in the center, rear view on the right, "
    "consistent pose and outfit across all three views, full body head to toe visible in each panel, "
    "standing tall at full height, plain flat color background, organized reference sheet layout"
)

NSFW_PREFIX = (
    "explicit uncensored NSFW, full frontal female nudity, fully naked woman, "
)
NSFW_TAIL_EXTRA = ", explicit full frontal female nudity, completely naked, bare breasts and perfectly drawn bare pussy visible"

STYLES = [
    {
        "label": "s01_8k_deep_shading",
        "head": "8K resolution, intricate detail, stylized character illustration, sharp focus, detailed skin texture with subsurface scattering, realistic hair strands, dramatic light and shadow, deep smooth shading, ambient occlusion, three-point studio lighting with strong key light, strictly female character, feminine curves and anatomy",
        "tail": "8K resolution, intricate detail, stylized illustration, deep smooth shading, dramatic shadows, ambient occlusion",
    },
    {
        "label": "s02_hyperdetailed_chiaroscuro",
        "head": "hyperdetailed stylized character art, 8K, extremely intricate detail on skin and materials, slightly stylized proportions, realistic textures, strong chiaroscuro shading, deep cast shadows, soft gradient transitions between light and dark, cinematic three-point lighting, rich color depth, strictly female character, feminine curves and anatomy",
        "tail": "hyperdetailed stylized, 8K, strong chiaroscuro shading, deep shadows, soft gradients, cinematic lighting",
    },
    {
        "label": "s03_photorealistic_sculpted_light",
        "head": "photorealistic with subtle stylization, extremely detailed, 8K resolution, lifelike skin with pores and subsurface scattering, realistic hair with individual strands, sculpted light and shadow defining every curve and contour, deep soft shadows under chin and along body, strong directional key light, strictly female character, feminine curves and anatomy",
        "tail": "photorealistic with subtle stylization, 8K, sculpted light and shadow, deep soft shadows, strong directional lighting",
    },
    {
        "label": "s04_cgi_volumetric_depth",
        "head": "high-end CGI character render, cinematic quality, 8K ultra detailed, realistic skin shader with deep shading, volumetric lighting with visible light rays, ray traced shadows, ambient occlusion in crevices, physically based materials, soft shadow gradients, slight stylization, strictly female character, feminine curves and anatomy",
        "tail": "high-end CGI, 8K, deep shading, volumetric lighting, ray traced shadows, ambient occlusion, slight stylization",
    },
    {
        "label": "s05_fashion_dramatic_shadow",
        "head": "fashion editorial photography style, 8K ultra sharp, extremely detailed, shot on 85mm f/1.2, dramatic studio lighting with deep shadows and bright highlights, strong contrast, detailed skin texture with visible light falloff, realistic fabric shading, slightly stylized features, strictly female character, feminine curves and anatomy",
        "tail": "fashion editorial, 8K, dramatic studio lighting, deep shadows, strong contrast, detailed light falloff",
    },
    {
        "label": "s06_unreal5_global_illumination",
        "head": "Unreal Engine 5 cinematic render, stylized character, 8K textures, ray traced global illumination, lumen lighting with realistic light bounce and deep soft shadows, detailed subsurface scattering on skin, ambient occlusion, physically based material rendering, strictly female character, feminine curves and anatomy",
        "tail": "Unreal Engine 5, 8K, ray traced GI, lumen lighting, deep soft shadows, subsurface scattering, ambient occlusion",
    },
    {
        "label": "s07_octane_shadow_depth",
        "head": "octane render, extremely detailed stylized character, 8K resolution, intricate skin detail, realistic material properties, HDRI studio lighting with strong shadow definition, deep ambient occlusion, smooth shading gradients across skin, sharp focus, rich color palette, strictly female character, feminine curves and anatomy",
        "tail": "octane render, 8K, strong shadow definition, deep ambient occlusion, smooth shading gradients, sharp focus",
    },
    {
        "label": "s08_beauty_rembrandt_light",
        "head": "beauty shot, extremely detailed stylized character, 8K sharp focus, flawless skin with realistic texture, Rembrandt lighting with triangle shadow under eye, deep neck and body shadows, soft warm key light with cool shadow fill, glossy highlights contrasting deep darks, strictly female character, feminine curves and anatomy",
        "tail": "beauty shot, 8K, Rembrandt lighting, deep body shadows, warm highlights contrasting deep darks",
    },
    {
        "label": "s09_dimensional_shading",
        "head": "extremely detailed stylized character, 8K, strong three-dimensional shading that sculpts every form, deep shadows under breasts and along waist, visible light direction with smooth falloff, realistic shadow color with warm light and cool shadow, sharp focus, strictly female character, feminine curves and anatomy",
        "tail": "extremely detailed, 8K, strong 3D shading, deep sculpted shadows, smooth light falloff, sharp focus",
    },
    {
        "label": "s10_masterpiece_dramatic_light",
        "head": "masterpiece, best quality, extremely detailed, 8K, sharp focus, intricate detail on all surfaces, realistic skin texture, detailed hair, dramatic studio lighting with deep defined shadows, strong highlight-to-shadow ratio, smooth shading transitions, slightly stylized proportions, strictly female character, feminine curves and anatomy",
        "tail": "masterpiece, best quality, 8K, dramatic lighting, deep defined shadows, strong contrast, smooth shading",
    },
    {
        "label": "s11_aaa_cinematic_shadows",
        "head": "AAA game cinematic cutscene quality, extremely detailed stylized character, 8K resolution, realistic material rendering, subsurface scattering on skin, detailed fabric and leather textures, dramatic cinematic lighting with deep shadow pools, strong rim light separating figure from background, strictly female character, feminine curves and anatomy",
        "tail": "AAA cinematic, 8K, deep shadow pools, strong rim light, subsurface scattering, dramatic lighting",
    },
    {
        "label": "s12_noir_studio_light",
        "head": "film noir inspired studio lighting, extremely detailed stylized character, 8K resolution, high contrast light and shadow, deep black shadows with sharp edges, bright specular highlights, moody atmospheric quality, detailed skin and material textures, strictly female character, feminine curves and anatomy",
        "tail": "noir studio lighting, 8K, high contrast, deep black shadows, bright specular highlights, moody atmosphere",
    },
    {
        "label": "s13_soft_render_deep_shadow",
        "head": "extremely detailed, intricate, 8K resolution, sharp focus, realistic textures, soft rendered shading with deep shadows, smooth gradient transitions, visible light direction sculpting the form, warm studio lighting, strictly female character, feminine curves and anatomy",
        "tail": "extremely detailed, 8K, soft rendered shading, deep shadows, smooth gradients, warm studio lighting",
    },
    {
        "label": "s14_vfx_ray_traced_shadows",
        "head": "VFX film quality character, extremely detailed, 8K, photorealistic skin with subtle stylization, physically based rendering, ray traced shadows with soft penumbra, volumetric studio lighting, ambient occlusion in all crevices, smooth shading across body, strictly female character, feminine curves and anatomy",
        "tail": "VFX film quality, 8K, ray traced shadows with soft penumbra, volumetric lighting, ambient occlusion, smooth shading",
    },
    {
        "label": "s15_artstation_sculpted_form",
        "head": "trending on artstation, extremely detailed character illustration, 8K resolution, intricate detail, realistic skin and material rendering, cinematic studio lighting that sculpts every muscle and curve with deep shading, strong shadow definition, masterpiece quality, slightly stylized, strictly female character, feminine curves and anatomy",
        "tail": "artstation trending, 8K, cinematic lighting sculpting form, deep shading, strong shadows, masterpiece",
    },
]


def build_prompt(tier, style):
    if tier == "sfw":
        original = fighter["image_prompt_sfw"]["full_prompt"]
        new_head = style["head"] + ", " + LAYOUT_BLOCK
        new_tail = style["tail"]
        result = original.replace(OLD_STYLE_HEAD, new_head)
        result = result.replace(OLD_STYLE_TAIL, new_tail)
    elif tier == "barely":
        original = fighter["image_prompt"]["full_prompt"]
        new_head = style["head"] + ", " + LAYOUT_BLOCK
        new_tail = style["tail"]
        result = original.replace(OLD_STYLE_HEAD, new_head)
        result = result.replace(OLD_STYLE_TAIL, new_tail)
    elif tier == "nsfw":
        original = fighter["image_prompt_nsfw"]["full_prompt"]
        new_head = NSFW_PREFIX + style["head"] + ", " + LAYOUT_BLOCK
        new_tail = style["tail"] + NSFW_TAIL_EXTRA
        result = original.replace(OLD_STYLE_HEAD_NSFW, new_head)
        result = result.replace(OLD_STYLE_TAIL_NSFW, new_tail)
    return result


def main():
    output_dir = (
        Path(__file__).parent.parent / "data" / "_prompt_variations" / "style_swap_r4"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    tiers = ["sfw", "barely", "nsfw"]

    for style in STYLES:
        for tier in tiers:
            prompt = build_prompt(tier, style)
            all_results.append(
                {
                    "style_label": style["label"],
                    "tier": tier,
                    "prompt": prompt,
                }
            )

    with open(output_dir / "style_swap_results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    with open(output_dir / "style_swap_readable.md", "w") as f:
        f.write("# Venom Kiss — Style Swap Test\n\n")
        f.write(f"{len(STYLES)} styles x 3 tiers = {len(all_results)} prompts\n\n")
        f.write(
            "Pure string replacement — character details, layout, views, and expression are IDENTICAL.\n"
        )
        f.write("Only the style prefix and style tail are swapped.\n\n")

        current_style = None
        for r in all_results:
            if r["style_label"] != current_style:
                current_style = r["style_label"]
                style_info = next(s for s in STYLES if s["label"] == current_style)
                f.write(f"---\n\n## {current_style}\n\n")
                f.write(f"**Head:** `{style_info['head']}`\n\n")
                f.write(f"**Tail:** `{style_info['tail']}`\n\n")

            f.write(f"### {r['tier'].upper()}\n\n")
            f.write(f"```\n{r['prompt']}\n```\n\n")

    print(f"Saved {len(all_results)} prompts to:")
    print(f"  {output_dir / 'style_swap_results.json'}")
    print(f"  {output_dir / 'style_swap_readable.md'}")

    print(f"\nVerification — confirming replacements worked:")
    for style in STYLES:
        for tier in tiers:
            prompt = build_prompt(tier, style)
            if (
                "western action-cartoon" in prompt
                or "bold flat colors" in prompt
                or "low detail" in prompt
            ):
                print(
                    f"  WARNING: Old style text still present in {style['label']} / {tier}"
                )
            if "front view:" not in prompt:
                print(f"  WARNING: Missing 'front view:' in {style['label']} / {tier}")
            if tier == "nsfw" and "explicit uncensored NSFW" not in prompt:
                print(f"  WARNING: Missing NSFW prefix in {style['label']} / {tier}")
    print("  Verification complete.")


if __name__ == "__main__":
    main()
