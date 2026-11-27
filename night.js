(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const root = document.documentElement; root.classList.add('js');
  try { if (document.cookie.indexOf('jagerDrunk=off') > -1) root.classList.add('no-drunk'); } catch (e) { }
  const toast = (t, ms = 2600) => { const el = $('#toast'); if (!el) return; el.textContent = t; el.classList.add('on'); clearTimeout(toast.t); toast.t = setTimeout(() => el.classList.remove('on'), ms); };

  /* reveal */
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: .12 });
  $$('.rv').forEach(el => io.observe(el));

  /* nav, progress, HUD clock */
  const nav = $('#nav'), prog = $('#prog'), clk = $('#clock'), orb = $('#orb');
  const upd = () => {
    const h = document.documentElement.scrollHeight - innerHeight, p = h > 0 ? Math.min(1, scrollY / h) : 0;
    if (nav) nav.classList.toggle('scrolled', scrollY > 30);
    if (prog) prog.style.transform = `scaleX(${p})`;
    if (clk) { const m = Math.round(21 * 60 + p * 720) % 1440; clk.textContent = String(Math.floor(m / 60)).padStart(2, '0') + ':' + String(m % 60).padStart(2, '0'); if (orb) orb.classList.toggle('sun', m >= 6 * 60 + 30 && m < 12 * 60); }
  };
  addEventListener('scroll', upd, { passive: true }); upd();
  const burger = $('#burger'); if (burger) burger.addEventListener('click', () => { const o = nav.classList.toggle('open'); burger.setAttribute('aria-expanded', o); });
  $$('#menu a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));

  /* language (UI only) */
  const lb = $('#langBtn'), ll = $('#langList');
  if (lb) {
    const close = () => { ll.hidden = true; lb.setAttribute('aria-expanded', 'false'); };
    lb.addEventListener('click', e => { e.stopPropagation(); ll.hidden = !ll.hidden; lb.setAttribute('aria-expanded', String(!ll.hidden)); });
    document.addEventListener('click', e => { if (!ll.contains(e.target)) close(); });
    addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    ll.addEventListener('click', e => { const b = e.target.closest('button[data-lang]'); if (!b) return; $$('button', ll).forEach(x => x.removeAttribute('aria-selected')); b.setAttribute('aria-selected', 'true'); close(); toast(b.dataset.lang === 'English' ? 'English it is. Classic.' : `Jager is still learning ${b.dataset.lang}. For now: English, sober and slightly sarcastic.`, 3400); });
  }
  const fl = $('#footLang'); if (fl && lb) fl.addEventListener('click', () => { scrollTo({ top: 0, behavior: 'smooth' }); setTimeout(() => lb.click(), 500); });

  /* drunk text */
  $$('.drunk').forEach(el => { el.setAttribute('tabindex', '0'); el.title = 'Tap to sober up'; const s = () => { if (!el.classList.contains('sober')) { el.classList.add('sober'); if (!s.once) { s.once = 1; toast('Focused. Tap any blurry text to read it.'); } } }; el.addEventListener('click', s); el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); s(); } }); });
  const dt = $('#drunkToggle');
  if (dt) { const paint = () => { const on = !root.classList.contains('no-drunk'); dt.setAttribute('aria-pressed', on); $('b', dt).textContent = on ? 'ON' : 'OFF'; }; dt.addEventListener('click', () => { const off = root.classList.toggle('no-drunk'); document.cookie = 'jagerDrunk=' + (off ? 'off' : 'on') + ';path=/;max-age=31536000;SameSite=Lax'; paint(); toast(off ? 'Drunk mode off. Everything is sharp.' : 'Drunk mode on. Squint.'); }); paint(); }

  /* hero word rotator */
  const rot = $('#rot'); if (rot) { const L = rot.dataset.list.split('|'); let i = 0; setInterval(() => { i = (i + 1) % L.length; rot.textContent = L[i]; }, 2600); }

  /* story */
  const boot = () => {
    const J = window.JagerChat; if (!J) return; const sleep = J.sleep;
    const story = $('#story'); if (!story) return;
    const stage = $('#stage'), chat = $('#stChat')._api, feed = $('#stFeed'), fck = $('#fcClock');
    const chaps = $$('.chap', story);
    const post = (t, p, x, cls) => { const d = document.createElement('div'); d.className = 'fp' + (cls ? ' ' + cls : ''); d.innerHTML = '<b></b><span></span><em></em>'; $('b', d).textContent = p; $('span', d).textContent = x; $('em', d).textContent = t; feed.prepend(d); return d; };
    const S = {
      1: async ok => { chat.clear(); chat.setNow(21, 0); feed.innerHTML = ''; chat.sys('Setup');
        await sleep(500); if (!ok()) return;
        await chat.say('Hey, I just woke up on your machine.\nZernio: 5 accounts connected.\nBrain: OpenRouter, ready.\nTalking to you on ' + (J.channel === 'telegram' ? 'Telegram' : 'WhatsApp') + '.', 1200); if (!ok()) return;
        await sleep(900); if (!ok()) return;
        await chat.say('Weekly reminder: which day?', 800, ['Sunday', 'Monday', 'Daily']); if (!ok()) return;
        await sleep(1700); if (!ok()) return; chat.add('me', 'Sunday'); await sleep(400);
        await chat.say('Sunday 10:00. I send you what you posted and what people said. You reply, I act.', 1000); },
      2: async ok => { chat.clear(); chat.setNow(23, 30); feed.innerHTML = ''; chat.sys('Friday');
        await sleep(500); if (!ok()) return;
        chat.add('me', "going out. delete everything I post in the next 10 hours, 1 hour after"); await sleep(500);
        await chat.say('Night sprint on.\nUntil Saturday 09:30, every post is deleted 1 hour after you send it. Like your own post to keep it. I will stay quiet.', 1200, ['stop']); },
      3: async ok => { chat.clear(); chat.setNow(2, 0); feed.innerHTML = ''; fck.textContent = 'Sat 00:00'; chat.sys('Night sprint running');
        const P = [['00:20', 'X', 'hot take: cereal is soup', 1], ['01:05', 'LinkedIn', 'Honoured to announce my boss is wrong', 1], ['01:50', 'Instagram', 'dog in a tiny hat', 0], ['03:05', 'Threads', 'does anyone know a kebab shop', 1]]; const el = [];
        for (const [t, p, x, d] of P) { await sleep(950); if (!ok()) return; fck.textContent = 'Sat ' + t; el.push([post(t + (d ? '' : ' ♥'), p, x, d ? '' : 'kept'), d]); }
        await sleep(900); if (!ok()) return;
        for (const [e, d] of el) { if (!d) continue; await sleep(600); if (!ok()) return; e.classList.add('gone'); }
        await sleep(500); if (!ok()) return; chat.sys('Jager worked quietly all night'); },
      4: async ok => { chat.clear(); chat.setNow(3, 30); feed.innerHTML = ''; fck.textContent = 'Sat 03:30'; chat.sys('Comment sprint');
        chat.add('me', 'start a comment sprint'); await sleep(500); if (!ok()) return;
        await chat.say('3 new public comments.\n1. [Instagram] @maria: "where did you get this??"\n   draft: "Link in my bio!"\n2. [X] @troll99: "ratio"\n3. [YouTube] @sam: "great video, thanks"', 1300, ['send 1', 'hide 2', 'send 3']); if (!ok()) return;
        await sleep(1900); if (!ok()) return; chat.add('me', 'send 1, hide 2, send 3'); await sleep(400);
        await chat.say('Done. 2 replies sent, 1 comment hidden. Inbox zero.', 900); },
      5: async ok => { chat.clear(); chat.setNow(9, 0); feed.innerHTML = ''; chat.sys('Sunday, 10:00');
        await sleep(400); if (!ok()) return;
        await chat.say('Weekly reminder. You posted 3 things:\n1. [X] cereal is soup, round 2\n2. [Instagram] dog in a tiny hat ♥\n3. [Bluesky] i miss my ex\n\nReply "delete 1 3" or "keep all".', 1300, ['delete 1 3', 'keep all']); if (!ok()) return;
        await sleep(1800); if (!ok()) return; chat.add('me', 'delete 1 3'); await sleep(400);
        await chat.say('Delete 2 posts (1, 3) for good? Reply YES.', 800, ['YES', 'No']); if (!ok()) return;
        await sleep(1300); if (!ok()) return; chat.add('me', 'YES'); await sleep(400);
        await chat.say('Done. 2 posts gone. Your timeline is clean. Go touch grass.', 900); }
    };
    let active = 0, tok = 0;
    const go = n => { active = n; const my = ++tok; stage.dataset.s = n; chaps.forEach((c, i) => c.classList.toggle('on', i + 1 === n)); S[n](() => my === tok).catch(() => { }); };
    const o = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting && +e.target.dataset.n !== active) go(+e.target.dataset.n); }), { rootMargin: '-45% 0px -45% 0px' });
    chaps.forEach(c => o.observe(c));
    $$('.replay', story).forEach(b => b.addEventListener('click', () => go(+b.closest('.chap').dataset.n)));
    document.addEventListener('jager:channel', () => { if (active === 1) go(1); });
  };
  if (window.JagerChat) boot(); else document.addEventListener('jager:ready', boot);
})();
