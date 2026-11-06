# SMARTcoach – Dialogkatalog v0.2.1

**Stand:** 06.11.2026  
**Status:** Aktualisierter, vollständiger Demo-Katalog (v0.1-Dialoge erhalten, neue informationsorientierte Knoten ergänzt). Fachlich und gestalterisch noch zu validieren. Alle Personen, Dokumente und Ereignisse sind fiktiv. **Keine MP3-Dateien sind durch diese Markdown-Datei erzeugt.**

**Wichtigste Aenderung gegenüber v0.1:** `HOME` ist keine reine Rollenwahl mehr, sondern ein gemeinsames **Journey-Dashboard**. Der Rollenwechsel erfolgt über eine immer sichtbare Umschaltmöglichkeit `Patient` / `Angehörige`. Die Knoten `PAT_START` und `REL_START` bleiben erhalten, sind aber Unterbereiche des Dashboards. Neue `KNOW_*`-Knoten demonstrieren die erklärte, rückfragbare Spitalinformation. Die `KNOW_*`-Knoten sind zunächst mit sichtbarem Text testbar; einzelne MP3s werden später gezielt erstellt.  
**Ergaenzung v0.2.1:** Der HOME-Bildschirm zeigt die Option `Aktive Begleitung` mit EIN/AUS-Status und einer Erklaerung der proaktiven Befragungen, Erinnerungen und Vorschlaege. Die bestehenden PRO-Dialogknoten werden weiterverwendet. Die Schalterbedienung ist Teil des Grundgeruests; echte zeit- bzw. planabhaengige Ausloeser kommen spaeter.
**Anzahl Dialog-/Navigationsknoten:** 97 (unveraendert)

## 1. Aufbau und Medienzuordnung

Jeder Knoten besitzt eine **stabile ID**, eine Rolle, einen Auslöser/Titel, den optionalen **gesprochenen Text** (vorproduzierte MP3), den **sichtbaren Chatbot-Text**, auswählbare **Antwort-Buttons**, bei Bedarf **Wirkung auf das lokale Tagebuch** und optionale Medien.

- **MP3**: Wenn ein gesprochener Text vorhanden ist, wird er später in `Documents/SMART/audio/SC_<ID>.mp3` als Datei abgelegt. **Es werden hier keine MP3-Dateien erzeugt.**
- **Chat-Text**: Muss auch ohne MP3 gut lesbar sein und darf bei Stummschaltung nicht verschwinden. Kann bewusst anders gekürzt sein als die gesprochene Form.
- **Video**: Vorgesehene Dateinamen stehen bei den betreffenden Dialogen; diese Videos existieren im Dokument noch nicht und müssen lokal bereitgestellt werden.
- **Buttons**: Sind im Mock-up die verlässliche Demonstrationssteuerung. Freie Texteingabe und Android-Tastatur-Diktat können separat getestet werden, sind aber nicht mit einer KI-Antwort gleichzusetzen.
- **Globaler Stopp**: Aus jedem Bildschirm jederzeit erreichbar, stoppt laufende Videos/MP3s und führt zu `IDLE`. Die Schaltfläche wird global in der GUI implementiert; sie muss nicht in jedem Antwortsatz wiederholt werden.
- **Aktive Begleitung**: Auf HOME immer sichtbar, Standard AUS. Erst nach Opt-in darf SMARTcoach in der sichtbaren PWA von sich aus nachfragen, an vorhandene Plan-Uebungen erinnern oder Aktivitaeten vorschlagen. AUS bedeutet: nur nutzerinitiierte Gespraeche. Im Ruhebildschirm keine Ansprache und kein Medienstart.

Die Namen, Dateipfade und Inhalte sind Vorschläge für die Demo. Fehlende lokale Medien müssen mit einer unaufdringlichen Meldung und dem sichtbaren Text abgefangen werden.

## 2. Start- und Zustandsschema

```text
IDLE -> HOME (zentrale Journey, Perspektive Patient oder Angehörige)
HOME -> JOURNEY_ALL / KNOW_TODAY / KNOW_OVERVIEW / KNOW_NEXT
HOME -> PAT_START oder REL_START (entsprechend aktivierter Perspektive)
HOME -> Aktive Begleitung EIN -> PRO_OPTIN -> PRO_ON -> HOME
HOME -> Aktive Begleitung AUS -> PRO_OFF -> HOME
HOME -> Beispielfrage zeigen (nur wenn EIN) -> PRO_CHECK (explizite Demo)
PAT_START -> Übungen / Tagebuch / Journey / Dokumente / Chat
REL_START -> Alltagshilfe / Befinden / Quiz / Journey / Terminvorbereitung
Jeder Zustand --global Beenden--> STOP -> IDLE
```

**UI-Regel:** `Patient` / `Angehörige` ist eine globale Perspektivumschaltung, kein komplizierter neuer Login. Alle Aussagen über Spitalberichte kennzeichnen die fiktive Demo-Quelle. Effekte auf Tagebuch oder Fragenliste werden erst nach bewusster Bestätigung ausgeführt.

## 3. Vollständiger Demo-Dialogablauf

### IDLE — Ruhebildschirm
- **Rolle:** `alle`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „SMARTcoach – Berühren Sie den Bildschirm, um die Übersicht zu öffnen.“
- **Antwortmöglichkeiten:** „Bildschirm berühren“ -> `HOME`
- **Hinweis:** Ruhige lokale Bilderfolge; keine Musik; vor Start keine automatische Sprachausgabe.

### HOME - Zentrales Journey-Dashboard
- **Rolle:** `alle` (globale Perspektive `patient` oder `angehörige`)
- **MP3:** keine (Dashboard)
- **Gesprochen:** -
- **Chatbot-Text:** `Hier sehen Sie den bisherigen Weg, den heutigen Stand und die nächsten im Demo-Plan hinterlegten Schritte. Sie können direkt auf Ereignisse, Fragen und Berichte tippen.`
- **Journey:** Fiktive Ereignisse J00-J13 mit `Heute zentrieren`, `Gesamter Weg`, `+`, `-`. Aktueller Marker J09.
- **Informationskarten:** `Heute wichtig` -> `KNOW_TODAY`; `Was steht in den Berichten?` -> `KNOW_OVERVIEW`; `Fragen für den nächsten Termin` -> `SUM_START`.
- **Immer sichtbare Steuerkarte `Aktive Begleitung`:** Zustand `AUS`: `SMARTcoach antwortet nur, wenn Sie ihn selbst ansprechen.` Button `Einschalten` -> `PRO_OPTIN`. Zustand `EIN`: `SMARTcoach darf gelegentlich von sich aus nach Ihrem Befinden fragen, an Uebungen erinnern und Aktivitaeten vorschlagen.` Button `Ausschalten` -> `PRO_OFF`. Bei `EIN` optional `Beispielfrage zeigen` -> `PRO_CHECK`. Die Karte ist kein austauschbarer Infotext und bleibt im sichtbaren Dashboard.
- **Grosse Aktionen:** `SMARTcoach fragen` -> `KNOW_CONTEXT_ASK`; `Mein Weg` -> `JOURNEY_ALL`; `Mehr für Patienten` -> `PAT_START` (Rolle patient); `Mehr für Angehörige` -> `REL_START` (Rolle angehörige).
- **Globale Elemente:** `Perspektive wechseln`, `Einstellungen` -> `SETTINGS`, `Beenden` -> `STOP`.
- **Hinweis:** Die gezeigten Berichte und Termine sind erfundene Demo-Daten. Nach `STOP` kein automatisches Audio und keine proaktive Ansprache im Ruhemodus. Die gespeicherte EIN/AUS-Einwilligung bleibt bestehen und ist beim erneuten Oeffnen sofort sichtbar.

### SETTINGS — Einstellungen
- **Rolle:** `alle`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „Hier stellen Sie Lautstärke, Stummschaltung, Textgrösse, lokale Medien und die Demo-Konfiguration ein.“
- **Antwortmöglichkeiten:** „Proaktive Ansprache einstellen“ -> `PRO_OPTIN`; „Zurück zur Übersicht“ -> `HOME`
- **Wirkung:** Präferenzen lokal dauerhaft speichern. Medienberechtigung bei Neustart getrennt prüfen.

### STOP — Globaler Abbruch
- **Rolle:** `alle`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „Ruhebildschirm“
- **Antwortmöglichkeiten:** „Bildschirm berühren“ -> `HOME`
- **Wirkung:** Aus JEDER Ansicht direkt erreichbar. Audio und Video sofort stoppen; ausstehende Dialogaktionen nicht fortfuehren; proaktive Ansprache im Ruhebildschirm aussetzen, ohne die ausdrueckliche EIN/AUS-Praeferenz zu loeschen.
- **Hinweis:** Kein zu sprechender Dialog. Technisch als globale Aktion, nicht als normaler Dialogschritt implementieren.

### PAT_START — Persönlicher Einstieg
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_START.mp3`
- **Gesprochen:** „Guten Tag, Ernst. Schön, dass Sie da sind. Wie kann ich Sie heute unterstützen?“
- **Chatbot-Text:** „Guten Tag, Ernst. Schön, dass Sie da sind. Wie kann ich Sie heute unterstützen?“
- **Antwortmöglichkeiten:** „Welche Übungen sind heute vorgesehen?“ -> `PAT_EXPLAIN`; „Was habe ich heute gemacht?“ -> `PAT_LOG_START`; „Wie geht es mir auf meinem Weg?“ -> `PAT_JOURNEY`; „Was steht in meinem Spitalbericht?“ -> `PAT_DOC_START`; „Ich möchte etwas fragen“ -> `PAT_CHAT`

### PAT_EXPLAIN — Übungen erklären
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_EXPLAIN.mp3`
- **Gesprochen:** „Im Spital haben Sie mit der Physiotherapie Bewegungen und sicheres Aufstehen geübt. Ich kann Ihnen ein Beispielvideo zeigen. Massgebend sind Ihre persönlichen Anweisungen.“
- **Chatbot-Text:** „Laut Ihrem fiktiven Therapieplan wurden Übungen für zu Hause besprochen. Soll ich Ihnen das passende Beispielvideo zeigen?“
- **Antwortmöglichkeiten:** „Video ansehen“ -> `PAT_VIDEO`; „Ich habe bereits geübt“ -> `PAT_LOG_EX_SAVE`; „Ich bin unsicher“ -> `PAT_EX_UNSURE`; „Später“ -> `PAT_START`
- **Hinweis:** Kein automatisch erstelltes Therapieprogramm oder neue Belastungsvorgabe.

