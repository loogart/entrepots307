"""Production metadata and factual structured data for the bilingual static site."""
from html import escape
import json
import re

BASE = 'https://entrepots307.com'
FR = ['index.html','nos-entrepots/index.html','reservation-en-ligne/index.html','faq/index.html','conseils/index.html','contact/index.html']
EN = ['en/index.html','en/our-warehouses/index.html','en/online-booking/index.html','en/faq/index.html','en/tips/index.html','en/contact/index.html']
META = {
 'fr': [
  ('Entreposage à Cantley | Entrepôts 307', 'Plus de 300 unités en béton à Cantley : mini-entrepôts chauffés ou non, garages commerciaux et entreposage de motos. Accès sécurisé et réservation en ligne.'),
  ('Mini-entrepôts et garages à Cantley | Entrepôts 307', 'Comparez nos mini-entrepôts 10 x 18, garages commerciaux et entreposage de motos à Cantley. Dimensions, tarifs avant taxes et réservation en ligne.'),
  ('Réservation d’entreposage en ligne | Entrepôts 307', 'Réservez votre espace d’entreposage à Cantley avec notre système Anemone. Consultez les étapes et les conditions de location avant de réserver.'),
  ('FAQ sur l’entreposage à Cantley | Entrepôts 307', 'Trouvez les réponses sur nos unités, les contrats de location, l’accès sécurisé et la réservation chez Entrepôts 307, au 16, rue Burke à Cantley.'),
  ('Conseils pour bien entreposer vos biens | Entrepôts 307', 'Préparez, protégez et organisez vos biens avant l’entreposage. Nos conseils pratiques pour profiter de votre unité chez Entrepôts 307 à Cantley.'),
  ('Nous joindre à Cantley | Entrepôts 307', 'Contactez Entrepôts 307 au 819 593-4784 ou à info@entrepots307.com. Retrouvez nos coordonnées au 16, rue Burke, Cantley, Québec, J8V 3L5.')
 ],
 'en': [
  ('Self-storage in Cantley, Québec | Entrepôts 307', 'Over 300 concrete storage units in Cantley: heated and unheated mini-storage, commercial garages and motorcycle storage. Secure access and online booking.'),
  ('Storage units and commercial garages | Entrepôts 307', 'Compare 10 x 18 storage units, commercial garages and motorcycle storage in Cantley. View dimensions, prices before taxes and online booking options.'),
  ('Book storage online in Cantley | Entrepôts 307', 'Reserve your storage space in Cantley through our Anemone booking system. Review the booking steps and rental terms before reserving your unit.'),
  ('Storage questions answered | Entrepôts 307 FAQ', 'Find answers about storage units, rental agreements, secure access and online booking at Entrepôts 307, 16 rue Burke in Cantley, Québec.'),
  ('Practical storage and packing tips | Entrepôts 307', 'Prepare, protect and organize your belongings before storage. Practical tips to make the most of your storage unit at Entrepôts 307 in Cantley.'),
  ('Contact our Cantley storage facility | Entrepôts 307', 'Contact Entrepôts 307 at 819 593-4784 or info@entrepots307.com. Find our storage facility at 16 rue Burke, Cantley, Québec, J8V 3L5.')
 ]
}

def absolute(page):
 return BASE + '/' + page.removesuffix('index.html')

def json_script(value):
 return '<script type="application/ld+json">'+json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'

def page_data(current):
 english=current in EN
 routes=EN if english else FR
 index=routes.index(current)
 return english,index,META['en' if english else 'fr'][index]

def tracking(source_html):
 """Retain the actual existing marketing snippets, without legacy UI libraries."""
 scripts=re.findall(r'<script\b[^>]*>.*?</script>',source_html,re.I|re.S)
 head='\n'.join(s for s in scripts if any(marker in s for marker in ['googletagmanager.com/','gtag(\'','gtag("','fbq(','fbevents.js']))
 fallback='\n'.join(s for s in re.findall(r'<noscript\b[^>]*>.*?</noscript>',source_html,re.I|re.S) if 'facebook.com/tr' in s)
 return head,fallback

