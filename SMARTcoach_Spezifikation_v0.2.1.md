# SMARTcoach - Funktionale Spezifikation und Bedienkonzept v0.2.1

**Stand:** 06.11.2026  
**Status:** Konzeptentwurf / Diskussionsgrundlage; kein Implementierungsnachweis  
**Produkt:** Klickbares PWA-Mock-up auf Android-Tablets, gehostet via GitHub Pages  
**Grundlage:** Anforderungen aus dem SMARTcoach-Projekt, zwei Personas, drei Versorgungspfad-Versionen und ein Beobachtungsprotokoll aus einem Workshop.

## 0. Entscheidungslogik

- **FESTGELEGT (F):** Vom Auftraggeber formulierte Anforderungen / Rahmenbedingungen.
- **VORSCHLAG (V):** Abgeleitete Gestaltungs- oder Umsetzungsentscheidung; erst nach Diskussion freigeben.
- **OFFEN (O):** Zu testen oder zu entscheiden.
- **DEMO:** Durch fiktive Szenarien dargestellt, aber nicht real angebunden oder medizinisch validiert.
- **IMPLEMENTIERT:** In dieser Fassung **nichts als implementiert bestätigt**. Das GitHub-Repository entscheidet über den realen Stand.

**Wesentliche Aenderung von v0.1:** Der gemeinsame, informationsorientierte Journey-Startbildschirm ersetzt den Vorschlag zweier grosser Eingangskacheln. Die grafische Journey ist zentral; Patient und Angehörige teilen sich die Geschichte, mit einer einfach umschaltbaren Perspektive. Dies ist ein **UX-Vorschlag**, noch nicht beschlossen.

**Ergaenzung v0.2.1:** Im HOME ist die Option **`Aktive Begleitung`** gut sichtbar. Der Nutzer erkennt vor dem Einschalten, dass SMARTcoach von sich aus nachfragen, an im Therapieplan dokumentierte Übungen erinnern und Aktivitäten vorschlagen darf. Ein-/Aus-Zustand wird unmittelbar angezeigt. Die sichtbare Steuerung gehoert zum Grundgeruest; automatisch ausgeloeste Dialoge kommen spaeter. **Bezeichnung und Platzierung sind UX-Vorschlaege**, die ausdruecklich gewuenschte Funktion ist festgelegt.

## 1. Forschungsziel und Nutzenversprechen

### Ziel des Mock-ups (F)

Ein realistisch klickbares und gut bedienbares Demonstrationssystem für qualitative Interviews. Befragte können konkrete Aufgaben ausprobieren und beurteilen, welche Teile ihnen zu Hause nach einer hüftnahen Fraktur helfen würden.

### Kernnutzen der hypothetischen späteren Anwendung (F)

**Besser informiert und sicherer orientiert:** Zusammenhängende Erklärungen statt verstreuter Spitalberichte, schriftlicher Therapieblätter und muendlicher Informationen. SMARTcoach beantwortet anhand der bekannten Krankheits- und Therapiegeschichte die vier Leitfragen:

1. **Was ist passiert?** Sturz, Diagnose, Operation, Behandlung in leicht verständlicher Sprache.
2. **Wo stehen wir heute?** Bisheriger Verlauf, dokumentierte Taetigkeiten, offene Fragen, subjektives Befinden.
3. **Was steht als Nächstes an?** Individuell dokumentierte Übungen, Termine, Hilfsmittel und Ziele - keine neuen Verordnungen.
4. **Warum und woher weiss SMARTcoach das?** Kennzeichnung und Aufruf des zugrunde liegenden Demo-Dokuments, Datum und Rolle der Quelle.

Zweiter Nutzen: Selbstbestimmung, hilfreiche Unterstützung durch Angehörige, Motivation und vorbereitete Gespräche mit Fachpersonen. SMARTcoach ersetzt keine Fachperson und stellt keine Diagnosen.

### Erkenntnisse aus den bereitgestellten Unterlagen

