import subprocess, sys, glob
U, S = sys.argv[1], sys.argv[2]
F = f"{S}/fonts"
ANTON, BEBAS, PLAY, MARK = f"{F}/Anton-Regular.ttf", f"{F}/BebasNeue-Regular.ttf", f"{F}/PlayfairDisplay-Italic.ttf", f"{F}/PermanentMarker-Regular.ttf"
CREAM, YEL, INK = "0xF7EBD8", "0xFFC93C", "0x1A1208"
def txt(text, font, size, yc, t0, t1, color=CREAM, anim="punch", box=False, soft=False):
    if anim == "punch":
        fs = f"{size}*(1+0.45*exp(-max(t-{t0},0)*16))"; x = "(w-tw)/2"
    else:
        fs = str(size); d = -1 if anim == "left" else 1
        x = f"(w-tw)/2+{d}*1100*exp(-max(t-{t0},0)*11)"
    fi = 0.5 if soft else 0.06
    a = f"min(1,(t-{t0})/{fi})*min(1,({t1}-t)/0.12)"
    s = (f"drawtext=fontfile={font}:text='{text}':fontsize='{fs}':fontcolor={color}:x='{x}':y='{yc}-th/2'"
         f":alpha='max(0,{a})':enable='between(t,{t0},{t1})'")
    if box: s += f":box=1:boxcolor={YEL}:boxborderw=22"
    else: s += ":shadowcolor=black@0.75:shadowx=0:shadowy=5"
    return s
T = [
 # HOOK 0-2
 txt("MUNG", ANTON, 230, 470, 0.0, 2.0),
 txt("DOH RASA", ANTON, 170, 700, 0.5, 2.0),
 txt("KO BELUM?", ANTON, 190, 900, 1.0, 2.0, YEL),
 txt("KOPI SAIGON  •  PASIR PUTEH", BEBAS, 56, 1660, 1.5, 2.0, INK, box=True),
 # MENU 2-4
 txt("MENU WAJIB CUBA", BEBAS, 72, 1240, 2.0, 4.0, INK, "left", box=True),
 txt("AGLIO OLIO", ANTON, 170, 1390, 2.25, 4.0, CREAM, "right"),
 txt("DARI RM12 JE!", ANTON, 100, 1575, 3.0, 4.0, YEL),
 # CALM 4-6
 txt("tenang...", PLAY, 140, 760, 4.15, 5.95, soft=True, anim="none"),
 txt("port lepak paling chill", PLAY, 66, 910, 4.7, 5.95, soft=True, anim="none"),
 # BARISTA 6-10.5
 txt("DIBANCUH", ANTON, 190, 330, 6.0, 9.45, CREAM, "left"),
 txt("FRESH", ANTON, 280, 540, 6.5, 9.45, YEL, "right"),
 txt("setiap cawan.", PLAY, 80, 770, 7.2, 9.45, soft=True, anim="none"),
 txt("NI DIO!", MARK, 210, 520, 9.5, 10.5, YEL),
 txt("SIGNATURE DRINK KAMI", BEBAS, 70, 1660, 9.75, 10.5, INK, box=True),
 # FOOD 10.5-12.5
 txt("SUP PANAS", ANTON, 180, 330, 10.5, 12.5),
 txt("+ ROTI BAKAR", ANTON, 130, 520, 10.95, 12.5, CREAM, "right"),
 txt("sedak gile!", MARK, 120, 1520, 11.5, 12.5, YEL),
 # END 12.5-16
 txt("KOPI", ANTON, 300, 640, 12.5, 16.0),
 txt("SAIGON", ANTON, 300, 930, 12.75, 16.0, YEL),
 txt("PASIR PUTEH  •  KELANTAN", BEBAS, 72, 1200, 13.25, 16.0, CREAM, "left"),
 txt("JOM SINGGAH!", BEBAS, 86, 1380, 13.75, 16.0, INK, box=True),
]
flash = ",".join(f"drawbox=c=white@0.85:t=fill:enable='between(t,{c},{c+0.08})'" for c in (2.0, 6.0, 9.5, 10.5, 12.5))
seg = "".join(f"[{i}:v]" for i in range(6))
fc = (f"{seg}concat=n=6:v=1:a=0[base];[base][6:v]overlay=0:0:enable='between(t,6,12.5)'[bg];[bg]{flash},{','.join(T)},fade=t=in:st=0:d=0.15,fade=t=out:st=15.4:d=0.6[v];"
      f"[8:a:0]atrim=0.3,asetpts=PTS-STARTPTS,volume=0.8,adelay=4000|4000,afade=t=in:st=4:d=0.2,afade=t=out:st=5.6:d=0.4[amb];"
      f"[7:a][amb]amix=inputs=2:duration=first:normalize=0,afade=t=out:st=15.3:d=0.7[a]")
cmd = ["ffmpeg", "-v", "error", "-y"] + sum([["-i", f"{S}/v2_{k}.mp4"] for k in "ABCDEF"], []) + \
      ["-f", "lavfi", "-i", "color=c=black:s=1080x1000:r=24:d=16,format=rgba,geq=r=0:g=0:b=0:a='200*pow(1-Y/H,1.4)'", "-i", f"{S}/music_v2.wav", "-i", glob.glob(f"{U}/*9101.mov")[0], "-filter_complex", fc,
       "-map", "[v]", "-map", "[a]", "-t", "16", "-c:v", "libx264", "-crf", "20", "-maxrate", "14M", "-bufsize", "28M",
       "-preset", "slow", "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
       "-c:a", "aac", "-b:a", "192k", sys.argv[3]]
sys.exit(subprocess.call(cmd))
