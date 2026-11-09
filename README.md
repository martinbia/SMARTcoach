# SMARTcoach · Vorführbare Gespräche und lokale Medien 0.5.0

Klickbares PWA-Mock-up für Android-Tablets, umgesetzt mit HTML, CSS und Vanilla
JavaScript. **Phase A**: Orientierung, Navigation und gestalterische Prüfung mit
fiktiven Daten. Keine medizinische Beratung, keine echte Patientenakte.

## Bereits bedienbar

- Ruhebildschirm: eine Berührung öffnet das Dashboard.
- Ernst: kompakte Genesungsübersicht mit sechs Monaten als offenem Planungshorizont.
  Alle 14 vorhandenen Ereignisse sind über den detaillierten Weg erreichbar.
- Anna: eigener Begleit-Wochenweg mit sechs Themen und gemeinsamen medizinischen Terminen.
- Gesamter Weg, zwei Detailstufen, Demo-Heute ±14 Tage und Navigation zu
  früheren/späteren Zeitfenstern. Die Abstände sind schematisch, kein Heilungsgrad.
- Personenwechsel mit eigener Journey, Profilillustration, Aufgaben und Funktionen.
- Aktive Begleitung: standardmässig AUS, verständlicher Einwilligungsdialog,
  bestätigtes Einschalten und sofortiges Ausschalten, **getrennt je Person**.
  **Keine automatischen Impulse.**
- Globales „Beenden“, auch innerhalb der Bestätigungsdialoge: stoppt Medien und
  kehrt in den Ruhemodus zurück. Die Zustimmung bleibt beim Beenden erhalten.
- Lokal gespeicherte Perspektive, Schriftgrösse und Einwilligung; Demo-Reset
  erhält die Schriftgrösse. Jeder App-Start öffnet den Ruhebildschirm.
- Manifest, PNG-Icons, Service Worker und Offline-App-Shell ohne externe Ressourcen.

## Freigegebene Dashboard-Designs

**GUI-Freeze:** Die Willkommens-/Ruhebildschirme mit Luzern-Foto und Animationen
sowie die Hauptmenüs von Ernst und Anna sind gestalterisch eingefroren.
Animationen und Bedienung bleiben aktiv. Regeln für weitere Änderungen:
[AGENTS.md](AGENTS.md) und [GUI-Dokumentation](docs/GUI-DESIGN.md).

Die Oberflächen folgen den Referenzen in `docs/design/`: Profilbereich mit
Personenwechsel, eigener Journey, „Diese Woche“, „Nächste Termine“, vier farbigen
Hauptfunktionen und unterer Leiste für Aktive Begleitung und Beenden. Es werden
keine Android-Systemleisten oder Tablet-Rahmen nachgebildet. Die Darstellung
besteht aus echten HTML-Schaltflächen und lokalen SVG-Illustrationen.

Ernsts Spitalphase nimmt nur einen kleinen Teil der Übersicht ein; der Hauptteil
zeigt den Alltag zu Hause und persönliche Ziele. Annas „Meine Begleit-Woche“ ist
keine zweite Heilungsverlaufskurve, sondern ein wiederkehrender Wochenrahmen.
„Zum detaillierten Weg“ öffnet die Ereignisliste bzw. Annas Wochenaufgaben mit den
gemeinsamen Terminen. Der bekannte Physiotherapietermin bleibt **10.11.2026**.
Weitere Termine werden nicht in die Journey übernommen. Der Januartermin im
gesonderten Interview-Gespräch ist ausdrücklich ein erfundenes Kalenderbeispiel.

Bei 1280×800 sind die wesentlichen Bereiche beider Dashboards vollständig sichtbar.
Hochformat, kleine Bildschirme und sehr grosse Schrift dürfen zugunsten der
Lesbarkeit vertikal scrollen. Lokale Porträts und Landschaft sind austauschbare
Illustrationen, keine echten Personenfotos. Details zum Referenzvergleich:
[GUI-Umsetzung](docs/GUI-DESIGN.md).

Aktive Begleitung bleibt standardmässig AUS. Bei einem Upgrade wird die frühere
Einwilligung nur für die zuletzt ausgewählte Person übernommen. Die andere Person
beginnt mit AUS. Der Interview-Reset setzt beide Zustimmungen zurück; lokale
Fotos, Schriftgrösse und Animationseinstellung bleiben erhalten.

