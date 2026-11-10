# Original beat-synced track for Kopi Saigon v2 (120 BPM, cuts land on beats)
import numpy as np, wave, sys
sr=48000; T=16.5; n=int(sr*T); t=np.arange(n)/sr
rng=np.random.default_rng(11)
beat=0.5; L=np.zeros(n); R=np.zeros(n)
def mtof(m): return 440*2**((m-69)/12)
def add(sig,start,gain=1.0,pan=0.5):
    s=int(start*sr); e=min(n,s+len(sig))
    if s>=n or e<=s: return
    g=gain
    L[s:e]+=sig[:e-s]*g*np.sqrt(1-pan); R[s:e]+=sig[:e-s]*g*np.sqrt(pan)
def lp(x,fc):
    fc=np.broadcast_to(fc,x.shape); y=np.zeros_like(x); a=1-np.exp(-2*np.pi*fc/sr); z=0.0
    for i in range(len(x)): z+=a[i]*(x[i]-z); y[i]=z
    return y
def kick():
    tt=np.arange(int(0.45*sr))/sr
    return np.sin(2*np.pi*(48*tt+ (160/25)*(1-np.exp(-tt*25))))*np.exp(-tt*7)
def clap():
    tt=np.arange(int(0.3*sr))/sr; x=rng.normal(0,1,len(tt))
    x=x-lp(x,900); e=np.exp(-tt*18)*(1+0.6*np.exp(-((tt-0.012)%0.011)*400))
    return x*e*0.5
def hat(d=0.06):
    tt=np.arange(int(d*sr))/sr; x=rng.normal(0,1,len(tt)); x=x-lp(x,7000); return x*np.exp(-tt*70)*0.35
def boom():
    tt=np.arange(int(2.0*sr))/sr
    s=np.sin(2*np.pi*(35*tt+(120/6)*(1-np.exp(-tt*6))))*np.exp(-tt*2.2)
    nz=rng.normal(0,1,len(tt)); nz=lp(nz,2500)*np.exp(-tt*4)*0.6
    return (s+nz)
def whoosh(d=0.45):
    m=int(d*sr); tt=np.arange(m)/sr; x=rng.normal(0,1,m)
    fc=300+6000*(tt/d)**2; y=lp(x,fc)-lp(x,fc*0.3)
    return y*np.sin(np.pi*tt/d)**2*1.4
def riser(d):
    m=int(d*sr); tt=np.arange(m)/sr; x=rng.normal(0,1,m)
    y=lp(x,200+8000*(tt/d)**3)*(tt/d)**2
    tone=np.sin(2*np.pi*(200*tt+600*tt**2/d))*(tt/d)**2*0.15
    return y*0.8+tone
def shutter():
    tt=np.arange(int(0.12*sr))/sr; x=rng.normal(0,1,len(tt)); x=x-lp(x,2000)
    e=np.exp(-tt*80)+0.7*np.exp(-np.clip(tt-0.05,0,None)*90)*(tt>0.05)
    return x*e*0.7
def stab(ch,d=0.22):
    tt=np.arange(int(d*sr))/sr; y=np.zeros(len(tt))
    for m in ch:
        f=mtof(m)
        for h in range(1,7): y+=np.sin(2*np.pi*f*h*tt*(1+0.002*h))/h
    y=lp(y,2600)
    return y*np.exp(-tt*9)*0.09
def bassnote(m,d):
    tt=np.arange(int(d*sr))/sr; f=mtof(m)
    y=np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)
    return y*np.minimum(1,tt/0.005)*np.exp(-tt*2.5)*0.45
def pad(ch,d):
    tt=np.arange(int(d*sr))/sr; y=np.zeros(len(tt))
    for m in ch:
        for det in (-0.15,0.15): y+=np.sin(2*np.pi*mtof(m)*(1+det/100)*tt+rng.uniform(0,6))
    return y*np.minimum(1,tt/0.4)*np.minimum(1,(d-tt)/0.4)*0.05
prog=[[57,60,64,67],[53,57,60,64],[48,52,55,60],[55,59,62,67]]
def chord_at(x): return prog[int(x//2)%4]
groove=[(2,4),(6,9.5),(10.5,15.0)]
for a,b in groove:
    x=a
    while x<b-1e-6:
        k=round((x-a)/beat)
        add(kick(),x,0.9)
        if k%2==1: add(clap(),x,0.55,0.45)
        add(hat(),x+0.25,0.5,0.65); add(hat(0.03),x+0.125,0.25,0.35); add(hat(0.03),x+0.375,0.25,0.35)
        ch=chord_at(x); add(stab(ch),x+0.25,1.0,0.4 if k%2 else 0.6)
        if k%2==0: add(bassnote(ch[0]-24,0.9),x,1.0)
        x+=beat
# hook (0-2): filtered heartbeat kick + ticking hats + riser + snare roll
for i in range(4):
    add(lp(kick(),400),i*beat,1.0); add(hat(0.02),i*beat+0.25,0.3,0.6)
add(pad(prog[0],2.0),0,0.8)
add(riser(1.5),0.5,0.5)
for i in range(8): add(clap()*0.5,1.5+i*0.0625,0.25+i*0.05,0.5)
# breakdown 4-6: pads + soft plucks, riser into 6
add(pad(prog[1],1.0),4.0,1.2); add(pad(prog[2],1.0),5.0,1.2)
for i,m in enumerate([72,76,79,76,74,72,71,67]):
    tt=np.arange(int(0.6*sr))/sr; add(np.sin(2*np.pi*mtof(m)*tt)*np.exp(-tt*5)*0.12,4.0+i*0.25,1.0,0.3+0.05*i)
add(riser(1.0),5.0,0.45)
# freeze moment 9.5-10.5: boom + shutter, groove stops
add(shutter(),9.5,0.9); add(pad(prog[3],1.0),9.5,0.6)
# impacts & whooshes on cuts
for c in (2.0,6.0,12.5): add(boom(),c,0.55)
add(boom(),9.5,0.5)
for c in (2.0,4.0,6.0,10.5,12.5): add(whoosh(),c-0.35,0.5,0.5)
# ending: final chord + boom at 15.0
add(boom(),15.0,0.6); add(pad([45,57,60,64,67],1.5),15.0,1.2)
# reverb send
ir_n=int(1.6*sr); it=np.arange(ir_n)/sr
def rev(x,seed):
    ir=np.random.default_rng(seed).normal(0,1,ir_n)*np.exp(-it*3.5); ir[:int(0.01*sr)]=0
    N=1<<int(np.ceil(np.log2(n+ir_n)))
    return np.fft.irfft(np.fft.rfft(x,N)*np.fft.rfft(ir,N),N)[:n]*0.012
L2=L+rev(L,1); R2=R+rev(R,2)
# glue: soft clip
L2=np.tanh(L2*1.3); R2=np.tanh(R2*1.3)
fade=np.minimum(1,(T-t)/1.0); L2*=fade; R2*=fade
pk=max(abs(L2).max(),abs(R2).max()); L2*=0.9/pk; R2*=0.9/pk
out=(np.stack([L2,R2],1)*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(out.tobytes()); w.close()
