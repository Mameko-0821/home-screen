"""Moon texture + rendering, susuki grass, and the 'michiru tsuki' pair."""
import numpy as np, sys
from lib import *

MARIA = [  # cx, cy, rx, ry, angle(deg), darkness   (disk coords, y up)
    (-0.60, 0.05, 0.27, 0.55, 10, 0.40),   # Oceanus Procellarum
    (-0.46, -0.22, 0.20, 0.22, 0, 0.30),
    (-0.25, 0.48, 0.28, 0.23, -15, 0.46),  # Imbrium
    (-0.42, 0.63, 0.07, 0.05, 0, 0.35),    # Sinus Iridum
    (-0.05, 0.78, 0.48, 0.065, -8, 0.32),  # Frigoris
    (0.22, 0.42, 0.15, 0.145, 0, 0.47),    # Serenitatis
    (0.05, 0.22, 0.075, 0.05, 0, 0.32),    # Vaporum
    (0.38, 0.14, 0.20, 0.16, 25, 0.45),    # Tranquillitatis
    (0.72, 0.27, 0.085, 0.10, 0, 0.50),    # Crisium
    (0.62, -0.08, 0.10, 0.16, 10, 0.42),   # Fecunditatis
    (0.40, -0.27, 0.075, 0.075, 0, 0.40),  # Nectaris
    (-0.30, 0.10, 0.12, 0.08, 0, 0.26),    # Insularum
    (-0.25, -0.12, 0.10, 0.07, 0, 0.30),   # Cognitum
    (-0.18, -0.35, 0.17, 0.13, 0, 0.36),   # Nubium
    (-0.52, -0.42, 0.09, 0.09, 0, 0.42),   # Humorum
    (0.0, 0.03, 0.05, 0.04, 0, 0.22),      # Sinus Medii
]
BRIGHT = [(-0.12, -0.70, 0.024, 1.0, 14), (-0.33, 0.18, 0.018, 0.7, 8), (-0.55, 0.13, 0.012, 0.5, 6),
          (-0.73, 0.38, 0.012, 0.9, 0), (0.62, 0.24, 0.010, 0.6, 0)]

_ALB = {}
def moon_albedo(M=1024, seed=5):
    if M in _ALB:
        return _ALB[M]
    y, x = np.mgrid[0:M, 0:M].astype(np.float32)
    u = (x + 0.5) / M * 2 - 1
    v = 1 - (y + 0.5) / M * 2
    hl = 0.93 + 0.05 * fbm((M, M), M / 6, 7, 0.55, seed=seed) + 0.025 * fbm((M, M), M / 40, 4, 0.6, seed=seed + 3)
    du = 0.035 * fbm((M, M), M / 5, 4, seed=seed + 11)
    dv = 0.035 * fbm((M, M), M / 5, 4, seed=seed + 12)
    uu, vv = u + du, v + dv
    mask = np.zeros((M, M), np.float32)
    for cx, cy, rx, ry, ang, dk in MARIA:
        a = np.deg2rad(ang)
        px, py = uu - cx, vv - cy
        qx = (px * np.cos(a) + py * np.sin(a)) / rx
        qy = (-px * np.sin(a) + py * np.cos(a)) / ry
        d = np.sqrt(qx * qx + qy * qy)
        m = smoothstep(1.08, 0.70, d) * dk
        mask = np.maximum(mask, m)
    mvar = 0.85 + 0.15 * fbm((M, M), M / 14, 4, seed=seed + 21)
    alb = hl * (1 - mask * mvar)
    # bright ray craters
    for cx, cy, r, amp, nrays in BRIGHT:
        d = np.sqrt((u - cx) ** 2 + (v - cy) ** 2)
        alb += amp * 0.22 * np.exp(-(d / r) ** 2) + amp * 0.05 * np.exp(-(d / (r * 3.5)) ** 2)
        if nrays:
            rng = np.random.default_rng(int(abs(cx) * 1000) + nrays)
            th = np.arctan2(v - cy, u - cx)
            for k in range(nrays):
                t0 = rng.uniform(-np.pi, np.pi); L = rng.uniform(0.25, 0.85); w = rng.uniform(0.010, 0.022)
                dth = np.angle(np.exp(1j * (th - t0)))
                perp = np.abs(np.sin(dth)) * d
                along = np.cos(dth) * d
                ray = np.exp(-(perp / w) ** 2) * smoothstep(L, 0.02, along) * (along > 0)
                alb += 0.05 * amp * ray
    _ALB[M] = alb.astype(np.float32)
    return _ALB[M]