## Lokale Videos und redaktionelle Inhalte

Unter **Übungen** (Ernst) stehen sieben Video-Themen bereit. **Anleitungen** (Anna)
zeigt die drei Mobilitätsfilme zu Gehen und Treppen. Eine kompakte Tabelle zeigt
nur Titel und **Video ansehen**. Bei 1280×800 und 800×1280 sind alle sieben
Einträge für Ernst gleichzeitig sichtbar. Hinweise zum jeweiligen Film stehen
auf der Videoseite unter dem Player; die Dateiverwaltung bleibt in den Einstellungen.
Bei kleinen Bildschirmen und sehr grosser Schrift darf die Liste vertikal scrollen.
Die Zuordnung erfolgt anhand
der genannten Dateinamen, nicht anhand einer fachlichen Prüfung des Filminhalts.
Sie ist keine individuelle Übungsfreigabe. Konkrete Belastung und Übungsdosierung
bleiben an den persönlichen Plan gebunden.

Unter **Einstellungen → Lokale Übungsvideos → Lokale MP4-Filme auswählen**
die MP4-Dateien auf dem Tablet markieren, zum
Beispiel im selben Ordner wie das Luzern-Bild. Die PWA darf den Ordner nicht ohne
Auswahl durchsuchen. Die Dateien werden vollständig eingelesen und als unabhängige
Kopien in IndexedDB auf diesem Gerät gespeichert; sie werden nicht hochgeladen.
Mehrfachauswahl und Zuordnung tolerieren Unterschiede in Leerzeichen,
Unterstrichen, Gross-/Kleinschreibung sowie Download-Zusätze wie `(1)`.
Auch ein vom Android-Dateidialog gelieferter generischer Dateityp wird akzeptiert.
Eine lokale Kopie benötigt freien Website-Speicher; pro Datei gilt ein Limit von
512 MB. Falls Speichern scheitert, bleibt die eingelesene Datei für die laufende
Sitzung abspielbar; die Oberfläche kennzeichnet dies ausdrücklich.

In den Einstellungen lassen sich unter **Einzelne Filme zuordnen oder ersetzen**
auch MP4-Dateien mit abweichendem Namen zuordnen und lokale Kopien entfernen.
Übungen und Anleitungen enthalten keine Dateiauswahl mehr.

Ein Tipp auf die **gesamte Videozeile** oder **Video ansehen** öffnet den Film und
startet die Wiedergabe direkt. Der Button bleibt per Tastatur bedienbar. Das Video
füllt die Fläche unter der Kopfzeile, ohne Beschnitt oder Verzerrung. Oben bleiben
SMARTcoach, **Zurück zur Übersicht**, Personenwechsel und **Beenden** erreichbar.
Titel, **Video erneut starten**, **Dateiname und Zuordnung** und **Alle Videos
anzeigen** stehen unter dem Video. Falls der Browser den Start blockiert, kann
die Wiedergabetaste im Video oder der Startbutton darunter verwendet werden.
Ein während des Imports geöffneter Player wird nach Abschluss automatisch
bereitgestellt. Unlesbare alte Kopien können in den Einstellungen ersetzt werden,
ohne die übrigen Website-Daten zu löschen.
Die Originaldateien bleiben erhalten. Nicht unterstützte Formate werden mit Text
erklärt. Das Einlesen konvertiert keine Codecs; falls erforderlich, eine MP4-Version
mit H.264-Video und AAC-Ton verwenden. Ein Video startet beim bewussten Öffnen;
beim Verlassen oder Beenden wird es gestoppt.

Die tatsächlich angezeigten Texte liegen in diesen direkt geladenen Dateien:

- [Berichte und Erklärungen](content/berichte.md): E01–E08 mit Quelltext,
  einfacher Erklärung, Rollenbezug und Frage für den Termin.
- [Genesungsweg und Beispiel-Einträge](content/genesungsweg.md): J00–J13 als
  gemeinsame Datenquelle für den Pfad sowie L01–Q02 als fiktive Selbstauskünfte.
- [Videokatalog](content/videos.md): Titel, Dateinamen, Sichtbarkeit und Hinweise.
- [Vorführbare Gespräche](content/dialoge.md): drei Gesprächsabläufe für Ernst,
  Sprechertexte, Reihenfolge und Medienziele.