### PAT_EX_UNSURE — Unsicherheit zur Übung
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_EX_UNSURE.mp3`
- **Gesprochen:** „Wenn eine Bewegung unklar ist, lassen Sie sie sich bitte von Ihrer Physiotherapeutin oder Ihrem Physiotherapeuten zeigen. Ich kann die Frage für Ihren Termin vormerken.“
- **Chatbot-Text:** „Wenn eine Bewegung unklar ist, lassen Sie sie sich bitte von Ihrer Physiotherapeutin oder Ihrem Physiotherapeuten zeigen. Ich kann die Frage für Ihren Termin vormerken.“
- **Antwortmöglichkeiten:** „Frage vormerken“ -> `SUM_ADD_EXERCISE`; „Zurück zu Übungen“ -> `PAT_EXPLAIN`

### PAT_VIDEO — Übungsvideo
- **Rolle:** `patient`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „Beispielvideo: Sicheres Aufstehen. Ein Video ist nur ein Zusatz zu Ihrer persönlichen Instruktion.“
- **Antwortmöglichkeiten:** „Video beendet – weiter“ -> `PAT_VIDEO_DONE`; „Zurück zu Übungen“ -> `PAT_EXPLAIN`
- **Video/Medium:** `Documents/SMART/video/sicher_aufstehen.mp4`
- **Hinweis:** Video in Displaybreite; bei jeder Navigation oder Stopp pausieren und zurücksetzen; kein automatischer Start ohne User-Geste.

### PAT_VIDEO_DONE — Nach dem Video
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_VIDEO_DONE.mp3`
- **Gesprochen:** „Möchten Sie festhalten, ob Sie heute eine Übung gemacht haben?“
- **Chatbot-Text:** „Möchten Sie festhalten, ob Sie heute eine Übung gemacht haben?“
- **Antwortmöglichkeiten:** „Ja, Übung dokumentieren“ -> `PAT_LOG_EX_SAVE`; „Nein, nur angeschaut“ -> `PAT_START`

### PAT_LOG_START — Was heute geschehen ist
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_LOG_START.mp3`
- **Gesprochen:** „Was haben Sie heute gemacht? Wir können eine Aktivität oder Ihr Befinden festhalten.“
- **Chatbot-Text:** „Was haben Sie heute gemacht? Wir können eine Aktivität oder Ihr Befinden festhalten.“
- **Antwortmöglichkeiten:** „Ich bin gegangen“ -> `PAT_WALK_DURATION`; „Ich habe Übungen gemacht“ -> `PAT_LOG_EX_SAVE`; „Heute noch keine Aktivität“ -> `PAT_LOG_NONE`; „Ich habe Schmerzen“ -> `PAT_PAIN_START`; „Wie fühle ich mich?“ -> `PAT_MOOD_START`

### PAT_WALK_DURATION — Gehaktivität erfragen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_WALK_DURATION.mp3`
- **Gesprochen:** „Wie lange waren Sie ungefähr unterwegs? Eine Schätzung genügt.“
- **Chatbot-Text:** „Wie lange waren Sie ungefähr unterwegs? Eine Schätzung genügt.“
- **Antwortmöglichkeiten:** „Etwa fünf Minuten“ -> `PAT_WALK_5`; „Etwa zehn Minuten“ -> `PAT_WALK_10`; „Ich weiss es nicht“ -> `PAT_WALK_UNKNOWN`

### PAT_WALK_5 — Fünf Minuten dokumentiert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_WALK_5.mp3`
- **Gesprochen:** „Danke. Ich habe Ihren Bericht über ungefähr fünf Minuten Gehen für heute eingetragen.“
- **Chatbot-Text:** „Danke. Ich habe Ihren Bericht über ungefähr fünf Minuten Gehen für heute eingetragen.“
- **Antwortmöglichkeiten:** „Eintrag auf meinem Weg ansehen“ -> `PAT_JOURNEY`; „Weitere Aktivität eintragen“ -> `PAT_LOG_START`
- **Wirkung:** Tagebuch: patient/Bewegung/Gehen ca. 5 Min. am Demo-Heute; Journey-Marker.

### PAT_WALK_10 — Zehn Minuten dokumentiert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_WALK_10.mp3`
- **Gesprochen:** „Danke. Ich habe Ihren Bericht über ungefähr zehn Minuten Gehen für heute eingetragen.“
- **Chatbot-Text:** „Danke. Ich habe Ihren Bericht über ungefähr zehn Minuten Gehen für heute eingetragen.“
- **Antwortmöglichkeiten:** „Eintrag auf meinem Weg ansehen“ -> `PAT_JOURNEY`; „Weitere Aktivität eintragen“ -> `PAT_LOG_START`
- **Wirkung:** Tagebuch: patient/Bewegung/Gehen ca. 10 Min. am Demo-Heute; Journey-Marker.

### PAT_WALK_UNKNOWN — Gehen ohne Dauer dokumentiert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_WALK_UNKNOWN.mp3`
- **Gesprochen:** „Kein Problem. Ich notiere, dass Sie heute gegangen sind – ohne Zeitangabe.“
- **Chatbot-Text:** „Kein Problem. Ich notiere, dass Sie heute gegangen sind – ohne Zeitangabe.“
- **Antwortmöglichkeiten:** „Mein Tagebuch ansehen“ -> `PAT_JOURNEY`; „Zurück“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Bewegung/Gehen, Dauer nicht angegeben; Journey-Marker.

### PAT_LOG_EX_SAVE — Übung dokumentiert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_LOG_EX_SAVE.mp3`
- **Gesprochen:** „Gut, ich habe eingetragen, dass Sie heute Ihre vereinbarten Übungen gemacht haben. Ob die Übungen für Sie passend sind, beurteilen Sie gemeinsam mit Ihrer Physiotherapie.“
- **Chatbot-Text:** „Gut, ich habe eingetragen, dass Sie heute Ihre vereinbarten Übungen gemacht haben. Ob die Übungen für Sie passend sind, beurteilen Sie gemeinsam mit Ihrer Physiotherapie.“
- **Antwortmöglichkeiten:** „Auf meinem Weg anzeigen“ -> `PAT_JOURNEY`; „Weitere Aktivität eintragen“ -> `PAT_LOG_START`; „Zurück zum Patientenmenü“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Übung/heute nach Selbstauskunft; Journey-Marker. Keine klinische Fortschrittsbewertung.

### PAT_LOG_NONE — Keine Aktivität eingetragen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_LOG_NONE.mp3`
- **Gesprochen:** „Danke für die Rückmeldung. Ich halte fest, dass Sie heute noch keine Aktivität genannt haben. Sie können den Eintrag später ergänzen.“
- **Chatbot-Text:** „Danke für die Rückmeldung. Ich halte fest, dass Sie heute noch keine Aktivität genannt haben. Sie können den Eintrag später ergänzen.“
- **Antwortmöglichkeiten:** „Wie fühle ich mich?“ -> `PAT_MOOD_START`; „Zurück“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Aktivitätsstatus/keine gemeldet. Keine Schuldzuweisung.

### PAT_PAIN_START — Schmerz erfassen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_PAIN_START.mp3`
- **Gesprochen:** „Möchten Sie angeben, wie stark Ihre Schmerzen heute sind? Das ersetzt keine medizinische Beurteilung.“
- **Chatbot-Text:** „Möchten Sie angeben, wie stark Ihre Schmerzen heute sind? Das ersetzt keine medizinische Beurteilung.“
- **Antwortmöglichkeiten:** „Leicht“ -> `PAT_PAIN_MILD`; „Mittel“ -> `PAT_PAIN_MODERATE`; „Stark oder neu ungewöhnlich“ -> `PAT_PAIN_SEVERE`; „Überspringen“ -> `PAT_START`

### PAT_PAIN_MILD — Leichte Schmerzen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_PAIN_MILD.mp3`
- **Gesprochen:** „Ich habe Ihre Angabe notiert. Wenn Sie Fragen haben oder sich etwas verändert, wenden Sie sich an Ihr Behandlungsteam.“
- **Chatbot-Text:** „Ich habe Ihre Angabe notiert. Wenn Sie Fragen haben oder sich etwas verändert, wenden Sie sich an Ihr Behandlungsteam.“
- **Antwortmöglichkeiten:** „Frage für Physio vormerken“ -> `SUM_ADD_PAIN`; „Zurück“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Schmerz/leicht nach Selbstauskunft.

### PAT_PAIN_MODERATE — Mittlere Schmerzen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_PAIN_MODERATE.mp3`
- **Gesprochen:** „Ich habe Ihre Angabe notiert. Besprechen Sie anhaltende oder zunehmende Beschwerden mit Ihrem Behandlungsteam.“
- **Chatbot-Text:** „Ich habe Ihre Angabe notiert. Besprechen Sie anhaltende oder zunehmende Beschwerden mit Ihrem Behandlungsteam.“
- **Antwortmöglichkeiten:** „Frage für Physio vormerken“ -> `SUM_ADD_PAIN`; „Zurück“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Schmerz/mittel nach Selbstauskunft.

### PAT_PAIN_SEVERE — Starke oder neue Schmerzen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_PAIN_SEVERE.mp3`
- **Gesprochen:** „Das klingt wichtig. Bitte lassen Sie neue, starke oder zunehmende Schmerzen medizinisch abklären. Bei akuten Warnzeichen oder einem Notfall rufen Sie die Notrufnummer 144.“
- **Chatbot-Text:** „Das klingt wichtig. Bitte lassen Sie neue, starke oder zunehmende Schmerzen medizinisch abklären. Bei akuten Warnzeichen oder einem Notfall rufen Sie die Notrufnummer 144.“
- **Antwortmöglichkeiten:** „Kontakthinweis ansehen“ -> `PAT_DOC_CONTACT`; „Zurück“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Schmerz/stark oder neu; Hinweis. Kein späteres Abwarten als Standardempfehlung.

### PAT_MOOD_START — Befinden erfragen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_MOOD_START.mp3`
- **Gesprochen:** „Wie fühlen Sie sich heute? Wenn Sie nicht antworten möchten, ist das völlig in Ordnung.“
- **Chatbot-Text:** „Wie fühlen Sie sich heute? Wenn Sie nicht antworten möchten, ist das völlig in Ordnung.“
- **Antwortmöglichkeiten:** „Zuversichtlich“ -> `PAT_MOOD_GOOD`; „Unsicher oder ängstlich“ -> `PAT_MOOD_AFRAID`; „Niedergeschlagen“ -> `PAT_MOOD_LOW`; „Überspringen“ -> `PAT_START`