- `Persona2_Edgar.pdf`, Seite 1: Selbstbestimmung und Ablehnung von Bevormundung, Alleinleben, Spitex, Besorgnis über Autonomieverlust.
- `Persona1_Hildegard.pdf`, Seite 1: Soziales Leben, Familie, Rollen des Ehepaars, Sturzangst, Angst vor Verlust der Selbstständigkeit.
- `260527_sa_gra_pflege_versorgungspfad_a3_druck.pdf`, Seiten 3-5: Unterschiedliche Übergaenge von Spital nach Hause, Entlassinformationen, Familienhilfe, Therapieunterbrechungen und die Wiederaufnahme von Aktivitäten.
- `260526_sa_gra_pflege_versorgungspfad_a3eladef (002)_voa.pdf`, Seiten 3-5: Bearbeitete Workshop-Version mit aehnlichen Faellen und Korrekturanmerkungen; nicht als separate Stichprobe zaehlen.
- `260519_sa_gra_pflege_versorgungspfad_a0_v1_voa.pdf`, Seite 1: Fruehe Gestaltungsfassung des Versorgungspfades, keine zusaetzlichen Interviewresultate.
- `Beobachtungsprotokoll_Angehoerige.pdf`, Seiten 1-4: Qualitative Beobachtungen zur Beziehung, sozialen Sicherheit, professionellen Betreuung und Kommunikation; ausdrücklich **vertraulich**. Keine Originaldaten aus diesem Dokument in ein öffentliches Repository übernehmen.

**Methodische Grenze:** Die Unterlagen sind qualitative Personas, Workshop-Artefakte und Beobachtungen. Sie belegen nicht die Wirksamkeit von SMARTcoach und sind keine statistisch repraesentative Bedarfserhebung. Die folgenden Designentscheidungen sind Hypothesen für Interviews.

## 2. Zielgruppen und Nutzungskontext

- **Patienten:** Aeltere Erwachsene nach hüftnaher Fraktur, teilweise mit Hilfsmitteln, Erinnerungsluecken zu Spitalinformationen, sehr unterschiedlichem Bedarf an Hilfe.
- **Angehörige:** Lebenspartnerinnen/-partner, erwachsene Kinder oder andere unterstützende Personen; benoetigen praktische Hilfe, Hintergrundwissen und Raum für eigene Sorgen.
- **Interviewende:** Begleiten den Demo-Ablauf, waehlen ein fiktives Szenario, setzen Demo-Daten zurück.
- **Einsatzumgebung:** Tablet zu Hause bzw. in der Interviewsituation, Hoch- und Querformat, Touch, ggf. Sprache und lokale Medien.

**UX-Prinzipien (F/V):** Nicht bevormundend, einfache und kurze Saetze, keine Altersstereotype, grosse Touch-Ziele, hohe Kontraste, klare Lesereihenfolge, wenige Aktionen pro Ansicht, ruhige serioese Gestaltung. Auch bei mutloser oder aengstlicher Stimmung keine bestrafenden Fortschrittsindikatoren.

## 3. Informationsarchitektur und Startkonzept

### 3.1 Vier Zustandsarten (F/V)

1. **SETUP (F):** Einmalige Einstellungen, Mediendateien aus `Documents/SMART` und Demo-Konfiguration. Die `Aktive Begleitung` ist zu Beginn **AUS** und kann vom HOME aus mit informierter Zustimmung eingeschaltet werden, ohne den Erststart zu blockieren. Gespeicherte Präferenzen bleiben beim Neustart vorhanden; Dateiberechtigungen separat prüfen.
2. **IDLE / Ruhebildschirm (F):** Optisch zurückhaltende Luzern-Motive oder andere lokale Bilder; kein Audio und keine Unterbrechung. Berührung öffnet HOME.
3. **HOME / SMARTcoach-Übersicht (V):** Gemeinsames Journey-Dashboard mit aktuell relevantem Kontext, Informations-Kurzkarte und einer begrenzten Anzahl Aktionskarten. Rollenauswahl als jederzeit erreichbarer Perspektivwechsel.
4. **DETAIL / Fachansichten (F/V):** Journey-Detail, Bericht/Erklärung, Chat, Übungsvideo, Tagebuch, Fragenliste, Angehörigenhilfe, Quiz, Einstellungen.

**Globale Regel (F):** `Beenden` aus jeder interaktiven Ansicht -> sofort alle Audio-/Videowiedergaben, proaktiven Dialoge und laufenden Aktionen stoppen -> IDLE. Im Ruhebildschirm erfolgt keine Ansprache. Erst nach erneuter Beruehrung und Oeffnen des HOME darf die zuvor aktivierte Begleitung wieder wirksam werden; der Ein-/Aus-Schalter bleibt gut sichtbar. `Beenden` loescht weder Einwilligung noch Tagebucheintraege, waehrend `Aktive Begleitung AUS` die Einwilligung ausdruecklich widerruft. `Zurück` navigiert in der Interaktion.

