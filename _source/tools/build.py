"""Build the approved production website from frozen source copy. No dependencies."""
from pathlib import Path
from html.parser import HTMLParser
from html import escape
import re, os, json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT
SOURCE=ROOT/'_source/legacy'
from seo import head as seo_head, tracking
def strip_emojis(s):return re.sub(r'[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]', '', s)
VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
class Node:
 def __init__(self,tag='',attrs=None,parent=None): self.tag=tag;self.a=dict(attrs or []);self.children=[];self.parent=parent
 def all(self,pred):
  out=[]
  for c in self.children:
   if isinstance(c,Node):
    if pred(c):out.append(c)
    out+=c.all(pred)
  return out
 def find(self,id):return next(iter(self.all(lambda n:n.a.get('id')==id)),None)
 def cls(self,c):return c in self.a.get('class','').split()
 def text(self):return ''.join(c.text() if isinstance(c,Node) else c for c in self.children)
class Parser(HTMLParser):
 def __init__(self,s):
  super().__init__(convert_charrefs=True);self.root=Node();self.stack=[self.root];self.feed(s)
 def handle_starttag(self,t,a):
  n=Node(t,a,self.stack[-1]);self.stack[-1].children.append(n)
  if t not in VOID:self.stack.append(n)
 def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
 def handle_endtag(self,t):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==t:self.stack=self.stack[:i];break
 def handle_data(self,d):self.stack[-1].children.append(d)
def parse(path):return Parser((SOURCE/path).read_text()).root
def tx(n):return escape(n.text().strip()) if n else ''
def inner(n):return ''.join(render(c) for c in n.children) if n else ''
def render(n):
 if isinstance(n,str):return escape(n)
 if n.tag in ['script','style']:return ''
 attrs=''.join(f' {k}="{escape(str(v or ""),quote=True)}"' for k,v in n.a.items())
 return f'<{n.tag}{attrs}>'+('' if n.tag in VOID else inner(n)+f'</{n.tag}>')
ARROW='<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>'
PLUS='<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M5 12h14M12 5v14"/></svg>'
ICONS=[ '<path d="M3 10 12 3l9 7v11H3zM8 21V11h8v10"/>','<path d="M12 3 3 7v6c0 4 9 9 9 9s9-5 9-9V7zM8 12l3 3 5-6"/>','<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>','<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M7 3v4m10-4v4M3 10h18"/>']
def icon(i):return f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[i%4]}</svg>'
def feature_icon(i):
 if i==2:
  return '<svg width="56" height="56" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2 2 6v7c0 5 10 10 10 10s10-5 10-10V6z"/><path d="m7 12 3.5 3.5L17 9" fill="none" stroke="var(--icon-cutout)" stroke-width="2.2"/></svg>'
 if i==5:
  return '<svg width="56" height="56" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="m12 1 3.3 7.7L23 12l-7.7 3.3L12 23l-3.3-7.7L1 12l7.7-3.3z"/></svg>'
 paths=[
 '<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M7 3v4M17 3v4M3 10h18M8 15.5l2.5 2.5 5.5-5"/>',
 '<circle cx="8" cy="8" r="5"/><path d="m12 12 9 9m-4-4 3-3m-6 0 3-3"/>',
 '<path d="M12 3 3 7v6c0 4 9 9 9 9s9-5 9-9V7zM8 12l3 3 5-6"/>',
 '<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',
 '<path d="M3 10 12 3l9 7v11H3zM7 21V11h10v10M7 15h10m-10 3h10"/>',
 '<path d="m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3z"/>',
 '<path d="M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0Z"/><path d="M12 8v10m6-10h3m-3 4h3"/>',
 '<path d="M3 4h18v16H3zM3 9h18M3 15h18M9 4v5m6 0v6m-6 0v5"/>'
 ]
 return f'<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="square" stroke-linejoin="miter" aria-hidden="true">{paths[i]}</svg>'