### PAT_MOOD_GOOD — Zuversicht
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_MOOD_GOOD.mp3`
- **Gesprochen:** „Danke für die Rückmeldung. Ich habe Ihre Stimmung notiert.“
- **Chatbot-Text:** „Danke für die Rückmeldung. Ich habe Ihre Stimmung notiert.“
- **Antwortmöglichkeiten:** „Mein Weg“ -> `PAT_JOURNEY`; „Zurück“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Stimmung/zuversichtlich.

### PAT_MOOD_AFRAID — Angst vor erneutem Sturz
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_MOOD_AFRAID.mp3`
- **Gesprochen:** „Nach einem Sturz kann Unsicherheit im Alltag belastend sein. Möchten Sie diese Frage für die Physiotherapie vormerken?“
- **Chatbot-Text:** „Nach einem Sturz kann Unsicherheit im Alltag belastend sein. Möchten Sie diese Frage für die Physiotherapie vormerken?“
- **Antwortmöglichkeiten:** „Ja, vormerken“ -> `SUM_ADD_FEAR`; „Nicht jetzt“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Stimmung/ängstlich; freiwillig.

### PAT_MOOD_LOW — Niedergeschlagenheit
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_MOOD_LOW.mp3`
- **Gesprochen:** „Danke, dass Sie mir das sagen. Möchten Sie darüber mit Anna oder einer betreuenden Fachperson sprechen? Ich kann die Sorge für den nächsten Termin notieren.“
- **Chatbot-Text:** „Danke, dass Sie mir das sagen. Möchten Sie darüber mit Anna oder einer betreuenden Fachperson sprechen? Ich kann die Sorge für den nächsten Termin notieren.“
- **Antwortmöglichkeiten:** „Für Termin notieren“ -> `SUM_ADD_FEAR`; „Überspringen“ -> `PAT_START`
- **Wirkung:** Tagebuch: patient/Stimmung/niedergeschlagen; freiwillig.

### PAT_JOURNEY — Mein Weg – Überblick
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_JOURNEY.mp3`
- **Gesprochen:** „Hier sehen Sie Ihren Weg vom Sturz bis zu Ihren persönlichen Zielen. Der heutige Tag ist markiert.“
- **Chatbot-Text:** „Hier sehen Sie Ihren Weg vom Sturz bis zu Ihren persönlichen Zielen. Der heutige Tag ist markiert.“
- **Antwortmöglichkeiten:** „Gesamte Geschichte zeigen“ -> `JOURNEY_ALL`; „Auf heute zentrieren“ -> `JOURNEY_CENTER`; „Meilenstein öffnen“ -> `JOURNEY_MILESTONE`; „Zurück“ -> `PAT_START`

### JOURNEY_ALL — Gesamte Journey
- **Rolle:** `alle`
- **MP3:** keine (Ansicht)
- **Gesprochen:** -
- **Chatbot-Text:** „Gesamter Weg: Alltag vor dem Sturz, Sturz, Operation, Spital, Austritt, zu Hause, heute, nächste Termine und persönliche Ziele. Geplante Schritte sind keine Heilungsversprechen.“
- **Antwortmöglichkeiten:** „Auf heute zentrieren“ -> `JOURNEY_CENTER`; „Operation erklären“ -> `KNOW_OP`; „Berichte einfach erklärt“ -> `KNOW_OVERVIEW`; „Zurück zur Übersicht“ -> `HOME`
- **Wirkung:** Gesamten Demo-Zeitraum mit grossen, gut lesbaren Stationen anzeigen. Buttons `+` und `-` für Zoom verfügbar.

### JOURNEY_CENTER — Journey: heute +/- 14 Tage
- **Rolle:** `alle`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „Detailansicht: ungefähr 14 Tage vor bis 14 Tage nach dem Demo-Heute. Die aktuelle Position befindet sich in der Mitte.“
- **Antwortmöglichkeiten:** „Heutigen Tagebucheintrag öffnen“ -> `JOURNEY_TODAY`; „Gesamtansicht“ -> `JOURNEY_ALL`; „Zum Hauptmenü“ -> `HOME`
- **Wirkung:** Zentrierung auf Demo-Heute; Detail-Zoom umstellen.

### JOURNEY_TODAY — Journey: aktueller Tagebucheintrag
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_JOURNEY_TODAY.mp3`
- **Gesprochen:** „Hier erscheinen die Aktivitäten und Beobachtungen, die Sie für heute eingetragen haben.“
- **Chatbot-Text:** „Hier erscheinen die Aktivitäten und Beobachtungen, die Sie für heute eingetragen haben.“
- **Antwortmöglichkeiten:** „Zurück zur Detailansicht“ -> `JOURNEY_CENTER`; „Patientenmenü“ -> `PAT_START`
- **Wirkung:** Tatsächlich gespeicherte Demo-Einträge des aktuellen Tages anzeigen.

### JOURNEY_MILESTONE — Journey: Entlassung
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_JOURNEY_MILESTONE.mp3`
- **Gesprochen:** „Am zweiten November sind Sie aus dem Spital nach Hause gekommen. Die Entlassung ist ein wichtiger Abschnitt Ihrer Geschichte. Ich kann den fiktiven Entlassbrief in einfachen Worten erklären.“
- **Chatbot-Text:** „Entlassung am 2. November. Was wurde für zu Hause besprochen?“
- **Antwortmöglichkeiten:** „Was steht im Entlassbrief?“ -> `KNOW_NEXT`; „Quelle ansehen“ -> `KNOW_SOURCE_DISCHARGE`; „Zurück zur Journey“ -> `JOURNEY_ALL`
- **Quelle:** E06/E07 (Demo).

### PAT_DOC_START — Spitalunterlagen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_DOC_START.mp3`
- **Gesprochen:** „Ich kann Ihnen Informationen aus Ihren fiktiven Spitalunterlagen in einfacher Sprache erklären. Was interessiert Sie?“
- **Chatbot-Text:** „Ich kann Ihnen Informationen aus Ihren fiktiven Spitalunterlagen in einfacher Sprache erklären. Was interessiert Sie?“
- **Antwortmöglichkeiten:** „Was wurde operiert?“ -> `PAT_DOC_OP`; „Was steht zur Rehabilitation?“ -> `PAT_DOC_REHAB`; „Was steht zu den Medikamenten?“ -> `PAT_DOC_MED`; „Wen kann ich kontaktieren?“ -> `PAT_DOC_CONTACT`
- **Hinweis:** Die Demo muss kennzeichnen: Diese Unterlagen sind erfunden und nicht mit EPIC verbunden.

### PAT_DOC_OP — Operation in Alltagssprache
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_DOC_OP.mp3`
- **Gesprochen:** „Sie haben sich rechts nahe der Hüfte den oberen Oberschenkelknochen gebrochen. Bei der Operation wurde der Knochen mit einem Nagel und Schrauben stabilisiert. Das ist eine vereinfachte Erklärung des fiktiven Berichts.“
- **Chatbot-Text:** „Bei der Operation wurde der Bruch mit einem Nagel und Schrauben stabilisiert. Quelle: fiktiver Operationsbericht vom 27. Oktober.“
- **Antwortmöglichkeiten:** „Was ist ein Marknagel?“ -> `KNOW_TERMS`; „Quelle ansehen“ -> `KNOW_SOURCE_OP`; „Was bedeutet das für mich?“ -> `KNOW_NEXT`; „Weitere Unterlagen“ -> `PAT_DOC_START`
- **Quelle:** E01/E02. Keine automatische Belastungsfreigabe.

### PAT_DOC_REHAB — Entlassung und Mobilisation
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_DOC_REHAB.mp3`
- **Gesprochen:** „In Ihrem fiktiven Entlassbrief steht, dass Sie die vereinbarten Übungen fortsetzen und Ihre persönlichen Bewegungsvorgaben beachten sollen. Bei Unsicherheit hilft Ihnen die Physiotherapie weiter.“
- **Chatbot-Text:** „In Ihrem fiktiven Entlassbrief steht, dass Sie die vereinbarten Übungen fortsetzen und Ihre persönlichen Bewegungsvorgaben beachten sollen. Bei Unsicherheit hilft Ihnen die Physiotherapie weiter.“
- **Antwortmöglichkeiten:** „Frage für Physio vormerken“ -> `SUM_ADD_EXERCISE`; „Weitere Unterlagen“ -> `PAT_DOC_START`
- **Wirkung:** Fiktive EPIC-Quellen E03, E04 und E06 anzeigen.

### PAT_DOC_MED — Medikamente
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_DOC_MED.mp3`
- **Gesprochen:** „Hier könnte Ihre vom Spital verordnete Medikamentenliste angezeigt werden. Im Mock-up stehen keine echten Medikamente oder Dosierungen. Bitte verändern Sie Medikamente nicht aufgrund dieser Demo.“
- **Chatbot-Text:** „Hier könnte Ihre vom Spital verordnete Medikamentenliste angezeigt werden. Im Mock-up stehen keine echten Medikamente oder Dosierungen. Bitte verändern Sie Medikamente nicht aufgrund dieser Demo.“
- **Antwortmöglichkeiten:** „Weitere Unterlagen“ -> `PAT_DOC_START`; „Zurück“ -> `PAT_START`
- **Wirkung:** Fiktive EPIC-Quelle E08 anzeigen; keine Medikationsanweisung.

### PAT_DOC_CONTACT — Ansprechpartner / Sicherheit
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_DOC_CONTACT.mp3`
- **Gesprochen:** „Bei gesundheitlichen Fragen wenden Sie sich an Ihr Behandlungsteam. Bei einem akuten medizinischen Notfall gilt in der Schweiz die Notrufnummer 144.“
- **Chatbot-Text:** „Bei gesundheitlichen Fragen wenden Sie sich an Ihr Behandlungsteam. Bei einem akuten medizinischen Notfall gilt in der Schweiz die Notrufnummer 144.“
- **Antwortmöglichkeiten:** „Frage für Termin sammeln“ -> `SUM_START`; „Zurück“ -> `PAT_START`
- **Hinweis:** Im produktiven System wären individuelle Kontaktdaten aus dem Entlassbrief erforderlich.