### 3.2 HOME: Inhaltliche Prioritaeten (V)

**Header:** SMARTcoach, lesbare Rollenumschaltung `Ernst` / `Anna` bzw. `Patient` / `Angehörige`, Einstellungen, immer sichtbarer grosser `Beenden`-Button.

**Zentrale Journey (grösster Inhaltsbereich):** Standardmässig Überblick über den gesamten Weg mit wenigen grossen Stationen. Geschwungener Pfad nach Vorbild der bereitgestellten Versorgungspfad-Grafiken, aber digital für Touch optimiert. Gegenwart deutlich markiert; Stationen anklickbar. Innerhalb der Journey die Bedienelemente `Gesamter Weg`, `Heute zentrieren`, `+`, `-`. Für Gestenunabhängigkeit müssen diese Buttons funktionieren, ohne dass Pinch-Zoom benoetigt wird.

**Kontextkarten um die Journey (max. 2-3 gleichzeitig):**

- **Heute wichtig:** Nächster dokumentierter Termin oder eine im fiktiven persönlichen Plan vorgesehene Übung; `Ansehen`.
- **Das bedeutet Ihr Bericht:** Kurze, erklärende Zusammenfassung eines tatsächlich im Demo-Datensatz enthaltenen Spital-/Physioberichts; `Einfach erklären`, `Quelle ansehen`.
- **Offene Fragen / Beobachtungen:** Zaehler oder kurzer Vorschautext; `Für den nächsten Termin`.

### 3.2a Sichtbarer Schalter `Aktive Begleitung` (F/V)

**FESTGELEGT:** Auf dem Dashboard muss klar zu erkennen und freiwillig waehlbar sein, ob SMARTcoach auch **selbst** ein Gespraech anstossen darf. Dies ist ausdruecklich etwas anderes als `SMARTcoach fragen`, bei dem nur die Person selbst den Dialog beginnt.

**VORSCHLAG fuer Platzierung:** Eine fest sichtbare, ausreichend grosse Zeile/Karte **direkt unter der Journey und vor den wechselnden Kontextkarten**. Im Querformat kann sie seitlich an der Journey stehen, sofern sie nicht im sichtbaren Bereich verschwindet. Sie zaehlt nicht zu den 2-3 inhaltlichen Kontextkarten.

**Beschriftung im ausgeschalteten Zustand:**

- Titel: `Aktive Begleitung`
- Status: `AUS` (nicht nur ein graues Symbol)
- Klartext: `SMARTcoach antwortet nur, wenn Sie ihn selbst ansprechen.`
- Aktion: `Einschalten`
- Vor erstmaligem Einschalten wird gut lesbar erklaert: `Wenn Sie das erlauben, darf SMARTcoach von sich aus nach Ihrem Befinden fragen, an vorgesehene Uebungen erinnern und passende Aktivitaeten vorschlagen.` Zustimmung ueber `Ja, aktive Begleitung einschalten`.

**Beschriftung im eingeschalteten Zustand:**

- Titel: `Aktive Begleitung`
- Status: `EIN`
- Klartext: `SMARTcoach darf gelegentlich nachfragen, an Uebungen erinnern und Aktivitaeten vorschlagen.`
- Aktion: `Ausschalten` (sofort wirksam, ohne weitere Bestaetigung)
- Optional fuer das Interview: `Beispielfrage zeigen` oeffnet einen **ausdruecklich simulierten** proaktiven Dialog, ohne einen echten Timer oder laufenden Hintergrunddienst vorzutäuschen.

**Verhalten:** Standardmaessig AUS; Zustand lokal speichern. Bei AUS keine proaktive Ansprache, auch nicht per MP3. Bei EIN nur innerhalb der sichtbar geoeffneten PWA und ausserhalb laufender Dialoge, nie im IDLE/Ruhebildschirm. Manuelles `Beenden` bricht alles sofort ab und verhindert Ansprache im IDLE. `Heute nicht mehr fragen` pausiert proaktive Impulse fuer die Demo-Sitzung, ohne die gespeicherte grundsaetzliche Einwilligung zu loeschen. Fuer anstehende Uebungen ausschliesslich Angaben aus dem fiktiven, individuell hinterlegten Plan verwenden. Die Funktionslogik ist eine **spaetere Demo-Phase**; der Schalter mitsamt verstaendlichen Zustaenden ist **P0**.

