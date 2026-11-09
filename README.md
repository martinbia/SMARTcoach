# SMARTcoach · Lokale Videos und Demo-Inhalte 0.3.2

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
Weitere Termine, Uhrzeiten oder Therapieanordnungen werden nicht erfunden.

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
zeigt die drei Mobilitätsfilme zu Gehen und Treppen. Die Zuordnung erfolgt anhand
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

**Video ansehen** öffnet den Film und startet die Wiedergabe direkt. Das Video
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

**Kein Kompilieren erforderlich.** Nach einer Änderung im Repository veröffentlicht
GitHub Pages die statischen Dateien neu. Anschliessend in der PWA unter
**Einstellungen → Inhalte neu laden** aktualisieren oder die Seite neu laden.
Offline bleiben die zuletzt geladenen Inhalte verfügbar. Die Markdown-Dateien
werden bevorzugt aus dem Netz geladen; die App-Shell bleibt versioniert gecacht.
Eine Neuinstallation der PWA ist für reine Textänderungen nicht nötig.

Format, Datenbezüge und Bewertung von Markdown gegenüber JSON/YAML:
[Inhalte bearbeiten](docs/INHALTE.md).

## Weiterhin bewusst offen

Fragen stellen bleibt ein navigierbarer Platzhalter ohne KI. Die Eintragsansichten
zeigen vorbereitete fiktive Beispiele, keine vollständige Tagebuch-Eingabe oder
Speicherung persönlicher Angaben. Keine EPIC-Verbindung, kein Quiz und keine
automatischen Coaching-Impulse. Medikamente, Belastungsfreigaben und Übungsdosen
werden nicht erfunden. Audio ist weiterhin nicht eingebunden.

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
- `content/*.md`: redaktionelle Datenquelle ohne Build-Schritt.
- `dashboard-data.js`: Rollentexte, Wochenaufgaben und Annas sechs Begleitstationen.
- `app.js`: Navigation, Rollen, getrennte Einwilligungen und lokale Einstellungen.
- `idle-image.js`: lokale Foto-Prüfung und IndexedDB-Speicher für das Ruhebild.
- `styles.css`: responsive Ansichten, grosse Touch-Ziele und Fokusdarstellung.
- `sw.js`: nur explizite App-Shell-Dateien cachen; Cache-Version bei Änderungen
  an App-Dateien erhöhen. Neue Versionen werden nach Schliessen alter Tabs aktiv.
- `manifest.webmanifest`: Installation und Start im Standalone-Modus.

Einstellungen liegen unter `smartcoach.preferences.v1` im `localStorage` des
Browsers. Löschen der Browser-/Website-Daten entfernt sie. Bei gesperrtem Speicher
bleibt die App in der Sitzung benutzbar und zeigt einen Hinweis. Demo-Datum und
Beispielpersonen sind in Phase A bewusst fest hinterlegt. Es werden keine echten
Gesundheitsdaten erhoben und keine Daten an Dienste gesendet.

Die drei ursprünglichen Konzeptdateien bleiben unverändert die Grundlage für
spätere Phasen. Der Dialogkatalog ist noch keine implementierte Dialog-Engine.
