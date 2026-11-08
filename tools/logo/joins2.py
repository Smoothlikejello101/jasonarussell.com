import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from trace import layers, S
from joins import up, path, svg, bez
def leftedge(R,y,xmin,xmax):
    xs=np.where(R[int(y),xmin:xmax])[0]; return xs.min()+xmin
def topedge(R,x,ymin,ymax):
    ys=np.where(R[ymin:ymax,int(x)])[0]; return ys.min()+ymin, ys.max()+ymin
def jr(J,y): return np.where(J[int(y),:130*S])[0].max()
def build(top='taper', waist='taper', h=0.7, grow=0.75, over=2.5, short=1.6):
    d,y=layers(); Jm=up(d,grow); Rm=up(y,grow); J=np.asarray(Jm)>127; R=np.asarray(Rm)>127
    out=np.asarray(Rm).copy(); im=Image.fromarray(out); dr=ImageDraw.Draw(im)
    # ---------- waist ----------
    band=R[90*S:112*S,:150*S]; xe=np.where(band.any(0))[0].min()
    ya,_=topedge(R,xe+2*S,90*S,112*S)               # top edge of return stroke near its end
    yT=ya+0.4*S                                       # tip top
    xT=jr(J,yT+h*S/2)
    if waist!='none':
        th=6.0*S                                       # bowl-return thickness
        yB=ya+th; xB=leftedge(R,yB,100*S,160*S)        # point on leg's left edge
        if waist=='short': xtip=xT+short*S; hh=0.0
        elif waist=='soft': xtip=xT-over*S; hh=2.4*S
        else: xtip=xT-over*S; hh=h*S
        if waist=='short': xtip=xT+short*S
        yB=ya+th+3*S; xB=leftedge(R,yB,100*S,160*S); xB2=leftedge(R,yB+4*S,100*S,160*S)
        k=(xB2-xB)/(4*S)                               # leg edge dx/dy
        yc=yT+hh+0.25*S; xc=max(xB+(yc-yB)*k, xtip+0.5*S)
        top_e=bez((xe+3*S,ya),((xe+xtip)/2,ya+0.1*S),(xtip,yT))
        bot_e=bez((xB,yB),(xc,yc),(xtip,yT+hh))
        dr.polygon([tuple(p) for p in top_e]+[tuple(p) for p in bot_e[::-1]],fill=255)
    # ---------- top ----------
    band=R[10*S:32*S,:150*S]; xs=np.where(band.any(0))[0].min()
    x0=xs+5*S; yt,yb=topedge(R,x0,10*S,34*S)
    # erase R start left of x0 in this band
    arr=np.asarray(im).copy(); arr[yt-2*S:yb+2*S,:x0]=0; im=Image.fromarray(arr); dr=ImageDraw.Draw(im)
    if top=='flag':
        xj=jr(J,(yt+yb)/2)-3*S
        dr.polygon([(x0+S,yt),(xj,yt),(xj,yb),(x0+S,yb)],fill=255)
    else:
        yT2=yt+0.3*S; xJ2=jr(J,yT2+h*S)
        if top=='short': xtip=xJ2+short*S; hh=0.0
        else: xtip=xJ2-over*S; hh=h*S
        top_e=bez((x0+S,yt),((x0+xtip)/2,yt),(xtip,yT2))
        bot_e=bez((x0+S,yb),(x0-(x0-xtip)*0.55,yT2+hh+1.2*S),(xtip,yT2+hh))
        dr.polygon([tuple(p) for p in top_e]+[tuple(p) for p in bot_e[::-1]],fill=255)
    return Jm, im
