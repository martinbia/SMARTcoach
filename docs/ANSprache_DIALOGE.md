# Einstellungen für vorbereitete Dialoge und lokale WAV-Dateien

## Dialogkatalog

`content/ansprache-dialoge.md` ist die redaktionelle Quelle für Dialog A
(Ernährung), B (Spaziergang), C (Übungen) und D (Befinden und Schmerzen).
`content.js` lädt und validiert die stabilen Dialog- und Zeilen-IDs und gibt
für jede Zeile Sprecher, Anzeigetext und Freigabestatus zurück. Änderungen am
Text benötigen keinen Build. Alle 13 Dialogzeilen A1–D5 sind aktuell freigegeben
und können mit WAV-Dateien belegt, probegehört, ersetzt und entfernt werden.
Die ursprünglichen Interview-Demos D01–D03 in
`content/dialoge.md` bleiben davon getrennt.

Für eine neue Zeile wird die nächste fortlaufende ID unter dem bestehenden
Dialog ergänzt, zum Beispiel `### A4 · Patient`. Ein neuer Dialog verwendet einen
noch freien Grossbuchstaben, zum Beispiel `## Dialog E – Titel`, und startet bei
`### E1 · SMARTcoach`. Auswahl, Listenzeilen und Audio-IDs werden aus diesem
Katalog erzeugt; für eine Erweiterung ist keine Änderung der GUI-Logik nötig.
IDs müssen innerhalb des Katalogs eindeutig und je Dialog fortlaufend sein.

Der Freigabestatus wird je Zeile aus dem Katalogmarker `· GESPERRT` abgeleitet.
Gesperrte Zeilen bleiben ohne WAV-Steuerungen; freigegebene Zeilen erhalten die
gleichen Bedienmöglichkeiten. Es gibt keine fest codierte Sperre für einzelne
IDs. D5 ist mit einer überarbeiteten Textfassung freigegeben.

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
Standardwert 60 zurückgesetzt. Bei erfüllten Bedingungen steuert die Wartezeit
den Timer im Ruhebildschirm; Einzelheiten stehen im Abschnitt
„Timer und automatische Dialogführung“.

`local-prompt-audio.js` hält WAV-Kopien getrennt in der IndexedDB
`smartcoach-prompt-audio`, Object Store `files`. Der Schlüssel ist direkt die
Dialogzeilen-ID (z. B. `C3`), nicht ihre Position. Das Audio-Modul akzeptiert nur
freigegebene IDs aus einem erfolgreich validierten Dialogkatalog. Gesperrte Zeilen
bleiben allgemein ausgeschlossen. Jeder Datensatz enthält
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

## Timer und automatische Dialogführung

`smartcoach.preferences.v1` speichert den ausgewählten Dialog und die Wartezeit.
Ein Timer läuft nur im sichtbaren Ruhebildschirm, für Ernst mit eingeschalteter
Aktiver Begleitung, validiertem und vollständig freigegebenem Dialog sowie
lesbaren lokalen WAV-Dateien für jede Zeile. Vor dem Timerstart werden alle WAVs
vollständig gelesen und die RIFF/WAVE-Köpfe geprüft. Fehlt zum Beispiel `C3`,
erscheint die fehlende Zeilen-ID in den Einstellungen und es wird kein Timer
gestartet.

Jeder Aufenthalt beginnt mit einer neuen Wartezeit. Verlassen des Ruhebildschirms,
„Beenden“, Navigation, Hintergrundwechsel oder Schliessen der PWA stoppen den
Timer; eine spätere Rückkehr beginnt wieder bei null. Ein blosses Neurendern des
Ruhebildschirms, etwa nach Laden des Fotos, lässt den Timer weiterlaufen.
Der 2-Pixel-Fortschrittsstrich ist ein Overlay und belegt keinen zusätzlichen
Layoutplatz.

Der automatische Dialogmodus ist von den Interviewgesprächen D01–D03 getrennt.
Er durchläuft die freigegebenen Zeilen des gewählten A–D-Katalogs in Reihenfolge.
Coachzeilen erscheinen links und werden automatisch abgespielt; Patientenzeilen
erscheinen erst als Antwortbutton. Nach einem bewussten Tap wird die Antwort
rechts angezeigt, ihre WAV abgespielt und danach der nächste Katalogschritt
freigegeben. Dialogende bietet „Zur Übersicht“ und einen bewussten Neustart an.
Es gibt keine freie Texteingabe, KI, Spracherkennung oder automatische
Videowiedergabe aus C4.

## Wiedergabe auf Android

Probehören und automatische Dialogführung verwenden ein HTML-Audioelement mit
lokal erzeugten Blob-URLs; es kontaktiert weder TTS noch einen Server. Es läuft
jeweils höchstens eine WAV. Navigation, Personenwechsel, Sichtbarkeitswechsel,
„Beenden“ und PWA-Schliessen stoppen die Wiedergabe und verwerfen offene
Fortsetzungen. Android Chrome darf Autoplay blockieren: die Textzeile bleibt
sichtbar, **Ton abspielen** versucht es nach einem bewussten Tap erneut. Bei einem
Wiedergabefehler ist Wiederholen oder Fortfahren ohne Ton möglich. Automatischer
Hintergrundstart und Wiedergabe bei gesperrtem Bildschirm sind nicht vorgesehen.

Der Service Worker nimmt Katalog und Audio-Modul in die Offline-App-Shell auf.
Die ausgewählten WAV-Bytes liegen in der IndexedDB, die nicht Teil des
Service-Worker-Caches ist. Bereits lokal gespeicherte Dateien lassen sich so
nach dem Laden der App auch ohne Netzwerk probehören.

## Abgrenzung

Automatische Ansprache ist nur für Ernst und nur für die vorbereiteten Dialoge
A–D vorgesehen. Die Zustimmung wird nicht automatisch eingeschaltet. Es gibt
keine automatische Ansprache für Anna, keine KI, keine Spracherkennung, keine
automatische Videowiedergabe und keine freie Chat-Eingabe. Die drei D01–D03-
Interview-Gespräche bleiben unverändert und beginnen nur durch eine bewusste
Auswahl.