pages=['index.html','nos-entrepots/index.html','reservation-en-ligne/index.html','faq/index.html','conseils/index.html','contact/index.html','en/index.html','en/our-warehouses/index.html','en/online-booking/index.html','en/faq/index.html','en/tips/index.html','en/contact/index.html']
fr=pages[:6];en=pages[6:]
def url(path,current):return '/'+path.removesuffix('index.html')
def asset(name,current):
 if name.endswith('.jpg') and (ROOT/'assets/site'/name.replace('.jpg','.webp')).is_file():name=name.replace('.jpg','.webp')
 return '/assets/site/'+name
def button(label,href,extra=''):return f'<a class="button {extra}" href="{escape(href,quote=True)}">{label}{ARROW}</a>'
def cleaned(n,current):
 if isinstance(n,str):return escape(n)
 if n.tag in ['script','style','svg','use']:return ''
 if n.tag=='img':
  src=n.a.get('src','')
  if any(s in src for s in ['icon','icone','bande-']):return ''
  source=(ROOT/current).parent/src
  if source.is_file():return f'<img loading="lazy" src="{os.path.relpath(source,(OUT/current).parent)}" alt="{escape(n.a.get("alt",""))}">'
  return ''
 if n.tag=='button':return '<div>'+''.join(cleaned(c,current) for c in n.children)+'</div>'
 t=n.tag
 attrs=''
 if t in ['a','iframe']:
  for k in ['href','src','title','target','loading','allowfullscreen']:
   if k in n.a:
    v=n.a[k] or ''
    if k=='href' and v.startswith('/') and not v.startswith('//'):v=url(v.lstrip('/')+'index.html' if v.endswith('/') else v.lstrip('/'),current)
    attrs+=f' {k}="{escape(v,quote=True)}"'
  if t=='a':attrs+=' class="text-link"'
 return f'<{t}{attrs}>'+('' if t in VOID else ''.join(cleaned(c,current) for c in n.children)+f'</{t}>')
def header(current,english):
 routes=en if english else fr
 labels=['Home','Our Warehouses','Online booking','FAQ','Tips','Contact'] if english else ['Accueil','Nos entrepôts','Réservation en ligne','FAQ','Conseils','Nous joindre']
 other=fr[en.index(current)] if english else en[fr.index(current)]
 nav=''.join(f'<a href="{url(p,current)}"'+(' aria-current="page"' if p==current else '')+f'>{labels[i]}</a>' for i,p in enumerate(routes) if i not in [0,2])
 portal='https://www.anemonestorage.com/login.aspx?PartenaireID=82efa877-8719-4c28-a57a-1492a3f2f470&Langue='+('EN' if english else 'FR')
 return f'''<header class="site-header"><a class="brand" href="{url(routes[0],current)}" aria-label="Entrepôts 307 — {labels[0]}"><img src="{asset('logo-horizontal.svg',current)}" width="1168" height="433" alt="Entrepôts 307"></a><nav class="desktop-nav" aria-label="{'Main navigation' if english else 'Navigation principale'}">{nav}</nav><div class="header-actions"><a class="language" href="{url(other,current)}" lang="{'fr' if english else 'en'}">{'FR' if english else 'EN'}</a>{button(labels[2],url(routes[2],current))}<button class="menu-toggle" aria-label="Menu" aria-expanded="false" aria-controls="mobile-nav"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 8h18M3 16h18"/></svg></button></div><nav id="mobile-nav" class="mobile-nav" hidden>{nav}<a href="{escape(portal)}" target="_blank" rel="noopener">{'Customer portal' if english else 'Portail-client'}{ARROW}</a></nav></header>'''