_MAP = None
MOON_URL = 'https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_poles_2k.tif'
def moon_map():
    global _MAP
    if _MAP is None:
        import os, urllib.request
        from PIL import Image
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache', 'lroc_color_poles_2k.tif')
        if not os.path.exists(path):  # NASA SVS CGI Moon Kit colour map (public domain)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            urllib.request.urlretrieve(MOON_URL, path)
        im = Image.open(path).convert('RGB')
        _MAP = s2l(np.asarray(im, dtype=np.float32) / 255.0)
    return _MAP

def _bilinear(tex, mx, my):
    Hm, Wm = tex.shape[:2]
    x0 = np.floor(mx).astype(int); y0 = np.floor(my).astype(int)
    fx = (mx - x0)[..., None]; fy = (my - y0)[..., None]
    x0 %= Wm; x1 = (x0 + 1) % Wm
    y0 = np.clip(y0, 0, Hm - 1); y1 = np.clip(y0 + 1, 0, Hm - 1)
    a = tex[y0, x0] * (1 - fx) + tex[y0, x1] * fx
    b = tex[y1, x0] * (1 - fx) + tex[y1, x1] * fx
    return a * (1 - fy) + b * fy

MOON_TINT = np.array([1.0, 0.955, 0.88], np.float32)

def render_moon(R, L=(0, 0, 1), earth=0.0, ss=3, limb=0.10, gain=1.35):
    """Return (rgb_lin [N,N,3], alpha [N,N]) for a moon of radius R px; N = 2R+4.
    Surface: NASA SVS CGI Moon Kit colour map (public domain), orthographic near side."""
    N = int(2 * R + 4)
    M = N * ss
    tex = moon_map()
    Hm, Wm = tex.shape[:2]
    y, x = np.mgrid[0:M, 0:M].astype(np.float32)
    cx = M / 2
    u = (x + 0.5 - cx) / (R * ss)
    v = -(y + 0.5 - cx) / (R * ss)
    r2 = u * u + v * v
    inside = r2 < 1
    nz = np.sqrt(np.clip(1 - r2, 0, 1))
    lat = np.arcsin(np.clip(v, -1, 1))
    lon = np.arctan2(u, nz)
    mx = (lon / (2 * np.pi) + 0.5) * Wm - 0.5
    my = (0.5 - lat / np.pi) * Hm - 0.5
    alb = _bilinear(tex, mx, my) * MOON_TINT
    Lx, Ly, Lz = np.array(L, np.float32) / np.linalg.norm(L)
    mu0 = u * Lx + v * Ly + nz * Lz
    ls = np.where(mu0 > 0, 2 * mu0 / (mu0 + nz + 1e-4), 0)
    ls = np.clip(ls, 0, 1.6)
    lumf = ls * (1 - limb + limb * np.sqrt(nz)) + earth
    rgb = alb * (gain * lumf)[..., None]
    rgb *= inside[..., None]
    alpha = inside.astype(np.float32)
    rgb = rgb.reshape(N, ss, N, ss, 3).mean((1, 3))
    alpha = alpha.reshape(N, ss, N, ss).mean((1, 3))
    return rgb.astype(np.float32), alpha.astype(np.float32)

def place(layer, sub, x0, y0):
    """Add sub (h,w[,c]) into layer at top-left (x0,y0), clipped."""
    H, W = layer.shape[:2]
    h, w = sub.shape[:2]
    xa, ya = max(0, x0), max(0, y0)
    xb, yb = min(W, x0 + w), min(H, y0 + h)
    if xa >= xb or ya >= yb:
        return
    layer[ya:yb, xa:xb] += sub[ya - y0:yb - y0, xa - x0:xb - x0]

def moon_layers(size, cx, cy, R, L, earth=0.0):
    """Moon emission + coverage on a full canvas."""
    W, H = size
    rgb, a = render_moon(R, L, earth)
    N = rgb.shape[0]
    em = np.zeros((H, W, 3), np.float32); cov = np.zeros((H, W), np.float32)
    x0, y0 = int(round(cx - N / 2)), int(round(cy - N / 2))
    place(em, rgb, x0, y0); place(cov, a, x0, y0)
    return em, cov

def bloom(em, strength=1.0, sig=(5, 18, 60, 190), w=(0.30, 0.16, 0.085, 0.05)):
    out = np.zeros_like(em)
    for s, k in zip(sig, w):
        out += gblur(em, s) * k
    return out * strength

