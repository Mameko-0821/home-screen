"""'Shoji no kage' pair: closed = Shiba's moon-shadow on a shoji; open = shoji slid aside, Shiba on the engawa."""
import numpy as np
from lib import *
from moon import moon_layers, bloom, sky_grad, starfield, composite
from shiba_path import SHIBA, TAIL_HOLE

def shiba_mask(size, x, ground_y, height, flip=False, ss=4):
    """Silhouette mask; (x, ground_y) = left of nose/ground line, height px (ear tip to ground)."""
    sc = height / 256.0
    polys = path_points(SHIBA, 30)
    t = np.linspace(0, 2 * np.pi, 60)
    cx, cy, rx, ry = TAIL_HOLE
    hole = np.stack([cx + rx * np.cos(t), cy + ry * np.sin(t)], 1)
    def tf(p):
        q = p.copy()
        if flip:
            q[:, 0] = 200 - q[:, 0]
        return np.stack([x + q[:, 0] * sc, ground_y + (q[:, 1] - 258) * sc], 1)
    m = raster([tf(p) for p in polys], size, ss)
    h = raster([tf(hole)], size, ss)
    return np.clip(m - h, 0, 1)

def maple_leaf(cx, cy, s, rot, rng):
    """Polygon list for a 7-lobed Japanese maple leaf, size s (px), rotation rot (rad)."""
    polys = []
    angs = np.deg2rad(np.array([-128, -88, -48, 0, 48, 88, 128])) * rng.uniform(0.92, 1.05)
    lens = np.array([0.42, 0.72, 0.92, 1.0, 0.92, 0.72, 0.42]) * rng.uniform(0.9, 1.1, 7)
    for a, L in zip(angs, lens):
        a2 = a + rot - np.pi / 2
        d = np.array([np.cos(a2), np.sin(a2)]); n = np.array([-d[1], d[0]])
        w = 0.21 * L
        pts = [np.zeros(2), d * L * 0.25 + n * w * 0.9, d * L * 0.55 + n * w, d * L * 0.82 + n * w * 0.5, d * L,
               d * L * 0.82 - n * w * 0.5, d * L * 0.55 - n * w, d * L * 0.25 - n * w * 0.9]
        polys.append(np.array(pts) * s + [cx, cy])
    t = np.linspace(0, 2 * np.pi, 20)
    polys.append(np.stack([np.cos(t), np.sin(t)], 1) * s * 0.2 + [cx, cy])
    # petiole
    a2 = rot + np.pi / 2
    d = np.array([np.cos(a2), np.sin(a2)])
    polys.append(stroke_poly(np.array([[cx, cy], [cx + d[0] * s * 0.7, cy + d[1] * s * 0.7]]), s * 0.05, s * 0.03))
    return polys

def maple_branch(size, start, end, bend, n_twigs, leaf_s, seed, ss=3, droop=1.0):
    """A natural-looking momiji branch: tapered main limb, side twigs, leaf clusters hanging off them."""
    rng = np.random.default_rng(seed)
    p0, p3 = np.array(start, float), np.array(end, float)
    d = p3 - p0
    n = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-9)
    p1 = p0 + d * 0.33 + np.array(bend, float) * 0.8
    p2 = p0 + d * 0.66 + np.array(bend, float) * 0.9
    main = cubic(p0, p1, p2, p3, 120)
    polys = [stroke_poly(main, leaf_s * 0.20, leaf_s * 0.045, 0.9)]
    def leaf_at(base, dirv, s):
        dirv = dirv / (np.linalg.norm(dirv) + 1e-9)
        c = base + dirv * s * 0.95
        rot = np.arctan2(dirv[1], dirv[0]) - np.pi / 2 + rng.uniform(-0.35, 0.35)
        out = maple_leaf(c[0], c[1], s, rot, rng)
        out.append(stroke_poly(np.array([base, base + dirv * s * 0.3]), s * 0.05, s * 0.035))
        return out
    ts = np.sort(rng.uniform(0.18, 0.98, n_twigs))
    for k, t in enumerate(ts):
        i = int(t * 119)
        b = main[i]
        tang = main[min(119, i + 1)] - main[max(0, i - 1)]
        tang /= (np.linalg.norm(tang) + 1e-9)
        side = 1 if k % 2 == 0 else -1
        tw = tang * rng.uniform(0.3, 0.8) + np.array([-tang[1], tang[0]]) * side * rng.uniform(0.5, 1.0) + np.array([0, 0.55 * droop])
        tw /= np.linalg.norm(tw)
        L = leaf_s * rng.uniform(1.2, 2.4) * (1.1 - 0.4 * t)
        q0 = b; q3 = b + tw * L
        q1 = b + tw * L * 0.4 + np.array([0, -L * 0.12]); q2 = q3 + np.array([0, -L * 0.15])
        twig = cubic(q0, q1, q2, q3, 30)
        polys.append(stroke_poly(twig, leaf_s * 0.07, leaf_s * 0.03))
        # leaves: a fan at the twig tip + a couple along it
        nf = int(rng.integers(3, 6))
        for j in range(nf):
            a = np.deg2rad(rng.uniform(-75, 75))
            base_dir = tw + np.array([0, 0.5 * droop])
            ca, sa = np.cos(a), np.sin(a)
            dv = np.array([base_dir[0] * ca - base_dir[1] * sa, base_dir[0] * sa + base_dir[1] * ca])
            polys += leaf_at(q3, dv, leaf_s * rng.uniform(0.7, 1.0))
        for j in range(int(rng.integers(0, 3))):
            u = rng.uniform(0.35, 0.8)
            bb = twig[int(u * 29)]
            dv = np.array([rng.uniform(-1, 1), rng.uniform(0.3, 1.0)])
            polys += leaf_at(bb, dv, leaf_s * rng.uniform(0.6, 0.85))
    # leaves at the very end of the main limb
    for j in range(3):
        dv = (p3 - main[-8]) + np.array([rng.uniform(-30, 30), 30 * droop])
        polys += leaf_at(p3, dv, leaf_s * rng.uniform(0.75, 0.95))
    return raster(polys, size, ss)

