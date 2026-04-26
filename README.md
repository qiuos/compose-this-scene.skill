# 这个场景怎么拍 · Compose This Scene

一个摄影构图技能。分析任意照片，提出 3–5 种不同构图方向，并生成可视化的裁剪预览和标注图。

## 功能

给定一张照片，本技能会：

1. 分析画面——主体、光线、几何、纵深、色彩、时机、情绪
2. 提出 3–5 种构图方案，各有不同意图（经典三分法、留白、戏剧性近裁、引导线几何、对称、电影宽幅等）
3. 渲染裁剪预览、带辅助线标注的原图，以及缩略图总览
4. 为每个方案给出简明点评：为何有效、情绪效果、风格参考、拍摄建议

## 触发提示词

当用户说以下内容时使用本技能：

- "这个场景怎么拍" / "这张照片怎么构图" / "帮我裁一下"
- 询问如何拍摄、裁剪、取景、重新构图或改进场景/照片
- 任何关于构图建议、标注图片或裁剪预览的请求

## 使用方式

### 在 任意智能体 中

安装为技能后，上传或引用一张照片，然后询问构图建议即可。

### 渲染预览

创建构图方案 JSON：

```json
{
  "variants": [
    {
      "id": "classic-thirds",
      "title": "经典三分法",
      "crop": [0.05, 0.02, 0.88, 0.96],
      "guides": ["thirds"],
      "focus_points": [{"x": 0.34, "y": 0.45, "label": "主体"}],
      "caption": "将主体放在三分线交叉点附近，去除边缘杂乱元素。"
    }
  ]
}
```

运行渲染脚本：

```bash
python3 scripts/make_composition_variants.py \
  --image /path/to/photo.jpg \
  --plan /path/to/plan.json \
  --out-dir /path/to/output
```

### 输出

脚本会生成：

| 文件 | 说明 |
|------|------|
| `*_crop.jpg` | 每种构图的裁剪预览 |
| `*_annotated.jpg` | 原图加暗化蒙版、裁剪框、辅助线和焦点标注 |
| `*_contact_sheet.jpg` | 所有方案的缩略图总览 |
| `composition_outputs.json` | 机器可读的输出路径和元数据 |

## 构图辅助线

支持的辅助线类型：`thirds`（三分线）、`center`（中心线）、`crosshair`（十字线）、`diagonal` / `diagonals`（对角线）、`golden` / `golden_spiral`（黄金分割）

裁剪坐标使用归一化 `[left, top, right, bottom]` 值，范围 `0.0` 到 `1.0`，相对于原图尺寸。

## 依赖

- Python 3.10+
- Pillow（`pip install Pillow`）

## 许可证

MIT
