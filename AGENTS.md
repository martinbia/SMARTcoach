# SMARTcoach – Arbeitsregeln für Codex

**Status:** Verbindliche Arbeitsregel ab 09.11.2026.

## Geltung und Projektgrundlage

- Vor Änderungen den aktuellen Stand von `README.md`, `docs/GUI-DESIGN.md` und die betroffenen Spezifikations-/Testdokumente lesen. Bestehende Arbeitsregeln und beschlossene Gestaltungsanforderungen bleiben gültig.
- Die ausdrücklich freigegebenen Entwürfe unter `docs/design/` und vorhandene Screenshots unter `docs/screenshots/` als **Vergleichsmaterial** verwenden; eine Datei im Screenshot-Ordner ist aber nicht allein deshalb automatisch freigegeben.
- Die Anwendung nutzt nur fiktive Inhalte. Keine echten Patientendaten, medizinischen Anordnungen oder unfreigegebenen Medien erfinden oder veröffentlichen.
- Ein neuer Commit oder eine Datei mit Anweisungen startet keinen Codex-Auftrag automatisch.

## GUI-Bestandsschutz (GUI-Freeze) – verbindlich ab 09.11.2026

**Grundregel:** Die bestehende GUI ist bei Funktionsentwicklungen zu erhalten. Nur der im aktuellen Auftrag **ausdrücklich bezeichnete GUI-Bereich** darf soweit nötig verändert oder ergänzt werden. Für alle anderen Ansichten und Elemente gilt Bestandsschutz – auch dann, wenn Codex eine Änderung für eine gestalterische Verbesserung halten würde.

### Ohne ausdrückliche GUI-Freigabe untersagt

- Bestehende Positionen, Grössen, Abstände, Ränder, Farben, Schriftarten/-grössen, Icons, Bilder, Animationen, Beschriftungen oder die Informationshierarchie ändern.
- Navigation, Menüs, Buttons, Kopf-/Fusszeilen, responsive Layouts oder andere nicht beauftragte Ansichten umgestalten.
- Globale CSS-Anpassungen, Design-Refactoring, Vereinheitlichungen oder sonstige „Nebenbei-Optimierungen“ durchführen, wenn sie das Erscheinungsbild ausserhalb des Auftrags verändern.
- Freigegebene Designreferenzen oder Vergleichs-Screenshots eigenmächtig ersetzen oder neu als Sollzustand festlegen.

### Zulässiger Änderungsumfang

- Neue Funktionen im **beauftragten Bereich** implementieren und dort die dafür **ausdrücklich verlangten** GUI-Elemente hinzufügen.
- Bestehende Funktionen und übrige Ansichten dabei visuell und funktional erhalten; technische Änderungen möglichst ohne sichtbare Auswirkungen auf andere Bereiche realisieren.
- Ein Funktionsauftrag ist **keine pauschale Designfreigabe**. Auch für eine vermeintlich notwendige Änderung eines bisher bestehenden, nicht ausdrücklich freigegebenen GUI-Elements erst die konkrete Abweichung beschreiben, begründen und die Freigabe des Auftraggebers einholen. Falls möglich den übrigen Funktionsumfang unabhängig davon implementieren.
- Entdeckte Probleme an nicht beauftragten Ansichten (auch Darstellungs-, Responsivitäts- und Accessibility-Probleme) melden und eine gezielte Korrektur vorschlagen, **nicht ungefragt umsetzen**.

### Vor jedem Implementierungsauftrag

1. Betroffene Ansichten, Komponenten und Dateien sowie **nicht zu verändernde** Bereiche benennen.
2. Den aktuellen Stand anhand des Ausgangs-Commits, bestehender Designreferenzen und – sofern vorhanden – freigegebener Screenshots feststellen. Nicht vorhandene Referenzen nicht als freigegeben behaupten.
3. Die kleinstmögliche Änderung wählen. Bei einem Konflikt zwischen Funktion und Bestandsschutz **vor einer zusätzlichen GUI-Änderung** um Freigabe bitten.

### Prüfung und Abschlussbericht

1. Vor Abschluss die beauftragten Ansichten **und** die nicht betroffenen Ansichten auf unbeabsichtigte visuelle Veränderungen prüfen.
2. Vorhandene, ausdrücklich freigegebene Referenz-Screenshots bei konstantem Viewport/Browser vergleichen; animierte/dynamische Bereiche in reproduzierbare Zustände versetzen oder kenntlich ausklammern. Wenn kein visueller Vergleich möglich war, dies als **nicht geprüft** ausweisen.
3. Jede beabsichtigte GUI-Änderung, die betroffenen Ansichten und das Ergebnis des Vergleichs im Pull Request/Abschlussbericht dokumentieren. Nicht autorisierte Abweichungen zurücknehmen, statt sie zu rechtfertigen.
4. **Screenshot-Baselines nur nach ausdrücklicher GUI-Freigabe aktualisieren.** Ein grüner Funktionstest ersetzt keine visuelle Abnahme.
5. Änderungen zunächst auf einem Arbeitsbranch/PR zur Prüfung anbieten, sofern der Auftraggeber nicht ausdrücklich eine andere Vorgehensweise vorgibt.

**Vorrang:** Diese Regel schränkt die Freiheit bei reversiblen technischen Detailentscheidungen auf **nicht visuell wirksame** Änderungen ein. Projektspezifische fachliche, medizinische, Datenschutz- und Sicherheitsanforderungen gelten unverändert. Ein neuer Commit löst keinen Codex-Auftrag automatisch aus.
