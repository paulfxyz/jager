(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clock = (h, m) => String(h).padStart(2, '0') + ':' + String(m).padStart(2, '0');
  const sleep = ms => new Promise(r => setTimeout(r, reduce ? Math.min(ms, 60) : ms));
  const plural = (n, w) => `${n} ${w}${n === 1 ? '' : 's'}`;
  const SUB = { whatsapp: 'online · probably judging you', telegram: 'bot · replies instantly', email: 'buddy@jager.social' };
  const PH = { whatsapp: 'Message Jager…', telegram: 'Message Jager… (try /recap)', email: 'Reply to Jager…' };
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
      $('.who', d).textContent = who === 'me' ? 'You wrote' : 'Jager wrote';
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
    api.alive = my => my === token;

    /* auto script (hero) */
    async function auto() {
      const my = api.newToken(), ok = () => my === token;
      for (;;) {
        api.clear(); api.sys('Friday');
        await sleep(700); if (!ok()) return;
        api.add('me', "hey jager, i'm going out. delete everything I post tonight, an hour after I post it", '22:10');
        await sleep(600); if (!ok()) return;
        let t = api.typing(); await sleep(1300); t.remove(); if (!ok()) return;
        api.add('jg', "On it. Until 09:00 every post gets deleted 1h after you send it. Like your own post to keep it. Behave.", '22:10');
        await sleep(2200); if (!ok()) return;
        api.sys('Saturday'); await sleep(900); if (!ok()) return;
        t = api.typing(); await sleep(1300); t.remove(); if (!ok()) return;
        api.add('jg', "Morning. You posted 5 things last night.\n4 are gone. 1 survived: the dog in a tiny hat ♥\nWeekly recap lands Sunday.", '10:02');
        await sleep(2300); if (!ok()) return;
        api.add('me', 'what did i say to my boss??', '10:03');
        await sleep(600); if (!ok()) return;
        t = api.typing(); await sleep(1100); t.remove(); if (!ok()) return;
        api.add('jg', "Gone. You're welcome. We never speak of it.", '10:03');
        await sleep(6000); if (!ok()) return;
      }
    }

    /* interactive brain */
    if (form) {
      const state = { posts: [], comments: [], sprint: false, rule: null, recap: 'weekly', pending: null, started: false };
      const seed = () => { state.posts = [
        { n: 1, p: 'X', t: 'pineapple on pizza is a personality test and i failed it on purpose' },
        { n: 2, p: 'LinkedIn', t: 'Thrilled to announce I am at a kebab shop and have never been more aligned.' },
        { n: 3, p: 'Instagram', t: 'my dog in a tiny hat. no notes. ♥', kept: true },
        { n: 4, p: 'Threads', t: 'replying to my boss: bro we do NOT have synergy 😭' },
        { n: 5, p: 'Bluesky', t: "everyone i have ever dated is gonna see this and i'm fine with it" }]; };
      const seedC = () => { state.comments = [{ n: 1, p: 'Instagram', u: '@maria', t: 'where did you get this??', d: 'Link in my bio!' }, { n: 2, p: 'X', u: '@troll99', t: 'ratio' }, { n: 3, p: 'YouTube', u: '@sam', t: 'great video, thanks', d: 'Thanks Sam!' }]; };
      const clist = () => state.comments.map(x => `${x.n}. [${x.p}] ${x.u}: "${x.t}"${x.d ? '\n   draft: "' + x.d + '"' : ''}`).join('\n');
      const list = () => state.posts.map(p => `${p.n}. [${p.p}] ${p.t}${p.kept ? '  (kept ♥)' : ''}`).join('\n');
      const nums = s => [...new Set((s.match(/\d+/g) || []).map(Number))].filter(n => state.posts.some(p => p.n === n));
      const dur = (v, u) => { u = (u || 'h')[0]; const n = +v; return u === 'm' ? plural(n, 'minute') : u === 'd' ? plural(n, 'day') : u === 'w' ? plural(n, 'week') : plural(n, 'hour'); };
      const say = api.say;
      async function reply(raw) {
        let s = raw.toLowerCase().trim().replace(/^\//, '').replace(/^start$/, 'hi').replace(/^rules$/, 'status');
        if (state.pending) {
          const p = state.pending;
          if (/^(y|yes|yep|yeah|do it|confirm|sure|ok|okay)\b/.test(s)) {
            state.pending = null;
            const gone = state.posts.filter(x => p.ids.includes(x.n)); state.posts = state.posts.filter(x => !p.ids.includes(x.n));
            return say(`Done. ${plural(gone.length, 'post')} gone for good. ${state.posts.length ? state.posts.length + ' left.' : 'Your timeline is spotless.'}`);
          }
          if (/^(n|no|nope|cancel|stop|wait)\b/.test(s)) { state.pending = null; return say('Cancelled. Nothing deleted. Coward.'); }
          state.pending = null;
        }
        if (/\bcomment/.test(s) && /\b(sprint|inbox|triage|clear|new|show|what)\b/.test(s)) {
          seedC(); state.sprint = true;
          return say(`Comment sprint. ${plural(state.comments.length, 'new public comment')}:\n${clist()}\n\nReply "send 1", "hide 2" or "delete 2".`, 1200, ['send 1', 'hide 2', 'send 3']);
        }
        if (state.sprint && /\b(send|reply|hide|delete|skip)\b/.test(s) && !/\bpost/.test(s)) {
          const acts = [...s.matchAll(/(send|reply|hide|delete|skip)\s*((?:\d+[\s,and&]*)+)/g)]; const out = [];
          acts.forEach(m => (m[2].match(/\d+/g) || []).forEach(d => { const x = state.comments.find(k => k.n === +d); if (x) { state.comments = state.comments.filter(k => k !== x); out.push((m[1] === 'send' || m[1] === 'reply') ? `replied to ${x.u}` : m[1] === 'skip' ? `skipped ${x.u}` : `${m[1] === 'hide' ? 'hid' : 'deleted'} ${x.u}`); } }));
          if (out.length) { if (!state.comments.length) state.sprint = false; return say(`Done: ${out.join(', ')}.${state.comments.length ? ' ' + plural(state.comments.length, 'comment') + ' left.' : ' Inbox zero.'}`); }
        }
        if (/\b(stop|panic|pause|cancel (all|rules?)|turn off)\b/.test(s)) { const had = state.rule; state.rule = null; return say(had ? 'Stopped. All rules cancelled. You are on your own now.' : 'Nothing was running. Quietly judging you anyway.'); }
        if (/\b(recap|digest|remind|summary|report)\b/.test(s) && /\b(every|daily|weekly|each|morning|sunday|monday|friday)\b/.test(s) && !/what did/.test(s)) {
          state.recap = /daily|every day|morning|each day/.test(s) ? 'daily' : 'weekly';
          return say(`Done. Recaps are ${state.recap} from now on. I'll message you what you posted and you tell me what to delete.`);
        }
        const rule = /(next|for the|over the)\s+(\d+)\s*(minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|w)\b/.exec(s);
        const tonight = /\b(tonight|this evening|till morning)\b/.test(s);
        if (/\b(delete|remove|wipe|clean)\b/.test(s) && (rule || tonight) && /\b(post|everything|anything|what i)/.test(s)) {
          const after = /after\s+(\d+)\s*(minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|w)?/.exec(s);
          const imm = /\b(right away|immediately|instantly|asap)\b/.test(s);
          const win = rule ? dur(rule[2], rule[3]) : 'the night (until 09:00)';
          const lag = imm ? 'right away' : after ? dur(after[1], after[2] || 'h') + ' after you post' : '1 hour after you post';
          state.rule = { win, lag };
          return say(`Got it.\nFor the next ${win}, everything you post gets deleted ${lag}.\nLike your own post to keep it. Say "stop" to cancel.`, 900, ['stop', 'status']);
        }
        if (/\b(what|show|list|tell)\b/.test(s) && /\b(post|said|wrote|did i|recap|this week|last night|today)\b/.test(s) || /^(recap|list|show)\b/.test(s)) {
          if (!state.posts.length) return say("Nothing. You've been suspiciously well behaved.");
          return say(`You posted ${state.posts.length} things:\n${list()}\n\nReply "delete 2 4", "delete all" or "keep 1".`, 1200, ['delete 2 4', 'delete all', 'keep 1']);
        }
        if (/\bkeep\b/.test(s)) {
          const ids = nums(s); if (!ids.length) return say('Keep which one? Give me a number from the recap.');
          state.posts.forEach(x => { if (ids.includes(x.n)) x.kept = true; });
          return say(`Kept ${ids.join(', ')}. Jager respects the confidence. ♥`);
        }
        if (/\b(delete|remove|wipe|burn|nuke|kill)\b/.test(s)) {
          if (!state.posts.length) return say('Nothing left to delete.');
          let ids = /\b(all|everything|them all)\b/.test(s) ? state.posts.filter(x => !x.kept).map(x => x.n) : nums(s);
          if (!ids.length) return say("Which ones? Say a number, like “delete 2 and 4”, or ask me “what did I post?” first.");
          ids = ids.filter(n => !state.posts.find(x => x.n === n).kept);
          if (!ids.length) return say('Those are kept (you liked them). Say "delete 3 anyway" if you really mean it.');
          state.pending = { ids };
          return say(`Delete ${plural(ids.length, 'post')} (${ids.join(', ')}) for good? Reply YES to confirm.`, 900, ['YES', 'No']);
        }
        if (/\b(status|rules?|what are you doing)\b/.test(s)) return say(state.rule ? `Rule on: next ${state.rule.win}, deleting ${state.rule.lag}.\nRecaps: ${state.recap}.` : `No rule running. Recaps: ${state.recap}.`);
        if (/\b(hi|hello|hey|yo|sup)\b/.test(s)) return say('Hey. Ask me "what did I post this week?" or tell me to delete things.', 700, ['what did I post this week?', 'delete everything I post in the next 8 hours']);
        if (/\b(help|\?)\b/.test(s) || s.length < 3) return say('Try:\n• start a comment sprint\n• what did I post this week?\n• delete 2 and 4\n• delete everything I post in the next 8 hours, 1 hour after\n• send me a recap every Sunday\n• stop');
        return say("I'm a simple buddy. Try “what did I post this week?”, “delete 2 and 4” or “delete everything I post in the next 8 hours”.");
      }
      let busy = false;
      async function send(text) {
        if (busy || !text.trim()) return; busy = true; api.cancel();
        if (!state.started) { state.started = true; seed(); api.clear(); api.sys('Today'); }
        api.add('me', text.trim()); input.value = '';
        await sleep(300); await reply(text); busy = false;
      }
      api.send = send; root._send = send;
      api.setQuickHandler(l => send(l));
      form.addEventListener('submit', e => { e.preventDefault(); send(input.value); });
      const greet = async () => { api.clear(); state.started = false; state.pending = null; state.rule = null; seed(); api.sys('Today'); await say("Hey, I'm Jager. Ask me what you posted, or tell me what to delete. (This is a demo with fake posts.)", 500, ['what did I post this week?', 'delete everything I post in the next 8 hours, 1 hour after']); state.started = true; };
      greet(); root._reset = greet;
    } else if (root.dataset.auto === '1') auto();
    api.auto = auto;
    root._api = api;
    $$('.c-tabs button', root).forEach(b => b.addEventListener('click', () => setChannel(b.dataset.ch)));
    chats.push(api);
    return api;
  }

  function setChannel(ch) {
    currentCh = ch;
    chats.forEach(api => {
      const root = api.root;
      if (root.dataset.lock) return;
      root.dataset.ch = ch;
      $$('.c-tabs button', root).forEach(x => x.setAttribute('aria-selected', String(x.dataset.ch === ch)));
      const sub = $('.c-sub', root); if (sub) sub.textContent = SUB[ch];
      const inp = $('.c-form input', root); if (inp) inp.placeholder = PH[ch];
      if (root.dataset.auto === '1' && !api.form) api.auto();
    });
    $$('.c-tabs button').forEach(x => x.setAttribute('aria-selected', String(x.dataset.ch === ch)));
    document.dispatchEvent(new CustomEvent('jager:channel', { detail: ch }));
  }

  window.JagerChat = { makeChat, sleep, setChannel, get channel() { return currentCh; }, chats };
  $$('.chat').forEach(makeChat);
  $$('.c-tabs button').forEach(b => { if (!b.closest('.chat')) b.addEventListener('click', () => setChannel(b.dataset.ch)); });
  $$('#ideas button').forEach(b => b.addEventListener('click', () => { const c = $('#tryChat'); c && c._send && c._send(b.textContent); }));
  document.dispatchEvent(new Event('jager:ready'));
})();
