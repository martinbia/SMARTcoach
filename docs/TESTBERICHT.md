# SMARTcoach 0.3.4 – Videozeilen und GUI-Freeze

Prüfdatum: 09.11.2026. Lokale Cloud-Entwicklungsumgebung, Python 3.12.14,
Playwright 1.62.0, Chromium 156.0.8078.79 (headless). Ausschliesslich fiktive Daten.

## Ausführung und Ergebnis

`python3 -m unittest discover -s tests -v`

**37 Tests ausgeführt, 37 bestanden, 0 fehlgeschlagen, 0 übersprungen.**
Laufzeit der finalen Ausführung: 34,6 Sekunden. Keine JavaScript-Laufzeitfehler in
den geprüften Ansichten. Die Suite nutzt echte Browserkontexte und einen lokalen
HTTP-Server unter `/SMARTcoach/`; Root-Hosting wird separat geprüft.

## Videozeile antippen und GUI-Freeze

Zusätzlich zum vorhandenen Button öffnet jetzt die gesamte Filmzeile den
zugehörigen Player mit demselben Wiedergabeablauf. Die bestehende Prüfung aller
sieben Filme verwendet abwechselnd Klicks auf die Titelzelle, die freie Fläche
der rechten Zelle und den Button. Bei Annas drei Filmen wird die Titelzelle
per Touch angetippt. Für jede Öffnung werden das richtige Navigationsziel und
eine tatsächlich fortschreitende Wiedergabe des synthetischen Clips geprüft.
Die vorhandene Tastaturprüfung des nativen Buttons besteht weiter.

Die sichtbare Änderung beschränkt sich auf den Mauszeiger über der Videozeile.
Willkommens-/Ruhebildschirme und Hauptmenüs sind ausdrücklich in AGENTS.md und
GUI-DESIGN.md als eingefroren dokumentiert. Bezugspunkt ist `main` bei `25a270f`.
Die Anzeige- und Animationsfunktionen dieser Ansichten sind unverändert.

Ein separater Vorher-/Nachher-Vergleich mit diesem Commit, demselben Chromium
und identischen Viewports ergab **12 von 12 pixelgleiche Ansichten**:

- Ernst und Anna, jeweils 1280×800 und 800×1280.
- Ruhebildschirm ohne Foto, jeweils beide Viewports.
- Ruhebildschirm mit lokal ausgewähltem Test-PNG bei festgehaltenen
  Animationszeiten 0 und 16 Sekunden, jeweils beide Viewports.
- Ruhebildschirm mit Test-PNG und reduzierter Bewegung, jeweils beide Viewports.

Temporäre Vergleichsbilder und Ergebnisprotokoll wurden unter
`/tmp/smartcoach-gui-freeze/` erzeugt. Bestehende Screenshot-Referenzen wurden
nicht überschrieben. Das private Luzern-Foto lag nicht vor; der Vergleich
prüft die Darstellung und Animation mit einem lokalen Testbild.

## Kompakte Videoübersicht

Die Karten in Übungen/Anleitungen wurden durch eine semantische Tabelle ersetzt.
Jede Zeile enthält ausschliesslich den Titel und eine Schaltfläche „Video ansehen“.
Die Schaltflächen tragen zusätzlich einen zugänglichen Namen mit dem Filmtitel.
Hinweise bleiben auf der Videoseite erhalten; Auswahl und Zuordnung bleiben in
den Einstellungen. Es wurden keine Daten oder Zuordnungen geändert.

Die bestehende Katalogprüfung kontrolliert jetzt, dass alle sieben Einträge bei
1280×800 und 800×1280 vollständig im sichtbaren Bereich liegen und die
Abspielschaltflächen mindestens 48×48 CSS-Pixel messen. Das Öffnen des ersten
Films per Tastatur und die drei rollenspezifischen Anleitungen für Anna sind
ebenfalls geprüft. Die Prüfung bei 360 Pixeln und sehr grosser Schrift bleibt
erhalten; dort darf vertikal gescrollt werden.
Bei der Screenshot-Aufnahme im Querformat betrug die gesamte Seitenhöhe
800 Pixel bei 800 Pixeln Viewporthöhe; die letzte Filmzeile endete bei 669 Pixeln.

Aktuelle Screenshots: [Ernst quer](screenshots/videoauswahl-ernst.png),
[Ernst hoch](screenshots/videoauswahl-portrait.png) und
[Anna quer](screenshots/videoauswahl-anna.png).