def washi(size, seed):
    """Transmission of backlit washi: ~1 with cloudy fibre density variations."""
    W, H = size
    rng = np.random.default_rng(seed)
    cloud = fbm((H, W), 90, 5, 0.55, seed=seed) * 0.055 + fbm((H, W), 22, 3, 0.5, seed=seed + 1) * 0.02
    fib = []
    for k in range(int(W * H / 900)):
        x, y = rng.uniform(-50, W + 50), rng.uniform(-50, H + 50)
        L = rng.uniform(25, 140); a = rng.uniform(0, np.pi)
        d = np.array([np.cos(a), np.sin(a)]); n = np.array([-d[1], d[0]])
        c = np.array([x, y]); bend = n * rng.uniform(-L * 0.25, L * 0.25)
        pts = np.array([c - d * L / 2, c + bend, c + d * L / 2])
        tt = np.linspace(0, 1, 12)[:, None]
        cl = (1 - tt) ** 2 * pts[0] + 2 * (1 - tt) * tt * pts[1] + tt * tt * pts[2]
        fib.append(stroke_poly(cl, rng.uniform(0.6, 1.6), 0.4))
    fm = raster(fib, size, 2)
    T = 1 + cloud - 0.10 * gblur(fm, 0.5) + rng.normal(0, 0.012, (H, W)).astype(np.float32)
    return T.astype(np.float32)

def wood(size, seed, base='#2B231D', vertical=True, amp=0.22):
    W, H = size
    if vertical:
        g = fbm((H, W), 7, 4, 0.5, seed=seed, cell_y=420) * 0.6 + fbm((H, W), 40, 3, 0.5, seed=seed + 3, cell_y=900) * 0.4
    else:
        g = fbm((H, W), 420, 4, 0.5, seed=seed, cell_y=7) * 0.6 + fbm((H, W), 900, 3, 0.5, seed=seed + 3, cell_y=40) * 0.4
    col = hexl(base)
    return col[None, None, :] * (1 + amp * g)[..., None]

def rects_mask(size, rects):
    W, H = size
    m = np.zeros((H, W), np.float32)
    for x0, y0, x1, y1 in rects:
        m[max(0, int(y0)):min(H, int(y1)), max(0, int(x0)):min(W, int(x1))] = 1
    return m

