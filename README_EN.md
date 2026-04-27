# Compose This Scene

A photography composition skill. Analyze any photo, propose 3–5 distinct composition directions, and render visual crop/annotation previews.

## What It Does

Given a photo, this skill:

1. Inspects the scene — subject, light, geometry, depth, color, timing, mood
2. Proposes 3–5 composition options with different intents (classic thirds, negative space, dramatic close crop, leading-line geometry, symmetry, cinematic wide, etc.)
3. Renders crop previews, annotated originals with guide overlays, and a contact sheet
4. Returns a concise critique for each option: why it works, emotional effect, style reference, and shooting tips

## Prompt Triggers

Use this skill when the user asks:

- "这个场景怎么拍" / "这张照片怎么构图" / "帮我裁一下"
- How to shoot, crop, frame, recompose, or improve a scene/photo
- Any request for composition ideas, annotated images, or crop previews

## Usage

### Rendering Previews

Create a composition plan JSON:

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

Run the rendering script:

```bash
python3 scripts/make_composition_variants.py \
  --image /path/to/photo.jpg \
  --plan /path/to/plan.json \
  --out-dir /path/to/output
```

### Output

The script generates:

| File | Description |
|------|-------------|
| `*_crop.jpg` | Cropped preview for each composition |
| `*_annotated.jpg` | Original image with dim overlay, crop box, guide overlays, and focus points |
| `*_contact_sheet.jpg` | Grid summary of all variants |
| `composition_outputs.json` | Machine-readable output paths and metadata |

## Composition Guides

Supported guide overlays: `thirds`, `center`, `crosshair`, `diagonal`, `diagonals`, `golden`, `golden_spiral`

Crop coordinates use normalized `[left, top, right, bottom]` values from `0.0` to `1.0` relative to the original image.

## Dependencies

- Python 3.10+
- Pillow (`pip install Pillow`)

## License

MIT