def footer(current,english,source):
 routes=en if english else fr
 a=source.find('span-354-42');b=source.find('span-435-42');c=source.find('span-393-42')
 portal='https://www.anemonestorage.com/login.aspx?PartenaireID=82efa877-8719-4c28-a57a-1492a3f2f470&Langue='+('EN' if english else 'FR')
 return f'''<section class="closing"><div><p class="eyebrow">{tx(a)}</p><h2>{tx(b)}</h2></div>{button(tx(c),url(routes[5],current),'dark-button')}</section><footer class="site-footer"><div class="footer-top"><a class="brand" href="{url(routes[0],current)}"><img src="{asset('logo-horizontal.svg',current)}" width="1168" height="433" alt="Entrepôts 307"></a><div class="footer-address">16, rue Burke<br>Cantley (Québec), J8V 3L5</div><div><a href="tel:8195934784">819 593-4784</a><a href="mailto:info@entrepots307.com">info@entrepots307.com</a></div></div><div class="footer-bottom"><span>© Entrepôts 307</span><a href="{escape(portal)}" target="_blank" rel="noopener">{'Customer portal' if english else 'Portail-client'}{ARROW}</a><a href="https://www.facebook.com/profile.php?id=61566193457096" target="_blank" rel="noopener">Facebook{ARROW}</a></div></footer>'''
def unit_icon(kind):
 paths={
 'commercial':'<path d="M4 21V7l8-4 8 4v14M4 10h16M8 21v-7h8v7M8 17h8"/>',
 'heated':'<path d="M9 14V5a3 3 0 0 1 6 0v9a5 5 0 1 1-6 0Z"/><path d="M12 8v10m6-10h3m-3 4h3"/>',
 'unheated':'<path d="m12 3 9 5-9 5-9-5 9-5ZM3 8v10l9 5 9-5V8M12 13v10"/>',
 'large':'<path d="M3 21V6l9-4 9 4v15M6 21V10h12v11M6 14h12M6 18h12M3 6h18"/>',
 'motorcycle':'<circle cx="5" cy="17" r="3.25"/><circle cx="19" cy="17" r="3.25"/><path d="M3 10h5l4 7H5l4-6h5M9 11l2-3h3l2 3M14 5h3l2 12M17.7 8H21"/>',
 'key':'<circle cx="8" cy="8" r="5"/><path d="m11.5 11.5 9 9M17 17l3-3M14 14l3-3"/>',
 'booking':'<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M7 3v4M17 3v4M3 10h18M8 15.5l2.5 2.5 5.5-5"/>'}
 return f'<svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[kind]}</svg>'
def unit_heading(node):
 return re.sub(r'(\d+\s*[x×]\s*\d+)',r'<span class="unit-dimensions">\1</span>',tx(node))
def price_copy(text,english=False):
 # Keep amounts and billing terms; omit the redundant price label.
 pattern=r'(?:Prix\s*:\s*|Price:\s*)?(?:\$\s*\d[\d,.]*|\d[\d,.]*\s*\$)\s*\+ taxes / (?:mois|month|saison|season)'
 match=re.search(pattern,text)
 if not match:return escape(text)
 price=match.group();amount=re.search(r'\$\s*\d[\d,.]*|\d[\d,.]*\s*\$',price)
 value=escape(amount.group()).replace('$','<span class="price-currency">$</span>')
 terms=price[amount.end():];taxes,period=terms.split(' / ',1)
 styled=f'<span class="unit-price"><strong class="price-amount">{value}</strong><span class="price-terms"><span class="price-tax">{escape(taxes)}</span><span class="price-period"> / {escape(period)}</span></span></span>'
 return escape(text[:match.start()])+styled+escape(text[match.end():])

