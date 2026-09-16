# Visual Defect Taxonomy & Remediation Guide

| Defect Class | Description | Severity | Remediation Strategy |
|---|---|---|---|
| `ANATOMICAL_WARPING` | Extra fingers, distorted eyes, fused limbs | High (Blocker) | Re-render with negative prompt emphasis and modified seed offset. |
| `ANCHOR_DRIFT` | Missing cybernetic eye, incorrect jacket color | High (Blocker) | Re-inject exact `visual_anchor` string verbatim at start of prompt. |
| `PERSPECTIVE_MISMATCH` | Horizon line inconsistent with adjacent shot | Medium | Adjust lens and camera angle specification in shot breakdown. |
| `LIGHTING_FLIP` | Light source flipped 180 degrees between reverse shots | Medium | Explicitly define directional key light source (e.g. `key from screen-left`). |