## Erhaltene Videoansicht und Dateiverwaltung

Dateien werden ausschliesslich unter Einstellungen → Lokale Übungsvideos
ausgewählt. Dort sind Mehrfachimport, direkte Zuordnung einzelner Dateien mit
abweichendem Namen und Entfernen lokaler Kopien verfügbar. Die Tests prüfen,
dass Übungen/Anleitungen und Player keine Dateieingabefelder enthalten.

Alle sieben Katalogeinträge wurden mit dem synthetischen Testclip importiert und
bei Ernst geöffnet; die drei passenden Einträge wurden auch bei Anna geöffnet.
Jede Öffnung startet die Wiedergabe ohne zusätzlichen Startklick. Ein simulierter
NotAllowedError beim Start lässt die native Wiedergabetaste und den manuellen
Start verfügbar. „Video erneut starten“ setzt die Abspielposition zurück.

Die Videoansicht verwendet die gesamte Breite und die Höhe unter der Kopfzeile.
Die Kopfzeile enthält SMARTcoach, Zurück zur Übersicht, Personenwechsel und
Beenden. Titel und weitere Bedienelemente liegen unter dem Video. Die tatsächliche
Kopfzeilenhöhe wird nach Grössenwechseln gemessen, das Video wird vollständig und
unverzerrt eingepasst. Geprüft: 1280×800, 800×1280 und 360×800, jeweils normale
und sehr grosse Schrift und beide Personen. Kein horizontaler Überlauf;
Kopfaktionen mindestens 48×48 Pixel. Im Querformat bleibt die Kopfzeile einzeilig,
bei geringer Breite bzw. sehr grosser Schrift darf sie zugunsten der Bedienbarkeit
umbrechen. Rückkehr zur Übersicht wurde per Tastatur geprüft.

## Erhaltene Korrekturen der Videowiedergabe

Ein konkreter Ablaufdefekt wurde reproduziert: Beim Öffnen eines Films während
des noch laufenden Mehrfachimports blieb der Player nach Importabschluss
deaktiviert. Er wird jetzt automatisch bereitgestellt. Auch Navigation während
der direkten Einzelauswahl wird mit verzögertem Dateilesen geprüft.

Vor der Korrektur wurde ein MP4 mit Android-typischem MIME-Typ
`application/octet-stream` abgelehnt; ein Name mit Download-Zusatz `(1)` blieb
ohne Zuordnung. Beide Fälle werden jetzt erfolgreich importiert und tatsächlich
abgespielt. Die Einzelzuordnung in den Einstellungen akzeptiert abweichende Namen.
Der Speicher enthält unabhängig eingelesene Blob-Bytes statt des ursprünglichen
File-Objekts. Die Dateityp-Normalisierung ist keine Codec-Konvertierung.

Weitere neue Prüfungen: echte Wiedergabe trotz simuliertem Schreib-/Quota-Fehler
(als Sitzungskopie gekennzeichnet), Migration eines alten File-Datensatzes und
Erholung nach einer beschädigten MP4 durch direkte Neuauswahl. Der unbrauchbare
Player wird bei Medienfehlern ausgeblendet; ein lesbarer Hinweis bleibt sichtbar.
Die direkte Auswahl mit langem Dateinamen wurde zusätzlich bei 360 Pixeln mit
sehr grosser Schrift ohne horizontalen Überlauf geprüft. Der bestehende Test für
Offline-Neustart, erneute Wiedergabe, Löschen und globales Beenden besteht weiter.
Service-Worker-App-Shell-Version: `v0.3.4`.

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
| Lokale Videowiedergabe | Synthetischer VP9-in-MP4-Testclip aus den Einstellungen importiert; Öffnen über Video ansehen startet direkt, Beenden stoppt und setzt zurück; Offline-Neustart, erneute Wiedergabe und Löschen der Kopie geprüft; kein Upload-Request |
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

Aktuelle Screenshots vom 09.11.2026: [Player quer, 1280×800](screenshots/video-player-ready.png),
[Player hoch, 800×1280](screenshots/video-player-portrait.png),
[lesbare Fehlermeldung](screenshots/video-player-error.png) und
[Videoverwaltung in Einstellungen](screenshots/video-settings.png).
Die drei oben verlinkten Videoübersichten wurden ebenfalls aktualisiert.
Der einfarbige synthetische Testclip stellt keine der sieben Übungsaufnahmen dar.
