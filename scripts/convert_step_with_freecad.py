#!/usr/bin/env python3
"""
Optional STEP-to-mesh conversion helper.

Run this with FreeCAD's Python interpreter, for example:

    freecadcmd convert_step_with_freecad.py /path/to/model.STEP ../meshes/module_visual.stl

The generated mesh should be used as visual geometry in Gazebo. Keep collision geometry
simplified unless detailed contacts are required.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: freecadcmd convert_step_with_freecad.py INPUT.step OUTPUT.stl")
        return 2

    input_path = Path(sys.argv[-2]).resolve()
    output_path = Path(sys.argv[-1]).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    import Mesh  # type: ignore
    import Part  # type: ignore

    shape = Part.Shape()
    shape.read(str(input_path))
    objects = [type("ShapeObject", (), {"Shape": shape})()]
    if not objects:
        raise RuntimeError(f"No shape objects found in {input_path}")

    meshes = []
    for obj in objects:
        shape = obj.Shape
        if shape.isNull():
            continue
        facets = shape.tessellate(0.5)
        meshes.append(Mesh.Mesh(facets))

    if not meshes:
        raise RuntimeError(f"No valid shapes could be tessellated from {input_path}")

    merged = meshes[0]
    for mesh in meshes[1:]:
        merged.addMesh(mesh)

    merged.write(str(output_path))
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