def shoji_panel(size, x0, x1, y0, y_rail, ncol, nrow, seed, light_center, shadows):
    """Render one shoji panel region onto a fresh canvas; returns rgb and mask of the panel area.
    shadows: list of (mask, strength) on the paper."""
    W, H = size
    T = washi(size, seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lx, ly, lr = light_center
    fall = np.exp(-((xx - lx) ** 2 + (yy - ly) ** 2) / (2 * lr * lr))
    illum = 0.50 + 0.55 * fall
    sh = np.ones((H, W), np.float32)
    for m, k in shadows:
        sh *= (1 - k * m)
    paper_col = hexl('#7E776B')
    paper = paper_col[None, None, :] * (T * illum * sh)[..., None]
    # bars
    bw = 12
    stile = 44
    rects = [(x0, 0, x0 + stile, H), (x1 - stile, 0, x1, H), (x0, 0, x1, 40), (x0, y_rail, x1, y_rail + 34)]
    inner_w = (x1 - stile) - (x0 + stile)
    for k in range(1, ncol):
        cx = x0 + stile + inner_w * k / ncol
        rects.append((cx - bw / 2, 40, cx + bw / 2, y_rail))
    inner_h = y_rail - 40
    for k in range(1, nrow):
        cy = 40 + inner_h * k / nrow
        rects.append((x0 + stile, cy - bw / 2, x1 - stile, cy + bw / 2))
    bars = gblur(rects_mask(size, rects), 0.7)
    kick = rects_mask(size, [(x0, y_rail + 34, x1, H)])
    wv = wood(size, seed + 5, '#2A221C', vertical=True)
    wh = wood(size, seed + 6, '#2A221C', vertical=False)
    vert_bars = gblur(rects_mask(size, [r for r in rects if (r[2] - r[0]) < (r[3] - r[1])]), 0.7)
    img = paper.copy()
    img = img * (1 - bars[..., None]) + (wv * vert_bars[..., None] + wh * (bars - vert_bars).clip(0, 1)[..., None])
    kp = wood(size, seed + 7, '#231C17', vertical=False, amp=0.3)
    # kick panel: subtle frame-and-panel bevel
    img = img * (1 - kick[..., None]) + kp * kick[..., None]
    # faint glow of the paper into the bar edges (halation)
    glow = gblur(paper * (1 - bars[..., None]) * (1 - kick[..., None]), 6) * 0.10
    img += glow
    area = rects_mask(size, [(x0, 0, x1, H)])
    return img, area

def make_outer(out):
    size = OUTER; W, H = size
    y_rail = 1752
    sh_m = shiba_mask(size, 150, y_rail, 600)
    shiba_sh = gblur(sh_m, 3.2) * 0.62 + gblur(sh_m, 9) * 0.10
    leaves = maple_branch(size, (-120, -40), (760, 330), (40, 120), 9, 66, seed=21)
    far = maple_branch(size, (300, -160), (1250, 200), (0, 140), 7, 80, seed=27)
    leaves_sh = np.clip(gblur(leaves, 3.2) * 0.46 + gblur(far, 12) * 0.22, 0, 0.6)
    yy0 = np.arange(H, dtype=np.float32)[:, None]
    eaves = (1 - smoothstep(110, 330, yy0)) * np.ones((1, W), np.float32) * 0.42
    img, _ = shoji_panel(size, 0, W, 0, y_rail, 3, 4, seed=31, light_center=(240, 300, 1050),
                         shadows=[(shiba_sh, 1.0), (leaves_sh, 1.0), (eaves, 1.0)])
    vign = sky_grad(size, [(0, '#FFFFFF'), (1, '#FFFFFF')])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.40 * smoothstep(0.35, 1.25, np.hypot((xx - W * 0.35) / W, (yy - H * 0.35) / H) * 1.6)
    img *= v[..., None]
    u8 = finish(img, grain=0.010, seed=41)
    save(u8, out); preview(u8, out.replace('.jpg', '_prev.png'), 700)

def make_inner(out):
    size = INNER; W, H = size
    F = W // 2
    y_rail = 1640
    # right page: the slid shoji
    leaves_r = maple_branch(size, (1380, -120), (2250, 120), (0, 120), 7, 62, seed=23)
    leaves_r_sh = np.clip(gblur(leaves_r, 3.6) * 0.40, 0, 0.6)
    yy0 = np.arange(H, dtype=np.float32)[:, None]
    eaves_r = (1 - smoothstep(100, 320, yy0)) * np.ones((1, W), np.float32) * 0.40
    shoji, area = shoji_panel(size, F - 22, W, 0, y_rail, 3, 4, seed=33, light_center=(F + 120, 260, 1150),
                              shadows=[(leaves_r_sh, 1.0), (eaves_r, 1.0)])
    # left page: the view out to the garden
    sky = sky_grad(size, [(0, '#0B0A09'), (0.5, '#100E0C'), (0.62, '#16120F'), (1, '#1C1611')])
    mx, my, R = 360, 380, 112
    em, cov = moon_layers(size, mx, my, R, (-0.10, 0.03, 0.995))
    st = starfield(size, 130, 5, ymax=0.52, avoid=(mx, my, R))
    img = sky + st * (1 - cov[..., None])
    img = img * (1 - cov[..., None]) + em
    img += bloom(em, 1.0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # distant trees (soft, hazy)
    ridge = 1040 + 60 * fbm((1, W), 220, 4, seed=8)[0] + 40 * fbm((1, W), 60, 3, seed=9)[0]
    trees = (yy > ridge[None, :]).astype(np.float32)
    trees = gblur(trees, 4)
    mist = np.exp(-((yy - 1010) / 70.0) ** 2) * (0.6 + 0.4 * fbm((H, W), 300, 3, seed=12, cell_y=60))
    img += (mist * (1 - trees))[..., None] * hexl('#2A241D') * 0.55
    img = composite(img, trees, hexl('#0E0C0A'))
    # garden ground
    ground_top = 1180
    g = smoothstep(ground_top - 30, ground_top + 30, yy)
    img = composite(img, g, hexl('#0A0908'))
    # engawa (boards), from its outer edge to the sill
    e_top, e_bot = 1300, y_rail
    edge = rects_mask(size, [(0, e_top, F, e_top + 26)])
    boards = rects_mask(size, [(0, e_top + 26, F, e_bot)])
    bw = wood(size, 51, '#2A2019', vertical=False, amp=0.25)
    img = composite(img, edge, hexl('#14100D'))
    img = img * (1 - boards[..., None]) + bw * boards[..., None]
    # board seams with perspective spacing
    ys, y = [], e_top + 26
    step = 26
    while y < e_bot:
        ys.append(y); y += step; step *= 1.13
    seam = rects_mask(size, [(0, yv - 1.5, F, yv + 1.5) for yv in ys[1:]])
    img = composite(img, gblur(seam, 0.8) * 0.8, hexl('#110D0A'))
    # moon reflection pooled on the polished boards
    refl = np.exp(-((xx - mx - 30) ** 2) / (2 * 150 ** 2)) * smoothstep(e_top + 20, e_top + 140, yy) * (1 - smoothstep(e_bot - 220, e_bot, yy))
    img += (refl * boards)[..., None] * hexl('#3A3127') * 0.9
    # Shiba on the engawa + its shadow towards us
    gy = 1520
    sm = shiba_mask(size, 120, gy, 520)
    # shadow on boards (flip, squash, shear)
    from PIL import Image as _I
    shadow = np.zeros((H, W), np.float32)
    ys_, xs_ = np.nonzero(sm > 0.01)
    if len(ys_):
        sub = sm[ys_.min():gy + 1, xs_.min():xs_.max() + 1]
        h, w = sub.shape
        sq = np.asarray(_I.fromarray(sub[::-1]).resize((w, max(2, int(h * 0.24))), _I.BILINEAR))
        hh = sq.shape[0]
        for r in range(hh):
            off = int(r * 0.9)
            x0 = xs_.min() + off
            x1 = min(W, x0 + w)
            if gy + r < H and x0 < W:
                shadow[gy + r, x0:x1] = np.maximum(shadow[gy + r, x0:x1], sq[r, :x1 - x0])
    shadow = gblur(shadow, 6) * boards
    img *= (1 - 0.55 * shadow)[..., None]
    # silhouette with moon rim light (light from upper-left)
    rim = np.clip(sm - np.roll(np.roll(sm, 5, 0), 5, 1), 0, 1)
    rim = gblur(rim, 1.2)
    img = composite(img, sm, hexl('#0B0907'))
    img += (rim * sm)[..., None] * hexl('#6E6252') * 0.35
    # maple branch silhouette at the top of the opening (near, dark)
    br = maple_branch(size, (-120, -30), (820, 250), (40, 110), 7, 58, seed=21)
    img = composite(img, gblur(br, 0.8), hexl('#090807'))
    # architecture: pillar on the left edge, lintel at the top, sill + floor at the bottom
    arch_v = rects_mask(size, [(0, 0, 46, H)])
    arch_h = rects_mask(size, [(0, 0, F, 52)])
    sill = rects_mask(size, [(0, y_rail, F, y_rail + 40)])
    floor = rects_mask(size, [(0, y_rail + 40, F, H)])
    img = img * (1 - arch_v[..., None]) + wood(size, 61, '#1F1915', True) * arch_v[..., None]
    img = img * (1 - arch_h[..., None]) + wood(size, 62, '#1F1915', False) * arch_h[..., None]
    img = img * (1 - sill[..., None]) + wood(size, 63, '#2A221C', False) * sill[..., None]
    img = img * (1 - floor[..., None]) + wood(size, 64, '#15110E', False, 0.12) * floor[..., None]
    # combine with the shoji panel on the right page
    img = img * (1 - area[..., None]) + shoji * 0.76 * area[..., None]
    u8 = finish(img, grain=0.010, seed=42)
    save(u8, out); preview(u8, out.replace('.jpg', '_prev.png'), 1100)

if __name__ == '__main__':
    import os; os.makedirs('out', exist_ok=True)
    make_outer('out/shoji_outer.jpg')
    make_inner('out/shoji_inner.jpg')
    print('done')
