"""'Hyoshi to mikaeshi' pair: closed = cloth-bound cover with a gold-foil mark; open = marbled endpapers."""
import numpy as np
from lib import *
from shoji import shiba_mask
from moon import composite

LIGHT = np.array([-0.45, -0.55, 0.70], np.float32); LIGHT /= np.linalg.norm(LIGHT)

def weave_height(size, P=6.0, seed=0):
    """Plain-weave bookcloth height field in [0,1]."""
    W, H = size
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # slight waviness of threads
    x = x + 0.6 * vnoise((H, W), 60, seed + 1, cell_y=300)
    y = y + 0.6 * vnoise((H, W), 300, seed + 2, cell_y=60)
    i = np.floor(x / P).astype(np.int64); fx = x / P - i
    j = np.floor(y / P).astype(np.int64); fy = y / P - j
    warp_thick = 0.85 + 0.15 * rng.uniform(-1, 1, i.max() + 3)[np.clip(i + 1, 0, None)]
    weft_thick = 0.85 + 0.15 * rng.uniform(-1, 1, j.max() + 3)[np.clip(j + 1, 0, None)]
    cyl = lambda f, t: np.sqrt(np.clip(1 - ((2 * f - 1) / np.maximum(t, 0.3)) ** 2, 0, 1))
    top_warp = ((i + j) % 2 == 0)
    h_warp = cyl(fx, warp_thick) * (0.75 + 0.25 * np.cos((fy - 0.5) * np.pi))
    h_weft = cyl(fy, weft_thick) * (0.75 + 0.25 * np.cos((fx - 0.5) * np.pi))
    h = np.where(top_warp, h_warp, h_weft)
    # slubs: thread-wise brightness/height variation along their length
    slub_v = vnoise((H, W), P, seed + 3, cell_y=90)
    slub_h = vnoise((H, W), 90, seed + 4, cell_y=P)
    tone = np.where(top_warp, slub_v, slub_h)
    return h.astype(np.float32), tone.astype(np.float32)

