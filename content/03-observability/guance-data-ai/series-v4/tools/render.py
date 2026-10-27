# Graphviz .dot -> animated GIF (blue dots moving along edges). Logic from guance-free-zone/diagrams/src/animate.py, no captions.
# usage: python3 render.py <article_dir>   (renders <article_dir>/diagrams/src/*.dot -> diagrams/gif/<name>-wechat.gif / -xhs.gif)
import json,subprocess,glob,os,sys,io
from PIL import Image,ImageDraw
DPI=144; N=20
def fit(im,W,H=None):
    pad=50; s=min(1.0,(W-2*pad)/im.width)
    if H: s=min(s,(H-2*pad)/im.height)
    r=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    Hc=H or r.height+2*pad
    c=Image.new('RGB',(W,Hc),'white'); c.paste(r,((W-r.width)//2,(Hc-r.height)//2)); return c
def bez(p):
    pts=[]
    for i in range(0,len(p)-1,3):
        P=p[i:i+4]
        if len(P)<4: break
        for k in range(12):
            u=k/12; a=(1-u)**3;b=3*u*(1-u)**2;c=3*u*u*(1-u);d=u**3
            pts.append((a*P[0][0]+b*P[1][0]+c*P[2][0]+d*P[3][0],a*P[0][1]+b*P[1][1]+c*P[2][1]+d*P[3][1]))
    pts.append(tuple(p[-1])); return pts
art=sys.argv[1]; src=os.path.join(art,'diagrams/src'); out=os.path.join(art,'diagrams/gif'); os.makedirs(out,exist_ok=True)
for dot in sorted(glob.glob(src+'/*.dot')):
    name=os.path.basename(dot)[:-4]
    r=subprocess.run(['dot','-Tpng',f'-Gdpi={DPI}',dot],capture_output=True)
    if r.returncode: print('FAIL',dot,r.stderr.decode()); sys.exit(1)
    js=json.loads(subprocess.run(['dot','-Tjson',dot],capture_output=True).stdout.decode('utf-8','replace'),strict=False)
    base=Image.open(io.BytesIO(r.stdout)).convert('RGB')
    bb=[float(x) for x in js['bb'].split(',')]
    sx=sy=DPI/72; ox=(base.width-(bb[2]-bb[0])*sx)/2; oy=(base.height-(bb[3]-bb[1])*sy)/2
    paths=[]
    for e in js.get('edges',[]):
        if 'invis' in e.get('style',''): continue
        for op in e.get('_draw_',[]):
            if op['op'] in 'bB':
                pts=[(ox+x*sx, base.height-oy-y*sy) for x,y in op['points']]
                paths.append(bez(pts))
    frames={'wechat':[],'xhs':[]}
    for f in range(N):
        im=base.copy(); d=ImageDraw.Draw(im)
        for pts in paths:
            L=len(pts)
            for k in range(3):
                t=((f/N)+k/3)%1; q=pts[min(L-1,int(t*(L-1)))]
                rr=6; d.ellipse([q[0]-rr,q[1]-rr,q[0]+rr,q[1]+rr],fill='#2F80ED')
        frames['wechat'].append(fit(im,1080)); frames['xhs'].append(fit(im,1080,1440))
    for k,fr in frames.items():
        q=[x.convert('P',palette=Image.ADAPTIVE,colors=128) for x in fr]
        q[0].save(f'{out}/{name}-{k}.gif',save_all=True,append_images=q[1:],duration=80,loop=0,optimize=True)
    print(art,name,'edges',len(paths),'raw',base.size)
