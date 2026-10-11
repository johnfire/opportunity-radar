# Einreichung – Challenge „Die nächste Generation der Beihilfe-App“ (LBV Baden-Württemberg)

---

## 1. Unternehmen und Lösungsansatz
*(RF Nr. 1, 11)*

**Unternehmen.** Rehm KI Consulting, Einzelunternehmen (Freiberufler), Alpenstr. 3, 86836 Klosterlechfeld, Bayern.
Wir sind ein kleiner Anbieter mit Schwerpunkt auf KI-gestützter Prozessautomatisierung. Der
Inhaber ist Computeringenieur mit Hintergrund in Hardware- und Softwareentwicklung
(Verifikation bei Intel, ca. sechs Jahre Webentwicklung) sowie praktischer Erfahrung in der
Entwicklung mit KI und mit Java und TypeScript.

**Transparenz vorab (RF Nr. 1).** Wir verfügen *nicht* über eine bereits produktiv im Einsatz
befindliche, marktgängige Beihilfe-App und nennen daher keine Referenzkunden. Wir reichen
bewusst keinen Produktnachweis ein, sondern einen Lösungsansatz und Hinweise zur
Ausgestaltung der Leistungsbeschreibung. Wir möchten dem LBV damit Marktkenntnis zu
Möglichkeiten liefern, die in einer klassischen Beschaffung leicht untergehen.

**Lösungsansatz in Kürze.** Eine iOS/Android-App und ein im Rechenzentrum der öffentlichen
Hand betreibbarer Webservice, der Belege entgegennimmt, zwischenspeichert und über eine offen
dokumentierte Schnittstelle an das bestehende Beihilfeverfahren übergibt. Unterscheidungsmerkmal:
**Belegverständnis bereits bei der Erfassung**, mit KI-Modellen, die vollständig lokal im
Rechenzentrum bzw. auf dem Gerät laufen (keine Cloud-KI, keine Drittlandübermittlung).

**Unterscheidung zu anderen Marktteilnehmern (RF Nr. 11).**
1. Qualitätsprüfung und Belegerkennung schon am Gerät, sodass unleserliche, unvollständige oder
   falsch zugeordnete Belege vor der Einreichung auffallen und nicht erst bei der Sachbearbeitung.
2. Offene Schnittstellen (OpenAPI-Spezifikation) für App und Webservice – kein Hersteller-Lock-in.
3. Schlanke, auf wenige Spezialisten ausgelegte Entwicklung mit KI-Unterstützung; kurze
   Iterationszyklen bei Erweiterungen.
Wir sind (noch) kein etablierter Anbieter; diese drei Punkte sind unser Beitrag, keine
Marktführerschaft.

---

## 2. Barrierefreiheit und Nutzerfreundlichkeit
*(RF Nr. 3, 8)*

**Barrierefreiheit (RF Nr. 8).** Zielstandard WCAG 2.2 AA / EN 301 549 / BITV 2.0, nachgewiesen
durch (a) automatisierte Tests in der Entwicklung, (b) manuelle Prüfung mit VoiceOver und
TalkBack, (c) Test mit Nutzenden mit Einschränkungen vor jedem Release und (d) eine
„Erklärung zur Barrierefreiheit“. Konkret: dynamische Schriftgrößen, ausreichende Kontraste,
vollständige Screenreader-Beschriftung, Bedienung ohne Feinmotorik, Sprach- und Haptik-Hinweise
bei der Kameraführung, einfache Sprache für Hilfetexte.

**Nutzerfreundliche Belegerfassung (RF Nr. 3).** Live-Kantenerkennung, automatisches Auslösen
bei scharfem, vollständigem Bild, Prüfung auf Unschärfe, Spiegelung, Schatten und abgeschnittene
Ränder, Mehrseiten-Erfassung und sofortiges Feedback („bitte näher/heller“). Danach optional ein
Plausibilitätshinweis (z. B. „Rechnungsbetrag nicht erkennbar“). Diese Hinweise sind
**unterstützend**; die Entscheidung über den Antrag bleibt vollständig bei der Beihilfestelle.

