/* Small, deliberately limited Markdown content format; no HTML evaluation. */
(() => {
  const escape = text => String(text).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
  const date = value => new Intl.DateTimeFormat('de-CH', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T12:00:00Z`));
  function parse(text) {
    const records = [];
    let record, section;
    for (const line of text.replace(/\r/g, '').split('\n')) {
      const heading = line.match(/^## ([A-Z]\d{2}) \| (.+)$/);
      if (heading) {
        record = { id: heading[1], title: heading[2].trim(), meta: {}, sections: {} };
        if (records.some(item => item.id === record.id)) throw new Error(`Doppelte ID ${record.id}.`);
        records.push(record); section = null; continue;
      }
      if (!record) continue;
      const subheading = line.match(/^### (.+)$/);
      if (subheading) {
        section = subheading[1].trim();
        if (section in record.sections) throw new Error(`Doppelter Abschnitt in ${record.id}.`);
        record.sections[section] = ''; continue;
      }
      if (section) record.sections[section] += `${line}\n`;
      else if (line.trim()) {
        const field = line.match(/^([^:]+):\s*(.*)$/);
        if (!field || field[1] in record.meta) throw new Error(`Ungültige Metadaten in ${record.id}.`);
        record.meta[field[1]] = field[2].trim();
      }
    }
    records.forEach(record => Object.keys(record.sections).forEach(key => record.sections[key] = record.sections[key].trim()));
    return records;
  }
  function required(value, context) {
    if (!value) throw new Error(`Angabe fehlt: ${context}.`);
    return value;
  }
  function validDate(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '') || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0, 10) !== value) throw new Error('Ungültiges Inhaltsdatum.');
    return value;
  }
  function markdown(text) {
    // Paragraphs, bullet lists and bold only. HTML, images and links stay text.
    return text.split(/\n\s*\n/).filter(Boolean).map(block => {
      const inline = line => escape(line).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      if (block.split('\n').every(line => line.startsWith('- '))) return `<ul>${block.split('\n').map(line => `<li>${inline(line.slice(2))}</li>`).join('')}</ul>`;
      return `<p>${inline(block.replace(/\n/g, ' '))}</p>`;
    }).join('');
  }
  const content = { loaded: false, reports: [], entries: [], videos: [], escape, markdown, parse };
  content.load = async () => {
    const texts = await Promise.all(['genesungsweg', 'berichte', 'videos'].map(async name => {
      const response = await fetch(`./content/${name}.md`, { cache: 'no-cache' });
      if (!response.ok) throw new Error(`Inhaltsdatei ${name}.md ist nicht verfügbar.`);
      const text = await response.text();
      if (text.length > 1024 * 1024) throw new Error('Inhaltsdatei ist zu gross.');
      return text;
    }));
    const journeyRecords = parse(texts[0]);
    const reports = parse(texts[1]);
    const videos = parse(texts[2]);
    const eventRecords = journeyRecords.filter(record => record.id.startsWith('J'));
    for (let index = 0; index < 14; index++) required(eventRecords.find(record => record.id === `J${String(index).padStart(2, '0')}`), 'Journey-ID');
    const events = eventRecords.map(record => {
      if (!['ja', 'nein'].includes(record.meta['Übersicht'])) throw new Error(`Übersicht muss ja oder nein sein: ${record.id}.`);
      return {
        id: record.id, date: validDate(record.meta.Datum), label: escape(record.title),
        category: escape(required(record.meta.Kategorie, record.id)), symbol: escape(record.meta.Symbol || '●'),
        source: escape(required(record.meta.Quelle, record.id)), overview: record.meta['Übersicht'] === 'ja',
        dateLabel: record.meta.Datumsanzeige ? escape(record.meta.Datumsanzeige) : undefined,
        text: escape(required(record.sections.Beschreibung, record.id)),
        reports: (record.meta.Berichte || '').split(',').filter(Boolean).map(id => id.trim())
      };
    });
    const referenceDate = id => validDate(required(events.find(event => event.id === id), id).date);
    events.forEach((event, index) => {
      if (index && events[index - 1].date > event.date) throw new Error(`Die Ereignisse müssen zeitlich geordnet bleiben: ${event.id}.`);
    });
    const interpolate = text => text.replace(/\{\{(J\d{2})\.Datum\}\}/g, (_, id) => date(referenceDate(id)));
    for (const event of events) { event.text = interpolate(event.text); event.source = interpolate(event.source); }
    const entries = journeyRecords.filter(record => !record.id.startsWith('J')).map(record => {
      if (!/^[LQ]\d{2}$/.test(record.id) || !['Ernst', 'Anna'].includes(record.meta.Person) || !['ja', 'nein'].includes(record.meta.Privat)) throw new Error(`Ungültiger Eintrag ${record.id}.`);
      required(record.sections.Eintrag, record.id);
      required(record.meta.Typ, record.id);
      for (const key of Object.keys(record.sections)) record.sections[key] = interpolate(record.sections[key]);
      return { ...record, date: referenceDate(record.meta.Journey), role: record.meta.Person === 'Anna' ? 'relative' : 'patient' };
    });
    for (const report of reports) {
      if (!/^E\d{2}$/.test(report.id)) throw new Error('Ungültige Berichts-ID.');
      const anchorDate = referenceDate(report.meta.Journey);
      report.date = report.meta.Datum ? validDate(report.meta.Datum) : anchorDate;
      for (const section of ['Im Dokument steht', 'Einfach erklärt', 'Für Ernst', 'Für Anna', 'Frage für den Termin']) required(report.sections[section], `${report.id}: ${section}`);
      for (const key of Object.keys(report.sections)) report.sections[key] = interpolate(report.sections[key]);
    }
    events.forEach(event => event.reports.forEach(id => required(reports.find(report => report.id === id), id)));
    for (const video of videos) {
      if (!/^V\d{2}$/.test(video.id) || !/^[^/\\]+\.mp4$/i.test(video.meta.Datei || '')) throw new Error('Ungültige Video-Zuordnung.');
      video.roles = required(video.meta.Personen, video.id).split(',').map(name => {
        if (!['Ernst', 'Anna'].includes(name.trim())) throw new Error('Ungültige Video-Person.');
        return name.trim() === 'Anna' ? 'relative' : 'patient';
      });
      required(video.sections.Hinweis, video.id);
      required(video.meta.Kategorie, video.id);
    }
    if (!reports.length || !videos.length) throw new Error('Inhaltskatalog ist leer.');
    // Commit the coherent dataset only after all files and references validate.
    window.SMART_DEMO.events.splice(0, window.SMART_DEMO.events.length, ...events);
    window.SMART_DEMO.today = referenceDate('J09');
    Object.assign(content, { reports, entries, videos, loaded: true });
  };
  window.SMART_CONTENT = content;
})();