**Primare Aktionen:** `SMARTcoach fragen`, `Übungen`, `Tagebuch`. `Berichte & Erklärungen` muss gleichwertig gut erreichbar sein, entweder direkt als Aktion oder über die zentrale Informationskarte.

**Perspektive:** Beide Rollen sehen denselben zeitlichen Verlauf, aber rollenspezifische Hinweise (z. B. Patient: Übung; Angehörige: Unterstützung, eigene Belastung) und unterschiedliche Schnellaktionen. Kein separater Login, solange es nur fiktive Daten sind. Offen: Umgang mit privat erfassten Sorgen in einem späteren echten System.

### 3.3 Zwei Zoomstufen und selektiver Kontext (F/V)

- **Gesamtansicht (F):** Gesamte Patientengeschichte von `vor dem Sturz` bis `Ziele für später`; wenige grössere, gut lesbare Etappen statt unlesbarer Datumsdichte. Auch persönliche Vor-Sturz-Ziele zeigen.
- **Detailansicht (F):** Zeitfenster um das simulierte Heute von ca. `-14 / +14 Tagen`, mit übersichtlichen Detailmarkern und anschliessender horizontaler/vertikaler Navigation.
- **Zentrieren (F):** Unabhängig vom aktuellen Zoom geht es zurück auf das Demo-Heute mit dem Detailfenster.
- **Zeitleiste ≠ Heilungsgrad (V):** Position kennzeichnet Datum/Ereignis, nicht erreichten medizinischen Prozentwert. Zukunftsmarkierungen sind als `Termin` oder `Persönliches Ziel` gekennzeichnet, nicht als Heilungsversprechen.
- **Ereignisse (V):** Kategorien `Spital`, `Behandlung`, `Therapie`, `Zu Hause`, `Aktivität`, `Sorge/Frage`, `Termin`, `Ziel`. Immer Symbol UND Text statt reiner Farbsemantik.

### 3.4 Navigation (V)

```text
PWA-Start -> SETUP (nur bei Bedarf) -> IDLE
IDLE --Bildschirm berühren--> HOME (Journey-Dashboard)
HOME --Meilenstein antippen--> JOURNEY_DETAIL -> INFO_QUELLE / CHAT_KONTEXT
HOME --Bericht-Karte--> INFO_UEBERSICHT -> INFO_ERKLAERUNG -> INFO_QUELLE
HOME --Frage stellen--> CHAT (mit vorbereiteten Antwort-Buttons, MP3 optional)
HOME --Übung--> MEDIA -> LOGBUCH
HOME --Tagebuch--> LOGBUCH -> JOURNEY-EINTRAG
HOME --Rollenwechsel--> HOME mit anderer Perspektive
HOME --Aktive Begleitung: Einschalten--> PRO_OPTIN -> PRO_ON -> HOME
HOME --Aktive Begleitung: Ausschalten--> PRO_OFF -> HOME
HOME --Beispielfrage zeigen (nur wenn EIN)--> PRO_CHECK (Demo)
HOME --Mehr--> ANGEHOERIGE_HILFE / QUIZ / TERMINVORBEREITUNG
JEDER AKTIVE SCREEN --Beenden--> IDLE (Medien und Proaktivität gestoppt)
```

Auf dem **Tablet im Querformat** Journey zentral, flankiert von 1-2 schmalen Kontextkarten; im **Hochformat** Header, kurze Statuszeile, Journey über volle Breite, danach vertikal gestapelte Karten. Keine Verkleinerung der Karte auf unlesbare Miniaturschrift.

## 4. Funktionsanforderungen und Prioritaet

`P0` = für das erste klickbare Grundgerüst; `P1` = zentrale Demo nach Grundgerüst; `P2` = späterer Funktionsausbau. Prioritaetszuordnung ist **Vorschlag**, noch kein Auftrag an Codex.

