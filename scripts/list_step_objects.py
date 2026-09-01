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


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: freecadcmd list_step_objects.py INPUT.step")
        return 2

    input_path = Path(sys.argv[-1]).resolve()

    import FreeCAD  # type: ignore
    import Import  # type: ignore

    doc = FreeCAD.newDocument("xz_motion_mechanism_step_list")
    Import.insert(str(input_path), doc.Name)

    seen = set()
    objects = []

    def visit(obj):
        if obj.Name in seen:
            return
        seen.add(obj.Name)
        objects.append(obj)
        for child in getattr(obj, "OutList", []):
            visit(child)

    for obj in doc.Objects:
        visit(obj)

    rows = []
    print(f"document_objects={len(doc.Objects)} traversed_objects={len(objects)}")
    for obj in objects:
        if not hasattr(obj, "Shape") or obj.Shape.isNull():
            label = decode_step_label(getattr(obj, "Label", obj.Name))
            print(f"no_shape: {obj.Name} label={label}")
            continue
        label = decode_step_label(getattr(obj, "Label", obj.Name))
        box = obj.Shape.BoundBox
        rows.append(
            (
                label,
                box.XMin,
                box.XMax,
                box.YMin,
                box.YMax,
                box.ZMin,
                box.ZMax,
                (box.XMin + box.XMax) / 2.0,
                (box.YMin + box.YMax) / 2.0,
                (box.ZMin + box.ZMax) / 2.0,
            )
        )

    rows.sort(key=lambda row: (row[7], row[8], row[9], row[0]))
    print("label | xmin xmax | ymin ymax | zmin zmax | center")
    for row in rows:
        print(
            f"{row[0]} | "
            f"{row[1]:.3f} {row[2]:.3f} | "
            f"{row[3]:.3f} {row[4]:.3f} | "
            f"{row[5]:.3f} {row[6]:.3f} | "
            f"({row[7]:.3f}, {row[8]:.3f}, {row[9]:.3f})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
