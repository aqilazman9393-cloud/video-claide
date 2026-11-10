# Kopi Saigon Pasir Puteh: video sinematik

Hasil: `output/kopi_saigon_pasir_puteh.mp4`, menegak 1080x1920, 24fps, ~19 saat. Sesuai untuk Reels, TikTok dan Shorts.

## Struktur
1. Loceng angin + tajuk "KOPI SAIGON / Pasir Puteh"
2. Menu Aglio Olio: *"Rasa yang dirindui"*
3. Barista dengan minuman (slow-mo): *"Dibancuh penuh kasih"*
4. Sup dan roti bakar (slow-mo): *"Hangat. Ringkas. Sempurna."*
5. Kad penutup: *Pasir Puteh · Kelantan, "Singgah. Rasa. Kenang."*

## Proses
- HDR iPhone (HLG) ditukar ke SDR dengan tonemap Hable
- Gred warna filem: highlight hangat, shadow sejuk, vignette dan film grain
- Klip 30fps diperlahankan ke 24fps untuk slow-mo sebenar, dengan zoom perlahan
- Muzik lo-fi asli dijana dengan `scripts/music.py` (bebas hak cipta), dicampur dengan bunyi loceng angin asal

---

# Versi 2: hook, teks kinetik, potong ikut beat

Hasil: `output/kopi_saigon_v2.mp4`, 1080x1920, 24fps, 16 saat.

| Masa | Babak | Teks |
|---|---|---|
| 0–2s | Hook: sup, zoom punch ikut beat | MUNG / DOH RASA / KO BELUM? |
| 2–4s | Menu (drop pertama) | MENU WAJIB CUBA, AGLIO OLIO, DARI RM12 JE! |
| 4–6s | Loceng angin (breakdown tenang) | *tenang... port lepak paling chill* |
| 6–10.5s | Barista slow-mo, freeze frame hitam putih | DIBANCUH FRESH, NI DIO! |
| 10.5–12.5s | Sup + roti bakar | SUP PANAS + ROTI BAKAR, sedak gile! |
| 12.5–16s | Penutup | KOPI SAIGON, PASIR PUTEH • KELANTAN, JOM SINGGAH! |

Font (Google Fonts, lesen OFL/Apache, dalam `fonts/`): Anton, Bebas Neue, Playfair Display Italic, Permanent Marker.

Bina semula (`S` ialah folder kerja yang mengandungi `fonts/`):
```
python3 scripts/v2/music_v2.py $S/music_v2.wav
python3 scripts/v2/segments_v2.py <folder_video_asal> $S
python3 scripts/v2/compose_v2.py <folder_video_asal> $S $S/kopi_saigon_v2.mp4
```

---

# Versi 3: sinematik premium (disyorkan)

- `output/kopi_saigon_v3.mp4`: dengan skor piano dan bunyi suasana kafe
- `output/kopi_saigon_v3_tanpa_muzik.mp4`: bunyi suasana sahaja, untuk tambah lagu sendiri di TikTok/IG/CapCut

Footage distabilkan, pergerakan kamera licin dengan easing, gred filem dengan halation, transisi dissolve dan light leak, dua font (Playfair Display Italic dan Inter Light). Skrip dalam `scripts/v3/`.
