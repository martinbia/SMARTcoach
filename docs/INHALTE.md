# Inhalte bearbeiten und lokale Videos verwenden

## Empfehlung: Markdown für Texte, stabile IDs für Beziehungen

Für diese Demo sind separate Markdown-Dateien sinnvoll: längere Erklärungen und
Fallgeschichten lassen sich direkt auf GitHub lesen und bearbeiten. Die Dateien
sind die Datenquelle der Anwendung, keine zusätzlich zu pflegenden Kopien von
JavaScript-Texten. `content.js` liest sie zur Laufzeit mit einem kleinen,
absichtlich begrenzten Parser. Es sind keine externen Bibliotheken nötig.

| Format | Geeignet für | Abwägung |
| --- | --- | --- |
| Markdown mit wenigen Metadaten | Berichte, Erklärungen und diese kleine Demo-Geschichte | Gut lesbar; die unten beschriebenen Überschriften und Feldnamen müssen erhalten bleiben |
| JSON | Grössere strukturierte Datensätze, maschinelle Validierung, viele Beziehungen | Standardformat und technisch robuster skalierbar; längere Texte und Anführungszeichen sind weniger bequem zu bearbeiten |
| YAML mit Markdown | Umfangreichere redaktionelle Metadaten | Gut lesbar, benötigt aber einen verlässlichen YAML-Parser und weitere Formatregeln |

Bei stark wachsender Zahl an Fällen empfiehlt sich JSON für Metadaten und
Beziehungen plus Markdown für die Texte. Für den aktuellen Umfang bleibt eine
gemeinsame, lesbare Markdown-Quelle einfacher. Ein CMS oder Backend ist dafür
nicht erforderlich.

## Welche Datei ändern?

- `content/berichte.md`: acht fiktive Dokumente E01–E08 mit fünf Textebenen.
- `content/genesungsweg.md`: die 14 Ereignisse J00–J13 sowie Einträge L01–Q02.
  Ereignisdatum, Titel und Beschreibung werden vom grafischen Pfad übernommen.
- `content/videos.md`: die sieben lokalen Film-Themen, Dateinamen und Rollen.
- `content/dialoge.md`: drei Interview-Gespräche D01–D03 mit nummerierten
  Beiträgen und dem jeweiligen Abschlussziel. Diese Datei steuert die Anzeige
  und ist die Quelle für die optionale lokale Sprachausgabe.
- `content/ansprache-dialoge.md`: vier vorbereitete Gesprächsabläufe A–D für
  die spätere Ansprache. Die Überschriften `## Dialog A – Titel` und
  `### A1 · SMARTcoach` beziehungsweise `### A2 · Patient` enthalten stabile
  Schlüssel. Den Zeilentext darunter darf die Redaktion ändern. Reihenfolge und
  Buchstaben-/Nummern-IDs müssen erhalten bleiben; D5 ist zwingend gesperrt.
  Die dazugehörigen WAV-Kopien liegen getrennt in der lokalen IndexedDB des
  Tablets und sind nicht Teil dieser Datei oder des GitHub-Repositories.

Nur fiktive Inhalte eintragen: Diese Dateien werden über GitHub Pages öffentlich
ausgeliefert. Die Anzeige einer eigenen Sorge nur in Annas Ansicht ist eine
Demo-Konvention und keine Zugriffssperre auf die Inhaltsdateien.

## Das unterstützte Format

Jeder Datensatz beginnt mit einer stabilen ID und einem lesbaren Titel:

```markdown
## E02 | Operationsbericht

Journey: J02

### Im Dokument steht

Hier steht der fiktive Berichtstext.

### Einfach erklärt

Hier steht die Erklärung in Alltagssprache.

### Für Ernst

Hier steht der Bezug für Ernst.

### Für Anna

Hier steht der Bezug für Anna.

### Frage für den Termin

Hier steht eine mögliche Frage.
```

Texte können Absätze, einfache Listen mit `- ` und **Fettdruck** mit `**` verwenden.
HTML, Links und eingebettete Bilder werden nicht ausgeführt. Die Datensatz-ID,
Metadaten-Schlüssel und die Namen der `###`-Abschnitte bitte nicht umbenennen.
Vorhandene Absätze und Titel können frei redaktionell überarbeitet werden.

### Ereignisse und Einträge konsistent halten

Bei einem J-Ereignis sind `Datum` (JJJJ-MM-TT), `Kategorie`, `Symbol`, `Übersicht`
(`ja` oder `nein`), `Quelle` und der Abschnitt `Beschreibung` hinterlegt. Die
Ereignisse müssen in zeitlicher Reihenfolge stehen. J00–J13 bleiben als stabile
Anker erhalten; die kompakte Dashboard-Auswahl verwendet diese bekannten IDs.
`Berichte` kann mehrere vorhandene E-IDs mit Komma trennen.

