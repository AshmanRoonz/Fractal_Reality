// Server-rendered pages in the fractalreality.ca house style.
// Created: 2026-11-14

export function esc(s) {
  return String(s ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

export function timeAgo(unix) {
  const s = Math.max(1, Math.floor(Date.now() / 1000) - unix);
  if (s < 60) return 'just now';
  const m = Math.floor(s / 60); if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60); if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24); if (d < 30) return `${d}d ago`;
  const mo = Math.floor(d / 30); if (mo < 12) return `${mo}mo ago`;
  return `${Math.floor(mo / 12)}y ago`;
}

function avatar(name, url) {
  if (url) return `<img class="av" src="${esc(url)}" alt="" loading="lazy" referrerpolicy="no-referrer">`;
  const initial = (name || '?').trim().charAt(0).toUpperCase();
  return `<span class="av avi">${esc(initial)}</span>`;
}

const CSS = `
  :root {
    --ink-900:#0a0d14; --ink-800:#11141d; --ink-700:#141823;
    --rule:rgba(255,255,255,0.08);
    --fog-100:#e6e8ee; --fog-300:#a4abb8; --fog-500:#6b7180;
    --gold:#b8a060; --gold-bright:#d4b870; --violet:#8c7ad0;
    --glow-gold:rgba(184,160,96,0.22); --danger:#c77;
  }
  @media (prefers-color-scheme: light) {
    :root {
      --ink-900:#f6f3ea; --ink-800:#ffffff; --ink-700:#fbf9f3;
      --rule:rgba(60,50,20,0.14);
      --fog-100:#1d1f26; --fog-300:#4a4f5c; --fog-500:#7a7f8c;
      --gold:#8a7430; --gold-bright:#6e5b20; --violet:#5a4aa0;
      --glow-gold:rgba(138,116,48,0.18); --danger:#a44;
    }
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--ink-900); color:var(--fog-100); font-family:"EB Garamond",Georgia,serif;
         font-size:18px; line-height:1.65; -webkit-font-smoothing:antialiased; }
  a { color:var(--gold-bright); text-decoration:none; }
  a:hover { text-decoration:underline; }
  .sans { font-family:"Space Grotesk",system-ui,sans-serif; }

  header.top { border-bottom:1px solid var(--rule);
    background:radial-gradient(ellipse at 50% 0%, rgba(140,122,208,0.14), transparent 65%); }
  .bar { max-width:980px; margin:0 auto; padding:16px 20px; display:flex; align-items:center; gap:16px; flex-wrap:wrap; }
  .mark { font-size:22px; color:var(--gold-bright); text-decoration:none; }
  .mark:hover { text-decoration:none; }
  .site { font-family:"Space Grotesk",sans-serif; font-size:13px; letter-spacing:0.18em;
          text-transform:uppercase; color:var(--fog-100); }
  .site small { display:block; font-size:10px; letter-spacing:0.22em; color:var(--gold); margin-top:2px; }
  .spacer { flex:1; }
  .nav { display:flex; align-items:center; gap:14px; font-family:"Space Grotesk",sans-serif; font-size:13px; }
  .nav a { color:var(--fog-300); }
  .nav a:hover { color:var(--gold-bright); text-decoration:none; }
  .who { display:flex; align-items:center; gap:8px; color:var(--fog-300); font-size:13px; }

  main { max-width:980px; margin:0 auto; padding:28px 20px 70px; }
  h1 { font-weight:500; font-size:clamp(26px,4vw,38px); color:var(--gold-bright);
       text-shadow:0 0 36px var(--glow-gold); margin-bottom:6px; }
  .sub { font-style:italic; color:var(--fog-300); margin-bottom:26px; }

  .panel { background:var(--ink-800); border:1px solid var(--rule); border-radius:14px; overflow:hidden; }
  .panel + .panel, .sec { margin-top:26px; }
  .panel h2 { font-family:"Space Grotesk",sans-serif; font-size:12px; letter-spacing:0.2em;
      text-transform:uppercase; color:var(--gold); padding:14px 18px; border-bottom:1px solid var(--rule); font-weight:500; }

  .cat { display:block; padding:16px 18px; border-bottom:1px solid var(--rule); color:inherit; }
  .cat:last-child { border-bottom:0; }
  .cat:hover { background:var(--ink-700); text-decoration:none; }
  .cat .n { color:var(--gold-bright); font-size:19px; }
  .cat .d { color:var(--fog-300); font-size:16px; font-style:italic; }
  .cat .c { float:right; font-family:"Space Grotesk",sans-serif; font-size:12px; color:var(--fog-500); margin-top:4px; }

  .row { display:flex; gap:12px; align-items:baseline; padding:13px 18px; border-bottom:1px solid var(--rule); }
  .row:last-child { border-bottom:0; }
  .row .t { flex:1; min-width:0; }
  .row .t a { color:var(--fog-100); font-size:18px; }
  .row .t a:hover { color:var(--gold-bright); }
  .row .meta { font-family:"Space Grotesk",sans-serif; font-size:12px; color:var(--fog-500); white-space:nowrap; }
  .row .meta .cat-tag { color:var(--gold); }
  .lock { color:var(--fog-500); font-size:13px; }

  .av { width:30px; height:30px; border-radius:50%; object-fit:cover; flex:none; display:inline-flex;
        align-items:center; justify-content:center; vertical-align:middle; }
  .avi { background:var(--ink-700); border:1px solid var(--rule); color:var(--gold-bright);
         font-family:"Space Grotesk",sans-serif; font-size:14px; }

  .post { display:flex; gap:14px; padding:18px; border-bottom:1px solid var(--rule); }
  .post:last-child { border-bottom:0; }
  .post .body { flex:1; min-width:0; }
  .post .head { font-family:"Space Grotesk",sans-serif; font-size:12.5px; color:var(--fog-500); margin-bottom:6px; }
  .post .head .nm { color:var(--fog-100); font-size:13px; }
  .post .head .role { color:var(--gold); }
  .post .txt { white-space:pre-wrap; overflow-wrap:break-word; }
  .post .txt.gone { color:var(--fog-500); font-style:italic; }

  .btn { display:inline-block; font-family:"Space Grotesk",sans-serif; font-size:13px; letter-spacing:0.1em;
         text-transform:uppercase; color:var(--gold-bright); background:transparent;
         border:1px solid var(--gold); border-radius:8px; padding:9px 16px; cursor:pointer; }
  .btn:hover { background:var(--glow-gold); text-decoration:none; }
  .btn.quiet { border-color:var(--rule); color:var(--fog-300); }
  .btn.tiny { font-size:11px; padding:4px 9px; letter-spacing:0.08em; }
  .btn.danger { border-color:var(--danger); color:var(--danger); }

  form.stack { padding:18px; display:flex; flex-direction:column; gap:12px; }
  input[type=text], textarea, select {
    width:100%; background:var(--ink-700); color:var(--fog-100); border:1px solid var(--rule);
    border-radius:8px; padding:10px 12px; font-family:inherit; font-size:17px; }
  textarea { min-height:140px; resize:vertical; }
  input:focus, textarea:focus, select:focus { outline:none; border-color:var(--gold); }
  label { font-family:"Space Grotesk",sans-serif; font-size:12px; letter-spacing:0.14em;
          text-transform:uppercase; color:var(--fog-500); }
  .err { color:var(--danger); font-style:italic; padding:0 18px 14px; }
  .ok { color:var(--gold); font-style:italic; padding:0 18px 14px; }

  .providers { display:flex; flex-direction:column; gap:12px; padding:22px; max-width:380px; margin:0 auto; }
  .providers .btn { text-align:center; padding:12px 16px; }
  .invite { text-align:center; max-width:560px; margin:0 auto 26px; color:var(--fog-300); font-style:italic; font-size:19px; }
  .invite strong { color:var(--gold-bright); font-style:normal; font-weight:500; }

  .pager { display:flex; justify-content:space-between; margin-top:18px; font-family:"Space Grotesk",sans-serif; font-size:13px; }
  .crumb { font-family:"Space Grotesk",sans-serif; font-size:12px; letter-spacing:0.14em;
           text-transform:uppercase; color:var(--fog-500); margin-bottom:14px; }
  .crumb a { color:var(--fog-500); }
  .crumb a:hover { color:var(--gold-bright); }
  .actions { display:flex; gap:8px; align-items:center; flex-wrap:wrap; margin:14px 0; }
  .inline { display:inline; }

  footer { border-top:1px solid var(--rule); text-align:center; padding:26px 20px 44px;
           font-family:"Space Grotesk",sans-serif; font-size:12px; letter-spacing:0.12em; color:var(--fog-500); }
  footer a { color:var(--fog-500); }
  footer a:hover { color:var(--gold-bright); }
`;

