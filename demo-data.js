/* Redaktionelle Demo-Daten. IDs entsprechen der Patientenjourney v0.2.
   Keine echten Gesundheitsdaten, keine Therapieanweisungen. */
window.SMART_DEMO = Object.freeze({
  today: '2026-11-06',
  events: [
    { id: 'J00', date: '2026-10-20', label: 'Alltag davor', dateLabel: 'Vor dem Sturz', category: 'Erinnerung', symbol: '⌂', overview: true, text: 'Ernst ging gern an der Reuss spazieren, spielte Jass und bereitete sein Frühstück selbst zu.', source: 'Fiktive Biografie von Ernst' },
    { id: 'J01', date: '2026-10-26', label: 'Sturz', category: 'Spital', symbol: '+', overview: true, text: 'Ernst ist zu Hause gestürzt. Im Spital wurde ein hüftnaher Bruch rechts festgestellt.', source: 'E01 · Aufnahmebericht · 26.10.2026 (Demo)' },
    { id: 'J02', date: '2026-10-27', label: 'Operation', category: 'Behandlung', symbol: '+', overview: true, text: 'Der Bruch wurde mit einem Nagel im Knochen und Schrauben stabilisiert. Daraus folgt keine automatische Belastungsfreigabe.', source: 'E02 · Operationsbericht · 27.10.2026 (Demo)' },
    { id: 'J03', date: '2026-10-28', label: 'Erstes Aufstehen', category: 'Therapie', symbol: '↗', text: 'Ernst hat unter fachlicher Anleitung das erste Aufstehen geübt.', source: 'E04 · Physiotherapiebericht · 30.10.2026 (Demo)' },
    { id: 'J04', date: '2026-10-30', label: 'Im Spital üben', category: 'Therapie', symbol: '↗', text: 'Gehen und Wechsel zwischen Bett und Stuhl wurden mit einem Hilfsmittel unter Anleitung geübt.', source: 'E04 · Physiotherapiebericht · 30.10.2026 (Demo)' },
    { id: 'J05', date: '2026-11-02', label: 'Austritt', category: 'Zu Hause', symbol: '⌂', overview: true, text: 'Ernst ist wieder zu Hause. Er hat Unterlagen und einen Termin für die weitere Physiotherapie erhalten.', source: 'E06 · Entlassbrief · 02.11.2026 (Demo)' },
    { id: 'J06', date: '2026-11-03', label: 'Zu Hause gehen', category: 'Selbst berichtet', symbol: '✓', text: 'Im fiktiven Beispiellogbuch steht: Ernst ist in der Wohnung mit dem Rollator gegangen.', source: 'L01 · Selbstbericht · 03.11.2026 (Demo)' },
    { id: 'J07', date: '2026-11-04', label: 'Eine offene Frage', category: 'Frage', symbol: '?', text: 'Wie kann Anna Ernst bei den Eingangsstufen unterstützen? Diese Frage ist noch offen.', source: 'Q01 · Frage von Anna · 04.11.2026 (Demo)' },
    { id: 'J08', date: '2026-11-05', label: 'Übung ausprobiert', category: 'Selbst berichtet', symbol: '✓', text: 'Ernst hat eine vorgesehene Übung ausprobiert und fühlt sich dabei noch unsicher.', source: 'L02 · Selbstbericht · 05.11.2026 (Demo)' },
    { id: 'J09', date: '2026-11-06', label: 'Heute', category: 'Demo-Heute', symbol: '●', overview: true, text: 'In dieser Demo ist der 6. November 2026. Ernst ist seit vier Tagen zu Hause. Fragen zu Übungen und Unterstützung können beim nächsten Termin besprochen werden.', source: 'E06 / E07 · Entlassbrief und Terminplan (Demo)' },
    { id: 'J10', date: '2026-11-10', label: 'Physiotherapie', category: 'Geplanter Termin', symbol: '▦', overview: true, text: 'Der nächste fiktive Physiotherapietermin ist am 10. November. Eine Fragenliste wird in einer späteren Version ergänzt.', source: 'E07 · Terminplan · Stand 02.11.2026 (Demo)' },
    { id: 'J11', date: '2026-11-24', label: 'Verlauf besprechen', category: 'Geplant', symbol: '▦', text: 'Ein weiteres Gespräch über Verlauf und Alltag ist als fiktives Beispiel vorgesehen.', source: 'Fiktive Planung · kein bestätigter Behandlungstermin' },
    { id: 'J12', date: '2026-12-08', label: 'Frühstück machen', category: 'Persönliches Ziel', symbol: '☆', overview: true, text: 'Ernst möchte sein Frühstück wieder selbst organisieren. Das Datum ist ein Wunsch und kein Heilungsversprechen.', source: 'Persönlicher Wunsch von Ernst (Demo)' },
    { id: 'J13', date: '2027-01-19', label: 'Zusammen hinaus', category: 'Persönliches Ziel', symbol: '☆', overview: true, text: 'Ernst und Anna möchten wieder einen kleinen Ausflug machen. Der Zeitpunkt bleibt offen.', source: 'Persönliches Ziel von Ernst und Anna (Demo)' }
  ]
});