def starfield(size, n, seed, ymax=1.0, avoid=None):
    W, H = size
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0, W, n); ys = H * ymax * (rng.uniform(0, 1, n) ** 1.25)
    mag = rng.uniform(0, 1, n) ** 4.0
    amps = 0.012 + 0.32 * mag
    sig = 0.55 + 0.75 * mag
    if avoid is not None:
        ax, ay, ar = avoid
        d = np.hypot(xs - ax, ys - ay)
        amps *= smoothstep(ar * 0.9, ar * 2.6, d)
    st = gauss_splats(size, xs, ys, amps, sig)
    tints = np.stack([np.ones(n), 0.93 + 0.05 * rng.uniform(0, 1, n), 0.82 + 0.1 * rng.uniform(0, 1, n)], 1)
    # colourise with a single warm-white
    return st[..., None] * np.array([1.0, 0.95, 0.86], np.float32)

def sky_grad(size, stops):
    """stops: list of (t, hex) along y (0 top .. 1 bottom); interpolate in linear."""
    W, H = size
    t = (np.arange(H, dtype=np.float32) + 0.5) / H
    ts = np.array([s[0] for s in stops], np.float32)
    cs = np.stack([hexl(s[1]) for s in stops])
    col = np.stack([np.interp(t, ts, cs[:, c]) for c in range(3)], -1)
    return np.broadcast_to(col[:, None, :], (H, W, 3)).copy()

# ---------- susuki (Japanese pampas grass) ----------
def _quad(p0, c, p1, n=40):
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t * t * p1

def susuki(size, clumps, seed=1, sc=1.0, ss=3, wind=1.0):
    """clumps: list of dicts {x, n_leaves, leaf_len, stems:[(dx, height, lean, plume_len)]}
    Returns masks: dark (leaves+stems), fluff (soft plume), core (raceme lines)."""
    W, H = size
    rng = np.random.default_rng(seed)
    dark, fluff, core = [], [], []
    for cl in clumps:
        bx = cl['x']; by = H + 40 * sc
        # leaves: rise steeply then arch outward, tips drooping a little
        for k in range(cl['n_leaves']):
            L = cl['leaf_len'] * rng.uniform(0.55, 1.0) * sc
            side = rng.choice([-1, 1]) * (1 if rng.uniform() < 0.5 else 1)
            ang = np.deg2rad(rng.uniform(4, 38)) * side + np.deg2rad(6) * wind
            x0 = bx + rng.uniform(-25, 25) * sc
            p0 = np.array([x0, by])
            up = np.array([np.sin(ang), -np.cos(ang)])
            p1 = p0 + up * L * 0.55
            p2 = p1 + (up * 0.55 + np.array([side * 0.55 + 0.25 * wind, 0.05])) * L * 0.45
            p3 = p2 + np.array([side * 0.35 + 0.2 * wind, 0.55]) * L * rng.uniform(0.15, 0.35)
            dark.append(stroke_poly(cubic(p0, p1, p2, p3, 60), rng.uniform(6, 9) * sc, 0.5 * sc, 0.9))
        for (dx, h, lean, pl) in cl['stems']:
            p0 = np.array([bx + dx * sc, by])
            top = p0 + np.array([lean * sc, -h * sc])
            c = (p0 + top) / 2 + np.array([lean * sc * 0.45, 0])
            stem = _quad(p0, c, top, 50)
            dark.append(stroke_poly(stem, 5.0 * sc, 2.0 * sc))
            pl = pl * sc
            d = top - stem[-5]; d /= np.linalg.norm(d)
            # short main axis continuing the stem
            ax = _quad(top, top + d * pl * 0.12, top + d * pl * 0.22 + np.array([wind * pl * 0.05, 0]), 20)
            dark.append(stroke_poly(ax, 2.0 * sc, 1.2 * sc))
            nr = int(rng.integers(22, 32))
            for k in range(nr):
                t = rng.uniform(0, 1) ** 0.8
                o = ax[int(t * (len(ax) - 1))]
                L = pl * rng.uniform(0.55, 1.0) * (1.0 - 0.35 * t)
                a0 = np.deg2rad(rng.uniform(-10, 38)) * wind
                v0 = np.array([np.sin(a0), -np.cos(a0)])
                p1 = o + v0 * L * 0.35
                p2 = p1 + np.array([wind * 0.42, 0.05 + rng.uniform(0, 0.25)]) * L
                p3 = p2 + np.array([wind * rng.uniform(0.12, 0.30), rng.uniform(0.28, 0.55)]) * L
                curve = cubic(o, p1, p2, p3, 48)
                fluff.append(stroke_poly(curve, rng.uniform(7, 12) * sc, 3.0 * sc, 1.2))
                core.append(stroke_poly(curve, 1.0 * sc, 0.35 * sc, 0.8))
                # silky hairs along the raceme, swept downwind
                tang = np.gradient(curve, axis=0)
                tang /= (np.linalg.norm(tang, axis=1, keepdims=True) + 1e-9)
                for j in range(4, len(curve), 2):
                    for sgn in (-1, 1):
                        if rng.uniform() < 0.25:
                            continue
                        hl = rng.uniform(5, 13) * sc * (1 - 0.5 * j / len(curve))
                        rot = np.deg2rad(rng.uniform(18, 48)) * sgn
                        tx, ty = tang[j]
                        hv = np.array([tx * np.cos(rot) - ty * np.sin(rot), tx * np.sin(rot) + ty * np.cos(rot)])
                        hv = hv + np.array([0.25 * wind, 0.35])
                        hv /= np.linalg.norm(hv)
                        a = curve[j]; b = a + hv * hl
                        core.append(np.array([a + [0.35 * sc, 0], b, a - [0.35 * sc, 0]]))
    return raster(dark, size, ss), raster(fluff, size, ss), raster(core, size, ss)

