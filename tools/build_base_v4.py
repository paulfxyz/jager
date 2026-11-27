import os
OUT='/home/user/workspace/jager'
live=[("x","X","Posts & replies",""),("instagram","Instagram","Comments & replies","*"),("facebook","Facebook","Posts & comments",""),("linkedin","LinkedIn","Posts & comments",""),("tiktok","TikTok","Comments & replies","*"),("youtube","YouTube","Videos & comments",""),("threads","Threads","Posts & replies",""),("bluesky","Bluesky","Posts & replies","")]
soon=[("reddit","Reddit"),("pinterest","Pinterest"),("discord","Discord"),("mastodon","Mastodon"),("tumblr","Tumblr"),("snapchat","Snapchat"),("twitch","Twitch chat"),("letterboxd","Letterboxd"),("strava","Strava"),("substack","Substack Notes"),("googlemaps","Google reviews")]

LANGS=["English","中文 (Mandarin)","हिन्दी","Español","Français","العربية","বাংলা","Português","Русский","اردو","Bahasa Indonesia","Deutsch","日本語","Naijá (Pidgin)","मराठी","తెలుగు","Türkçe","தமிழ்","Tiếng Việt","한국어","Italiano","ไทย","ગુજરાતી","فارسی","Polski","Українська","Kiswahili","粵語 (Cantonese)","Basa Jawa","ਪੰਜਾਬੀ","עברית"]
def langs():
    return ''.join(f'<li><button type="button" role="option" data-lang="{l}"{" aria-selected=\"true\"" if i==0 else ""}>{l}</button></li>' for i,l in enumerate(LANGS))

PAGES=[("how.html","How it works"),("channels.html","Channels"),("platforms.html","Platforms"),("pricing.html","Pricing"),("faq.html","FAQ")]

def head(title,desc,page):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#08170f">
<link rel="canonical" href="https://jager.social/{page if page!='index.html' else ''}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="Jager">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:url" content="https://jager.social/{page if page!='index.html' else ''}">
<meta property="og:image" content="https://jager.social/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/BricolageGrotesque-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="fonts.css"><link rel="stylesheet" href="styles.css">
</head>
<body>
<script>document.documentElement.classList.add('js');try{{if(document.cookie.indexOf('jagerDrunk=off')>-1)document.documentElement.classList.add('no-drunk')}}catch(e){{}}</script>
<div class="progress" id="progress" aria-hidden="true"></div>
'''

def nav(active=''):
    links=''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==active else ""}>{t}</a></li>' for h,t in PAGES)
    return f'''<header class="nav" id="nav"><div class="wrap in">
  <a class="logo" href="index.html" aria-label="Jager home">jager<i>.</i></a>
  <ul id="menu">{links}<li class="only-m"><a href="login.html">Log in</a></li></ul>
  <div class="lang" id="lang">
    <button class="lang-btn" id="langBtn" type="button" aria-haspopup="listbox" aria-expanded="false" aria-label="Choose language"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/></svg><span id="langCur">EN</span></button>
    <ul class="lang-list" id="langList" role="listbox" hidden>{langs()}</ul>
  </div>
  <a class="login" href="login.html">Log in</a>
  <a class="btn btn--amber" href="login.html">Get Jager</a>
  <button class="burger" id="burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
</div></header>
'''

FOOT='''<footer class="site-foot">
  <div class="wrap">
    <div class="sf-pitch">
      <div>
        <span class="sf-pill mono"><b></b> Waitlist open</span>
        <h2 class="sf-title">Post drunk.<br><span class="serif">Wake up clean.</span></h2>
        <p class="sf-sub">Jager is your buddy on WhatsApp, Telegram or email. $2 a month, billed $24 a year.</p>
        <div class="sf-cta"><a class="btn btn--amber btn--lg" href="login.html">Join the waitlist <span class="arr">→</span></a><a class="sf-ask" href="mailto:ask@jager.social">Ask us anything: ask@jager.social</a></div>
      </div>
      <nav class="sf-cols" aria-label="Footer">
        <div><h4 class="mono">Product</h4><a href="how.html">How it works</a><a href="how.html#demo">Live demo</a><a href="channels.html">Channels</a><a href="platforms.html">Platforms</a><a href="pricing.html">Pricing</a><a href="faq.html">FAQ</a></div>
        <div><h4 class="mono">Channels</h4><a href="channels.html#whatsapp">WhatsApp</a><a href="channels.html#telegram">Telegram</a><a href="channels.html#email">Email</a><a href="channels.html#soon">More coming soon</a></div>
        <div><h4 class="mono">Legal</h4><a href="terms.html">Terms</a><a href="privacy.html">Privacy</a><a href="cookies.html">Cookies</a><a href="gdpr.html">GDPR</a></div>
        <div><h4 class="mono">Say hello</h4><a href="mailto:ask@jager.social">Contact</a><button type="button" id="footLang">Languages</button><a href="login.html">Log in</a><a href="https://iris.online" rel="noopener">Iris</a><a href="https://digital.spot" rel="noopener">Digital Spot</a></div>
      </nav>
    </div>
    <div class="sf-word" aria-hidden="true">Jager</div>
    <div class="sf-legal">
      <a class="logo" href="index.html" aria-label="Jager home">jager<i>.</i></a>
      <ul class="sf-facts">
        <li>© 2026 Enki Ltd</li><li>Company number 2067348138</li><li>14 Antim I Street, fl. 1 &amp; 2, Sofia, Bulgaria</li><li><a href="mailto:ask@jager.social">ask@jager.social</a></li>
        <li><button type="button" class="dtoggle mono" id="drunkToggle" aria-pressed="true">Drunk mode: <b>ON</b></button></li>
      </ul>
      <p class="sf-note">Jager is a sister product of <a href="https://iris.online" rel="noopener">Iris</a> and <a href="https://digital.spot" rel="noopener">Digital Spot</a>, which are made by Enki Ltd. The app and customer service are in English only. Brand names and logos belong to their owners; no endorsement is implied. Not affiliated with Jägermeister, WhatsApp, Telegram or Meta. Please drink and post responsibly.</p>
    </div>
  </div>
