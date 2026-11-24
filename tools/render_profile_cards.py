"""Generate the README's SVG cards using public GitHub data and Python 3.

Usage: python3 tools/render_profile_cards.py
Optional: pass a directory with downloaded GitHub calendar and language JSON files
to render from snapshots rather than fetching new data.
"""
from collections import Counter
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

OWNER = "khantthuaung-kta"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "neon"
OUT.mkdir(parents=True, exist_ok=True)
REPOS = ("n2-news-reader-demo", "techpulse-ai", "movie-highlight-extractor", "estate_property_management")

def get(url, cache):
    if len(sys.argv) > 1:
        return (Path(sys.argv[1]) / cache).read_text()
    with urlopen(Request(url, headers={"User-Agent":"NeonDevCity-ProfileRenderer"}), timeout=20) as response:
        return response.read().decode()

def text(x,y,s,size=15,color="#ecedfa",weight=400,anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="system-ui, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(s))}</text>'

def rect(x,y,w,h,fill,r=4):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{r:.2f}" fill="{fill}"/>'

def card(w,h,title,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
<title>{escape(title)}</title>
<defs><linearGradient id="bg" x2="1" y2=".8"><stop stop-color="#0e1427"/><stop offset="1" stop-color="#1d1834"/></linearGradient></defs>
<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="12" fill="url(#bg)" stroke="#554773"/>
{body}
</svg>
'''

def write(name,w,h,title,body):
    (OUT / (name+".svg")).write_text(card(w,h,title,body), encoding="utf-8")

# Original pictograms, not brand logo files.
icons = {
    "python": ("Python", "#78d6ff", "M9 4h7a3 3 0 0 1 3 3v5H9a3 3 0 0 0-3 3v2H5a3 3 0 0 1-3-3v-3a3 3 0 0 1 3-3h7M15 20H8a3 3 0 0 1-3-3v-2m0 0v-3m3 0h7a3 3 0 0 0 3-3V7h1a3 3 0 0 1 3 3v3a3 3 0 0 1-3 3h-7M9 6h.01M15 18h.01"),
    "odoo": ("Odoo", "#e5a3ff", "M2 7l10-5 10 5-10 5zM2 12l10 5 10-5M2 17l10 5 10-5"),
    "postgresql": ("PostgreSQL", "#87bdfd", "M4 6a8 4 0 1 0 16 0 8 4 0 1 0-16 0m0 0v12a8 4 0 0 0 16 0V6M4 12a8 4 0 0 0 16 0"),
    "javascript": ("JavaScript", "#ffdc91", "M8 6l-6 6 6 6m8-12l6 6-6 6m-2-15l-4 18"),
    "react": ("React", "#7eeaff", "M2 12a10 4 0 1 0 20 0 10 4 0 1 0-20 0M6 4c2-2 6 0 9 6s4 10 2 11-6-1-9-7S4 5 6 4zm11 0c2 1 1 5-2 11s-7 7-9 6-1-5 2-11 7-8 9-6zm-5 8h.01"),
    "expo": ("Expo", "#c8b5ff", "M5 3h14v18H5zM9 7h6m-4 10h2"),
    "actions": ("GitHub Actions", "#a0e3bd", "M4 3a2 2 0 1 0 0 4 2 2 0 1 0 0-4zm16 14a2 2 0 1 0 0 4 2 2 0 1 0 0-4zM4 7v8a4 4 0 0 0 4 4h10M14 9v6m-3-3h6"),
    "linkedin": ("LinkedIn", "#7aceff", "M3 7h18v14H3zM8 7V4h8v3M3 12h18m-10 0v3h2v-3"),
    "github": ("GitHub", "#d5b4ff", "M4 4h16v16H4zM8 8l-3 4 3 4m8-8l3 4-3 4m-3-8l-2 8"),
}
for slug,(label,col,path) in icons.items():
    w=160 if slug in ("actions","postgresql") else 125
    write(slug,w,41,label,rect(8,7,27,27,"#2b2549",7)+
          f'<path d="{path}" transform="translate(12 11) scale(.8)" fill="none" stroke="{col}" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round"/>'+
          text(43,26,label,14,weight=650))

# GitHub's own rendered calendar. Record only the displayed date and intensity level.
html = get(f"https://github.com/users/{OWNER}/contributions",f"github.com_users_{OWNER}_contributions")
days = sorted((date.fromisoformat(day),int(level)) for day,level in re.findall(r'<td\b[^>]*data-date="([0-9-]+)"[^>]*data-level="([0-4])"[^>]*>',html))
assert 364 <= len(days) <= 371 and len(set(d for d,_ in days)) == len(days)
m = re.search(r'id="js-contribution-activity-description"[^>]*>\s*([0-9,]+)\s+contribution',html)
assert m, "Public calendar total is missing"
total = m.group(1)
start,end = days[0][0],days[-1][0]
assert (end-start).days+1 == len(days)
palette = ("#26263c","#41417f","#6959ba","#a470ef","#d5abff")
calendar = text(23,32,"Contribution heatmap",20,weight=700)+text(23,55,f"{total} contributions reported by GitHub  ·  Snapshot through {end:%b %d, %Y}",13,"#c6bfdd")
offset = (start.weekday()+1)%7
last_month_label_x = 15
for day,level in days:
    i = (day-start).days+offset
    col,row = divmod(i,7)
    x,y = 50+13.45*col,83+13.5*row
    calendar += rect(x,y,10.8,10.8,palette[level],2.5)
    if day.day == 1 and x - last_month_label_x >= 32:
        calendar += text(x,76,day.strftime("%b"),10,"#c6bfdd")
        last_month_label_x = x
for y,name in ((106,"Mon"),(133,"Wed"),(160,"Fri")):
    calendar += text(18,y,name,10,"#c6bfdd")
calendar += text(23,200,"GitHub’s five activity levels",12,"#c6bfdd")
calendar += text(610,200,"Less",11,"#c6bfdd")
for i,col in enumerate(palette):
    calendar += rect(643+16*i,190,11,11,col,2.5)
calendar += text(727,200,"More",11,"#c6bfdd")
write("contribution-map",790,220,f"GitHub contribution snapshot: {total} contributions through {end.isoformat()}",calendar)

aggregate = Counter()
for repo in REPOS:
    langs = json.loads(get(f"https://api.github.com/repos/{OWNER}/{repo}/languages",f"{repo}.languages.json"))
    assert langs and all(isinstance(v,int) and v>0 for v in langs.values())
    aggregate.update(langs)
langcolors = {"Python":"#8aafff","JavaScript":"#f3ca7e","CSS":"#cf9bfb"}
mix = text(23,31,"Language mix",20,weight=700)+text(23,53,"Share of code bytes across the four featured public repositories",13,"#c6bfdd")
totalbytes=sum(aggregate.values())
rows=aggregate.most_common()
for i,(name,count) in enumerate(rows):
    y=77+29*i
    pct=100*count/totalbytes
    mix+=text(23,y+10,name,13,weight=650)+rect(130,y,347,10,"#2c2848",5)
    mix+=rect(130,y,347*pct/100,10,langcolors.get(name,"#79ddd5"),5)
    mix+=text(525,y+10,f"{pct:.1f}%",13,anchor="end")
write("language-mix",550,90+29*len(rows),"Language mix: "+", ".join(f"{k} {100*v/totalbytes:.1f}%" for k,v in rows),mix)

projects = [
    ("newsroom","01","The Newsroom","N2 NEWS READER DEMO","#81eaff","M4 4h16v16H4zM7 8h10M7 12h4m2 0h4m-10 4h10"),
    ("signal","02","The Signal Tower","TECHPULSE AI","#ef93ff","M4 4l17 7-7 3-3 7-7-17zm7 10l7-5"),
    ("screening","03","The Screening Room","MOVIE HIGHLIGHT EXTRACTOR","#97adff","M3 5h18v14H3zM10 8l6 4-6 4z"),
]
for slug,num,title,label,col,p in projects:
    body=rect(15,15,41,41,"#2d2749",9)+f'<path d="{p}" transform="translate(24 24)" fill="none" stroke="{col}" stroke-width="1.6" stroke-linejoin="round" stroke-linecap="round"/>'+text(68,33,title,18,weight=700)+text(69,51,label,10,col,700)+text(325,34,num,15,col,700,"end")
    write(slug,345,71,title,body)
