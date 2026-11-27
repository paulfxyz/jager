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

  /* language */
  const FR = document.documentElement.lang === 'fr';
  const T = (en, fr) => FR ? fr : en;
  const lb = $('#langBtn'), ll = $('#langList');
  if (lb) {
    const close = () => { ll.hidden = true; lb.setAttribute('aria-expanded', 'false'); };
    lb.addEventListener('click', e => { e.stopPropagation(); ll.hidden = !ll.hidden; lb.setAttribute('aria-expanded', String(!ll.hidden)); });
    document.addEventListener('click', e => { if (!ll.contains(e.target)) close(); });
    addEventListener('keydown', e => { if (e.key === 'Escape') close(); });
    ll.addEventListener('click', e => { const b = e.target.closest('button[data-lang]'); if (!b) return; close(); toast(T('Not translated yet. Translations are welcome on GitHub.', 'Pas encore traduit. Les traductions sont bienvenues sur GitHub.'), 3400); });
  }
  const fl = $('#footLang'); if (fl && lb) fl.addEventListener('click', () => { scrollTo({ top: 0, behavior: 'smooth' }); setTimeout(() => lb.click(), 500); });

  /* Product Hunt countdown */
  const cds = $$('[data-cd]');
  if (cds.length) {
    const target = Date.UTC(2026, 11, 3, 8, 1, 0)   /* Product Hunt day starts 00:01 Pacific = 08:01 UTC */;
    const tick = () => { const d = Math.max(0, target - Date.now()); const v = [Math.floor(d / 864e5), Math.floor(d / 36e5) % 24, Math.floor(d / 6e4) % 60, Math.floor(d / 1e3) % 60];
      cds.forEach(c => $$('[data-u]', c).forEach((el, i) => el.textContent = String(v[i]).padStart(2, '0'))); };
    tick(); setInterval(tick, 1000);
  }

  /* drunk text */
  $$('.drunk').forEach(el => { el.setAttribute('tabindex', '0'); el.title = T('Tap to sober up', 'Touche pour dessoûler'); const s = () => { if (!el.classList.contains('sober')) { el.classList.add('sober'); if (!s.once) { s.once = 1; toast(T('Focused. Tap any blurry text to read it.', 'Net. Touche un texte flou pour le lire.')); } } }; el.addEventListener('click', s); el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); s(); } }); });
  const dt = $('#drunkToggle');
  if (dt) { const paint = () => { const on = !root.classList.contains('no-drunk'); dt.setAttribute('aria-pressed', on); $('b', dt).textContent = on ? 'ON' : 'OFF'; }; dt.addEventListener('click', () => { const off = root.classList.toggle('no-drunk'); document.cookie = 'jagerDrunk=' + (off ? 'off' : 'on') + ';path=/;max-age=31536000;SameSite=Lax'; paint(); toast(off ? T('Drunk mode off. Everything is sharp.', 'Mode ivre désactivé. Tout est net.') : T('Drunk mode on. Squint.', 'Mode ivre activé. Plisse les yeux.')); }); paint(); }

  /* hero word rotator */
  const rot = $('#rot'); if (rot) { const L = rot.dataset.list.split('|'); let i = 0; setInterval(() => { i = (i + 1) % L.length; rot.textContent = L[i]; }, 2600); }

  /* story */
  const boot = () => {
    const J = window.JagerChat; if (!J) return; const sleep = J.sleep;
    const story = $('#story'); if (!story) return;
    const stage = $('#stage'), chat = $('#stChat')._api, feed = $('#stFeed'), fck = $('#fcClock');
    const chaps = $$('.chap', story);
    const post = (t, p, x, cls) => { const d = document.createElement('div'); d.className = 'fp' + (cls ? ' ' + cls : ''); d.innerHTML = '<b></b><span></span><em></em>'; $('b', d).textContent = p; $('span', d).textContent = x; $('em', d).textContent = t; feed.prepend(d); return d; };
    const L = J.LANG;
    const X = { en: {
      sys1: 'Setup', hi: ch => 'Hey, I just woke up on your machine.\nZernio: 5 accounts connected.\nBrain: OpenRouter, ready.\nTalking to you on ' + ch + '.', day: 'Weekly reminder: which day?', dq: ['Sunday', 'Monday', 'Daily'], dme: 'Sunday', dok: 'Sunday 10:00. I send you what you posted and what people said. You reply, I act.',
      fri: 'Friday', sme: 'going out. delete everything I post in the next 10 hours, 1 hour after', son: 'Night sprint on.\nUntil Saturday 09:30, every post is deleted 1 hour after you send it. Like your own post to keep it. I will stay quiet.',
      run: 'Night sprint running', quiet: 'Jager worked quietly all night', P: [['00:20', 'X', 'hot take: cereal is soup', 1], ['01:05', 'LinkedIn', 'Honoured to announce my boss is wrong', 1], ['01:50', 'Instagram', 'dog in a tiny hat', 0], ['03:05', 'Threads', 'does anyone know a kebab shop', 1]], sat: 'Sat ', csys: 'Comment sprint', cme: 'start a comment sprint',
      cs: '3 new public comments.\n1. [Instagram] @maria: "where did you get this??"\n   draft: "Link in my bio!"\n2. [X] @troll99: "ratio"\n3. [YouTube] @sam: "great video, thanks"', csq: ['send 1', 'hide 2', 'send 3'], cme2: 'send 1, hide 2, send 3', cdone: 'Done. 2 replies sent, 1 comment hidden. Inbox zero.',
      sun: 'Sunday, 10:00', wk: 'Weekly reminder. You posted 3 things:\n1. [X] cereal is soup, round 2\n2. [Instagram] dog in a tiny hat ♥\n3. [Bluesky] i miss my ex\n\nReply "delete 1 3" or "keep all".', wq: ['delete 1 3', 'keep all'], wme: 'delete 1 3', wc: 'Delete 2 posts (1, 3) for good? Reply YES.', wcq: ['YES', 'No'], wy: 'YES', wd: 'Done. 2 posts gone. Your timeline is clean. Go touch grass.', wa: 'WhatsApp', ta: 'Telegram' },
    fr: {
      sys1: 'Installation', hi: ch => "Salut, je viens de me réveiller sur ta machine.\nZernio : 5 comptes connectés.\nCerveau : OpenRouter, prêt.\nJe te parle sur " + ch + '.', day: 'Rappel hebdo : quel jour ?', dq: ['Dimanche', 'Lundi', 'Chaque jour'], dme: 'Dimanche', dok: "Dimanche 10:00. Je t'envoie ce que tu as publié et ce que les gens ont dit. Tu réponds, j'agis.",
      fri: 'Vendredi', sme: 'je sors. supprime tout ce que je publie dans les 10 prochaines heures, 1 heure après', son: "Sprint de nuit lancé.\nJusqu'à samedi 09:30, chaque publication est supprimée 1 heure après ton envoi. Aime ta propre publication pour la garder. Je reste discret.",
      run: 'Sprint de nuit en cours', quiet: 'Jager a travaillé en silence toute la nuit', P: [['00:20', 'X', 'avis tranché : les céréales, c’est de la soupe', 1], ['01:05', 'LinkedIn', 'Fier d’annoncer que mon boss a tort', 1], ['01:50', 'Instagram', 'chien avec un petit chapeau', 0], ['03:05', 'Threads', 'quelqu’un connaît un kebab ouvert ?', 1]], sat: 'Sam ', csys: 'Sprint commentaires', cme: 'lance un sprint commentaires',
      cs: '3 nouveaux commentaires publics.\n1. [Instagram] @maria : « où tu as trouvé ça ?? »\n   brouillon : « Lien dans ma bio ! »\n2. [X] @troll99 : « ratio »\n3. [YouTube] @sam : « super vidéo, merci »', csq: ['envoie 1', 'cache 2', 'envoie 3'], cme2: 'envoie 1, cache 2, envoie 3', cdone: 'Fait. 2 réponses envoyées, 1 commentaire masqué. Boîte à zéro.',
      sun: 'Dimanche, 10:00', wk: 'Rappel hebdo. Tu as publié 3 choses :\n1. [X] les céréales, c’est de la soupe, saison 2\n2. [Instagram] chien avec un petit chapeau ♥\n3. [Bluesky] mon ex me manque\n\nRéponds « supprime 1 3 » ou « garde tout ».', wq: ['supprime 1 3', 'garde tout'], wme: 'supprime 1 3', wc: 'Supprimer 2 publications (1, 3) pour de bon ? Réponds OUI.', wcq: ['OUI', 'Non'], wy: 'OUI', wd: 'Fait. 2 publications supprimées. Ta timeline est propre. Va toucher de l’herbe.', wa: 'WhatsApp', ta: 'Telegram' } }[L];
    const S = {
      1: async ok => { chat.clear(); chat.setNow(21, 0); feed.innerHTML = ''; chat.sys(X.sys1);
        await sleep(500); if (!ok()) return;
        await chat.say(X.hi(J.channel === 'telegram' ? X.ta : X.wa), 1200); if (!ok()) return;
        await sleep(900); if (!ok()) return;
        await chat.say(X.day, 800, X.dq); if (!ok()) return;
        await sleep(1700); if (!ok()) return; chat.add('me', X.dme); await sleep(400);
        await chat.say(X.dok, 1000); },
      2: async ok => { chat.clear(); chat.setNow(23, 30); feed.innerHTML = ''; chat.sys(X.fri);
        await sleep(500); if (!ok()) return;
        chat.add('me', X.sme); await sleep(500);
        await chat.say(X.son, 1200, ['stop']); },
      3: async ok => { chat.clear(); chat.setNow(2, 0); feed.innerHTML = ''; fck.textContent = X.sat + '00:00'; chat.sys(X.run);
        const el = [];
        for (const [t, p, x, d] of X.P) { await sleep(950); if (!ok()) return; fck.textContent = X.sat + t; el.push([post(t + (d ? '' : ' ♥'), p, x, d ? '' : 'kept'), d]); }
        await sleep(900); if (!ok()) return;
        for (const [e, d] of el) { if (!d) continue; await sleep(600); if (!ok()) return; e.classList.add('gone'); }
        await sleep(500); if (!ok()) return; chat.sys(X.quiet); },
      4: async ok => { chat.clear(); chat.setNow(3, 30); feed.innerHTML = ''; fck.textContent = X.sat + '03:30'; chat.sys(X.csys);
        chat.add('me', X.cme); await sleep(500); if (!ok()) return;
        await chat.say(X.cs, 1300, X.csq); if (!ok()) return;
        await sleep(1900); if (!ok()) return; chat.add('me', X.cme2); await sleep(400);
        await chat.say(X.cdone, 900); },
      5: async ok => { chat.clear(); chat.setNow(9, 0); feed.innerHTML = ''; chat.sys(X.sun);
        await sleep(400); if (!ok()) return;
        await chat.say(X.wk, 1300, X.wq); if (!ok()) return;
        await sleep(1800); if (!ok()) return; chat.add('me', X.wme); await sleep(400);
        await chat.say(X.wc, 800, X.wcq); if (!ok()) return;
        await sleep(1300); if (!ok()) return; chat.add('me', X.wy); await sleep(400);
        await chat.say(X.wd, 900); }
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
