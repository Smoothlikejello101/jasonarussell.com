import numpy as np, potrace
from PIL import Image, ImageFilter, ImageDraw
from trace import layers, S
def up(cov, grow=0.75):
    im=Image.fromarray((cov*255).astype(np.uint8)).resize((cov.shape[1]*S,cov.shape[0]*S),Image.BICUBIC)
    im=im.filter(ImageFilter.GaussianBlur(S*0.3)).point(lambda p:255 if p>127 else 0)
    n=int(round(grow*S))
    if n: im=im.filter(ImageFilter.MaxFilter(2*n+1)).filter(ImageFilter.GaussianBlur(S/3)).point(lambda p:255 if p>127 else 0)
    return im.convert('L')
def tolist(m): return np.asarray(m)>127
def jright(J,y,xmax):
    xs=np.where(J[int(y),:xmax])[0]; return xs.max()
def end_geom(R, y0,y1, xmax, inset):
    band=R[y0:y1,:xmax]; cols=np.where(band.any(0))[0]; xe=cols.min()
    xc=xe+inset; ys=np.where(band[:,xc])[0]+y0
    return xe, xc, ys.min(), ys.max()
def bez(p0,p1,p2,n=40):
    t=np.linspace(0,1,n)[:,None]; p0,p1,p2=map(np.array,(p0,p1,p2))
    return ((1-t)**2*p0+2*(1-t)*t*p1+t**2*p2).tolist()
def taper(draw, xc,yt,yb, xj, tip_frac, h, depth=0.6):
    yc=yt+(yb-yt)*tip_frac
    top=bez((xc,yt),(xc-(xc-xj)*0.5,yt+(yc-yt)*0.15),(xj,yc-h/2))
    bot=bez((xc,yb),(xc-(xc-xj)*depth,yb-(yb-yc)*0.1),(xj,yc+h/2))
    draw.polygon([tuple(p) for p in top]+[tuple(p) for p in bot[::-1]],fill=255)
def build(top='taper', waist='taper', h=0.8, grow=0.75):
    d,y=layers(); Jm=up(d,grow); Rm=up(y,grow); J=tolist(Jm); R=tolist(Rm)
    dr=ImageDraw.Draw(Rm)
    # waist
    xe,xc,yt,yb=end_geom(R,92*S,114*S,150*S,4*S)
    yc=yt+(yb-yt)*0.35; jr=jright(J,yc,130*S)
    if waist=='taper': taper(dr,xc,yt,yb,jr+2*S,0.35,h*S)
    elif waist=='full': taper(dr,xc,yt,yb,jr+2*S,0.4,h*S*4,depth=0.45)
    elif waist=='short': taper(dr,xc,yt,yb,jr+1.6*S,0.35,0.01)
    # top
    xe,xc,yt,yb=end_geom(R,12*S,32*S,140*S,4*S)
    yc=yt+(yb-yt)*0.25; jr=jright(J,yc,130*S)
    if top=='taper': taper(dr,xc,yt,yb,jr+2*S,0.25,h*S)
    elif top=='flag': dr.polygon([(xc,yt),(jr-3*S,yt),(jr-3*S,yb),(xc,yb)],fill=255)
    elif top=='short': taper(dr,xc,yt,yb,jr+1.6*S,0.25,0.01)
    if waist=='short' or top=='short':
        # pen-lift: carve an even 1.6px gap from J
        Jg=Jm.filter(ImageFilter.MaxFilter(int(1.6*S)*2+1))
        Rm=Image.fromarray(np.where(np.asarray(Jg)>127,0,np.asarray(Rm)).astype(np.uint8))
    return Jm, Rm
def path(m, alphamax=1.0):
    arr=np.asarray(m.filter(ImageFilter.GaussianBlur(S*0.15)))>127
    p=potrace.Bitmap(~arr).trace(turdsize=40, alphamax=alphamax, opticurve=True, opttolerance=0.2)
    d=[]
    for c in p:
        sp=c.start_point; d.append(f'M{sp.x/S:.2f} {sp.y/S:.2f}')
        for s in c.segments:
            if s.is_corner: d.append(f'L{s.c.x/S:.2f} {s.c.y/S:.2f}L{s.end_point.x/S:.2f} {s.end_point.y/S:.2f}')
            else: d.append(f'C{s.c1.x/S:.2f} {s.c1.y/S:.2f} {s.c2.x/S:.2f} {s.c2.y/S:.2f} {s.end_point.x/S:.2f} {s.end_point.y/S:.2f}')
        d.append('Z')
    return ''.join(d)
def svg(jd, rd, J='#141414', R='#e2ae0e', slant=6, px=None, vb='12 6 232 248', style=''):
    st=f' style="width:{px}px;height:{px}px;{style}"' if px else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{st}><g transform="translate(0 187) skewX({-slant}) translate(0 -187)">'
            f'<path d="{rd}" fill="{R}"/><path d="{jd}" fill="{J}"/></g></svg>')
