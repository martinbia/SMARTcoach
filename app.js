(() => {
  'use strict';
  const { events } = window.SMART_DEMO;
  let today = window.SMART_DEMO.today;
  const content = window.SMART_CONTENT;
  const escape = content.escape;
  const dashboards = window.SMART_DASHBOARDS;
  const app = document.querySelector('#app');
  const dialog = document.querySelector('#confirmation');
  const storageKey = 'smartcoach.preferences.v1';
  const defaults = { role: 'patient', activeByRole: { patient: false, relative: false }, textSize: 'normal', idleMotion: true, proactiveDialogue: 'none', waitSeconds: 60 };
  const freshPreferences = () => ({ ...defaults, activeByRole: { ...defaults.activeByRole } });
  let preferences = freshPreferences();
  let storageAvailable = true;
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    if (saved && typeof saved === 'object') {
      preferences = {
        role: saved.role === 'relative' ? 'relative' : 'patient',
        activeByRole: saved.activeByRole && typeof saved.activeByRole === 'object'
          ? { patient: saved.activeByRole.patient === true, relative: saved.activeByRole.relative === true }
          : { patient: saved.role !== 'relative' && saved.active === true, relative: saved.role === 'relative' && saved.active === true },
        textSize: saved.textSize === 'large' ? 'large' : 'normal',
        idleMotion: saved.idleMotion !== false,
        proactiveDialogue: /^[A-Z]$/.test(saved.proactiveDialogue || '') ? saved.proactiveDialogue : 'none',
        waitSeconds: Number.isInteger(saved.waitSeconds) && saved.waitSeconds >= 5 && saved.waitSeconds <= 3600 ? saved.waitSeconds : 60
      };
    }
  } catch { storageAvailable = false; }
  let level = 0;
  let windowOffset = 0;
  let route = 'idle';
  let detailOrigin = 'home';
  let installPrompt = null;
  let dialogOpener = null;
  let offlineReady = false;
  let contentError = '';
  let contentBusy = false;
  let videoKeys = new Set();
  let videoMessage = '';
  let videoBusy = false;
  let playerURL = null;
  let playerRequest = 0;
  let idleImageURL = null;
  let imageMessage = '';
  let imageBusy = false;
  let dialogueId = null;
  let dialogueStep = 1;
  let dialogueMode = 'text';
  let dialogueVideoReturn = false;
  let xrayURL = null;
  let xrayName = '';
  let xrayMessage = '';
  let xrayBusy = false;
  let speechRequest = 0;
  let promptAudioRecords = new Map();
  let promptAudioMessage = '';
  let promptAudioBusy = false;
  let promptAudioURL = null;
  let promptAudioId = null;
  let promptAudioReady = false;
  const promptAudioLoaded = window.SMART_PROMPT_AUDIO.keys().then(async keys => {
    const records = await Promise.all(keys.map(async id => [id, await window.SMART_PROMPT_AUDIO.get(id)]));
    promptAudioRecords = new Map(records);
    promptAudioReady = true;
    if (route === 'settings') render(route, false);
  }).catch(() => {
    promptAudioMessage = 'Der lokale WAV-Speicher ist nicht verfügbar. Dateien können nur vorübergehend für diese Sitzung bereitstehen.';
    promptAudioReady = true;
    if (route === 'settings') render(route, false);
  });
  function setXray(record) {
    if (xrayURL) URL.revokeObjectURL(xrayURL);
    xrayURL = record?.blob instanceof Blob ? URL.createObjectURL(record.blob) : null;
    xrayName = xrayURL ? record.name || 'Lokales Demo-Bild' : '';
  }
  const xrayReady = window.SMART_XRAY.access('read').then(record => {
    setXray(record);
    if (route === 'settings' || route === 'xray') render(route, false);
  }).catch(() => { xrayMessage = 'Der lokale Speicher für das Demo-Röntgenbild ist nicht verfügbar.'; });
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
  function horizonEnd() {
    const start = events.find(event => event.id === 'J01').date;
    const result = new Date(`${start}T12:00:00Z`);
    const day = result.getUTCDate();
    result.setUTCDate(1);
    result.setUTCMonth(result.getUTCMonth() + 6);
    const lastDay = new Date(Date.UTC(result.getUTCFullYear(), result.getUTCMonth() + 1, 0)).getUTCDate();
    result.setUTCDate(Math.min(day, lastDay));
    return result.toISOString().slice(0, 10);
  }
  // Local outline icons; labels stay visible alongside every primary action.
  const icons = {
    companion: '<path d="M21 11a8 8 0 0 1-8 8H8l-5 3 1-6a8 8 0 1 1 17-5Z"/><path d="M8 10h8m-8 4h5"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 11h18m-13 5h2m4 0h2"/>',
    ask: '<path d="M21 11a8 8 0 0 1-8 8H8l-5 3 1-6a8 8 0 1 1 17-5Z"/><path d="M10 8a2 2 0 1 1 3 2c-1 1-1 1-1 2m0 3h.01"/>',
    exercises: '<circle cx="14" cy="4" r="2"/><path d="m10 10 3-3 3 4 4 1m-7-5-2 7-4 6m4-6 5 2 1 5M6 8l4 2"/>',
    reports: '<path d="M14 3H5v18h14V8Zm0 0v5h5M8 12h8m-8 4h8"/>',
    diary: '<rect x="5" y="3" width="15" height="18" rx="2"/><path d="M3 7h4m-4 5h4m-4 5h4M11 8h5m-5 4h5"/>',
    heart: '<path d="M12 21 3 12a5 5 0 0 1 9-6 5 5 0 0 1 9 6Z"/><path d="m5 12 4-1 2 4 3-7 2 4h3"/>',
    cup: '<path d="M4 9h12v7a5 5 0 0 1-10 0V9m10 1h2a3 3 0 0 1 0 6h-2M3 22h17M7 3v3m5-3v3"/>',
    flag: '<path d="M5 22V3m0 0h14l-2 4 2 4H5"/>',
    settings: '<circle cx="12" cy="12" r="3"/><path d="m10 3-1 3-3 1-3 3 2 3-1 3 3 2 3-1 3 2 3-2 1-3 3-2-1-3-3-1-1-3Z"/>'
  };
  const icon = name => `<svg class="action-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[name]}</svg>`;
  const symbolMarkup = symbol => symbol === '↗'
    ? '<svg class="symbol" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
    : symbol;
  const isRelative = () => preferences.role === 'relative';
  const active = () => preferences.activeByRole[preferences.role];
  const profile = () => dashboards[preferences.role];

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
    speechRequest++;
    // All future players must stay inside the document so this global stop owns them.
    document.querySelectorAll('audio, video').forEach(media => {
      media.pause();
      try { media.currentTime = 0; } catch { /* Metadata may not be loaded yet. */ }
    });
    stopPromptAudioPreview();
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  }
  function stopPromptAudioPreview() {
    if (promptAudioURL) URL.revokeObjectURL(promptAudioURL);
    promptAudioURL = null;
    promptAudioId = null;
    const player = document.querySelector('#prompt-wav-player');
    if (player) {
      player.pause();
      try { player.currentTime = 0; } catch { /* Metadata may not be loaded yet. */ }
      player.removeAttribute('src');
      player.load();
    }
  }
  function closeDialog(restoreFocus = true) {
    dialog.close();
    if (restoreFocus && dialogOpener?.isConnected) dialogOpener.focus();
  }
  function navigate(next) {
    if (dialog.open) closeDialog(false);
    stopMedia();
    if (next.startsWith('event-') || next.startsWith('week-')) detailOrigin = ['journey', 'week'].includes(route) ? route : 'home';
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
  function roleSwitch() {
    return `<div class="role-switch" role="group" aria-label="Person wechseln">
      <span class="switch-label">Person wechseln</span>
      ${button('Ernst', 'role-patient', '', `aria-pressed="${!isRelative()}"`)}
      ${button('Anna', 'role-relative', '', `aria-pressed="${isRelative()}"`)}
    </div>`;
  }
  function header() {
    const person = profile();
    if (route.startsWith('video-')) return `<header class="topbar video-header"><div class="topbar-inner">
      <div class="brand"><img src="./assets/icon.svg" alt=""><strong>SMART<span>coach</span></strong></div>
      ${button('← Zurück zur Übersicht', 'home', 'video-back')}${roleSwitch()}${button('Beenden', 'stop', 'stop')}
      </div></header>`;
    if (route === 'home' && content.loaded) return `<header class="topbar home-header"><div class="masthead">
      <div class="brand"><img src="./assets/icon.svg" alt=""><strong>SMART<span>coach</span></strong></div>
      <span class="masthead-title">Meine Rehabilitation zu Hause</span>
      <nav class="header-actions" aria-label="Globale Aktionen">${button(icon('settings') + 'Einstellungen', 'settings')}${button('? Hilfe', 'help')}</nav>
      </div><div class="profile-bar"><div class="person-profile">
      <img class="avatar" src="./assets/profile-${isRelative() ? 'anna' : 'ernst'}.svg" alt="Illustration von ${person.name}">
      <h1 id="page-title" tabindex="-1">${person.name}</h1><div class="person-caption"><strong>${person.role}</strong><span>${person.subtitle}</span></div>
      </div>${roleSwitch()}</div></header>`;
    return `<header class="topbar"><div class="topbar-inner">
      <div class="brand"><img src="./assets/icon.svg" alt=""><strong>SMART<span>coach</span></strong></div>
      ${roleSwitch()}<nav class="header-actions" aria-label="Globale Aktionen">
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
  function sharedAppointments() {
    // Only dated appointments already backed by the demo record, never image dates.
    return events.filter(event => event.id === 'J10');
  }
  function appointmentButtons() {
    return sharedAppointments().map(event => button(`<span>${date(event.date)}</span><strong>${event.label}</strong><span aria-hidden="true">›</span>`, `event-${event.id}`, 'appointment')).join('');
  }
  function summaryJourney() {
    const relative = isRelative();
    const hospital = ['J01', 'J02', 'J05'];
    const selection = ['J01', 'J02', 'J05', 'J09', 'J10', 'J12', 'J13'].map(id => events.find(event => event.id === id));
    const points = relative ? dashboards.week : [...selection, { id: 'horizon', label: 'Meine Ziele', category: 'Offener Planungshorizont', symbol: '☆' }];
    return `<section class="card summary-journey ${relative ? 'weekly' : 'recovery'}" aria-labelledby="summary-title">
      <div class="summary-heading"><h2 id="summary-title">${profile().journeyTitle}</h2><span>${relative ? 'Wiederkehrender Wochenrahmen' : 'Rehabilitation zu Hause · fiktive Geschichte'}</span></div>
      <div class="summary-map"><svg class="journey-line" viewBox="0 0 1200 120" preserveAspectRatio="none" aria-hidden="true"><path d="M20 60 C180 85 250 30 390 56 S650 85 790 55 S1020 85 1180 60"/></svg>
      <div class="summary-nodes ${relative ? '' : 'recovery-nodes'}">${points.map(point => {
        const todayPoint = relative ? point.id === 'A04' : point.id === 'J09';
        const future = !relative && (!point.date || point.date > today);
        const action = relative ? `week-${point.id}` : point.id === 'horizon' ? 'goals' : `event-${point.id}`;
        const label = point.id === 'J05' ? 'Austritt' : point.id === 'J10' ? 'Physio-therapie' : point.label;
        return button(`<span class="summary-today">${todayPoint ? 'Heute' : ''}</span>
          <span class="node-dot" aria-hidden="true">${relative ? icon(point.icon) : symbolMarkup(point.symbol)}</span>
          <span class="node-label">${label}</span><span class="node-date">${relative ? point.caption : point.date ? date(point.date).slice(0, 6) : '6 Monate · Ziele offen'}</span>`, action,
          `journey-node ${hospital.includes(point.id) ? 'hospital-node' : ''} ${todayPoint ? 'today' : ''} ${future ? 'future' : ''}`, todayPoint && !relative ? 'aria-current="date"' : '');
      }).join('')}</div></div>
      <div class="phase-ribbon" aria-hidden="true">${relative ? '<span>Planen</span><span>Unterstützen</span><span>Eigene Balance</span>' : '<span>Spital</span><span>Zu Hause ankommen</span><span>Alltag aufbauen</span><span>Persönliche Ziele</span>'}</div>
      <div class="summary-bottom"><p>${relative ? 'Eine Woche begleiten – mit Raum für die eigenen Bedürfnisse.' : 'Schematischer Weg, kein Heilungsgrad. Weitere Physiotermine nach Vereinbarung.'}</p>${button('→ Zum detaillierten Weg', 'journey', 'primary')}</div>
    </section>`;
  }
  function home() {
    const person = profile();
    return `${summaryJourney()}<div class="context-grid">
      <section class="context-card week-card"><h2>${icon('calendar')}Diese Woche <small>${isRelative() ? 'Eigene Balance' : 'Fragen und Ziele'}</small></h2>
      ${button(person.tasks.map(task => `<span class="task-line"><span aria-hidden="true">○</span>${task}</span>`).join(''), 'week', 'week-tasks', 'aria-label="Wochenaufgaben ansehen"')}</section>
      <section class="context-card appointments-card"><h2>${icon('calendar')}Nächste Termine</h2>${appointmentButtons()}<p>Weitere Termine sind noch nicht hinterlegt.</p></section>
      </div><nav class="primary-actions" aria-label="Hauptfunktionen">${person.actions.map(([action, title, description]) => button(`${icon(action)}<span class="action-title">${title}</span><small>${description}</small><span class="action-chevron" aria-hidden="true">›</span>`, action, `function-tile tile-${action}`)).join('')}</nav>
      <section class="companion-bar" aria-label="Aktive Begleitung">
      ${button(`${icon('companion')}<strong>Aktive Begleitung</strong><span class="badge ${active() ? 'on' : ''}" role="status">${active() ? 'EIN' : 'AUS'}</span>`, 'companion-details', 'companion', 'aria-haspopup="dialog"')}
      <span class="companion-note">${active() ? 'Zustimmung gespeichert.' : 'Nur auf Ihre Initiative.'} Noch keine automatische Ansprache.</span>${button('Beenden', 'stop', 'stop')}</section>`;
  }
  function roleDetail(title, body, back = 'home', className = '') {
    return `<div class="detail ${className}">${button(back === 'journey' ? '← Zurück zum Weg' : '← Zurück zur Übersicht', back, 'back')}<section class="card"><span class="eyebrow">${profile().name} · Fiktive Demo</span><h1 id="page-title" tabindex="-1">${title}</h1>${body}</section></div>`;
  }
  function weekDetails() {
    const start = shiftDate(today, -((new Date(`${today}T12:00:00Z`).getUTCDay() + 6) % 7));
    const weekList = dashboards.week.map(point => button(`${icon(point.icon)}<span><strong>${point.label}</strong><small>${point.caption}</small></span>`, `week-${point.id}`, 'week-detail-item')).join('');
    return roleDetail(isRelative() ? 'Meine Begleit-Woche' : 'Diese Woche',
      `<p>${date(start)} bis ${date(shiftDate(start, 6))} · Demo-Woche</p>
      ${isRelative() ? `<p>Ein wiederkehrender Wochenrahmen für Anna. Er erfasst weder einen Heilungsgrad noch erledigte Aufgaben.</p><div class="week-detail-list">${weekList}</div>` : `<ul>${profile().tasks.map(task => `<li>${task}</li>`).join('')}</ul><p>Vorschläge für das Demo-Gespräch, keine neuen Therapieanweisungen. Es werden noch keine Aufgaben abgehakt oder Einträge gespeichert.</p>`}
      <h2>Gemeinsame medizinische Termine</h2>${appointmentButtons()}`);
  }
  function journeyDetails() {
    if (isRelative()) return weekDetails();
    return `<div class="journey-detail">${button('← Zurück zur Übersicht', 'home', 'back')}<h1 id="page-title" tabindex="-1">Ernsts detaillierter Weg</h1>${journey()}<section class="card all-events"><h2>Alle Ereignisse und Meilensteine</h2><p>Alle vorhandenen Demo-Einträge, einschliesslich weiterer Planung. Zusätzliche Physiotermine sind offen.</p><div>${events.map(event => button(`${event.dateLabel || date(event.date)} · ${event.label}`, `event-${event.id}`)).join('')}</div></section></div>`;
  }
  function detail(event) {
    return `<div class="detail">${button(detailOrigin === 'home' ? '← Zurück zur Übersicht' : '← Zurück zum Weg', detailOrigin, 'back')}<article class="card"><span class="eyebrow">${event.category} · ${event.dateLabel || date(event.date)}</span>
      <h1 id="page-title" tabindex="-1">${event.label}</h1><p>${event.text}</p>
      ${isRelative() ? '<p class="muted">Annas Perspektive: Dieselbe Geschichte hilft Ihnen, Ernsts Weg nachzuvollziehen. Eigene Fragen dürfen dabei Raum haben.</p>' : ''}
      <div class="source"><strong>Quelle · fiktive Beispieldaten</strong><p>${event.source}</p></div>
      ${event.reports.map(id => button(`Bericht ${id} ansehen`, `report-${id}`)).join('')}
      ${entryCards(content.entries.filter(entry => entry.meta.Journey === event.id && entry.role === preferences.role))}
      ${button('SMARTcoach fragen', 'ask', 'primary')}</article></div>`;
  }
  function releasePlayer() {
    playerRequest++;
    stopMedia();
    if (playerURL) { URL.revokeObjectURL(playerURL); playerURL = null; }
  }
  async function loadContent() {
    if (contentBusy) return;
    contentBusy = true;
    contentError = '';
    try {
      await content.load();
      today = events.find(event => event.id === 'J09').date;
      try { videoKeys = new Set(await window.SMART_VIDEOS.keys()); }
      catch { videoMessage = 'Der lokale Videospeicher ist nicht verfügbar.'; }
    } catch (error) { contentError = `Die redaktionellen Inhalte konnten nicht geladen werden: ${error.message}`; }
    contentBusy = false;
    if (route !== 'idle') render(route, false);
  }
  function reportPage(report) {
    const person = isRelative() ? 'Anna' : 'Ernst';
    return roleDetail(report.title ? escape(report.title) : report.id,
      `<p class="muted">${report.id} · ${date(report.date)} · Fiktiver Beispielbericht</p>` +
      ['Im Dokument steht', 'Einfach erklärt', `Für ${person}`, 'Frage für den Termin'].map(section => `<section class="report-section"><h2>${section}</h2>${content.markdown(report.sections[section])}</section>`).join('') +
      button('Zur Berichtsübersicht', 'reports') + ' ' + button('Zum zugehörigen Ereignis', `event-${report.meta.Journey}`));
  }
  function reportsPage() {
    return roleDetail('Berichte & Erklärungen', '<p>Erfundene Dokumente zur gemeinsamen Geschichte von Ernst und Anna. Wählen Sie einen Bericht für die Erklärung und den Quellenbezug.</p><div class="content-list">' +
      content.reports.map(report => button(`<strong>${escape(report.title)}</strong><small>${report.id} · ${date(report.date)} · Demo</small>`, `report-${report.id}`, 'content-choice')).join('') + '</div>');
  }
  function entryCards(entries) {
    return entries.map(entry => `<article class="entry-card"><p class="eyebrow">${date(entry.date)} · ${escape(entry.meta.Person)} · ${escape(entry.meta.Typ)}</p>
      <h2>${escape(entry.title)}</h2>${content.markdown(entry.sections.Eintrag)}
      ${entry.sections.Einordnung ? `<p class="small muted">${escape(entry.sections.Einordnung)}</p>` : ''}
      <p class="small muted">${entry.id} · Bezug ${entry.meta.Journey} · Fiktive Beispieldaten${entry.meta.Privat === 'ja' ? ` · Nur ${escape(entry.meta.Person)}s Demo-Ansicht` : ''}</p>
      ${button('Ereignis im Weg ansehen', `event-${entry.meta.Journey}`)}</article>`).join('');
  }
  function diaryPage() {
    return roleDetail(isRelative() ? 'Mein Eintrag zum Begleitweg' : 'Mein Eintrag zum Genesungsweg',
      '<p>Hier sehen Sie vorbereitete Beispiel-Einträge aus der fiktiven Geschichte. Eigene Einträge werden in dieser Version noch nicht erfasst.</p>' +
      (isRelative() ? '<p class="small muted">Eigene Sorgen erscheinen nur in Annas Ansicht. Der Personenwechsel am gemeinsamen Tablet ist keine echte Zugriffskontrolle.</p>' : '') +
      entryCards(content.entries.filter(entry => entry.role === preferences.role)));
  }
  function videosPage() {
    const videos = content.videos.filter(video => video.roles.includes(preferences.role));
    return roleDetail(isRelative() ? 'Anleitungen' : 'Übungen',
      `<table class="video-catalog"><caption class="visually-hidden">${isRelative() ? 'Anleitungen für Anna' : 'Übungsvideos für Ernst'}</caption>
      <thead class="visually-hidden"><tr><th scope="col">Video</th><th scope="col">Wiedergabe</th></tr></thead>
      <tbody>${videos.map(video => `<tr class="video-row"><th scope="row">${escape(video.title)}</th>
      <td>${button('Video ansehen', `video-${video.id}`, 'primary', `aria-label="Video ansehen: ${escape(video.title)}"`)}</td></tr>`).join('')}</tbody></table>`, 'home', 'media-detail video-library');
  }
  function videoPage(video) {
    if (!video.roles.includes(preferences.role)) return roleDetail('Video-Thema für Ernst', '<p>Dieses Thema finden Sie in Ernsts Übungsbibliothek.</p>');
    return `<section class="video-stage" aria-label="${escape(video.title)}"><h1 id="page-title" class="visually-hidden" tabindex="-1">${escape(video.title)}</h1>
      <video id="local-player" controls playsinline preload="metadata" aria-label="${escape(video.title)}" hidden></video>
      <div id="video-placeholder"><p id="video-placeholder-message" role="status">Lokale Datei wird geprüft …</p>${button('Videos in Einstellungen verwalten', 'settings')}</div>
      </section><section class="video-controls"><h2>${escape(video.title)}</h2>
      ${button('Video erneut starten', 'play-video', 'primary', 'disabled')}<p id="video-status" role="status"></p>
      ${content.markdown(video.sections.Hinweis)}
      <details><summary>Dateiname und Zuordnung</summary><p id="selected-video-file" class="media-filename"></p><p class="media-filename">Katalog: ${escape(video.meta.Datei)}</p>${button('Videos in Einstellungen verwalten', 'settings')}</details>
      ${button('Alle Videos anzeigen', 'exercises')}</section>`;
  }
  function videoStatus(message, unavailable = false) {
    const status = document.querySelector('#video-status');
    if (!status) return;
    status.textContent = message;
    status.hidden = unavailable;
    document.querySelector('#video-placeholder').hidden = !unavailable;
    document.querySelector('#video-placeholder-message').textContent = unavailable ? message : '';
  }
  async function playVideo(player, restart = false) {
    if (!player?.isConnected || document.hidden) return;
    if (restart) player.currentTime = 0;
    try { await player.play(); }
    catch (error) {
      // The media error listener supplies the more specific decoder/read error.
      if (!player.isConnected || error.name === 'AbortError' || player.error) return;
      videoStatus(error.name === 'NotAllowedError'
        ? 'Der Browser benötigt einen weiteren Tipp zum Starten. Bitte die Wiedergabetaste im Video oder „Video erneut starten“ antippen.'
        : 'Die Filmdatei kann nicht abgespielt werden. Bitte in den Einstellungen erneut zuordnen. Falls nötig, eine kompatible MP4-Version mit H.264/AAC verwenden.');
    }
  }
  async function mountVideo(video) {
    const request = playerRequest;
    const player = document.querySelector('#local-player');
    if (!player) return;
    try {
      const record = await window.SMART_VIDEOS.get(video.id);
      if (request !== playerRequest || !player.isConnected) return;
      const status = document.querySelector('#video-status');
      if (!(record?.blob instanceof Blob)) { videoStatus(videoBusy ? 'Die Filme werden noch eingelesen. Dieser Player wird danach automatisch bereitgestellt.' : 'Diese Datei wurde noch nicht ausgewählt. Bitte die passende MP4-Datei in den Einstellungen zuordnen.', true); return; }
      playerURL = URL.createObjectURL(record.blob);
      document.querySelector('#selected-video-file').textContent = `Ausgewählte Datei: ${record.name || video.meta.Datei}`;
      player.addEventListener('error', () => {
        if (!status.isConnected) return;
        player.hidden = true;
        document.querySelector('[data-action="play-video"]').disabled = true;
        videoStatus(player.error?.code === 3
          ? 'Der Browser kann dieses Video nicht decodieren. Bitte eine MP4-Version mit H.264-Video und gegebenenfalls AAC-Ton verwenden.'
          : 'Die Filmdatei kann nicht gelesen werden oder ihr Format wird nicht unterstützt. Bitte die Originaldatei in den Einstellungen erneut zuordnen. Bleibt der Fehler bestehen, wird eine kompatible MP4-Version (H.264/AAC) benötigt.', true);
      }, { once: true });
      player.src = playerURL;
      player.hidden = false;
      player.load();
      player.addEventListener('ended', () => {
        if (dialogueVideoReturn && request === playerRequest && player.isConnected) navigate('home');
      }, { once: true });
      document.querySelector('[data-action="play-video"]').disabled = false;
      videoStatus(record.persistent ? 'Der Film ist lokal gespeichert.' : 'Bereit für diese Sitzung. Dauerhaftes Speichern war nicht möglich; Sie können den Film trotzdem abspielen. Nach einem Neustart bitte in den Einstellungen erneut auswählen.');
      await playVideo(player);
    } catch { if (request === playerRequest) videoStatus('Die gespeicherte Datei kann nicht gelesen werden. Bitte die Originaldatei in den Einstellungen erneut zuordnen.', true); }
  }
  async function chooseSingleVideo(file, id) {
    if (!file || videoBusy) return;
    const video = content.videos.find(item => item.id === id);
    if (!video) return;
    videoBusy = true;
    document.querySelectorAll('#video-settings input').forEach(picker => { picker.disabled = true; });
    document.querySelector('#video-import-status').textContent = 'Die ausgewählte Datei wird eingelesen …';
    try {
      const record = await window.SMART_VIDEOS.choose(file, id);
      videoKeys.add(id);
      videoMessage = record.persistent ? `${video.title}: Film lokal gespeichert.` : `${video.title}: Film nur für diese Sitzung ausgewählt und abspielbar.`;
    } catch (error) {
      videoMessage = `Die Datei konnte nicht geöffnet werden. ${error.message} Bitte die lokale Originaldatei erneut auswählen.`;
    } finally {
      videoBusy = false;
      finishVideoImport();
    }
  }
  function finishVideoImport() {
    if (route === 'settings' || route === 'exercises') render(route, false);
    else if (route.startsWith('video-') && !document.querySelector('#local-player')?.getAttribute('src')) {
      const video = content.videos.find(item => `video-${item.id}` === route);
      if (video) mountVideo(video);
    }
  }
  async function importVideos(files) {
    if (videoBusy || !files.length) return;
    videoBusy = true;
    document.querySelectorAll('#video-settings input').forEach(picker => { picker.disabled = true; });
    const status = document.querySelector('#video-import-status');
    if (status) status.textContent = 'Filme werden nur auf diesem Gerät gespeichert …';
    try {
      const result = await window.SMART_VIDEOS.importFiles([...files], content.videos);
      [...result.imported, ...result.temporary].forEach(id => videoKeys.add(id));
      videoMessage = `${result.imported.length} Film(e) lokal gespeichert. ${result.ignored.length} Datei(en) ohne passende Zuordnung. ${result.failed.length} Datei(en) konnten nicht gespeichert werden.`;
      if (result.temporary.length) videoMessage += ` ${result.temporary.length} Film(e) sind nur für diese Sitzung ausgewählt und trotzdem abspielbar.`;
      if (result.ignored.length) videoMessage += ` Nicht zugeordnet: ${result.ignored.join(', ')}. Bitte unten beim jeweiligen Film zuordnen.`;
      if (result.failed.length) videoMessage += ` Nicht lesbar: ${result.failed.join(', ')}. Bitte die lokale MP4-Datei und ihre Grösse prüfen.`;
    } catch { videoMessage = 'Die Filme konnten nicht lokal gespeichert werden. Bitte den Website-Speicher prüfen.'; }
    finally {
      videoBusy = false;
      finishVideoImport();
    }
  }
  function placeholder(page) {
    const [, symbol] = actions.find(([id]) => id === page);
    const [, title] = profile().actions.find(([id]) => id === page);
    const copy = {
      ask: 'Hier können Sie später vorbereitete Fragen auswählen und die dazugehörigen Demo-Antworten lesen. In dieser Version gibt es noch keinen Chat und keine KI-Antworten.',
    };
    return `<div class="detail">${button('← Zurück zur Übersicht', 'home', 'back')}<section class="card"><span class="eyebrow">Vorschau · Phase A</span><h1 id="page-title" tabindex="-1"><span aria-hidden="true">${symbolMarkup(symbol)}</span> ${title}</h1>
      <div class="placeholder"><h2>Dieser Bereich entsteht als Nächstes.</h2><p>${copy[page]}</p></div>
      <p class="muted" style="margin-top:24px">${isRelative() ? 'Sie betrachten diesen Bereich als Anna, Angehörige von Ernst.' : 'Sie betrachten diesen Bereich als Ernst, Patient.'}</p>
      ${button('Zur Journey', 'home', 'primary')}</section></div>`;
  }
  const currentDialogue = () => content.dialogues.find(item => item.id === dialogueId);
  function localVoice() {
    return window.speechSynthesis?.getVoices().find(voice => voice.localService && /^de(?:-|$)/i.test(voice.lang));
  }
  function dialoguePage() {
    const layout = body => `<div class="detail dialogue-demo"><section class="card"><div class="dialogue-heading"><h1 id="page-title" tabindex="-1">Fragen stellen</h1>${button('← Zurück zur Übersicht', 'home', 'back')}</div>${body}</section></div>`;
    if (isRelative()) return layout('<p>Die drei vorbereiteten Gespräche sind für Ernst angelegt. Für Anna sind noch keine eigenen Gesprächsabläufe hinterlegt. Wählen Sie oben Ernst und öffnen Sie dort „Fragen stellen“.</p>');
    const conversation = currentDialogue();
    const mode = `<div class="dialogue-modes" role="group" aria-label="Gesprächsdarstellung">${button('Chat', 'dialogue-mode-text', '', `aria-pressed="${dialogueMode === 'text'}"`)}${button('Voice-Demo', 'dialogue-mode-voice', '', `aria-pressed="${dialogueMode === 'voice'}"`)}</div>`;
    const note = '<p class="dialogue-notice">Interview-Demo: vorbereitete Gesprächsschritte, keine KI und keine freie Sprach- oder Texteingabe.</p>';
    if (!conversation) return layout(`${note}${mode}<p class="small">Gespräch auswählen und die Unterhaltung Schritt für Schritt vorführen.</p><div class="dialogue-topics">${content.dialogues.map(item => button(`<strong>${escape(item.title)}</strong><small>${escape(item.meta.Kurztext)}</small>`, `dialogue-select-${item.id}`)).join('')}</div>`);
    dialogueStep = Math.min(dialogueStep, conversation.steps.length);
    const visible = conversation.steps.slice(0, dialogueStep);
    const next = conversation.steps[dialogueStep];
    const lastSpeaker = visible.at(-1).speaker;
    return layout(`${note}<div class="dialogue-session"><h2>${escape(conversation.title)}</h2>${mode}</div>
      ${dialogueMode === 'voice' ? `<section class="dialogue-voice"><strong>Voice-Demo · ohne Mikrofonaufnahme</strong>${button(lastSpeaker === 'Ernst' ? 'Ernsts Beitrag vorlesen' : 'Coach vorlesen', 'dialogue-read', '', localVoice() ? '' : 'disabled')}${button('Vorlesen stoppen', 'dialogue-stop-voice')}<p id="dialogue-voice-status" class="small" role="status">${localVoice() ? 'Lokale deutsche Stimme verfügbar.' : 'Keine lokale deutsche Stimme verfügbar. Das Gespräch bleibt als Text vorführbar.'}</p></section>` : ''}
      <div class="dialogue-log" role="log" aria-label="Gespräch zwischen Ernst und SMARTcoach" aria-live="polite" aria-relevant="additions">${visible.map(step => `<article class="dialogue-message ${step.speaker === 'Ernst' ? 'message-ernst' : 'message-coach'}"><strong>${step.speaker === 'Ernst' ? 'Ernst' : 'SMARTcoach'}</strong>${content.markdown(step.text)}</article>`).join('')}</div>
      <p class="dialogue-progress" role="status">Schritt ${dialogueStep} von ${conversation.steps.length}</p>
      <div class="dialogue-navigation">${button('Vorheriger Schritt', 'dialogue-previous', '', dialogueStep <= 1 ? 'disabled' : '')}
      ${button(next ? next.speaker === 'Coach' ? 'Coach antwortet' : dialogueMode === 'voice' ? 'Ernst spricht (Demo)' : 'Ernst fragt weiter' : 'Fertig', 'dialogue-next', 'primary', next ? '' : 'disabled')}
      ${!next ? button(escape(conversation.meta.Aktionslabel), 'dialogue-media', 'primary') : ''}
      ${button('Gespräch neu starten', 'dialogue-restart')}${button('Andere Gespräche', 'dialogue-topics')}</div>`);
  }
  function redrawDialogue(action) {
    render('ask', false);
    const log = document.querySelector('.dialogue-log');
    if (log) log.scrollTop = log.scrollHeight;
    const target = document.querySelector(`[data-action="${action}"]:not(:disabled)`) || document.querySelector('[data-action="dialogue-media"]') || document.querySelector('[data-action="dialogue-next"]:not(:disabled)');
    target?.focus({ preventScroll: true });
  }
  function readDialogue() {
    const voice = localVoice();
    const conversation = currentDialogue();
    const last = conversation?.steps[dialogueStep - 1];
    const status = document.querySelector('#dialogue-voice-status');
    if (route !== 'ask' || document.hidden || !voice || !last || !status) return;
    stopMedia();
    const request = speechRequest;
    const speech = new SpeechSynthesisUtterance(last.text.replace(/\*\*/g, ''));
    speech.voice = voice; speech.lang = voice.lang; speech.rate = 0.9;
    speech.onend = () => { if (request === speechRequest && status.isConnected) status.textContent = 'Vorlesen beendet.'; };
    speech.onerror = () => { if (request === speechRequest && status.isConnected) status.textContent = 'Vorlesen wurde beendet oder ist nicht verfügbar. Der Text bleibt sichtbar.'; };
    status.textContent = `${last.speaker === 'Coach' ? 'SMARTcoach' : 'Ernst'} wird vorgelesen …`;
    window.speechSynthesis.speak(speech);
  }
  function xraySettings() {
    return `<div class="settings-row xray-settings"><div><h2>Röntgenbild für das Demo-Gespräch</h2><p>Wählen Sie einmalig eine Demo-Abbildung aus dem lokalen Ordner. Sie bleibt auf diesem Gerät; die EPIC-Suche im Gespräch ist simuliert.</p>
      <label for="xray-image">Demo-Röntgenbild auswählen (JPG, PNG oder WebP, bis 12 MB)</label><input id="xray-image" type="file" accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp" ${xrayBusy ? 'disabled' : ''}>
      ${xrayURL ? `<p class="media-filename">${escape(xrayName)}</p><img class="xray-preview" src="${xrayURL}" alt="Lokal ausgewählte Demo-Abbildung">${button('Demo-Röntgenbild entfernen', 'remove-xray', '', xrayBusy ? 'disabled' : '')}` : '<p class="small muted">Noch kein Demo-Bild ausgewählt.</p>'}
      <p id="xray-status" role="status">${escape(xrayMessage)}</p></div></div>`;
  }
  function xrayPage() {
    return roleDetail('Röntgenbild', `<p class="dialogue-notice">Simulierte EPIC-Suche · lokal ausgewähltes Demo-Bild · keine Verbindung zu EPIC.</p>
      ${xrayURL ? `<figure><img id="demo-xray" src="${xrayURL}" alt="Lokal ausgewählte Röntgen-Demo-Abbildung; keine medizinische Befundung"><figcaption class="media-filename">${escape(xrayName)}</figcaption></figure><p id="xray-view-status" role="status">Keine automatische Befundung oder Aussage zum Heilungsgrad.</p>` : '<p id="xray-view-status" role="status">Für die Vorführung ist noch kein Bild hinterlegt. Bitte das Demo-Röntgenbild einmalig in den Einstellungen auswählen.</p>'}
      ${button('Demo-Bild in Einstellungen auswählen', 'settings')}${button('Zurück zum Gespräch', 'ask')}`, 'home', 'xray-detail');
  }
  async function choosePromptAudio(file, id) {
    if (!file || promptAudioBusy || id === 'D5') return;
    await promptAudioLoaded;
    promptAudioBusy = true;
    stopPromptAudioPreview();
    try {
      const record = await window.SMART_PROMPT_AUDIO.choose(file, id);
      promptAudioRecords.set(id, record);
      promptAudioMessage = record.persistent
        ? `${id}.wav wurde lokal auf diesem Gerät gespeichert.`
        : `${id}.wav ist nur für diese Sitzung verfügbar. Die dauerhafte Speicherung ist fehlgeschlagen.`;
    } catch (error) {
      promptAudioMessage = `Die WAV-Datei konnte nicht verwendet werden. ${error.message || 'Bitte eine gültige WAV-Datei auswählen.'}`;
    } finally {
      promptAudioBusy = false;
      if (route === 'settings') render(route, false);
    }
  }
  async function removePromptAudio(id) {
    if (promptAudioBusy || id === 'D5') return;
    await promptAudioLoaded;
    promptAudioBusy = true;
    stopPromptAudioPreview();
    try {
      await window.SMART_PROMPT_AUDIO.remove(id);
      promptAudioRecords.delete(id);
      promptAudioMessage = `Die lokale WAV-Kopie für ${id} wurde entfernt. Die Originaldatei bleibt erhalten.`;
    } catch (error) {
      promptAudioMessage = `Die lokale WAV-Kopie für ${id} konnte nicht entfernt werden. ${error.message || ''}`;
    } finally {
      promptAudioBusy = false;
      if (route === 'settings') render(route, false);
    }
  }
  async function previewPromptAudio(id) {
    await promptAudioLoaded;
    const status = document.querySelector(`#prompt-audio-status-${id}`);
    if (promptAudioId === id) {
      stopPromptAudioPreview();
      if (status) status.textContent = promptAudioRecords.get(id)?.persistent ? 'Gespeichert · Probehören gestoppt' : 'Nur für diese Sitzung · Probehören gestoppt';
      const button = document.querySelector(`[data-action="prompt-wav-preview-${id}"]`);
      if (button) button.textContent = 'Probehören';
      return;
    }
    try {
      const record = promptAudioRecords.get(id) || await window.SMART_PROMPT_AUDIO.get(id);
      if (!record?.blob) throw new Error('Für diese Zeile ist keine WAV-Datei zugeordnet.');
      promptAudioRecords.set(id, record);
      stopPromptAudioPreview();
      const player = document.querySelector('#prompt-wav-player');
      if (!player) throw new Error('Der Audio-Player ist gerade nicht verfügbar.');
      promptAudioURL = URL.createObjectURL(record.blob);
      promptAudioId = id;
      player.src = promptAudioURL;
      player.onerror = () => {
        if (promptAudioId !== id) return;
        if (status?.isConnected) status.textContent = 'Die WAV-Datei ist gespeichert, lässt sich aber in diesem Browser nicht abspielen.';
        stopPromptAudioPreview();
      };
      await player.play();
      if (status?.isConnected) status.textContent = `${record.persistent ? 'Gespeichert' : 'Nur für diese Sitzung'} · Probehören läuft`;
      const button = document.querySelector(`[data-action="prompt-wav-preview-${id}"]`);
      if (button) button.textContent = 'Probehören stoppen';
      player.onended = () => {
        if (promptAudioId !== id) return;
        stopPromptAudioPreview();
        if (status?.isConnected) status.textContent = `${record.persistent ? 'Gespeichert' : 'Nur für diese Sitzung'} · Probehören beendet`;
        if (button?.isConnected) button.textContent = 'Probehören';
      };
    } catch (error) {
      stopPromptAudioPreview();
      if (status?.isConnected) status.textContent = `Wiedergabe nicht möglich. ${error.message || 'Bitte wählen Sie die Datei erneut aus.'}`;
    }
  }
  async function updateXray(file) {
    if (xrayBusy) return;
    xrayBusy = true;
    const input = document.querySelector('#xray-image');
    if (input) input.disabled = true;
    try {
      await xrayReady;
      const record = file ? await window.SMART_XRAY.prepare(file) : null;
      await window.SMART_XRAY.access(file ? 'write' : 'remove', record);
      setXray(record);
      xrayMessage = file ? 'Das Demo-Röntgenbild ist lokal gespeichert und auch nach einem Neustart verfügbar.' : 'Die lokale Demo-Kopie wurde entfernt. Die Originaldatei bleibt erhalten.';
    } catch (error) { xrayMessage = `Das Demo-Bild konnte nicht gespeichert werden. ${error.message}`; }
    finally { xrayBusy = false; if (route === 'settings' || route === 'xray') render(route, false); }
  }
  function videoSettings() {
    return `<section id="video-settings" class="settings-video-library"><h2>Lokale Übungsvideos</h2>
      <p>Wählen Sie die MP4-Filme aus dem Ordner mit Ihrem Luzern-Bild, zum Beispiel Documents/SMART. Sie bleiben auf diesem Gerät; es gibt keinen Upload.</p>
      <label for="local-videos">Lokale MP4-Filme auswählen</label><input id="local-videos" type="file" accept="video/mp4,.mp4" multiple ${videoBusy ? 'disabled' : ''}>
      <p id="video-import-status" role="status">${videoBusy ? 'Filme werden lokal gespeichert …' : escape(videoMessage)}</p>
      <details><summary>Einzelne Filme zuordnen oder ersetzen</summary><p>Bei abweichenden Dateinamen können Sie die passende MP4 hier ausdrücklich zuordnen. Bitte Titel und Filminhalt selbst vergleichen.</p>
      ${content.videos.map(video => `<div class="video-setting"><label for="local-video-${video.id}">${escape(video.title)}</label>
        <p class="media-filename">${videoKeys.has(video.id) ? window.SMART_VIDEOS.sessionInfo(video.id)?.persistent === false ? 'Für diese Sitzung ausgewählt' : 'Auf diesem Gerät gespeichert' : 'Noch keine lokale Datei ausgewählt'} · ${escape(window.SMART_VIDEOS.sessionInfo(video.id)?.name || video.meta.Datei)}</p>
        <input id="local-video-${video.id}" data-video-id="${video.id}" type="file" accept="video/mp4,.mp4" ${videoBusy ? 'disabled' : ''}>
        ${videoKeys.has(video.id) ? button('Lokale Kopie entfernen', `remove-video-${video.id}`, '', videoBusy ? 'disabled' : '') : ''}</div>`).join('')}
      </details><p class="small muted">Je Film höchstens 512 MB. Dauerhafte Kopien benötigen freien Website-Speicher. Bei Speicherproblemen bleiben eingelesene Filme nur für die laufende Sitzung verfügbar. Das Löschen von Website-Daten entfernt die Kopien, nicht die Originaldateien.</p>
      ${button('Alle Videos anzeigen', 'exercises')}</section>`;
  }
  function promptAudioSettings() {
    const catalogue = content.promptDialogues || [];
    const selected = catalogue.some(item => item.id === preferences.proactiveDialogue) ? preferences.proactiveDialogue : 'none';
    if (selected !== preferences.proactiveDialogue) preferences.proactiveDialogue = selected;
    const dialogue = catalogue.find(item => item.id === selected);
    const rows = dialogue ? dialogue.steps.map(step => {
      const record = step.locked ? null : promptAudioRecords.get(step.id);
      const persistent = record?.persistent === true;
      const status = step.locked ? 'Gesperrt · keine WAV-Zuordnung erlaubt'
        : record ? persistent ? 'Gespeichert' : 'Nur für diese Sitzung'
          : 'Nicht zugeordnet';
      return `<article class="prompt-audio-row ${step.locked ? 'is-locked' : ''}" data-step-id="${step.id}">
        <div class="prompt-audio-step"><h3>${step.id} · ${step.speaker}${step.locked ? ' · GESPERRT' : ''}</h3><p>${escape(step.text)}</p></div>
        <div class="prompt-audio-file"><p class="media-filename">${escape(record?.name || 'Keine WAV-Datei ausgewählt')}</p><p class="prompt-audio-status" id="prompt-audio-status-${step.id}" role="status">${status}</p></div>
        ${step.locked ? '<p class="prompt-audio-warning">D5 ist gesperrt und bleibt bis zu einer fachlichen Überarbeitung und ausdrücklichen Freigabe blockiert. Es kann keine WAV-Datei hinterlegt oder probegehört werden.</p>' : `<div class="prompt-audio-actions">
          ${button('WAV auswählen', `prompt-wav-choose-${step.id}`, '', promptAudioBusy ? 'disabled' : '')}<input class="prompt-audio-input" id="prompt-wav-${step.id}" data-prompt-audio-id="${step.id}" type="file" accept="audio/wav,audio/x-wav,.wav" aria-label="WAV-Datei für ${step.id} auswählen" ${promptAudioBusy ? 'disabled' : ''}>
          ${button(promptAudioId === step.id ? 'Probehören stoppen' : 'Probehören', `prompt-wav-preview-${step.id}`, '', !record || promptAudioBusy ? 'disabled' : '')}
          ${button('Zuordnung entfernen', `prompt-wav-remove-${step.id}`, '', !record || promptAudioBusy ? 'disabled' : '')}
        </div>`}
      </article>`;
    }).join('') : '<p class="muted">Wählen Sie einen Dialog, um seine Zeilen zu verwalten.</p>';
    return `<section class="settings-row proactive-settings" aria-labelledby="proactive-settings-title">
      <div class="proactive-settings-intro"><h2 id="proactive-settings-title">Automatische Ansprache – vorbereitete Dialoge</h2>
        <p>Hier ordnet die Interviewleitung den späteren Dialogzeilen lokale Sprachdateien zu. Dateien werden einzeln vom Gerät ausgewählt; ein Ordnerzugriff oder Upload findet nicht statt.</p>
        <p class="prompt-audio-notice">Die Auswahl und Wartezeit werden nur gespeichert. In dieser Version startet weder ein Timer noch ein Dialog automatisch. Aktive Begleitung löst weiterhin keine Ansprache aus.</p></div>
      <div class="prompt-audio-config">
        <div class="prompt-audio-config-row"><label for="proactive-dialogue">Dialog für automatische Ansprache</label><select id="proactive-dialogue">
          <option value="none" ${selected === 'none' ? 'selected' : ''}>Keiner</option>
          ${catalogue.map(item => `<option value="${item.id}" ${selected === item.id ? 'selected' : ''}>${item.id} – ${escape(item.title)}${item.id === 'D' ? ' (noch nicht vollständig freigegeben)' : ''}</option>`).join('')}
        </select></div>
        <div class="prompt-audio-config-row"><label for="proactive-wait">Wartezeit bis zur Ansprache (Sekunden)</label><input id="proactive-wait" type="number" min="5" max="3600" step="1" value="${preferences.waitSeconds}" inputmode="numeric" aria-describedby="proactive-wait-status"></div>
        <p id="proactive-wait-status" class="prompt-audio-status" role="status"></p>
        ${dialogue?.id === 'D' ? '<p class="prompt-audio-warning">Dialog D ist noch nicht vollständig freigegeben. D5 ist gesperrt; der Dialog kann daher nicht als vollständig abspielbar gelten.</p>' : ''}
        <p class="prompt-audio-status" id="prompt-audio-storage-status" role="status">${escape(promptAudioMessage || (promptAudioReady ? 'Lokaler WAV-Speicher bereit.' : 'Lokalen WAV-Speicher wird geprüft …'))}</p>
      </div>
      ${dialogue ? `<div class="prompt-audio-catalogue"><h3>Zeilen in Dialog ${dialogue.id} – ${escape(dialogue.title)}</h3>${rows}</div>` : ''}
      <audio id="prompt-wav-player" preload="none" hidden></audio>
    </section>`;
  }
  function settings() {
    return `<div class="detail">${button('← Zurück zur Übersicht', 'home', 'back')}<section class="card"><span class="eyebrow">So passt es für Sie</span><h1 id="page-title" tabindex="-1">Einstellungen</h1>
      <p>Ihre Auswahl bleibt auf diesem Gerät gespeichert.</p>
      <div class="settings-row"><div><h2>Demo-Inhalte aktualisieren</h2><p class="muted small">Lädt die Markdown-Texte neu. Lokale Fotos und Videos bleiben erhalten.</p><p class="small" role="status">${escape(contentError || 'Die redaktionellen Inhalte sind geladen.')}</p></div>${button('Inhalte neu laden', 'reload-content')}</div>
      <div class="settings-row"><div><h2><label for="text-size">Schriftgrösse</label></h2><p class="muted small">Alle Ansichten passen sich an.</p></div><select id="text-size"><option value="normal" ${preferences.textSize === 'normal' ? 'selected' : ''}>Gross</option><option value="large" ${preferences.textSize === 'large' ? 'selected' : ''}>Sehr gross</option></select></div>
      <div class="settings-row"><div><h2>Aktive Begleitung: ${active() ? 'EIN' : 'AUS'}</h2><p class="muted small">Noch ohne automatische Ansprache.</p></div>${button(active() ? 'Ausschalten' : 'Einschalten', 'companion')}</div>
      <div class="settings-row"><div><h2>Luzern-Bild im Ruhemodus</h2><p class="muted">Wählen Sie Ihr Luzern-Foto, zum Beispiel aus <strong>Documents/SMART</strong>. Es bleibt nur auf diesem Gerät und wird auch offline angezeigt.</p>
        ${idleImageURL ? `<img class="idle-photo-preview" src="${idleImageURL}" alt="Ihr ausgewähltes Ruhebild">` : '<p class="small muted">Noch kein Foto ausgewählt. Bis dahin bleibt der ruhige Farbhintergrund.</p>'}
        <label class="photo-picker" for="idle-photo">Luzern-Foto auswählen (JPG, PNG oder WebP, bis 12 MB)</label>
        <input id="idle-photo" type="file" accept="image/jpeg,image/png,image/webp" ${imageBusy ? 'disabled' : ''}>
        <p id="image-status" class="small" role="status"></p>
        ${idleImageURL ? button('Foto entfernen', 'remove-photo', '', imageBusy ? 'disabled' : '') : ''}
      </div></div>
      <div class="settings-row"><div><h2><label for="idle-motion">Ruhebildschirm animieren</label></h2><p class="muted small">Langsame Bildbewegung und wechselnder Text. Bei reduzierter Bewegung im Gerät bleibt die Ansicht ruhig.</p></div><select id="idle-motion"><option value="on" ${preferences.idleMotion ? 'selected' : ''}>Ein</option><option value="off" ${!preferences.idleMotion ? 'selected' : ''}>Aus</option></select></div>
      ${videoSettings()}
      ${xraySettings()}
      ${promptAudioSettings()}
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
  function layoutSummary() {
    const map = document.querySelector('.summary-map');
    if (!map) return;
    const grid = map.querySelector('.summary-nodes');
    const columns = Number(getComputedStyle(grid).getPropertyValue('--summary-columns'));
    const nodes = [...grid.querySelectorAll('.journey-node')];
    nodes.forEach((node, index) => {
      const row = Math.floor(index / columns);
      node.style.gridRow = row + 1;
      node.style.gridColumn = row % 2 ? columns - index % columns : index % columns + 1;
    });
    const bounds = map.getBoundingClientRect();
    const points = nodes.map(node => {
      const rect = node.querySelector('.node-dot').getBoundingClientRect();
      return { x: rect.x + rect.width / 2 - bounds.x, y: rect.y + rect.height / 2 - bounds.y };
    });
    const svg = map.querySelector('svg');
    svg.setAttribute('viewBox', `0 0 ${bounds.width} ${bounds.height}`);
    let path = '';
    points.forEach((point, index) => {
      if (!index) { path = `M ${point.x} ${point.y}`; return; }
      const previous = points[index - 1];
      if (Math.abs(previous.y - point.y) < 2) {
        const middle = (previous.x + point.x) / 2;
        path += ` C ${middle} ${previous.y - 12}, ${middle} ${point.y + 12}, ${point.x} ${point.y}`;
      } else {
        const direction = Math.floor((index - 1) / columns) % 2 ? -1 : 1;
        const outer = Math.max(4, Math.min(bounds.width - 4, point.x + direction * 50));
        path += ` C ${outer} ${previous.y}, ${outer} ${point.y}, ${point.x} ${point.y}`;
      }
    });
    svg.querySelector('path').setAttribute('d', path);
  }
  function sizeVideoStage() {
    const header = document.querySelector('.video-header');
    if (header) app.style.setProperty('--video-header-height', `${header.getBoundingClientRect().height}px`);
  }
  const resizeObserver = new ResizeObserver(() => { layoutJourney(); layoutSummary(); sizeVideoStage(); });
  function render(next, focus = true) {
    if (route === 'settings') stopPromptAudioPreview();
    const event = events.find(item => `event-${item.id}` === next);
    const weekPoint = dashboards.week.find(point => `week-${point.id}` === next);
    const report = content.reports.find(item => `report-${item.id}` === next);
    const video = content.videos.find(item => `video-${item.id}` === next);
    route = ['idle', 'home', 'settings', 'journey', 'week', 'goals', 'help', 'xray', ...actions.map(([id]) => id)].includes(next) || event || weekPoint || report || video ? next : 'idle';
    if (route === 'home' || route === 'idle') { dialogueId = null; dialogueStep = 1; }
    if (!route.startsWith('video-')) dialogueVideoReturn = false;
    resizeObserver.disconnect();
    releasePlayer();
    if (route === 'idle') {
      app.innerHTML = `<main class="idle ${idleImageURL ? 'has-photo' : ''} ${preferences.idleMotion ? '' : 'idle-static'}" id="content">
        ${idleImageURL ? `<img class="idle-photo" src="${idleImageURL}" alt="">` : ''}<div class="idle-wash" aria-hidden="true"></div>
        <button class="idle-open" data-action="home" aria-label="Bildschirm berühren – Übersicht öffnen"></button><div class="idle-content"><div class="brand"><img src="./assets/icon.svg" alt=""><strong>SMART<span>coach</span></strong></div><h1>In Ihrem Tempo.<br>Schritt für Schritt.</h1><p>Ein gemeinsamer Blick auf Ihren Weg.</p><span class="idle-prompt">Bildschirm berühren</span></div><p class="idle-note">Demo mit fiktiven Beispieldaten · Keine Ansprache im Ruhemodus</p>
        <button class="idle-motion-control" data-action="idle-toggle">${preferences.idleMotion ? 'Animation anhalten' : 'Animation starten'}</button></main>`;
    } else {
      const html = !content.loaded ? roleDetail(contentError ? 'Inhalte nicht verfügbar' : 'Inhalte werden geladen', `<p>${escape(contentError || 'Die Demo-Daten werden vorbereitet.')}</p>${contentError ? button('Erneut laden', 'reload-content', 'primary') : ''}`)
        : route === 'home' ? home() : route === 'settings' ? settings() : route === 'journey' ? journeyDetails() : route === 'week' ? weekDetails()
        : weekPoint ? roleDetail(weekPoint.label, `<p>${weekPoint.text}</p><div class="source"><strong>Quelle · fiktive Beispieldaten</strong><p>Annas Begleit-Woche · ${weekPoint.id} · Gestaltungsinhalt, keine medizinische Anordnung.</p></div>`, detailOrigin)
        : route === 'goals' ? roleDetail('Mein Planungshorizont', `<p>Die sechs Monate bilden einen offenen Zeitraum ab dem fiktiven Sturz am ${date(events.find(event => event.id === 'J01').date)} bis zum ${date(horizonEnd())} ab. Persönliche Ziele sind Wünsche, keine Heilungsversprechen oder bestätigten Termine.</p>`)
        : report ? reportPage(report) : video ? videoPage(video)
        : route === 'exercises' ? videosPage() : route === 'reports' ? reportsPage() : route === 'diary' ? diaryPage() : route === 'ask' ? dialoguePage() : route === 'xray' ? xrayPage()
        : route === 'help' ? roleDetail('SMARTcoach verwenden', '<p>Wählen Sie Ernst oder Anna. Tippen Sie auf eine Station oder eine der vier Hauptfunktionen. Der detaillierte Weg zeigt die vollständigen vorhandenen Demo-Einträge.</p><p>Mit Beenden gelangen Sie immer zum Ruhebildschirm. Aktive Begleitung benötigt Ihre Zustimmung und löst in dieser Version noch keine automatischen Dialoge aus.</p>')
        : event ? detail(event) : placeholder(route);
      app.innerHTML = `${header()}<main id="content" ${route === 'home' ? `class="dashboard role-${preferences.role}"` : video && video.roles.includes(preferences.role) ? 'class="video-view"' : ''}>${html}</main>${footer()}`;
      if (video && content.loaded && document.querySelector('#local-player')) {
        sizeVideoStage();
        resizeObserver.observe(document.querySelector('.video-header'));
        mountVideo(video);
      }
      const importStatus = document.querySelector('#video-import-status');
      if (importStatus) importStatus.textContent = videoMessage;
      document.querySelector('#demo-xray')?.addEventListener('error', event => {
        event.target.hidden = true;
        document.querySelector('#xray-view-status').textContent = 'Die gespeicherte Demo-Abbildung kann nicht gelesen werden. Bitte in den Einstellungen erneut auswählen.';
      }, { once: true });
      const map = document.querySelector('.journey-map');
      if (map) { layoutJourney(); resizeObserver.observe(map); }
      const summary = document.querySelector('.summary-map');
      if (summary) { layoutSummary(); resizeObserver.observe(summary); }
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
        : '<p>Die Perspektive wechselt zu Ernst. Die Journey zeigt wieder den gesamten Weg und Aktive Begleitung wird ausgeschaltet.</p><p>Schriftgrösse, Ruhebild und Animationseinstellung bleiben erhalten. Die vorbereiteten Demo-Einträge und lokalen Videos bleiben erhalten.</p>';
    document.querySelector('#dialog-actions').innerHTML = kind === 'consent'
      ? button('Ja, aktive Begleitung einschalten', 'confirm-consent', 'primary') + button('Nein, ausgeschaltet lassen', 'cancel-dialog')
      : kind === 'companion'
        ? button('Ausschalten', 'companion') + button('Zurück', 'cancel-dialog')
        : button('Ja, Demo zurücksetzen', 'confirm-reset', 'primary') + button('Abbrechen', 'cancel-dialog');
    if (kind === 'consent' || kind === 'companion') {
      document.querySelector('#dialog-body').insertAdjacentHTML('afterbegin', `<p><strong>Diese Einstellung gilt für ${profile().name} (${profile().role}).</strong></p>`);
    }
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
    const target = event.target.closest('[data-action]')
      || event.target.closest('.video-row')?.querySelector('button[data-action]');
    if (!target) return;
    const action = target.dataset.action;
    if (action === 'stop') return stop();
    if (action.startsWith('prompt-wav-choose-')) {
      const id = action.slice('prompt-wav-choose-'.length);
      if (id !== 'D5') document.querySelector(`#prompt-wav-${id}`)?.click();
      return;
    }
    if (action.startsWith('prompt-wav-preview-')) { await previewPromptAudio(action.slice('prompt-wav-preview-'.length)); return; }
    if (action.startsWith('prompt-wav-remove-')) { await removePromptAudio(action.slice('prompt-wav-remove-'.length)); return; }
    if (action.startsWith('dialogue-') && route === 'ask' && !isRelative()) {
      stopMedia();
      const conversation = currentDialogue();
      if (action.startsWith('dialogue-select-')) {
        const selected = content.dialogues.find(item => `dialogue-select-${item.id}` === action);
        if (selected) { dialogueId = selected.id; dialogueStep = 1; render('ask'); }
      } else if (action === 'dialogue-mode-text' || action === 'dialogue-mode-voice') {
        dialogueMode = action.endsWith('voice') ? 'voice' : 'text'; redrawDialogue(action);
      } else if (action === 'dialogue-topics') { dialogueId = null; render('ask'); }
      else if (action === 'dialogue-stop-voice') {
        document.querySelector('#dialogue-voice-status').textContent = 'Vorlesen gestoppt.';
      } else if (action === 'dialogue-read') readDialogue();
      else if (conversation) {
        if (action === 'dialogue-previous' || action === 'dialogue-next') {
          dialogueStep = Math.max(1, Math.min(conversation.steps.length, dialogueStep + (action.endsWith('next') ? 1 : -1)));
          redrawDialogue(action);
        } else if (action === 'dialogue-restart') { dialogueStep = 1; redrawDialogue(action); }
        else if (action === 'dialogue-media' && dialogueStep === conversation.steps.length) {
          dialogueVideoReturn = conversation.meta.Aktion.startsWith('video-');
          navigate(conversation.meta.Aktion);
        }
      }
      return;
    }
    if (action === 'remove-xray') { await updateXray(null); return; }
    if (action === 'reload-content') { await loadContent(); return; }
    if (action === 'play-video') {
      await playVideo(document.querySelector('#local-player'), true);
      return;
    }
    if (action.startsWith('remove-video-')) {
      if (videoBusy) return;
      try { await window.SMART_VIDEOS.remove(action.slice(13)); videoKeys.delete(action.slice(13)); videoMessage = 'Die ausgewählte lokale Kopie wurde entfernt. Die Originaldatei bleibt erhalten.'; }
      catch { videoMessage = 'Die lokale Kopie konnte nicht entfernt werden.'; }
      if (route === 'settings') render(route, false); return;
    }
    if (action === 'cancel-dialog') return closeDialog();
    if (action === 'confirm-consent') {
      preferences.activeByRole[preferences.role] = true;
      savePreferences(); closeDialog(false); redraw(route === 'home' ? 'companion-details' : 'companion'); return;
    }
    if (action === 'confirm-reset') {
      preferences = { ...freshPreferences(), textSize: preferences.textSize, idleMotion: preferences.idleMotion };
      level = 0; windowOffset = 0;
      dialogueMode = 'text';
      savePreferences(); closeDialog(false); navigate('home'); return;
    }
    if (action === 'companion-details') return openDialog(active() ? 'companion' : 'consent', target);
    if (action === 'companion') {
      if (!active()) return openDialog('consent', target);
      preferences.activeByRole[preferences.role] = false;
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
      level = 0; windowOffset = 0; detailOrigin = 'home';
      savePreferences();
      if (route === 'home' || route === 'settings' || route === 'journey') redraw(action);
      else navigate('home');
      return;
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
    if (event.target.matches('input[data-prompt-audio-id]')) { await choosePromptAudio(event.target.files[0], event.target.dataset.promptAudioId); return; }
    if (event.target.id === 'xray-image') { if (event.target.files[0]) await updateXray(event.target.files[0]); return; }
    if (event.target.matches('input[data-video-id]')) { await chooseSingleVideo(event.target.files[0], event.target.dataset.videoId); return; }
    if (event.target.id === 'local-videos') { await importVideos(event.target.files); return; }
    if (event.target.id === 'idle-photo') {
      const file = event.target.files[0];
      if (file) await updatePhoto(file);
      return;
    }
    if (event.target.id === 'idle-motion') {
      preferences.idleMotion = event.target.value === 'on';
      savePreferences(); return;
    }
    if (event.target.id === 'proactive-dialogue') {
      stopPromptAudioPreview();
      preferences.proactiveDialogue = event.target.value === 'none' || (content.promptDialogues || []).some(item => item.id === event.target.value) ? event.target.value : 'none';
      savePreferences();
      render('settings', false);
      return;
    }
    if (event.target.id === 'proactive-wait') {
      const value = Number(event.target.value);
      const status = document.querySelector('#proactive-wait-status');
      if (!Number.isInteger(value) || value < 5 || value > 3600) {
        if (status) status.textContent = 'Bitte eine ganze Zahl zwischen 5 und 3600 eingeben. Der gespeicherte Wert bleibt unverändert.';
        event.target.value = String(preferences.waitSeconds);
        return;
      }
      preferences.waitSeconds = value;
      savePreferences();
      if (status) status.textContent = 'Wartezeit gespeichert. Es wird noch kein Timer gestartet.';
      return;
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
  window.speechSynthesis?.addEventListener('voiceschanged', () => {
    const read = document.querySelector('[data-action="dialogue-read"]');
    const status = document.querySelector('#dialogue-voice-status');
    if (!read || !status) return;
    const voice = localVoice();
    read.disabled = !voice || !currentDialogue()?.steps[dialogueStep - 1];
    if (!window.speechSynthesis.speaking) status.textContent = voice ? 'Lokale deutsche Stimme verfügbar.' : 'Keine lokale deutsche Stimme verfügbar. Das Gespräch bleibt als Text vorführbar.';
  });
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
  loadContent();
})();
