(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const LANG = (document.documentElement.lang || 'en').slice(0, 2) === 'fr' ? 'fr' : 'en';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clock = (h, m) => String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0');
  const sleep = ms => new Promise(r => setTimeout(r, reduce ? Math.min(ms, 60) : ms));
  const U = { en: { post: ['post', 'posts'], comment: ['comment', 'comments'], minute: ['minute', 'minutes'], hour: ['hour', 'hours'], day: ['day', 'days'], week: ['week', 'weeks'], reply: ['reply', 'replies'] },
              fr: { post: ['publication', 'publications'], comment: ['commentaire', 'commentaires'], minute: ['minute', 'minutes'], hour: ['heure', 'heures'], day: ['jour', 'jours'], week: ['semaine', 'semaines'], reply: ['réponse', 'réponses'] } }[LANG];
  const plural = (n, w) => `${n} ${U[w][n === 1 || (LANG === 'fr' && n === 0) ? 0 : 1]}`;
  const D = { en: {
    sub: { whatsapp: 'online · probably judging you', telegram: 'bot · replies instantly' }, ph: { whatsapp: 'Message Jager…', telegram: 'Message Jager… (try /recap)' },
    fri: 'Friday', sat: 'Saturday', today: 'Today',
    a1: "hey jager, i'm going out. delete everything I post tonight, an hour after I post it",
    a2: "On it. Until 09:00 every post gets deleted 1h after you send it. Like your own post to keep it. Behave.",
    a3: "Morning. You posted 5 things last night.\n4 are gone. 1 survived: the dog in a tiny hat ♥\nWeekly reminder lands Sunday.",
    a4: 'what did i say to my boss??', a5: "Gone. You're welcome. We never speak of it.",
    posts: [['X', 'pineapple on pizza is a personality test and i failed it on purpose'], ['LinkedIn', 'Thrilled to announce I am at a kebab shop and have never been more aligned.'], ['Instagram', 'my dog in a tiny hat. no notes. ♥'], ['Threads', 'replying to my boss: bro we do NOT have synergy 😭'], ['Bluesky', "everyone i have ever dated is gonna see this and i'm fine with it"]],
    comments: [['Instagram', '@maria', 'where did you get this??', 'Link in my bio!'], ['X', '@troll99', 'ratio', ''], ['YouTube', '@sam', 'great video, thanks', 'Thanks Sam!']],
    kept: '  (kept ♥)', draft: 'draft',
    gone: (n, left) => `Done. ${plural(n, 'post')} gone for good. ${left ? left + ' left.' : 'Your timeline is spotless.'}`,
    cancelled: 'Cancelled. Nothing deleted. Coward.', stopped: 'Stopped. All sprints cancelled. You are on your own now.', nothing: 'Nothing was running. Quietly judging you anyway.',
    recapSet: w => `Done. Reminders are ${w} from now on. I'll message you what you posted and you tell me what to delete.`, daily: 'daily',
    nightWin: 'the night (until 09:00)', right: 'right away', after: l => l + ' after you post', after1: '1 hour after you post',
    sprintOn: (w, l) => `Night sprint on.\nFor the next ${w}, everything you post gets deleted ${l}.\nLike your own post to keep it. Say "stop" to cancel.`,
    none: "Nothing. You've been suspiciously well behaved.", listIntro: n => `You posted ${n}:`, listOutro: 'Reply "delete 2 4", "delete all" or "keep 1".',
    keepWhich: 'Keep which one? Give me a number from the list.', keptN: ids => `Kept ${ids}. Jager respects the confidence. ♥`,
    nothingLeft: 'Nothing left to delete.', which: "Which ones? Say a number, like “delete 2 and 4”, or ask me “what did I post?” first.", alreadyKept: 'Those are kept (you liked them). Say "delete 3 anyway" if you really mean it.',
    confirm: (n, ids) => `Delete ${plural(n, 'post')} (${ids}) for good? Reply YES to confirm.`, yes: 'YES', no: 'No',
    status: (r, rc) => r ? `Sprint on: next ${r.win}, deleting ${r.lag}.\nReminders: ${rc}.` : `No sprint running. Reminders: ${rc}.`, weeklyW: 'weekly', dailyW: 'daily',
    hi: 'Hey. Ask me "what did I post this week?" or start a comment sprint.', hiQ: ['what did I post this week?', 'start a comment sprint'],
    help: 'Try:\n• start a comment sprint\n• what did I post this week?\n• delete 2 and 4\n• delete everything I post in the next 8 hours, 1 hour after\n• send me a reminder every Sunday\n• stop',
    dunno: "I'm a simple buddy. Try “what did I post this week?”, “delete 2 and 4” or “delete everything I post in the next 8 hours”.",
    greet: "Hey, I'm Jager. Ask me what you posted, start a comment sprint or tell me what to delete. (Demo with fake posts.)", greetQ: ['what did I post this week?', 'start a comment sprint', 'delete everything I post in the next 8 hours, 1 hour after'],
    cs: (n, l) => `Comment sprint. ${plural(n, 'comment')} to deal with:\n${l}\n\nReply "send 1", "hide 2" or "delete 2".`, csQ: ['send 1', 'hide 2', 'send 3'],
    csDone: (o, left) => `Done: ${o}.${left ? ' ' + plural(left, 'comment') + ' left.' : ' Inbox zero.'}`, replied: u => `replied to ${u}`, skipped: u => `skipped ${u}`, hid: u => `hid ${u}`, deleted: u => `deleted ${u}`,
    tuU: { m: 'minute', h: 'hour', d: 'day', w: 'week' } },
  fr: {
    sub: { whatsapp: 'en ligne · te juge probablement', telegram: 'bot · répond tout de suite' }, ph: { whatsapp: 'Écris à Jager…', telegram: 'Écris à Jager… (essaie /recap)' },
    fri: 'Vendredi', sat: 'Samedi', today: "Aujourd'hui",
    a1: "salut jager, je sors. supprime tout ce que je poste ce soir, une heure après",
    a2: "Compris. Jusqu'à 09:00, chaque publication est supprimée 1 h après ton envoi. Aime ta propre publication pour la garder. Sois sage.",
    a3: "Bonjour. Tu as publié 5 choses cette nuit.\n4 ont disparu. 1 a survécu : le chien avec un petit chapeau ♥\nLe rappel hebdo arrive dimanche.",
    a4: "qu'est-ce que j'ai dit à mon boss ??", a5: "Supprimé. De rien. On n'en parlera jamais.",
    posts: [['X', "l'ananas sur la pizza est un test de personnalité et je l'ai raté exprès"], ['LinkedIn', "Ravi d'annoncer que je suis dans un kebab et que je n'ai jamais été aussi aligné."], ['Instagram', 'mon chien avec un petit chapeau. rien à ajouter. ♥'], ['Threads', 'réponse à mon boss : frère, on n’a PAS de synergie 😭'], ['Bluesky', "tous mes ex vont voir ça et ça me va très bien"]],
    comments: [['Instagram', '@maria', 'où tu as trouvé ça ??', 'Lien dans ma bio !'], ['X', '@troll99', 'ratio', ''], ['YouTube', '@sam', 'super vidéo, merci', 'Merci Sam !']],
    kept: '  (gardé ♥)', draft: 'brouillon',
    gone: (n, left) => `Fait. ${plural(n, 'post')} supprimée${n > 1 ? 's' : ''} pour de bon. ${left ? 'Il en reste ' + left + '.' : 'Ta timeline est impeccable.'}`,
    cancelled: 'Annulé. Rien de supprimé. Poule mouillée.', stopped: 'Arrêté. Tous les sprints sont annulés. Te voilà livré à toi-même.', nothing: "Rien n'était en cours. Je te juge en silence quand même.",
    recapSet: w => `C'est noté. Rappel ${w === 'daily' ? 'quotidien' : 'hebdomadaire'} dès maintenant. Je t'écris ce que tu as publié et tu me dis quoi supprimer.`, daily: 'daily',
    nightWin: 'la nuit (jusqu’à 09:00)', right: 'tout de suite', after: l => l + ' après ta publication', after1: '1 heure après ta publication',
    sprintOn: (w, l) => `Sprint de nuit lancé.\nPendant ${w}, tout ce que tu publies est supprimé ${l}.\nAime ta propre publication pour la garder. Dis « stop » pour annuler.`,
    none: "Rien. Tu as été étonnamment sage.", listIntro: n => `Tu as publié ${n} :`, listOutro: 'Réponds « supprime 2 4 », « supprime tout » ou « garde 1 ».',
    keepWhich: 'Garder lequel ? Donne-moi un numéro de la liste.', keptN: ids => `Gardé : ${ids}. Jager respecte la confiance. ♥`,
    nothingLeft: 'Plus rien à supprimer.', which: "Lesquels ? Donne un numéro, comme « supprime 2 et 4 », ou demande-moi d'abord « qu'est-ce que j'ai publié ? ».", alreadyKept: 'Ceux-là sont gardés (tu les as aimés). Dis « supprime 3 quand même » si tu es sûr.',
    confirm: (n, ids) => `Supprimer ${plural(n, 'post')} (${ids}) pour de bon ? Réponds OUI pour confirmer.`, yes: 'OUI', no: 'Non',
    status: (r, rc) => r ? `Sprint en cours : ${r.win} à venir, suppression ${r.lag}.\nRappels : ${rc}.` : `Aucun sprint en cours. Rappels : ${rc}.`, weeklyW: 'hebdomadaires', dailyW: 'quotidiens',
    hi: 'Salut. Demande-moi « qu\'est-ce que j\'ai publié cette semaine ? » ou lance un sprint commentaires.', hiQ: ["qu'est-ce que j'ai publié cette semaine ?", 'lance un sprint commentaires'],
    help: "Essaie :\n• lance un sprint commentaires\n• qu'est-ce que j'ai publié cette semaine ?\n• supprime 2 et 4\n• supprime tout ce que je publie dans les 8 prochaines heures, 1 heure après\n• rappelle-moi chaque dimanche\n• stop",
    dunno: "Je suis un buddy tout simple. Essaie « qu'est-ce que j'ai publié cette semaine ? », « supprime 2 et 4 » ou « supprime tout ce que je publie dans les 8 prochaines heures ».",
    greet: "Salut, moi c'est Jager. Demande-moi ce que tu as publié, lance un sprint commentaires ou dis-moi quoi supprimer. (Démo avec de fausses publications.)", greetQ: ["qu'est-ce que j'ai publié cette semaine ?", 'lance un sprint commentaires', 'supprime tout ce que je publie dans les 8 prochaines heures, 1 heure après'],
    cs: (n, l) => `Sprint commentaires. ${plural(n, 'comment')} à traiter :\n${l}\n\nRéponds « envoie 1 », « cache 2 » ou « supprime 2 ».`, csQ: ['envoie 1', 'cache 2', 'envoie 3'],
    csDone: (o, left) => `Fait : ${o}.${left ? ' Il en reste ' + left + '.' : ' Boîte de réception à zéro.'}`, replied: u => `réponse envoyée à ${u}`, skipped: u => `${u} ignoré`, hid: u => `${u} masqué`, deleted: u => `${u} supprimé`,
    tuU: { m: 'minute', h: 'hour', d: 'day', w: 'week' } } }[LANG];
  const chats = [];
  let currentCh = 'whatsapp';

  function makeChat(root) {
    const body = $('.c-body', root), form = $('.c-form', root), input = form && $('input', form);
    let now = [2, 14], token = 0, onQuick = null;
    const api = { root, body, form };
    const stamp = () => { now[1] += 1 + Math.floor(Math.random() * 2); if (now[1] > 59) { now[1] -= 60; now[0]++; } return clock(now[0], now[1]); };
    const scroll = () => { body.scrollTop = body.scrollHeight; };
    api.dropQuick = () => $$('.qr', body).forEach(q => q.remove());
    api.add = (who, text, t) => {
      api.dropQuick();
      const d = document.createElement('div'); d.className = 'b ' + who;
      d.innerHTML = '<span class="who"></span><span class="tx"></span><i></i>';
      $('.tx', d).textContent = text; $('i', d).textContent = t || stamp();
      body.appendChild(d); scroll(); return d;
    };
    api.sys = text => { const d = document.createElement('div'); d.className = 'b sys'; d.textContent = text; body.appendChild(d); scroll(); };
    api.typing = () => { const d = document.createElement('div'); d.className = 'typing'; d.innerHTML = '<span></span><span></span><span></span>'; body.appendChild(d); scroll(); return d; };
    api.quick = list => {
      api.dropQuick();
      const q = document.createElement('div'); q.className = 'qr';
      list.forEach(l => { const b = document.createElement('button'); b.type = 'button'; b.textContent = l; b.addEventListener('click', () => { if (onQuick) onQuick(l); }); q.appendChild(b); });
      body.appendChild(q); scroll();
    };
    api.setQuickHandler = f => { onQuick = f; };
    api.say = async (text, ms = 900, quick) => { const t = api.typing(); await sleep(ms); t.remove(); const d = api.add('jg', text); if (quick) api.quick(quick); return d; };
    api.clear = () => { body.innerHTML = ''; now = [2, 14]; };
    api.setNow = (h, m) => { now = [h, m]; };
    api.sleep = sleep;
    api.cancel = () => { token++; };
    api.newToken = () => ++token;

    async function auto() {
      const my = api.newToken(), ok = () => my === token;
      for (;;) {
        api.clear(); api.sys(D.fri);
        await sleep(700); if (!ok()) return;
        api.add('me', D.a1, '22:10'); await sleep(600); if (!ok()) return;
        let t = api.typing(); await sleep(1300); t.remove(); if (!ok()) return;
        api.add('jg', D.a2, '22:10'); await sleep(2200); if (!ok()) return;
        api.sys(D.sat); await sleep(900); if (!ok()) return;
        t = api.typing(); await sleep(1300); t.remove(); if (!ok()) return;
        api.add('jg', D.a3, '10:02'); await sleep(2300); if (!ok()) return;
        api.add('me', D.a4, '10:03'); await sleep(600); if (!ok()) return;
        t = api.typing(); await sleep(1100); t.remove(); if (!ok()) return;
        api.add('jg', D.a5, '10:03'); await sleep(6000); if (!ok()) return;
      }
    }

    if (form) {
      const state = { posts: [], comments: [], sprint: false, rule: null, recap: 'weekly', pending: null, started: false };
      const seed = () => { state.posts = D.posts.map((p, i) => ({ n: i + 1, p: p[0], t: p[1], kept: i === 2 })); };
      const seedC = () => { state.comments = D.comments.map((c, i) => ({ n: i + 1, p: c[0], u: c[1], t: c[2], d: c[3] })); };
      const clist = () => state.comments.map(x => `${x.n}. [${x.p}] ${x.u}: "${x.t}"${x.d ? `\n   ${D.draft}: "${x.d}"` : ''}`).join('\n');
      const list = () => state.posts.map(p => `${p.n}. [${p.p}] ${p.t}${p.kept ? D.kept : ''}`).join('\n');
      const nums = s => [...new Set((s.match(/\d+/g) || []).map(Number))].filter(n => state.posts.some(p => p.n === n));
      const dur = (v, u) => { u = (u || 'h')[0]; const n = +v; return plural(n, u === 'm' ? 'minute' : u === 'd' || u === 'j' ? 'day' : u === 'w' || u === 's' ? 'week' : 'hour'); };
      const say = api.say;
      const UNIT = '(minutes?|mins?|m|hours?|hrs?|heures?|h|days?|jours?|d|j|weeks?|semaines?|w|sem)';
      const DEL = '(delete|remove|wipe|burn|nuke|kill|supprime\\w*|efface\\w*|enl[eè]ve\\w*|vire\\w*)';
      async function reply(raw) {
        let s = raw.toLowerCase().trim().replace(/^\//, '').replace(/^start$/, 'hi').replace(/^rules$/, 'status');
        if (state.pending) {
          const p = state.pending;
          if (/^(y|yes|yep|yeah|do it|confirm|sure|ok|okay|oui|ouais|d'accord|carrément)\b/.test(s)) {
            state.pending = null;
            const gone = state.posts.filter(x => p.ids.includes(x.n)); state.posts = state.posts.filter(x => !p.ids.includes(x.n));
            return say(D.gone(gone.length, state.posts.length));
          }
          if (/^(n|no|nope|cancel|stop|wait|non|annule\w*|attends)\b/.test(s)) { state.pending = null; return say(D.cancelled); }
          state.pending = null;
        }
        if (state.sprint && /\b(send|reply|hide|delete|skip|envoie\w*|r[ée]ponds|cache\w*|masque\w*|supprime\w*|efface\w*|passe\w*)\b/.test(s) && !/\b(post|publi)/.test(s)) {
          const acts = [...s.matchAll(/(send|reply|hide|delete|skip|envoie\w*|r[ée]ponds|r[ée]pondre|cache\w*|masque\w*|supprime\w*|efface\w*|passe\w*)\s*((?:\d+[\s,and&et]*)+)/g)]; const out = [];
          acts.forEach(m => { const a = /^(send|reply|envoie|r[ée]pon)/.test(m[1]) ? 'send' : /^(hide|cache|masque)/.test(m[1]) ? 'hide' : /^(skip|passe)/.test(m[1]) ? 'skip' : 'delete';
            (m[2].match(/\d+/g) || []).forEach(d => { const x = state.comments.find(k => k.n === +d); if (x) { state.comments = state.comments.filter(k => k !== x); out.push(a === 'send' ? D.replied(x.u) : a === 'skip' ? D.skipped(x.u) : a === 'hide' ? D.hid(x.u) : D.deleted(x.u)); } }); });
          if (out.length) { if (!state.comments.length) state.sprint = false; return say(D.csDone(out.join(', '), state.comments.length)); }
        }
        if (/\bcomment|commentaire/.test(s) && /\b(sprint|inbox|triage|clear|new|show|what|bo[iî]te|trier|tri|nouveau|montre|affiche|lance\w*)\b/.test(s)) {
          seedC(); state.sprint = true; return say(D.cs(state.comments.length, clist()), 1200, D.csQ);
        }
        if (/\b(stop|panic|pause|cancel (all|rules?)|turn off|arr[eê]te\w*|annule\w* tout)\b/.test(s)) { const had = state.rule || state.sprint; state.rule = null; state.sprint = false; return say(had ? D.stopped : D.nothing); }
        if (/\b(recap|r[ée]cap|digest|remind|rappel\w*|summary|r[ée]sum[ée]|report)\b/.test(s) && /\b(every|daily|weekly|each|morning|sunday|monday|friday|chaque|quotidien|hebdo|matin|dimanche|lundi|vendredi|tous les)\b/.test(s) && !/what did|j'ai publi/.test(s)) {
          state.recap = /daily|every day|morning|each day|quotidien|tous les jours|matin/.test(s) ? 'daily' : 'weekly'; return say(D.recapSet(state.recap));
        }
        const rule = new RegExp('(next|for the|over the|prochaines?|pendant|dans les)\\s+(\\d+)\\s*' + UNIT + '\\b').exec(s);
        const tonight = /\b(tonight|this evening|till morning|ce soir|cette nuit)\b/.test(s);
        if (new RegExp('\\b' + DEL + '\\b').test(s) && (rule || tonight) && /\b(post|everything|anything|what i|tout|publi|ce que je)/.test(s)) {
          const after = new RegExp('(after|apr[èe]s)\\s+(\\d+)\\s*' + UNIT + '?').exec(s);
          const imm = /\b(right away|immediately|instantly|asap|tout de suite|imm[ée]diatement)\b/.test(s);
          const win = rule ? dur(rule[2], rule[3]) : D.nightWin;
          const lag = imm ? D.right : after ? D.after(dur(after[2], after[3] || 'h')) : D.after1;
          state.rule = { win, lag };
          return say(D.sprintOn(win, lag), 900, ['stop', 'status']);
        }
        if (/\b(what|show|list|tell|qu'est|quoi|montre\w*|affiche\w*|liste|dis)\b/.test(s) && /\b(post|said|wrote|did i|recap|this week|last night|today|publi|cette semaine|hier|aujourd)/.test(s) || /^(recap|r[ée]cap|list|liste|show|montre)\b/.test(s)) {
          if (!state.posts.length) return say(D.none);
          return say(`${D.listIntro(plural(state.posts.length, 'post'))}\n${list()}\n\n${D.listOutro}`, 1200, LANG === 'fr' ? ['supprime 2 4', 'supprime tout', 'garde 1'] : ['delete 2 4', 'delete all', 'keep 1']);
        }
        if (/\b(keep|garde\w*|conserve\w*)\b/.test(s)) {
          const ids = nums(s); if (!ids.length) return say(D.keepWhich);
          state.posts.forEach(x => { if (ids.includes(x.n)) x.kept = true; }); return say(D.keptN(ids.join(', ')));
        }
        if (new RegExp('\\b' + DEL + '\\b').test(s)) {
          if (!state.posts.length) return say(D.nothingLeft);
          let ids = /\b(all|everything|them all|tout|toutes|tous)\b/.test(s) ? state.posts.filter(x => !x.kept).map(x => x.n) : nums(s);
          if (!ids.length) return say(D.which);
          ids = ids.filter(n => !state.posts.find(x => x.n === n).kept);
          if (!ids.length) return say(D.alreadyKept);
          state.pending = { ids }; return say(D.confirm(ids.length, ids.join(', ')), 900, [D.yes, D.no]);
        }
        if (/\b(status|rules?|what are you doing|statut|r[èe]gles?)\b/.test(s)) return say(D.status(state.rule, state.recap === 'daily' ? D.dailyW : D.weeklyW));
        if (/\b(hi|hello|hey|yo|sup|salut|bonjour|coucou)\b/.test(s)) return say(D.hi, 700, D.hiQ);
        if (/\b(help|aide)\b|\?/.test(s) && s.length < 12 || s.length < 3) return say(D.help);
        return say(D.dunno);
      }
      let busy = false;
      async function send(text) {
        if (busy || !text.trim()) return; busy = true; api.cancel();
        if (!state.started) { state.started = true; seed(); api.clear(); api.sys(D.today); }
        api.add('me', text.trim()); input.value = '';
        await sleep(300); await reply(text); busy = false;
      }
      api.send = send; root._send = send;
      api.setQuickHandler(l => send(l));
      form.addEventListener('submit', e => { e.preventDefault(); send(input.value); });
      const greet = async () => { api.clear(); state.started = false; state.pending = null; state.rule = null; state.sprint = false; seed(); api.sys(D.today); await say(D.greet, 500, D.greetQ); state.started = true; };
      greet(); root._reset = greet;
    } else if (root.dataset.auto === '1') auto();
    api.auto = auto; root._api = api;
    $$('.c-tabs button', root).forEach(b => b.addEventListener('click', () => setChannel(b.dataset.ch)));
    chats.push(api);
    return api;
  }

  function setChannel(ch) {
    currentCh = ch;
    chats.forEach(api => {
      const root = api.root; root.dataset.ch = ch;
      $$('.c-tabs button', root).forEach(x => x.setAttribute('aria-selected', String(x.dataset.ch === ch)));
      const sub = $('.c-sub', root); if (sub) sub.textContent = D.sub[ch];
      const inp = $('.c-form input', root); if (inp) inp.placeholder = D.ph[ch];
      if (root.dataset.auto === '1' && !api.form) api.auto();
    });
    $$('.c-tabs button').forEach(x => x.setAttribute('aria-selected', String(x.dataset.ch === ch)));
    document.dispatchEvent(new CustomEvent('jager:channel', { detail: ch }));
  }
  window.JagerChat = { makeChat, sleep, setChannel, D, LANG, get channel() { return currentCh; }, chats };
  $$('.chat').forEach(makeChat);
  $$('.c-tabs button').forEach(b => { if (!b.closest('.chat')) b.addEventListener('click', () => setChannel(b.dataset.ch)); });
  $$('#ideas button').forEach(b => b.addEventListener('click', () => { const c = $('#tryChat'); c && c._send && c._send(b.textContent); }));
  document.dispatchEvent(new Event('jager:ready'));
})();
