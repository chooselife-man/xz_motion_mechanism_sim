#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def decode_step_label(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        try:
            return bytes.fromhex(match.group(1)).decode("utf-16-be")
        except Exception:
            return match.group(0)

    return re.sub(r"\\X2\\([0-9A-Fa-f]+)\\X0\\", repl, text)


def object_center(obj):
    box = obj.Shape.BoundBox
    return (
        (box.XMin + box.XMax) / 2.0,
        (box.YMin + box.YMax) / 2.0,
        (box.ZMin + box.ZMax) / 2.0,
    )


def object_size(obj):
    box = obj.Shape.BoundBox
    return (
        box.XMax - box.XMin,
        box.YMax - box.YMin,
        box.ZMax - box.ZMin,
    )


def classify(label: str) -> str | None:
    if label.startswith("BODY_") or label.startswith("NAT_"):
        return None

    if "上下驱动齿条" in label:
        return "y_stage"
    if "20-30长一米齿条" in label or "移动横齿" in label:
        return "base"
    if label == "滚轮滑座":
        return "base"
    if "STW15L1R500ZACM]_1_STW15L" in label:
        return "x_stage"

    base_keywords = [
        "横杠",
        "支撑架",
        "角件",
        "T型螺母",
        "STW15L]001",
        "不锈钢导轨",
        "808",
        "404",
    ]
    x_stage_keywords = [
        "滑块连接件",
        "连接件1",
        "连接件2",
        "连接件3",
        "支架滚轮",
        "凸轮轴承随动器",
        "台达伺服电机",
        "上下驱动长齿轮",
        "横齿222",
        "执行机构连接件",
        "执行机构盒盖",
    ]

    if any(keyword in label for keyword in base_keywords):
        return "base"
    if any(keyword in label for keyword in x_stage_keywords):
        return "x_stage"
    return None


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: freecadcmd export_grouped_step_meshes.py INPUT.step OUTPUT_DIR")
        return 2

    input_path = Path(sys.argv[-2]).resolve()
    output_dir = Path(sys.argv[-1]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    import FreeCAD  # type: ignore
    import Import  # type: ignore
    import Mesh  # type: ignore

    doc = FreeCAD.newDocument("xz_motion_mechanism_grouped_export")
    Import.insert(str(input_path), doc.Name)

    groups = {"base": [], "x_stage": [], "y_stage": []}
    skipped = []

    for obj in doc.Objects:
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            continue
        label = decode_step_label(getattr(obj, "Label", obj.Name))
        group = classify(label)
        if group:
            groups[group].append(obj)
        else:
            skipped.append(label)

    for group, objects in groups.items():
        if not objects:
            raise RuntimeError(f"group {group} is empty")
        path = output_dir / f"{group}_visual.stl"
        Mesh.export(objects, str(path))
        print(f"wrote {path} objects={len(objects)}")
        for obj in objects:
            label = decode_step_label(getattr(obj, "Label", obj.Name))
            center = object_center(obj)
            print(f"  {group}: {label} center_mm=({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")

    if skipped:
        print("skipped:")
        for label in skipped:
            print(f"  {label}")

    manifest_path = output_dir / "grouped_meshes_manifest.txt"
    with manifest_path.open("w", encoding="utf-8") as manifest:
        for group, objects in groups.items():
            manifest.write(f"[{group}]\n")
            for obj in objects:
                label = decode_step_label(getattr(obj, "Label", obj.Name))
                center = object_center(obj)
                size = object_size(obj)
                manifest.write(
                    f"{label} center_mm=({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f}) "
                    f"size_mm=({size[0]:.3f}, {size[1]:.3f}, {size[2]:.3f})\n"
                )
            manifest.write("\n")
        if skipped:
            manifest.write("[skipped]\n")
            for label in skipped:
                manifest.write(f"{label}\n")
    print(f"wrote {manifest_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
