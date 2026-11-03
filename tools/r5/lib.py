"""Shared helpers for the round-5 wallpaper renders (numpy + PIL only)."""
import numpy as np
from PIL import Image, ImageDraw

OUTER = (1398, 2034)   # closed: width, height
INNER = (2670, 1878)   # open:   width, height

# ---------- colour ----------
def s2l(c):
    c = np.asarray(c, dtype=np.float32)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4).astype(np.float32)

def l2s(c):
    c = np.clip(np.asarray(c, dtype=np.float32), 0, None)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055).astype(np.float32)

def hexl(h):
    h = h.lstrip('#')
    return s2l(np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], dtype=np.float32))

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)

# ---------- blur ----------
def _gblur_fft(a, sigma):
    pad = int(3 * sigma) + 2
    if a.ndim == 2:
        a3 = a[..., None]
    else:
        a3 = a
    p = np.pad(a3, ((pad, pad), (pad, pad), (0, 0)), mode='reflect')
    H, W = p.shape[:2]
    fy = np.fft.fftfreq(H)[:, None]
    fx = np.fft.rfftfreq(W)[None, :]
    tf = np.exp(-2 * (np.pi ** 2) * sigma * sigma * (fy * fy + fx * fx)).astype(np.float32)
    out = np.empty_like(p)
    for c in range(p.shape[2]):
        out[..., c] = np.fft.irfft2(np.fft.rfft2(p[..., c]) * tf, s=(H, W))
    out = out[pad:-pad, pad:-pad]
    return out[..., 0] if a.ndim == 2 else out

def resize_f(a, size):
    """Resize float array (H,W) or (H,W,C) to size=(W,H) with bicubic."""
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), 'F').resize(size, Image.BICUBIC))
    return np.stack([resize_f(a[..., c], size) for c in range(a.shape[2])], -1)

def gblur(a, sigma):
    if sigma <= 0.3:
        return a
    if sigma <= 10:
        return _gblur_fft(a, sigma)
    k = sigma / 5.0
    H, W = a.shape[:2]
    small = resize_f(a, (max(8, int(W / k)), max(8, int(H / k))))
    small = _gblur_fft(small, sigma / k)
    return resize_f(small, (W, H))

# ---------- noise ----------
def vnoise(shape, cell, seed, cell_y=None):
    """Smooth value noise in [-1,1]. shape=(H,W); cell in px (x), optional cell_y."""
    H, W = shape
    cy = cell_y or cell
    rng = np.random.default_rng(seed)
    gw, gh = int(np.ceil(W / cell)) + 4, int(np.ceil(H / cy)) + 4
    g = rng.uniform(-1, 1, (gh, gw)).astype(np.float32)
    big = np.asarray(Image.fromarray(g, 'F').resize((int(gw * cell), int(gh * cy)), Image.BICUBIC))
    ox, oy = int(cell * 1.5), int(cy * 1.5)
    return big[oy:oy + H, ox:ox + W]

def fbm(shape, cell, octaves=5, pers=0.5, lac=2.0, seed=0, cell_y=None, min_cell=1.5):
    tot = np.zeros(shape, np.float32)
    amp, norm, c, cy = 1.0, 0.0, float(cell), float(cell_y or cell)
    for o in range(octaves):
        if min(c, cy) < min_cell:
            break
        tot += amp * vnoise(shape, c, seed * 101 + o * 7 + 1, cell_y=cy)
        norm += amp
        amp *= pers
        c /= lac
        cy /= lac
    return tot / max(norm, 1e-6)

# ---------- shapes ----------
def cubic(p0, p1, p2, p3, n=24):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.asarray, (p0, p1, p2, p3))
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + (t ** 3) * p3

