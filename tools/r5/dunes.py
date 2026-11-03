"""'Yoake no sakyu' pair: height-field dune renderer (voxel-space visibility + shadow rays)."""
import numpy as np, sys, time
from lib import *

def periodic_noise(N=1024, beta=2.2, seed=0):
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 1, (N, N))
    fy = np.fft.fftfreq(N)[:, None]; fx = np.fft.fftfreq(N)[None, :]
    f = np.sqrt(fx * fx + fy * fy); f[0, 0] = 1
    spec = np.fft.fft2(w) / f ** (beta / 2)
    spec[0, 0] = 0
    n = np.real(np.fft.ifft2(spec))
    n = (n - n.mean()) / (n.std() * 2.2)
    return n.astype(np.float32)

def smooth_noise(N=1024, f0=8.0, seed=0):
    rng = np.random.default_rng(seed)
    w = rng.normal(0, 1, (N, N))
    fy = np.fft.fftfreq(N)[:, None] * N; fx = np.fft.fftfreq(N)[None, :] * N
    spec = np.fft.fft2(w) * np.exp(-(fx * fx + fy * fy) / (f0 * f0))
    spec[0, 0] = 0
    n = np.real(np.fft.ifft2(spec))
    return (n / (n.std() * 2.0)).astype(np.float32)

NT = smooth_noise(1024, 9.0, 3)      # large, smooth features only
NT2 = periodic_noise(1024, 1.6, 9)   # fine texture (ripples, albedo)

def tex(T, u, v):
    N = T.shape[0]
    x = (u * N) % N; y = (v * N) % N
    xf = np.floor(x); yf = np.floor(y)
    fx = x - xf; fy = y - yf
    x0 = xf.astype(np.int32) % N; y0 = yf.astype(np.int32) % N
    x1 = (x0 + 1) % N; y1 = (y0 + 1) % N
    a = T[y0, x0] * (1 - fx) + T[y0, x1] * fx
    b = T[y1, x0] * (1 - fx) + T[y1, x1] * fx
    return a * (1 - fy) + b * fy

RIP = dict(amp=0.016)
P = dict(ang=66.0, lam=68.0, k=0.74, amp=10.0, warp=55.0)

def height(x, z):
    wx = x + P['warp'] * tex(NT, x / 2000, z / 2000)
    wz = z + P['warp'] * tex(NT, x / 2000 + 0.37, z / 2000 + 0.61)
    a = np.deg2rad(P['ang'])
    s = (wx * np.cos(a) + wz * np.sin(a)) / P['lam'] + 0.9 * tex(NT, x / 1800 + 0.5, z / 1800 + 0.2)
    f = s - np.floor(s)
    k = P['k']
    a1 = f / k; b1 = (1 - f) / (1 - k)
    kk = 0.03 + np.abs(z) / 9000.0
    hh = np.clip(kk - np.abs(a1 - b1), 0, None) / kk
    prof = np.minimum(a1, b1) - hh * hh * kk / 4
    prof = 0.65 * prof + 0.35 * prof * prof * (3 - 2 * prof)
    A = P['amp'] * (0.6 + 0.4 * tex(NT, x / 2600 + 0.7, z / 2600 + 0.3))
    h = A * prof + 18 * tex(NT, x / 4200 + 0.2, z / 4200 + 0.9)
    return h.astype(np.float32)

def ripple(x, z, footprint):
    a = np.deg2rad(P['ang'] + 8)
    s = (x * np.cos(a) + z * np.sin(a)) / 0.32 + 3.0 * tex(NT, x / 60, z / 60) + 8 * tex(NT, x / 300 + .3, z / 300)
    fade = np.clip(1 - footprint / 0.035, 0, 1) ** 1.5
    patch = np.clip(0.35 + 0.65 * (0.5 + tex(NT, x / 140 + .1, z / 140 + .7)), 0, 1)
    return RIP['amp'] * np.sin(2 * np.pi * s) * fade * patch