| ID | Anforderung | Status | Prio |
|---|---|---|---|
| F01 | Ruhiger, lokaler und touch-aktivierbarer Ruhebildschirm. | F | P0 |
| F02 | Globaler `Beenden`-Button beendet Interaktion, MP3 und Video sofort und kehrt in Ruhemodus zurück. | F | P0 |
| F03 | Journey als zentrales Element des HOME-Dashboards. | V (neu) | P0 |
| F04 | Zwei Perspektiven Patient/Angehörige auf derselben Geschichte; einfache Umschaltung. | V (neu) | P0 |
| F05 | Journey-Gesamtansicht, Detailfenster `+/-14 Tage`, `Heute zentrieren`, Marker anklicken. | F, Details V | P0/P1 |
| F06 | Erklärung `Was ist passiert? / Wo stehe ich? / Was kommt als Nächstes?` anhand fiktiver Spital- und Therapiedaten. | F (Kernnutzen), V (Ablauf) | P1 |
| F07 | Zu jeder medizinisch bezogenen Erklärung eine erkennbare Dokumentquelle, Datum, einfache Sprache, Rückfrage. | V (neu) | P1 |
| F08 | Quellenbezogener Chat mit vorbereitetem Text, MP3s und Antwortbuttons; Texteingabe optional. | F | P1 |
| F09 | Lokale MP3-/Videodateien aus `Documents/SMART`; responsives Abspielen, kein Weiterlaufen nach Verlassen. | F | P1 |
| F10 | Patient: Anleitungen, Alltagssituationen und Videos nur passend zum fiktiven individuellen Therapieplan. | F | P1 |
| F11 | Angehörige: Erklärungen zu Unterstützung und Balance zwischen zu viel/zu wenig Hilfe. | F | P1 |
| F12 | Therapietagebuch: Aktivität, Schmerz, Stimmung, Sorgen, subjektive Sicherheit und offene Fragen erfassen. | F | P1 |
| F13 | Logbucheintrag erzeugt Journey-Marker; bestätigte Erfassung, ohne automatischen medizinischen Heilungsgrad. | F/V | P1 |
| F14 | Vorbereitete Zusammenfassung für Physio-/Arzttermin, mit Nutzerkontrolle über private Angehörigenangaben. | F/V | P2 |
| F15 | Kurzes Angehörigenquiz und Feedback ohne Schuldzuweisung. | F | P2 |
| F16a | Im Dashboard deutlich sichtbare `Aktive Begleitung` mit Status EIN/AUS, kurzer Folgenbeschreibung, Opt-in und lokaler Speicherung. | F (Funktion), V (Benennung/Platzierung) | P0 |
| F16b | Nach Einwilligung situativ proaktiv nachfragen, an planmaessige Uebungen erinnern und Aktivitaeten vorschlagen; nie im IDLE. | F/V | P2 |
| F17 | Speicherung von Einstellungen, Demo-Zustand und auf Wunsch fiktiven Tagebucheintraegen zwischen Neustarts. | F/V | P0/P1 |
| F18 | Interviewmodus: Demo-Datum, Beispielperson, Szenario und Logbuch zurücksetzen, ohne Medieneinstellungen zu loeschen. | V | P0 |
| F19 | Eingabefeld mit Android-Tastatur-Diktat testbar; keine freie KI-Antwort suggerieren. | O | P2 |
| F20 | Optionales simuliertes Wetter für situationsbezogene Vorschlaege; keine Live-Abhaengigkeit. | F/V | P2 |
| F21 | Medizinische Unsicherheit: individuelle Vorgaben sichtbar lassen, unklare oder akute Anliegen nicht automatisch diagnostizieren. | V (Sicherheitsanforderung) | P1 |

## 5. Bildschirme

