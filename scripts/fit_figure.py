#!/usr/bin/env python3
"""Calcula el ajuste estándar de una página individual a partir de su miniatura 600x600.

Entrada : miniatura de la página + marco/imageBox actuales (de read-design).
Salida  : marco estándar (top 243.58, alto 728.42, centrado en x), imageBox para
          crop_media y parches blancos (sobre el arco blanco) para tapar rótulos
          del proveedor que no se puedan recortar con un rectángulo.
Los cálculos usan coordenadas de página (1080x1080).
"""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

PAGE = 1080.0
STD_TOP, STD_H = 243.58, 728.42
FIG_H_TARGET = 690.0
FIG_W_MAX = 600.0
MARGIN_X = 10.0
ARCH_L, ARCH_R, ARCH_TOP, ARCH_R_TOP = 189.0, 891.0, 252.0, 351.0

def arch_mask(x0, y0, x1, y1, s):
    ys, xs = np.mgrid[y0:y1, x0:x1]
    X, Y = xs / s, ys / s
    cx, cy = 540.0, ARCH_TOP + ARCH_R_TOP
    rect = (X >= ARCH_L + 3) & (X <= ARCH_R - 3) & (Y >= cy)
    circ = (X - cx) ** 2 + (Y - cy) ** 2 <= (ARCH_R_TOP - 5) ** 2
    return rect | circ

def analyze(png, roi):
    """Devuelve (bbox_figura, [cajas_rotulo], avisos) en px de página."""
    im = np.asarray(Image.open(png).convert('RGB')).astype(int)
    s = im.shape[1] / PAGE
    x0, y0, x1, y1 = [int(round(v * s)) for v in roi]
    sub = im[y0:y1, x0:x1]
    mask = (sub.min(axis=2) < 215) & arch_mask(x0, y0, x1, y1, s)
    lab, n = ndi.label(mask, structure=np.ones((3, 3)))
    if n == 0:
        return None, [], ['sin contenido']
    objs = ndi.find_objects(lab)
    areas = ndi.sum(mask, lab, range(1, n + 1))
    main = int(np.argmax(areas)) + 1
    gh, gw = int(round(26 * s / 0.5556 * 0.5556)), int(round(34 * s / 0.5556 * 0.5556))
    def is_glyph(i):
        o = objs[i - 1]
        h, w = o[0].stop - o[0].start, o[1].stop - o[1].start
        return h <= gh and w <= gw and areas[i - 1] < 450
    mb = objs[main - 1]
    bb = [mb[1].start, mb[0].start, mb[1].stop, mb[0].stop]
    keep = {main}
    pad = 5
    changed = True
    while changed:
        changed = False
        for i in range(1, n + 1):
            if i in keep or is_glyph(i): continue
            o = objs[i - 1]
            if areas[i - 1] < 60: continue
            near = (o[1].start <= bb[2] + pad and o[1].stop >= bb[0] - pad and
                    o[0].start <= bb[3] + pad and o[0].stop >= bb[1] - pad)
            if near:
                keep.add(i)
                bb = [min(bb[0], o[1].start), min(bb[1], o[0].start),
                      max(bb[2], o[1].stop), max(bb[3], o[0].stop)]
                changed = True
    # rótulos: glifos sueltos fuera del cuerpo; agrupar
    gl = np.zeros_like(mask)
    for i in range(1, n + 1):
        if i not in keep and is_glyph(i):
            gl |= (lab == i)
    boxes = []
    if gl.any():
        gd = ndi.binary_dilation(gl, iterations=max(3, int(round(9 * s / 0.5556 * 0.5556))))
        gl2, gn = ndi.label(gd)
        for o in ndi.find_objects(gl2):
            sub_has = gl[o].sum()
            if sub_has < 25: continue          # ruido
            boxes.append([roi[0] + o[1].start / s, roi[1] + o[0].start / s,
                          roi[0] + o[1].stop / s, roi[1] + o[0].stop / s])
    fb = [roi[0] + bb[0] / s, roi[1] + bb[1] / s, roi[0] + bb[2] / s, roi[1] + bb[3] / s]
    return fb, boxes, []

def plan(png, frame, box):
    """frame=(L,T,W,H); box=(bt,bl,bw,bh) relativos al marco."""
    L, T, W, H = frame; bt, bl, bw, bh = box
    fb, labels, warn = analyze(png, (L, T, L + W, T + H))
    if fb is None: return None, warn
    fw, fh = fb[2] - fb[0], fb[3] - fb[1]
    k = min(FIG_H_TARGET / fh, FIG_W_MAX / fw)
    newW = max(380.0, min(640.0, k * fw + 2 * MARGIN_X))
    newL = (PAGE - newW) / 2
    X0, Y0 = L + bl, T + bt
    fcx, fcy = (fb[0] + fb[2]) / 2, (fb[1] + fb[3]) / 2
    nbl = newW / 2 - k * (fcx - X0)
    nbt = STD_H / 2 - k * (fcy - Y0)
    # parches: cajas de rótulo transformadas a la página nueva y recortadas al marco
    patches = []
    for b in labels:
        px0 = newL + nbl + k * (b[0] - X0); px1 = newL + nbl + k * (b[2] - X0)
        py0 = STD_TOP + nbt + k * (b[1] - Y0); py1 = STD_TOP + nbt + k * (b[3] - Y0)
        cx0, cx1 = max(px0, newL), min(px1, newL + newW)
        cy0, cy1 = max(py0, STD_TOP), min(py1, STD_TOP + STD_H)
        if cx1 - cx0 > 4 and cy1 - cy0 > 4:
            patches.append([round(cx0 - 6, 1), round(cy0 - 6, 1), round(cx1 + 6, 1), round(cy1 + 6, 1)])
    return dict(frame=dict(left=round(newL, 2), top=STD_TOP, width=round(newW, 2), height=STD_H),
                imageBox=dict(left=round(nbl, 2), top=round(nbt, 2), width=round(bw * k, 2), height=round(bh * k, 2)),
                figure_bbox=[round(v, 1) for v in fb], scale=round(k, 3), patches=patches,
                labels=[[round(v, 1) for v in b] for b in labels]), warn

if __name__ == '__main__':
    print(json.dumps(plan(sys.argv[1], json.loads(sys.argv[2]), json.loads(sys.argv[3])), ensure_ascii=False))
