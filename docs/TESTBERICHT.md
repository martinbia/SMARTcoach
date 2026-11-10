# SMARTcoach 0.5.0 – Vorbereitete Ansprache-Dialoge und lokale WAV-Dateien

Prüfdatum: 09.11.2026. Lokale Cloud-Entwicklungsumgebung, Python 3.12.14,
Playwright 1.62.0, Chromium 156.0.8078.79 (headless). Ausschliesslich fiktive Daten.

## Ausführung und Ergebnis

`python3 -m unittest discover -s tests -v`

**49 Tests ausgeführt, 49 bestanden, 0 fehlgeschlagen, 0 übersprungen.**
Laufzeit der finalen Ausführung: 47,9 Sekunden. Keine JavaScript-Laufzeitfehler in
den geprüften Ansichten. Die Suite nutzt echte Browserkontexte und einen lokalen
HTTP-Server unter `/SMARTcoach/`; Root-Hosting wird separat geprüft.

## Neue Gesprächsansichten und lokale Bildkonfiguration

Ausgangsstand: `main` bei `2d9185e`. Beauftragte GUI-Bereiche: „Fragen stellen“
mit Chat-/Voice-Demo, die Demo-Röntgenansicht und deren zusätzliche Einstellung.
Die Hauptmenüs und Willkommens-/Ruhebildschirme wurden nicht umgestaltet.

## Vorbereitete Ansprache-Dialoge in den Einstellungen

Ausgangsstand: `main` bei `30b873c`. Ausschliesslich die Einstellungen wurden
um Auswahl A–D, Wartezeit und WAV-Zuordnungen ergänzt. Vier neue Browserprüfungen
erweitern die bestehende Suite auf 49 Tests:

| Prüfung | Ergebnis und Abdeckung |
| --- | --- |
| Dialogkatalog und Konfiguration | IDs, Sprecher und Volltexte für A–D; Auswahl lokal wiederhergestellt; Wartezeit 5 und 3600 akzeptiert, 4 verworfen; alle 13 Zeilen A1–D5 freigegeben und konfigurierbar (siehe aktuelle Timerprüfung unten) |
| WAV-Datei und Probehören | Generischer Android-MIME-Typ mit `.wav`-Endung angenommen, RIFF/WAVE-Header geprüft; Probe startet nur nach Tap und stoppt durch erneutes Antippen, Navigation oder globales Beenden |
| Ersetzen / Entfernen / Offline | A1 wird unter stabiler ID ersetzt; Dateiname und Blob bleiben nach Reload und Offline-Neustart verfügbar; Entfernen löscht nur die Browserkopie |
| Speicherfehler und ungeeignete Datei | Falsche Endung und ungültiger Inhalt abgefangen; bei blockierter IndexedDB wird die Kopie ausdrücklich als „Nur für diese Sitzung“ angezeigt |
| Hoch- und Querformat / automatische Ansprache | 1280×800 und 800×1280 ohne horizontalen Überlauf, Schaltflächen mindestens 48 CSS-Pixel; Timer startet nur bei vollständig freigegebenem Dialog und lokalen WAV-Dateien (siehe aktuelle Timerprüfung unten) |

Die WAV-Dateien in den Tests sind synthetische Browser-Fixtures. Dateiauswahl und
Wiedergabe mit Androids tatsächlichem Dateidialog, Decoder und Audioausgang
müssen am Tablet geprüft werden. Browser-/Website-Speicher kann vom Betriebssystem
entfernt werden.

Ein pixelweiser Vorher-/Nachhervergleich mit `main` bei `30b873c` ergab **6/6
pixelgleiche** eingefrorene Ansichten: Ruhebildschirm ohne lokales Foto sowie
Ernst- und Anna-Dashboard bei 1280×800 und 800×1280. Der Ruhebildschirm wurde in
beiden Builds mit reduzierter Bewegung gerendert. Die Einstellungen waren die
einzige beabsichtigte visuelle Ergänzung. Bestehende Referenz-Screenshots wurden
nicht verändert.

Acht neue Browserprüfungen ergänzen die bestehenden 37 Prüfungen:

| Prüfung | Ergebnis und Abdeckung |
| --- | --- |
| Januar-Gespräch | Einzelne Beiträge, Tastatursteuerung, Vorheriger Schritt, Neustart, Abschluss und neue Gesprächsauswahl; Beispieltermin 26.01.2027, Geburtstag 25.01.; J10 bleibt 10.11.2026 |
| Übungs-Gespräch | Lokaler Film V07 aus dem Gespräch startet tatsächlich; am Filmende Rückkehr zu Ernsts Hauptmenü; übrige Videobibliothek unverändert geprüft |
| Fehlende Medien / Beenden | Fehlendes Video und noch nicht ausgewähltes Röntgenbild zeigen Hinweise; Beenden führt in Ruhemodus |
| Lokales Demo-Röntgenbild | PNG mit generischem MIME-Typ ausgewählt, korrekt angezeigt und benannt; Interview-Reset und Offline-Neustart erhalten Auswahl; Entfernen löscht nur Kopie; kein Upload-Request |
| Bildfehler / Speicherfehler | Beschädigte PNG, nicht unterstützte DICOM-Datei und gesperrte IndexedDB abgefangen |
| Voice / TTS | Lokale deutsche Stimme wird gegenüber einer angebotenen Online-Stimme ausgewählt; Ernsts Frage und Coach-Antwort werden an die TTS-API übergeben; globales Beenden cancelt, kein automatisches Wiederanlaufen |
| Markdown als Quelle | Geänderter Dialogtext erscheint ohne JavaScript-Änderung; ungültiges Videoziel V99 erzeugt Inhaltsfehler |
| Responsive / Textfallback | Dialog in 1280×800, 800×1280 und 360×800 mit beiden Schriftgrössen; kein horizontaler Überlauf, Buttons mindestens 48×48; bei fehlender lokaler Stimme deaktivierter Vorlesebutton; Bildauswahl mit langem Namen und Bildansicht bei 360 Pixeln geprüft |

Der TTS-Test verwendet API-Doubles für Stimme und Sprechauftrag. Er beweist die
lokale Auswahlregel und den Abbruch, **keine hörbare Android-Sprachausgabe**.
Im Headless-Browser war keine lokale deutsche Stimme verfügbar; der Textfallback
funktioniert. Verfügbarkeit, Klang und Offline-Betrieb der tatsächlichen
Android-TTS-Engine müssen am Tablet geprüft werden. Es gibt weder Spracherkennung
noch einen KI-, EPIC- oder Kalenderzugriff.

Das Demo-Röntgenbild wurde mit einem lokalen Test-PNG (App-Icon) geprüft, nicht
mit einer medizinischen Aufnahme. Das künftig vom Nutzer gewählte Bild sowie
die sieben privaten Originalfilme waren in der Cloud nicht vorhanden.

Neue Screenshots, ohne Ersetzen vorhandener Referenzbilder:
[Gesprächsauswahl](screenshots/dialogue-topics-landscape.png),
[Januar-Gespräch](screenshots/dialogue-calendar-landscape.png),
[Voice-Demo hoch](screenshots/dialogue-voice-portrait.png) und
[Röntgenbild noch nicht ausgewählt](screenshots/dialogue-xray-missing.png).

## GUI-Freeze erneut geprüft

Vorher-/Nachher-Vergleich mit `2d9185e`, identischem Chromium und identischen
Viewports: **12 von 12 Ansichten pixelgleich**. Enthalten sind Ernst und Anna,
Ruhebildschirm ohne Foto, mit lokalem Testbild bei 0 und 16 Sekunden Animationszeit
sowie mit reduzierter Bewegung, jeweils bei 1280×800 und 800×1280.
Vor den Animationsaufnahmen wurden die Animationen über ihre `ready`-Promises
synchronisiert und pausiert. Ein vorheriger unsynchronisierter Lauf enthielt
zeitbedingte Abweichungen; am Anwendungscode der eingefrorenen Ansichten wurde
dafür nichts geändert. Temporäre Ergebnisse: `/tmp/smartcoach-dialogue-gui-freeze/`.
Das private Luzern-Foto stand nicht zur Verfügung; benutzt wurde ein Test-PNG.
Bestehende Referenzbilder wurden nicht ersetzt.

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

## Timer und automatische WAV-Dialoge

Aktueller Stand: `feat/release-dialog-d5`, Cache-Version `v0.5.3`. Die Wartezeit
läuft nur auf dem sichtbaren Ruhebildschirm für Ernst, wenn Aktive Begleitung
eingeschaltet, ein vollständiger freigegebener Dialog gewählt und jede zugehörige
WAV-Datei lokal vorhanden und lesbar ist. Ein Aufenthalt startet mit der vollen
Wartezeit; Neurendern setzt sie nicht zurück. Navigation, Beenden und Wechsel in
den Hintergrund stoppen den Timer. Nach Ablauf öffnet der getrennte Chatmodus
den Katalogdialog; Patientenantworten brauchen einen bewussten Tap. Autoplay-Fehler
lassen Text und eine explizite Wiedergabe-/Stummfortsetzen-Auswahl sichtbar.
Verspätete Medienfehler eines vorherigen WAVs werden nicht der nächsten Zeile
zugeordnet.

