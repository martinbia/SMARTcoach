/* Editorial UI content. Clinical dates and facts remain in demo-data.js.
   Tasks are suggestions for the fictional interview, never prescriptions. */
window.SMART_DASHBOARDS = {
  patient: {
    name: 'Ernst', role: 'Patient', subtitle: 'Meine Rehabilitation zu Hause',
    journeyTitle: 'Mein Weg der Genesung – 6 Monate',
    actions: [
      ['ask', 'Fragen stellen', 'Fragen zu meinem Alltag besprechen.'],
      ['exercises', 'Übungen', 'Lokale Videos zur Orientierung.'],
      ['reports', 'Berichte & Erklärungen', 'Unterlagen verständlich erklärt.'],
      ['diary', 'Mein Eintrag zum Genesungsweg', 'Beispiel-Einträge ansehen.']
    ],
    tasks: ['Fragen zu Übungen klären', 'Persönlichen Plan besprechen', 'Eigene Ziele im Blick behalten']
  },
  relative: {
    name: 'Anna', role: 'Angehörige', subtitle: 'Begleitet Ernst zu Hause',
    journeyTitle: 'Meine Begleit-Woche',
    actions: [
      ['ask', 'Fragen stellen', 'Fragen zur Unterstützung im Alltag.'],
      ['exercises', 'Anleitungen', 'Mobilitätsabläufe verstehen.'],
      ['reports', 'Berichte & Erklärungen', 'Gemeinsame Unterlagen verstehen.'],
      ['diary', 'Mein Eintrag zum Begleitweg', 'Eigene Beispiel-Einträge ansehen.']
    ],
    tasks: ['Die Woche gemeinsam planen', 'Eigene Belastung wahrnehmen', 'Zeit für mich einplanen']
  },
  week: [
    { id: 'A01', label: 'Wochenüberblick', caption: 'Planen und Schwerpunkte setzen', icon: 'calendar', text: 'Welche Unterstützung ist diese Woche sinnvoll? Welche eigenen Vorhaben möchten Sie berücksichtigen? Diese Demo sammelt noch keine Antworten.' },
    { id: 'A02', label: 'Sicher helfen', caption: 'Im Alltag unterstützen', icon: 'exercises', text: 'Wie viel Unterstützung ist hilfreich? Individuelle Bewegungsanweisungen müssen mit einer Fachperson geklärt werden. Die lokalen Mobilitätsvideos dienen der Orientierung im gemeinsamen Gespräch.' },
    { id: 'A03', label: 'Fragen sammeln', caption: 'Offene Fragen im Blick', icon: 'ask', text: 'Was möchten Sie beim gemeinsamen Termin besprechen? Eine gespeicherte Fragenliste ist noch nicht implementiert.' },
    { id: 'A04', label: 'Belastung prüfen', caption: 'Wie geht es mir selbst?', icon: 'heart', text: 'Wie erleben Sie Ihre Begleitrolle? Eigene Sorgen und Grenzen haben hier Platz. Diese Vorschau erfasst noch keine persönlichen Angaben.' },
    { id: 'A05', label: 'Zeit für mich', caption: 'Erholung einplanen', icon: 'cup', text: 'Welche Zeit möchten Sie für sich reservieren? Die Begleit-Woche erinnert als Gestaltungsidee an eigene Bedürfnisse, ohne einen Hintergrunddienst zu starten.' },
    { id: 'A06', label: 'Gute Balance diese Woche', caption: 'Rückblick und Ausblick', icon: 'flag', text: 'Was war hilfreich und was möchten Sie nächste Woche anders gestalten? Die sechs Themen bilden einen wiederkehrenden Wochenrahmen, keinen bewerteten Fortschritt.' }
  ]
};