def shade(height, k):
    gy, gx = np.gradient(height * k)
    n = np.stack([-gx, -gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.clip((n @ LIGHT) / LIGHT[2], 0, 2), n

def cloth(size, base_hex, seed, P=6.0, extra_h=None, extra_k=7.0):
    W, H = size
    hw, tone = weave_height(size, P, seed)
    dif_w, _ = shade(hw, 0.9)
    mott = fbm((H, W), 260, 4, 0.5, seed=seed + 9) * 0.035 + fbm((H, W), 30, 3, 0.5, seed=seed + 10) * 0.02
    col = hexl(base_hex)[None, None, :] * (1 + mott + 0.06 * tone)[..., None]
    img = col * (0.60 + 0.40 * dif_w)[..., None]
    if extra_h is not None:
        dif_e, _ = shade(extra_h, extra_k)
        img *= (0.25 + 0.75 * dif_e)[..., None]
    return img, hw

def ring_mask(size, cx, cy, r, w):
    W, H = size
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.hypot(x - cx, y - cy)
    return np.clip(w / 2 - np.abs(d - r) + 0.5, 0, 1)

def crescent_mask(size, cx, cy, r, off, ang):
    W, H = size
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    a = np.clip(r - np.hypot(x - cx, y - cy) + 0.5, 0, 1)
    ox, oy = cx + off * np.cos(ang), cy + off * np.sin(ang)
    b = np.clip(r * 0.92 - np.hypot(x - ox, y - oy) + 0.5, 0, 1)
    return np.clip(a - b, 0, 1)

def emblem_mask(size, cx, cy, R):
    """Gold mark: double ring, Shiba under a crescent."""
    m = ring_mask(size, cx, cy, R, 6) + ring_mask(size, cx, cy, R - 14, 2.2)
    sh_h = R * 1.05
    m += shiba_mask(size, cx - sh_h * 0.42, cy + R * 0.62, sh_h)
    m += crescent_mask(size, cx - R * 0.42, cy - R * 0.40, R * 0.17, R * 0.07, np.deg2rad(-40))
    return np.clip(m, 0, 1)

def gold_foil(mask, n_hint, seed):
    """Metallic gold colour field for the foil area."""
    H, W = mask.shape
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    broad = 0.55 + 0.45 * np.cos((x * 0.6 + y * 0.8) / 260.0 + 1.2)
    crinkle = 1 + 0.08 * fbm((H, W), 8, 3, seed=seed)
    gold_dk, gold_lt = hexl('#5A4526'), hexl('#C9A86B')
    t = np.clip(broad * crinkle, 0, 1)
    return gold_dk + (gold_lt - gold_dk) * t[..., None]

def make_outer(out):
    size = OUTER; W, H = size
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # relief: hinge groove near the spine (left), blind double frame, debossed emblem
    groove = np.exp(-((x - 70) / 9.0) ** 2)
    frame = np.zeros((H, W), np.float32)
    for inset, wdt in ((120, 3.0), (134, 1.6)):
        x0, x1, y0, y1 = inset + 40, W - inset + 40, inset, H - inset
        on_v = (np.abs(x - x0) < wdt) | (np.abs(x - x1) < wdt)
        on_h = (np.abs(y - y0) < wdt) | (np.abs(y - y1) < wdt)
        frame += (((on_v & (y > y0 - wdt) & (y < y1 + wdt)) | (on_h & (x > x0 - wdt) & (x < x1 + wdt)))).astype(np.float32)
    frame = gblur(np.clip(frame, 0, 1), 1.0)
    ex, ey, ER = 336, 520, 128
    em = emblem_mask(size, ex, ey, ER)
    em_b = gblur(em, 1.6)
    relief = -1.6 * gblur(groove, 2) - 0.5 * frame - 0.9 * em_b
    img, hw = cloth(size, '#2E2925', seed=3, extra_h=relief, extra_k=6.0)
    # edge wear / board rounding
    edge = np.minimum.reduce([x, W - 1 - x, y, H - 1 - y])
    img *= (0.78 + 0.22 * smoothstep(0, 60, edge))[..., None]
    # broad soft light from the upper-left
    img *= (0.84 + 0.28 * np.exp(-(((x - 200) / 1300) ** 2 + ((y - 300) / 1500) ** 2)))[..., None]
    # foil: smooth, follows the deboss, catches light on its bevel
    dif_e, _ = shade(-0.9 * em_b + 0.15 * hw, 6.0)
    foil = gold_foil(em, None, 7) * (0.55 + 0.55 * dif_e)[..., None]
    img = img * (1 - em[..., None]) + foil * em[..., None]
    u8 = finish(img, grain=0.006, seed=51)
    save(u8, out, q=90); preview(u8, out.replace('.jpg', '_prev.png'), 700)

# ---------- marbling (suminagashi) ----------
def suminagashi(size, centers, seed, n_drops=90, r_range=(45, 85), wind=120, swirls=()):
    """Mathematical marbling: concentric drops at several centres, then blown by a smooth flow.
    Returns (drop_number_at_its_centre map, -1 = untouched water)."""
    W, H = size
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    # backward map of the final gentle blowing: mostly horizontal drift + meanders
    dx = fbm((H, W), 700, 4, 0.55, seed=seed + 1) * wind + fbm((H, W), 180, 3, 0.5, seed=seed + 2) * wind * 0.30
    dy = fbm((H, W), 900, 4, 0.55, seed=seed + 3) * wind * 0.55 + fbm((H, W), 180, 3, 0.5, seed=seed + 4) * wind * 0.25
    px, py = (x - dx).ravel(), (y - dy).ravel()
    for (sx, sy, s_r, s_a) in swirls:
        r = np.hypot(px - sx, py - sy)
        th = -s_a * np.exp(-(r / s_r) ** 2)
        c, s = np.cos(th), np.sin(th)
        qx, qy = px - sx, py - sy
        px, py = sx + qx * c - qy * s, sy + qx * s + qy * c
    seq = []
    for k in range(n_drops):
        for ci, (cx, cy) in enumerate(centers):
            rmax, rmin = r_range
            r = (rmax - (rmax - rmin) * (k / max(1, n_drops - 1)) ** 0.7) * rng.uniform(0.8, 1.15)
            seq.append((cx + rng.normal(0, 4), cy + rng.normal(0, 4), r, k))
    out = np.full(W * H, -1, np.int32)
    idx_alive = np.arange(W * H)
    for i in range(len(seq) - 1, -1, -1):
        cx, cy, r, k = seq[i]
        qx = px - cx; qy = py - cy
        d2 = qx * qx + qy * qy
        inside = d2 <= r * r
        if inside.any():
            out[idx_alive[inside]] = k
            keep = ~inside
            idx_alive = idx_alive[keep]; qx = qx[keep]; qy = qy[keep]; d2 = d2[keep]
        f = np.sqrt(1 - (r * r) / d2)
        px = cx + qx * f; py = cy + qy * f
    return out.reshape(H, W)

def make_inner(out):
    size = INNER; W, H = size
    F = W // 2
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    centers = [(380, 470), (980, 1420), (1180, 260), (1760, 700), (2330, 1480), (2520, 230), (300, 1700)]
    k = suminagashi(size, centers, seed=12, n_drops=64, r_range=(150, 48), wind=150,
                    swirls=[(1335, 900, 520, 0.8), (520, 1250, 300, -0.9), (2150, 560, 320, 0.9)])
    base = hexl('#2A231F')
    ink_dark = hexl('#211B18')
    ink_warm = hexl('#352B25')
    gold = hexl('#7E6844')
    col = np.broadcast_to(base, (H, W, 3)).copy()
    is_ink = (k >= 0) & (k % 2 == 0)
    kind_cls = (k // 2) % 7
    dark_m = is_ink & ((kind_cls % 2) == 0) & (kind_cls != 6)
    warm_m = is_ink & ((kind_cls % 2) == 1)
    gold_m = is_ink & (kind_cls == 6)
    col[dark_m] = ink_dark; col[warm_m] = ink_warm; col[gold_m] = gold * 0.55
    tone = np.random.default_rng(3).uniform(0.9, 1.1, 200)
    col *= np.where(k >= 0, tone[np.clip(k, 0, 199)], 1.0)[..., None]
    col = gblur(col, 0.9)
    # paper tooth
    col *= (1 + 0.03 * fbm((H, W), 40, 3, seed=5) + 0.02 * fbm((H, W), 6, 2, seed=6))[..., None]
    img = col
    # gold rings get a little metallic sheen variation
    gm = gblur(gold_m.astype(np.float32), 0.8)
    sheen = 0.75 + 0.45 * np.cos((x * 0.7 - y * 0.7) / 300.0)
    img = img + (gm * (sheen - 0.75))[..., None] * gold * 0.6
    # left page: cloth turn-ins around the pastedown (left, top, bottom)
    t = 44
    turn = ((x < t) | (y < t) | (y > H - t)) & (x < F)
    turn_m = gblur(turn.astype(np.float32), 0.8)
    cl, _ = cloth(size, '#2E2925', seed=3)
    img = img * (1 - turn_m[..., None]) + cl * turn_m[..., None]
    # pastedown edge casts a hairline shadow onto the turn-in
    edge_sh = gblur(np.clip(turn_m - np.roll(np.roll(turn_m, -2, 0), -2, 1), 0, 1), 2.0)
    img *= (1 - 0.0 * edge_sh)[..., None]
    # gutter: pages curve into the fold
    g = np.abs(x - F)
    gut = 1 - 0.50 * np.exp(-(g / 26.0) ** 2) - 0.22 * np.exp(-(g / 120.0) ** 2)
    hl = 0.06 * np.exp(-((x - F - 150) / 90.0) ** 2)  # flyleaf lifts and catches light
    img = img * (gut + hl)[..., None]
    img *= (0.88 + 0.16 * np.exp(-(((x - 600) / 1800) ** 2 + ((y - 400) / 1500) ** 2)))[..., None]
    u8 = finish(img, grain=0.008, seed=52)
    save(u8, out, q=90); preview(u8, out.replace('.jpg', '_prev.png'), 1100)

if __name__ == '__main__':
    import os; os.makedirs('out', exist_ok=True)
    import sys
    if 'outer' in sys.argv or len(sys.argv) == 1:
        make_outer('out/hon_outer.jpg')
    if 'inner' in sys.argv or len(sys.argv) == 1:
        make_inner('out/hon_inner.jpg')
    print('done')