Acht gezielte Browserprüfungen bestanden (Chromium 156.0.8078.79, Playwright
1.62.0): Einwilligung/Vollständigkeit und fehlende Datei, Timer mit 5 und 60
Sekunden, Wiederholung nach Navigation, Hintergrundwechsel und Rückkehr, alle
Dialoge A–D samt Dialogtexten, Sprecherwahl, lokalem WAV-Blob und Gesprächsende,
Autoplay-Blockierung und globaler Stopp. Zusätzlich bestanden die bestehenden
Prüfungen für Gesprächs-Kalendernavigation, Übungsvideo sowie Service-Worker- und
Offline-Neustart. **8 Tests ausgeführt, 8 bestanden.** Die vollständige Suite
wurde für diesen Funktionsumfang nicht erneut ausgeführt.

Der pixelweise RGB-Vergleich von Ruhebildschirm sowie Ernst- und Anna-Dashboard
mit dem Ausgangsstand `d054778` wurde bei 1280×800 und 800×1280 durchgeführt.
Alle sechs Ansichten zeigen erwartete reine Textunterschiede: Der Ruhebildschirm
erklärt jetzt, dass automatische Ansprache nur mit aktiver Begleitung möglich
ist; die Dashboards erklären, dass für Ernst ein vollständiger Dialog und lokale
WAV-Dateien nötig sind. Das Overlay ist mangels aktiver Einwilligung und
vollständiger WAV-Konfiguration verborgen. Layout, Positionen und übrige Elemente
blieben unverändert. Referenz-Screenshots wurden nicht verändert.

Es stand kein echtes Android-Tablet zur Verfügung. Native WAV-Auswahl,
Android-Autoplay, Audioausgabe und Hintergrund-/Sperrbildschirmverhalten müssen
nach Bereitstellung auf dem Tablet praktisch geprüft werden. Die synthetischen
WAV-Fixtures und Playwright-Mocks prüfen App-Zustände und Ablaufsteuerung, nicht
den Klang eines realen Tablet-Lautsprechers.

## Röntgenbildzugang und lesbare Ereignisdetails

Änderungsstand: `feat/xray-operation-and-detail-readability`, abgeleitet von
`main` bei `9bbc66b`. D03 enthält drei kurze Beiträge und zeigt nach Schritt 3
den vorhandenen Bildbutton. J02 führt zur gleichen lokal gespeicherten
IndexedDB-Abbildung; Rücknavigation geht je nach Herkunft zum Chat oder zurück
zur Operationsinformation. Die Ereignisdetails verwenden 21-px-Informationstext
und eine 12-px-Quellenzeile. Cache-Version: `v0.5.10`.

**13 gezielte Browserprüfungen bestanden** (Chromium/Playwright): D03 und
fehlende Bilddatei, J02 samt Bildauswahl und Rückwegen, J10-Datum, Annas
Begleitdetails, Ereignisdaten aus Markdown, D01/D02-Navigation, automatische
Dialoge A–D, WAV-Zuordnung/Probehören/Offline-Neustart, Einstellungen sowie
Service-Worker-Offline-Neustart. Es gab keine JavaScript-Laufzeitfehler. Die
Dashboards von Ernst und Anna waren im pixelweisen Vergleich mit `main` bei
1280×800 und 800×1280 **4/4 pixelgleich**. Die vollständige Test-Suite wurde
nicht erneut ausgeführt.

