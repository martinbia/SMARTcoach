(() => {
  'use strict';
  const { today, events } = window.SMART_DEMO;
  const app = document.querySelector('#app');
  const dialog = document.querySelector('#confirmation');
  const storageKey = 'smartcoach.preferences.v1';
  const defaults = { role: 'patient', active: false, textSize: 'normal', idleMotion: true };
  let preferences = { ...defaults };
  let storageAvailable = true;
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (saved && typeof saved === 'object') {
      preferences = {
        role: saved.role === 'relative' ? 'relative' : 'patient',
        active: saved.active === true,
        textSize: saved.textSize === 'large' ? 'large' : 'normal',
        idleMotion: saved.idleMotion !== false
      };
    }
  } catch { storageAvailable = false; }
  let level = 0;
  let windowOffset = 0;
  let route = 'idle';
  let installPrompt = null;
  let dialogOpener = null;
  let offlineReady = false;
  let idleImageURL = null;
  let imageMessage = '';
  let imageBusy = false;
  function setIdleImage(blob) {
    if (idleImageURL) URL.revokeObjectURL(idleImageURL);
    idleImageURL = blob ? URL.createObjectURL(blob) : null;
  }
  const imageReady = window.SMART_IDLE_IMAGE.access('read').then(blob => {
    if (blob instanceof Blob) setIdleImage(blob);
    if (route === 'idle' || route === 'settings') render(route, false);
  }).catch(() => {
    imageMessage = 'Der lokale Bildspeicher ist nicht verfügbar. Sie können die App weiterhin ohne Foto nutzen.';
  });
  const date = value => new Intl.DateTimeFormat('de-CH', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T12:00:00Z`));
  const shiftDate = (value, days) => {
    const result = new Date(`${value}T12:00:00Z`);
    result.setUTCDate(result.getUTCDate() + days);
    return result.toISOString().slice(0, 10);
  };
  const button = (label, action, cls = '', extra = '') => `<button class="${cls}" data-action="${action}" ${extra}>${label}</button>`;
  // Local outline icons; labels stay visible alongside every primary action.
  const icons = {
    companion: '<path d="M21 11a8 8 0 0 1-8 8H8l-5 3 1-6a8 8 0 1 1 17-5Z"/><path d="M8 10h8m-8 4h5"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 11h18m-13 5h2m4 0h2"/>',
    ask: '<path d="M21 11a8 8 0 0 1-8 8H8l-5 3 1-6a8 8 0 1 1 17-5Z"/><path d="M10 8a2 2 0 1 1 3 2c-1 1-1 1-1 2m0 3h.01"/>',
    exercises: '<circle cx="14" cy="4" r="2"/><path d="m10 10 3-3 3 4 4 1m-7-5-2 7-4 6m4-6 5 2 1 5M6 8l4 2"/>',
    reports: '<path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8m-8 4h8"/>',
    diary: '<rect x="5" y="3" width="15" height="18" rx="2"/><path d="M3 7h4m-4 5h4m-4 5h4M11 8h5m-5 4h5"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="m10 3-1 3-3 1-3 3 2 3-1 3 3 2 3-1 3 2 3-2 1-3 3-2-1-3-3-1-1-3Z"/>'
  };
  const icon = name => `<svg class="action-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[name]}</svg>`;
  const symbolMarkup = symbol => symbol === '↗'
    ? '<svg class="symbol" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    : symbol;
  const isRelative = () => preferences.role === 'relative';

  function applyPreferences() {
    document.documentElement.classList.toggle('large-text', preferences.textSize === 'large');
    document.querySelector('#storage-warning').hidden = storageAvailable;
  }
  function savePreferences() {
    try {
      localStorage.setItem(storageKey, JSON.stringify(preferences));
      storageAvailable = true;
    } catch { storageAvailable = false; }
    applyPreferences();
  }
  function stopMedia() {
    // All future players must stay inside the document so this global stop owns them.
    document.querySelectorAll('audio, video').forEach(media => {
      media.pause();
      try { media.currentTime = 0; } catch { /* Metadata may not be loaded yet. */ }
    });
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }
  function closeDialog(restoreFocus = true) {
    dialog.close();
    if (restoreFocus && dialogOpener?.isConnected) dialogOpener.focus();
  }
  function navigate(next) {
    if (dialog.open) closeDialog(false);
    stopMedia();
    if (location.hash === `#${next}`) render(next);
    else location.hash = next;
  }
  function stop() {
    closeDialog(false);
    stopMedia();
    // Replace the current entry so browser Back cannot reopen the abandoned modal.
    history.replaceState(null, '', '#idle');
    render('idle');
  }
  function header() {
    return `<header class="topbar"><div class="topbar-inner">
      <div class="brand"><img src="./assets/icon.svg" alt=""><strong>SMART<span>coach</span></strong></div>
      ${route === 'home' ? `<h1 class="greeting" id="page-title" tabindex="-1">Guten Tag, ${isRelative() ? 'Anna' : 'Ernst'}.</h1>` : ''}
      <div class="role-switch" role="group" aria-label="Perspektive wählen">
        ${button('Ernst<span>Patient</span>', 'role-patient', '', `aria-pressed="${!isRelative()}"`)}
        ${button('Anna<span>Angehörige</span>', 'role-relative', '', `aria-pressed="${isRelative()}"`)}
      </div><nav class="header-actions" aria-label="Globale Aktionen">
        ${button(icon('settings') + 'Einstellungen', 'settings')}${button('Beenden', 'stop', 'stop')}
      </nav></div></header>`;
  }
  function footer() {
    return '<footer class="footer"><span>Fiktive Demo · Keine medizinische Beratung</span><span>SMARTcoach</span></footer>';
  }
  function journey() {
    const center = shiftDate(today, windowOffset);
    const start = shiftDate(center, -14);
    const end = shiftDate(center, 14);
    const selected = level === 0 ? events.filter(event => event.overview) : events.filter(event => event.date >= start && event.date <= end);
    return `<section class="card journey-card" aria-labelledby="journey-title">
      <div class="journey-heading"><h2 id="journey-title">Ernsts Weg</h2>
      <div class="journey-tools" role="group" aria-label="Journey-Ansicht">
        ${button('Gesamter Weg', 'overview', '', `aria-pressed="${level === 0}"`)}
        ${button('Heute zentrieren', 'center')}
        <div class="zoom">${button('−', 'zoom-out', '', `aria-label="Weniger Details" ${level === 0 ? 'disabled' : ''}`)}${button('+', 'zoom-in', '', `aria-label="Mehr Details" ${level === 2 ? 'disabled' : ''}`)}</div>
      </div>
      </div><p class="journey-caption ${level === 0 ? 'visually-hidden' : ''}" role="status">${level === 0 ? 'Vom Alltag vor dem Sturz bis zu persönlichen Zielen' : `${date(start)} bis ${date(end)} · ${level === 2 ? 'grosse Detailansicht' : 'Detailansicht'}`}</p>
      <div class="journey-map ${level === 2 ? 'large' : ''}"><svg class="journey-line" aria-hidden="true"><path></path></svg>
        <div class="journey-nodes">${selected.map(event => `<button class="journey-node ${event.id === 'J09' ? 'today' : ''} ${event.date > today ? 'future' : ''}" data-action="event-${event.id}" ${event.id === 'J09' ? 'aria-current="date"' : ''}>
          <span class="node-dot" aria-hidden="true">${symbolMarkup(event.symbol)}</span><span class="node-label">${event.label}</span><span class="node-date">${event.dateLabel || date(event.date)}</span><span class="node-category">${event.category}</span>
        </button>`).join('') || '<p>In diesem Zeitfenster sind keine Demo-Ereignisse hinterlegt.</p>'}</div>
      </div>
      ${level ? `<div class="window-nav">${button('← Frühere Tage', 'previous', '', windowOffset <= -28 ? 'disabled' : '')}${button('Spätere Tage →', 'next', '', windowOffset >= 70 ? 'disabled' : '')}</div>` : ''}
      <p class="legend">Der Weg zeigt Ereignisse in zeitlicher Reihenfolge, keinen Heilungsgrad. ☆ Persönliche Ziele sind Wünsche.</p>
    </section>`;
  }
  const actions = [
    ['ask', '?', 'SMARTcoach fragen', 'Ein Platz für Ihre Fragen'],
    ['exercises', '↗', 'Übungen', 'Orientierung für den Alltag'],
    ['reports', '▤', 'Berichte & Erklärungen', 'Die eigene Geschichte verstehen'],
    ['diary', '✎', 'Tagebuch', 'Beobachtungen festhalten']
  ];
  function home() {
    const appointment = events.find(event => event.id === 'J10');
    const shortDate = date(appointment.date).slice(0, 6);
    return `<nav class="dashboard-tiles" aria-label="Hauptfunktionen">
      ${button(`${icon('companion')}<span class="tile-label">Aktive Begleitung</span><span class="badge ${preferences.active ? 'on' : ''}" role="status">${preferences.active ? 'EIN' : 'AUS'}</span>`, 'companion-details', 'function-tile companion', 'aria-haspopup="dialog"')}
      ${button(`${icon('calendar')}<span class="tile-label">Nächster Termin<small>${shortDate} · Physio</small></span>`, 'event-J10', 'function-tile')}
      ${actions.map(([action, , title]) => button(`${icon(action)}<span class="tile-label">${action === 'reports' ? 'Berichte' : title}</span>`, action, 'function-tile')).join('')}
    </nav>${journey()}`;
  }
  function detail(event) {
    return `<div class="detail">${button('← Zurück zur Übersicht', 'home', 'back')}<article class="card"><span class="eyebrow">${event.category} · ${event.dateLabel || date(event.date)}</span>
      <h1 id="page-title" tabindex="-1">${event.label}</h1><p>${event.text}</p>
      ${isRelative() ? '<p class="muted">Annas Perspektive: Dieselbe Geschichte hilft Ihnen, Ernsts Weg nachzuvollziehen. Eigene Fragen dürfen dabei Raum haben.</p>' : ''}
      <div class="source"><strong>Quelle · fiktive Beispieldaten</strong><p>${event.source}</p></div>
      <p class="small muted">Erste Ereigniskarte des Grundgerüsts. Ausführliche Berichte, Erklärungen und Rückfragen folgen später.</p>
      ${button('SMARTcoach fragen', 'ask', 'primary')}</article></div>`;
  }
  function placeholder(page) {
    const [, symbol, title] = actions.find(([id]) => id === page);
    const copy = {
      ask: 'Hier können Sie später vorbereitete Fragen auswählen und die dazugehörigen Demo-Antworten lesen. In dieser Version gibt es noch keinen Chat und keine KI-Antworten.',
      exercises: 'Hier werden später die im fiktiven persönlichen Plan hinterlegten Übungen angezeigt. Es sind noch keine Übungsanleitungen oder Videos eingebunden.',
      reports: 'Hier werden später fiktive Spital- und Therapieberichte in einfacher Sprache erklärt. Die Ereigniskarten auf der Journey zeigen bereits kurze Hinweise mit Demo-Quellen.',
      diary: 'Hier können Sie später Aktivitäten und Ihr Befinden festhalten. In dieser Version werden noch keine Einträge erfasst oder gespeichert.'
    };
    return `<div class="detail">${button('← Zurück zur Übersicht', 'home', 'back')}<section class="card"><span class="eyebrow">Vorschau · Phase A</span><h1 id="page-title" tabindex="-1"><span aria-hidden="true">${symbolMarkup(symbol)}</span> ${title}</h1>
      <div class="placeholder"><h2>Dieser Bereich entsteht als Nächstes.</h2><p>${copy[page]}</p></div>
      <p class="muted" style="margin-top:24px">${isRelative() ? 'Sie betrachten diesen Bereich als Anna, Angehörige von Ernst.' : 'Sie betrachten diesen Bereich als Ernst, Patient.'}</p>
      ${button('Zur Journey', 'home', 'primary')}</section></div>`;
  }
  function settings() {
    return `<div class="detail">${button('← Zurück zur Übersicht', 'home', 'back')}<section class="card"><span class="eyebrow">So passt es für Sie</span><h1 id="page-title" tabindex="-1">Einstellungen</h1>
      <p>Ihre Auswahl bleibt auf diesem Gerät gespeichert.</p>
      <div class="settings-row"><div><h2><label for="text-size">Schriftgrösse</label></h2><p class="muted small">Alle Ansichten passen sich an.</p></div><select id="text-size"><option value="normal" ${preferences.textSize === 'normal' ? 'selected' : ''}>Gross</option><option value="large" ${preferences.textSize === 'large' ? 'selected' : ''}>Sehr gross</option></select></div>
      <div class="settings-row"><div><h2>Aktive Begleitung: ${preferences.active ? 'EIN' : 'AUS'}</h2><p class="muted small">Noch ohne automatische Ansprache.</p></div>${button(preferences.active ? 'Ausschalten' : 'Einschalten', 'companion')}</div>
      <div class="settings-row"><div><h2>Luzern-Bild im Ruhemodus</h2><p class="muted">Wählen Sie Ihr Luzern-Foto, zum Beispiel aus <strong>Documents/SMART</strong>. Es bleibt nur auf diesem Gerät und wird auch offline angezeigt.</p>
        ${idleImageURL ? `<img class="idle-photo-preview" src="${idleImageURL}" alt="Ihr ausgewähltes Ruhebild">` : '<p class="small muted">Noch kein Foto ausgewählt. Bis dahin bleibt der ruhige Farbhintergrund.</p>'}
        <label class="photo-picker" for="idle-photo">Luzern-Foto auswählen (JPG, PNG oder WebP, bis 12 MB)</label>
        <input id="idle-photo" type="file" accept="image/jpeg,image/png,image/webp" ${imageBusy ? 'disabled' : ''}>
        <p id="image-status" class="small" role="status"></p>
        ${idleImageURL ? button('Foto entfernen', 'remove-photo', '', imageBusy ? 'disabled' : '') : ''}
      </div></div>
      <div class="settings-row"><div><h2><label for="idle-motion">Ruhebildschirm animieren</label></h2><p class="muted small">Langsame Bildbewegung und wechselnder Text. Bei reduzierter Bewegung im Gerät bleibt die Ansicht ruhig.</p></div><select id="idle-motion"><option value="on" ${preferences.idleMotion ? 'selected' : ''}>Ein</option><option value="off" ${!preferences.idleMotion ? 'selected' : ''}>Aus</option></select></div>
      <div class="settings-row"><div><h2>Weitere lokale Medien</h2><p class="muted">Audio und Videos sind noch nicht eingebunden.</p></div></div>
      <div class="settings-row"><div><h2>Interview-Demo zurücksetzen</h2><p class="muted small">Zurück zu Ernst, Gesamtansicht und Begleitung AUS. Die Schriftgrösse bleibt erhalten. Das Demo-Datum ist fest: 06.11.2026.</p></div>${button('Demo zurücksetzen', 'reset')}</div>
      <details class="install-help"><summary>SMARTcoach auf dem Tablet installieren</summary><ol><li>Die veröffentlichte GitHub-Pages-Seite in Chrome auf Android öffnen.</li><li>Im Browsermenü „Zum Startbildschirm hinzufügen“ und, falls angeboten, „Installieren“ wählen.</li><li>Einmal online öffnen. Sobald unten „Offline bereit“ steht, ist das Grundgerüst auch ohne Internet erreichbar.</li></ol><p class="small muted">Das Browsermenü kann je nach Android-Version anders heissen. Gespeicherte Einstellungen können beim Löschen der Browserdaten verloren gehen.</p></details>
      ${installPrompt ? button('App installieren', 'install', 'primary') : ''}
    </section></div>`;
  }
  function layoutJourney() {
    const map = document.querySelector('.journey-map');
    if (!map) return;
    const nodes = [...map.querySelectorAll('.journey-node')];
    // Do not count computed tracks: old inline positions can create implicit
    // columns after rotation and would otherwise lock the map into four columns.
    const cols = map.classList.contains('large') || window.matchMedia('(max-width: 740px)').matches ? 2 : 4;
    nodes.forEach((node, index) => {
      const row = Math.floor(index / cols);
      node.style.gridRow = row + 1;
      node.style.gridColumn = row % 2 === 0 ? index % cols + 1 : cols - index % cols;
    });
    const bounds = map.getBoundingClientRect();
    const points = nodes.map(node => {
      const rect = node.querySelector('.node-dot').getBoundingClientRect();
      return { x: rect.x + rect.width / 2 - bounds.x, y: rect.y + rect.height / 2 - bounds.y };
    });
    let path = '';
    points.forEach((point, index) => {
      if (index === 0) { path = `M ${point.x} ${point.y}`; return; }
      const last = points[index - 1];
      if (Math.abs(point.y - last.y) < 2) {
        const middle = (last.x + point.x) / 2;
        path += ` C ${middle} ${last.y - 20}, ${middle} ${point.y + 20}, ${point.x} ${point.y}`;
      } else {
        const direction = Math.floor((index - 1) / cols) % 2 === 0 ? 1 : -1;
        const outer = Math.max(4, Math.min(bounds.width - 4, point.x + direction * 65));
        path += ` C ${outer} ${last.y}, ${outer} ${point.y}, ${point.x} ${point.y}`;
      }
    });
    map.querySelector('path').setAttribute('d', path);
  }
  const resizeObserver = new ResizeObserver(() => layoutJourney());
  function render(next, focus = true) {
    const event = events.find(item => `event-${item.id}` === next);
    route = ['idle', 'home', 'settings', ...actions.map(([id]) => id)].includes(next) || event ? next : 'idle';
    resizeObserver.disconnect();
    if (route === 'idle') {
      app.innerHTML = `<main class="idle ${idleImageURL ? 'has-photo' : ''} ${preferences.idleMotion ? '' : 'idle-static'}" id="content">
        ${idleImageURL ? `<img class="idle-photo" src="${idleImageURL}" alt="">` : ''}<div class="idle-wash" aria-hidden="true"></div>
        <button class="idle-open" data-action="home" aria-label="Bildschirm berühren – Übersicht öffnen"></button><div class="idle-content"><div class="brand"><img src="./assets/icon.svg" alt=""><strong>SMART<span>coach</span></strong></div><h1>In Ihrem Tempo.<br>Schritt für Schritt.</h1><p>Ein gemeinsamer Blick auf Ihren Weg.</p><span class="idle-prompt">Bildschirm berühren</span></div><p class="idle-note">Demo mit fiktiven Beispieldaten · Keine Ansprache im Ruhemodus</p>
        <button class="idle-motion-control" data-action="idle-toggle">${preferences.idleMotion ? 'Animation anhalten' : 'Animation starten'}</button></main>`;
    } else {
      const content = route === 'home' ? home() : route === 'settings' ? settings() : event ? detail(event) : placeholder(route);
      app.innerHTML = `${header()}<main id="content" ${route === 'home' ? 'class="dashboard"' : ''}>${content}</main>${footer()}`;
      const map = document.querySelector('.journey-map');
      if (map) { layoutJourney(); resizeObserver.observe(map); }
    }
    applyPreferences();
    const status = document.querySelector('#image-status');
    if (status) status.textContent = imageMessage;
    if (focus) {
      window.scrollTo(0, 0);
      (document.querySelector('#page-title') || document.querySelector('.idle-open'))?.focus({ preventScroll: true });
    }
  }
  function redraw(action) {
    const scrollY = window.scrollY;
    render(route, false);
    document.querySelector(`[data-action="${action}"]`)?.focus({ preventScroll: true });
    window.scrollTo(0, scrollY);
  }
  function openDialog(kind, opener) {
    dialogOpener = opener;
    document.querySelector('#dialog-title').textContent = kind === 'consent' ? 'Darf SMARTcoach von sich aus nachfragen?' : kind === 'companion' ? 'Aktive Begleitung ist EIN' : 'Demo wirklich zurücksetzen?';
    document.querySelector('#dialog-body').innerHTML = kind === 'consent'
      ? '<p>Wenn Sie das erlauben, darf SMARTcoach von sich aus nach Ihrem Befinden fragen, an vorgesehene Übungen erinnern und passende Aktivitäten vorschlagen.</p><p>Das gilt nur, während die App sichtbar geöffnet ist. Im Ruhebildschirm bleibt sie still. Sie können die Begleitung jederzeit ausschalten.</p><p class="placeholder">In diesem Grundgerüst speichern wir nur Ihre Zustimmung. Automatische Fragen und Erinnerungen folgen später.</p>'
      : kind === 'companion'
        ? '<p>Sie haben erlaubt, dass SMARTcoach nach Ihrem Befinden fragen, an vorgesehene Übungen erinnern und Aktivitäten vorschlagen darf.</p><p>In dieser Version gibt es noch keine automatische Ansprache. Im Ruhebildschirm bleibt SMARTcoach still.</p><p>Mit „Ausschalten“ widerrufen Sie Ihre Zustimmung sofort.</p>'
        : '<p>Die Perspektive wechselt zu Ernst. Die Journey zeigt wieder den gesamten Weg und Aktive Begleitung wird ausgeschaltet.</p><p>Schriftgrösse, Ruhebild und Animationseinstellung bleiben erhalten. Es gibt noch keine Tagebucheinträge.</p>';
    document.querySelector('#dialog-actions').innerHTML = kind === 'consent'
      ? button('Ja, aktive Begleitung einschalten', 'confirm-consent', 'primary') + button('Nein, ausgeschaltet lassen', 'cancel-dialog')
      : kind === 'companion'
        ? button('Ausschalten', 'companion') + button('Zurück', 'cancel-dialog')
        : button('Ja, Demo zurücksetzen', 'confirm-reset', 'primary') + button('Abbrechen', 'cancel-dialog');
    dialog.showModal();
    document.querySelector('#dialog-actions button:last-child').focus();
  }
  document.addEventListener('click', async event => {
    if (event.target.closest('.skip-link')) {
      event.preventDefault();
      const content = document.querySelector('#content');
      content.setAttribute('tabindex', '-1');
      content.focus();
      return;
    }
    const target = event.target.closest('[data-action]');
    if (!target) return;
    const action = target.dataset.action;
    if (action === 'stop') return stop();
    if (action === 'cancel-dialog') return closeDialog();
    if (action === 'confirm-consent') {
      preferences.active = true;
      savePreferences(); closeDialog(false); redraw(route === 'home' ? 'companion-details' : 'companion'); return;
    }
    if (action === 'confirm-reset') {
      preferences = { ...defaults, textSize: preferences.textSize, idleMotion: preferences.idleMotion };
      level = 0; windowOffset = 0;
      savePreferences(); closeDialog(false); navigate('home'); return;
    }
    if (action === 'companion-details') return openDialog(preferences.active ? 'companion' : 'consent', target);
    if (action === 'companion') {
      if (!preferences.active) return openDialog('consent', target);
      preferences.active = false;
      savePreferences(); closeDialog(false); redraw(route === 'home' ? 'companion-details' : action); return;
    }
    if (action === 'reset') return openDialog('reset', target);
    if (action === 'idle-toggle') {
      preferences.idleMotion = !preferences.idleMotion;
      savePreferences(); redraw(action); return;
    }
    if (action === 'remove-photo') {
      await updatePhoto(null); return;
    }
    if (action.startsWith('role-')) {
      preferences.role = action.slice(5);
      savePreferences(); redraw(action); return;
    }
    if (['overview', 'center', 'zoom-in', 'zoom-out', 'previous', 'next'].includes(action)) {
      if (action === 'overview') { level = 0; windowOffset = 0; }
      if (action === 'center') { level = 1; windowOffset = 0; }
      if (action === 'zoom-in') level = Math.min(2, level + 1);
      if (action === 'zoom-out') level = Math.max(0, level - 1);
      if (action === 'previous') windowOffset = Math.max(-28, windowOffset - 14);
      if (action === 'next') windowOffset = Math.min(70, windowOffset + 14);
      redraw(action);
      return;
    }
    if (action === 'install' && installPrompt) {
      const prompt = installPrompt;
      installPrompt = null;
      await prompt.prompt(); await prompt.userChoice;
      if (route === 'settings') render(route);
      return;
    }
    navigate(action);
  });
  async function updatePhoto(file) {
    if (imageBusy) return;
    imageBusy = true;
    const input = document.querySelector('#idle-photo');
    if (input) input.disabled = true;
    try {
      await imageReady;
      if (file) await window.SMART_IDLE_IMAGE.validate(file);
      await window.SMART_IDLE_IMAGE.access(file ? 'write' : 'remove', file);
      setIdleImage(file);
      imageMessage = file ? 'Ihr Foto ist auf diesem Gerät gespeichert.' : 'Das Foto wurde von diesem Gerät entfernt.';
    } catch (error) {
      imageMessage = ['QuotaExceededError', 'UnknownError', 'SecurityError', 'InvalidStateError'].includes(error.name)
        ? 'Das Foto konnte nicht gespeichert werden. Bitte ein kleineres Bild auswählen oder den Website-Speicher prüfen.'
        : error.message;
    } finally {
      imageBusy = false;
      if (route === 'settings' || route === 'idle') render(route, false);
    }
  }
  document.addEventListener('change', async event => {
    if (event.target.id === 'idle-photo') {
      const file = event.target.files[0];
      if (file) await updatePhoto(file);
      return;
    }
    if (event.target.id === 'idle-motion') {
      preferences.idleMotion = event.target.value === 'on';
      savePreferences(); return;
    }
    if (event.target.id !== 'text-size') return;
    preferences.textSize = event.target.value === 'large' ? 'large' : 'normal';
    savePreferences();
  });
  dialog.addEventListener('cancel', event => { event.preventDefault(); closeDialog(); });
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const controls = [...dialog.querySelectorAll('button:not(:disabled)')];
    const first = controls[0];
    const last = controls.at(-1);
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault(); first.focus();
    }
  });
  window.addEventListener('hashchange', () => {
    closeDialog(false); stopMedia(); render(location.hash.slice(1));
  });
  window.addEventListener('pagehide', stopMedia);
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopMedia(); });
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); installPrompt = event;
    if (route === 'settings') render(route, false);
  });
  function updateConnection() {
    document.querySelector('#connection-status').textContent = offlineReady
      ? `Offline bereit${navigator.onLine ? '' : ' · Keine Internetverbindung'}`
      : navigator.onLine ? '' : 'Offline · Zum erstmaligen Laden bitte eine Verbindung herstellen.';
  }
  window.addEventListener('online', updateConnection);
  window.addEventListener('offline', updateConnection);
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js', { scope: './' }).then(async () => {
      await navigator.serviceWorker.ready;
      offlineReady = true; updateConnection();
    }).catch(() => {
      document.querySelector('#connection-status').textContent = 'Offline-Einrichtung nicht möglich. Bitte die Seite bei bestehender Verbindung neu öffnen.';
    });
  }
  // Every launch starts calmly, regardless of a previous view's URL fragment.
  history.replaceState(null, '', '#idle');
  render('idle', false); updateConnection();
})();