def path_points(d, n=24):
    """Tiny absolute SVG path parser (M L C Q Z). Returns list of polygons (Nx2)."""
    import re
    toks = re.findall(r'[MLCQZ]|-?\d*\.?\d+(?:e-?\d+)?', d)
    polys, cur, pts, i, cmd = [], None, [], 0, None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v
    while i < len(toks):
        t = toks[i]
        if t in 'MLCQZ':
            cmd = t; i += 1
            if cmd == 'Z':
                if pts:
                    polys.append(np.array(pts)); pts = []
                continue
        if cmd == 'M':
            if pts:
                polys.append(np.array(pts))
            cur = (num(), num()); pts = [cur]; cmd = 'L'
        elif cmd == 'L':
            cur = (num(), num()); pts.append(cur)
        elif cmd == 'C':
            c1 = (num(), num()); c2 = (num(), num()); e = (num(), num())
            seg = cubic(cur, c1, c2, e, n); pts.extend(map(tuple, seg[1:])); cur = e
        elif cmd == 'Q':
            q = (num(), num()); e = (num(), num())
            c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            c2 = (e[0] + 2 / 3 * (q[0] - e[0]), e[1] + 2 / 3 * (q[1] - e[1]))
            seg = cubic(cur, c1, c2, e, n); pts.extend(map(tuple, seg[1:])); cur = e
    if pts:
        polys.append(np.array(pts))
    return polys

def raster(polys, size, ss=4, bbox=None):
    """Anti-aliased coverage mask (H,W) float for filled polygons (pixel coords). size=(W,H)."""
    W, H = size
    im = Image.new('L', (W * ss, H * ss), 0)
    d = ImageDraw.Draw(im)
    for p in polys:
        p = np.asarray(p, dtype=np.float64)
        if len(p) < 3:
            continue
        d.polygon([(float(x) * ss, float(y) * ss) for x, y in p], fill=255)
    return np.asarray(im.resize((W, H), Image.BOX), dtype=np.float32) / 255.0

def stroke_poly(pts, w0, w1, taper_pow=1.0):
    """Tapered stroke polygon around centreline pts (Nx2), width w0 -> w1."""
    pts = np.asarray(pts, dtype=np.float64)
    d = np.gradient(pts, axis=0)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    nrm /= (np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9)
    t = np.linspace(0, 1, len(pts)) ** taper_pow
    w = (w0 + (w1 - w0) * t)[:, None] / 2
    left = pts + nrm * w
    right = pts - nrm * w
    return np.vstack([left, right[::-1]])

def gauss_splats(size, xs, ys, amps, sigmas):
    """Sum of small gaussian dots, returns (H,W)."""
    W, H = size
    out = np.zeros((H, W), np.float32)
    for x, y, a, s in zip(xs, ys, amps, sigmas):
        r = int(np.ceil(s * 4))
        x0, x1 = max(0, int(x) - r), min(W, int(x) + r + 2)
        y0, y1 = max(0, int(y) - r), min(H, int(y) + r + 2)
        if x0 >= x1 or y0 >= y1:
            continue
        yy, xx = np.mgrid[y0:y1, x0:x1]
        out[y0:y1, x0:x1] += a * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * s * s))
    return out

# ---------- output ----------
def finish(img_lin, grain=0.012, seed=0, grain_blur=0.55):
    """linear RGB -> sRGB uint8 with soft film grain + dither."""
    s = l2s(img_lin)
    H, W = s.shape[:2]
    rng = np.random.default_rng(seed + 999)
    if grain > 0:
        g = rng.normal(0, 1, (H, W)).astype(np.float32)
        g = gblur(g, grain_blur)
        g /= (g.std() + 1e-6)
        # grain is a bit weaker in deep shadows and highlights
        lum = s.mean(-1)
        wgt = 0.55 + 0.45 * np.sin(np.clip(lum, 0, 1) * np.pi) 
        s = s + (g * grain * wgt)[..., None]
        c = rng.normal(0, 1, (H, W, 3)).astype(np.float32) * grain * 0.25
        s = s + c
    s = s * 255 + rng.uniform(-0.5, 0.5, s.shape)
    return np.clip(s, 0, 255).astype(np.uint8)

def save(u8, path, q=92):
    Image.fromarray(u8).save(path, quality=q, subsampling=0, optimize=True)

def preview(u8, path, w=700):
    im = Image.fromarray(u8)
    h = int(im.height * w / im.width)
    im.resize((w, h), Image.LANCZOS).save(path)