**Erfahrung mit Erkennungsquoten (RF Nr. 3).** Wir bringen praktische
Erfahrung in der Entwicklung mit KI sowie in Java und TypeScript mit, haben aber keine
Erkennungsquoten aus einem Beihilfe-Produktivbetrieb und nennen daher keine Zahl. Wir bieten
an, die Quote **messbar auf einem vom LBV bereitgestellten, synthetischen oder anonymisierten
Testbelegsatz** zu belegen, bevor irgendeine Beschaffungsentscheidung fällt.

---

## 3. Zeitaufwand und wirtschaftliche Voraussetzungen
*(RF Nr. 6, 10)*

**Zeitaufwand (RF Nr. 10) – unsere Schätzung ohne Gewähr.**
Ab Zuschlag etwa **6–9 Monate bis zu einem Pilotbetrieb** mit begrenztem Nutzerkreis und
**9–12 Monate bis zum Regelbetrieb**, inklusive Sicherheits- und Datenschutzkonzept, Anbindung
an das Beihilfeverfahren, Barrierefreiheitsprüfung, Store-Freigaben und Migration vom
bestehenden Vertrag. KI-gestützte Entwicklung verkürzt vor allem die Programmierphase; nicht
verkürzen lassen sich Abnahmen, Sicherheitsfreigaben und Store-Reviews. Wir empfehlen eine
**Übergangsphase mit paralleler Laufzeit** der bestehenden App, damit es keine Versorgungslücke
gibt.

**Preismodell (RF Nr. 6).** Ein **Pauschalpreis unabhängig von Nutzer- und Antragszahlen**
wäre für uns kalkulierbar: jährliche Pauschale für Lizenz, Pflege und Support, getrennt davon
ein Rahmen mit festen Tagessätzen für Weiterentwicklungen. Konkrete Preise nennen wir
entsprechend der Vorgabe „keine Angebote“ nicht.

**Personal (zur Einordnung).** Die Rollen Mobile-Entwicklung, Backend/Betrieb sowie
Datenschutz/IT-Sicherheit sind derzeit **nicht besetzt**. Im Zuschlagsfall bauen wir das
Team bedarfsgerecht aus. Als möglichen Kooperationspartner sehen wir die Firma SoftB. Für den
Beihilfe-Fachbereich würden wir einen Berater mit Beihilfe-/PKV-Erfahrung
einbinden (siehe Abschnitt 5, RF Nr. 12).

---

## 4. Technische und organisatorische Voraussetzungen, Betrieb
*(RF Nr. 2, 4, 13, 14)*

**Architektur (RF Nr. 2).** Mobile App (iOS/Android, ein gemeinsamer Codebestand) mit
verschlüsseltem lokalem Zwischenspeicher für die Offline-Erfassung; zentraler Webservice
(containerisiert, zustandslos skalierbar) mit Test- und Produktivumgebung. **Betrieb im
Rechenzentrum der öffentlichen Hand ist ausdrücklich möglich und von uns bevorzugt**; die
Lösung hat keine Abhängigkeit von Cloud-Diensten außerhalb.

**Datenschutz (RF Nr. 4).** Gesundheitsdaten nach Art. 9 DSGVO: Datenminimierung,
Ende-zu-Ende-gesicherte Übertragung (TLS 1.3) und Verschlüsselung im Ruhezustand,
rollenbasiertes Berechtigungskonzept, **automatische Löschung nach erfolgreicher Abholung**,
keine Tracking-/Analyse-SDKs, keine Cloud-KI-Dienste, Datenschutz-Folgenabschätzung
(Art. 35 DSGVO) und Auftragsverarbeitungsvertrag als Vertragsbestandteil. Das
Sicherheitskonzept orientiert sich am BSI IT-Grundschutz.

**IT-Sicherheitsstandards (RF Nr. 14).** Orientierung an BSI IT-Grundschutz und OWASP MASVS/ASVS,
Abhängigkeits- und Schwachstellenscans in jedem Build, signierte Releases, unabhängiger
Penetrationstest vor Produktivstart. **Wir verfügen derzeit über keine ISO-27001- oder
BSI-Zertifizierung**; Nachweise können im Zuschlagsfall über Betriebspartner oder durch eine
Zertifizierung erbracht werden.