### PAT_CHAT — Chat und mögliche Frage
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_CHAT.mp3`
- **Gesprochen:** „Sie können eine Frage eintippen oder eine vorgeschlagene Frage auswählen. In dieser Demo sind die Antworten vorbereitet.“
- **Chatbot-Text:** „Sie können eine Frage eintippen oder eine vorgeschlagene Frage auswählen. In dieser Demo sind die Antworten vorbereitet.“
- **Antwortmöglichkeiten:** „Warum muss ich mich bewegen?“ -> `PAT_CHAT_MOVE`; „Was ist ein Marknagel?“ -> `PAT_DOC_OP`; „Ich habe eine andere Frage“ -> `PAT_CHAT_UNMATCHED`; „Zurück“ -> `PAT_START`
- **Wirkung:** Freies Texteingabefeld fokussierbar; Android-Tastatur-Diktat optional, aber keine echte KI-Antwort.

### PAT_CHAT_MOVE — Wozu Bewegung?
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_CHAT_MOVE.mp3`
- **Gesprochen:** „Die vereinbarten Bewegungen und Übungen gehören zu Ihrem Rehabilitationsplan. Wie viel und was genau für Sie passend ist, besprechen Sie mit Ihrer Physiotherapie.“
- **Chatbot-Text:** „Die vereinbarten Bewegungen und Übungen gehören zu Ihrem Rehabilitationsplan. Wie viel und was genau für Sie passend ist, besprechen Sie mit Ihrer Physiotherapie.“
- **Antwortmöglichkeiten:** „Passendes Video ansehen“ -> `PAT_VIDEO`; „Zurück zum Chat“ -> `PAT_CHAT`

### PAT_CHAT_UNMATCHED — Freitext ausserhalb der Demo
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PAT_CHAT_UNMATCHED.mp3`
- **Gesprochen:** „Diese Frage ist in der aktuellen Demonstration noch nicht vorbereitet. Sie können eine der Beispielantworten wählen oder Ihre Frage für den nächsten Termin sammeln.“
- **Chatbot-Text:** „Diese Frage ist in der aktuellen Demonstration noch nicht vorbereitet. Sie können eine der Beispielantworten wählen oder Ihre Frage für den nächsten Termin sammeln.“
- **Antwortmöglichkeiten:** „Für Termin sammeln“ -> `SUM_ADD_OTHER`; „Beispiel-Fragen zeigen“ -> `PAT_CHAT`
- **Hinweis:** Keine vorgetäuschte freie KI-Konversation.

### REL_START — Angehörigen-Einstieg
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_START.mp3`
- **Gesprochen:** „Guten Tag, Anna. Was beschäftigt Sie heute? Ich kann Informationen erklären, eine Frage notieren oder ein kleines Quiz mit Ihnen machen.“
- **Chatbot-Text:** „Guten Tag, Anna. Was beschäftigt Sie heute? Ich kann Informationen erklären, eine Frage notieren oder ein kleines Quiz mit Ihnen machen.“
- **Antwortmöglichkeiten:** „Alltag & praktische Hilfe“ -> `REL_HELP`; „Rehabilitation & Berichte“ -> `KNOW_REL_PERSPECTIVE`; „Wie geht es mir selbst?“ -> `REL_MOOD_START`; „Wissensquiz starten“ -> `QUIZ_1`; „Für den Physiotermin vorbereiten“ -> `SUM_START`

### REL_HELP — Praktische Hilfe im Alltag
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_HELP.mp3`
- **Gesprochen:** „Was möchten Sie über die Unterstützung im Alltag wissen? Ich kann typische Situationen anhand der fiktiven Geschichte von Ernst erklären.“
- **Chatbot-Text:** „Was möchten Sie über die Unterstützung im Alltag wissen? Ich kann typische Situationen anhand der fiktiven Geschichte von Ernst erklären.“
- **Antwortmöglichkeiten:** „Treppensteigen“ -> `REL_STAIRS`; „Aufstehen aus dem Bett“ -> `REL_BED`; „Nach einem Sturz“ -> `REL_FALL`; „Eigene Frage stellen“ -> `REL_ASK`; „Zurück“ -> `REL_START`

### REL_INFO — Rehabilitation verstehen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_INFO.mp3`
- **Gesprochen:** „Die Erholung nach einer Hüftfraktur verläuft individuell. Ich kann typische Etappen erklären oder die fiktiven Spitalberichte von Ernst zusammenfassen.“
- **Chatbot-Text:** „Die Erholung nach einer Hüftfraktur verläuft individuell. Ich kann typische Etappen erklären oder die fiktiven Spitalberichte von Ernst zusammenfassen.“
- **Antwortmöglichkeiten:** „Wie verläuft die Rehabilitation normalerweise?“ -> `REL_INFO_STAGES`; „Was geschah bei Ernst im Spital?“ -> `REL_INFO_EPIC`; „Gemeinsame Journey ansehen“ -> `JOURNEY_ALL`; „Weitere Frage“ -> `REL_ASK`; „Zurück“ -> `REL_START`

### REL_INFO_STAGES — Typischer Therapieverlauf
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_INFO_STAGES.mp3`
- **Gesprochen:** „Viele Menschen werden nach der Operation zunächst beim Aufstehen, Gehen und im Alltag angeleitet. Anschliessend werden Ziele mit der Physiotherapie individuell überprüft. Ein fester Zeitplan passt nicht für alle.“
- **Chatbot-Text:** „Viele Menschen werden nach der Operation zunächst beim Aufstehen, Gehen und im Alltag angeleitet. Anschliessend werden Ziele mit der Physiotherapie individuell überprüft. Ein fester Zeitplan passt nicht für alle.“
- **Antwortmöglichkeiten:** „Ernsts Geschichte ansehen“ -> `JOURNEY_ALL`; „Frage für Physio vormerken“ -> `SUM_ADD_BALANCE`; „Zurück zu Informationen“ -> `REL_INFO`
- **Hinweis:** Nur allgemeine, nicht normative Phasen. Keine Versprechen über den Zeitpunkt der vollständigen Genesung.

### REL_INFO_EPIC — Fiktive Spitalgeschichte
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_INFO_EPIC.mp3`
- **Gesprochen:** „Ernst wurde nach seinem Sturz an der rechten Hüfte operiert. Während des Spitalaufenthalts übte er das Aufstehen und Gehen unter Anleitung. Seit dem zweiten November ist er wieder zu Hause.“
- **Chatbot-Text:** „Ernsts Geschichte: Sturz, Operation, erste Physiotherapie, Entlassung nach Hause. Alle Angaben sind fiktiv.“
- **Antwortmöglichkeiten:** „Was bedeutet die Operation?“ -> `KNOW_OP`; „Was steht im Entlassbrief?“ -> `KNOW_NEXT`; „Gemeinsame Journey“ -> `JOURNEY_ALL`; „Zurück zu Informationen“ -> `REL_INFO`
- **Quelle:** E01-E07 (Demo). Reale Angehörigenrechte wären später gesondert zu klären.

### REL_ASK — Individuelle Frage stellen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_ASK.mp3`
- **Gesprochen:** „Schreiben Sie Ihre Frage auf oder wählen Sie ein Beispiel. Die Antworten in dieser Demonstration sind vorbereitet.“
- **Chatbot-Text:** „Schreiben Sie Ihre Frage auf oder wählen Sie ein Beispiel. Die Antworten in dieser Demonstration sind vorbereitet.“
- **Antwortmöglichkeiten:** „Wie viel Unterstützung ist richtig?“ -> `SUM_ADD_BALANCE`; „Was tun nach einem Sturz?“ -> `REL_FALL`; „Meine Frage ist noch nicht dabei“ -> `REL_ASK_OTHER`; „Zurück“ -> `REL_HELP`
- **Wirkung:** Freies Texteingabefeld; Diktat über Android-Tastatur optional; kein Live-KI-Dienst.

### REL_ASK_OTHER — Frage noch nicht im Mock-up
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_ASK_OTHER.mp3`
- **Gesprochen:** „Diese Frage kann die Demonstration noch nicht selbstständig beantworten. Möchten Sie sie für den nächsten Termin festhalten?“
- **Chatbot-Text:** „Diese Frage kann die Demonstration noch nicht selbstständig beantworten. Möchten Sie sie für den nächsten Termin festhalten?“
- **Antwortmöglichkeiten:** „Frage festhalten“ -> `SUM_ADD_OTHER`; „Zurück zu Beispiel-Fragen“ -> `REL_ASK`
- **Hinweis:** Bei freier Texteingabe die Grenze zur simulierten KI klar machen.

### REL_STAIRS — Treppensteigen unterstützen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_STAIRS.mp3`
- **Gesprochen:** „Bei Treppen ist wichtig, dass Sie sich an die Anleitung der Physiotherapie halten. Ich kann ein Beispielvideo zeigen und Ihre offenen Fragen festhalten.“
- **Chatbot-Text:** „Bei Treppen ist wichtig, dass Sie sich an die Anleitung der Physiotherapie halten. Ich kann ein Beispielvideo zeigen und Ihre offenen Fragen festhalten.“
- **Antwortmöglichkeiten:** „Beispielvideo ansehen“ -> `REL_STAIRS_VIDEO`; „Frage vormerken“ -> `SUM_ADD_STAIRS`; „Zurück“ -> `REL_START`
- **Hinweis:** Keine allgemeingültige Schrittfolge als individuelle Anweisung ausgeben.

### REL_STAIRS_VIDEO — Video Treppenhilfe
- **Rolle:** `angehörige`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „Video: Unterstützung beim Treppensteigen – nur als Gesprächsgrundlage mit persönlicher Anleitung.“
- **Antwortmöglichkeiten:** „Frage vormerken“ -> `SUM_ADD_STAIRS`; „Zurück“ -> `REL_STAIRS`
- **Video/Medium:** `Documents/SMART/video/treppen_unterstuetzung.mp4`