def render(size, f, hy, cam_y, sun, sky_fn, mode, ss=1.5, zmax=5000, steps=2200, seed=0):
    W0, H0 = size
    W, H = int(W0 * ss), int(H0 * ss)
    f = f * ss; hy = hy * ss
    cx = W / 2
    cols = (np.arange(W, dtype=np.float32) + 0.5 - cx) / f
    z0 = 2.0
    zs = z0 * (zmax / z0) ** (np.arange(steps) / (steps - 1))
    ymin = np.full(W, H, np.float32)
    YM = np.empty((steps, W), np.float32); YS = np.empty((steps, W), np.float32)
    for i, z in enumerate(zs):
        x = cols * z
        h = height(x, np.full_like(x, z))
        ys = hy - f * (h - cam_y) / z
        YS[i] = ys
        ymin = np.minimum(ymin, ys)
        YM[i] = ymin
    # per pixel: first step where ymin <= row
    rows = np.arange(H, dtype=np.float32) + 0.5
    Z = np.full((H, W), np.inf, np.float32)
    for c in range(W):
        arr = -YM[:, c]
        idx = np.searchsorted(arr, -rows, side='left')
        hit = idx < steps
        ii = np.clip(idx, 1, steps - 1)
        y_prev, y_cur = YS[ii - 1, c], YS[ii, c]
        t = np.clip((y_prev - rows) / np.maximum(y_prev - y_cur, 1e-3), 0, 1)
        ok = (y_prev > rows) & (rows >= y_cur)
        zc = np.where(ok, zs[ii - 1] + (zs[ii] - zs[ii - 1]) * t, zs[ii])
        Z[:, c] = np.where(hit, zc, np.inf)
    ground = np.isfinite(Z)
    Xc = (np.arange(W, dtype=np.float32)[None, :] + 0.5 - cx) / f
    Yr = (hy - (np.arange(H, dtype=np.float32)[:, None] + 0.5)) / f
    img = np.zeros((H, W, 3), np.float32)
    # sky for everything first
    img[:] = sky_fn(Xc, Yr)
    gi = np.nonzero(ground)
    z = Z[gi]; x = Xc[0, gi[1]] * z
    y = height(x, z)
    eps = np.maximum(0.06, z / f * 1.5)
    hx = (height(x + eps, z) - height(x - eps, z)) / (2 * eps)
    hz = (height(x, z + eps) - height(x, z - eps)) / (2 * eps)
    fp = z / f
    e2 = 0.02
    rx = (ripple(x + e2, z, fp) - ripple(x - e2, z, fp)) / (2 * e2)
    rz = (ripple(x, z + e2, fp) - ripple(x, z - e2, fp)) / (2 * e2)
    steep = np.clip(np.sqrt(hx * hx + hz * hz) / 0.45, 0, 1)
    rx *= (1 - steep); rz *= (1 - steep)
    n = np.stack([-(hx + rx), np.ones_like(hx), -(hz + rz)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    S = np.array(sun['dir'], np.float32); S /= np.linalg.norm(S)
    ndl = np.clip(n @ S, 0, None)
    # soft shadow ray-march toward the sun
    sh = np.ones_like(z)
    if sun.get('shadows', True):
        t = 0.3
        for k in range(48):
            px = x + S[0] * t; py = y + S[1] * t + 0.05; pz = z + S[2] * t
            hh = height(px, pz)
            d = py - hh
            sh = np.minimum(sh, np.clip(10.0 * d / t + 0.5, 0, 1))
            t *= 1.16
            t += 0.25
    alb = sun['albedo'] * (1 + 0.06 * tex(NT, x / 400, z / 400) + 0.03 * tex(NT, x / 60, z / 60))[:, None]
    sky_amb = sun['amb'] * (0.55 + 0.45 * n[:, 1:2]) 
    back = sun.get('back', None)
    col = alb * (sun['col'] * (ndl * sh)[:, None] + sky_amb)
    if back is not None:
        B = np.array(back[0], np.float32); B /= np.linalg.norm(B)
        col += alb * back[1] * np.clip(n @ B, 0, None)[:, None]
    # aerial perspective
    fog = 1 - np.exp(-z / sun['fogd'])
    fogc = sky_fn(Xc[0, gi[1]], np.zeros_like(z) + 0.004)
    col = col * (1 - fog[:, None]) + fogc * fog[:, None]
    img[gi] = col
    # downsample
    from PIL import Image as _I
    out = np.stack([np.asarray(_I.fromarray(img[..., c]).resize((W0, H0), _I.BOX)) for c in range(3)], -1)
    return out

def tonemap(x, expo=1.0):
    x = x * expo
    return x / (1 + x * 0.6)

def make(fmt, out, quick=False):
    RIP['amp'] = 0.0065 if fmt == 'inner' else 0.005
    if fmt == 'inner':
        size = INNER; W, H = size
        f = 2096.0; hy = 0.535 * H
        sun_px = 330
        az = np.arctan((sun_px - W / 2) / f); el = np.deg2rad(2.6)
    else:
        size = OUTER; W, H = size
        f = 1688.0; hy = 0.53 * H
        sun_px = 360
        az = np.arctan((sun_px - W / 2) / f); el = np.deg2rad(-6.0)
    Sdir = np.array([np.sin(az) * np.cos(el), np.sin(el), np.cos(az) * np.cos(el)], np.float32)
    def sky_fn(xc, yr):
        xc = np.asarray(xc, np.float32); yr = np.asarray(yr, np.float32)
        xc, yr = np.broadcast_arrays(xc, yr)
        nrm = np.sqrt(xc * xc + yr * yr + 1)
        d = np.stack([xc / nrm, yr / nrm, 1 / nrm], -1)
        el_v = np.arcsin(d[..., 1]); az_v = np.arctan2(d[..., 0], d[..., 2])
        ang = np.arccos(np.clip(d @ Sdir, -1, 1))
        e = np.maximum(el_v, 0)
        daz = az_v - az
        if fmt == 'inner':
            stops = [(0.0, '#A8673F'), (0.04, '#7A4A3A'), (0.12, '#48313A'), (0.30, '#291F27'), (0.9, '#15121A')]
        else:
            stops = [(0.0, '#3A241C'), (0.05, '#24191A'), (0.15, '#151115'), (0.4, '#0D0B0E'), (0.9, '#09080A')]
        ts = np.array([s[0] for s in stops]); cs = np.stack([hexl(s[1]) for s in stops])
        base = np.stack([np.interp(e, ts, cs[:, c]) for c in range(3)], -1)
        if fmt == 'inner':
            glow = 3.0 * np.exp(-ang / 0.035) + 0.75 * np.exp(-ang / 0.15) + 0.16 * np.exp(-ang / 0.5)
            band = 0.5 * np.exp(-e / 0.035) * np.exp(-(daz / 0.9) ** 2)
            disk = smoothstep(0.0115, 0.0095, ang) * 40.0
            return base + hexl('#FFB06A') * (glow + band + disk)[..., None]
        band = np.exp(-e / 0.05) * np.exp(-(daz / 0.55) ** 2)
        return base + hexl('#B8652F') * (0.55 * band)[..., None] + hexl('#6B3A26') * (0.30 * np.exp(-e / 0.02))[..., None]
    if fmt == 'inner':
        sun = dict(dir=Sdir, col=hexl('#FFB070') * 3.4, amb=hexl('#3A2A2E') * 0.50, albedo=hexl('#C8935E'), fogd=4800.0)
        cam_y = 17.0
    else:
        L2 = np.array([np.sin(az), 0.10, np.cos(az)], np.float32)
        sun = dict(dir=L2, col=hexl('#8A4A2C') * 0.62, amb=hexl('#221B21') * 0.85, albedo=hexl('#B98A5E'), fogd=4200.0, shadows=False)
        cam_y = 17.0
    if quick:
        size_q = (W // 3, H // 3)
        img = render(size_q, f / 3, hy / 3, cam_y, sun, sky_fn, fmt, ss=1.0, steps=900)
    else:
        img = render(size, f, hy, cam_y, sun, sky_fn, fmt, ss=1.5, steps=2400)
    img = tonemap(img, 1.0)
    if fmt == 'outer' and not quick:
        # morning star
        vx, vy = 380, 640
        img += gauss_splats(size, [vx], [vy], [2.0], [1.6])[..., None] * hexl('#FFF2DE')
        img += gauss_splats(size, [vx], [vy], [0.06], [14])[..., None] * hexl('#FFE2BE')
        rng = np.random.default_rng(4)
        n = 70
        xs = rng.uniform(0, W, n); ys = rng.uniform(0, H * 0.38, n) ** 1.0
        img += gauss_splats(size, xs, ys, 0.02 + 0.2 * rng.uniform(0, 1, n) ** 4, 0.6 + 0.5 * rng.uniform(0, 1, n))[..., None] * hexl('#FFF1DF')
    if fmt == 'inner' and not quick:
        b = np.zeros_like(img)
        hot = np.clip(img - 1.2, 0, None)
        img += bloom_hot(hot)
    u8 = finish(img, grain=0.010, seed=61 if fmt == 'outer' else 62)
    if quick:
        Image.fromarray(u8).save(out)
    else:
        save(u8, out); preview(u8, out.replace('.jpg', '_prev.png'), 700 if fmt == 'outer' else 1100)

def bloom_hot(hot):
    out = np.zeros_like(hot)
    for s, k in ((4, 0.25), (16, 0.18), (60, 0.12), (200, 0.08)):
        out += gblur(hot, s) * k
    return out

from PIL import Image
if __name__ == '__main__':
    import os; os.makedirs('out', exist_ok=True)
    quick = 'quick' in sys.argv
    t0 = time.time()
    for fmt in ('inner', 'outer'):
        if fmt in sys.argv or not any(a in sys.argv for a in ('inner', 'outer')):
            make(fmt, f'out/sakyu_{fmt}' + ('_q.png' if quick else '.jpg'), quick)
            print(fmt, round(time.time() - t0, 1), 's')
