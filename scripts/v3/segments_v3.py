# v3: cinematic segments from stabilized, tonemapped 1296x2304 sources
import subprocess, sys
S = sys.argv[1]
W, H, PW = 1080, 1920, 1296
LOOK = ("curves=r='0/0.025 0.5/0.515 1/0.98':g='0/0.032 0.5/0.512 1/0.965':b='0/0.045 0.5/0.47 1/0.9',"
        "eq=saturation=0.95:contrast=1.06")
HAL = "curves=all='0/0 0.72/0 1/1',gblur=sigma=28,colorchannelmixer=rr=1:gg=0.6:bb=0.35"
# key: (src, start, slow, dur, z0, z1, drift, extra, freeze)
SEG = {
 "1": ("9100", 2.2, 1.25, 2.6, 1.10, 1.02, 0.0, "", 0),      # barista raises cup (pull back)
 "2": ("9099", 0.0, 1.0, 2.1, 1.00, 1.09, 0.25, "", 0),      # menu push + drift
 "3": ("9101", 0.0, 1.0, 3.3, 1.02, 1.08, 0.0, "", 0),       # wind chime, breath
 "4": ("9102", 0.0, 1.25, 4.4, 1.00, 1.12, -0.2, "", 0),     # soup slow push
 "5": ("9100", 4.2, 1.25, 2.2, 1.04, 1.12, 0.0, "", 3.0),    # cup placed, hold
}
def run(k):
    c, ss, slow, D, z0, z1, dx, extra, fr = SEG[k]
    T = D + fr
    p = f"min(t/{T},1)"; e = f"(3*pow({p},2)-2*pow({p},3))"
    Z = f"({z0}+({z1}-{z0})*{e})"
    x = f"(iw-{W})*(0.5+{dx}*({e}-0.5))"
    pre = [f"setpts={slow}*PTS", "fps=24", f"trim=duration={D}", "setpts=PTS-STARTPTS"]
    if fr: pre.append(f"tpad=stop_mode=clone:stop_duration={fr}")
    pre += [f"scale=w='trunc(min({W}*{Z},{PW})/2)*2':h=-2:eval=frame:flags=lanczos",
            f"crop={W}:{H}:x='{x}':y='(ih-{H})/2'", LOOK]
    fc = (f"[0:v]{','.join(pre)},split[a][b];[b]{HAL}[h];"
          f"[a][h]blend=all_mode=screen:all_opacity=0.18,vignette=angle=PI/5.5,"
          f"noise=c0s=5:c0f=t,format=yuv420p,setsar=1[v]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(D / slow + 0.1), "-i", f"{S}/stab_{c}.mp4",
           "-filter_complex", fc, "-map", "[v]", "-t", str(T), "-c:v", "libx264", "-crf", "14", "-preset", "fast",
           f"{S}/seg_{k}.mp4"]
    return subprocess.Popen(cmd)
only = sys.argv[2:] or list(SEG)
print(dict(zip(only, [p.wait() for p in [run(k) for k in only]])))