</footer>
<dialog id="modal" aria-labelledby="mTitle">
  <div class="m-card">
    <button class="m-close" data-close aria-label="Close">×</button>
    <div class="emoji">🥃</div>
    <h3 id="mTitle">Thank you. <span class="serif">Coming soon.</span></h3>
    <p id="mBody">Jager isn't live yet, but you're on the list. We'll let you know the second the doors open.</p>
    <button class="btn btn--amber" data-close>Cheers</button>
  </div>
</dialog>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="app.js" defer></script><script src="fun.js" defer></script><script src="chat.js" defer></script><script src="demo.js" defer></script>
</body></html>'''

def phero(kicker,h1,lead):
    return f'''<section class="phero"><div class="wrap"><span class="kicker mono"><b></b> {kicker}</span><h1>{h1}</h1><p class="lead2 drunk" data-drunk>{lead}</p></div></section>'''

MARQ='''<div class="mq-wrap" aria-hidden="true"><div class="marquee"><div class="tr">'''+('<div style="display:flex">'+'<span>Text Jager</span><span>Reply DELETE</span><span>Your bouncer on WhatsApp</span><span>Telegram too</span><span>Email works too</span>'*2+'</div>')*2+'</div></div></div>'

def cta_close():
    return '''<section class="closer"><div class="wrap">
    <h2 class="rv">Sober up, <span class="serif">cyber.</span></h2>
    <p class="rv">Two dollars a month. Zero 2&nbsp;AM regrets.</p>
    <a class="btn btn--dark btn--lg rv" href="login.html">Get Jager <span class="arr">→</span></a>
  </div></section>'''

def platgrid():
    c=''.join(f'<li class="pc live rv" style="--d:{i*.04}s"><img src="assets/icons/{k}.svg" alt="" width="34" height="34"><div><div class="nm">{n}</div><div class="st">{s}{" *" if a else ""}</div></div></li>' for i,(k,n,s,a) in enumerate(live))
    c+=''.join(f'<li class="pc soon rv"><img src="assets/icons/{k}.svg" alt="" width="34" height="34"><div><div class="nm">{n}</div><div class="st">Coming soon</div></div></li>' for k,n in soon)
    c+='<li class="rv" style="display:contents"><button class="pc req" data-modal="platform" type="button"><span class="plus">+</span><span><span class="nm" style="display:block">Your platform missing?</span><span class="st" style="font-family:var(--f-mono);font-size:.66rem;text-transform:uppercase">Tell us</span></span></button></li>'
    return f'<ul class="pgrid" style="list-style:none;padding:0">{c}</ul>'

def receipt():
    return '''<div class="receipt rv">
      <h3>jager<i>.</i></h3><div class="cen">THE MORNING-AFTER PLAN</div><span class="stamp">NO REGRETS</span><hr>
      <div class="row"><span>Jager on WhatsApp, Telegram or email</span><span>✓</span></div>
      <div class="row"><span>Daily or weekly recaps</span><span>✓</span></div>
      <div class="row"><span>"Delete what I post" rules</span><span>✓</span></div>
      <div class="row"><span>Reply-to-delete</span><span>✓</span></div>
      <div class="row"><span>All launch platforms</span><span>✓</span></div>
      <div class="row"><span>Judgement</span><span>none</span></div>
      <hr><div class="tot"><span>$2<small>/mo</small></span><small>billed $24/yr</small></div>
      <a class="btn btn--amber" href="login.html">Get Jager <span class="arr">→</span></a>
      <div class="note2">Email code login. No password. No app.</div></div>'''

VS='''<div class="vs" id="vs"><div class="bar coffee"><span>A flat white</span><div class="b">≈ $4</div></div><div class="bar jager"><span>A month of Jager</span><div class="b">$2</div></div></div>'''

def w(name,html): open(os.path.join(OUT,name),'w').write(html)

