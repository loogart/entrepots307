"""Validate release copy, tracking, crawlability, assets and booking destinations."""
import re
from pathlib import Path
from urllib.parse import urlsplit, unquote, parse_qs
import build

# Approved product-card refinement: remove redundant Prix/Price labels.
def norm(s):
    s=build.strip_emojis(s)
    s=re.sub(r'(?:Prix|Price)\s*:\s*', '', s)
    return re.sub(r'\s+', ' ', s).strip()
# Approved English headline/description corrections in revision 02.
english_revisions={'Unit 10x18','for $195/month!','New Non-Climate-Controlled Units! 🌟 Reserve now a non-climate-controlled 10x18 unit for only $195/month!"'}
english_revisions={norm(s) for s in english_revisions}
errors=[]
for page in build.pages:
    source=build.parse(page).find('div_block-1-42')
    generated=build.Parser((build.OUT/page).read_text()).root
    actual=norm(generated.find('main').text())
    def check_copy(node):
        if isinstance(node,str):
            if norm(node) and norm(node) not in actual and not (page=='en/index.html' and norm(node) in english_revisions): errors.append((page,'Missing source copy',norm(node)))
        elif node.a.get('id')=='span-187-219' and page in ['index.html','en/index.html']:
            pass # User-approved 50% shorter service introduction.
        elif node.a.get('id')=='span-31-213' and page in ['reservation-en-ligne/index.html','en/online-booking/index.html']:
            pass # Embedded booking now appears above the instructions.
        elif node.tag not in ['script','style','svg']:
            for c in node.children:check_copy(c)
    check_copy(source)
    for n in generated.all(lambda n:n.tag in ['a','img','link','script']):
        ref=n.a.get('href',n.a.get('src',''))
        parts=urlsplit(ref)
        if not ref or parts.scheme or parts.netloc or ref.startswith('#'): continue
        target=(build.OUT/unquote(parts.path).lstrip('/')).resolve()
        if target.is_dir():target=target/'index.html'
        if not target.is_file():errors.append((page,'Broken local reference',ref))
    assert len(generated.all(lambda n:n.tag=='h1'))==1
    raw=(build.OUT/page).read_text()
    from seo import absolute, tracking, FR, EN, BASE
    import json, struct
    one=lambda tag,key,value: generated.all(lambda n:n.tag==tag and n.a.get(key)==value)
    assert one('html','lang','en-CA' if page.startswith('en/') else 'fr-CA')
    assert one('link','rel','canonical')[0].a['href']==absolute(page)
    assert 'noindex' not in one('meta','name','robots')[0].a['content']
    alternates={n.a['hreflang']:n.a['href'] for n in one('link','rel','alternate')}
    i=(EN if page in EN else FR).index(page)
    assert alternates=={'fr-CA':absolute(FR[i]),'en-CA':absolute(EN[i]),'x-default':absolute(FR[i])}
    for snippet in tracking((build.SOURCE/page).read_text()):
        assert snippet and snippet in raw, (page,'Tracking changed')
    assert raw.count("fbq('init', '1455636772776328')")==1 or raw.count("fbq('init','1455636772776328')")==1
    assert '/redesign/' not in raw and 'temp-site.link' not in raw
    assert 'Logo SVG' not in raw
    schema=generated.all(lambda n:n.tag=='script' and n.a.get('type')=='application/ld+json')
    graph=json.loads(schema[0].text())['@graph']
    business=next(n for n in graph if n['@type']=='SelfStorage')
    assert business['address']['postalCode']=='J8V 3L5'
    assert business['telephone']=='+1-819-593-4784'
    if i==1:
        services=[n for n in graph if n['@type']=='Service']
        assert [n['offers']['price'] for n in services]==['599','269','195','325']
    if i==3:
        faq=next(n for n in graph if n['@type']=='FAQPage')
        assert len(faq['mainEntity'])==len(generated.all(lambda n:n.cls('faq-item')))
        for q in faq['mainEntity']:
            assert norm(q['name']) in actual and norm(q['acceptedAnswer']['text']) in actual
    for prop in ['og:image','og:url','og:title','og:description']:
        assert len(one('meta','property',prop))==1
    assert one('meta','property','og:url')[0].a['content']==absolute(page)
    assert one('meta','name','twitter:card')[0].a['content']=='summary_large_image'
    for n in generated.all(lambda n:n.tag=='img' and n.a.get('src','').startswith('/assets/site/')):
        assert n.a.get('alt') and n.a.get('width') and n.a.get('height'), (page,n.a)

    if page in ['reservation-en-ligne/index.html','en/online-booking/index.html']:
        booking=generated.all(lambda n:n.tag=='a' and 'Recherche.aspx' in n.a.get('href',''))
        assert len(booking)==2
        frames=generated.all(lambda n:n.tag=='iframe' and n.cls('reservation-frame'))
        assert len(frames)==1 and frames[0].a['src']==booking[0].a['href']
        assert '/(S(' not in frames[0].a['src']
        assert frames[0].a.get('title') and frames[0].a['height']=='560'
        assert booking[0].a['target']=='_blank' and booking[0].a['rel']=='noopener'
        assert all(n.tag=='details' and 'open' not in n.a for n in generated.all(lambda n:n.cls('rental-terms') or n.cls('booking-guide-details')))
        q=parse_qs(urlsplit(booking[0].a['href']).query)
        assert q['PartenaireID']==['82EFA877-8719-4C28-A57A-1492A3F2F470']
        assert q['Langue']==['EN' if page.startswith('en/') else 'FR']
    if page in ['nos-entrepots/index.html','en/our-warehouses/index.html']:
        cards=generated.all(lambda n:n.cls('unit-card'))
        assert len(cards)==6
        photos=generated.all(lambda n:n.tag=='img' and 'unit-' in n.a.get('src',''))
        assert len(photos)==5 and len({n.a['src'] for n in photos})==5
        assert len(generated.all(lambda n:n.cls('unit-symbol')))==6
        assert len(generated.all(lambda n:n.cls('unit-motorcycle')))==1
    print('PASS',page)
