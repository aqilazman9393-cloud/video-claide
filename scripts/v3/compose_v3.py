import subprocess, sys, glob
U, S, OUT, MODE = sys.argv[1:5]   # MODE: score | ambience
PLAY, INTER = f"{S}/PlayfairDisplay-Italic.ttf", f"{S}/Inter-Light.otf"
CREAM = "0xF4EADB"
segs = [f"{S}/seg_{k}.mp4" for k in "12345"]
D = [2.583, 2.083, 3.292, 4.417, 5.208]; X = 0.5
offs, L = [], D[0]
for d in D[1:]:
    offs.append(round(L - X, 3)); L = L + d - X
TOTAL = round(L, 3)
def sp(s): return "   ".join(" ".join(w) for w in s.split(" "))
def tx(text, font, size, y, t0, t1, x="96"):
    e = f"(1-pow(1-clip((t-{t0})/0.9,0,1),3))"
    a = f"clip((t-{t0})/0.7,0,1)*clip(({t1}-t)/0.5,0,1)"
    if x == "c": x = "(w-tw)/2"
    return (f"drawtext=fontfile={font}:text='{text}':fontsize={size}:fontcolor={CREAM}:x={x}:"
            f"y='{y}+28*(1-{e})':alpha='{a}':enable='between(t,{t0},{t1})':shadowcolor=black@0.45:shadowx=0:shadowy=2")
T = [
 tx("Kopi Saigon", PLAY, 132, 1440, 0.45, 1.95),
 tx(sp("PASIR PUTEH"), INTER, 36, 1610, 0.75, 1.95),
 tx("Aglio Olio", PLAY, 88, 1500, 2.35, 3.6),
 tx(sp("DARI RM12"), INTER, 34, 1612, 2.6, 3.6),
 tx("Lepak dulu.", PLAY, 80, 1540, 4.4, 6.3),
 tx("Sup panas,", PLAY, 88, 1410, 7.0, 10.2),
 tx("roti bakar.", PLAY, 88, 1515, 7.35, 10.2),
 tx(sp("SEDAK, MUNG KENA RASA"), INTER, 32, 1652, 7.9, 10.2),
 tx("Kopi Saigon", PLAY, 150, 1400, 12.75, TOTAL, "c"),
 tx(sp("PASIR PUTEH · KELANTAN"), INTER, 34, 1590, 13.15, TOTAL, "c"),
 tx("Jom singgah.", PLAY, 66, 1670, 13.6, TOTAL, "c"),
]
inp = sum([["-i", s] for s in segs], [])
# 5: bottom gradient, 6: light leak, 7: score, 8: ambience, 9: chime
inp += ["-f", "lavfi", "-i", f"color=c=black:s=1080x1000:r=24:d={TOTAL},format=rgba,geq=r=0:g=0:b=0:a='135*pow(Y/H,1.7)'"]
leakI = "(exp(-pow((T-3.9)/0.32,2))+0.6*exp(-pow((T-0.15)/0.35,2))+0.5*exp(-pow((T-10.4)/0.3,2)))"
cx = "(W*(-0.3+1.6*(T-floor(T))))"
inp += ["-f", "lavfi", "-i", f"color=c=black:s=540x960:r=24:d={TOTAL},format=rgb24,"
        f"geq=r='255*{leakI}*exp(-(pow(X-{cx},2)+pow(Y-H*0.35,2))/(2*pow(W*0.45,2)))':"
        f"g='150*{leakI}*exp(-(pow(X-{cx},2)+pow(Y-H*0.35,2))/(2*pow(W*0.4,2)))':"
        f"b='60*{leakI}*exp(-(pow(X-{cx},2)+pow(Y-H*0.35,2))/(2*pow(W*0.35,2)))',scale=1080:1920"]
inp += ["-i", f"{S}/score.wav", "-i", glob.glob(f"{U}/*9100.mov")[0], "-i", glob.glob(f"{U}/*9101.mov")[0]]
norm = "settb=1/24,fps=24,setsar=1,format=yuv420p"
fc = "".join(f"[{i}:v]{norm}[s{i}];" for i in range(5))
prev = "s0"
for i, o in enumerate(offs):
    fc += f"[{prev}][s{i+1}]xfade=transition=fade:duration={X}:offset={o}[x{i}];"; prev = f"x{i}"
fc += (f"[6:v]{norm},format=gbrp[leak];[{prev}]format=gbrp[bp];[bp][leak]blend=all_mode=screen:shortest=1,format=yuv420p[lk];"
       f"[lk][5:v]overlay=0:H-h:shortest=1,"
       f"eq=brightness='-0.2*clip((t-12.35)/0.9,0,1)':saturation='1-0.35*clip((t-12.35)/0.9,0,1)':eval=frame,"
       f"{','.join(T)},fade=t=in:st=0:d=0.5,fade=t=out:st={TOTAL-0.6}:d=0.6[v];")
amb = (f"[8:a:0]aloop=loop=-1:size=288000,atrim=0:{TOTAL},asetpts=PTS-STARTPTS,highpass=f=120,lowpass=f=7000,"
       f"volume={'0.35' if MODE=='score' else '0.9'}[amb];"
       f"[9:a:0]atrim=0.2:3.4,asetpts=PTS-STARTPTS,volume=3.0,adelay=3800|3800,apad[chime];")
if MODE == "score":
    fc += amb + f"[7:a][amb][chime]amix=inputs=3:duration=first:normalize=0,afade=t=out:st={TOTAL-1.2}:d=1.2,alimiter=limit=0.9[a]"
else:
    fc += amb + f"[amb][chime]amix=inputs=2:duration=first:normalize=0,afade=t=in:d=0.4,afade=t=out:st={TOTAL-1.0}:d=1.0,alimiter=limit=0.9[a]"
cmd = ["ffmpeg", "-v", "error", "-y"] + inp + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(TOTAL),
       "-c:v", "libx264", "-crf", "19", "-maxrate", "14M", "-bufsize", "28M", "-preset", "slow", "-pix_fmt", "yuv420p",
       "-profile:v", "high", "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", OUT]
print("total", TOTAL, "offsets", offs)
sys.exit(subprocess.call(cmd))