def storage(source,current,english):
 cards=[]
 booking=url('en/online-booking/index.html' if english else 'reservation-en-ligne/index.html',current)
 accordions=source.all(lambda n:n.cls('oxel_accordion'))
 for i,n in enumerate(accordions):
  h=n.all(lambda x:x.tag=='h3')[0];row=n.all(lambda x:x.cls('oxel_accordion__row'))[0]
  textblocks=row.all(lambda x:x.cls('ct-text-block'))
  content=''.join(cleaned(x,current) for x in n.all(lambda x:x.cls('accordion-content')))
  kind=['commercial','heated','unheated','large'][i]
  summary=price_copy(textblocks[0].text().strip(),english)
  if english:
   found=re.search(r'Price: \$[0-9]+ \+ taxes / month',n.text())
   if found:summary+=' '+price_copy(found.group(),True)
  cards.append(f'<article id="{kind}" class="unit-card unit-{kind}"><div class="unit-photo"><img src="{asset("unit-"+kind+("-actual" if kind in ["commercial","large"] else "-row")+".jpg",current)}" alt="{tx(h)}" loading="lazy"></div><div class="unit-body"><div class="unit-symbol">{unit_icon(kind)}</div><h2>{unit_heading(h)}</h2><p class="unit-subtitle">{summary}</p><details><summary>{tx(textblocks[-1])}{PLUS}</summary><div class="unit-description">{content}</div></details></div></article>')
 motorcycle=source.all(lambda n:n.a.get('aria-labelledby')=='motorcycle-title')
 if motorcycle:
  n=motorcycle[0];ps=n.all(lambda x:x.tag=='p');h=n.all(lambda x:x.tag=='h3')[0];a=n.all(lambda x:x.tag=='a')[0]
  label=tx(n.all(lambda x:x.cls('seasonal-lease__label'))[0]);limited=tx(n.all(lambda x:x.cls('seasonal-lease__limited'))[0])
  cards.append(f'<article id="motorcycle" class="unit-card unit-motorcycle"><div class="unit-photo"><img src="{asset("unit-motorcycle-angle.jpg",current)}" alt="{tx(h)}" loading="lazy"></div><div class="unit-body"><div class="unit-symbol">{unit_icon("motorcycle")}</div><h2>{unit_heading(h)}</h2><p class="unit-subtitle">{price_copy(ps[0].text().strip(),english)}</p><details><summary>{"Learn more" if english else "En savoir plus"}{PLUS}</summary><div class="unit-description"><p class="eyebrow">{label}</p>'+''.join(f'<p>{tx(p)}</p>' for p in ps[1:])+f'<p>{limited}</p></div></details>{button(tx(a),booking,"card-booking")}</div></article>')
 storage_art=f'<img class="booking-bumper" src="{asset("booking-bumper.svg",current)}" width="600" height="400" alt="Entrepôts 307">'
 reserve='Online booking' if english else 'Réservation en ligne'
 help_title='Need storage?' if english else 'Vous avez besoin d’entreposage?'
 help_desc='We have the solution!' if english else 'Nous avons la solution!'
 cards.append(f'<article class="unit-card unit-help"><div class="unit-help-art">{storage_art}</div><div class="unit-body"><div class="unit-symbol">{unit_icon("key")}</div><h2>{help_title}</h2><p class="unit-subtitle">{help_desc}</p>{button(reserve,booking,"card-booking")}</div></article>')
 heading=source.find('span-126-705')
 return f'<section class="section storage-section"><div class="section-heading"><p class="eyebrow">{tx(heading)}</p></div><div class="units-grid">'+''.join(cards)+'</div></section>'