export function layout({ title, user, content, description }) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${esc(title)}</title>
${description ? `<meta name="description" content="${esc(description)}">` : ''}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Space+Grotesk:wght@400;500;600&display=swap" rel="stylesheet">
<style>${CSS}</style>
</head>
<body>
<header class="top">
  <div class="bar">
    <a class="mark" href="/" aria-label="Forum home">&#8857;</a>
    <a href="/" class="site" style="text-decoration:none;">The Forum<small>fractalreality.ca</small></a>
    <div class="spacer"></div>
    <nav class="nav">
      <a href="/">Threads</a>
      <a href="/guidelines">Guidelines</a>
      <a href="https://fractalreality.ca" rel="noopener">Main site</a>
      ${user ? `
        <span class="who">${avatar(user.name, user.avatar_url)}<a href="/me">${esc(user.name)}</a></span>
        <form method="post" action="/logout" class="inline"><button class="btn quiet tiny" type="submit">Sign out</button></form>
      ` : `<a class="btn tiny" href="/login">Sign in</a>`}
    </nav>
  </div>
</header>
<main>
${content}
</main>
<footer>
  The Circumpunct Framework &middot; Parts are fractals of their wholes<br>
  <a href="https://fractalreality.ca">fractalreality.ca</a> &middot; <a href="/guidelines">Guidelines</a> &middot; <a href="https://fractalreality.ca/privacy.html">Privacy</a>
