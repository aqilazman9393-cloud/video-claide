import numpy as np, wave, sys
sr=48000; T=20.0; n=int(sr*T); t=np.arange(n)/sr
rng=np.random.default_rng(7)
def mtof(m): return 440*2**((m-69)/12)
bpm=76; beat=60/bpm; bar=4*beat
chords=[[57,60,64,67],[53,57,60,64],[48,52,55,59],[55,59,62,66]]  # Am7 Fmaj7 Cmaj7 G(add)
L=np.zeros(n); R=np.zeros(n)
def env(start,dur,a=0.8,r=1.5):
    e=np.zeros(n); s=int(start*sr); d=int((dur+r)*sr); s2=min(n,s+d)
    tt=np.arange(s2-s)/sr
    v=np.minimum(1,tt/a)*np.where(tt<dur,1,np.exp(-(tt-dur)*3/r))
    e[s:s2]=v; return e
# pad
for i in range(6):
    c=chords[i%4]; st=i*bar
    if st>T: break
    e=env(st,bar,a=1.2,r=2.0)
    for m in c:
        f=mtof(m)
        for det,pan in ((-0.12,0.3),(0.12,0.7)):
            ph=rng.uniform(0,6.28)
            w=np.sin(2*np.pi*f*(1+det/100)*t+ph)+0.25*np.sin(2*np.pi*2*f*t+ph)
            L+=0.035*e*w*(1-pan); R+=0.035*e*w*pan
    # bass
    fb=mtof(c[0]-12); eb=env(st,bar*0.9,a=0.05,r=0.6)
    b=np.sin(2*np.pi*fb*t)*eb*0.12; L+=b; R+=b
# keys plucks (arpeggio)
for i in range(int(T/ (beat/2))):
    st=i*beat/2; c=chords[int(st//bar)%4]
    if i%8 in (1,4,6) or (i%16==11):
        m=c[(i*3)%4]+12; f=mtof(m); s=int(st*sr); d=int(1.6*sr); s2=min(n,s+d); tt=np.arange(s2-s)/sr
        w=(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt)*np.exp(-tt*6))*np.exp(-tt*2.5)*0.06
        pan=0.3+0.4*((i*7)%5)/4
        L[s:s2]+=w*(1-pan); R[s:s2]+=w*pan
# soft kick + shaker from bar 1
for i in range(int(T/beat)):
    st=i*beat
    if st<bar or st>T-3.5: continue
    s=int(st*sr); d=int(0.4*sr); s2=min(n,s+d); tt=np.arange(s2-s)/sr
    if i%2==0:
        k=np.sin(2*np.pi*(45+60*np.exp(-tt*30))*tt)*np.exp(-tt*9)*0.22; L[s:s2]+=k; R[s:s2]+=k
    s=int((st+beat/2)*sr); d=int(0.08*sr); s2=min(n,s+d); tt=np.arange(s2-s)/sr
    h=np.diff(np.r_[0,rng.normal(0,1,s2-s)])*np.exp(-tt*60)*0.015; L[s:s2]+=h*0.8; R[s:s2]+=h*1.2
# vinyl crackle
cr=(rng.random(n)>0.9993)*rng.normal(0,0.05,n); L+=cr; R+=cr*0.8
# reverb via FFT convolution
ir_n=int(2.5*sr); it=np.arange(ir_n)/sr
def rev(x,seed):
    ir=np.random.default_rng(seed).normal(0,1,ir_n)*np.exp(-it*2.2); ir[0]=0
    N=1<<int(np.ceil(np.log2(n+ir_n)))
    y=np.fft.irfft(np.fft.rfft(x,N)*np.fft.rfft(ir,N),N)[:n]
    return y/np.max(np.abs(y)+1e-9)
L2=L+0.25*rev(L,1)*np.max(np.abs(L)); R2=R+0.25*rev(R,2)*np.max(np.abs(R))
# fade
fade=np.minimum(1,t/1.5)*np.minimum(1,(T-t)/3.0)
L2*=fade; R2*=fade
pk=max(np.abs(L2).max(),np.abs(R2).max()); L2/=pk/0.85; R2/=pk/0.85
out=(np.stack([L2,R2],1)*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(out.tobytes()); w.close()
