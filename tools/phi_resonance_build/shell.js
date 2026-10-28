  // ============= THE SHELL: tabs, breath guide, preset picker, stage =============
  // The Last Ship Sailing look (owner: "last ship sailing has a nice interface,
  // and the settings menu is nice too"). The main screen is the player, with
  // every settings tab along its top (owner: "put all the tabs from the
  // settings screen onto the main screen at the top"): a tab opens its panel
  // under the session card, and the open tab again, the panel's ✕, or Esc
  // closes it.

  function anyOverlayOpen() { return !!document.querySelector('.overlay.open'); }
  function openOverlay(el) {
    el.classList.add('open');
    el.scrollTop = 0;
    document.body.classList.add('overlay-open');
  }
  function closeOverlay(el) {
    el.classList.remove('open');
    if (!anyOverlayOpen()) document.body.classList.remove('overlay-open');
  }

  // ---- the tabs along the top ----
  const appEl = document.querySelector('.app');
  const tabRow = $('mainTabs');
  const tabPanels = $('tabPanels');
  let openTab = '';

  // Bring something into view when it starts off screen or under the tab row
  function revealEl(el, minRoom) {
    requestAnimationFrame(() => {
      const r = el.getBoundingClientRect();
      const barBottom = tabRow.getBoundingClientRect().bottom;
      if (r.top < barBottom || r.top > window.innerHeight - (minRoom || 160)) {
        el.scrollIntoView({ block: 'start', behavior: 'smooth' });
      }
    });
  }
  function revealStage() { revealEl($('stage'), 240); }

  function showTab(name) {
    openTab = name || '';
    tabRow.querySelectorAll('.settings-tab').forEach(b => {
      const on = b.dataset.tab === openTab;
      b.dataset.active = on ? '1' : '';
      b.setAttribute('aria-selected', String(on));
      if (!on) return;
      $('panelTitle').textContent = b.textContent;
      // keep the open tab in view along a row that scrolls sideways
      if (b.offsetLeft < tabRow.scrollLeft || b.offsetLeft + b.offsetWidth > tabRow.scrollLeft + tabRow.clientWidth) {
        tabRow.scrollTo({ left: b.offsetLeft - (tabRow.clientWidth - b.offsetWidth) / 2, behavior: 'smooth' });
      }
    });
    tabPanels.querySelectorAll('.settings-panel').forEach(p => { p.dataset.active = p.dataset.panel === openTab ? '1' : ''; });
    appEl.classList.toggle('panel-open', !!openTab);
    if (openTab) revealEl(tabPanels);
  }
  tabRow.querySelectorAll('.settings-tab').forEach(b => {
    b.addEventListener('click', () => showTab(openTab === b.dataset.tab ? '' : b.dataset.tab));
  });
  $('panelClose').addEventListener('click', () => showTab(''));

  // On a phone the row scrolls sideways; its edges fade where more tabs wait
  function tabEdges() {
    const max = tabRow.scrollWidth - tabRow.clientWidth;
    tabRow.classList.toggle('more-left', tabRow.scrollLeft > 4);
    tabRow.classList.toggle('more-right', tabRow.scrollLeft < max - 4);
  }
  tabRow.addEventListener('scroll', tabEdges, { passive: true });
  window.addEventListener('resize', tabEdges);
  tabEdges();

  // ---- Base, Beat and Mode in the session card: tap one to change it there ----
  // (owner: "i should be able to click on the base hz and the beat hz and mode,
  // as buttons to change those values"). The quick sliders drive the Sound
  // tab's own sliders, so every change takes the same path; the quick mode
  // buttons are more .mode-tab buttons, which the mode code already serves.
  let openStat = '';
  const QUICK = {
    base: { real: 'base', quick: 'qBase', fmt: v => Math.round(v) + ' Hz' },
    beat: { real: 'beat', quick: 'qBeat', fmt: v => v.toFixed(3) + ' Hz' }
  };
  function syncQuick() {
    Object.keys(QUICK).forEach(k => {
      const q = QUICK[k], real = $(q.real), quick = $(q.quick), out = $(q.quick + 'Val');
      if (quick.value !== real.value) quick.value = real.value;
      if (!out.querySelector('.val-input')) out.textContent = q.fmt(parseFloat(real.value));
    });
  }
  function setReal(k, v) {
    const real = $(QUICK[k].real);
    real.value = String(v);
    real.dispatchEvent(new Event('input', { bubbles: true }));
    syncQuick();
    // a typed value commits while its input is still in the readout; relabel
    // the readout once the input has gone
    setTimeout(syncQuick, 0);
  }
  function showStat(name) {
    openStat = name || '';
    document.querySelectorAll('.stat[data-edit]').forEach(b => b.setAttribute('aria-expanded', String(b.dataset.edit === openStat)));
    document.querySelectorAll('#statEdit .stat-pane').forEach(p => { p.dataset.active = p.dataset.pane === openStat ? '1' : ''; });
    $('statEdit').classList.toggle('open', !!openStat);
    $('statHint').hidden = openStat === 'mode';
    if (openStat) syncQuick();
  }
  document.querySelectorAll('.stat[data-edit]').forEach(b => {
    b.addEventListener('click', () => showStat(openStat === b.dataset.edit ? '' : b.dataset.edit));
  });
  Object.keys(QUICK).forEach(k => {
    $(QUICK[k].quick).addEventListener('input', e => setReal(k, e.target.value));
    $(QUICK[k].real).addEventListener('input', () => { if (openStat) syncQuick(); });
  });
  document.querySelectorAll('[data-nudge]').forEach(b => {
    b.addEventListener('click', () => {
      const k = b.dataset.nudge, real = $(QUICK[k].real);
      const dec = (String(real.step).split('.')[1] || '').length;
      let v = parseFloat(real.value) + parseFloat(b.dataset.by);
      v = Math.min(parseFloat(real.max), Math.max(parseFloat(real.min), v));
      setReal(k, dec ? v.toFixed(dec) : Math.round(v));
    });
  });
  // presets, frequency chips and saved states set the sliders without an event
  setInterval(() => { if (openStat) syncQuick(); }, 250);

  // ---- the session card folds to a slim bar in its place; the bar keeps
  // play / stop, the preset and the timer, and the choice is remembered ----
  const MINI_KEY = 'phi_resonance_session_mini';
  const sessionCard = document.querySelector('.play-card');
  function updateSessionSummary() {
    if (!sessionCard.classList.contains('mini')) return;
    const text = $('presetName').textContent + ' · ' + $('timer').textContent;
    if ($('sessionSummary').textContent !== text) $('sessionSummary').textContent = text;
  }
  function setSessionMini(on) {
    sessionCard.classList.toggle('mini', on);
    $('sessionMin').textContent = on ? '+' : '−';
    $('sessionMin').title = on ? 'Expand the session card' : 'Minimize the session card';
    $('sessionMin').setAttribute('aria-expanded', String(!on));
    if (on) showStat('');   // an open stat editor folds away with the card
    updateSessionSummary();
    try { localStorage.setItem(MINI_KEY, on ? '1' : ''); } catch (e) {}
  }
  $('sessionMin').addEventListener('click', () => setSessionMini(!sessionCard.classList.contains('mini')));
  setInterval(updateSessionSummary, 500);
  let startMini = false;
  try { startMini = localStorage.getItem(MINI_KEY) === '1'; } catch (e) {}
  setSessionMini(startMini);

  // ---- the breath guide's own view ----
  const openBreathGuide = () => openOverlay($('breathOverlay'));
  $('openBreath').addEventListener('click', openBreathGuide);
  $('openBreath2').addEventListener('click', openBreathGuide);
  $('breathClose').addEventListener('click', () => closeOverlay($('breathOverlay')));

  // Esc closes the breath view, or else an open stat editor, or else the open
  // panel. (Capture phase: this runs before the safety notice's and the
  // flashes' own Esc handlers, so it can leave them their Esc and one press
  // closes one thing; a field being typed in keeps its Esc too.)
  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    if ($('safetyNotice').classList.contains('active') || (state.vbeat && state.vbeat.active)) return;
    if (e.target && e.target.closest && e.target.closest('input, select, textarea')) return;
    if ($('breathOverlay').classList.contains('open')) { e.preventDefault(); closeOverlay($('breathOverlay')); return; }
    if (openStat) { e.preventDefault(); showStat(''); return; }
    if (openTab) { e.preventDefault(); showTab(''); }
  }, true);

  // The flashes run full screen, or inside the main window where the
  // circumpunct and the breath lane stay in view
  const FLASH_WHERE_KEY = 'phi_resonance_flash_where';
  try { if (localStorage.getItem(FLASH_WHERE_KEY) === 'stage') state.vbeat.where = 'stage'; } catch (e) {}
  function syncFlashControls() {
    document.querySelectorAll('[data-flash-where]').forEach(b => {
      b.setAttribute('aria-pressed', String(b.dataset.flashWhere === state.vbeat.where));
    });
    $('vbeatLaunch').textContent = state.vbeat.active ? '■ Stop the flashes'
      : (state.vbeat.where === 'stage' ? '▣ Start in the main window' : '▣ Launch full-screen');
    syncBreathControls();
  }
  document.querySelectorAll('[data-flash-where]').forEach(b => {
    b.addEventListener('click', () => {
      const where = b.dataset.flashWhere;
      if (where === state.vbeat.where) return;
      const wasActive = state.vbeat.active;
      if (wasActive) closeFlash();
      state.vbeat.where = where;
      try { localStorage.setItem(FLASH_WHERE_KEY, where); } catch (e) {}
      if (wasActive) openFlash(); else syncFlashControls();
    });
  });
  $('stageFlashStop').addEventListener('click', () => closeFlash());
  syncFlashControls();

  // The preset picker on the main screen: ◀ name ▶ (the game's map selector)
  function presetIndex() { return Math.max(0, PRESETS.findIndex(p => p.id === state.currentPreset)); }
  function stepPreset(d) {
    const i = presetIndex();
    applyPreset(PRESETS[(i + d + PRESETS.length) % PRESETS.length].id);
  }
  function updatePresetPicker() {
    const pr = PRESETS.find(p => p.id === state.currentPreset);
    $('presetName').textContent = pr ? pr.name : 'CUSTOM';
    $('presetDesc').textContent = pr ? pr.desc : 'Your own settings';
  }
  $('presetPrev').addEventListener('click', () => stepPreset(-1));
  $('presetNext').addEventListener('click', () => stepPreset(1));
  $('presetName').addEventListener('click', () => showTab('library'));
  updatePresetPicker();