def home(source,current,english):
 routes=en if english else fr
 title=inner(source.find('span-98-219'))
 desc=tx(source.find('span-234-219'))
 if english:
  title='10 × 18 ft units<br><span class="hero-title-bigger">$195/month</span>'
  desc='New unheated storage units! Reserve a 10 × 18 ft unit for just $195/month.'
 # Keep the original promotion wording; visual hierarchy alone changes.
 intro=source.find('span-187-219'); features=source.find('span-257-219').all(lambda n:n.tag=='li')
 lead=tx(source.find('span-248-219'));heading=tx(source.find('span-240-219'))
 paragraphs=json.loads((OUT/'assets/site/home-copy.json').read_text())['en' if english else 'fr']
 intro_copy=''.join(f'<p>{escape(p)}</p>' for p in paragraphs)
 intro_copy=re.sub(r'(\S+)\s+(\S+)(</p>)',r'\1&#160;\2\3',intro_copy)
 bento=''
 # Keep source wording while giving each feature a distinct eyebrow and headline.
 feature_parts=(
  [('main','Quick and easy'),('eyebrow','booking')],
  [('main','Self-service'),('eyebrow','access')],
  [('main','24/7'),('eyebrow','video surveillance')],
  [('main','Flexible'),('eyebrow','rental'),('support','to suit your needs')],
  [('main','Direct vehicle'),('eyebrow','access'),('support','for maximum convenience')],
  [('main','Impeccably maintained'),('eyebrow','premises')],
  [('main','Heating'),('eyebrow','options')],
  [('main','Fireproof'),('eyebrow','concrete units')]
 ) if english else (
  [('eyebrow','Réservation'),('main','facile et rapide')],
  [('eyebrow','Accès'),('main','libre-service')],
  [('eyebrow','Surveillance vidéo'),('main','24/7')],
  [('eyebrow','Flexibilité de location'),('main','adaptée à vos besoins')],
  [('eyebrow','Accès'),('main','direct en véhicule'),('support','pour une commodité maximale')],
  [('eyebrow','Locaux'),('main','impeccablement entretenus')],
  [('eyebrow','Options'),('main','de chauffage')],
  [('eyebrow','Unités en béton'),('main','coupe-feu')]
 )
 for i,parts in enumerate(feature_parts):
  text=' '.join(f'<span class="feature-{role}">{escape(words)}</span>' for role,words in parts)
  bento+=f'<div class="feature feature-{i}"><div class="feature-icon">{feature_icon(i)}</div><h3>{text}</h3></div>'
 return f'''<section class="hero"><img class="hero-image" src="{asset('storage-dusk.jpg',current)}" alt="Entrepôts 307" fetchpriority="high"><div class="hero-shade"></div><div class="hero-copy"><p class="eyebrow"><span class="status-dot"></span>16, rue Burke · Cantley (Québec)</p><h1>{title}</h1><p class="hero-description">{desc}</p><div class="hero-actions">{button(tx(source.find('span-230-219')),url(routes[1],current))}<a class="light-link" href="{url(routes[2],current)}">{'Online booking' if english else 'Réservation en ligne'}{ARROW}</a></div></div><div class="hero-caption"><span>ENTREPÔTS 307</span><span>10 × 18</span></div></section><div class="location-strip"><span>{tx(features[1])}</span><span>{tx(features[2])}</span><span>{tx(features[7])}</span><a href="tel:8195934784">819 593-4784{ARROW}</a></div><section class="section intro"><div><p class="eyebrow">{heading}</p><h2>{lead}</h2><a class="text-link" href="{url(routes[1],current)}">{'Our Warehouses' if english else 'Nos entrepôts'}{ARROW}</a></div><div class="prose">{intro_copy}</div></section><section class="section features-section"><div class="section-heading"><h2>{tx(source.find('span-253-219'))}</h2></div><div class="bento">{bento}</div><div class="section-end">{button(tx(source.find('span-264-219')),url(routes[2],current),'dark-button')}</div></section><section class="architecture"><img src="{asset('facility-real-daylight.jpg',current)}" alt="Entrepôts 307" loading="lazy"><div class="architecture-caption"><span>ENTREPÔTS 307</span><span>CANTLEY, QUÉBEC</span></div></section>'''