| Bildschirm | Zweck | Wichtigste Elemente | Übergang |
|---|---|---|---|
| IDLE | Ansprechbar, aber nicht stoerend | Luzern-Bild(er), Hinweis `Berühren` | HOME |
| HOME | Orientierung, Fortschritt, Information und Steuerung der proaktiven Ansprache | Journey, Heute-Information, `Aktive Begleitung` EIN/AUS, nächste Aktivität, Rolle, Stopp | Detail/Chat/Übung/Tagebuch/PRO_OPTIN |
| JOURNEY_DETAIL | Weg verstehen, Ereignis oeffnen | +/- 14 Tage, Gesamter Weg, Heute, Marker | Ereignisdetails |
| EREIGNIS | Bedeutung eines Ereignisses | Was geschah, was bedeutet es, Datum, Datenherkunft | Quellenansicht/Chat |
| INFO_UEBERSICHT | Personalisierte Unterlagen | Was passiert ist, aktuelle Empfehlungen, nächste Schritte | Erklärung |
| INFO_ERKLAERUNG | Einfach erklären und fragen | Originalbegriff, einfaches Deutsch, Bedeutung für den eigenen Fall, Quellenbutton | Chat/Quelle/Frage |
| CHAT | Demonstrierter Dialog | Text, MP3 optional, 2-4 grosse Auswahlantworten, Freitext optional | Abhaengig von Auswahl |
| UEBUNG/MEDIA | Passende Demonstrationsmedien | Video/Audio, Pause, Titel, Zurück | Logbuch/Home |
| LOGBUCH | Eigene Beobachtungen erfassen | Kurze Auswahl, bestätigen, Einträge anzeigen | HOME/Journey |
| ANGEHOERIGE | Hilfe und Entlastung | Alltagshilfe, Sorgen, Quiz, eigene Fragen | Info/Chat/Quiz |
| FRAGENLISTE | Nächsten Physiotermin vorbereiten | Fragen nach Quelle / Rolle, manuell selektieren | HOME/Export-Simulation |
| EINSTELLUNGEN | Vorlieben und Demo | Audio, ergänzende Einstellungen zur aktiven Begleitung, lokale Medien, Textgrösse, Demo-Reset | HOME/IDLE |

## 6. Kontextualisierte Informationen statt blosser PDF-Anzeige

**Kernablauf A (F/V):**

1. Nutzer tippt auf einem Journey-Marker `Operation` oder auf `Was steht im Bericht?`.
2. SMARTcoach zeigt eine einfache Zusammenfassung des simulierten Berichts.
3. Erklärungsansicht unterscheidet `Im Dokument steht`, `Einfach erklärt`, `Was bedeutet es für uns?` und `Das möchten wir beim Termin fragen`.
4. `Quelle ansehen` zeigt Dokumenttitel und Datum, ggf. simulierten Auszug; **keine** behauptete Live-EPIC-Verbindung.
5. Antwortbuttons leiten zu weiteren Erklärungen oder speichern eine Frage in der Terminliste.

**Kernablauf B (F/V):** Eine Person sieht `Nächste Physio am 10.11.` und fragt `Welche Themen sollten wir ansprechen?`. SMARTcoach bietet anhand der fiktiven Vorgeschichte vorbereitete Fragen an. Diese werden erst nach expliziter Bestätigung übernommen.

**Kernablauf C (F/V):** Anna wechselt auf die Angehörigenperspektive. Dieselbe Journey zeigt Zusatzthemen `Wie unterstützen?`, `Was weiss ich über den Verlauf?`, `Was belastet mich?`. Eigene sensible Beobachtungen werden nicht ohne Zustimmung für andere freigegeben.

**Provenienzmodell (V):** Jede Datenkarte enthaelt eine Kategorie und Quelle: `Spitalbericht (Demo)`, `Physioplan (Demo)`, `Selbst berichtet`, `Geplant`, `Frage`, `Persönliches Ziel`. Die Daten erhalten interne IDs, damit Erklärungen und Journey auf dieselbe Quelle zeigen. `Aus Bericht` ist nie gleichbedeutend mit `medizinisch vom Coach verordnet`.

## 7. Simulierte Daten und Quellen

**FESTGELEGT:** Keine produktive EPIC-Verbindung. Personen, Dokumente, Befunde, Termine und Eingaben im Mock-up sind erfunden. Demos müssen erkennbar als solche gekennzeichnet sein (z. B. unaufdringlicher Header `Demo mit Beispieldaten`). Keine echten Gesundheitsdaten in GitHub Pages.

**VORSCHLAG zur Wartbarkeit:** Inhalte getrennt vom Code in statischen strukturierten Demo-Datendateien (`demo-personen.json`, `demo-ereignisse.json`, `demo-berichte.json`, `dialoge.json`) halten. Die `.md`-Dateien dienen als redaktionelle Spezifikation und Koordinationsbasis für Codex; spätere Fiktionsgeschichte und Dialoge sollen austauschbar sein, ohne dass Layoutkomponenten neu gebaut werden.

