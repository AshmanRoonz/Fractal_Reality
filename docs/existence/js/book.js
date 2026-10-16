// The book: page turning, running head, contents, and the plate runner.
(function () {
  'use strict';
  const PAGES = window.PAGES, ART = window.ART, Kit = window.PlateKit;
  const $ = function (id) { return document.getElementById(id); };
  const canvas = $('art'), frame = $('plateFrame'), inner = $('pageInner'), spread = $('spread');
  const rail = $('rail'), toc = $('toc'), scrim = $('scrim'), tocBtn = $('tocBtn');
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- structure ----------
  const plain = function (s) { return s.replace(/\*\*|\*/g, ''); };
  const chapters = [];      // { title, page }
  const chapterOf = [];     // page index -> chapter index
  PAGES.forEach(function (p, i) {
    if (p.k === 'title') chapters.push({ title: 'Existence', page: i });
    else if (p.k === 'th') chapters.push({ title: plain(p.x), page: i });
    else if (p.k === 'part') chapters.push({ title: p.n + ': ' + plain(p.t), page: i, part: true });
    else if (p.s) { if (!PAGES[i - 1] || PAGES[i - 1].s !== p.s) chapters.push({ title: p.s, page: i, sub: true }); }
    else if (p.k === 'pp') chapters.push({ title: plain(p.t), page: i, sub: true });
    else if (p.ch) chapters.push({ title: p.ch, page: i });
    chapterOf[i] = Math.max(0, chapters.length - 1);
  });
  const partCount = 1 + PAGES.filter(function (p) { return p.k === 'part'; }).length;

  // The narration (js/narration.js): one recording per track, played in order. A track covers
  // pages first .. first + starts.length - 1.
  const N = window.NARRATION;
  const tracks = N && N.tracks ? N.tracks.filter(function (t) { return t.starts && t.starts.length; }) : [];
  const narrSecs = tracks.reduce(function (s, t) { return s + t.duration; }, 0);
  const narrPages = tracks.reduce(function (s, t) { return s + t.starts.length; }, 0);
  const trackOf = function (i) {
    for (let k = 0; k < tracks.length; k++) {
      if (i >= tracks[k].first && i < tracks[k].first + tracks[k].starts.length) return k;
    }
    return -1;
  };

  function md(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>');
  }

  function pageHTML(i) {
    const p = PAGES[i];
    switch (p.k) {
      case 'title':
        return '<h1 class="title">Existence</h1>' +
          '<p class="subtitle">One and many. A Circumpunct manifesto.</p>' +
          (p.x ? '<p class="txt lede">' + md(p.x) + '</p>' : '') +
          '<p class="hint">' + PAGES.length + ' pages' + (partCount > 1 ? ' in ' + partCount + ' parts' : '') + '. ' +
          'Turn pages with the arrow keys, a swipe, or the buttons below, and tap a plate to draw it again.' +
          (tracks.length ? ' Press Listen, top left, to hear ' +
            (narrPages < PAGES.length ? 'the first ' + narrPages + ' pages' : 'it') +
            ' read in the author’s cloned voice (about ' + Math.round(narrSecs / 60) + ' minutes).' : '') +
          '</p>';
      case 'part':
        return '<p class="kicker">' + md(p.n) + '</p><h2 class="parttitle">' + md(p.t) + '</h2>' +
          '<p class="subtitle">' + md(p.x) + '</p>';
      case 'pp':
        return (p.s ? '<p class="kicker">' + md(p.s) + '</p>' : '<div class="mark" aria-hidden="true"></div>') +
          '<h2 class="pagehead">' + md(p.t) + '</h2>' +
          p.p.map(function (s) { return '<p class="txt">' + md(s) + '</p>'; }).join('');
      case 'th':
        return '<div class="mark" aria-hidden="true"></div><h2 class="thesis">' + md(p.x) + '</h2>';
      case 'q':
        return '<p class="q">' + md(p.x) + '</p>';
      case 'sym':
        return '<p class="txt">' + md(p.x) + '</p><p class="sym" role="img" aria-label="Circumpunct">⊙</p>';
      case 'tbl': {
        const head = '<tr>' + p.head.map(function (h) { return '<th scope="col">' + md(h) + '</th>'; }).join('') + '</tr>';
        const rows = p.rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + md(c) + '</td>'; }).join('') + '</tr>'; }).join('');
        return '<p class="txt">' + md(p.x) + '</p><div class="tbl-wrap"><table><thead>' + head + '</thead><tbody>' + rows + '</tbody></table></div>';
      }
      default: {
        const prev = PAGES[i - 1];
        const lead = prev && prev.k === 'th' && p.x.length > 120;
        return '<p class="txt' + (lead ? ' lead' : '') + '">' + md(p.x) + '</p>';
      }
    }
  }

  // ---------- plate runner ----------
  const variant = {};
  let cur = -1, jobId = 0, raf = 0;

  function sizeCanvas() {
    const r = frame.getBoundingClientRect();
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    const px = Math.max(64, Math.min(1600, Math.round(r.width * dpr)));
    if (canvas.width === px && canvas.height === px) return false;
    canvas.width = px; canvas.height = px;
    return true;
  }

  function startArt() {
    const token = ++jobId;
    cancelAnimationFrame(raf);
    sizeCanvas();
    const p = PAGES[cur];
    const seed = Kit.hashSeed('existence', cur, variant[cur] || 0);
    const g = Kit.Plate(canvas, seed, chapterOf[cur] + (variant[cur] || 0), Object.assign({ variant: variant[cur] || 0 }, p.o));
    const it = (ART[p.a] || ART.circumpunct)(g);
    const budget = reduce ? 160 : 12;
    const step = function () {
      if (token !== jobId) return;
      const t0 = performance.now();
      let done = false;
      while (performance.now() - t0 < budget) {
        if (it.next().done) { done = true; break; }
      }
      if (!done) raf = requestAnimationFrame(step);
    };
    step();
    frame.setAttribute('aria-label', (g.name || 'Fractal plate') + '. Press to draw a new version.');
  }

  // ---------- navigation ----------
  let textTimer = 0;
  let narrator = null, onTurn = null, onPage = null;   // set by the narration block below

  function go(i, opts) {
    i = Math.max(0, Math.min(PAGES.length - 1, i | 0));
    if (i === cur) return;
    const first = cur < 0;
    cur = i;
    const html = pageHTML(i), kind = PAGES[i].k;
    clearTimeout(textTimer);
    if (first || reduce) {
      inner.innerHTML = html;
      inner.dataset.kind = kind;
      inner.classList.remove('leaving');
    } else {
      inner.classList.add('leaving');
      textTimer = setTimeout(function () {
        inner.innerHTML = html;
        inner.dataset.kind = kind;
        spread.scrollTop = 0;
        inner.classList.remove('leaving');
      }, 170);
    }
    $('pgNum').textContent = i + 1;
    $('runhead').textContent = PAGES[i].k === 'title' ? '' : chapters[chapterOf[i]].title;
    $('prev').disabled = i === 0;
    $('next').disabled = i === PAGES.length - 1;
    const ticks = rail.children;
    for (let k = 0; k < ticks.length; k++) {
      ticks[k].classList.toggle('on', k === i);
      ticks[k].classList.toggle('past', k < i);
      if (k === i) ticks[k].setAttribute('aria-current', 'page'); else ticks[k].removeAttribute('aria-current');
    }
    try { history.replaceState(null, '', '#p' + (i + 1)); } catch (e) { /* sandboxed */ }
    try { localStorage.setItem('existence-page', String(i)); } catch (e) { /* storage blocked */ }
    if (!(opts && opts.noArt)) startArt();
    if (onTurn && !(opts && opts.fromAudio)) onTurn(i);
    if (onPage) onPage(i);
  }

  function redraw() {
    variant[cur] = (variant[cur] || 0) + 1;
    startArt();
  }

  // Rail of page ticks; taller ticks open chapters.
  PAGES.forEach(function (p, i) {
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'tick' + (chapters.some(function (c) { return c.page === i; }) ? ' ch' : '');
    b.setAttribute('aria-label', 'Page ' + (i + 1) + ', ' + chapters[chapterOf[i]].title);
    b.title = 'Page ' + (i + 1);
    b.addEventListener('click', function () { go(i); });
    rail.appendChild(b);
  });
  $('pgTotal').textContent = PAGES.length;

  // Contents.
  const list = $('tocList');
  chapters.forEach(function (c) {
    const li = document.createElement('li');
    if (c.part) li.className = 'partrow';
    else if (c.sub) li.className = 'subrow';
    const b = document.createElement('button');
    b.type = 'button';
    b.innerHTML = '<span class="n">' + (c.page + 1) + '</span><span class="t"></span>';
    b.querySelector('.t').textContent = c.title;
    b.addEventListener('click', function () { closeToc(); go(c.page); });
    li.appendChild(b);
    list.appendChild(li);
  });

  function openToc() {
    const here = chapterOf[cur];
    Array.prototype.forEach.call(list.children, function (li, k) { li.classList.toggle('here', k === here); });
    toc.hidden = false; scrim.hidden = false;
    tocBtn.setAttribute('aria-expanded', 'true');
    const btn = list.children[here] && list.children[here].querySelector('button');
    if (btn) btn.focus();
  }
  function closeToc() {
    if (toc.hidden) return;
    toc.hidden = true; scrim.hidden = true;
    tocBtn.setAttribute('aria-expanded', 'false');
    tocBtn.focus();
  }
  tocBtn.addEventListener('click', function () { if (toc.hidden) openToc(); else closeToc(); });
  $('tocClose').addEventListener('click', closeToc);
  scrim.addEventListener('click', closeToc);

  $('prev').addEventListener('click', function () { go(cur - 1); });
  $('next').addEventListener('click', function () { go(cur + 1); });
  frame.addEventListener('click', redraw);
  frame.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); e.stopPropagation(); redraw(); }
  });

  document.addEventListener('keydown', function (e) {
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === 'Escape') { closeToc(); return; }
    if (!toc.hidden) return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); go(cur + 1); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); go(cur - 1); }
    else if (e.key === 'Home') { e.preventDefault(); go(0); }
    else if (e.key === 'End') { e.preventDefault(); go(PAGES.length - 1); }
    else if (e.key === 'r' || e.key === 'R') redraw();
    else if (e.key === ' ' && narrator && !(e.target.closest && e.target.closest('button, a, input, textarea'))) {
      e.preventDefault(); narrator.toggle();
    }
  });

  // Horizontal swipe turns the page; vertical movement still scrolls.
  let sx = 0, sy = 0, swiping = false;
  spread.addEventListener('touchstart', function (e) {
    if (e.touches.length !== 1) { swiping = false; return; }
    sx = e.touches[0].clientX; sy = e.touches[0].clientY; swiping = true;
  }, { passive: true });
  spread.addEventListener('touchend', function (e) {
    if (!swiping) return;
    swiping = false;
    const t = e.changedTouches[0], dx = t.clientX - sx, dy = t.clientY - sy;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) go(cur + (dx < 0 ? 1 : -1));
  }, { passive: true });

  // Redraw the plate at the new resolution when its size changes.
  let resizeTimer = 0;
  if (window.ResizeObserver) {
    new ResizeObserver(function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () { if (cur >= 0 && sizeCanvas()) startArt(); }, 160);
    }).observe(frame);
  }

  // ---------- narration: the book read aloud, turning pages at each pause ----------
  // One audio element plays the tracks in order. Within a track, starts[j] is the second at which
  // page first + j turns; when a track ends, the next one carries on from its first page.
  const listenBtn = $('listen'), clock = $('clock');
  if (tracks.length) {
    const offset = [];   // seconds of narration before each track
    tracks.reduce(function (s, t, k) { offset[k] = s; return s + t.duration; }, 0);
    const pageAt = function (k, t) {
      const s = tracks[k].starts;
      let j = 0;
      while (j + 1 < s.length && s[j + 1] <= t) j++;
      return tracks[k].first + j;
    };
    const fmt = function (s) {
      s = Math.max(0, Math.floor(s));
      return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    };
    const show = function (playing) {
      listenBtn.setAttribute('aria-pressed', playing ? 'true' : 'false');
      listenBtn.querySelector('.lbl').textContent = playing ? 'Pause' : 'Listen';
    };
    let audio = null, tk = -1, syncing = false;   // tk: the loaded track. syncing: a seek is in flight, so time updates must not turn pages
    // target: a seek waiting until the file allows it. landing: a seek in flight, checked on arrival.
    let target = null, landing = null, resumeAfterSeek = false, fetching = -1;
    const blobs = [];   // per track: the file fetched into memory, as a blob URL
    const canSeekTo = function (t) {
      const s = audio.seekable;
      for (let i = 0; i < s.length; i++) if (t >= s.start(i) && t <= s.end(i) + 0.5) return true;
      return false;
    };
    // A server without range requests leaves an MP3 unseekable. Then fetch it once and play from memory.
    const fromBlob = function () {
      const k = tk;
      if (blobs[k] || fetching === k) return;
      fetching = k;
      resumeAfterSeek = resumeAfterSeek || !audio.paused;
      audio.pause();
      clock.textContent = 'Loading narration';
      fetch(tracks[k].src).then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.blob();
      }).then(function (b) {
        blobs[k] = URL.createObjectURL(b);
        fetching = -1;
        if (tk === k) audio.src = blobs[k];
      }).catch(function () {
        fetching = -1;
        syncing = false;
        resumeAfterSeek = false;
        audio.muted = false;
        clock.textContent = 'Narration unavailable';
      });
    };
    const applySeek = function () {
      if (target == null || audio.readyState < 1) return;
      if (!canSeekTo(target)) { fromBlob(); return; }   // in memory already: wait for the next readiness event
      landing = target;
      target = null;
      audio.currentTime = landing;
    };
    // Point the player at page i: load its track if another one is loaded, then seek to the page.
    const seekTo = function (i) {
      const k = trackOf(i), t = tracks[k].starts[i - tracks[k].first];
      if (k !== tk) {
        tk = k;
        target = null;
        landing = null;
        audio.src = blobs[k] || tracks[k].src;   // a new source starts paused, at its beginning
        if (t < 0.05) { syncing = false; audio.muted = false; return; }
      }
      syncing = true;
      target = t;
      applySeek();
    };
    const load = function () {
      if (audio) return audio;
      audio = new Audio();
      audio.preload = 'auto';
      ['loadedmetadata', 'durationchange', 'canplay'].forEach(function (ev) { audio.addEventListener(ev, applySeek); });
      audio.addEventListener('seeked', function () {
        if (landing != null && Math.abs(audio.currentTime - landing) > 1.5) {
          // The seek did not land (the file cannot be seeked here): keep pages locked and play from memory.
          target = landing;
          landing = null;
          fromBlob();
          return;
        }
        landing = null;
        syncing = false;
        audio.muted = false;
        if (resumeAfterSeek) {
          resumeAfterSeek = false;
          audio.play().catch(function () { show(false); });
        }
      });
      audio.addEventListener('timeupdate', function () {
        if (syncing || tk < 0) return;
        const p = pageAt(tk, audio.currentTime);
        if (p !== cur) go(p, { fromAudio: true });
        clock.textContent = fmt(offset[tk] + audio.currentTime) + ' / ' + fmt(narrSecs);
      });
      audio.addEventListener('play', function () { show(true); });
      audio.addEventListener('pause', function () { show(false); });
      audio.addEventListener('ended', function () {
        if (tk + 1 >= tracks.length) return;   // the end of the book
        seekTo(tracks[tk + 1].first);           // carry straight on into the next recording
        audio.play().catch(function () { show(false); });
      });
      audio.addEventListener('error', function () {
        show(false);
        listenBtn.disabled = true;
        clock.textContent = 'Narration unavailable';
      });
      return audio;
    };
    narrator = {
      toggle: function () {
        if (trackOf(cur) < 0) return;   // a page with no recording
        const a = load();
        if (fetching >= 0) return;   // still loading into memory
        if (!a.paused) { a.pause(); return; }
        if (trackOf(cur) !== tk || a.ended || pageAt(tk, a.currentTime) !== cur) {
          a.muted = true;   // silent until the seek lands, so the opening words never leak through
          seekTo(cur);
        }
        const played = a.play();   // called inside the click so browsers allow sound
        if (played && played.catch) played.catch(function () { show(false); });
      },
      seek: function (i) {
        if (!audio || tk < 0) return;
        const k = trackOf(i);
        if (k < 0) { if (!audio.paused) audio.pause(); return; }
        if (k === tk && pageAt(tk, audio.currentTime) === i) return;
        const resume = k !== tk && !audio.paused;   // a new source starts paused
        if (resume) audio.muted = true;
        seekTo(i);
        if (resume) audio.play().catch(function () { show(false); });
      }
    };
    onTurn = narrator.seek;
    onPage = function (i) {
      const off = trackOf(i) < 0;
      listenBtn.disabled = off;
      listenBtn.title = off ? 'This page is not narrated yet' :
        'Read aloud by an ElevenLabs clone of ' + N.reader + '’s voice';
    };
    listenBtn.hidden = false;
    listenBtn.title = 'Read aloud by an ElevenLabs clone of ' + N.reader + '’s voice';
    listenBtn.addEventListener('click', narrator.toggle);
    if ('mediaSession' in navigator) {
      try {
        navigator.mediaSession.metadata = new MediaMetadata({ title: 'Existence', artist: N.reader, album: 'One and many. A Circumpunct manifesto.' });
        navigator.mediaSession.setActionHandler('play', function () { if (!audio || audio.paused) narrator.toggle(); });
        navigator.mediaSession.setActionHandler('pause', function () { if (audio && !audio.paused) audio.pause(); });
        navigator.mediaSession.setActionHandler('previoustrack', function () { go(cur - 1); });
        navigator.mediaSession.setActionHandler('nexttrack', function () { go(cur + 1); });
      } catch (e) { /* media session unsupported */ }
    }
  }

  function pageFromHash() {
    const m = /^#p(\d+)$/.exec(location.hash || '');
    return m ? parseInt(m[1], 10) - 1 : null;
  }
  window.addEventListener('hashchange', function () { const h = pageFromHash(); if (h != null) go(h); });

  let start = pageFromHash();
  if (start == null) {
    try { const s = localStorage.getItem('existence-page'); if (s != null) start = parseInt(s, 10) || 0; } catch (e) { start = 0; }
  }
  go(start || 0);
})();