### REL_BED — Unterstützung beim Aufstehen aus dem Bett
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_BED.mp3`
- **Gesprochen:** „Lassen Sie sich den für Ernst passenden Bewegungsablauf von der Physiotherapie zeigen. Unterstützung soll sicher sein und die Selbstständigkeit fördern.“
- **Chatbot-Text:** „Lassen Sie sich den für Ernst passenden Bewegungsablauf von der Physiotherapie zeigen. Unterstützung soll sicher sein und die Selbstständigkeit fördern.“
- **Antwortmöglichkeiten:** „Beispielvideo ansehen“ -> `REL_BED_VIDEO`; „Frage vormerken“ -> `SUM_ADD_BED`; „Zurück“ -> `REL_START`

### REL_BED_VIDEO — Video Aufstehen aus Bett
- **Rolle:** `angehörige`
- **MP3:** keine (Text-/Navigationsansicht)
- **Gesprochen:** —
- **Chatbot-Text:** „Video: Aufstehen aus dem Bett – fiktives Anschauungsmaterial. Befolgen Sie die individuellen therapeutischen Hinweise.“
- **Antwortmöglichkeiten:** „Frage vormerken“ -> `SUM_ADD_BED`; „Zurück“ -> `REL_BED`
- **Video/Medium:** `Documents/SMART/video/aufstehen_aus_bett.mp4`

### REL_FALL — Verhalten nach einem Sturz
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_FALL.mp3`
- **Gesprochen:** „Nach einem Sturz kommt es zuerst darauf an, ob Ernst verletzt ist. Versuchen Sie nicht, ihn ungeprüft hochzuheben. Bei Verdacht auf ernste Verletzung oder akuten Warnzeichen ist rasch medizinische Hilfe nötig.“
- **Chatbot-Text:** „Nach einem Sturz kommt es zuerst darauf an, ob Ernst verletzt ist. Versuchen Sie nicht, ihn ungeprüft hochzuheben. Bei Verdacht auf ernste Verletzung oder akuten Warnzeichen ist rasch medizinische Hilfe nötig.“
- **Antwortmöglichkeiten:** „Wann Hilfe holen?“ -> `REL_FALL_ALERT`; „Frage für Termin sammeln“ -> `SUM_ADD_FALL`; „Zurück“ -> `REL_START`

### REL_FALL_ALERT — Warnzeichen / Notfall
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_FALL_ALERT.mp3`
- **Gesprochen:** „Bei einer akuten Notfallsituation – etwa wenn Ernst bewusstlos ist oder schwer verletzt sein könnte – rufen Sie in der Schweiz 144. Bei Unsicherheit zur Versorgung sprechen Sie mit einer medizinischen Fachperson.“
- **Chatbot-Text:** „Bei einer akuten Notfallsituation – etwa wenn Ernst bewusstlos ist oder schwer verletzt sein könnte – rufen Sie in der Schweiz 144. Bei Unsicherheit zur Versorgung sprechen Sie mit einer medizinischen Fachperson.“
- **Antwortmöglichkeiten:** „Frage für Physio vormerken“ -> `SUM_ADD_FALL`; „Zurück“ -> `REL_START`
- **Hinweis:** Keine Hebetechniken, keine eigenmächtige Einschätzung von Frakturen.

### REL_MOOD_START — Angehörigen-Stimmung
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_MOOD_START.mp3`
- **Gesprochen:** „Wie geht es Ihnen selbst mit der neuen Situation? Sie dürfen die Frage auch überspringen.“
- **Chatbot-Text:** „Wie geht es Ihnen selbst mit der neuen Situation? Sie dürfen die Frage auch überspringen.“
- **Antwortmöglichkeiten:** „Ich fühle mich sicher“ -> `REL_MOOD_OK`; „Ich mache mir Sorgen“ -> `REL_MOOD_WORRY`; „Ich fühle mich überfordert“ -> `REL_MOOD_OVER`; „Überspringen“ -> `REL_START`

### REL_MOOD_OK — Angehörige: sicher
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_MOOD_OK.mp3`
- **Gesprochen:** „Danke. Sie können jederzeit eine neue Frage stellen oder etwas für den nächsten Termin notieren.“
- **Chatbot-Text:** „Danke. Sie können jederzeit eine neue Frage stellen oder etwas für den nächsten Termin notieren.“
- **Antwortmöglichkeiten:** „Quiz ausprobieren“ -> `QUIZ_1`; „Zurück“ -> `REL_START`
- **Wirkung:** Optional: Tagebuch Angehörige/Stimmung/zuversichtlich – nur nach Einwilligung.

### REL_MOOD_WORRY — Angehörige: Sorgen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_MOOD_WORRY.mp3`
- **Gesprochen:** „Das klingt belastend. Wir können festhalten, was Ihnen besonders Sorgen macht, damit Sie es mit der Physiotherapie besprechen können.“
- **Chatbot-Text:** „Das klingt belastend. Wir können festhalten, was Ihnen besonders Sorgen macht, damit Sie es mit der Physiotherapie besprechen können.“
- **Antwortmöglichkeiten:** „Sorge für Termin notieren“ -> `SUM_ADD_REL_WORRY`; „Ein Quiz ausprobieren“ -> `QUIZ_1`; „Nicht speichern“ -> `REL_START`
- **Wirkung:** Stimmung freiwillig; nur bei explizitem Speichern in Fragenliste übernehmen.

### REL_MOOD_OVER — Angehörige: Überforderung
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_REL_MOOD_OVER.mp3`
- **Gesprochen:** „Wenn die Unterstützung zu viel wird, ist es sinnvoll, auch über Ihre Entlastung zu sprechen. Soll ich diese Frage für den nächsten Termin vormerken?“
- **Chatbot-Text:** „Wenn die Unterstützung zu viel wird, ist es sinnvoll, auch über Ihre Entlastung zu sprechen. Soll ich diese Frage für den nächsten Termin vormerken?“
- **Antwortmöglichkeiten:** „Ja, vormerken“ -> `SUM_ADD_REL_OVER`; „Nein, danke“ -> `REL_START`
- **Wirkung:** Keine Diagnose; Terminfrage nur nach Zustimmung.

### QUIZ_1 — Quiz 1: alles abnehmen?
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_1.mp3`
- **Gesprochen:** „Ernst möchte selbst den Kaffee zubereiten. Sie haben Angst, dass er stürzt. Was wäre eine angemessene Reaktion – unter Beachtung seiner persönlichen Sicherheitsvorgaben?“
- **Chatbot-Text:** „Ernst möchte selbst den Kaffee zubereiten. Sie haben Angst, dass er stürzt. Was wäre eine angemessene Reaktion – unter Beachtung seiner persönlichen Sicherheitsvorgaben?“
- **Antwortmöglichkeiten:** „Ich verbiete es grundsätzlich.“ -> `QUIZ_1_TOO_MUCH`; „Wir prüfen gemeinsam, was sicher möglich ist.“ -> `QUIZ_1_BALANCED`; „Ich lasse ihn ungeprüft alles alleine machen.“ -> `QUIZ_1_TOO_LITTLE`

### QUIZ_1_TOO_MUCH — Quiz 1: zu viel Hilfe
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_1_TOO_MUCH.mp3`
- **Gesprochen:** „Das könnte zu viel Hilfe sein. Wenn etwas sicher und freigegeben ist, kann eigene Aktivität wichtig für die Selbstständigkeit sein.“
- **Chatbot-Text:** „Das könnte zu viel Hilfe sein. Wenn etwas sicher und freigegeben ist, kann eigene Aktivität wichtig für die Selbstständigkeit sein.“
- **Antwortmöglichkeiten:** „Nächste Frage“ -> `QUIZ_2`; „Zurück“ -> `REL_START`

### QUIZ_1_BALANCED — Quiz 1: angemessene Hilfe
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_1_BALANCED.mp3`
- **Gesprochen:** „Das ist im Beispiel ein guter Mittelweg: mögliche Selbstständigkeit erhalten und Sicherheitsvorgaben beachten.“
- **Chatbot-Text:** „Das ist im Beispiel ein guter Mittelweg: mögliche Selbstständigkeit erhalten und Sicherheitsvorgaben beachten.“
- **Antwortmöglichkeiten:** „Nächste Frage“ -> `QUIZ_2`; „Zurück“ -> `REL_START`

### QUIZ_1_TOO_LITTLE — Quiz 1: zu wenig Hilfe
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_1_TOO_LITTLE.mp3`
- **Gesprochen:** „Das könnte zu wenig Unterstützung sein. Sicherheit und individuelle Bewegungsvorgaben sollten zuerst geklärt werden.“
- **Chatbot-Text:** „Das könnte zu wenig Unterstützung sein. Sicherheit und individuelle Bewegungsvorgaben sollten zuerst geklärt werden.“
- **Antwortmöglichkeiten:** „Nächste Frage“ -> `QUIZ_2`; „Zurück“ -> `REL_START`

### QUIZ_2 — Quiz 2: abendlicher Spaziergang
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_2.mp3`
- **Gesprochen:** „Ernst möchte abends allein spazieren, ohne Telefon. Was wäre hier am sinnvollsten?“
- **Chatbot-Text:** „Ernst möchte abends allein spazieren, ohne Telefon. Was wäre hier am sinnvollsten?“
- **Antwortmöglichkeiten:** „Ich sage aus Prinzip immer Nein.“ -> `QUIZ_2_TOO_MUCH`; „Wir besprechen eine sichere, freigegebene Alternative.“ -> `QUIZ_2_BALANCED`; „Ich lasse ihn ohne Rückfrage gehen.“ -> `QUIZ_2_TOO_LITTLE`

### QUIZ_2_TOO_MUCH — Quiz 2: zu viel Einschränkung
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_2_TOO_MUCH.mp3`
- **Gesprochen:** „Ein pauschales Verbot kann die Selbstständigkeit unnötig einschränken. Prüfen Sie gemeinsam, welche sichere Alternative zum individuellen Stand passt.“
- **Chatbot-Text:** „Ein pauschales Verbot kann die Selbstständigkeit unnötig einschränken. Prüfen Sie gemeinsam, welche sichere Alternative zum individuellen Stand passt.“
- **Antwortmöglichkeiten:** „Nächste Frage“ -> `QUIZ_3`; „Zurück“ -> `REL_START`

### QUIZ_2_BALANCED — Quiz 2: sicher abwägen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_2_BALANCED.mp3`
- **Gesprochen:** „Im Beispiel ist das eine ausgewogene Lösung: Wünsche ernst nehmen und Risiken sowie persönliche Vorgaben gemeinsam prüfen.“
- **Chatbot-Text:** „Im Beispiel ist das eine ausgewogene Lösung: Wünsche ernst nehmen und Risiken sowie persönliche Vorgaben gemeinsam prüfen.“
- **Antwortmöglichkeiten:** „Nächste Frage“ -> `QUIZ_3`; „Zurück“ -> `REL_START`

