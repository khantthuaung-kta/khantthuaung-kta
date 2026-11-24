"""Render the README banner. Run with Python 3 and Pillow."""
from math import cos, sin, pi
from pathlib import Path
from random import Random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,S = 960,336,2
OUT = Path(__file__).resolve().parents[1] / 'assets'
OUT.mkdir(exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu'
def font(size, bold=False, mono=False):
    return ImageFont.truetype(f'{FONT}/DejaVu{"SansMono" if mono else "Sans"}{"-Bold" if bold else ""}.ttf',size*S)
def xy(p): return tuple(round(v*S) for v in p)
def iso(x,y,z=0): return (685+1.15*(x-y), 232+.51*(x+y)-z)
def poly(d,pts,fill,edge=None):
    d.polygon([xy(p) for p in pts],fill,edge,width=S)
def line(d,pts,col,k=1):
    d.line([xy(p) for p in pts],col,width=max(1,round(k*S)),joint='curve')
def circ(d,p,r,c):
    x,y=p;d.ellipse((*xy((x-r,y-r)),*xy((x+r,y+r))),fill=c)
def ring(x,y,r,z,n=42):
    return [iso(x+r*cos(i*2*pi/n),y+r*sin(i*2*pi/n),z) for i in range(n)]

bg=Image.new('RGB',(W,H))
pix=bg.load()
for y in range(H):
    for x in range(W):
        a=max(0,1-(((x-737)/610)**2+((y-112)/320)**2)**.5)
        b=max(0,1-(((x-871)/450)**2+((y-243)/190)**2)**.5)
        pix[x,y]=(int(9+19*a+9*b),int(12+6*a+7*b),int(24+26*a+13*b))
bg=bg.resize((W*S,H*S),Image.Resampling.BILINEAR).convert('RGBA')
d=ImageDraw.Draw(bg)
rng=Random(24)
for _ in range(110):
    x,y=rng.uniform(399,947),rng.uniform(20,295)
    if y<197:
        circ(d,(x,y),rng.choice([.35,.5,.65,1.05]),rng.choice(['#303653','#3b385b','#4c3e69']))
for u in range(-216,217,18):
    line(d,[iso(-218,u),iso(218,u)],'#232340',.5)
    line(d,[iso(u,-218),iso(u,218)],'#27223e',.5)
def slab(x,y,w,l,z,depth,top,left,right,edge):
    a,b,c,e=(iso(x,y,z),iso(x+w,y,z),iso(x+w,y+l,z),iso(x,y+l,z))
    lift=lambda p:(p[0],p[1]+depth)
    poly(d,[e,c,lift(c),lift(e)],left,edge)
    poly(d,[b,c,lift(c),lift(b)],right,edge)
    poly(d,[a,b,c,e],top,edge)
    return a,b,c,e

roads=[
    ([(-145,36),(-111,80),(-83,105),(-46,116),(32,116),(71,103),(109,71),(142,28)], '#ff54db','#643478'),
    ([(-126,62),(-90,107),(-58,129),(-26,137),(38,136),(87,123),(125,92),(161,47)], '#4ce4ff','#246075'),
    ([(27,-143),(93,-117),(143,-87),(159,-47),(159,-4),(142,28)], '#a879ff','#513a83'),
]
roads=[([iso(*p) for p in raw],c,low) for raw,c,low in roads]
g=Image.new('RGBA',bg.size);gd=ImageDraw.Draw(g)
for path,c,low in roads:
    line(gd,path,c,6)
bg=Image.alpha_composite(bg,g.filter(ImageFilter.GaussianBlur(6*S)))
d=ImageDraw.Draw(bg)
for path,c,low in roads: line(d,path,low,1.2)
for x,y,w,l in [(-49,63,91,70),(-64,-27,96,87),(26,-107,81,75)]:
    slab(x,y,w,l,6,8,'#292748','#131729','#201834','#4a3e68')
    slab(x+5,y+5,w-10,l-10,8,3,'#292e49','#161a2e','#251b39','#614779')

CYAN=('#52edff','#2c889e','#165c76','#2a5675')
VIOLET=('#ce75ff','#8156ba','#51317c','#4d365f')
GOLD=('#ffb79b','#c78391','#814765','#71415d')

def box_tower(x,y,w,l,base,levels,colors):
    bright,mid,dark,roof=colors
    ht=15*levels
    slab(x,y,w,l,base+ht,ht,roof,'#25324c','#19293f',dark)
    for k in range(levels):
        z=base+7+k*15
        for i in range(5):
            px=x+4+i*(w-7)/5; step=(w-7)/5-2
            col=rng.choice([mid,mid,dark,bright,'#a1bedb'])
            poly(d,[iso(px,y+l,z),iso(px+step,y+l,z),iso(px+step,y+l,z+6),iso(px,y+l,z+6)],col)
        for i in range(4):
            py=y+4+i*(l-7)/4;step=(l-7)/4-2
            col=rng.choice([mid,dark,dark,'#777aaa'])
            poly(d,[iso(x+w,py,z),iso(x+w,py+step,z),iso(x+w,py+step,z+6),iso(x+w,py,z+6)],col)
    for z in [base+2,base+ht]:
        line(d,[iso(x,y+l,z),iso(x+w,y+l,z),iso(x+w,y,z)],bright,1.2)
    return base+ht

def round_tower(x,y,r,base,ht,colors):
    br,mid,dk,roof=colors
    lo,hi=ring(x,y,r,base),ring(x,y,r,base+ht)
    for i in range(len(lo)//2+1):
        c=['#35234f','#43305e','#39254e','#2a2041'][min(3,i//6)]
        poly(d,[lo[i],lo[i+1],hi[i+1],hi[i]],c)
        if i%2==0:
            for j in range(6,ht-5,11):
                w=ring(x,y,r+.2,base+j)
                v=[(px,py-4) for px,py in w]
                poly(d,[w[i],w[i+1],v[i+1],v[i]],rng.choice([mid,dk,'#f4a2ff','#a883cb']))
    for z in (base+1,base+ht//2,base+ht):
        rr=ring(x,y,r+.7,z);line(d,rr+[rr[0]],br,1.25)
    poly(d,hi,roof,br)
    inner=ring(x,y,r*.74,base+ht+.6); poly(d,inner,'#151b33',mid)

# Back-right blade tower, left staggered blocks, central round building.
box_tower(48,-91,41,40,9,5,CYAN)
box_tower(53,-87,32,34,84,2,CYAN)
poly(d,[iso(55,-87,114),iso(86,-87,114),iso(86,-52,114),iso(63,-76,142)],'#3c4f78','#82dbff')
line(d,[iso(63,-76,142),iso(86,-52,114),iso(86,-87,114)],'#a199ff',1.2)
box_tower(-39,75,55,41,9,2,CYAN)
box_tower(-33,79,46,33,39,2,CYAN)
box_tower(-23,83,32,24,69,2,CYAN)
slab(-19,87,21,15,102,3,'#22294d','#20506a','#46366e','#9fb8ff')
round_tower(-19,12,28,9,85,VIOLET)
round_tower(-19,12,21,94,30,VIOLET)
for x,y,h,col in [(7,124,10,'#ff81d8'),(-38,109,8,'#89eaff'),(-45,24,10,'#ffa5d9'),(99,-61,8,'#ad99ff'),(48,-24,7,'#4aeaff'),(22,-15,8,'#ff71cc')]:
    line(d,[iso(x,y,7),iso(x,y,7+h)],'#69688b',1)
    circ(d,iso(x,y,7+h),2.35,col)
    circ(d,iso(x,y,7+h),.9,'#fef2f9')

# Foreground text remains steady; motion is restricted to the street network.
fade=Image.new('RGBA',bg.size); f=ImageDraw.Draw(fade)
for x in range(550):
    k=max(0,min(1,(550-x)/210))
    f.line((x*S,0,x*S,H*S),fill=(11,13,25,round(210*k)),width=S)
bg=Image.alpha_composite(bg,fade)
d=ImageDraw.Draw(bg)
def txt(x,y,value,ft,c): d.text(xy((x,y)),value,font=ft,fill=c)
txt(38,46,'02  /  PERSONAL BUILD DISTRICT',font(13,mono=True),'#bca9ed')
txt(36,90,'Khant Thu Aung',font(46,True),'#f5f2ff')
txt(39,155,'Odoo & Python Developer',font(23),'#d4cceb')
line(d,[(39,213),(81,213)],'#fa61d3',2)
line(d,[(82,213),(124,213)],'#6a77f6',2)
for x,y,label,col in [(556,309,'01','#7feaff'),(712,266,'02','#f4a8ff'),(860,258,'03','#90bdfd')]:
    d.rounded_rectangle((*xy((x-14,y-10)),*xy((x+14,y+10))),radius=5*S,fill='#171830',outline=col,width=S)
    txt(x-7,y-7,label,font(10,True,True),col)
txt(39,236,'N E O N   D E V   C I T Y',font(14,True,True),'#f1dfff')
txt(39,267,'ERP  /  AUTOMATION  /  WEB',font(12,mono=True),'#a6a9c9')
d.rounded_rectangle((0,0,W*S-1,H*S-1),radius=14*S,outline='#504162',width=S)

def make_frame(t):
    trail=Image.new('RGBA',bg.size);td=ImageDraw.Draw(trail)
    highlights=Image.new('RGBA',bg.size);hd=ImageDraw.Draw(highlights)
    for j,(path,col,_) in enumerate(roads):
        def point(t):
            s=max(0,min(len(path)-1-1e-6,t*(len(path)-1)))
            i=int(s);a,b=path[i:i+2];u=s-i
            return (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
        t0=(t+(.32*j))%1
        for p in (t0,(t0+.49)%1):
            # Fade up and down at both ends so the moving lights wrap seamlessly.
            ramp=min(1,p/.11,(1-p)/.11)
            if ramp<.05: continue
            seg=[point(p-i*.006) for i in range(8,-1,-1)]
            rgb=tuple(bytes.fromhex(col[1:]))
            line(td,seg,(*rgb,round(200*ramp)),3)
            for i in range(len(seg)-1):
                line(hd,seg[i:i+2],(*rgb,round((85+20*i)*ramp)),1.55)
            circ(hd,seg[-1],1.55,(253,245,255,round(240*ramp)))
    fr=Image.alpha_composite(bg,trail.filter(ImageFilter.GaussianBlur(4*S)))
    fr=Image.alpha_composite(fr,highlights)
    return fr.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

master=make_frame(.40)
master.save(OUT/'neon-dev-city-still.png',optimize=True)
palette=master.quantize(colors=224,method=Image.Quantize.MEDIANCUT)
frames=[make_frame(i/48).quantize(palette=palette,dither=Image.Dither.NONE) for i in range(48)]
frames[0].save(OUT/'neon-dev-city.gif', save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=True, disposal=1)