- [Vorbereitete Ansprache-Dialoge](content/ansprache-dialoge.md): editierbare
  Dialoge A–D mit stabilen Zeilen-IDs. Die WAV-Zuordnung erfolgt separat lokal
  auf dem Tablet.

**Kein Kompilieren erforderlich.** Nach einer Änderung im Repository veröffentlicht
GitHub Pages die statischen Dateien neu. Jede Veröffentlichung erhält eine eigene
Service-Worker-Version, die App-Shell und zugehörige Markdown-Dateien gemeinsam
cached. In der PWA unter **Einstellungen → Inhalte neu laden** nach einer
veröffentlichten Aktualisierung suchen. Offline bleiben App und zuletzt
veröffentlichte Inhalte verfügbar. Die PWA übernimmt verfügbare Updates und lädt
die neue Version neu; eine Neuinstallation ist nicht nötig.

Format, Datenbezüge und Bewertung von Markdown gegenüber JSON/YAML:
[Inhalte bearbeiten](docs/INHALTE.md).

## Weiterhin bewusst offen

Freie Fragen und Spracherkennung sind noch nicht implementiert; „Fragen stellen“
zeigt die unten beschriebenen vorbereiteten Gespräche. Die Eintragsansichten
zeigen vorbereitete fiktive Beispiele, keine vollständige Tagebuch-Eingabe oder
Speicherung persönlicher Angaben. Keine EPIC-Verbindung, kein Quiz und keine
automatischen Coaching-Impulse. Medikamente, Belastungsfreigaben und Übungsdosen
werden nicht erfunden. Vorproduzierte MP3-Dateien sind weiterhin nicht eingebunden.

## Fragen stellen: Chat und Voice-Demo

Ernsts bestehender Menüpunkt **Fragen stellen** öffnet drei Interview-Gespräche:

- **Physiotermin und Geburtstag:** Im separaten Beispielkalender steht der
  26.01.2027 um 10 Uhr, der Geburtstag des Enkelkindes am 25.01.2027. Keine
  Buchung oder Änderung der vorhandenen Journey-Termine.
- **Meine aktuelle Übung:** Zeigt das Thema Wadenheben mit Festhalten. Nach den
  Gesprächsschritten startet **Wadenheben-Video abspielen** den lokal zugeordneten
  Film V07. Nach dessen Ende kehrt die Demo ins Hauptmenü zurück. Die normale
  Videobibliothek behält ihr bisheriges Verhalten.
- **Mein Röntgenbild:** Führt eine ausdrücklich simulierte EPIC-Suche vor und
  öffnet das lokale Demo-Bild. Es gibt keine Bildauswertung oder Befundung.

Die Gesprächsbuttons schalten genau einen Beitrag weiter oder zurück.
**Gespräch neu starten** und **Andere Gespräche** unterstützen die Vorführung.
Es gibt keine freie Texteingabe, Mikrofonaufnahme, KI oder echten Kalenderzugriff.
Für Anna sind noch keine eigenen Gesprächsszenarien angelegt. Hauptmenüs und
Willkommensbildschirme bleiben im GUI-Freeze.

**Voice-Demo / Vorlesen:** Die aktuell sichtbaren Beiträge von Ernst und dem
Coach können auf Knopfdruck direkt aus dem Markdown-Text gesprochen werden.
Die Web Speech API verwendet ausschliesslich eine vom Browser als lokal gemeldete
deutsche Stimme (`localService`). Es wird kein TTS-Dienst angesprochen und keine
MP3 erzeugt. Die Verfügbarkeit hängt von Android, TTS-Engine und Chrome ab.
Gegebenenfalls in den Android-Einstellungen für Text-in-Sprache eine deutsche
Offline-Stimme installieren. Meldet Chrome keine geeignete lokale Stimme,
bleibt der Vorlesebutton deaktiviert und der Text nutzbar. „Beenden“, Navigation,
Schrittwechsel und „Vorlesen stoppen“ brechen die Sprachausgabe ab.

**Demo-Röntgenbild:** Unter **Einstellungen → Röntgenbild für das Demo-Gespräch**
einmalig eine JPG-, PNG- oder WebP-Datei bis 12 MB auswählen. Das Bild wird in
einem eigenen IndexedDB-Speicher auf dem Tablet gehalten, nicht hochgeladen.
Neustart, Offlinebetrieb und Interview-Reset behalten die Auswahl. Ein Entfernen
löscht nur die Browserkopie. DICOM-Dateien werden nicht unterstützt. Solange kein
Bild vorliegt, zeigt der Gesprächszweig einen Hinweis zur lokalen Auswahl.