def subpage(source,current,english):
 title=source.find('span-19-52');kind=current.split('/')[-2]
 head=f'<section class="page-title"><p class="eyebrow">ENTREPÔTS 307 / CANTLEY</p><h1>{tx(title)}</h1><span class="title-line"></span></section>'
 if kind in ['nos-entrepots','our-warehouses']:return head+storage(source,current,english)
 if kind=='faq':
  main=source.find('section-110-200');items=main.all(lambda n:n.cls('oxy-pro-accordion_item'))
  hs=main.all(lambda n:n.tag=='h3');out=''
  for i,n in enumerate(items):
   q=n.all(lambda x:x.cls('oxy-pro-accordion_title'))[0];a=n.all(lambda x:x.cls('oxy-pro-accordion_content'))[0]
   out+=f'<details class="faq-item"><summary><span class="faq-number">{i+1:02}</span><span>{tx(q)}</span>{PLUS}</summary><div class="faq-answer">{inner(a)}</div></details>'
  return head+f'<section class="section faq-layout"><aside><h2>{tx(hs[0])}</h2>'+''.join(f'<h2>{tx(h)}</h2>' for h in hs[1:])+f'</aside><div>{out}</div></section>'
 if kind in ['conseils','tips']:
  intro=source.find('span-16-165');items=source.all(lambda n:n.cls('conseils-repeater-item'));out=''
  for i,n in enumerate(items):
   spans=n.all(lambda x:x.a.get('data-id')=='span-94-165');body=n.all(lambda x:x.a.get('data-id')=='span-97-165')
   photos=['tips-preparation.jpg','unit-unheated.jpg','tips-protection.jpg','tips-inventory.jpg']
   if i<4:
    visual=f'<div class="tip-visual"><img src="{asset(photos[i],current)}" alt="{tx(spans[0])}" loading="lazy"></div>'
   else:
    visual='<div class="tip-visual tip-warning" aria-hidden="true"><svg width="128" height="128" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M29 9a3.5 3.5 0 0 1 6 0l24 42a3.5 3.5 0 0 1-3 5H8a3.5 3.5 0 0 1-3-5z"/><path d="M32 24v14"/><circle cx="32" cy="46" r="1.5" fill="currentColor" stroke="none"/></svg><div class="warning-ring"></div></div>'
   out+=f'<article class="tip-card {"tip-safety" if i==4 else ""}">{visual}<div class="tip-body"><span class="index-label">0{i+1}</span><h2>{tx(spans[0])}</h2><div class="prose">{inner(body[0])}</div></div></article>'
  return head+f'<section class="section"><p class="tips-intro">{tx(intro)}</p><div class="tips-grid">{out}</div></section>'
 if kind in ['reservation-en-ligne','online-booking']:
  steps=source.all(lambda n:n.a.get('data-id')=='div_block-34-213');out=''
  for i,n in enumerate(steps):
   h=n.all(lambda x:x.a.get('data-id')=='span-43-213')[0];p=n.all(lambda x:x.a.get('data-id')=='span-45-213')[0]
   out+=f'<article class="step">{icon(i)}<h3>{tx(h)}</h3><div class="prose">{inner(p)}</div></article>'
  contract=source.all(lambda n:n.cls('contract-box'))
  terms=cleaned(contract[0],current) if contract else ''
  a=source.find('link-47-213')
  # Start a fresh provider session rather than reusing a visitor's temporary /S(...)/ URL.
  href='https://www.anemonestorage.com/Recherche.aspx?PartenaireID=82EFA877-8719-4C28-A57A-1492A3F2F470&Langue='+('EN' if english else 'FR')+'&Ref='
  portal_title='Find your space.' if english else 'Trouvez votre espace.'
  portal_desc='Choose your date and rental agreement to see availability. Reserve your space, sign and pay online.' if english else 'Choisissez votre date et votre bail pour voir les disponibilités. Réservez votre espace, signez et payez en ligne.'
  open_label='Open in a new tab' if english else 'Ouvrir dans un nouvel onglet'
  frame_title='Entrepôts 307 reservations via Anemone' if english else 'Réservation Entrepôts 307 avec Anemone'
  help_label='Need a hand?' if english else 'Besoin d’un coup de main?'
  provider_label='Booking powered by Anemone' if english else 'Réservation avec Anemone'
  contract_label='Rental terms' if english else 'Conditions de location'
  contract_title=tx(contract[0].all(lambda n:n.tag=='h4')[0])
  terms=re.sub(r'<h4>.*?</h4>','',terms,flags=re.S)
  portal=f'''<section class="section reservation-experience" aria-labelledby="reservation-title"><div class="reservation-heading"><div><p class="eyebrow">{tx(title)} · CANTLEY</p><h1 id="reservation-title">{portal_title}</h1><p>{portal_desc}</p></div><a class="reservation-help" href="tel:8195934784"><span>{help_label}</span><strong>819 593-4784</strong>{ARROW}</a></div><div class="reservation-console"><div class="reservation-toolbar"><span class="reservation-provider"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="5" y="10" width="14" height="11"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/></svg>{provider_label}</span><a href="{escape(href,quote=True)}" target="_blank" rel="noopener">{open_label}{ARROW}</a></div><iframe class="reservation-frame" src="{escape(href,quote=True)}" title="{frame_title}" width="1200" height="560" referrerpolicy="strict-origin-when-cross-origin" allow="payment"></iframe></div></section>'''
  guide_label='How booking works' if english else 'Comment réserver?'
  return portal+f'<section class="section booking booking-guide"><details class="booking-guide-details"><summary><span>{guide_label}</span>{PLUS}</summary><div class="booking-guide-content"><h2 class="booking-instructions-title">{tx(source.find("span-25-213"))}</h2><div class="steps">{out}</div><a class="text-link" href="{escape(href,quote=True)}" target="_blank" rel="noopener">{tx(source.find("span-49-213")) or tx(a)}{ARROW}</a></div></details><details class="rental-terms"><summary><span>{contract_title}</span>{PLUS}</summary><div class="contract-content"><div class="contract-masthead"><span>ENTREPÔTS 307</span><span>{contract_label}</span></div><div class="terms prose">{terms}</div></div></details></section>'
 # Contact: retain all content from the existing page body.
 main=source.find('div_block-1-42');sections=main.all(lambda n:n.tag=='section' and not n.cls('page-header'))
 return head+'<section class="section contact-layout"><div class="contact-content">'+''.join(cleaned(n,current) for n in sections)+f'</div><div class="contact-photo"><img src="{asset("contact-facility-locks.jpg",current)}" width="1536" height="1024" alt="Entrepôts 307, Cantley"></div></section>'