def composite(img, alpha, color):
    return img * (1 - alpha[..., None]) + np.asarray(color, np.float32) * alpha[..., None]

def make(fmt, out):
    if fmt == 'outer':
        size = OUTER; W, H = size
        sky = sky_grad(size, [(0, '#0A0908'), (0.55, '#100E0C'), (0.82, '#1A1511'), (1, '#2A1F17')])
        cx, cy, R = 336, 612, 112
        L = (0.62, -0.36, -0.70)
        em, cov = moon_layers(size, cx, cy, R, L, earth=0.012)
        em *= 1.55
        stars = starfield(size, 150, 7, ymax=0.82, avoid=(cx, cy, R))
        clumps = [dict(x=140, n_leaves=16, leaf_len=520, stems=[(-40, 660, 40, 210), (30, 560, 90, 190), (90, 430, 120, 170)]),
                  dict(x=-60, n_leaves=8, leaf_len=420, stems=[(40, 520, 50, 190)])]
        sc = 0.72
    else:
        size = INNER; W, H = size
        sky = sky_grad(size, [(0, '#0A0908'), (0.6, '#0F0D0B'), (0.86, '#17130F'), (1, '#211912')])
        cx, cy, R = 340, 482, 140
        L = (-0.10, 0.03, 0.995)
        em, cov = moon_layers(size, cx, cy, R, L, earth=0.0)
        stars = starfield(size, 260, 11, ymax=0.78, avoid=(cx, cy, R))
        clumps = [dict(x=120, n_leaves=22, leaf_len=640, stems=[(-60, 860, 40, 250), (0, 760, 90, 240), (60, 640, 130, 220), (120, 520, 150, 200)]),
                  dict(x=520, n_leaves=14, leaf_len=480, stems=[(-20, 480, 80, 190), (40, 380, 110, 170)]),
                  dict(x=-80, n_leaves=10, leaf_len=520, stems=[(50, 700, 40, 220)]),
                  dict(x=2080, n_leaves=12, leaf_len=380, stems=[(0, 330, 70, 160), (60, 260, 90, 140)]),
                  dict(x=2430, n_leaves=10, leaf_len=340, stems=[(10, 300, 60, 150)])]
        sc = 0.8
    img = sky + stars * (1 - cov[..., None])
    img = img * (1 - cov[..., None]) + em
    img += bloom(em, 1.0)
    da, fa, ca = susuki(size, clumps, seed=5, sc=sc, wind=1.0)
    # moonlight from upper-left catches the plumes; stems/leaves stay silhouettes
    img = composite(img, gblur(da, 0.6), hexl('#060504'))
    img = composite(img, gblur(fa, 3.0) * 0.30, hexl('#4A433A'))
    img = composite(img, gblur(ca, 0.7) * 0.62, hexl('#8A806F'))
    u8 = finish(img, grain=0.011, seed=3 if fmt == 'outer' else 4)
    save(u8, out)
    preview(u8, out.replace('.jpg', '_prev.png'), 700 if fmt == 'outer' else 1100)

if __name__ == '__main__':
    import os; os.makedirs('out', exist_ok=True)
    make('outer', 'out/tsuki_outer.jpg')
    make('inner', 'out/tsuki_inner.jpg')
    print('done')
