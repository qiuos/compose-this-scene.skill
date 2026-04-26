---
name: compose-this-scene
description: Photo composition critique and visual crop planning for uploaded images or local image files. Use when the user asks how to shoot, crop, frame, recompose, improve, or annotate a scene/photo, including Chinese prompts like "这个场景怎么拍", "这张照片怎么构图", "帮我裁一下", or requests for 3-5 composition ideas, photographer-inspired composition references, annotated images, crop previews, or shooting advice.
---

# Compose This Scene

## Goal

Act as a world-class photography composition mentor. Analyze the user's photo, propose 3-5 distinct composition directions, create visual crop/annotation previews when possible, and explain the artistic logic in the user's language.

## Core Workflow

1. Inspect the image first. Identify scene type, main subject, supporting elements, distractions, light direction, color relationships, spatial depth, rhythm, and the current frame's biggest missed opportunity.
2. Choose 3-5 genuinely different composition approaches. Vary intent, not only crop size: classic balance, negative space, dramatic close crop, leading-line geometry, symmetry, cinematic foreground/background, documentary moment, etc.
3. For each approach, define a crop box and optional guide overlays. Prefer normalized coordinates `[left, top, right, bottom]` from `0.0` to `1.0` relative to the original image.
4. Use `scripts/make_composition_variants.py` to render crop previews, annotated originals, and a contact sheet when a local image path is available.
5. Return the previews plus a concise critique for each option: why this crop works, emotional effect, best use case, and a photographer/style reference when helpful.

## Image Analysis Checklist

- **Subject hierarchy**: primary subject, secondary anchors, and visual noise.
- **Light**: direction, contrast, highlight placement, shadows, atmosphere.
- **Geometry**: thirds, diagonals, leading lines, frames within frames, symmetry, horizon stability.
- **Depth**: foreground, middle ground, background, overlap, scale cues.
- **Color**: dominant palette, accent colors, warm/cool contrast, saturation distractions.
- **Timing**: gesture, expression, decisive moment, implied motion.
- **Mood**: calm, tension, intimacy, loneliness, scale, mystery, documentary truth.

Read `references/composition-playbook.md` when you need more scene-specific prompts, composition patterns, or style references.

## Rendering Visual Options

Create a plan JSON with this shape:

```json
{
  "variants": [
    {
      "id": "classic-thirds",
      "title": "Classic thirds balance",
      "crop": [0.05, 0.02, 0.88, 0.96],
      "guides": ["thirds"],
      "focus_points": [{"x": 0.34, "y": 0.45, "label": "subject"}],
      "caption": "Place the subject near a thirds intersection and remove edge clutter."
    }
  ]
}
```

Run:

```bash
python3 path/to/compose-this-scene/scripts/make_composition_variants.py \
  --image /path/to/photo.jpg \
  --plan /path/to/plan.json \
  --out-dir /path/to/output
```

The script writes:

- `*_crop.*`: cropped preview for each composition.
- `*_annotated.*`: original image dimmed outside the crop with guide overlays.
- `contact_sheet.*`: a grid summary of all variants.
- `composition_outputs.json`: machine-readable output paths.

If no local image path is available, still provide 3-5 composition recommendations in text and ask the user to provide a local file path if they want rendered crops.

## Composition Direction Rules

- Provide exactly 3-5 options unless the user asks otherwise.
- Make each option distinct in intent, frame shape, and emotional effect.
- Avoid generic praise. Name the strongest improvement and the tradeoff for every option.
- Use photographer references as compositional analogies, not as claims that the image fully matches that photographer.
- Prefer practical crops that preserve image quality. Warn when an aggressive crop may reduce resolution.
- For portraits, avoid cutting joints awkwardly and preserve gaze room unless intentionally creating tension.
- For landscapes, protect horizon placement and edge cleanliness before applying decorative rules.
- For street/documentary photos, preserve gesture and context; do not crop away the story just to center the subject.
- For product/food/interior images, prioritize legibility, shape, brand/object clarity, and clean negative space.

## Response Structure

Start with a one-sentence overall diagnosis. Then list each composition option with:

- Option title
- Preview image path if generated
- Crop intent
- Why it works
- Emotional effect
- Style reference
- Shooting tip if the user can retake the photo

End by naming the strongest option for the user's likely goal. If the goal is unclear, choose the most broadly effective option and state the assumption.
