# SMARTcoach · Grundgerüst 0.1

Klickbares PWA-Mock-up für Android-Tablets, umgesetzt mit HTML, CSS und Vanilla
JavaScript. **Phase A**: Orientierung, Navigation und gestalterische Prüfung mit
fiktiven Daten. Keine medizinische Beratung, keine echte Patientenakte.

## Bereits bedienbar

- Ruhebildschirm: eine Berührung öffnet das Dashboard.
- Geschwungene Journey von Ernst Baumann; acht Stationen in der Übersicht,
  alle 14 Demo-Ereignisse über Detailfenster erreichbar. Ereigniskarten mit Quelle.
- Gesamter Weg, zwei Detailstufen, Demo-Heute ±14 Tage und Navigation zu
  früheren/späteren Zeitfenstern. Die Abstände sind schematisch, kein Heilungsgrad.
- Perspektiven Ernst / Anna mit gemeinsamem Verlauf und angepasstem Kontext.
- Aktive Begleitung: standardmässig AUS, verständlicher Einwilligungsdialog,
  bestätigtes Einschalten und sofortiges Ausschalten. **Keine automatischen Impulse.**
- Globales „Beenden“, auch innerhalb der Bestätigungsdialoge: stoppt Medien und
  kehrt in den Ruhemodus zurück. Die Zustimmung bleibt beim Beenden erhalten.
- Lokal gespeicherte Perspektive, Schriftgrösse und Einwilligung; Demo-Reset
  erhält die Schriftgrösse. Jeder App-Start öffnet den Ruhebildschirm.
- Manifest, PNG-Icons, Service Worker und Offline-App-Shell ohne externe Ressourcen.

## Bewusste Platzhalter

„SMARTcoach fragen“, „Übungen“, „Berichte & Erklärungen“ und „Tagebuch“ öffnen
eigene Ansichten, die den späteren Nutzen erklären. Noch kein Chat, keine
Tagebucheinträge, vollständigen Berichte, Quiz, KI, EPIC-Anbindung oder Coachinglogik.
Keine Medienauswahl und keine Medienwiedergabe in dieser Version. Die spätere
Sammlung unter `Documents/SMART` wird nicht über GitHub geladen. Das Ruhebild
ist zunächst eine ruhige Farbfläche.

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
Ansichten: [Querformat](docs/screenshots/home-landscape.png),
[Hochformat](docs/screenshots/home-portrait.png), [Ruhebildschirm](docs/screenshots/idle.png).

## Weiterentwicklung

- `demo-data.js`: redaktionelle Ereignisse J00–J13 mit stabilen IDs und Demo-Quellen.
- `app.js`: Navigation, Rollen, Einwilligung und lokale Einstellungen.
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