def structured(current,source):
 english,index,(title,description)=page_data(current)
 lang='en-CA' if english else 'fr-CA'
 canonical=absolute(current)
 business={
  '@type':'SelfStorage','@id':BASE+'/#business','name':'Entrepôts 307','url':BASE+'/',
  'description':META['en' if english else 'fr'][0][1],
  'telephone':'+1-819-593-4784','email':'info@entrepots307.com',
  'address':{'@type':'PostalAddress','streetAddress':'16, rue Burke','addressLocality':'Cantley','addressRegion':'QC','postalCode':'J8V 3L5','addressCountry':'CA'},
  'areaServed':{'@type':'City','name':'Cantley'},
  'logo':{'@type':'ImageObject','url':BASE+'/assets/site/icon-512.png','width':512,'height':512},
  'image':BASE+'/assets/site/facility-real-daylight.webp',
  'currenciesAccepted':'CAD','sameAs':['https://www.facebook.com/profile.php?id=61566193457096'],
  'contactPoint':{'@type':'ContactPoint','telephone':'+1-819-593-4784','contactType':'customer service','availableLanguage':['French','English']}
 }
 website={'@type':'WebSite','@id':BASE+'/#website','url':BASE+'/','name':'Entrepôts 307','publisher':{'@id':BASE+'/#business'},'inLanguage':['fr-CA','en-CA']}
 page={'@type':'ContactPage' if index==5 else ('CollectionPage' if index==1 else 'WebPage'),'@id':canonical+'#webpage','url':canonical,'name':title,'description':description,'inLanguage':lang,'isPartOf':{'@id':BASE+'/#website'},'about':{'@id':BASE+'/#business'},'primaryImageOfPage':{'@type':'ImageObject','url':BASE+'/assets/site/og-'+('en' if english else 'fr')+'.png','width':1200,'height':630}}
 graph=[business,website,page]
 if index:
  crumb={'@type':'BreadcrumbList','@id':canonical+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':1,'name':'Home' if english else 'Accueil','item':absolute(EN[0] if english else FR[0])},{'@type':'ListItem','position':2,'name':title.split(' | ')[0],'item':canonical}]}
  graph.append(crumb);page['breadcrumb']={'@id':crumb['@id']}
 if index==1:
  kinds=['commercial','heated','unheated','motorcycle']
  names=(['13 x 30 Commercial Garages','Heated Mini-Storage Units 10 x 18','Unheated Mini-Warehouses 10 x 18','Motorcycle storage'] if english else ['Garages commerciaux 13 x 30','Mini-entrepôts chauffés 10 x 18','Mini-entrepôts non chauffés 10 x 18','Entreposage de motos'])
  offers=[]
  for kind,name,price in zip(kinds,names,[599,269,195,325]):
   service={'@type':'Service','@id':canonical+'#'+kind,'name':name,'serviceType':'Self-storage rental','provider':{'@id':BASE+'/#business'},'url':canonical+'#'+kind}
   offer={'@type':'Offer','price':str(price),'priceCurrency':'CAD','url':canonical+'#'+kind,'itemOffered':{'@id':service['@id']},'priceSpecification':{'@type':'UnitPriceSpecification','price':str(price),'priceCurrency':'CAD','valueAddedTaxIncluded':False,'unitText':('season' if english else 'saison') if kind=='motorcycle' else ('month' if english else 'mois')}}
   service['offers']=offer;offers.append(offer);graph.append(service)
  business['hasOfferCatalog']={'@type':'OfferCatalog','name':'Storage rentals' if english else 'Location d’entreposage','itemListElement':offers}
 if index==3:
  # Every answer comes from the same visible source used to build the FAQ accordions.
  questions=[]
  for item in source.all(lambda n:n.cls('oxy-pro-accordion_item')):
   q=item.all(lambda n:n.cls('oxy-pro-accordion_title'))
   a=item.all(lambda n:n.cls('oxy-pro-accordion_content'))
   if q and a:questions.append({'@type':'Question','name':re.sub(r'\s+',' ',q[0].text()).strip(),'acceptedAnswer':{'@type':'Answer','text':re.sub(r'\s+',' ',a[0].text()).strip()}})
  if questions:page['@type']='FAQPage';page['mainEntity']=questions
 if index==2:
  page['potentialAction']={'@type':'ReserveAction','name':'Reserve storage' if english else 'Réserver un espace','target':absolute(EN[2] if english else FR[2])}
 return {'@context':'https://schema.org','@graph':graph}

def head(current,source,asset):
 english,index,(title,description)=page_data(current)
 canonical=absolute(current);fr=absolute(FR[index]);en=absolute(EN[index])
 locale='en_CA' if english else 'fr_CA';other='fr_CA' if english else 'en_CA'
 og=BASE+'/assets/site/og-'+('en' if english else 'fr')+'.png'
 h=f'''<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><meta name="description" content="{escape(description,quote=True)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<link rel="canonical" href="{canonical}"><link rel="alternate" hreflang="fr-CA" href="{fr}"><link rel="alternate" hreflang="en-CA" href="{en}"><link rel="alternate" hreflang="x-default" href="{fr}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Entrepôts 307"><meta property="og:locale" content="{locale}"><meta property="og:locale:alternate" content="{other}">
<meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{escape(description,quote=True)}"><meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}"><meta property="og:image:secure_url" content="{og}"><meta property="og:image:type" content="image/png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Entrepôts 307 — Cantley, Québec">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{escape(title,quote=True)}"><meta name="twitter:description" content="{escape(description,quote=True)}"><meta name="twitter:image" content="{og}"><meta name="twitter:image:alt" content="Entrepôts 307 — Cantley, Québec">
<meta name="theme-color" content="#080808"><meta name="application-name" content="Entrepôts 307"><meta name="apple-mobile-web-app-title" content="Entrepôts 307">
<link rel="icon" href="/favicon.ico" sizes="any"><link rel="icon" type="image/svg+xml" href="/assets/site/favicon.svg"><link rel="icon" type="image/png" sizes="32x32" href="/assets/site/favicon-32.png"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site/styles.css"><script src="/assets/site/site.js" defer></script>'''
 if index==0:h+='<link rel="preload" as="image" href="/assets/site/storage-dusk.webp" fetchpriority="high">'
 return h+json_script(structured(current,source))