**Hochverfügbarkeit (RF Nr. 13).** Zielgröße des LBV (≥ 99,5 % im 24/7-Betrieb) ist
architektonisch erreichbar: zustandslose Dienste, redundante Instanzen, Healthchecks und
Alarmierung, getestete Wiederanlaufverfahren. Die tatsächliche Verfügbarkeit hängt wesentlich
von Betrieb und Infrastruktur im Rechenzentrum ab; wir würden die Aufgabenteilung im
Betriebskonzept klar festlegen. Einen Betriebsnachweis aus Produktivbetrieb haben wir nicht.

**Dimensionierung (rechnerisch aus den Angaben des LBV).** 2,4 Mio. Anträge und 23 Mio.
Seiten pro Jahr entsprechen im Mittel ca. 6.600 Anträgen und 63.000 Seiten pro Tag; für
Spitzenlast (z. B. Jahreswechsel) planen wir ein Vielfaches ein. Weil Daten nach der Abholung
gelöscht werden, bleibt der Speicherbedarf im Dauerbetrieb gering.

---

## 5. Best Practices, Erfahrungen aus vergleichbaren Projekten
*(RF Nr. 5, 9, 12)*

**Erfahrung im Bereich Beihilfe / PKV (RF Nr. 12).** Wir haben **keine eigene Vorerfahrung** im
Beihilfe- oder PKV-Umfeld. Wir würden einen fachlichen Berater einbinden.

**Hinweise zur Ausschreibung (RF Nr. 9):**
1. **Losbildung prüfen** (§ 97 Abs. 4 GWB): App + Webservice, Betrieb im Rechenzentrum und
   Weiterentwicklung als getrennte Lose öffnen den Markt für mittelständische Anbieter und
   senken das Risiko eines einzelnen Anbieters.
2. **Offene, dokumentierte Abholschnittstelle** (OpenAPI) und Übergabe von Quellcode bzw.
   Quellcode-Hinterlegung, damit App und Webservice später austauschbar bleiben.
3. **Messbare Abnahmekriterien statt Herstellerangaben:** z. B. Anteil der Belege, die ohne
   manuelle Nacharbeit im nachgelagerten OCR-Verfahren erkannt werden, gemessen auf einem
   gemeinsamen Testbelegsatz; Barrierefreiheit als Abnahmetest (BITV-Prüfung).
4. **Spannung in den Anforderungen auflösen:** „marktgängige Standardlösung, keine
   Individualentwicklung“ und zugleich „kontinuierliche Weiterentwicklung“ und Customizing
   passen nur zusammen, wenn Konfigurierbarkeit und Erweiterungspunkte (Design-Tokens,
   Konfiguration statt Code) gefordert werden.
5. **Übergang:** Konten, Verläufe und Store-Einträge der bestehenden App sollen weitergeführt
   werden können; Wechsel ohne Versorgungslücke als Anforderung formulieren.
6. **Neue Möglichkeiten bei der Belegerfassung:** Heutige multimodale Modelle können Belegtyp
   und Pflichtfelder bereits bei der Aufnahme erkennen. Das ist lokal betreibbar und sollte
   als optionale Erweiterung in der Leistungsbeschreibung vorgesehen werden.

**Customizing (RF Nr. 5).** Corporate Design des Landes über Design-Tokens/Themes, Texte und
Hilfeinhalte konfigurierbar ohne Programmieraufwand; funktionale Anpassungen nach Aufwand im
Rahmen der Weiterentwicklung.

---

## 6. Erweiterbarkeit und Weiterentwicklung
*(RF Nr. 7)*

Der Webservice kapselt Fachlogik hinter einer versionierten API, die App ist modular
aufgebaut (Erfassung, Antragsübersicht, Kommunikation). Dadurch lassen sich die vom LBV
genannten Erweiterungen – **Bescheide und Bearbeitungsstände in der App, Schriftverkehr mit der
Beihilfestelle, digitaler Rückkanal** – als eigenständige Module ergänzen, ohne die Erfassung zu
berühren. Roadmap-Vorschlag: (1) Funktionsparität mit der heutigen App, (2) Qualitäts- und
Plausibilitätshinweise bei der Erfassung, (3) Statusanzeige, (4) Nachrichten/Rückkanal.
Skalierung erfolgt horizontal über zusätzliche Instanzen.

---

*Hinweis: Diese Rückmeldung enthält keine Angebote im Sinne des Vergaberechts und enthält
keine vertraulichen Inhalte.*