## Vorbereitete Dialoge und lokale WAV-Dateien

Unter **Einstellungen → Automatische Ansprache – vorbereitete Dialoge** wählt
die Interviewleitung einen Dialog A–D, ordnet WAV-Dateien anhand stabiler
Zeilen-IDs einzeln zu und kann jede Zuordnung dort bewusst probehören. WAV-Dateien
werden über den Android-Dateidialog ausgewählt, als unabhängige Kopien in einer
eigenen IndexedDB gespeichert und nie hochgeladen. Bei blockierter oder
fehlgeschlagener Speicherung kennzeichnet die Oberfläche eine Datei ausdrücklich
als **Nur für diese Sitzung**. WAV-Dateien dürfen höchstens 64 MB gross sein und
werden anhand ihrer Dateiendung sowie ihres RIFF/WAVE-Headers geprüft.

Dialogauswahl und Wartezeit (5–3600 Sekunden, Standard 60) liegen im lokalen
Einstellungsobjekt. Die WAV-Bytes und Dateinamen bleiben getrennt davon in der
IndexedDB, mit A1, B1 usw. als Schlüssel. Alle 13 Zeilen A1–D5 sind aktuell
freigegeben und lokal konfigurierbar. Gesperrte Katalogzeilen bleiben allgemein
ohne WAV-Steuerungen.
Der separate Markdown-Katalog lässt sich um fortlaufende Zeilen oder weitere
Dialoge erweitern, ohne die Anzeige- und Zuordnungslogik anzupassen.

Diese Einstellungen starten **keinen** Timer oder Dialog. Aktive Begleitung,
Ruhebildschirm und bisherige Gesprächs-Demos lösen keine automatische Ansprache
aus. Die ausgewählte Wartezeit wird nur gespeichert. Eine spätere automatische
Dialogsteuerung benötigt einen eigenen Entwicklungsauftrag.

Probehören benötigt einen bewussten Tastendruck. Chrome/Android kann die
Wiedergabe je nach Dateiformat, Audioausgabe und Systemrichtlinie ablehnen;
mehrere parallele Audios werden von der App unterbunden. Automatischer
Hintergrundstart und verlässliche Wiedergabe bei gesperrtem Bildschirm sind
nicht zugesichert. Lokale Website-Daten können vom Betriebssystem entfernt werden.

## Luzern-Bild und ruhiger Bildwechsel

Unter **Einstellungen → Luzern-Bild im Ruhemodus** ein eigenes Stadtfoto auswählen
(JPG, PNG oder WebP, bis 12 MB), zum Beispiel aus `Documents/SMART`. Das Foto wird
in der IndexedDB des Browsers auf dem Tablet gespeichert, nicht hochgeladen. Es
steht nach Neustart und offline bereit. Über „Foto entfernen“ lässt es sich löschen;
ein Demo-Reset behält das Bild bei. Löschen der Website-Daten entfernt auch das Foto.

Beim Start und nach „Beenden“ erscheint dieselbe Ansicht. Die bisherigen Texte
bleiben erhalten: Über 32 Sekunden wechseln lesbare Schrift auf stark aufgehelltem
Bild und eine klare Bildansicht ohne Text sanft ab. Das Foto bewegt sich dabei über
64 Sekunden langsam hin und her. Ein Antippen öffnet jederzeit das Dashboard.
„Animation anhalten“ oder die entsprechende Einstellung zeigt eine ruhige Ansicht
mit lesbarem Text. Auch die Geräteeinstellung „Bewegung reduzieren“ deaktiviert
Bewegung und Textwechsel. Ohne ausgewähltes Foto wird kein Text ausgeblendet.

## Lokal starten

Keine Installation und kein Build für die Anwendung nötig. Aus dem Checkout:

```sh
python3 -m http.server 8000 --directory ..
```

Die Anwendung über den Repository-Pfad `/SMARTcoach/` auf diesem lokalen Server
öffnen. Ein HTTP-Server ist erforderlich; `file://` unterstützt keinen Service Worker.
Für Service Worker und Installation ist auf einem entfernten Gerät HTTPS nötig.

## GitHub Pages und Android-Installation

Nach Review und Merge des Pull Requests:

1. Im Repository unter **Settings → Pages → Build and deployment → Source**
   **GitHub Actions** auswählen.
