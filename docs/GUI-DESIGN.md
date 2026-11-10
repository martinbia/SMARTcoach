# Umsetzung der freigegebenen GUI-Designs

Stand: 08.11.2026. Grundlage sind die beiden WebP-Dateien in `docs/design/` und der
ausdrücklich beauftragte Wechsel zu unterschiedlichen Personen-Dashboards.
Die älteren Konzeptdateien bleiben unverändert erhalten.

## GUI-Freeze ab 09.11.2026

Der aktuelle Willkommens-/Ruhebildschirm mit lokalem Luzern-Foto und bestehenden
Animationen sowie die Hauptmenüs von Ernst und Anna sind gestalterisch eingefroren.
Grundlage ist `main` bei `25a270f`. Laufende Animationen und Bedienung bleiben aktiv;
der Freeze betrifft künftige Designänderungen. Änderungen dieser Oberflächen
erfordern einen ausdrücklichen Auftrag für den betroffenen Bereich.
Die verbindlichen Arbeitsregeln stehen in [AGENTS.md](../AGENTS.md).

Die zusätzlich beauftragte Bedienung der Videozeile betrifft nur die vorhandene
Videoliste und deren Klickverarbeitung. Sie verändert die eingefrorenen Ansichten
nicht. Vergleichs-Screenshots werden dafür nicht als neue Designreferenz ersetzt.

| Referenzmerkmal | Umsetzung |
| --- | --- |
| Landschaft, türkiser Profilbereich, Porträt | Lokale SVG-Kopflandschaft und getrennte Profilillustrationen mit Namen und Rollenbezeichnung |
| Personenwechsel im oberen Bereich | Sichtbare Ernst-/Anna-Schaltflächen; jeweils nur eine Oberfläche, Auswahl lokal gespeichert |
| Ernst: sechs Monate | Acht anklickbare Übersichtsmarker; drei kompakte Spitalereignisse, danach Alltag, Termin und Ziele; sechs Monate sind Planungshorizont, kein Heilungsversprechen |
| Anna: Begleit-Woche | Alle sechs freigegebenen Themen als eigener verbundener Wochenweg; im Hochformat umgebrochen, nicht abgeschnitten |
| Detaillierter Weg | Ernst: vorhandene Gesamt-/Detailansicht und vollständige Liste J00–J13. Anna: Wochenstationen mit Erklärung, Aufgaben und gemeinsamer medizinischer Terminliste |
| Diese Woche / Nächste Termine | Zwei nebeneinanderliegende Bereiche mit rollenspezifischen Demo-Aufgaben und dem bestehenden Termin E07 |
| Vier farbige Funktionskarten | Unterschiedliche Beschriftungen für Ernst und Anna; echte Schaltflächen zu den bisherigen Vorschauansichten |
| Aktive Begleitung / Beenden unten | Sichtbarer EIN/AUS-Zustand, Einwilligung und sofortiges Ausschalten; Beenden stoppt Medien und öffnet den vorhandenen Ruhebildschirm |
| Android-Tablet | Keine gezeichneten Systemleisten und kein eingebetteter Tablet-Rahmen; nutzbare Fläche wird vom echten Viewport bestimmt |

Die Screenshots unter `docs/screenshots/` wurden nach dem Vergleich mit den
Referenzen verbessert: kompaktere Kopfhöhe, klarere Spitalbeschriftung, kleinere
Zwischenräume, passende Kartenhöhen und durchgehende Journey-Linien auch im
Hochformat. Beide Rollen passen bei 1280×800 ohne Seitenscrollen in den Viewport.

## Bewusste Unterschiede und Datengrenzen

- Referenzdaten im März/April, Woche 5–6, Uhrzeiten, Orthopädietermin, konkrete
  Trainingsmengen und medizinische Fortschrittsstufen sind keine Demo-Fakten.
  Verwendet werden weiterhin Sturz 26.10.2026, Operation 27.10., Austritt 02.11.,
  Demo-Heute 06.11. und Physiotherapie 10.11.2026 sowie die vorhandenen Ziele.
