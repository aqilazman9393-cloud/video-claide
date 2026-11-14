#!/usr/bin/env bash
# Gred warna v4 (kafe barista). Guna: grade_v4.sh <input> <output> [A|B|C]
# A = Warm Cafe (default), B = Soft Matte, C = Golden Hour
set -euo pipefail
IN="$1"; OUT="$2"; LOOK="${3:-A}"
case "$LOOK" in
  A) BASE="curves=master='0/0.045 0.25/0.24 0.75/0.77 1/0.955':red='0/0.01 0.5/0.51 1/0.99':blue='0/0.05 0.5/0.49 1/0.94',colorbalance=rs=-0.03:bs=0.04:gm=0.005:rh=0.05:gh=0.01:bh=-0.04:pl=1"; EQ="eq=saturation=0.9:contrast=1.03"; HAL=0.22 ;;
  B) BASE="curves=master='0/0.07 0.3/0.3 0.75/0.75 1/0.93':blue='0/0.07 1/0.94',colorbalance=rs=-0.05:gs=0.01:bs=0.06:gm=0.03:rh=0.03:bh=-0.03:pl=1"; EQ="eq=saturation=0.8:contrast=0.98"; HAL=0.15 ;;
  C) BASE="curves=master='0/0.04 0.5/0.52 1/0.96':red='0/0.02 0.5/0.53 1/1':blue='0/0.03 0.5/0.45 1/0.88',colorbalance=rs=-0.01:bs=0.02:gm=0.03:rm=0.03:bm=-0.04:rh=0.07:gh=0.03:bh=-0.08"; EQ="eq=saturation=0.95:contrast=1.04"; HAL=0.28 ;;
esac
# halation: highlight dikaburkan dan diwarnakan jingga, dicampur 'screen'
FC="[0:v]${EQ},format=gbrp,${BASE},split[m][h];\
[h]curves=master='0/0 0.72/0 1/1',gblur=sigma=26,colorchannelmixer=rr=1:gg=0.55:bb=0.25[hb];\
[m][hb]blend=all_mode=screen:all_opacity=${HAL},vignette=angle=PI/7:mode=forward,noise=alls=5:allf=t+u,format=yuv420p[v]"
ffmpeg -v error -y -i "$IN" -filter_complex "$FC" -map "[v]" -map 0:a? -c:v libx264 -crf 14 -preset medium -c:a copy "$OUT"
