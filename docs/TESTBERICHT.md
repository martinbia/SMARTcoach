# SMARTcoach 0.3.1 – Lokale Videowiedergabe und Markdown-Inhalte

Prüfdatum: 09.11.2026. Lokale Cloud-Entwicklungsumgebung, Python 3.12.14,
Playwright 1.62.0, Chromium 156.0.8078.79 (headless). Ausschliesslich fiktive Daten.

## Ausführung und Ergebnis

`python3 -m unittest discover -s tests -v`

**34 Tests ausgeführt, 34 bestanden, 0 fehlgeschlagen, 0 übersprungen.**
Laufzeit der finalen Ausführung: 27,1 Sekunden. Keine JavaScript-Laufzeitfehler in
den geprüften Ansichten. Die Suite nutzt echte Browserkontexte und einen lokalen
HTTP-Server unter `/SMARTcoach/`; Root-Hosting wird separat geprüft.

## Korrektur der Videowiedergabe

Ein konkreter Ablaufdefekt wurde reproduziert: Beim Öffnen eines Films während
des noch laufenden Mehrfachimports blieb der Player nach Importabschluss
deaktiviert. Er wird jetzt automatisch bereitgestellt. Auch Navigation während
der direkten Einzelauswahl wird mit verzögertem Dateilesen geprüft.

Vor der Korrektur wurde ein MP4 mit Android-typischem MIME-Typ
`application/octet-stream` abgelehnt; ein Name mit Download-Zusatz `(1)` blieb
ohne Zuordnung. Beide Fälle werden jetzt erfolgreich importiert und tatsächlich
abgespielt. Eine direkte Auswahl beim einzelnen Film akzeptiert abweichende Namen.
Der Speicher enthält unabhängig eingelesene Blob-Bytes statt des ursprünglichen
File-Objekts. Die Dateityp-Normalisierung ist keine Codec-Konvertierung.

Weitere neue Prüfungen: echte Wiedergabe trotz simuliertem Schreib-/Quota-Fehler
(als Sitzungskopie gekennzeichnet), Migration eines alten File-Datensatzes und
Erholung nach einer beschädigten MP4 durch direkte Neuauswahl. Der unbrauchbare
Player wird bei Medienfehlern ausgeblendet; ein lesbarer Hinweis bleibt sichtbar.
Die direkte Auswahl mit langem Dateinamen wurde zusätzlich bei 360 Pixeln mit
sehr grosser Schrift ohne horizontalen Überlauf geprüft. Der bestehende Test für
Offline-Neustart, erneute Wiedergabe, Löschen und globales Beenden besteht weiter.
Service-Worker-App-Shell-Version: `v0.3.1`.

Diese Ergebnisse belegen die genannten technischen Fehler und Korrekturen. Sie
bestimmen nicht den Codec oder die genaue Ursache des Fehlers der sieben privaten
Originalfilme auf dem physischen Tablet; diese Dateien standen nicht zur Verfügung.

## Bestehende Funktionen und Regressionen