**Medien (F):** Lokal auf dem Tablet `Documents/SMART`, nicht im öffentlichen GitHub. Einstellung muss nach Neustart bekannt sein; Zugriffberechtigungen auf ausgewählte Dateien können Android-/Browser-abhaengig neu erforderlich sein. Wo noetig Import in Browser-`IndexedDB` nach expliziter Auswahl prüfen. Fehlende Medien: Text anzeigen und unaufdringlich auf fehlende Datei hinweisen.

**Speicher:** Kleine Präferenzen `localStorage`; Demo-Einträge je nach Aufwand `localStorage` oder `IndexedDB`. Offline/Service-Worker wie PWA, jedoch keine Zusage für permanente Datei-Berechtigungen oder Betrieb im Hintergrund.

**Interviewkontext:** Testdaten vor dem nächsten Interview über eine leicht auffindbare Reset-Funktion im Interviewmodus rücksetzbar machen. Ein echtes Krankenhaus-Logo oder EPIC-Fenster ohne klare Demo-Markierung vermeiden.

## 8. Besondere Sicherheits- und Datenschutzregeln

- Auch bei fiktiven Angaben keine unbelegten Freigaben zu Belastung, Treppensteigen, Sturz-Aufstehen oder Medikamentenaenderungen erfinden.
- Gespräche mit medizinscher Dringlichkeit dürfen nicht mit einem harmlosen Quiz oder erfundener Sicherheit beantwortet werden; für echte akute Situationen auf Behandlungsteam bzw. Notfall verweisen (Schweiz 144).
- Aktive Erinnerungen und proaktive Ansprache nur nach Zustimmung; nach `Beenden` keine Sprachmeldungen mehr, bis Interaktion neu aufgenommen wird.
- Keine ungewollte Einsicht in individuelle Sorgen der Angehörigen. Im Mock-up als Designfrage kennzeichnen, wie später Rollen- und Freigaberechte gestaltet werden.
- Qualitatives Beobachtungsprotokoll mit Kennzeichnung `Vertraulich` nicht im öffentlichen GitHub-Repository oder als statische GitHub-Pages-Datei speichern.
- Fortschrittsindikatoren zeigen **dokumentierte Schritte**, nicht medizinische Heilung, Erfolg in Prozent oder Wettbewerbsmechaniken.

## 9. Vorgehen und Abnahmekriterien (Vorschlag)

### Phase A - Klickbares und gestalterisch testbares Grundgerüst

- Ruhebildschirm, Journey-Dashboard mit sichtbarem, fiktivem Ablauf, Rolle umschalten, **sichtbarer Schalter `Aktive Begleitung` (AUS als Standard, Einwilligungsdialog, EIN/AUS-Anzeige, lokale Speicherung)**, vier grosse Quick-Actions, Basis-Navigation, grosse Stopp-Schaltflaeche.
- Konfiguration/Reset, gespeicherte Präferenzen, responsive Layouts Hoch-/Querformat, Standalone-PWA via GitHub Pages.
- Mindestens drei anklickbare Ereignisse (`Operation`, `Austritt`, `Heute`), zunächst mit Platzhaltertexten und Quellenhinweis.
- Abnahme: keine Ansicht unleserlich; Stopp stoppt alles; Neustart behaelt Einstellungen; Journey-HOME von IDLE in einem Tap erreichbar. Eine Testperson kann auf HOME erkennen, **ob** SMARTcoach selbst nachfragen darf, **welche** Impulse moeglich sind, und die Funktion aktivieren und ausschalten. Beim ersten Geruest wird noch kein autonomer Dialog ausgelöst.

### Phase B - Kernnutzen Information demonstrieren

- Fiktive Entlass-/OP-/Physio-Berichte, leicht verständliche Erklärungen, `Woher kommt das?`, `Was heisst das für mich?`, vorgefertigte Fragen/Antworten.
- Abnahme: Testperson kann nach einem kurzen Interviewfall die Fragen `Was wurde operiert?`, `Was steht als Nächstes an?`, `Woher kommt diese Information?` erfolgreich beantworten.

### Phase C - Dialog und lokale Medien