### QUIZ_2_TOO_LITTLE — Quiz 2: Risiko unterschätzt
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_2_TOO_LITTLE.mp3`
- **Gesprochen:** „Das könnte zu wenig Unterstützung sein. Nach der Hüftfraktur sollte die geplante Aktivität zur individuellen Sicherheitssituation passen.“
- **Chatbot-Text:** „Das könnte zu wenig Unterstützung sein. Nach der Hüftfraktur sollte die geplante Aktivität zur individuellen Sicherheitssituation passen.“
- **Antwortmöglichkeiten:** „Nächste Frage“ -> `QUIZ_3`; „Zurück“ -> `REL_START`

### QUIZ_3 — Quiz 3: wer bestimmt das Tempo?
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_3.mp3`
- **Gesprochen:** „Ernst benötigt mehr Zeit beim Anziehen. Welche Reaktion unterstützt ihn am besten?“
- **Chatbot-Text:** „Ernst benötigt mehr Zeit beim Anziehen. Welche Reaktion unterstützt ihn am besten?“
- **Antwortmöglichkeiten:** „Ich übernehme sofort alles.“ -> `QUIZ_3_TOO_MUCH`; „Ich frage, wobei er Unterstützung möchte.“ -> `QUIZ_3_BALANCED`; „Ich lasse ihn auch bei erkennbarer Gefahr allein.“ -> `QUIZ_3_TOO_LITTLE`

### QUIZ_3_TOO_MUCH — Quiz 3: zu viel Hilfe
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_3_TOO_MUCH.mp3`
- **Gesprochen:** „Gut gemeinte Hilfe kann Eigenständigkeit verringern. Fragen Sie möglichst zuerst, was Ernst selbst machen möchte und sicher kann.“
- **Chatbot-Text:** „Gut gemeinte Hilfe kann Eigenständigkeit verringern. Fragen Sie möglichst zuerst, was Ernst selbst machen möchte und sicher kann.“
- **Antwortmöglichkeiten:** „Quiz abschliessen“ -> `QUIZ_END`

### QUIZ_3_BALANCED — Quiz 3: Selbstständigkeit unterstützen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_3_BALANCED.mp3`
- **Gesprochen:** „Das ist ein guter Ansatz: Wünsche und Sicherheit beachten, ohne unnötig alles abzunehmen.“
- **Chatbot-Text:** „Das ist ein guter Ansatz: Wünsche und Sicherheit beachten, ohne unnötig alles abzunehmen.“
- **Antwortmöglichkeiten:** „Quiz abschliessen“ -> `QUIZ_END`

### QUIZ_3_TOO_LITTLE — Quiz 3: zu wenig Unterstützung
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_3_TOO_LITTLE.mp3`
- **Gesprochen:** „Selbstständigkeit ist wichtig, aber erkennbare Gefahren brauchen Aufmerksamkeit und gegebenenfalls Unterstützung.“
- **Chatbot-Text:** „Selbstständigkeit ist wichtig, aber erkennbare Gefahren brauchen Aufmerksamkeit und gegebenenfalls Unterstützung.“
- **Antwortmöglichkeiten:** „Quiz abschliessen“ -> `QUIZ_END`

### QUIZ_END — Quiz abgeschlossen
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_QUIZ_END.mp3`
- **Gesprochen:** „Danke fürs Mitmachen. Es geht nicht um perfekte Antworten, sondern um ein gutes Gleichgewicht zwischen Sicherheit und Selbstständigkeit.“
- **Chatbot-Text:** „Danke fürs Mitmachen. Es geht nicht um perfekte Antworten, sondern um ein gutes Gleichgewicht zwischen Sicherheit und Selbstständigkeit.“
- **Antwortmöglichkeiten:** „Frage für Physio sammeln“ -> `SUM_ADD_BALANCE`; „Zum Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Optional Quiz-Ergebnis auf Demogerät. Keine medizinische oder psychologische Bewertung.

### PRO_OPTIN — Erlaubnis zur proaktiven Ansprache
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_PRO_OPTIN.mp3`
- **Gesprochen:** „Darf SMARTcoach Sie gelegentlich ansprechen, während die Anwendung geöffnet ist? Sie können die Funktion jederzeit wieder ausschalten.“
- **Chatbot-Text:** „Wenn Sie die Aktive Begleitung einschalten, darf SMARTcoach von sich aus fragen, wie es Ihnen geht, an Uebungen aus Ihrem Plan erinnern und passende Aktivitaeten vorschlagen. Er spricht Sie nur an, wenn SMARTcoach geoeffnet ist. Moechten Sie das erlauben?“
- **Antwortmöglichkeiten:** „Ja, aktive Begleitung einschalten“ -> `PRO_ON`; „Nein, ausgeschaltet lassen“ -> `PRO_OFF`
- **Hinweis:** Standardwert AUS. Zugriff vom HOME-Schalter ohne Umweg ueber Einstellungen. Nicht mit Android-Hintergrundbenachrichtigungen gleichsetzen. Die Vorfuehrung darf kein scheinbar frei handelndes KI-System vortaeuschen.

### PRO_ON — Proaktivität eingeschaltet
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_PRO_ON.mp3`
- **Gesprochen:** „Danke. Ich melde mich nur in der geöffneten Anwendung. Wenn Sie Ruhe möchten, können Sie die Ansprache ausschalten oder jederzeit beenden.“
- **Chatbot-Text:** „Aktive Begleitung ist EIN. Ich darf gelegentlich nachfragen, an Ihre vorgesehenen Uebungen erinnern und Aktivitaeten vorschlagen. Sie koennen die Begleitung jederzeit auf der Uebersicht ausschalten oder auf Beenden tippen.“
- **Antwortmöglichkeiten:** „Beispielfrage zeigen“ -> `PRO_CHECK`; „Zurueck zur Uebersicht“ -> `HOME`
- **Wirkung:** Einstellung proaktiv=true lokal speichern; HOME zeigt EIN. Keine automatische MP3 unmittelbar durch Aktivieren erforderlich.

### PRO_OFF — Proaktivität ausgeschaltet
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_PRO_OFF.mp3`
- **Gesprochen:** „In Ordnung. Ich spreche Sie nicht von mir aus an. Sie können jederzeit selbst einen Dialog beginnen.“
- **Chatbot-Text:** „In Ordnung. Ich spreche Sie nicht von mir aus an. Sie können jederzeit selbst einen Dialog beginnen.“
- **Antwortmöglichkeiten:** „Zum Hauptmenü“ -> `HOME`
- **Wirkung:** Einstellung proaktiv=false lokal speichern; alle noch wartenden proaktiven Impulse abbrechen; HOME zeigt AUS. Nutzerinitiierte Dialoge bleiben moeglich.

### PRO_CHECK — Proaktive Frage zum Befinden
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PRO_CHECK.mp3`
- **Gesprochen:** „Guten Tag, Ernst. Wie geht es Ihnen heute? Möchten Sie mir etwas erzählen oder lieber in Ruhe gelassen werden?“
- **Chatbot-Text:** „Guten Tag, Ernst. Wie geht es Ihnen heute? Möchten Sie mir etwas erzählen oder lieber in Ruhe gelassen werden?“
- **Antwortmöglichkeiten:** „Welche Übung steht an?“ -> `PRO_EXERCISE`; „Ich habe heute etwas gemacht“ -> `PAT_LOG_START`; „Ich möchte einen Vorschlag“ -> `PRO_WALK`; „Bitte heute nicht mehr fragen“ -> `PRO_TODAY_QUIET`
- **Hinweis:** Nur bei sichtbarer PWA, wenn Einwilligung aktiv; keine Unterbrechung eines laufenden Gesprächs. Im ersten Grundgeruest darf dieser Dialog nur ueber den Demo-Button gestartet werden; kein echter Zeit-Ausloeser.

### PRO_EXERCISE — Erinnerung an Übungen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PRO_EXERCISE.mp3`
- **Gesprochen:** „In Ihrem fiktiven Plan sind Übungen für zu Hause vorgesehen. Möchten Sie die Anleitung noch einmal ansehen oder sagen, was Sie bereits gemacht haben?“
- **Chatbot-Text:** „In Ihrem fiktiven Plan sind Übungen für zu Hause vorgesehen. Möchten Sie die Anleitung noch einmal ansehen oder sagen, was Sie bereits gemacht haben?“
- **Antwortmöglichkeiten:** „Video zeigen“ -> `PAT_VIDEO`; „Schon gemacht“ -> `PAT_LOG_EX_SAVE`; „Nicht jetzt“ -> `PRO_TODAY_QUIET`
- **Hinweis:** Vorschlag nur aus Demo-Therapieplan und Tagebuch; keine automatische neue Verordnung.

### PRO_WALK — Spaziergang bei Demo-Wetter
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PRO_WALK.mp3`
- **Gesprochen:** „Für die Demonstration ist das Wetter gerade trocken. Wäre ein kurzer Aufenthalt draussen eine Möglichkeit, sofern das für Sie freigegeben und sicher ist?“
- **Chatbot-Text:** „Für die Demonstration ist das Wetter gerade trocken. Wäre ein kurzer Aufenthalt draussen eine Möglichkeit, sofern das für Sie freigegeben und sicher ist?“
- **Antwortmöglichkeiten:** „Ich war bereits unterwegs“ -> `PAT_WALK_DURATION`; „Ich bespreche es erst“ -> `SUM_ADD_WALK`; „Nein, danke“ -> `PRO_TODAY_QUIET`
- **Hinweis:** Wetter im Mock-up simuliert, nicht als echte Vorhersage kennzeichnen.

### PRO_TODAY_QUIET — Heute in Ruhe lassen
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_PRO_TODAY_QUIET.mp3`
- **Gesprochen:** „Selbstverständlich. Ich lasse Sie jetzt in Ruhe. Sie können mich jederzeit selbst öffnen.“
- **Chatbot-Text:** „Selbstverständlich. Ich lasse Sie jetzt in Ruhe. Sie können mich jederzeit selbst öffnen.“
- **Antwortmöglichkeiten:** „Zum Ruhebildschirm“ -> `STOP`; „Zum Patientenmenü“ -> `PAT_START`
- **Wirkung:** Proaktives Nachfragen für die aktuelle Demo-Sitzung pausieren.

