import os
exec(open('/home/user/workspace/build_base_v4.py').read().split("PAGES=")[0])  # live, soon, LANGS, langs()
OUT='/home/user/workspace/v6'
GH='https://github.com/paulfxyz'
def w(n,h): open(os.path.join(OUT,n),'w').write(h)
def chatbox(id,auto=False,interactive=False,ch='whatsapp',tabs=False):
    tb=''
    if tabs: tb='<div class="c-tabs" role="tablist" aria-label="Channel">'+''.join(f'<button type="button" role="tab" data-ch="{k}" aria-selected="{str(ch==k).lower()}">{n}</button>' for k,n in [('whatsapp','WhatsApp'),('telegram','Telegram')])+'</div>'
    form=(f'<form class="c-form" autocomplete="off"><label class="sr" for="{id}In">Message Jager</label><input id="{id}In" type="text" maxlength="160" placeholder="Message Jager…"><button type="submit" aria-label="Send">➤</button></form>') if interactive else ''
    return f'<div class="chat" id="{id}" data-ch="{ch}" data-auto="{1 if auto else 0}"><div class="c-top"><span class="av">J</span><div class="c-who"><b>Jager</b><small class="c-sub">online · probably judging you</small></div>{tb}</div><div class="c-body" aria-live="polite"></div>{form}</div>'
TABS='<div class="c-tabs" role="tablist" aria-label="Channel"><button type="button" role="tab" data-ch="whatsapp" aria-selected="true">WhatsApp</button><button type="button" role="tab" data-ch="telegram" aria-selected="false">Telegram</button></div>'
GHI='<img src="assets/icons/github.svg" alt="" width="20" height="20" style="filter:none">'
def head(title,desc,page,body=''):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><meta name="theme-color" content="#07061a">
<link rel="canonical" href="https://jager.social/{'' if page=='index.html' else page}"><link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="Jager"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:image" content="https://jager.social/og.png"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="assets/fonts/BricolageGrotesque-800-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="fonts.css"><link rel="stylesheet" href="night.css"></head>
<body class="{body}"><script>document.documentElement.classList.add('js')</script><div class="prog" id="prog"></div>
<div class="hud" aria-hidden="true"><div class="orb" id="orb"></div><div class="clock" id="clock">21:00</div></div>
'''
def nav(active=''):
    items=[("index.html#night","The night"),("index.html#try","Try it"),("setup.html","Setup"),("index.html#faq","FAQ")]
    links=''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==active else ""}>{t}</a></li>' for h,t in items)
    return f'''<header class="nav" id="nav"><div class="wrap in"><a class="logo" href="index.html" aria-label="Jager home">jager<i>.</i></a>