Screenshots: [Operation quer, 1280×800](screenshots/operation-detail-landscape.png)
und [Operation hoch, 800×1280](screenshots/operation-detail-portrait.png).
Für das Bildverhalten wurde das lokal vorhandene App-Icon als Testdatei gewählt;
es ist keine medizinische Röntgenaufnahme. Ein echtes Android-Tablet stand nicht
zur Verfügung, daher bleibt der native Tablet-Dateiauswahldialog ungeprüft.

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
Service-Worker-App-Shell-Version: `v0.5.1`.

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
| Cache / Root-Hosting | Offline auch am Domain-Root; die fünf redaktionellen content/*.md werden gezielt gecacht; die ursprüngliche Spezifikation wird nicht aufgenommen |
| Speicherfehler | Gesperrter localStorage und beschädigte Einstellungen bleiben benutzbar und führen nicht zur Einwilligung |
| Lokales Ruhebild | Import, Offline-Neustart, Löschen, Erhalt beim Demo-Reset; beschädigte/zu grosse Dateien und gesperrte IndexedDB abgefangen |
| Animation | Synchroner Text-/Bildwechsel, Pause, reduzierte Bewegung und Abbruch beim Öffnen des Dashboards |
| Responsive / Tastatur | Beide Rollen bei 1280×800, 800×1280, 600×960 und 360×800, beide Schriftgrössen; kein horizontaler Seitenüberlauf; Touch-Ziele mindestens 48×48; Modal-Fokus, Skip-Link und Browser-Zurück |
| Breitere Schriftmetriken | Die bekannte Regression bei 360 Pixeln mit sehr grosser Schrift und zusätzlichem Zeichenabstand bleibt geprüft; Kopfaktionen dürfen umbrechen |

Zusätzlich bestanden: `node --check app.js`, `node --check dashboard-data.js`,
`node --check content.js`, `node --check local-videos.js`,
`node --check xray-media.js`, `node --check sw.js` und `git diff --check`. Die drei ursprünglichen Konzeptdateien
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
am Tablet zu prüfen. KI, echte EPIC-Anbindung, eigene Tagebuch-Eingaben und automatisches Coaching
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

## Android-WAV-Dateiauswahl

Ursache: Der MIME-/Endungsfilter `accept="audio/wav,audio/x-wav,.wav"` schränkte
Androids Auswahl möglicher Apps ein und konnte statt des allgemeinen Dateipickers
Recorder- oder Medien-Apps anbieten. Der WAV-Input verwendet jetzt den generischen
HTML-Datei-Input ohne `accept` und ohne `capture`. Die bestehende Schaltfläche
öffnet ihn weiterhin nur nach einer bewussten Benutzeraktion. Die Validierung
(Endung `.wav`, höchstens 64 MB, vollständiges Einlesen und RIFF/WAVE-Kopf),
IndexedDB-Speicherung und bestehende Zuordnungsfunktionen bleiben erhalten.
Der Service-Worker-Cache wurde auf `v0.5.1` erhöht, damit das aktualisierte
`app.js` nach dem Deploy geladen wird.

Gezielt geprüft: Datei-Chooser-Auslösung, gültige und ungültige WAV-Datei,
Probehören, Ersetzen, Offline-Neustart und Wiederherstellung, fehlerhafte
Dateiendung/-kopf sowie Service-Worker-Cache. Die drei gezielten Browser-Tests
bestanden. Zusätzlich bestanden `node --check app.js`, `node --check sw.js` und
`git diff --check`. Der Test verwendet Chromium am Desktop und bestätigt nicht die
native Picker-Oberfläche von Android. Nach dem Deploy muss auf dem Tablet geprüft
werden, dass `Documents/SMART` über „WAV auswählen“ erreichbar ist; die PWA kann
die konkrete Systemdialog-Oberfläche nicht erzwingen.

## D5-Freigabe und WAV-Konfiguration

D5 zeigt jetzt die neue redaktionelle Textfassung und ist wie die übrigen zwölf
Zeilen für WAV-Auswahl, Probehören, Ersetzen, Entfernen und dauerhafte lokale
Speicherung freigegeben. Die Einstellungen verwenden weiterhin denselben
generischen Datei-Input ohne `accept` oder `capture`; WAV-Auswahl bleibt eine
bewusste Benutzeraktion. Im Speicher werden nur IDs akzeptiert, die als freigegebene
Zeilen aus einem erfolgreich validierten Dialogkatalog stammen. Der allgemeine
Katalogmarker `· GESPERRT` wurde mit einer gesperrten Erweiterungszeile geprüft.

Fünf gezielte Browserprüfungen bestanden: Katalogstruktur und generische Sperren,
D5-Text und -Steuerungen, D5-Probehören, dauerhafte Wiederherstellung nach Reload,
Ersetzen/Entfernen, bisherige WAV-Zuordnungen, ungültige WAV-Dateien sowie
Service-Worker-Offline-Neustart. `node --check app.js`, `node --check content.js`,
`node --check local-prompt-audio.js`, `node --check sw.js` und `git diff --check`
bestanden. Die vollständige Suite wurde gemäss risikobasierter Testvorgabe nicht
erneut ausgeführt.

Vorher-/Nachhervergleich bei identischem Chromium und identischen Viewports:
**6 von 6 eingefrorenen Ansichten pixelgleich** – Ruhebildschirm sowie Ernst-
und Anna-Dashboard bei 1280×800 und 800×1280. Referenz-Screenshots wurden nicht
verändert. Der Service-Worker-App-Shell-Cache steht auf `v0.5.2`, damit die
geänderten Katalog-, Audio- und Einstellungsdateien aktualisiert werden.

## GUI-Redesign des aktiven Dialogs · Variante 4

Dieser Abschnitt hält den ersten Zwischenstand fest. Das Layout wurde danach auf
alle Zustände der Seite „Fragen stellen“ erweitert; der aktuelle Stand und seine
Prüfungen folgen im Abschnitt „Einheitliches Zweispaltenlayout“.

Gezielte Browserprüfungen (Chromium): **7 Tests bestanden**. Geprüft wurden die
Dialogabläufe A–D mit den jeweiligen Katalogantworten, lange Nachrichten und
Zeilenumbrüche, interne Chat-Scrollposition und fehlender horizontaler Überlauf,
WAV-Wiedergabe und blockierte Autoplay-Fallbacks, Abbruch laufender Wiedergabe,
Timer, Navigation, Neustart, manuelle Dialoge D01–D03 sowie Service-Worker-Offline-
Neustart. Der Cache wurde auf `v0.5.4` erhöht, damit die neue SVG-Illustration
offline verfügbar ist.

`node --check app.js`, `node --check sw.js`, Python-Kompilierung der Browserprüfungen
und `git diff --check` bestanden. Der Screenshot
[automatic-dialog-variant4-1280x800.png](screenshots/automatic-dialog-variant4-1280x800.png)
zeigt den laufenden Dialog mit erreichbarer Antwortschaltfläche.

Vorher-/Nachhervergleich auf Basis des aktuellen `main` bei gleichen Viewports:
**6 von 6 eingefrorenen Ansichten pixelgleich** (Ruhebildschirm sowie Ernst- und
Anna-Dashboard bei 1280×800 und 800×1280). Die GUI-Änderung beschränkt sich auf
den aktiven automatischen Dialog; der Ablaufcode für Dialoge, WAVs und Antworten
wurde nicht verändert. Eine native Prüfung auf einem physischen Android-Tablet
war in dieser Umgebung nicht möglich und bleibt vor Ort zu prüfen.

## Einheitliches Zweispaltenlayout für „Fragen stellen“

Zehn gezielte Chromium-Browserprüfungen bestanden: gemeinsames Layout für
Themenauswahl, manuelles D01, automatische Dialoge A–D und Annas Hinweis;
Hochformatdarstellung und fehlender horizontaler Überlauf; bestehende manuelle
Schritte und Mediennavigation; automatische WAV-Wiedergabe, Antworten, Abbruch
und Autoplay-Fallback; Offline-Neustart. Drei Screenshots der Zustände bei
1280×800 liegen in `docs/screenshots/questions-*-landscape.png`. Der
Service-Worker-Cache ist wegen der aktualisierten SVG-Illustration auf `v0.5.5`
erhöht.

`node --check app.js`, `node --check sw.js`, `python3 -m py_compile tests/test_browser.py`
und `git diff --check` bestanden. Die sechs eingefrorenen
Ansichten (Ruhebildschirm sowie beide Dashboards bei 1280×800 und 800×1280)
blieben im Pixelvergleich mit `main` unverändert. Die native Darstellung auf
Android-Hardware wurde nicht geprüft.

## Bereitgestellte PNG für „Fragen stellen“

Bildquelle: `SMARTcoach_Gesundheitsfachkraft_Referenz.png`, unverändert als
`assets/coach-reference.png` abgelegt (SHA-256:
`85d4bb4a3bd97f554606f19bbd263fb66377e6a98b495cadad374315452bae69`).
Wortmarke und Untertitel stehen im Bild; separate HTML-Kopien wurden entfernt.
Der Service-Worker-Cache wurde für das PNG und die geänderte App-Shell auf
`v0.5.7` erhöht.

Die vollständige Browser-Suite bestand mit **56 Tests**. Nach der letzten
CSS-Anpassung bestanden zusätzlich die gezielten Tests für Fragen-Ansicht und
Offline-Neustart. Der Browser-Test prüft Bildpfad, geladene Originalabmessungen
(312×413), unverzerrtes Seitenverhältnis und fehlenden Bildbeschnitt. Bei
1280×800 und 800×1280 ist das PNG vollständig sichtbar, ohne horizontalen
Seitenüberlauf. Die sechs eingefrorenen Ansichten (Ruhemodus sowie Ernsts und
Annas Dashboard in beiden Tabletgrössen) waren im visuellen Vergleich mit dem
unveränderten Branch-Stand pixelgleich. Die Screenshot-Baselines wurden nicht
ersetzt.

Aktuelle Ansichten: [Themenauswahl quer](screenshots/questions-illustration-landscape.png),
[manuelles Gespräch quer](screenshots/questions-illustration-manual-landscape.png),
[manuelles Gespräch hoch](screenshots/questions-illustration-portrait.png),
[automatischer Dialog quer](screenshots/questions-illustration-automatic-landscape.png)
und [Anna quer](screenshots/questions-illustration-anna-landscape.png).
Eine native Prüfung auf einem Android-Tablet steht noch aus.

## Kompakte manuelle Chatsteuerung

Auf der Seite „Fragen stellen“ wurden für die Gesprächsauswahl und D01–D03 die
Voice-Demo- und Chat-Modusbuttons sowie der grüne Interviewhinweis entfernt.
„Andere Gespräche“ steht beim Gesprächsthema. Unter dem scrollbar grossen
Verlauf bleiben Vorheriger Schritt und Nächster Schritt als 48-px-Steuerung;
am Ende erscheint eine kleine Abschlussmeldung. Unnötige Hauptmenü-Aktionen
werden nicht mehr angezeigt; Video- und Röntgenaktionen bleiben erhalten.

Acht gezielte Chromium-Tests bestanden: Schrittnavigation, Zurück zur Auswahl,
Abschluss und langes Chat-Scrollen; Darstellung in beiden Tabletformaten;
manuelle Voice-Demo nicht sichtbar; automatische Dialoge A–D und WAV-Fallback
unverändert. Bei 1280×800 blieb das Zweispaltenverhältnis erhalten und die
Chatlog-Höhe beträgt über 300 px; bei 800×1280 gab es keinen horizontalen
Überlauf. Die linke PNG-Karte blieb unverändert. Der App-Shell-Cache wurde wegen
der geänderten `app.js`/`styles.css` auf `v0.5.8` erhöht; lokale Medien- und
Einstellungsdaten werden dabei nicht gelöscht.

Screenshots: [manuelles Gespräch quer](screenshots/questions-compact-manual-landscape.png)
und [hoch](screenshots/questions-compact-manual-portrait.png). Die eingefrorenen
Ruhe- und Dashboardansichten wurden durch die ausschliesslich auf
`.questions-page` begrenzten Regeln nicht geändert.

## Manuelle Chats mit mehr Platz

Der Rücksprung in die Übersicht steht jetzt in der SMARTcoach-Kopfzeile auf
Themenauswahl, manuellen und automatischen Gesprächen sowie in Annas Ansicht.
Die separate Navigationszeile entfällt. Bei begrenzter Breite wird der sichtbare
Text zu „← Übersicht“ verkürzt; der zugängliche Name bleibt „Zurück zur
Übersicht“. In D01–D03 entfallen der wiederholte Gesprächstitel und „Andere
Gespräche“. Die manuellen Nachrichten sind gezielt auf `1.08rem` mit `1.45`
Zeilenhöhe vergrössert. Der scrollbare Verlauf erhält die zusätzliche Höhe;
Schritt- und Medienaktionen bleiben erhalten. Der App-Shell-Cache wurde wegen
der geänderten Kopfzeile und Chatansicht auf `v0.5.9` erhöht.

Zwölf gezielte Chromium-Prüfungen bestanden: alle drei manuellen Gespräche,
Kopfzeilen-Navigation und Bezeichnungen bei 1280×800 und 800×1280, grössere
Nachrichtenschrift, scrollbar langer Verlauf, Video-/Röntgenaktionen,
automatische Dialoge A–D samt WAV-Fallback und Abbruch, WAV-Wiederherstellung
offline, Einstellungen, D5 und Service-Worker-Offline-Neustart. Zusätzlich waren
Ernsts und Annas Dashboards in Quer- und Hochformat im pixelweisen Vergleich mit
dem unveränderten `main` **4 von 4 pixelgleich**. Die vollständige Testsuite
wurde nicht erneut ausgeführt.

Screenshot: [Manuelles Gespräch „Mein Röntgenbild“ bei 1280×800](screenshots/questions-xray-manual-expanded-landscape.png).