### SUM_START — Vorbereitung auf den Physiotermin
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_SUM_START.mp3`
- **Gesprochen:** „Hier sammeln wir Fragen und Beobachtungen für den nächsten Physiotherapietermin am zehnten November. Möchten Sie die bisherige Liste ansehen?“
- **Chatbot-Text:** „Hier sammeln wir Fragen und Beobachtungen für den nächsten Physiotherapietermin am zehnten November. Möchten Sie die bisherige Liste ansehen?“
- **Antwortmöglichkeiten:** „Gesammelte Fragen ansehen“ -> `SUM_OVERVIEW`; „Frage zu Übungen vormerken“ -> `SUM_ADD_EXERCISE`; „Frage zur Unterstützung vormerken“ -> `SUM_ADD_BALANCE`; „Zum Hauptmenü“ -> `HOME`

### SUM_ADD_EXERCISE — Frage zu Übungen gespeichert
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_EXERCISE.mp3`
- **Gesprochen:** „Ich habe die Frage notiert: Welche Übungen sind für Ernst im Moment geeignet, und woran erkennt er, ob er sie richtig ausführt?“
- **Chatbot-Text:** „Ich habe die Frage notiert: Welche Übungen sind für Ernst im Moment geeignet, und woran erkennt er, ob er sie richtig ausführt?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Zurück zum Patientenmenü“ -> `PAT_START`
- **Wirkung:** Terminfokus: Übungen und persönliche Anleitung hinzufügen; Duplikate vermeiden.

### SUM_ADD_PAIN — Schmerzfrage gespeichert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_PAIN.mp3`
- **Gesprochen:** „Ich habe notiert: Welche Schmerzen sind im aktuellen Verlauf zu erwarten, und bei welchen Veränderungen sollte sich Ernst früher melden?“
- **Chatbot-Text:** „Ich habe notiert: Welche Schmerzen sind im aktuellen Verlauf zu erwarten, und bei welchen Veränderungen sollte sich Ernst früher melden?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Zurück“ -> `PAT_START`
- **Wirkung:** Terminfokus: Schmerzfrage hinzufügen; keine medizinische Entwarnung.

### SUM_ADD_FEAR — Unsicherheit gespeichert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_FEAR.mp3`
- **Gesprochen:** „Ich habe notiert, dass Ernst sich unsicher fühlt und das Thema Sturzangst besprechen möchte.“
- **Chatbot-Text:** „Ich habe notiert, dass Ernst sich unsicher fühlt und das Thema Sturzangst besprechen möchte.“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Zurück“ -> `PAT_START`
- **Wirkung:** Terminfokus: Sturzangst; freiwillig dokumentiert.

### SUM_ADD_OTHER — Eigene Frage als Platzhalter
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_OTHER.mp3`
- **Gesprochen:** „Ich habe einen Platzhalter für Ihre Frage angelegt. Im Mock-up kann die interviewende Person den Wortlaut später ergänzen.“
- **Chatbot-Text:** „Ich habe einen Platzhalter für Ihre Frage angelegt. Im Mock-up kann die interviewende Person den Wortlaut später ergänzen.“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Zurück zum Chat“ -> `PAT_CHAT`
- **Wirkung:** Terminfokus: Freitext-Frage speichern, falls eingegeben; andernfalls Demo-Platzhalter.

### SUM_ADD_STAIRS — Frage zu Treppen gespeichert
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_STAIRS.mp3`
- **Gesprochen:** „Ich habe notiert: Wie kann Anna Ernst bei den fünf Eingangsstufen entsprechend seinen persönlichen Vorgaben unterstützen?“
- **Chatbot-Text:** „Ich habe notiert: Wie kann Anna Ernst bei den fünf Eingangsstufen entsprechend seinen persönlichen Vorgaben unterstützen?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Terminfokus: Treppenunterstützung hinzufügen.

### SUM_ADD_BED — Frage zum Aufstehen gespeichert
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_BED.mp3`
- **Gesprochen:** „Ich habe notiert: Welcher Bewegungsablauf beim Aufstehen aus dem Bett ist für Ernst geeignet, und wie kann Anna helfen?“
- **Chatbot-Text:** „Ich habe notiert: Welcher Bewegungsablauf beim Aufstehen aus dem Bett ist für Ernst geeignet, und wie kann Anna helfen?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Terminfokus: Betttransfer hinzufügen.

### SUM_ADD_FALL — Frage zu Sturz gespeichert
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_FALL.mp3`
- **Gesprochen:** „Ich habe notiert: Was sollen Ernst und Anna nach einem erneuten Sturz tun, und wann ist sofort medizinische Hilfe nötig?“
- **Chatbot-Text:** „Ich habe notiert: Was sollen Ernst und Anna nach einem erneuten Sturz tun, und wann ist sofort medizinische Hilfe nötig?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Terminfokus: Verhalten nach Sturz und Kontaktplan hinzufügen.

### SUM_ADD_REL_WORRY — Sorge der Angehörigen gespeichert
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_REL_WORRY.mp3`
- **Gesprochen:** „Ich habe notiert, dass Anna sich um Ernsts Sicherheit zu Hause sorgt und darüber sprechen möchte.“
- **Chatbot-Text:** „Ich habe notiert, dass Anna sich um Ernsts Sicherheit zu Hause sorgt und darüber sprechen möchte.“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Terminfokus: Angehörigensorge. Nur mit Zustimmung der Angehörigen.

### SUM_ADD_REL_OVER — Überforderung der Angehörigen gespeichert
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_REL_OVER.mp3`
- **Gesprochen:** „Ich habe notiert, dass Anna Möglichkeiten für Unterstützung und Entlastung besprechen möchte.“
- **Chatbot-Text:** „Ich habe notiert, dass Anna Möglichkeiten für Unterstützung und Entlastung besprechen möchte.“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Terminfokus: Entlastung Angehörige. Nur mit Zustimmung.

### SUM_ADD_BALANCE — Frage zu angemessener Hilfe gespeichert
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_BALANCE.mp3`
- **Gesprochen:** „Ich habe die Frage notiert: Welche Aufgaben kann Ernst sicher selbstständig übernehmen, und wo braucht er noch Begleitung?“
- **Chatbot-Text:** „Ich habe die Frage notiert: Welche Aufgaben kann Ernst sicher selbstständig übernehmen, und wo braucht er noch Begleitung?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Angehörigenmenü“ -> `REL_START`
- **Wirkung:** Terminfokus: Balance zwischen Hilfe und Selbstständigkeit.

### SUM_ADD_WALK — Frage zu Spaziergängen gespeichert
- **Rolle:** `patient`
- **MP3:** `Documents/SMART/audio/SC_SUM_ADD_WALK.mp3`
- **Gesprochen:** „Ich habe notiert: Unter welchen Bedingungen ist ein Spaziergang draussen für Ernst derzeit geeignet?“
- **Chatbot-Text:** „Ich habe notiert: Unter welchen Bedingungen ist ein Spaziergang draussen für Ernst derzeit geeignet?“
- **Antwortmöglichkeiten:** „Fragenübersicht“ -> `SUM_OVERVIEW`; „Zum Patientenmenü“ -> `PAT_START`
- **Wirkung:** Terminfokus: Aktivität draussen hinzufügen.

### SUM_OVERVIEW — Zusammenfassung für Physio
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_SUM_OVERVIEW.mp3`
- **Gesprochen:** „Hier stehen Ihre ausgewählten Fragen, Aktivitäten und Sorgen für das nächste Gespräch. Sie entscheiden, was Sie der Physiotherapie zeigen möchten.“
- **Chatbot-Text:** „Hier stehen Ihre ausgewählten Fragen, Aktivitäten und Sorgen für das nächste Gespräch. Sie entscheiden, was Sie der Physiotherapie zeigen möchten.“
- **Antwortmöglichkeiten:** „Zurück zur Übersicht“ -> `HOME`; „Noch eine Frage aufnehmen“ -> `SUM_START`
- **Wirkung:** Nur freiwillig gespeicherte Fragen und Einträge zeigen. Mock-up: auf Gerät, ohne automatische Datenübertragung.


### KNOW_TODAY - Heute im Überblick
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_TODAY.mp3` (optional)
- **Gesprochen:** `Heute ist in der Demonstration der 6. November. Der nächste Physiotherapietermin ist für den 10. November vorgesehen. Ich kann Ihnen auch zeigen, was laut den fiktiven Unterlagen im Spital gemacht wurde.`
- **Chatbot-Text:** `Ihr Stand heute: seit dem 2. November zu Hause. Nächste Physiotherapie am 10. November. Offen: Fragen zu Übungen und zu den Eingangsstufen.`
- **Antwortmöglichkeiten:** `Was ist bisher passiert?` -> `KNOW_RECAP`; `Was steht als Nächstes an?` -> `KNOW_NEXT`; `Was bedeutet mein Bericht?` -> `KNOW_OVERVIEW`; `Eine Frage festhalten` -> `SUM_START`.
- **Quelle:** E06, E07, L01, L02, Q01; keine automatische medizinische Bewertung.

### KNOW_OVERVIEW - Meine Berichte, erklärt
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_OVERVIEW.mp3` (optional)
- **Gesprochen:** `Aus den fiktiven Spital- und Therapieberichten kann ich Ihnen die wichtigsten Informationen in einfacher Sprache zusammenfassen. Welches Thema interessiert Sie?`
- **Chatbot-Text:** `Berichte in einfachen Worten: Was wurde behandelt? Was haben wir im Spital geübt? Was ist für zu Hause dokumentiert?`
- **Antwortmöglichkeiten:** `Operation erklären` -> `KNOW_OP`; `Wichtig für zu Hause` -> `KNOW_NEXT`; `Woher kommt die Information?` -> `KNOW_SOURCE_OP`; `Was ist bisher passiert?` -> `KNOW_RECAP`.
- **Hinweis:** Nur statische Demo-Dokumente E01-E08; keine echte EPIC-Abfrage.