| Prüfung | Ergebnis und Abdeckung |
| --- | --- |
| Ruhemodus / Ereignisse | Berührung öffnet Dashboard; Operation, Austritt und Heute mit Quellen erreichbar |
| Personenwechsel | Name, Profilillustration, Rollenbezeichnung, Journey und Funktionen wechseln; Auswahl überlebt Neustart |
| Beide Dashboards | Vier Hauptfunktionen, Wochenaufgaben, Termin E07, aktive Begleitung und Beenden erreichbar; alle wesentlichen Bereiche bei 1280×800 ohne Scrollen |
| Annas Begleit-Woche | Sechs eigene Themen; Anleitungen und Begleitweg; keine vorgetäuschten erledigten Aufgaben oder erfundenen Uhrzeiten |
| Detaillierte Wege | Ernst: alle 14 Ereignisse und vorhandene Zoom-/Zeitfenstersteuerung. Anna: sechs Wochenstationen und gemeinsame medizinische Termine. Rückkehr vom Ereignis zum Weg erhält das Zeitfenster |
| Einwilligung je Person | AUS als Standard; bestätigtes Einschalten, Abbrechen und Escape; Ausschalten sofort; getrennte Zustände über Neustart; Dialog benennt Person |
| Migration | Alte globale Zustimmung wird nur für die zuletzt ausgewählte Person übernommen, andere Person bleibt AUS |
| Einstellungen / Reset | Schriftgrösse, Zustimmung und Rolle lokal; Interview-Reset erhält Schriftgrösse und Ruhebild und setzt Demo zurück |
| Beenden / Medien | Aus Fach-, Detail-, Einstellungs- und Dialogansichten zurück in Ruhemodus; Pause-/Reset-Hook und Sprachsyntheseabbruch geprüft |
| Markdown-Berichte und Einträge | Acht Berichte, fünf Beispiel-Einträge, Quellenbezüge und Datum aus dem zugehörigen J-Ereignis; private Anna-Demo-Sorge erscheint nicht bei Ernst |
| Laufzeitänderung ohne Build | Geändertes Termin-Datum in genesungsweg.md erscheint im Dashboard, Pfad und Bericht E07 ohne JavaScript-Änderung |
| Fehler / sichere Darstellung | Unvollständige Inhaltsdatei zeigt Fehler und Wiederholen; Markdown-HTML bleibt Text, Fettdruck funktioniert |
| Videokatalog | Sieben Themen bei Ernst, drei Mobilitätsanleitungen bei Anna; fehlender Film zeigt Auswahlhinweis und keinen entfernten src |
| Lokale Videowiedergabe | Synthetischer VP9-in-MP4-Testclip lokal importiert, spielt erst nach Klick, stoppt und setzt bei Beenden zurück; Offline-Neustart, erneute Wiedergabe und Löschen der Kopie geprüft; kein Upload-Request |
| Neue Inhaltsansichten | Videoauswahl, Berichte und Einträge bei 360 Pixeln und sehr grosser Schrift ohne horizontalen Überlauf |
| PWA / Offline | Manifest, Icons und Chromium-Installierbarkeitsdiagnose ohne Fehler; Offline-Neuladen, Rollenwechsel und Annas Detailweg einschliesslich Profilasset funktionieren |
| Cache / Root-Hosting | Offline auch am Domain-Root; Nur die drei redaktionellen content/*.md werden gezielt gecacht; die ursprüngliche Spezifikation wird nicht aufgenommen |
| Speicherfehler | Gesperrter localStorage und beschädigte Einstellungen bleiben benutzbar und führen nicht zur Einwilligung |
| Lokales Ruhebild | Import, Offline-Neustart, Löschen, Erhalt beim Demo-Reset; beschädigte/zu grosse Dateien und gesperrte IndexedDB abgefangen |
| Animation | Synchroner Text-/Bildwechsel, Pause, reduzierte Bewegung und Abbruch beim Öffnen des Dashboards |
| Responsive / Tastatur | Beide Rollen bei 1280×800, 800×1280, 600×960 und 360×800, beide Schriftgrössen; kein horizontaler Seitenüberlauf; Touch-Ziele mindestens 48×48; Modal-Fokus, Skip-Link und Browser-Zurück |
| Breitere Schriftmetriken | Die bekannte Regression bei 360 Pixeln mit sehr grosser Schrift und zusätzlichem Zeichenabstand bleibt geprüft; Kopfaktionen dürfen umbrechen |

Zusätzlich bestanden: `node --check app.js`, `node --check dashboard-data.js`,
`node --check content.js`, `node --check local-videos.js`,
`node --check sw.js` und `git diff --check`. Die drei ursprünglichen Konzeptdateien
und `idle-image.js` sind unverändert. Die bisherigen J-Ereignisse liegen jetzt
als direkt geladene Quelle in content/genesungsweg.md; demo-data.js enthält nur
noch den initialen Kontext. Der Inhaltstermin J10 wurde im Test gezielt verändert
und die gemeinsame Anzeige in Bericht und Pfad verifiziert.

## Visuelle Abnahme

Die beiden WebP-Referenzen wurden vor der Implementierung geöffnet und analysiert.
Screenshots bei 1280×800 und 800×1280 wurden für beide Personen aufgenommen:

- [Ernst quer](screenshots/ernst-dashboard-landscape.png)
- [Ernst hoch](screenshots/ernst-dashboard-portrait.png)
- [Anna quer](screenshots/anna-dashboard-landscape.png)
- [Anna hoch](screenshots/anna-dashboard-portrait.png)

Nach dem Vergleich wurden Kopfbereich, Kartenhöhen und Abstände kompakter,
Spitalmarker klarer beschriftet und die Journey-Verbindungen für umgebrochene
Hochformat-Ansichten ergänzt. Beide 1280×800-Screenshots passen vollständig in
den Viewport. Bei kleineren Höhen, sehr grosser Schrift und Detailfenstern ist
vertikales Scrollen zugunsten der Lesbarkeit erlaubt. Es werden keine künstlichen
Android-Leisten gezeichnet. Weitere Designentscheidungen und Datengrenzen stehen
in [GUI-DESIGN.md](GUI-DESIGN.md).

## Grenzen der Prüfung

Die lokalen Ergebnisse beweisen noch keinen erfolgreichen neuen GitHub-Actions-
Lauf oder Pages-Deploy. Neue CI-Ergebnisse sind nach dem Push separat zu prüfen.
Es wurde nichts gemergt oder veröffentlicht.

Die tatsächliche Android-Installation, Dateiauswahl, TalkBack, Nutzung mit echten
Systemleisten und Lesbarkeit auf einem physischen 10-Zoll-Tablet sind weiterhin
am Gerät zu prüfen. Automatische Layoutprüfungen ersetzen keine Nutzertests.
Browser-/Website-Speicher kann vom Betriebssystem entfernt werden. Die sieben
Originalfilme waren in der Cloud nicht verfügbar und wurden nicht inhaltlich oder
mit ihren tatsächlichen Codecs geprüft. Der technische Wiedergabetest verwendet
einen synthetischen MP4-Clip aus tests/video_fixture.py, der nicht zum Pages-
Artefakt gehört. Echte Android-Dateiauswahl, Quota und Codec-Kompatibilität bleiben
am Tablet zu prüfen. KI, EPIC, eigene Tagebuch-Eingaben und automatisches Coaching
gehören nicht zu dieser Implementierung.

## Neue redaktionelle Dateien

Bearbeitung, unterstütztes Markdown-Format, IDs und Bewertung von Alternativen:
[INHALTE.md](INHALTE.md). Die Rohdaten sind content/berichte.md,
content/genesungsweg.md und content/videos.md. Inhaltliche Änderungen benötigen
keinen Compiler; nach statischem Deploy kann die PWA sie neu laden. Die tatsächliche
fachliche Freigabe von Übungen wird durch diese UI-Prüfung nicht ersetzt.

Neue Ansichten: [Videoauswahl Ernst](screenshots/videoauswahl-ernst.png),
[Anleitungen Anna](screenshots/videoauswahl-anna.png),
[Videoauswahl hoch](screenshots/videoauswahl-portrait.png),
[Operationsbericht](screenshots/bericht-operation.png),
[Einträge](screenshots/eintraege-ernst.png).

Aktuelle Screenshots der Korrektur vom 09.11.2026, jeweils 1280 Pixel breit und
mit synthetischem Testfilm: [Player bereit](screenshots/video-player-ready.png)
und [lesbare Fehlermeldung](screenshots/video-player-error.png). Der kleine
Testclip stellt keine der sieben Übungsaufnahmen dar.