2. Der Workflow `Deploy PWA to GitHub Pages` veröffentlicht bei App-Änderungen
   auf `main`; alternativ unter **Actions** manuell starten. Er lädt ausschliesslich
   die App-Dateien und Icons hoch, keine Tests oder Konzeptdokumente.
3. Die von GitHub Pages angezeigte HTTPS-Adresse in Chrome auf Android öffnen.
   Alle Asset-, Manifest- und Service-Worker-Pfade sind relativ und funktionieren
   auch unter `/SMARTcoach/`.
4. Einmal online laden und auf „Offline bereit“ warten. Im Chrome-Menü
   **Zum Startbildschirm hinzufügen → Installieren** wählen, sofern angeboten.
   Eine zusätzliche Installationsschaltfläche erscheint bei verfügbarem Browserprompt
   in den App-Einstellungen. Danach vom Startbildschirm im Standalone-Modus öffnen.

Der Workflow wird nicht auf Feature-Branches oder bei einem Pull Request deployt.
Eine GitHub-Pages-Veröffentlichung oder Android-Geräteinstallation ist durch die
lokalen Tests allein noch nicht nachgewiesen.

## Tests

Python 3.12 oder neuer und Playwright mit Chromium:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r tests/requirements.txt
python -m playwright install --with-deps chromium
python -m unittest discover -s tests -v
```

Ein vorhandenes System-Chromium wird automatisch verwendet. `CHROMIUM_PATH`
kann den Pfad explizit festlegen. Ohne System-Chromium wird Playwrights Browser
verwendet. Die Tests starten ihren HTTP-Server selbst. Die CI führt dieselbe Suite
für Pushes und Pull Requests aus.

Ergebnisse, Grenzen und Tablet-Abnahme: [Testbericht](docs/TESTBERICHT.md).
Ansichten: [Ernst quer](docs/screenshots/ernst-dashboard-landscape.png),
[Ernst hoch](docs/screenshots/ernst-dashboard-portrait.png),
[Anna quer](docs/screenshots/anna-dashboard-landscape.png),
[Anna hoch](docs/screenshots/anna-dashboard-portrait.png),
[Ruhebildschirm](docs/screenshots/idle.png).

## Weiterentwicklung

- `demo-data.js`: initialer Demo-Kontext; Ereignisse werden aus Markdown geladen.
- `content.js`: kleiner Markdown-Lader, Validierung und sichere Textdarstellung.
- `local-videos.js`: lokaler MP4-Speicher und Dateinamen-Zuordnung.
- `local-prompt-audio.js`: lokale WAV-Kopien, getrennt nach stabiler Dialogzeilen-ID.
- `xray-media.js`: lokale Bildprüfung und getrennte Speicherung der Demo-Abbildung.
- `content/*.md`: redaktionelle Datenquelle ohne Build-Schritt.
- `dashboard-data.js`: Rollentexte, Wochenaufgaben und Annas sechs Begleitstationen.
- `app.js`: Navigation, Rollen, getrennte Einwilligungen und lokale Einstellungen.
- `idle-image.js`: lokale Foto-Prüfung und IndexedDB-Speicher für das Ruhebild.
- `styles.css`: responsive Ansichten, grosse Touch-Ziele und Fokusdarstellung.
- `sw.js`: App-Shell und Markdown pro Pages-Deployment gemeinsam cachen; der
  Pages-Workflow versieht den Cache mit der Commit-ID. Ein neues Deployment wird
  nach erfolgreichem Vorladen aktiviert und die PWA lädt die neue Version.
- `manifest.webmanifest`: Installation und Start im Standalone-Modus.

Einstellungen liegen unter `smartcoach.preferences.v1` im `localStorage` des
Browsers. Löschen der Browser-/Website-Daten entfernt sie. Bei gesperrtem Speicher
bleibt die App in der Sitzung benutzbar und zeigt einen Hinweis. Demo-Datum und
Beispielpersonen sind in Phase A bewusst fest hinterlegt. Es werden keine echten
Gesundheitsdaten erhoben und keine Daten an Dienste gesendet.

Die drei ursprünglichen Konzeptdateien bleiben unverändert die Grundlage für
spätere Phasen. Der ursprüngliche Dialogkatalog ist nicht vollständig umgesetzt;
implementiert sind die drei gesonderten Interview-Gespräche aus content/dialoge.md.