- MP3-Zuordnung und lokale Videos, Textalternativen, Antwortbuttons, Bedienbarkeit bei Medienwechseln, Neustart- und Offline-Test.

### Phase D - Alltag und Verlauf

- Tagebuch, Sichtbarkeit neuer Einträge auf Journey, Angehörigenhilfen, Terminvorbereitung, Quiz.

### Phase E - Proaktive Demo und weitere Verfeinerung

- Simulierte Ausloeser fuer die bereits im HOME einschaltbare `Aktive Begleitung`, Regeln aus Demo-Plan/Einträgen, Ruhe- und Unterbrechungsverhalten, Spracheingabe-Experiment.

Keine Phase beginnt ohne Besprechung des Umfangs und einen klar formulierten Codex-Auftrag; bestätigte Funktionen bleiben erhalten.

## 10. Beobachtungsaufgaben für Interviews (Vorschlag)

1. `Zeigen Sie auf der Journey, was im Spital passiert ist.`
2. `Finden Sie heraus, was im Entlassbrief zu Bewegung und nächstem Termin steht.`
3. `Lassen Sie sich einen medizinischen Begriff erklären und zeigen Sie, woher die Aussage stammt.`
4. `Wechseln Sie in die Angehörigenperspektive und finden Sie eine Antwort auf die Frage nach sinnvoller Unterstützung.`
5. `Halten Sie eine Sorge für den nächsten Termin fest.`
6. `Erkennen Sie, ob SMARTcoach von sich aus Fragen stellen darf. Schalten Sie Aktive Begleitung ein, erklaeren Sie, was dadurch geschieht, und schalten Sie sie wieder aus.`
7. `Beenden Sie SMARTcoach während einer laufenden Interaktion und starten Sie neu.`

Pro Aufgabe getrennt erheben: Gefunden? Richtig verstanden? Als nuetzlich empfunden? Als selbstbestimmt empfunden? Würde die Person Informationen für glaubwuerdig halten - und warum?

## 11. Noch offene Entscheidungen

- Soll HOME initial `Gesamter Weg` oder die Zeitspanne `Heute +/- 14 Tage` zeigen? **Empfehlung:** zunächst die gesamte Journey mit wenigen grossen Stationen und markiertem Heute zeigen. `Heute zentrieren` wechselt in die Detailansicht von ca. +/- 14 Tagen. Lesbarkeit auf dem Tablet prüfen.
- Soll die Rollenauswahl direkt als Umschalter auf HOME erfolgen? **Empfehlung:** ja, statt zweier Eingangstore. Auf Testpersonen prüfen.
- Wie viele Kontextkarten sind zugleich lesbar? **Empfehlung:** hoechstens drei.
- Gehören medizinische Fragen, Übungen und Angehörigenfragen in einen gemeinsamen Dialogbereich oder in zwei Varianten? Zunächst dieselbe Dialogkomponente, andere Vorschlagsfragen.
- Was ist für Testpersonen intuitiver: `Beenden`, `Ruhemodus` oder `Stopp`? Funktion bleibt unabhängig von der Bezeichnung gleich.
- Welcher gut verstaendliche Name passt der Zielgruppe besser: `Aktive Begleitung`, `Aktives Coaching` oder `Von sich aus nachfragen`? Vorerst `Aktive Begleitung` als UX-Vorschlag.
- Welche lokal verfuegbaren Bilder/MP3/Video-Dateien werden für die Pilot-Interviews tatsächlich geliefert?
- Welche Informationen dürfen später zwischen Patienten- und Angehörigenperspektive geteilt werden? Im Mock-up ausschliesslich fiktive Daten; reale Freigabelogik nicht vorgaukeln.

## 12. Bezug zu den anderen Markdown-Dateien

- `SMARTcoach_Patientenjourney_v0.2.md` - fiktive, aus den Unterlagen abgeleitete Geschichte Ernst (79) und Anna (72), mit Quellenzuordnung und Interview-Szenen.
- `SMARTcoach_Dialogkatalog_v0.2.md` - Dialogknoten aus v0.1, aktualisiert um HOME als Journey-Dashboard und neue Informationsdialoge. Kein Nachweis, dass MP3-Dateien bereits existieren.

**Diese v0.2.1 ist als Konzept überarbeitet, aber noch nicht als Implementierungsauftrag beschlossen.**
