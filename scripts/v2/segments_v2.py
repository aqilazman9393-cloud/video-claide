import subprocess, sys, glob, os
U, S = sys.argv[1], sys.argv[2]
src = lambda n: glob.glob(f"{U}/*{n}.mov")[0]
P = 1.4  # prescale so zoom stays sharp
TM = (f"zscale=w={int(1080*P)}:h={int(1920*P)}:filter=lanczos,zscale=t=linear:npl=160,format=gbrpf32le,"
      "zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
GRADE = ("eq=contrast=1.08:saturation=1.08,colorbalance=rs=-0.04:bs=0.05:rh=0.05:bh=-0.04,"
         "curves=master='0/0.03 0.3/0.27 0.7/0.74 1/0.97',vignette=PI/5,noise=alls=7:allf=t")
# name: (clip, start, slow, dur, zoom expr Z(t), shake amp, extra)
SEG = {
 "A": ("9102", 0.0, 1.25, 2.0, "1.20-0.03*t+0.14*exp(-t*9)+0.05*exp(-mod(t,0.5)*12)", 14, "eq=brightness=-0.06"),
 "B": ("9099", 0.0, 1.0, 2.0, "1.04+0.05*t+0.16*exp(-t*9)+0.06*exp(-(t-1)*12)*gte(t,1)", 16, ""),
 "C": ("9101", 0.3, 1.0, 2.0, "1.0+0.04*t", 0, "eq=brightness=-0.13:saturation=0.85"),
 "D": ("9100", 2.4, 1.25, 3.5, "1.06+0.025*t+0.14*exp(-t*9)+0.16*exp(-(t-3.5)*8)*gte(t,3.5)", 14, "hue=s=0.35:enable='gte(t,3.5)'", 1.0),
 "E": ("9102", 1.2, 1.25, 2.0, "1.0+0.04*t+0.12*exp(-t*9)", 12, ""),
 "F": ("9102", 0.5, 1.25, 3.5, "1.12", 0, "gblur=sigma=22,eq=brightness=-0.16:saturation=0.8"),
}
def run(k):
    c, ss, slow, dur, Z, sh, extra, *fr = SEG[k]
    freeze = fr[0] if fr else 0
    total = dur + freeze
    src_len = dur / slow + 0.05
    chain = [TM, f"setpts={slow}*PTS", "fps=24", f"trim=duration={dur}", "setpts=PTS-STARTPTS"]
    if freeze: chain.append(f"tpad=stop_mode=clone:stop_duration={freeze}")
    zw = f"trunc(1080*({Z})/2)*2"
    chain.append(f"scale=w='min({zw},{int(1080*P)})':h=-2:eval=frame:flags=bicubic")
    sx = f"(iw-1080)/2+{sh}*sin(t*83)*exp(-t*9)" + (f"+{sh}*sin(t*97)*exp(-(t-3.5)*9)*gte(t,3.5)" if freeze else "")
    sy = f"(ih-1920)/2+{sh}*cos(t*71)*exp(-t*9)"
    chain.append(f"crop=1080:1920:x='{sx}':y='{sy}'")
    if extra: chain.append(extra)
    chain += [GRADE, "format=yuv420p", "setsar=1"]
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(src_len), "-i", src(c), "-an",
           "-vf", ",".join(chain), "-t", str(total), "-c:v", "libx264", "-crf", "15", "-preset", "fast",
           f"{S}/v2_{k}.mp4"]
    return subprocess.Popen(cmd)
ONLY=sys.argv[3:] or list(SEG)
procs = [run(k) for k in ONLY]
codes = [p.wait() for p in procs]
print(dict(zip(ONLY, codes)))