- Im Datensatz ist nur ein konkreter Physiotherapietermin hinterlegt. Weitere
  regelmässige Termine bleiben offen, statt neue Termine zu behaupten.
- „Meine Ziele“ am Ende ist ein offener Planungshorizont bis 26.04.2027, kein
  medizinisches Ereignis oder bestätigter Termin. Zeitabstände sind schematisch.
- Wochenaufgaben sind Gesprächsvorschläge. Es gibt keine vorgetäuschten Häkchen,
  automatische Bewertung oder neue Tagebuchspeicherung. Annas Woche ist ein
  wiederkehrender Themenrahmen, kein automatisch laufender Coachingdienst.
- Porträts und Landschaft sind eigens angelegte SVG-Illustrationen. Sie ersetzen
  die Bildsprache der Referenz, ohne die komplette Referenzoberfläche als Bild
  einzubetten oder echte Personenfotos zu behaupten. Ein Austausch durch weitere
  freigegebene Bildassets ist möglich.
- Die Original-WebP-Dateien bleiben nur Designreferenzen; der Pages-Workflow
  veröffentlicht sie nicht. Die private lokale Ruhebild-Auswahl bleibt separat.

## Einwilligung je Person

Der bestehende Speicherschlüssel `smartcoach.preferences.v1` enthält jetzt
`activeByRole.patient` und `activeByRole.relative`. Werte werden nur bei explizitem
Boolean `true` aktiviert. Beim Lesen alter Einstellungen gilt die bisherige
Zustimmung ausschliesslich für die zuletzt ausgewählte Person; es entsteht keine
zusätzliche Zustimmung für die andere Person. Dialoge benennen die betroffene
Person. Ein Ausschalten ändert nur deren Zustand. Der Interview-Reset setzt beide
Zustimmungen zurück und erhält Schriftgrösse, Animationseinstellung und Ruhebild.

Die Dialog-, Medien-, Installations- und Offline-Funktionen sind weiterhin Teil
derselben PWA. KI, EPIC, vollständige Tagebücher und echte Coaching-Impulse sind
weiterhin nicht implementiert.

## Fragen stellen · gemeinsames Zweispaltenlayout

Die Seite „Fragen stellen“ verwendet in allen Zuständen dieselbe äussere
Zweispaltenstruktur: links die lokale WebP-Gesundheitsfachkraft mit Wortmarke,
geschwungener Fläche und Untertitel, rechts Themenauswahl, manuelles Gespräch,
automatischer Dialog oder Annas Hinweis. Im Querformat beträgt die Aufteilung
ungefähr 38:62; im Hochformat erscheint die Figur kompakt über dem Gespräch.
Manuelle Gesprächszeilen und automatische Nachrichten teilen sich die
Sprechblasendarstellung. Im linken Bereich erscheinen Schallwellen nur während
der bestehenden Coach-WAV-Wiedergabe.

Die neue Illustration in `assets/coach-illustration.webp` wurde anhand der vom
Auftraggeber im Chat gezeigten Bildvorlage als vergleichbares lokales Asset
erzeugt; sie ist kein Ausschnitt der Originaldatei. Die Wortmarke und der
Untertitel bleiben als HTML-Text erhalten. Die Illustration wird in allen vier
Zuständen derselben „Fragen stellen“-Ansicht verwendet.

Die gemeinsame Struktur ändert weder Dialogablauf noch Auswahl, Timer,
WAV-Zuordnungen, Wiedergabe, Antworten, Voice-Demo oder Abbruch. D01–D03 bleiben
manuell und starten nicht beim Öffnen der Themenauswahl. Die eingefrorenen
Ansichten ausserhalb von „Fragen stellen“ bleiben unverändert.

Screenshots bei 1280×800: [Themenauswahl](screenshots/questions-topics-landscape.png),
[manuelles Gespräch](screenshots/questions-manual-landscape.png) und
[automatischer Dialog](screenshots/questions-automatic-landscape.png). Die
Dialoginhalte sind fiktive Testdaten.