for current in pages:
 source=parse(current);english=current.startswith('en/');ishome=current in ['index.html','en/index.html']
 main=home(source,current,english) if ishome else subpage(source,current,english)
 title=source.all(lambda n:n.tag=='title')[0].text()
 tracking_head,tracking_body=tracking((SOURCE/current).read_text())
 html=f'''<!doctype html><html lang="{'en-CA' if english else 'fr-CA'}"><head>{seo_head(current,source,asset)}{tracking_head}</head><body class="{'home' if ishome else 'inner-page'}{' booking-page' if current in ['reservation-en-ligne/index.html','en/online-booking/index.html'] else ''}">{tracking_body}<a class="skip-link" href="#main">{'Skip to content' if english else 'Aller au contenu'}</a>{header(current,english)}<main id="main">{main}</main>{footer(current,english,source)}</body></html>'''
 # Reserve image dimensions to reduce layout shifts, without altering approved crops.
 dimensions=json.loads((ROOT/'_source/media-dimensions.json').read_text())
 def image_size(match):
  tag=match.group();name=match.group(1)
  if 'width=' not in tag and name in dimensions:
   width,height=dimensions[name];tag=tag[:-1]+f' width="{width}" height="{height}">'
  if 'decoding=' not in tag:tag=tag[:-1]+' decoding="async">'
  return tag
 html=re.sub(r'<img\b[^>]*src="/assets/site/([^"/]+)"[^>]*>',image_size,html)
 dest=OUT/current;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text('\n'.join(line.rstrip() for line in strip_emojis(html).splitlines())+'\n')
# Publish every translated route, with reciprocal language alternatives.
import xml.etree.ElementTree as ET
from seo import FR, EN, absolute
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9')
ET.register_namespace('xhtml', 'http://www.w3.org/1999/xhtml')
ns='http://www.sitemaps.org/schemas/sitemap/0.9'
sitemap=ET.Element('{'+ns+'}urlset')
for fr,en in zip(FR,EN):
 for current in (fr,en):
  node=ET.SubElement(sitemap,'{'+ns+'}url')
  ET.SubElement(node,'{'+ns+'}loc').text=absolute(current)
  for lang,target in [('fr-CA',fr),('en-CA',en),('x-default',fr)]:
   ET.SubElement(node,'{http://www.w3.org/1999/xhtml}link',rel='alternate',hreflang=lang,href=absolute(target))
ET.ElementTree(sitemap).write(OUT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print('Built 12 bilingual production pages and sitemap.')