Ein Beispiel-Eintrag verwendet `Journey: J06`, `Person: Ernst`, `Typ: Aktivität`
und `Privat: nein` sowie `### Eintrag` und `### Einordnung`. Sein Datum stammt
direkt von J06 und wird nicht nochmals separat gepflegt. Zusätzliche L- oder
Q-Einträge können auf vorhandene Ereignisse verweisen. Sie erscheinen bei der
betreffenden Person und am zugehörigen Ereignis, ohne ein neues medizinisches
Ereignis oder einen Heilungsfortschritt zu behaupten.

In Texten und Quellen kann ein Datum über `{{J10.Datum}}` eingesetzt werden.
So beziehen sich Bericht E07, Termin-Karte und Pfad auf dasselbe Datum. Auch das
Demo-Heute stammt aus J09. Eigene Datumsangaben im Bericht sind nur nötig, wenn
das Dokument an einem anderen Tag entstanden ist, wie beim Pflegebericht E05.
Beim Ändern von Daten auch den fachlichen und erzählerischen Zusammenhang prüfen.

Fehlende Pflichtfelder, ungültige Daten, doppelte IDs und fehlende Bezüge werden
als Inhaltsfehler angezeigt. Es werden keine stillen medizinischen Ersatzdaten
erfunden. Unter Einstellungen kann das Laden erneut ausgelöst werden.

## Was passiert nach einer Änderung?

1. Gewünschte Markdown-Datei auf GitHub bearbeiten und Änderungen prüfen lassen.
2. Nach dem Merge veröffentlicht der vorhandene Pages-Workflow die statischen
   Dateien. Es gibt keinen Compiler und keinen JavaScript-Build für Textänderungen.
3. In der PWA **Einstellungen → Inhalte neu laden** wählen oder die Seite neu
   laden. Eine App-Neuinstallation ist nicht nötig.
4. Ohne Verbindung bleiben die zuletzt gecachten Inhalte verfügbar. Neue Texte
   können erst mit Verbindung zur veröffentlichten Seite geladen werden.

Eine Änderung einer beliebigen `.md`-Datei im Tablet-Dateisystem ändert die App
nicht automatisch. Diese Umsetzung lädt die veröffentlichten Repository-Dateien.

## Lokale Filme auf dem Tablet

Unter **Einstellungen → Lokale Übungsvideos** mehrere MP4-Dateien ausdrücklich
auswählen. Übungen/Anleitungen und die Playeransicht enthalten keine Dateiauswahl.
Der Browser
erhält durch die Fotoauswahl keinen automatischen Zugriff auf den restlichen
Ordner. Es gibt keinen Netzwerk-Upload und keine GitHub-URL für einen Film.
Der Katalog ordnet die Dateien nach normalisierten Namen zu; Leerzeichen,
Unterstriche, Bindestriche, Grossschreibung, Unicode-Umlaute und Download-Zusätze
wie `(1)` werden toleriert. Bei einer echten Umbenennung kann die Zeile `Datei:`
in `content/videos.md` angepasst werden. Alternativ in den Einstellungen
**Einzelne Filme zuordnen oder ersetzen** öffnen: diese direkte Zuordnung
akzeptiert jeden MP4-Dateinamen. Titel und Inhalt selbst vergleichen.
Der im ursprünglichen Wadenheber-Dateinamen enthaltene Text „beien“ bleibt als
Dateizuordnung erhalten, der sichtbare Titel ist davon unabhängig.

- Ernst sieht alle sieben Übungs- und Mobilitätsthemen.
- Anna sieht Gehen mit Teilbelastung sowie die beiden Treppen-Themen zum
  Verständnis und zur Vorbereitung von Fragen zur Unterstützung.
- Die Zuordnung basiert ausschliesslich auf den genannten Dateinamen. Die Filme
  wurden hier nicht fachlich gesichtet und sind keine individuelle Freigabe.
- Die lokale Kopie liegt in IndexedDB; Website-Speicher kann begrenzt oder vom
  Betriebssystem entfernt werden. Jede ausgewählte Datei wird vollständig gelesen
  und als unabhängiger Blob gespeichert. Ein generischer Android-MIME-Typ ist
  kein Ablehnungsgrund. Pro Film sind höchstens 512 MB vorgesehen.
- Scheitert die Speicherung, bleibt der Film für die laufende Sitzung verfügbar.
  Dies wird ausdrücklich angezeigt; nach einem Neustart erneut auswählen.
  Alte File-basierte Kopien werden beim Lesen migriert, soweit noch lesbar.
  Andernfalls kann die Datei in den Einstellungen neu ausgewählt werden.
