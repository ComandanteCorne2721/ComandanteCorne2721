#!/usr/bin/env python3
"""Parche blanco recortado al arco (para tapar rótulos/accesorios del proveedor sin
salirse del arco). Uso: arch_patch.py circle cx cy r | rect x0 y0 x1 y1
Imprime JSON con left/top/width/height y el path SVG (viewBox = tamaño del bbox)."""
import sys, json, math
from shapely.geometry import Point, box
from shapely.ops import unary_union
CX, CY, R = 540.0, 252.0 + 351.0, 351.0 - 3
ARCH = unary_union([Point(CX, CY).buffer(R, 64), box(192, CY, 888, 1080)])
def patch(shape):
    g = shape.intersection(ARCH)
    if g.is_empty: return None
    if g.geom_type != 'Polygon': g = max(g.geoms, key=lambda x: x.area)
    x0, y0, x1, y1 = g.bounds
    pts = [(x - x0, y - y0) for x, y in g.exterior.coords]
    d = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + ' Z'
    return dict(left=round(x0, 2), top=round(y0, 2), width=round(x1 - x0, 2), height=round(y1 - y0, 2),
                view_box_width=round(x1 - x0, 2), view_box_height=round(y1 - y0, 2), path=d)
if __name__ == '__main__':
    k = sys.argv[1]; a = [float(v) for v in sys.argv[2:]]
    s = Point(a[0], a[1]).buffer(a[2], 48) if k == 'circle' else box(*a)
    print(json.dumps(patch(s)))
