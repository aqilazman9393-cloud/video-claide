# v3 score: soft felt piano + string pad, chord changes land on picture cuts
import numpy as np, wave, sys
sr = 48000; T = float(sys.argv[2]); n = int(sr * T); t = np.arange(n) / sr
rng = np.random.default_rng(3)
L = np.zeros(n); R = np.zeros(n)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def put(sig, st, g, pan):
    s = int(st * sr); e = min(n, s + len(sig))
    if e <= s: return
    L[s:e] += sig[:e - s] * g * np.sqrt(1 - pan); R[s:e] += sig[:e - s] * g * np.sqrt(pan)
def lp1(x, fc):
    a = 1 - np.exp(-2 * np.pi * fc / sr); y = np.empty_like(x); z = 0.0
    for i in range(len(x)): z += a * (x[i] - z); y[i] = z
    return y
def piano(m, vel=0.7, dur=5.0):
    f = mtof(m); m_ = int(dur * sr); tt = np.arange(m_) / sr; y = np.zeros(m_)
    B = 0.00025; bright = 0.6 + 0.6 * vel
    for k in range(1, 13):
        fk = k * f * np.sqrt(1 + B * k * k)
        if fk > 9000: break
        amp = (1 / k ** 1.15) * np.exp(-(k - 1) * (0.32 / bright))
        d = (0.5 + 0.28 * k) * (f / 260) ** 0.35
        env = 0.65 * np.exp(-d * 1.8 * tt) + 0.35 * np.exp(-d * 0.35 * tt)
        for det in (-0.7, 0.7):
            y += amp * env * np.sin(2 * np.pi * fk * (1 + det / 1200) * tt + rng.uniform(0, 6.28)) * 0.5
    hammer = lp1(rng.normal(0, 1, int(0.012 * sr)), 1800) * np.exp(-np.arange(int(0.012 * sr)) / sr * 300) * 0.25
    y[:len(hammer)] += hammer
    y *= np.minimum(1, tt / 0.004)
    rel = max(0.0, dur - 0.8); y *= np.where(tt < rel, 1, np.exp(-(tt - rel) * 6))
    return y * vel
def pad(ms, dur, g=1.0):
    m_ = int(dur * sr); tt = np.arange(m_) / sr; y = np.zeros(m_)
    for m in ms:
        for det in (-5, 0, 5):
            ph = rng.uniform(0, 1); f = mtof(m) * (1 + det / 1200)
            saw = 2 * ((f * tt + ph) % 1) - 1
            y += saw
    y = lp1(lp1(y, 900), 1400)
    env = np.minimum(1, tt / 1.2) * np.minimum(1, np.clip(dur - tt, 0, None) / 1.0)
    return y * env * 0.012 * g
cuts = [float(c) for c in sys.argv[3].split(",")]  # times of picture cuts
c1, c2, c3, c4, c_end = cuts
# chords (D major): Dmaj9 | Bm9 | Gmaj7 | Em9->A | D(add9)
sec = [
 (0.0, c1, 38, [57, 66, 69, 76], [74, 76, 78]),
 (c1, c2, 35, [54, 62, 69, 73], [73, 74]),
 (c2, c3, 31, [55, 62, 66, 71], [71, 69, 66]),
 (c3, c4, 40, [55, 62, 67, 71], [74, 73, 71, 69]),
 (c4, T, 38, [57, 62, 66, 69, 76], [78, 76]),
]
for i, (a, b, bass, ch, mel) in enumerate(sec):
    span = b - a
    put(piano(bass, 0.55, min(6, span + 2.5)), a, 1.0, 0.45)
    put(piano(bass + 12, 0.35, min(6, span + 2.5)), a + 0.02, 1.0, 0.45)
    step = span / (len(ch) + len(mel) + 1)
    for j, m in enumerate(ch):
        put(piano(m, 0.38 + 0.04 * j, 4.5), a + 0.15 + j * min(step, 0.42), 1.0, 0.3 + 0.1 * j)
    for j, m in enumerate(mel):
        st = a + 0.15 + len(ch) * min(step, 0.42) + j * max(step, 0.55)
        if st < b - 0.3 or i == len(sec) - 1:
            put(piano(m, 0.5, 4.5), st, 1.0, 0.62)
    put(pad([bass + 12, bass + 19, bass + 24], span + 1.2, 1.0), max(0, a - 0.3), 1.0, 0.5)
# title moment: high D + A rings out under end title
put(piano(86,0.42,3.5),c_end,1.0,0.6); put(piano(81,0.3,3.5),c_end+0.35,1.0,0.4)
# big reverb (stereo decorrelated)
ir_n = int(3.2 * sr); it = np.arange(ir_n) / sr
def rev(x, seed):
    ir = np.random.default_rng(seed).normal(0, 1, ir_n) * np.exp(-it * 2.0)
    ir[:int(0.02 * sr)] = 0; ir = lp1(ir, 5000)
    N = 1 << int(np.ceil(np.log2(n + ir_n)))
    y = np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:n]
    return y / (np.abs(y).max() + 1e-9)
dryL, dryR = L.copy(), R.copy(); pk = max(abs(dryL).max(), abs(dryR).max())
L = dryL + 0.55 * pk * rev(dryL, 1); R = dryR + 0.55 * pk * rev(dryR, 2)
fade = np.minimum(1, t / 0.3) * np.minimum(1, (T - t) / 1.2)
L *= fade; R *= fade
pk = max(abs(L).max(), abs(R).max()); L *= 0.8 / pk; R *= 0.8 / pk
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(out.tobytes()); w.close()