- Wird ein Film während eines Imports geöffnet, wird der Player nach Abschluss
  automatisch bereitgestellt. Auch Navigation während der direkten Auswahl ist
  abgedeckt. Die Dateiauswahl in den Einstellungen startet keine Wiedergabe.
- **Video ansehen** öffnet und startet den Film direkt. Der Player füllt die Fläche
  unter der Kopfzeile; Quer- und Hochformat sowie grosse Schrift werden berücksichtigt.
  Es wird kein Systemvollbild erzwungen, damit Beenden und Navigation sichtbar bleiben.
  Bei blockiertem Start bleiben native Wiedergabetaste und **Video erneut starten**
  verfügbar. Letzteres beginnt den Film von vorne. Die weiteren Funktionen und
  **Dateiname und Zuordnung** befinden sich unterhalb des Videos.
- Navigation, Personenwechsel und Beenden
  pausieren den Player und setzen die Wiedergabe zurück. Fehlende Dateien und
  nicht unterstützte Codecs werden erklärt, statt einen leeren defekten Player
  stehenzulassen. Die MIME-Normalisierung wandelt keine Codecs um; für den Fall
  eines Codecfehlers wird eine MP4-Version mit H.264/AAC empfohlen.
- Entfernen einer lokalen Kopie und Interview-Reset löschen keine Originalfilme.
  Der Interview-Reset behält lokale Videos und die redaktionellen Beispiele bei.

Die echte Wiedergabe der sieben Originalfilme, Speichergrenzen und Android-
Dateiauswahl müssen am Tablet geprüft werden. Die Browserprüfung verwendet
einen kleinen synthetischen MP4-Testfilm, keinen der privaten Originalfilme.

## Gesprächsabläufe bearbeiten

`content/dialoge.md` wird wie die anderen redaktionellen Dateien direkt geladen
und offline gecacht. Kein Compiler und keine Textkopien im JavaScript.

```markdown
## D02 | Meine aktuelle Übung

Person: Ernst
Kurztext: Das lokale Wadenheber-Video zeigen.
Aktion: video-V07
Aktionslabel: Wadenheben-Video abspielen

### 01 Ernst

Welche Übung ist jetzt dran?

### 02 Coach

Wir zeigen die Beispielübung Wadenheben mit Festhalten.
```

Die `D`-ID bleibt stabil. Die Abschnitte werden ab `01` lückenlos nummeriert;
der Sprecher heisst jeweils `Ernst` oder `Coach`. Mindestens zwei Beiträge sind
nötig, der erste stammt von Ernst. Die Texte dürfen Absätze und Fettdruck
enthalten. Sie werden als Text gerendert, nicht als HTML ausgeführt. Die Labels
für Weiter/Zurück sind allgemeine Interview-Steuerelemente der Anwendung.

`Aktion` darf `home`, `xray` oder ein vorhandenes, für Ernst sichtbares Video wie
`video-V07` sein. `Aktionslabel` beschriftet den Abschlussbutton. Er erscheint
nach dem letzten Beitrag. Ein aus dem Gespräch gestartetes Video führt nach
seinem Ende ins Hauptmenü zurück. Es gibt keine automatischen Gesprächsschritte
und keine freie Eingabe. Fehlerhafte Reihenfolgen, Sprecher und Medienziele
werden beim Laden als Inhaltsfehler angezeigt.

D01 ist ausdrücklich eine **separate fiktive Vorausschau auf Januar 2027**.
Änderungen dort buchen keinen Termin und ändern weder J10 noch den Pfad. Bei
anderen Daten auch Wochentag, Uhrzeit und Geburtstagsvergleich im Text gemeinsam
anpassen. D02 ist keine neue Übungsverordnung. D03 behauptet keine echte Suche
oder Befundung in EPIC. In den öffentlich geladenen Texten keine lokalen privaten
Bilddateien, medizinischen Echtdaten oder externen Medien-URLs hinterlegen.

Das Röntgen-Demo-Bild wird ausschliesslich in den Einstellungen des Tablets
gewählt (JPG/PNG/WebP bis 12 MB). Der Name wird angezeigt, die Bytes werden als
unabhängige lokale Kopie in `smartcoach-demo-xray` gespeichert. Der Interview-Reset
behält das Bild bei. Es gibt keine Kopplung an den Speicher des Luzern-Fotos.

Die manuelle Chatoberfläche zeigt die Beiträge dieser Markdown-Datei als Text
und steuert sie schrittweise über Vorheriger und Nächster Schritt. Eine
manuelle Voice-Demo wird nicht angeboten. Die separaten automatischen Dialoge
A–D verwenden weiterhin die dafür lokal konfigurierten WAV-Dateien.
