"""Jana compositions/captions.html daripada senarai kumpulan sari kata.
Masa diambil daripada transkripsi whisper 'medium' (masa perkataan),
teks dibetulkan dengan whisper 'large-v3' dan semakan manual.
Perkataan dengan kw=blue/pink mendapat garis bawah berwarna."""
import sys, html

# (mula, tamat, [(perkataan, masa_mula, kw)])
G = [
 (0.20, 2.15, [("Kita",0.20,None),("ada",0.40,None),("dua",0.78,None),("warna",1.10,None)]),
 (2.20, 4.05, [("Ni",2.20,None),("blue,",2.60,"blue"),("ni",3.10,None),("pink.",3.50,"pink")]),
 (4.10, 6.35, [("Boleh",4.10,None),("dah,",4.40,None),("sebab",4.60,None),("ni",5.00,None),("tumbler",5.20,None),("baru",5.60,None)]),
 (6.40, 7.75, [("Dia",6.40,None),("ada",6.60,None),("macam",6.80,None),("strap",7.20,None)]),
 (7.80, 9.85, [("Macam",7.80,None),("ni",8.40,None),("kita",8.70,None),("pakai",9.20,None)]),
 (10.20, 13.25, [("Kalau",11.20,None),("kita",11.40,None),("pergi",11.70,None),("ke",12.00,None),("mana-mana",12.10,None)]),
 (13.30, 14.50, [("Tumbler",13.30,None),("jual",13.90,None),("ke?",14.20,None)]),
 (14.55, 15.25, [("Ha,",14.55,None),("jual.",14.80,None)]),
 (15.30, 17.25, [("Kita",15.80,None),("ada",16.10,None),("dua",16.30,None),("warna",16.60,None)]),
 (17.30, 20.85, [("Satu",19.00,None),("blue,",19.40,"blue"),("satu",20.00,None),("pink.",20.30,"pink")]),
]
# kumpulan 6 mula pada 11.2 (perkataan pertama) supaya tiada sari kata kosong lama
G[5] = (11.15, 13.25, G[5][2])
# kumpulan 10: tunjuk dari 17.3 dengan perkataan pertama muncul bertingkat
G[9] = (17.30, 20.85, [("Satu",17.40,None),("blue,",17.70,"blue"),("satu",19.40,None),("pink.",19.80,"pink")])

out = []
out.append("""<template>
  <style>
    #root { position: absolute; inset: 0; pointer-events: none; }
    #cap-scrim { position: absolute; left: 0; bottom: 0; width: 1080px; height: 760px;
      background: linear-gradient(180deg, rgba(14, 9, 5, 0) 0%, rgba(14, 9, 5, 0.38) 45%, rgba(14, 9, 5, 0.62) 100%); }
    .cap { position: absolute; left: 96px; width: 888px; bottom: 380px; overflow: visible;
      font-family: var(--serif); font-style: italic; font-size: 72px; line-height: 1.12; color: var(--cream);
      text-shadow: var(--shadow); opacity: 0; }
    .cap .w { display: inline-block; position: relative; margin-right: 0.24em; opacity: 0; }
    .cap .ul { position: absolute; left: 2px; right: 6px; bottom: -4px; height: 5px; border-radius: 3px; transform-origin: 0 50%; transform: scaleX(0); }
    .cap .ul.blue { background: var(--blue); }
    .cap .ul.pink { background: var(--pink); }
    #cap-tick { position: absolute; left: 96px; bottom: 300px; font-family: var(--sans); font-weight: 300; font-size: 32px;
      letter-spacing: 0.32em; text-transform: uppercase; color: var(--cream); opacity: 0.0; }
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
    <div id="cap-scrim" class="clip" data-start="0" data-duration="20.9"></div>
""")
for gi,(s,e,ws) in enumerate(G):
    spans=[]
    for wi,(t,_,kw) in enumerate(ws):
        ul = f'<span class="ul {kw}"></span>' if kw else ""
        spans.append(f'<span class="w" id="c{gi}w{wi}">{html.escape(t)}{ul}</span>')
    out.append(f'    <div id="cap{gi}" class="cap clip" data-start="{s:.2f}" data-duration="{e-s:.2f}">{"".join(spans)}</div>\n')
out.append("""  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#cap-scrim", { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.out" }, 0);
    tl.to("#cap-scrim", { opacity: 0, duration: 0.5, ease: "power2.in" }, 20.3);
    const G = %s;
    G.forEach(([s, e, ws], gi) => {
      const g = "#cap" + gi;
      tl.fromTo(g, { opacity: 1 }, { opacity: 1, duration: 0.01 }, s);
      ws.forEach(([t, at, kw], wi) => {
        // fade + naik 28px, ease-out (gaya v3)
        tl.fromTo(`#c${gi}w${wi}`, { opacity: 0, y: 28 }, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }, Math.max(s, at - 0.08));
        if (kw) tl.fromTo(`#c${gi}w${wi} .ul`, { scaleX: 0 }, { scaleX: 1, duration: 0.55, ease: "power3.out" }, Math.max(s, at) + 0.2);
      });
      tl.to(g, { opacity: 0, duration: 0.14, ease: "power2.in" }, e - 0.14);
      tl.set(g, { opacity: 0, visibility: "hidden" }, e);
    });
    window.__timelines["captions"] = tl;
  </script>
</template>
""" % __import__("json").dumps([[s,e,[[t,a,k] for t,a,k in ws]] for s,e,ws in G]))
open(sys.argv[1],"w").write("".join(out))
print("ok", len(G), "kumpulan")
