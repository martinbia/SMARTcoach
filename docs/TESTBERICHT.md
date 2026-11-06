# SMARTcoach 0.1 – Prüfung von Phase A

Prüfdatum: 06.11.2026. Lokale Cloud-Entwicklungsumgebung, Python 3.12.14,
Playwright 1.62.0, Chromium 156.0.8078.79 (headless). Keine echte Patientendaten.

## Automatisierte Funktionsprüfung

Aufruf: `python3 -m unittest discover -s tests -v`.

Die Suite verwendet einen lokalen HTTP-Server und echte Browserkontexte. Der
Standardpfad ist `/SMARTcoach/`; Root-Hosting wird zusätzlich separat geprüft.

| Prüfung | Abgedecktes Verhalten |
| --- | --- |
| Ruhemodus und Ereignisse | Dashboard per Berührung; Operation, Austritt und Heute öffnen passende Inhalte mit Demo-Quelle |
| Einwilligung | Standard AUS, Abbrechen und Escape ohne Zustimmung; bestätigtes EIN überlebt Neustart; AUS sofort und dauerhaft |
| Perspektive | Anna-Kontext, identische Journey und gespeicherter Rollenwechsel |
| Journey-Navigation | Übersicht, Detailfenster 23.10.–20.11., Fensterwechsel, Rückkehr zu Demo-Heute und Vergrösserung |
| Navigation / Beenden | Vier Platzhalter und Einstellungen; Beenden auch aus Modal; keine versehentliche Zustimmung |
| Einstellungen / Reset | Sehr grosse Schrift und Zustimmung nach Reload; Reset auf Ernst/AUS/Übersicht erhält Schriftgrösse |
| PWA / Offline | Scope unter Repository-Pfad, Manifest und Icons vorhanden; offline neu laden und Ereignisse öffnen; Zustimmung bleibt erhalten |
| Root-Hosting / Caching | Offline auch am Domain-Root; abgerufene Markdown-Dokumente landen nicht im App-Cache |
| Speicherfehler | Gesperrter Schreibzugriff und beschädigte Einstellungen führen nicht zum Ausfall oder automatischer Einwilligung |
| Responsive / Tastatur | 1280×800, 800×1280, 600×960 und 360×800, jeweils beide Schriftgrössen; kein horizontaler Seitenüberlauf; Touch-Flächen mindestens 48×48; Modal-Fokus und Escape |
| Globaler Medienstopp | Eingesetztes Test-Medienelement erhält Pause/Reset; Sprachsynthese wird abgebrochen. Noch kein realer Medienplayer im Produkt |
| Skip-Link / Browser-Zurück | Inhaltsfokus ohne Navigation in Ruhemodus; Zurück von Fachansicht zur Journey |
| Installierbarkeitsdiagnose | Chromium-Manifest- und Installierbarkeitsprüfung im normalen persistenten Browserprofil |
| Lokales Ruhebild | Fotoimport, Blob-URL, Offline-Neustart, Entfernen und Erhalt beim Interview-Reset |
| Animation | Synchrones Ausblenden und Aufhellen, Bildbewegung, dauerhafte Pause und reduzierte Bewegung |
| Bildfehler | Beschädigte Datei, Dateigrössenlimit und nicht verfügbarer IndexedDB-Speicher |

Screenshots in `docs/screenshots/` wurden mit Chromium aufgenommen und visuell
geprüft. Sie zeigen den Ruhebildschirm und die komplette Dashboard-Seite im Hoch-
und Querformat. Scrollen ist auf kleineren Displays vorgesehen.

Zusätzlich: `node --check app.js`, `node --check demo-data.js`, `node --check idle-image.js`,
`node --check sw.js` sowie `git diff --check`.

## Ergebnis

**16 Tests ausgeführt, 16 bestanden, 0 fehlgeschlagen, 0 übersprungen**
(Laufzeit 12,8 Sekunden, einschliesslich Ruhebild-Erweiterung). Keine JavaScript-Laufzeitfehler in den geprüften Ansichten.
Chromium meldet im normalen Browserprofil keine Manifest- oder
Installierbarkeitsfehler. Die zusätzlichen Syntax- und Diff-Prüfungen bestanden.
Die GitHub-Actions-Ausführung wird erst nach dem Push ausgelöst und ist getrennt
von dieser lokalen Ausführung zu bewerten.

## Noch auf echtem Tablet zu prüfen

- GitHub Pages über HTTPS, Installation aus dem normalen Android-Chrome-Profil
  und Start über das Startbildschirm-Icon im Standalone-Modus.
- Offline öffnen nach komplettem Schliessen der installierten App; Einstellungen
  nach erneutem App-/Gerätestart prüfen.
- Lesbarkeit, natürliche Berührungen, Bildschirmtastatur, TalkBack und tatsächliche
  Geräteausrichtung mit älteren Testpersonen. Automatische Grössenprüfungen
  ersetzen keine Prüfung der Barrierefreiheit oder einen Nutzertest.
- Website-/Browser-Speicher kann vom Betriebssystem gelöscht werden. Keine
  Zusicherung dauerhafter Speicherung.
- Die Fotoauswahl aus `Documents/SMART` ist lokal im Browser geprüft, muss aber
  noch mit dem Android-Dateiauswahldialog getestet werden. Reale Audio-/Video-
  Wiedergabe und automatisches Coaching gehören zu späteren Phasen.

Kein Android-Gerät, keine tatsächliche Installation und kein produktiver
GitHub-Pages-Deploy wurden in dieser Cloud-Sitzung getestet.
