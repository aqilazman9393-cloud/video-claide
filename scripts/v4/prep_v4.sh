#!/usr/bin/env bash
# Sediakan footage v4: buang bar kabur sisi, 24fps, stabil (vidstab smoothing 40), gred warna A, GOP 1s.
# Guna: prep_v4.sh <video_asal.mov> <folder_kerja>
set -euo pipefail
IN="$1"; W="$2"; mkdir -p "$W"; HERE="$(cd "$(dirname "$0")" && pwd)"
ffmpeg -v error -y -i "$IN" -vf "crop=960:1920:60:0,fps=24,vidstabdetect=shakiness=6:accuracy=15:result=$W/tr.trf" -f null -
ffmpeg -v error -y -i "$IN" -vf "crop=960:1920:60:0,fps=24,vidstabtransform=input=$W/tr.trf:smoothing=40:zoom=4:optzoom=0:interpol=bicubic,scale=1080:2160:flags=lanczos,crop=1080:1920:0:110,setsar=1" \
  -c:v libx264 -crf 12 -preset medium -pix_fmt yuv420p -c:a copy "$W/stab.mp4"
"$HERE/grade_v4.sh" "$W/stab.mp4" "$W/graded.mp4" A
ffmpeg -v error -y -i "$W/graded.mp4" -c:v libx264 -crf 15 -g 24 -keyint_min 24 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart "$W/tumbler_graded.mp4"
ffmpeg -v error -y -sseof -0.1 -i "$W/tumbler_graded.mp4" -frames:v 1 -vf "gblur=sigma=28,eq=brightness=-0.12:saturation=0.85" -q:v 3 "$W/end_blur.jpg"
echo "Salin $W/tumbler_graded.mp4 dan $W/end_blur.jpg ke v4-tumbler/assets/"
