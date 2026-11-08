import numpy as np, potrace
from PIL import Image, ImageFilter
SRC='/mnt/user-data/uploads/4ce30f99-image.png'
S=8  # upscale factor
def layers():
    a=np.asarray(Image.open(SRC).convert('RGB')).astype(float)
    r,g,b=a[...,0],a[...,1],a[...,2]
    # yellow coverage from blue channel drop where r high
    yel=np.clip((255-b)/(255-31),0,1)*(r>150)
    lum=0.299*r+0.587*g+0.114*b
    dark=np.clip((255-lum)/(255-58),0,1)*(b>r-40)*(np.abs(r-b)<40)
    return dark, yel
def trace(cov, blur=1.2, thr=0.5, alphamax=1.0, grow=0.0):
    im=Image.fromarray((cov*255).astype(np.uint8)).resize((cov.shape[1]*S,cov.shape[0]*S),Image.BICUBIC)
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur*S/4))
    arr=np.asarray(im)/255.0
    bm=potrace.Bitmap(~(arr>(thr-grow)))
    path=bm.trace(turdsize=20, alphamax=alphamax, opticurve=True, opttolerance=0.2)
    d=[]
    for c in path:
        sp=c.start_point; d.append(f'M{sp.x/S:.2f} {sp.y/S:.2f}')
        for seg in c.segments:
            if seg.is_corner:
                d.append(f'L{seg.c.x/S:.2f} {seg.c.y/S:.2f}L{seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}')
            else:
                d.append(f'C{seg.c1.x/S:.2f} {seg.c1.y/S:.2f} {seg.c2.x/S:.2f} {seg.c2.y/S:.2f} {seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}')
        d.append('Z')
    return ''.join(d)
if __name__=='__main__':
    dark,yel=layers()
    jd=trace(dark); rd=trace(yel)
    open('orig_J.d','w').write(jd); open('orig_R.d','w').write(rd)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 259 260"><path d="{jd}" fill="#3a3a3a" fill-rule="evenodd"/><path d="{rd}" fill="#e8cb1f" fill-rule="evenodd"/></svg>'
    open('orig_traced.svg','w').write(svg); print(len(jd),len(rd))

def trace_w(cov, k=0.0, blur=1.2, alphamax=1.0):
    """k = stroke growth in source px per side (negative = thinner)."""
    im=Image.fromarray((cov*255).astype(np.uint8)).resize((cov.shape[1]*S,cov.shape[0]*S),Image.BICUBIC)
    im=im.filter(ImageFilter.GaussianBlur(blur*S/4))
    m=im.point(lambda p:255 if p>127 else 0)
    n=int(round(abs(k)*S))
    if n:
        size=2*n+1
        m=m.filter(ImageFilter.MaxFilter(size) if k>0 else ImageFilter.MinFilter(size))
        m=m.filter(ImageFilter.GaussianBlur(S/3)).point(lambda p:255 if p>127 else 0)
    arr=np.asarray(m)>127
    path=potrace.Bitmap(~arr).trace(turdsize=20, alphamax=alphamax, opticurve=True, opttolerance=0.2)
    d=[]
    for c in path:
        sp=c.start_point; d.append(f'M{sp.x/S:.2f} {sp.y/S:.2f}')
        for seg in c.segments:
            if seg.is_corner: d.append(f'L{seg.c.x/S:.2f} {seg.c.y/S:.2f}L{seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}')
            else: d.append(f'C{seg.c1.x/S:.2f} {seg.c1.y/S:.2f} {seg.c2.x/S:.2f} {seg.c2.y/S:.2f} {seg.end_point.x/S:.2f} {seg.end_point.y/S:.2f}')
        d.append('Z')
    return ''.join(d)
