# Einstellungen für vorbereitete Dialoge und lokale WAV-Dateien

## Dialogkatalog

`content/ansprache-dialoge.md` ist die redaktionelle Quelle für Dialog A
(Ernährung), B (Spaziergang), C (Übungen) und D (Befinden und Schmerzen).
`content.js` lädt und validiert die stabilen Dialog- und Zeilen-IDs und gibt
für jede Zeile Sprecher, Anzeigetext und Freigabestatus zurück. Änderungen am
Text benötigen keinen Build. Die ursprünglichen Interview-Demos D01–D03 in
`content/dialoge.md` bleiben davon getrennt.

Für eine neue Zeile wird die nächste fortlaufende ID unter dem bestehenden
Dialog ergänzt, zum Beispiel `### A4 · Patient`. Ein neuer Dialog verwendet einen
noch freien Grossbuchstaben, zum Beispiel `## Dialog E – Titel`, und startet bei
`### E1 · SMARTcoach`. Auswahl, Listenzeilen und Audio-IDs werden aus diesem
Katalog erzeugt; für eine Erweiterung ist keine Änderung der GUI-Logik nötig.
IDs müssen innerhalb des Katalogs eindeutig und je Dialog fortlaufend sein.

Der gesperrte Schritt D5 bleibt als Platzhalter-ID im Katalog enthalten. Seine
Zeile wird mit Hinweis angezeigt; die Einstellungsoberfläche erzeugt dafür
weder einen Dateiauswahldialog noch eine Probehör-Schaltfläche. Dialog D ist
sichtbar als unvollständig freigegeben markiert. Ein späteres Ersetzen/Freigeben
von D5 benötigt eine fachlich geprüfte Textfassung und einen separaten Auftrag.

## Einstellungen und Daten

`smartcoach.preferences.v1` enthält zwei einfache Einstellungswerte:

```json
{
  "proactiveDialogue": "C",
  "waitSeconds": 60
}
```

`proactiveDialogue` nimmt `none`, `A`, `B`, `C` oder `D` an. `waitSeconds` ist
eine ganze Zahl von 5 bis 3600; ungültige gespeicherte Werte werden auf den
Standardwert 60 zurückgesetzt. Die Wartezeit ist derzeit nur eine gespeicherte
Konfiguration und wird von keiner Timerlogik gelesen.

`local-prompt-audio.js` hält WAV-Kopien getrennt in der IndexedDB
`smartcoach-prompt-audio`, Object Store `files`. Der Schlüssel ist direkt die
Dialogzeilen-ID (z. B. `C3`), nicht ihre Position. Das Audio-Modul erhält seine
Liste gesperrter Schritte aus dem geladenen Dialogkatalog. Jeder Datensatz enthält
`{ blob, name }`. Bytes liegen nie im `localStorage` oder Git. Es gibt keinen
Ordnerzugriff ohne Auswahl und keinen Upload. WAV-Dateien werden einzeln anhand
ihres `.wav`-Namens gelesen, auf einen RIFF/WAVE-Header geprüft und auf 64 MB
begrenzt. Generische Android-MIME-Typen werden akzeptiert.

Die Settings-Oberfläche kombiniert redaktionelle Daten (`id`, `speaker`, `text`,
`locked`/`approved`) zur Laufzeit mit dem Status der lokalen Datei. Der Speicher-
status unterscheidet `Nicht zugeordnet`, `Gespeichert` und `Nur für diese Sitzung`.
Entfernen löscht nur die PWA-Kopie. Eine gescheiterte IndexedDB-Schreiboperation
wird nie als dauerhaft gespeichert dargestellt.

### WAV-Dateiauswahl unter Android

Der Datei-Input für WAV-Zuordnungen hat absichtlich kein `accept`- und kein
`capture`-Attribut. Ein MIME-Filter kann Android dazu bringen, passende
Aufnahme-/Medien-Apps anzubieten statt einen allgemeinen Dateipicker. Die
Schaltfläche öffnet weiterhin den nativen Picker über eine direkte
Benutzeraktion. Dort kann der Benutzer selbst zu `Interner Speicher/Documents/SMART`
navigieren; die Web-App kann weder den Systemdialog erzwingen noch diesen Ordner
ohne Auswahl öffnen.

Nach der Auswahl prüft die App weiterhin die Endung `.wav`, eine Grenze von
64 MB, die vollständige Lesbarkeit beim Einlesen und den RIFF/WAVE-Kopf. Beliebige
Dateien, die der unbeschränkte Picker zeigt, werden nicht ungeprüft gespeichert.

## Vorgesehene spätere Schnittstelle

Ein späterer Controller kann `SMART_CONTENT.promptDialogues` als Dialogkatalog
und `SMART_PROMPT_AUDIO.get(stepId)` als lokale Datei-Schnittstelle verwenden.
Der ausgewählte Dialog und die gespeicherte Wartezeit liegen unter
`smartcoach.preferences.v1`. Die Dateikopie lässt sich mit `keys()`, `get(id)`
und `remove(id)` abfragen oder verwalten. Das aktuelle Einstellungsmodul bietet
keine Timer- oder Chatsteuerung und startet keine Audiodatei ausserhalb einer
bewussten Probehör-Aktion.

## Wiedergabe auf Android

Probehören verwendet ein HTML-Audioelement mit einer lokal erzeugten Blob-URL;
es kontaktiert weder TTS noch einen Server. Die App spielt jeweils nur eine
Datei, und Navigation, Sichtbarkeitswechsel sowie **Beenden** stoppen die
Wiedergabe. Android Chrome und dessen Decoder müssen den konkreten WAV-Codec
unterstützen. Eine erfolgreiche Dateiauswahl garantiert keine Wiedergabe; bei
einem Decoder- oder Autoplay-Fehler erscheint eine verständliche Meldung. Ein
bewusster Tap startet die Probe. Automatischer Start, Hintergrundwiedergabe,
Wiedergabe bei gesperrtem Bildschirm und Verhalten mit jeder Android-Version
sind nicht zugesichert und müssen am Tablet geprüft werden.

Der Service Worker nimmt Katalog und Audio-Modul in die Offline-App-Shell auf.
Die ausgewählten WAV-Bytes liegen in der IndexedDB, die nicht Teil des
Service-Worker-Caches ist. Bereits lokal gespeicherte Dateien lassen sich so
nach dem Laden der App auch ohne Netzwerk probehören.

## Abgrenzung

Es gibt keinen automatischen Timerstart auf dem Ruhebildschirm, keinen Wechsel
zum Chat, keine automatische WAV- oder Videowiedergabe, keine Antwortbuttons,
keine automatische Reaktion auf „Aktive Begleitung EIN“, keine KI und keine
Spracherkennung. Das bestehende Chatverhalten und die drei D01–D03-Interview-
Gespräche bleiben unverändert.
