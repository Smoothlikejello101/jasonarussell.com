import numpy as np
from PIL import Image, ImageDraw
from trace import layers, S
from joins import up, bez
from joins2 import leftedge, topedge, jr
def build(rscale=1.0, gap=1.6, tipr=0.0, tb=0.0, trise=0.0, wrise=0.0, wlen=0.0, tlen=5.0, jgrow=0.75, rgrow=0.75):
    d,y=layers()
    if rscale!=1.0:
        ax,ay=118.0,18.0; inv=1/rscale
        yi=Image.fromarray((y*255).astype(np.uint8)).transform((y.shape[1],y.shape[0]),Image.AFFINE,(inv,0,ax-ax*inv,0,inv,ay-ay*inv),resample=Image.BICUBIC)
        y=np.asarray(yi)/255.0
    Jm=up(d,jgrow); Rm=up(y,rgrow)
    J=np.asarray(Jm)>127; R=np.asarray(Rm)>127
    im=Image.fromarray(np.asarray(Rm).copy()); dr=ImageDraw.Draw(im)
    # waist
    band=R[78*S:112*S,:150*S]; xe=np.where(band.any(0))[0].min()
    ya,_=topedge(R,xe+2*S,78*S,112*S)
    xs5=int(xe+5*S); ya5,_=topedge(R,xs5+2*S,78*S,112*S)
    arr=np.asarray(im).copy(); arr[int(min(ya,ya5)-4*S):int(ya+2*S), :xs5+S]=0; im=Image.fromarray(arr); dr=ImageDraw.Draw(im)
    yT=ya+0.4*S+wrise*S; xT=jr(J,yT)
    xtip=xT+(gap+tb/2)*S
    yB=ya+9*S+wlen*S; xB=leftedge(R,yB,100*S,160*S); xB2=leftedge(R,yB+4*S,100*S,160*S)
    k=(xB2-xB)/(4*S); yc=yT+0.25*S; xc=max(xB+(yc-yB)*k, xtip+0.5*S)
    top_e=bez((xs5+2*S,ya5),((xs5+xtip)/2,min(ya,ya5)+0.1*S+wrise*S*0.3),(xtip,yT))
    bot_e=bez((xB,yB),(xc,yc+tb*S),(xtip,yT+tb*S))
    dr.polygon([tuple(p) for p in top_e]+[tuple(p) for p in bot_e[::-1]],fill=255)
    if tb: dr.ellipse([xtip-tb*S/2,yT,xtip+tb*S/2,yT+tb*S],fill=255)
    # top
    band=R[10*S:32*S,:150*S]; xs=np.where(band.any(0))[0].min()
    x0=int(xs+tlen*S); yt,yb=topedge(R,x0,10*S,34*S)
    arr=np.asarray(im).copy(); arr[yt-3*S:yb+2*S,:x0]=0; im=Image.fromarray(arr); dr=ImageDraw.Draw(im)
    yT2=yt+0.3*S+trise*S; xJ2=jr(J,max(yT2,yt)+S)
    xtip=xJ2+(gap+tb/2)*S
    xa=x0+S; ytA,ybA=topedge(R,xa,10*S,34*S); ytB,ybB=topedge(R,xa+4*S,10*S,34*S)
    mt=(ytB-ytA)/(4*S); mb=(ybB-ybA)/(4*S)        # edge slopes (dy/dx)
    cx=xa-(xa-xtip)*0.5
    top_e=bez((xa,ytA),(cx,ytA-mt*(xa-cx)+trise*S*0.2),(xtip,yT2))
    cxb=xa-(xa-xtip)*0.55
    bot_e=bez((xa,ybA),(cxb,ybA-mb*(xa-cxb)),(xtip,yT2+tb*S))
    dr.polygon([tuple(p) for p in top_e]+[tuple(p) for p in bot_e[::-1]],fill=255)
    if tb: dr.ellipse([xtip-tb*S/2,yT2,xtip+tb*S/2,yT2+tb*S],fill=255)
    return Jm, im
