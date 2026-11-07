"""An original 132 BPM beat for OPPA family style: kick, clap, hats and a square-wave riff in A minor."""
import math, random, struct, sys, wave
RATE, BPM, BARS = 44100, 132, 8
STEP = 60 / BPM / 4
RIFF = [57, 0, 57, 60, 0, 57, 55, 0, 57, 0, 57, 60, 62, 60, 57, 0]
out = [0.0] * int(RATE * STEP * 16 * BARS + RATE)
def add(start, samples):
    i0 = int(start * RATE)
    for i, v in enumerate(samples):
        if i0 + i < len(out): out[i0 + i] += v
hz = lambda n: 440 * 2 ** ((n - 69) / 12)
def kick():
    n = int(.2 * RATE); ph = 0
    for i in range(n):
        t = i / RATE; f = 40 + 110 * math.exp(-t * 25); ph += 2 * math.pi * f / RATE
        yield .9 * math.sin(ph) * math.exp(-t * 18)
def noise(length, vol, bright):
    prev = 0
    for i in range(int(length * RATE)):
        x = random.uniform(-1, 1); hp = x - prev * bright; prev = x
        yield vol * hp * math.exp(-i / RATE * (6 / length))
def square(f, length, vol):
    for i in range(int(length * RATE)):
        t = i / RATE
        yield vol * (1 if math.sin(2 * math.pi * f * t) >= 0 else -1) * math.exp(-t * 14)
def bass(f, length, vol):
    for i in range(int(length * RATE)):
        t = i / RATE
        yield vol * ((2 * (f * t % 1)) - 1) * min(1, t * 50) * math.exp(-t * 1.5)
random.seed(7)
for bar in range(BARS):
    up = 12 if bar >= 4 else 0
    for s in range(16):
        at = (bar * 16 + s) * STEP
        if s % 4 == 0: add(at, kick())
        if s % 8 == 4: add(at, noise(.15, .45, .3))
        if s % 2 == 1: add(at, noise(.04, .12, .95))
        if RIFF[s]: add(at, square(hz(RIFF[s] + up), .16, .07))
        if s in (0, 8): add(at, bass(hz(45 if s == 0 else 43), STEP * 8, .12))
peak = max(abs(v) for v in out)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
    w.writeframes(b"".join(struct.pack("<h", int(v / peak * 0.85 * 32767)) for v in out))
