from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.pointInsidePen import PointInsidePen
FS='node_modules/@fontsource/'
class G:
    def __init__(s, font, ch):
        t=TTFont(FS+font); s.gs=t.getGlyphSet(); s.g=s.gs[t.getBestCmap()[ord(ch)]]
        p=SVGPathPen(s.gs); s.g.draw(p); s.d=p.getCommands()
        b=BoundsPen(s.gs); s.g.draw(b); s.b=b.bounds
        s.cap=t['OS/2'].sCapHeight or 650
    def inside(s,x,y):
        p=PointInsidePen(s.gs,(x,y)); s.g.draw(p); return p.getResult()
    def runs(s,y,step=2):
        x0,_,x1,_=s.b; out=[]; cur=None; x=x0-2
        while x<=x1+2:
            i=s.inside(x,y)
            if i and cur is None: cur=x
            if not i and cur is not None: out.append((cur,x)); cur=None
            x+=step
        return out
def build(font, rfont=None, J='#141414', R='#e2ae0e', pad=40, idp='c', trim=2, rshift=0):
    j=G(font,'J'); r=G(rfont or font,'R'); cap=j.cap
    h1,h2=0.3*cap,0.62*cap
    jr1,jr2=j.runs(h1)[0], j.runs(h2)[0]
    rr1,rr2=r.runs(h1)[0], r.runs(h2)[0]
    jmid=((jr1[0]+jr1[1])/2+(jr2[0]+jr2[1])/2)/2; rmid=((rr1[0]+rr1[1])/2+(rr2[0]+rr2[1])/2)/2
    dx=jmid-rmid+rshift
    # clip line along J stem right edge
    slope=(jr2[1]-jr1[1])/(h2-h1)
    xr=lambda y: jr1[1]+slope*(y-h1)-trim
    # R stem geometry (R coords, then shifted by dx)
    rslope=(rr2[1]-rr1[1])/(h2-h1)
    rright=lambda y: rr1[1]+rslope*(y-h1)+dx+3
    stemw=rr1[1]-rr1[0]
    joinY=None
    for y in range(int(0.12*cap), int(0.75*cap), 4):
        rs=r.runs(y)
        if rs and (rs[0][1]-rs[0][0])>stemw*1.6: joinY=y; break
    if joinY is None: joinY=int(0.4*cap)
    joinY-=6
    footTop=None; footRight=None
    for y in range(2,160,4):
        rs=r.runs(y)
        if not rs: continue
        f=rs[0]
        if (f[1]-f[0])>stemw*1.15 and f[0]<rr1[0]+stemw and y<joinY: footTop=y; footRight=max(footRight or 0,f[1])
    Y0,Y1=-400,1300
    m=f'<mask id="{idp}" maskUnits="userSpaceOnUse" x="-3000" y="-3000" width="9000" height="9000">'
    m+=f'<path fill="#fff" d="M{xr(Y0):.1f} {Y0}L{xr(Y1):.1f} {Y1}L3000 {Y1}L3000 {Y0}Z"/>'
    m+=f'<path fill="#000" d="M-3000 -400L{rright(-400):.1f} -400L{rright(joinY):.1f} {joinY}L-3000 {joinY}Z"/>'
    if footTop is not None:
        m+=f'<rect fill="#000" x="-3000" y="-400" width="{3000+footRight+dx+14:.1f}" height="{400+footTop+14}"/>'
    m+='</mask>'
    clip=m
    # bounds
    X0=min(j.b[0], xr(0))-pad; X1=max(j.b[2], r.b[2]+dx)+pad
    Yb=min(j.b[1], r.b[1])-pad; Yt=max(j.b[3], r.b[3])+pad
    W,H=X1-X0,Yt-Yb
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}"><defs>{clip}</defs>'
         f'<g transform="matrix(1 0 0 -1 {-X0:.1f} {Yt:.1f})">'
         f'<g mask="url(#{idp})"><path d="{r.d}" transform="translate({dx:.1f} 0)" fill="{R}"/></g>'
         f'<path d="{j.d}" fill="{J}"/></g></svg>')
    return svg, dict(foot=footTop, dx=dx, join=joinY)