assert not errors, errors
print('PASS: source copy retained; local links/assets resolved; booking partner and languages correct.')

from xml.etree import ElementTree as ET
sitemap=ET.parse(build.OUT/'sitemap.xml')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','x':'http://www.w3.org/1999/xhtml'}
urls=sitemap.findall('s:url',ns)
assert {n.find('s:loc',ns).text for n in urls}=={absolute(p) for p in build.pages}
assert all(len(n.findall('x:link',ns))==3 for n in urls)
titles=[];descriptions=[]
for page in build.pages:
    doc=build.Parser((build.OUT/page).read_text()).root
    titles.append(doc.all(lambda n:n.tag=='title')[0].text())
    descriptions.append(doc.all(lambda n:n.tag=='meta' and n.a.get('name')=='description')[0].a['content'])
assert len(set(titles))==len(titles) and len(set(descriptions))==len(descriptions)
for name,size in [('apple-touch-icon.png',(180,180)),('assets/site/icon-512.png',(512,512)),('assets/site/icon-maskable-512.png',(512,512)),('assets/site/og-fr.png',(1200,630)),('assets/site/og-en.png',(1200,630))]:
    data=(build.OUT/name).read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',data[16:24])==size
manifest=json.loads((build.OUT/'site.webmanifest').read_text())
assert all((build.OUT/icon['src'].lstrip('/')).is_file() for icon in manifest['icons'])
assert 'Sitemap: '+BASE+'/sitemap.xml' in (build.OUT/'robots.txt').read_text()
assert 'noindex' in (build.OUT/'404.html').read_text()
assert (build.OUT/'CNAME').read_text().strip()=='entrepots307.com'
print('PASS: tracking unchanged; bilingual metadata/schema/sitemap valid; brand assets verified.')