### KNOW_OP - Was wurde operiert?
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_OP.mp3` (optional)
- **Gesprochen:** `Im fiktiven Operationsbericht vom 27. Oktober steht, dass der gebrochene obere Oberschenkelknochen rechts mit einem Nagel im Knochen und Schrauben stabilisiert wurde. Ich kann den Fachbegriff erklären.`
- **Chatbot-Text:** `Operiert am 27. Oktober: Stabilisierung des hüftnahen Bruchs rechts mit Nagel und Schrauben. Quelle: fiktiver Operationsbericht E02.`
- **Antwortmöglichkeiten:** `Was ist ein Marknagel?` -> `KNOW_TERMS`; `Quelle ansehen` -> `KNOW_SOURCE_OP`; `Was heisst das für mich?` -> `KNOW_NEXT`; `Übersicht` -> `HOME`.
- **Quelle:** E02. **Keine** aus der Operation abgeleitete automatische Belastungsfreigabe.

### KNOW_TERMS - Medizinische Begriffe verstehen
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_TERMS.mp3` (optional)
- **Gesprochen:** `Ein Marknagel ist ein Metallstift, der im Innern eines Knochens eingesetzt wird, um die Knochenbruchstelle zu stabilisieren. Wie stark Ernst das Bein belasten darf, wird dadurch nicht automatisch festgelegt; dafür ist sein individueller Behandlungsplan wichtig.`
- **Chatbot-Text:** `Marknagel: Metallstift im Innern des Knochens zur Stabilisierung. Welche Belastung erlaubt ist, steht im persönlichen Plan.`
- **Antwortmöglichkeiten:** `Persönlichen Plan zeigen` -> `KNOW_NEXT`; `Originalquelle` -> `KNOW_SOURCE_OP`; `Frage für Physio notieren` -> `SUM_ADD_EXERCISE`; `Übersicht` -> `HOME`.
- **Quelle:** E02/E03 (Demo); medizinische Inhalte vor einem echten Einsatz fachlich prüfen.

### KNOW_RECAP - Was bisher geschah
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_RECAP.mp3` (optional)
- **Gesprochen:** `Am 26. Oktober ist Ernst gestürzt. Am 27. Oktober wurde seine rechte Hüfte operiert. Im Spital hat er das Aufstehen und Gehen unter Anleitung geübt. Seit dem 2. November ist er wieder zu Hause. Sie können jeden Abschnitt auf dem Weg anklicken und nachfragen.`
- **Chatbot-Text:** `Sturz 26.10. -> Operation 27.10. -> Üben im Spital -> Austritt 02.11. -> Heute 06.11. (alles fiktive Beispieldaten).`
- **Antwortmöglichkeiten:** `Weg ansehen` -> `JOURNEY_ALL`; `Operation erklären` -> `KNOW_OP`; `Nächste Schritte` -> `KNOW_NEXT`; `Zur Übersicht` -> `HOME`.
- **Quelle:** E01, E02, E04, E06, L01, L02.

### KNOW_NEXT - Was jetzt zu Hause wichtig ist
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_NEXT.mp3` (optional)
- **Gesprochen:** `Im fiktiven Entlassbrief ist die weitere Physiotherapie vorgesehen. Der nächste Termin ist am 10. November. Welche Übungen und Belastungen im Einzelnen passen, richtet sich nach dem persönlichen, noch zu validierenden Behandlungsplan. Haben Sie dazu Fragen?`
- **Chatbot-Text:** `Zu Hause: nach individuellen Abmachungen bewegen und üben. Nächster Physiotherapietermin: 10.11.2026. Bei Unsicherheit persönlichen Plan und Fachperson konsultieren.`
- **Antwortmöglichkeiten:** `Quelle: Entlassbrief` -> `KNOW_SOURCE_DISCHARGE`; `Übungen ansehen` -> `PAT_EXPLAIN`; `Fragen sammeln` -> `SUM_START`; `Übersicht` -> `HOME`.
- **Quelle:** E03, E06, E07; **keine** automatisch erzeugten Therapieanweisungen.

### KNOW_SOURCE_OP - Woher kommt das? Operation
- **Rolle:** `alle`
- **MP3:** keine (Quellenkarte)
- **Gesprochen:** -
- **Chatbot-Text:** `Demo-Quelle: Operationsbericht E02, 27.10.2026. Kurztext: Stabilisierung einer pertrochantaeren Femurfraktur rechts mit intramedullaerem Nagel. Das ist ein erfundener Beispielbericht, kein aus EPIC eingelesener Originaltext.`
- **Antwortmöglichkeiten:** `Einfach erklären` -> `KNOW_OP`; `Begriff erklären` -> `KNOW_TERMS`; `Übersicht` -> `HOME`.

### KNOW_SOURCE_DISCHARGE - Woher kommt das? Austritt
- **Rolle:** `alle`
- **MP3:** keine (Quellenkarte)
- **Gesprochen:** -
- **Chatbot-Text:** `Demo-Quelle: Entlassbrief E06 vom 02.11.2026 und Terminliste E07. Enthalten: Weiterbetreuung zu Hause und Physiotherapie am 10.11.2026. Die individuellen Bewegungsangaben sind Demo-Platzhalter; keine echten Spitalinformationen.`
- **Antwortmöglichkeiten:** `Einfach erklären` -> `KNOW_NEXT`; `Frage notieren` -> `SUM_START`; `Übersicht` -> `HOME`.

### KNOW_CONTEXT_ASK - Meine Frage an SMARTcoach
- **Rolle:** `alle`
- **MP3:** `Documents/SMART/audio/SC_KNOW_CONTEXT_ASK.mp3` (optional)
- **Gesprochen:** `Sie können eine vorbereitete Frage auswaehlen oder einen Text eingeben. Ich zeige Ihnen in dieser Demo die vorbereiteten Antworten. Was möchten Sie wissen?`
- **Chatbot-Text:** `Worüber möchten Sie etwas wissen?`
- **Antwortmöglichkeiten:** `Was wurde bei mir operiert?` -> `KNOW_OP`; `Was steht als Nächstes an?` -> `KNOW_NEXT`; `Wie können Angehörige helfen?` -> `REL_HELP`; `Andere Frage eingeben` -> `PAT_CHAT_UNMATCHED`.
- **Hinweis:** Freie Spracheingabe ist noch **keine** echte medizinische Dialog-KI. Android-Diktat später prüfen.

### KNOW_REL_PERSPECTIVE - Was bedeutet das für Angehörige?
- **Rolle:** `angehörige`
- **MP3:** `Documents/SMART/audio/SC_KNOW_REL_PERSPECTIVE.mp3` (optional)
- **Gesprochen:** `Sie sehen den gleichen Weg von Ernst. In Ihrer Ansicht finden Sie zusaetzlich Hinweise zur Unterstützung zu Hause und einen Platz für Ihre eigenen Fragen und Sorgen. Sie entscheiden, was Sie davon teilen möchten.`
- **Chatbot-Text:** `Gleiche Journey, andere Fragen: Wie helfe ich angemessen? Woher kommen die Informationen? Was möchte ich beim Termin besprechen?`
- **Antwortmöglichkeiten:** `Alltagshilfe` -> `REL_HELP`; `Berichte erklären` -> `KNOW_OVERVIEW`; `Meine Sorgen` -> `REL_MOOD_START`; `Gemeinsamer Weg` -> `JOURNEY_ALL`.
- **Hinweis:** Rollenspezifische Einträge nur nach Bestätigung in gemeinsame Terminliste übernehmen.


## 4. Regeln für die Dialog-Engine des späteren Mock-ups

1. Sprech- und Chat-Inhalt erscheinen in derselben Dialogrunde. Audio darf nur nach erlaubter Nutzerinteraktion starten und muss beim Stopp/Screenwechsel beendet werden.
2. Buttons müssen grosse Touchflächen haben. Mehr als vier bis fünf Auswahlmöglichkeiten sollten bei Bedarf in gut lesbare Gruppen oder eine scrollbare Ansicht aufgeteilt werden.
3. Die vorgefertigte Antwort darf nicht den Eindruck erwecken, dass SMARTcoach frei auf jeden eingegebenen Satz reagieren kann.
4. Fehlt eine MP3 oder Video-Datei, soll die App funktionsfähig bleiben, den Text zeigen und eine geeignete Nachwahl ermöglichen.
5. Jeder Eintrag bekommt ein Demo-Datum, Rolle, Kategorie und Quellknoten-ID; dadurch kann er später in Tagebuch und Journey wiedergefunden werden.
6. Bei `STOP` werden Dialogzustand, Wiedergabe und laufende Eingabe beendet. Bestätigte Demo-Einträge bleiben erhalten, solange sie nicht explizit zurückgesetzt werden.
7. Personenbezogene Angaben und angebliche EPIC-Dokumente sind Demo-Fiktion. Sie dürfen nicht unklar als echte Spitalakte erscheinen.
8. Sicherheitskritische Inhalte (Sturz, Schmerzen, Belastung, Mobilisation) müssen vor einem möglichen realen Einsatz klinisch geprüft und individualisiert werden.

## 5. Verzeichnisvorschlag (nur lokale Medien)

```text
Documents/SMART/
  audio/SC_PAT_START.mp3
  audio/SC_REL_START.mp3
  audio/... (weitere SC_<ID>.mp3)
  video/sicher_aufstehen.mp4
  video/treppen_unterstützung.mp4
  video/aufstehen_aus_bett.mp4
  images/luzern_01.jpg
  images/luzern_02.jpg
```

**Hinweis:** Die PWA darf diese Dateien nicht als GitHub-Pages-URLs behandeln. Der Zugriff erfolgt nach bewusster lokaler Auswahl/Import durch die nutzende Person. Die konkrete Berechtigungspersistenz ist auf Android zu testen.

## 6. Noch offene Inhalte

- Welche Aussagen sollen tatsächlich als MP3 eingesprochen werden und welche bleiben nur als Text?
- Welche lokalen Videos sind vorhanden, und unter welchen Dateinamen/Unterordnern?
- Werden in der Demo Ereignisse live nacheinander gespielt oder kann die interviewende Person verschiedene Startsituationen zurücksetzen?
- Wie sollen Angehörigenbeiträge und Patienteneinträge in der gemeinsamen Journey differenziert angezeigt werden?
- Welcher sprachliche Stil (Du/Sie, Humorgrad, Schweizer Hochdeutsch) gefällt den älteren Testpersonen?
- Wie gehen wir mit nicht vorgefertigter Spracheingabe um (Hinweis, Auswahlvorschläge oder Moderator-Steuerung)?

**Versionsprinzip:** IDs bleiben stabil. Texte, Namen, Auswahlmöglichkeiten, Medientitel und Demo-Szenario können später über separate Inhaltsdateien geändert werden, ohne das Grundgerüst umzuschreiben.