<ul id="menu">{links}<li class="only-m"><a href="{GH}" rel="noopener">GitHub</a></li></ul>
<div class="lang"><button class="lang-btn" id="langBtn" type="button" aria-haspopup="listbox" aria-expanded="false" aria-label="Choose language">🌐 <span>EN</span></button><ul class="lang-list" id="langList" role="listbox" hidden>{langs()}</ul></div>
<span class="mit mono">MIT</span><a class="btn" href="{GH}" rel="noopener">{GHI} GitHub</a>
<button class="burger" id="burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span></button></div></header>'''
FOOT=f'''<footer class="foot"><div class="wrap">
<div class="sf-pitch"><div><span class="sf-pill mono"><b></b> Free · open source · MIT</span>
<h2 class="sf-title">Last call.<br><span class="serif">Clean timeline.</span></h2>
<p class="sf-sub">Jager is a free, MIT-licensed buddy for your public comments and posts. Bring a Zernio key. Chat on WhatsApp or Telegram.</p>
<div class="sf-cta"><a class="btn btn--pink btn--lg" href="{GH}" rel="noopener">{GHI} View on GitHub →</a><a class="sf-ask" href="mailto:ask@jager.social">ask@jager.social</a></div></div>
<nav class="sf-cols" aria-label="Footer">
<div><h4 class="mono">Project</h4><a href="index.html#night">The night</a><a href="index.html#try">Try it</a><a href="setup.html">Setup guide</a><a href="index.html#faq">FAQ</a></div>
<div><h4 class="mono">Built on</h4><a href="https://zernio.com" rel="noopener">Zernio</a><a href="https://openrouter.ai" rel="noopener">OpenRouter</a><a href="https://runware.ai" rel="noopener">Runware</a></div>
<div><h4 class="mono">Open source</h4><a href="{GH}" rel="noopener">GitHub</a><a href="setup.html#license">MIT license</a><a href="setup.html#contribute">Contribute</a></div>
<div><h4 class="mono">Say hello</h4><a href="mailto:ask@jager.social">Contact</a><button type="button" id="footLang">Languages</button><a href="https://iris.online" rel="noopener">Iris</a><a href="https://digital.spot" rel="noopener">Digital Spot</a></div></nav></div>
<div class="sf-word" aria-hidden="true">Jager</div>
<div class="sf-legal"><a class="logo" href="index.html">jager<i>.</i></a>
<ul class="sf-facts"><li>© 2026 Enki Ltd. Released under the MIT License</li><li>Company number 2067348138</li><li>14 Antim I Street, fl. 1 &amp; 2, Sofia, Bulgaria</li><li><a href="mailto:ask@jager.social">ask@jager.social</a></li><li><button type="button" class="dtoggle mono" id="drunkToggle" aria-pressed="true">Drunk mode: <b>ON</b></button></li></ul>
<p class="sf-note">Jager is a sister project of <a href="https://iris.online" rel="noopener">Iris</a> and <a href="https://digital.spot" rel="noopener">Digital Spot</a>, which are made by Enki Ltd. The software is provided as is, without warranty. Brand names and logos belong to their owners; no endorsement is implied. Not affiliated with Jägermeister, Zernio, WhatsApp, Telegram or Meta. Please drink and post responsibly.</p></div>
</div></footer><div class="toast" id="toast" role="status" aria-live="polite"></div>
<script src="chat.js" defer></script><script src="night.js" defer></script></body></html>'''
ROT='|'.join(["texting your ex","quote-tweeting your boss","rating a kebab shop one star","commenting “marry me” on a stranger's dog","a LinkedIn post about synergy at 3 AM"])
tick='<div class="tick" aria-hidden="true"><div class="tr">'+('<div>'+''.join(f'<span>{t}</span>' for t in ["Free","MIT licensed","Bring your own keys","WhatsApp","Telegram","Weekly sprints","No signup","Open source"])+'</div>')*4+'</div></div>'
logos=''.join(f'<span class="lg"><img src="assets/icons/{k}.svg" alt="{n}"></span>' for k,n,_,_ in live)
def chap(n,t,hh,p,m): return f'<article class="chap" data-n="{n}"><div class="hh">{hh}</div><h3>{t}</h3><p class="drunk">{p}</p><details class="more"><summary>More details</summary><p>{m}</p></details><button class="replay mono" type="button">↻ replay</button></article>'
chaps=''.join([
chap(1,'Plug in the keys','21:00','Paste a Zernio key and an AI key. Your accounts and your WhatsApp number or Telegram bot come with them. Jager says hi.','Zernio holds the connections to each platform. OpenRouter is the brain. Runware is optional, for image jobs. Jager never sees a password.'),
chap(2,'Start a night sprint','23:30','Heading out? Say "delete everything I post in the next 10 hours, 1 hour after". That is the whole setup.','Say "stop" and the sprint ends at once. Hours or days, you choose.'),
chap(3,'Go be a menace','02:00','You post. Each post gets a timer and disappears when it runs out. Jager stays quiet, no 3 AM buzzing.','Like your own post to keep it. Where a platform does not let apps delete posts, Jager clears comments and replies and tells you what it could not remove.'),
chap(4,'Clear the comments','03:30','Start a comment sprint. Jager serves public comments one by one with a draft reply. Answer with a word.','Replies are drafted by the AI model you picked and are never sent without your OK.'),
chap(5,'The morning after','09:00','Once a week, Jager lists what you posted and what people said. Reply "delete 1 3", say YES, done.','Reminders never delete anything on their own and big deletes always ask first.')])
faq=[("Is Jager really free?","Yes. It is open source under the MIT license. You only pay the providers whose keys you bring, such as Zernio and your AI provider."),
("Do I need an account with you?","No. There is nothing to sign up for. You run Jager yourself and nothing passes through our servers."),
("What do I need to run it?","A Zernio API key with your channels connected, an OpenRouter key (or Runware for image jobs), and any machine that can stay on: a laptop, a small server or a Raspberry Pi."),
("How do I talk to Jager?","On WhatsApp or Telegram, through a number or bot you set up in Zernio. Buttons and plain words both work."),
("What is a sprint?","A time-boxed job you start with a sentence. A night sprint deletes what you post after a delay. A comment sprint clears your inbox with draft replies. A launch sprint watches a post for a couple of days. A cleanup sprint reviews old posts."),
("Will Jager delete things without asking?","Only inside a sprint you started. Weekly reminders never delete anything on their own and big deletes always ask first."),
("Can Jager delete every post on every platform?","It can do what each platform's API allows. On some platforms, such as Instagram and TikTok, apps can only manage comments and replies. Jager tells you what it could and could not remove."),
("Who sees my data?","Your server, Zernio and the AI provider you choose. Jager itself collects nothing. Read the code to check."),
("Can I contribute?","Please do. Open an issue or a pull request on GitHub."),
("Is this affiliated with Jägermeister, Zernio, WhatsApp or Telegram?","No to all of them. Jägermeister is just a pun, and a very on-brand one.")]
idx=head("Jager — the free, open-source buddy for your public comments","Jager is a free, MIT-licensed buddy on WhatsApp or Telegram. Bring a Zernio key and an AI key. He handles your public comments, sends weekly reminders and runs sprints that clean up after you.","index.html","on-dark")+nav()+f'''<main>
<section class="hero on-dark"><div class="wrap grid"><div>
<div class="stickers"><span class="stk y">Free</span><span class="stk">MIT license</span><span class="stk p">0 servers of ours</span></div>
<h1><span class="f">Post drunk.</span><span class="o">Wake up</span><span class="s">clean.</span></h1>
<p class="sub drunk">Jager is a free, open-source buddy that lives in your WhatsApp or Telegram. He tells you what you posted, deals with your public comments and runs sprints that clean up after you.</p>
<p class="hint mono">↑ blurry? that's you at 2 AM. tap the text to focus.</p>
<div class="cta-row"><a class="btn btn--lg" href="{GH}" rel="noopener">{GHI} View on GitHub →</a><a class="btn btn--ghost btn--lg" href="#night">Watch the night</a></div>
<p class="micro mono">Tonight's mistake: <span id="rot" data-list="{ROT}">texting your ex</span></p></div>
<div class="hero-phone"><svg class="badge" viewBox="0 0 130 130" aria-hidden="true"><circle cx="65" cy="65" r="63" fill="#e4ff3a" stroke="#0d0b1f" stroke-width="3"/><defs><path id="cp" d="M65,65 m-47,0 a47,47 0 1,1 94,0 a47,47 0 1,1 -94,0"/></defs><text><textPath href="#cp" textLength="290" lengthAdjust="spacing">OPEN SOURCE ✦ MIT LICENSE ✦ FREE ✦</textPath></text><text x="65" y="74" text-anchor="middle" style="font-size:26px;letter-spacing:0">MIT</text></svg>
<div class="phone">{chatbox('heroChat',auto=True,tabs=True)}</div></div></div></section>
{tick}
<section class="sec story-sec on-dark" id="night"><div class="wrap">
<div class="eyebrow rv" style="color:var(--acid)">One night with Jager</div>
<h2 class="rv">From <span class="serif">sunset</span> to spotless.</h2>
<div class="chan-pick rv"><span class="mono">Preview on</span>{TABS}</div>
<div class="story" id="story"><div class="chaps">{chaps}</div>
<div class="stage" id="stage" data-s="1"><div class="stage-in"><div class="phone">{chatbox('stChat')}</div><div class="fcard"><div class="fc-top mono"><b>Your feed</b><span class="fc-clock" id="fcClock">Sat 00:00</span></div><div class="fc-list" id="stFeed"></div></div></div></div></div></div>
</div></section>
<section class="sec spr"><div class="wrap"><div class="eyebrow rv">Sprints</div><h2 class="rv">Say it once. <span class="serif">Jager does the rest.</span></h2>
<div class="sp-grid">
<article class="sp rv"><span class="mono tag">night sprint</span><h3>Delete after X</h3><blockquote>"Going out. Delete everything I post in the next 12 hours, 1 hour after."</blockquote><p>Every post gets a timer. Like your own post to keep it.</p></article>
<article class="sp rv" style="--d:.06s"><span class="mono tag">comment sprint</span><h3>Inbox zero in 10 min</h3><blockquote>"Comment sprint, 10 minutes."</blockquote><p>Comments one at a time with a draft reply. Send, hide, delete or skip.</p></article>
<article class="sp rv" style="--d:.12s"><span class="mono tag">launch sprint</span><h3>Watch a post for 48h</h3><blockquote>"Watch my launch post for two days."</blockquote><p>Jager pings you when real people comment and quietly hides the spam.</p></article>
<article class="sp rv" style="--d:.18s"><span class="mono tag">cleanup sprint</span><h3>Dig through the past</h3><blockquote>"Cleanup sprint: everything from 2023."</blockquote><p>Old posts in batches. You decide what stays.</p></article></div></div></section>
<section class="sec try" id="try"><div class="wrap try-grid"><div><div class="eyebrow rv">Fake data. Real commands.</div><h2 class="rv">Your turn. <span class="serif">Talk to him.</span></h2>
<p class="lead rv drunk" style="font-size:1.2rem;max-width:44ch">This runs in your browser with made-up posts and comments. Ask for a recap, start a comment sprint or set a night rule.</p>
<div class="chips rv" id="ideas"><button type="button">what did I post this week?</button><button type="button">start a comment sprint</button><button type="button">delete everything I post in the next 8 hours, 1 hour after</button><button type="button">delete 2 and 4</button></div></div>
<div class="rv"><div class="phone">{chatbox('tryChat',interactive=True,tabs=True)}</div></div></div></section>
<section class="sec cream" id="stack"><div class="wrap"><div class="eyebrow rv">The stack</div><h2 class="rv">Three keys. <span class="serif">That's the product.</span></h2>
<div class="keys"><div class="key rv"><span class="no">key 1</span><b>Zernio</b><p>Connect your accounts and a WhatsApp number or Telegram bot, then paste the API key.</p></div>
<div class="key rv" style="--d:.06s"><span class="no">key 2</span><b>OpenRouter</b><p>Any model you like for reading comments, drafting replies and understanding you.</p></div>
<div class="key rv" style="--d:.12s"><span class="no">key 3 · optional</span><b>Runware</b><p>For image jobs such as alt text, image checks or a picture to go with a reply.</p></div></div>
<div class="flow rv"><div class="nd"><b>Your accounts</b><span>X, Instagram, Facebook, LinkedIn, TikTok, YouTube, Threads, Bluesky</span></div><div class="ar">⇄</div><div class="nd"><b>Zernio</b><span>one API, plus your chat channel</span></div><div class="ar">⇄</div><div class="nd hot"><b>Jager</b><span>small MIT server you run</span></div><div class="ar">⇄</div><div class="nd"><b>OpenRouter / Runware</b><span>the brain</span></div></div>
<div class="logos rv">{logos}<span class="more-l mono">+ whatever Zernio connects</span></div></div></section>
<section class="sec oss on-dark"><div class="wrap oss-grid"><div><div class="mitbig rv">MIT</div><h2 class="rv">Take it. <span class="serif">Change it. Ship it.</span></h2>
<p class="drunk" style="font-size:1.2rem;max-width:44ch">No servers of ours in the middle. No account, no subscription, no data collected. Jager runs on your machine with your keys.</p>
<div class="cta-row rv" style="margin-top:20px"><a class="btn btn--lg" href="{GH}" rel="noopener">{GHI} View on GitHub →</a><a class="btn btn--ghost btn--lg" href="setup.html">Setup guide</a></div></div>
<div class="term rv"><div class="term-bar"><i></i><i></i><i></i><span class="mono">~/jager</span></div><pre>$ git clone github.com/paulfxyz/jager
$ cp .env.example .env
$ nano .env   <span class="c"># 3 keys, that's it</span>
$ docker compose up -d
<span class="g">✓ Jager is awake. Say hi on Telegram.</span></pre></div></div></section>
<section class="sec cream" id="faq"><div class="wrap"><div class="eyebrow rv">FAQ</div><h2 class="rv">Sober <span class="serif">questions.</span></h2>
<div class="faq rv">{''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q,a in faq)}</div></div></section>
<section class="closer"><div class="wrap"><h2 class="rv">Sober up, <span class="serif">cyber.</span></h2><p class="rv">Free. Open source. Yours to run.</p><a class="btn btn--lg rv" href="{GH}" rel="noopener">{GHI} View on GitHub →</a></div></section>
</main>'''+FOOT
w('index.html',idx)
def step(n,t,b): return f'<article class="stp rv"><div class="n">{n}</div><div><h3>{t}</h3>{b}</div></article>'
setup=head("Setup — Jager","Run Jager yourself in four steps: a Zernio key, an AI key, a WhatsApp number or Telegram bot, and one command. MIT licensed.","setup.html","on-dark")+nav('setup.html')+f'''<main><section class="phead on-dark"><div class="wrap"><div class="eyebrow" style="color:var(--acid)">Setup</div><h1>Four steps. <span class="serif">Then he's awake.</span></h1><p class="drunk">Jager is free and MIT licensed. You bring the keys and run it anywhere: a laptop, a Raspberry Pi or a small server.</p></div></section>
<section class="sec cream" style="padding-top:60px"><div class="wrap" style="max-width:960px"><div class="steps">
{step(1,'Get a Zernio key','<p>Create a Zernio workspace, connect the accounts Jager should look after, and create an API key. Zernio also gives you the channel Jager talks to you on.</p><p><a href="https://docs.zernio.com/quickstart.mdx" rel="noopener">Zernio quickstart</a> · <a href="https://docs.zernio.com/guides/connecting-accounts.mdx" rel="noopener">Connecting accounts</a></p>')}
{step(2,'Pick your channel','<div class="two"><div class="mini"><img src="assets/icons/whatsapp.svg" alt="" width="26" height="26"><b>WhatsApp</b><p>Add a WhatsApp number in Zernio. Messages from Jager and your replies flow through it.</p></div><div class="mini"><img src="assets/icons/telegram.svg" alt="" width="26" height="26"><b>Telegram</b><p>Create a bot with BotFather, connect it in Zernio, press Start. Buttons and slash commands work.</p></div></div><p><a href="https://docs.zernio.com/llms/platforms/telegram.txt" rel="noopener">Zernio Telegram docs</a></p>')}
{step(3,'Add an AI key','<p>Use <a href="https://openrouter.ai" rel="noopener">OpenRouter</a> for reading comments, drafting replies and understanding your messages. Add <a href="https://runware.ai" rel="noopener">Runware</a> for image jobs. Pick any model, cheap or clever.</p>')}
{step(4,'Run it','''<div class="term"><div class="term-bar"><i></i><i></i><i></i><span class="mono">.env</span></div><pre><span class="c"># the whole config</span>
ZERNIO_API_KEY=zk_...
OPENROUTER_API_KEY=sk-or-...
RUNWARE_API_KEY=            <span class="c"># optional</span>
JAGER_CHANNEL=telegram      <span class="c"># or whatsapp</span>
JAGER_MODEL=openai/gpt-4o-mini
JAGER_TIMEZONE=Europe/Lisbon
JAGER_RECAP=sunday 10:00</pre></div><div class="term" style="margin-top:14px"><div class="term-bar"><i></i><i></i><i></i><span class="mono">terminal</span></div><pre>$ git clone github.com/paulfxyz/jager
$ cd jager &amp;&amp; cp .env.example .env
$ docker compose up -d
<span class="g">✓ Jager is awake. Say hi on Telegram.</span></pre></div><p style="font-size:.85rem;margin-top:10px">Example config. Names follow the repository on <a href="'''+GH+f'''" rel="noopener">GitHub</a>.</p>''')}
</div>
<div class="note2"><h3>What does it cost?</h3><p>Jager is free. You pay your providers directly for what you use: Zernio for the connections and your AI provider for tokens. Check each provider's current pricing before you start.</p></div>
<div class="note2" id="license"><h3>MIT, plain and simple</h3><p>Use it, change it, sell it, host it for friends. Keep the copyright notice. The software is provided as is, without warranty.</p></div>
<div class="note2" id="contribute"><h3>Add a sprint, fix a bug, translate a joke</h3><p>Open an issue or a pull request on GitHub. Sprint ideas are especially welcome.</p><a class="btn btn--lg" href="{GH}" rel="noopener">{GHI} View on GitHub →</a></div>
</div></section>
<section class="closer"><div class="wrap"><h2>Sober up, <span class="serif">cyber.</span></h2><p>Free. Open source. Yours to run.</p><a class="btn btn--lg" href="{GH}" rel="noopener">{GHI} View on GitHub →</a></div></section></main>'''+FOOT
w('setup.html',setup)
nf=head("Page not found — Jager","This page does not exist.","404.html","on-dark").replace('<meta name="theme-color"','<meta name="robots" content="noindex"><meta name="theme-color"',1)+nav()+f'<main><section class="phead on-dark" style="min-height:70vh"><div class="wrap"><h1>Lost? <span class="serif">Classic.</span></h1><p>This page went home early.</p><a class="btn btn--lg" href="index.html">Back to Jager →</a></div></section></main>'+FOOT
w('404.html',nf)
print('built')