</footer>
</body>
</html>`;
}

function threadRow(t, { showCategory = true } = {}) {
  const replies = `${t.reply_count} ${t.reply_count === 1 ? 'reply' : 'replies'}`;
  return `<div class="row">
    <div class="t">${t.locked ? '<span class="lock">&#128274;</span> ' : ''}<a href="/t/${t.id}">${esc(t.title)}</a></div>
    <div class="meta">
      ${showCategory ? `<a class="cat-tag" href="/c/${esc(t.category_slug)}">${esc(t.category_name)}</a> &middot; ` : ''}
      ${esc(t.author_name)} &middot; ${replies} &middot; ${timeAgo(t.bumped_at)}
    </div>
  </div>`;
}

export function homePage({ categories, threads, user }) {
  const content = `
  <h1>The Forum</h1>
  <p class="sub">Share ideas. Steelman each other. Practice corrigibility and curiosity.</p>
  <div class="actions">
    ${user ? `<a class="btn" href="/new">Start a thread</a>` : `<a class="btn" href="/login">Sign in to post</a>`}
  </div>
  <div class="panel">
    <h2>Places</h2>
    ${categories.map((c) => `
      <a class="cat" href="/c/${esc(c.slug)}">
        <span class="c">${c.thread_count} ${c.thread_count === 1 ? 'thread' : 'threads'}</span>
        <div class="n">${esc(c.name)}</div>
        <div class="d">${esc(c.description)}</div>
      </a>`).join('')}
  </div>
  <div class="panel sec">
    <h2>Recent threads</h2>
    ${threads.length ? threads.map((t) => threadRow(t)).join('') : '<div class="row"><div class="t" style="color:var(--fog-500); font-style:italic;">Nothing yet. Be the first center of convergence.</div></div>'}
  </div>`;
  return layout({
    title: 'The Forum, at Fractal Reality',
    description: 'Share ideas, steelman each other, practice corrigibility and curiosity.',
    user, content,
  });
}

export function categoryPage({ category, threads, user, page, hasMore }) {
  const content = `
  <div class="crumb"><a href="/">Forum</a> / ${esc(category.name)}</div>
  <h1>${esc(category.name)}</h1>
  <p class="sub">${esc(category.description)}</p>
  <div class="actions">
    ${user ? `<a class="btn" href="/new?c=${esc(category.slug)}">Start a thread here</a>` : `<a class="btn" href="/login">Sign in to post</a>`}
  </div>
  <div class="panel">
    <h2>Threads</h2>
    ${threads.length ? threads.map((t) => threadRow(t, { showCategory: false })).join('') : '<div class="row"><div class="t" style="color:var(--fog-500); font-style:italic;">No threads yet.</div></div>'}
  </div>
  <div class="pager">
    <span>${page > 1 ? `<a href="/c/${esc(category.slug)}?page=${page - 1}">&larr; Newer</a>` : ''}</span>
    <span>${hasMore ? `<a href="/c/${esc(category.slug)}?page=${page + 1}">Older &rarr;</a>` : ''}</span>
  </div>`;
  return layout({ title: `${category.name}, at the Fractal Reality forum`, user, content });
}

export function threadPage({ thread, posts, user, error }) {
  const canModerate = user && (user.role === 'admin' || user.role === 'mod');
  const content = `
  <div class="crumb"><a href="/">Forum</a> / <a href="/c/${esc(thread.category_slug)}">${esc(thread.category_name)}</a></div>
  <h1>${esc(thread.title)}</h1>
  <p class="sub">${thread.locked ? 'This thread is locked. ' : ''}Started ${timeAgo(thread.created_at)}</p>
  ${canModerate ? `
  <div class="actions">
    <form class="inline" method="post" action="/t/${thread.id}/${thread.locked ? 'unlock' : 'lock'}"><button class="btn quiet tiny" type="submit">${thread.locked ? 'Unlock' : 'Lock'}</button></form>
    <form class="inline" method="post" action="/t/${thread.id}/delete" onsubmit="return confirm('Delete this whole thread?')"><button class="btn danger tiny" type="submit">Delete thread</button></form>
  </div>` : ''}
  <div class="panel">
    ${posts.map((p) => `
    <div class="post" id="p${p.id}">
      ${avatar(p.author_name, p.author_avatar)}
      <div class="body">
        <div class="head">
          <span class="nm">${esc(p.author_name)}</span>
          ${p.author_role !== 'member' ? `<span class="role">&middot; ${esc(p.author_role)}</span>` : ''}
          &middot; ${timeAgo(p.created_at)}
          ${canModerate && !p.deleted ? `<form class="inline" method="post" action="/p/${p.id}/delete" onsubmit="return confirm('Delete this post?')"><button class="btn danger tiny" type="submit" style="margin-left:8px;">delete</button></form>` : ''}
        </div>
        <div class="txt${p.deleted ? ' gone' : ''}">${p.deleted ? 'Removed by a moderator.' : esc(p.body)}</div>
      </div>
    </div>`).join('')}
  </div>
  ${error ? `<p class="err sec">${esc(error)}</p>` : ''}
  ${thread.locked ? '' : user ? `
  <div class="panel sec">
    <h2>Reply</h2>
    <form class="stack" method="post" action="/t/${thread.id}/reply">
      <textarea name="body" required maxlength="20000" placeholder="Steelman first. Then speak."></textarea>
      <div><button class="btn" type="submit">Post reply</button></div>
    </form>
  </div>` : `<p class="sub sec"><a href="/login">Sign in</a> to join this thread.</p>`}`;
  return layout({ title: `${thread.title}, at the Fractal Reality forum`, user, content });
}

export function newThreadPage({ categories, selected, user, error, draft }) {
  const content = `
  <div class="crumb"><a href="/">Forum</a> / New thread</div>
  <h1>Start a thread</h1>
  <p class="sub">Open with something real: an idea, a question, a position you want steelmanned.</p>
  ${error ? `<p class="err">${esc(error)}</p>` : ''}
  <div class="panel">
    <form class="stack" method="post" action="/new">
      <label for="c">Place</label>
      <select id="c" name="category">
        ${categories.map((c) => `<option value="${esc(c.slug)}"${c.slug === selected ? ' selected' : ''}>${esc(c.name)}</option>`).join('')}
      </select>
      <label for="ti">Title</label>
      <input id="ti" type="text" name="title" required maxlength="200" value="${esc(draft?.title || '')}">
      <label for="bo">First post</label>
      <textarea id="bo" name="body" required maxlength="20000">${esc(draft?.body || '')}</textarea>
      <div><button class="btn" type="submit">Create thread</button></div>
    </form>
  </div>`;
  return layout({ title: 'Start a thread, at the Fractal Reality forum', user, content });
}

export function loginPage({ providerList, devLogin, error }) {
  const content = `
  <h1 style="text-align:center;">Enter the Forum</h1>
  <p class="invite">Are you curious about philosophy, life, reality, consciousness, truth, and what it means to be human?<br>
  <strong>Curiosity opens the door. Corrigibility keeps it open.</strong></p>
  ${error ? `<p class="err" style="text-align:center;">${esc(error)}</p>` : ''}
  <div class="panel" style="max-width:440px; margin:0 auto;">
    <h2>Sign in</h2>
    <div class="providers">
      ${providerList.map((p) => `<a class="btn" href="/auth/${p.id}">Continue with ${esc(p.label)}</a>`).join('')}
      ${providerList.length === 0 ? '<p style="color:var(--fog-300); font-style:italic; text-align:center;">No sign-in providers are configured yet.</p>' : ''}
      ${devLogin ? `<a class="btn quiet" href="/auth/dev">Continue as test user (dev only)</a>` : ''}
    </div>
  </div>
  <p class="sub sec" style="text-align:center;">We store only your name, avatar, and email, to know you when you return.<br>No posts or profiles are shared with the sign-in providers. <a href="https://fractalreality.ca/privacy.html">Privacy policy</a>.</p>`;
  return layout({ title: 'Sign in, at the Fractal Reality forum', user: null, content });
}

export function mePage({ user, saved }) {
  const content = `
  <div class="crumb"><a href="/">Forum</a> / You</div>
  <h1>Your profile</h1>
  <p class="sub">Signed in with ${esc(user.provider)}${user.role !== 'member' ? `, role: ${esc(user.role)}` : ''}.</p>
  ${saved ? '<p class="ok">Saved.</p>' : ''}
  <div class="panel">
    <form class="stack" method="post" action="/me">
      <label for="nm">Display name</label>
      <input id="nm" type="text" name="name" required maxlength="60" value="${esc(user.name)}">
      <div><button class="btn" type="submit">Save</button></div>
    </form>
  </div>
  <div class="panel sec">
    <h2>Delete your data</h2>
    <form class="stack" method="post" action="/me/delete"
          onsubmit="return confirm('Permanently delete your account and data? Your name, email, avatar, and sign-in link are removed immediately. Posts you wrote remain, shown as Deleted member. This cannot be undone.')">
      <p style="color:var(--fog-300); font-style:italic;">Removes your name, email, avatar, and sign-in link, permanently and immediately. Posts you wrote remain in their threads, attributed to &ldquo;Deleted member&rdquo;. See the <a href="https://fractalreality.ca/privacy.html#delete">privacy policy</a>.</p>
      <div><button class="btn danger" type="submit">Delete my account and data</button></div>
    </form>
  </div>`;
  return layout({ title: 'Your profile, at the Fractal Reality forum', user, content });
}

export function guidelinesPage({ user }) {
  const content = `
  <div class="crumb"><a href="/">Forum</a> / Guidelines</div>
  <h1>How we talk here</h1>
  <p class="sub">The forum is a practice space for the same five pillars the rest of the site is built on.</p>
  <div class="panel">
    <div class="cat"><div class="n">Be curious before you conclude</div>
      <div class="d">Ask what the other person actually means. Questions open apertures; verdicts close them.</div></div>
    <div class="cat"><div class="n">Steelman before you disagree</div>
      <div class="d">State the strongest version of the position you are about to argue with, strong enough that its holder would sign it. Then answer that version, not a weaker one.</div></div>
    <div class="cat"><div class="n">Practice corrigibility</div>
      <div class="d">Yield to evidence, not to pressure. "I was wrong, and here is what corrected me" is the strongest sentence on this forum. Changing your mind in public is a win, not a loss.</div></div>
    <div class="cat"><div class="n">Stay whole, let others stay whole</div>
      <div class="d">Attack positions, never people. No harassment, no gaslighting, no dogpiles. Each person here is a whole at their own scale.</div></div>
    <div class="cat"><div class="n">Keep agreements</div>
      <div class="d">Agreement earned at the end of a real exchange is worth more than agreement assumed at the start. Honor what the thread has established, or reopen it honestly.</div></div>
  </div>
  <p class="sub sec">Moderators may remove content that breaks these guidelines. Deception to control, harassment, and spam are the hard lines.</p>`;
  return layout({ title: 'Guidelines, at the Fractal Reality forum', user, content });
}

export function messagePage({ title, body, user }) {
  const content = `<h1>${esc(title)}</h1><p class="sub">${esc(body)}</p><p><a class="btn" href="/">Back to the forum</a></p>`;
  return layout({ title: `${title}, at the Fractal Reality forum`, user, content });
}
