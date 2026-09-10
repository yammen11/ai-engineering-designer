# AI Engineering Designer – langfristiges Projektgedächtnis

Stand: 2026-09-09. Grundlage: konsolidierte Chatanalyse und lokaler Codeabgleich vom selben Tag. Der Benutzer hat das Projektverständnis grundsätzlich bestätigt und die Dokumentation beauftragt. Das ist keine pauschale Bestätigung aller Detailvorschläge und kein Implementierungsauftrag.

Fortschreibung am 2026-09-09: Der Benutzer hat die nächste Entwicklungsstufe ausdrücklich konkretisiert. Ihr verbindlicher Zielumfang steht unter „ACCEPTED TARGET ARCHITECTURE – nächster Montageprototyp“. Der lokale Code bleibt v0.1; die neue Richtung ist keine Freigabe zur Implementierung. Eine neue Versionsnummer wurde nicht festgelegt.

## Status und Geltungsbereich

- **ACCEPTED:** ausdrücklich entschieden oder als Architekturleitlinie übernommen.
- **PROPOSED:** diskutierter Ansatz; noch nicht verbindlich beschlossen.
- **OPEN:** ungeklärte Frage oder nicht ausreichend belegtes Detail.
- **REJECTED:** ausdrücklich verworfene Richtung, im jeweils genannten Umfang.

Dieses Dokument beschreibt das Zielverständnis. Der tatsächliche Implementierungsstand steht in `CURRENT_STATE.md`. Ein akzeptiertes Ziel ist nicht automatisch implementiert. Vorschläge und offene Fragen dürfen niemals eigenständig als Arbeitsauftrag ausgeführt werden.

## Ziel und fachlicher Rahmen

**ACCEPTED:** Eine generalisierbare Engineering-Software soll aus Lastenheften, Benutzerzielen, Produktdaten, Arbeitsplänen, CAD-Modellen und verfügbaren Betriebsmitteln mehrere geeignete Automatisierungskonzepte ableiten, technisch prüfen und vergleichbar bewerten.

Die Zielanwendung umfasst:

- Greenfield, Brownfield und Übergänge zwischen alten und neuen Produktvarianten;
- variantenreiche Montage und weitere industrielle Aufgaben;
- Wiederverwendung bestehender Betriebsmittel und Berücksichtigung externer Ressourcen;
- Maschinen, Vorrichtungen, Fördertechnik, Roboter und menschliche Tätigkeiten;
- geometrische Darstellung und langfristig simulationsgestützte Prüfung.

**ACCEPTED:** Daimler-Anwendungsfälle dienen als konkrete Erprobung; der Kern soll über ein einzelnes Unternehmen und einen einzelnen Prozess hinaus verwendbar bleiben. Stoßeckenmontage und Sitzfertigung wurden als Anwendungsfälle benannt. Damit ist noch keine vollständige Pilotdatensammlung oder feste Implementierungsreihenfolge beschlossen.

**PROPOSED:** Ein späterer Automation Hub mit wiederverwendbaren Assets, Konzepten und Automation Recipes; darauf aufbauend Simulationsdaten, Modelltraining oder Roboter-Policies. Das sind langfristige Erweiterungen, keine Funktionen des aktuellen Prototyps.

**ACCEPTED:** Der nächste kleine Demonstrator behandelt Grundplatte, Winkelhalterung und zwei Schrauben (siehe Zielumfang unten). **OPEN:** Weitergehender industrieller Demonstratorumfang, Evaluation, konkrete Pilotdaten, spätere Produktstrategie sowie Kooperations- und IP-Regelungen. Historische Überlegungen zu Förderung, Promotion oder Startup sind keine gesicherten Zusagen.

## Drei Hauptbereiche

**ACCEPTED:** Die Hauptarchitektur bleibt Asset Factory, Project Planner und Validation Factory. Sie wird intern vertieft und durch nachvollziehbare Datenverträge und Rückmeldungen verbunden.

| Bereich | Langfristige Verantwortung |
|---|---|
| Asset Factory | Betriebsmittel finden, technische Informationen zusammentragen und normalisieren; Fähigkeiten, CAD und gegebenenfalls Simulationsinformationen bereitstellen. |
| Project Planner | Aufgabe, Varianten und Randbedingungen verstehen; Automatisierungspotenzial bewerten; Fähigkeiten ableiten, Ressourcen zuordnen und Konzeptvarianten entwickeln. |
| Validation Factory | Konzepte durch Regeln, Geometrie, Kinematik und später Simulation prüfen; begründetes Feedback liefern. |

Der fachliche Zusammenhang lautet: Projektanforderungen → Project Planner ↔ Asset Factory → Konzept → Validation Factory → Ergebnis oder gezielte Überarbeitung. Die Asset Factory kann unabhängig davon eine Bibliothek vorbereiten. Die Dreiteilung ist daher keine ausschließlich lineare Einmal-Pipeline.

**ACCEPTED:** Der Benutzer soll Ergebnisse und Zwischenergebnisse nachvollziehen können. Rückmeldungen zwischen den Bereichen gehören zum Zielbild.

**PROPOSED:** Konkrete Feedbackpakete und Schleifen für Ressourcenwechsel, Layoutänderung, Bewegungsplanung, Prozessänderung, Informationsbeschaffung und Simulationsmodellverbesserung. Ein Fehler soll gezielt an den verantwortlichen Bereich gehen, statt zwangsläufig alles neu zu starten.

### Asset Factory

**ACCEPTED:** Interne Bibliotheken und externe Quellen sollen grundsätzlich unterstützt werden. Die Auswahl soll technische Fähigkeiten und Anforderungen berücksichtigen, nicht allein Namen oder geometrisches Aussehen.

**PROPOSED:** Föderierter Asset-Index, bedarfsabhängiger Download und Asset Packages mit Identität, Capabilities, technischen Daten, CAD, Kinematik, Simulationsreferenzen, Quellen und Verfügbarkeitsinformationen. Hersteller, TraceParts und CADENAS/3Dfindit wurden als mögliche Quellen diskutiert; ein gesicherter automatischer Zugang ist damit nicht belegt.

**OPEN:** Konkrete Adapter, Zugänge, Datenqualität, Nutzungsrechte, Aktualisierung und Verhalten bei nicht verfügbaren Assets. Ein einfaches Ersatzmodell ist nicht gleichwertig mit einem realen Maschinenmodell.

### Project Planner

**ACCEPTED:** Fachlich begründete Konzeptentwicklung für unterschiedliche Automatisierungsarten. Eine konkrete Roboterauswahl darf das Gesamtproblem nicht vorwegnehmen.

**PROPOSED:** Die besprochene Methodik verbindet Problemverständnis, Produkt-/Prozessanalyse, Varianten-/Komplexitätsanalyse, Bewertung des Automatisierungspotenzials, Konzeptgenerierung, Ressourcen-/Prozesszuordnung, geometrischen Aufbau, Machbarkeitsprüfung und Ranking.

**ACCEPTED seit der Fortschreibung vom 09.09.2026:** PPR (Product–Process–Resource) als gemeinsames Engineering-Wissensmodell, nicht als eigener Agent. Ein wachsendes EngineeringProject/PPRContext ist für den nächsten Prototyp vorgesehen.

**PROPOSED:** Produktfamilien, BOM/GBOM, Reihenfolgeabhängigkeiten und wissenschaftliche Komplexitätsmaße als weitere Grundlagen. Konkrete Kennzahlen, Gewichte und Solver sind nicht verbindlich festgelegt; Automation-Potential-Bewertung und Ranking sind aus der nächsten Stufe ausgeschlossen.

**ACCEPTED als Schnittstellenabsicht:** Arbeitspläne und Produktinformationen aus der Arbeit des Kollegen Emin/TwinMap sollen nutzbare Eingaben sein. Eine technische Integration oder fertige automatische Arbeitsplanerzeugung ist nicht nachgewiesen.

### Validation Factory

**ACCEPTED als Ziel:** Technische Prüfung mit nachvollziehbaren Ergebnissen. Ein plausibler LLM-Text oder eine darstellbare CAD-Datei allein ist kein Machbarkeitsnachweis.

**PROPOSED:** Drei Prüfebenen: Logik/Prozess/Capabilities, Geometrie/Layout und Bewegung/Physik/Simulation. Ergänzende Checks umfassen Erreichbarkeit, Kollision, Zugänglichkeit und später Taktzeit.

**OPEN:** Welche Prüfungen zwingend sind, deren Methoden und Toleranzen, die Behandlung unprüfbarer Fälle und die Kriterien für menschliche Freigabe.

## Agenten, Engineering Core und Orchestrierung

**ACCEPTED:** LLMs interpretieren und planen; Python-Funktionen, CAD-Bibliotheken, Regeln und Solver führen konkrete Berechnungen aus. Eine Funktion ist nicht allein durch ihre Existenz ein dem LLM zugängliches Tool.

**ACCEPTED:** Langfristig mehrere spezialisierte Agenten; klare Trennung zwischen Agenten, technischen Services, Tools, Datenmodellen, Ablaufsteuerung und GUI. Nicht jede neue Funktion benötigt einen neuen Agenten.

**ACCEPTED:** Schrittweise Erweiterung des bestehenden Python-Projekts mit kleinen funktionierenden Zwischenständen („Successful Design Solutions“). Der Benutzer möchte die Struktur und den Code dabei verstehen.

**ACCEPTED als konzeptionelle Richtung:** Holonische Zusammenarbeit der drei Hauptbereiche: begrenzte lokale Zuständigkeit und gemeinsame Zielverfolgung. Dies ist ein Organisationsprinzip, nicht der eigentliche Produktzweck.

**PROPOSED:** Rollen wie Requirement-, Process-, Asset-, Concept-, Layout- und Validation-Agent; typisierte Feedbacknachrichten, gemeinsamer Workflow-Zustand, kontrollierte Wiederholungen und Parallelverarbeitung.

**PROPOSED:** LangGraph wurde ausdrücklich als Idee zum späteren Wiederaufgreifen notiert. n8n, OpenAI Agents SDK, Responses API, MCP und FastAPI wurden ebenfalls diskutiert. Keine dieser Diskussionen legt das endgültige Orchestrierungsframework fest.

**OPEN:** Controller im Project Planner oder separate übergeordnete Steuerung; spätere Agentenzahl, Toolverträge, Wiederholungsgrenzen und genaue Zustandsverwaltung. Für die nächste Stufe ist genau ein Analyse-Agent namens `ProductProcessAnalysisAgent` festgelegt. Weitere benannte Komponenten sind dadurch nicht automatisch zusätzliche LLM-Agenten.

## Canonical Data Model

**ACCEPTED:** „Stable Core + Extensible Data“ wurde am 8. September als Leitlinie für die weitere Datenstruktur übernommen. Stabile Grundverträge sollen durch erweiterbare Eigenschaften und Fähigkeiten unterschiedliche Aufgaben und Asset-Arten abbilden.

Übernommene Prinzipien:

- generische Objekte statt eines starren Gesamtmodells je Roboter-, Greifer- oder Förderbandklasse;
- flexible Eigenschaften über `DataValue`;
- explizite Darstellung unbekannter, geschätzter und abgeleiteter Informationen;
- Matching mit `pass / fail / unknown`;
- Normalisierung externer Quellen vor der Verarbeitung durch Agenten;
- AAS-kompatibel, aber nicht AAS-abhängig;
- `semantic_id` berücksichtigen;
- Workflow-Schemas von Engineering-/Asset-Schemas trennen.

| Begriff | Status und bisheriges Verständnis |
|---|---|
| Process | **ACCEPTED seit 09.09.2026 als Core-Objekt:** strukturierter Prozess; genaue Felder und Beziehungen **OPEN**. |
| Operation | **ACCEPTED seit 09.09.2026 als Core-Objekt:** einzelne Prozessoperation; genaue Felder und Beziehungen **OPEN**. Nicht mit dem CAD-Befehlsfeld `CadInstruction.operation` gleichsetzen. |
| CapabilityRequirement | **ACCEPTED als Kernbegriff:** erforderliche Fähigkeit; konkretes Schema **OPEN**. |
| AssetRequirement | **ACCEPTED als Kernbegriff:** Anforderungen an Ressourcen; konkretes Schema **OPEN**. |
| CanonicalAsset | **ACCEPTED als Kernbegriff:** normalisierte, quellenunabhängige Asset-Repräsentation; konkretes Schema **OPEN**. |
| MatchResult | **ACCEPTED als Kernbegriff:** strukturiertes Matching-Ergebnis einschließlich `pass / fail / unknown`; konkrete Prüf- und Aggregationsregeln **OPEN**. |
| DataValue | **ACCEPTED als Kernbegriff:** flexible Eigenschaftsdarstellung; genaue Felder, Datentypen und Validierung **OPEN**. |

**OPEN:** Verbindliche Beziehungen zwischen Process, Operation, Requirements, Assets und Konzepten; Schema-Versionierung, Persistenz und Trennung von Datenzustand und Prüfergebnis. Dieses Dokument ergänzt keine unbestätigten Detailfelder.

### Datenzustände

**ACCEPTED:** Fehlende oder abgeleitete Daten sollen ausdrücklich erkennbar sein. Mit der neuen Zielentscheidung vom 09.09.2026 ist die vollständige Zustandsmenge `known`, `unknown`, `estimated`, `derived`, `not_applicable` verbindlich vorgesehen. `unknown` darf niemals automatisch `fail` bedeuten. Die Zustände beschreiben Daten, nicht bereits die technische Eignung eines Assets.

**PROPOSED als Arbeitsdefinition, Detailvertrag OPEN:**

| Zustand | Bedeutung |
|---|---|
| known | Wert liegt mit nachvollziehbarer Grundlage vor. |
| unknown | Wert ist unbekannt. |
| estimated | Wert wurde geschätzt. |
| derived | Wert wurde aus anderen Informationen abgeleitet oder berechnet. |
| not_applicable | Eigenschaft ist für diesen Fall nicht anwendbar. |

**OPEN:** Quellen, Einheiten, Ableitungsverfahren, Unsicherheit, Freigaben und Auswirkungen dieser Zustände auf Matching und Validation. Die bloße Nennung der Zustände ist noch kein ausführbarer Prüfvertrag.

## Source Adapter und AAS-Strategie

**ACCEPTED:** `Source → Adapter / Normalizer → CanonicalAsset → Agents / Matching`. Quellenabhängige Strukturen sollen nicht alle nachgelagerten Komponenten bestimmen.

**PROPOSED:** Adapter für lokale Metadaten, Herstellerinformationen, CAD-Portale und AAS; Vereinheitlichung von Eigenschaften, Einheiten und semantischen Zuordnungen. Konkrete Implementierung und Fehlerbehandlung sind **OPEN**.

**ACCEPTED seit 09.09.2026 für die nächste Stufe:** Ausschließlich eine lokale Asset Library als erste Quelle, angebunden über einen Local Asset Adapter/Normalizer an `CanonicalAsset`. Die konkrete Quellanbindung darf nicht direkt in Agenten eingebaut werden. Externe Adapter bleiben spätere Erweiterungen.

**ACCEPTED:** AAS als möglicher Integrationsweg und semantische Quelle berücksichtigen, ohne den Kern ausschließlich an AAS zu binden.

Die AAS-Modellierung und der bestehende Machbarkeitsassistent sind belegte Vorarbeiten aus einem anderen Softwareprojekt und der Praktikumsarbeit. Sie dürfen nicht als bereits integrierte Designer-Funktionen dargestellt werden.

**PROPOSED:** Teile des vorhandenen Machbarkeitsassistenten als Prüfkomponente übernehmen oder anbinden.

**OPEN:** Übernahmeumfang, Schnittstelle, Mapping zum Canonical Data Model und Umgang mit bisherigen maschinenspezifischen Capability-Strukturen.

## CAD, Geometry und Simulation

**ACCEPTED:** Das LLM erzeugt kontrollierte Anweisungen; die tatsächliche Geometrie entsteht im Engineering Core. Die aktuelle CAD-Grundeinheit ist Millimeter. Eine allgemeine Einheiten- und Koordinatensystemstrategie bleibt **OPEN**.

**PROPOSED:** Wiederverwendbare Tools für Import, Messung, Translation, Rotation, Zusammenbau, Export und Prüfung; einfache selbst erzeugte Geometrien als Ergänzung zu realen Assets.

**PROPOSED:** Simulation Model Resolver/Builder: vorhandene URDF-/USD- oder Herstellerinformationen verwenden und nötigenfalls Geometrie um Kinematik und weitere Daten ergänzen. Diskutiert wurden statische Geometrie, funktionale Bewegung und vollständige Kinematik/Dynamik als unterschiedliche Modellierungstiefen.

**OPEN:** Simulationswerkzeug, unterstützte Modellklassen, automatische Kinematikanreicherung und menschliche Prüfung. Die Rekonstruktion beliebiger Maschinenkinematik aus STEP ist keine zugesicherte Fähigkeit. Eine STEP-Datei oder Formatkonvertierung allein belegt keine vollständigen Gelenk-, Bewegungs- oder Physikdaten.

## Entscheidungen und Begründungen

| Status | Entscheidung | Begründung |
|---|---|---|
| ACCEPTED | Allgemeiner, unternehmensübergreifender Kern | Neue Aufgaben und industrielle Beispiele unterstützen. |
| ACCEPTED | Drei Hauptbereiche beibehalten | Bestehendes Konzept verständlich vertiefen. |
| ACCEPTED | Strukturierte Datenverträge | Ergebnisse kontrolliert weiterverarbeiten und prüfen. |
| ACCEPTED | Stable Core + Extensible Data | Neue Eigenschaften und Asset-Arten ohne ständigen Kernumbau aufnehmen. |
| ACCEPTED | Python-Engineering-Core getrennt von GUI und LLM | Berechnungen nachvollziehbar halten und Komponenten erweitern können. |
| ACCEPTED | Lokales LLM für den aktuellen Prototyp | Zunächst ohne bezahlte API weiterarbeiten; keine endgültige Anbieterbindung. |
| ACCEPTED | Kleine funktionierende Entwicklungsstände | Lernen, testen und anhand konkreter Probleme erweitern. |
| REJECTED | Gesamtprojekt auf Roboter beschränken | Allgemeine Automatisierung umfasst weitere Maschinen und menschliche Tätigkeiten. |
| REJECTED | Gesamtmodell auf Pick-and-Place festlegen | Spätere Aufgaben sollen offen bleiben; Pick-and-Place bleibt als Testfall möglich. |
| REJECTED | Für jede Erweiterung eine neue Gesamtsoftware herunterladen | Bestehenden Code schrittweise verstehen und erweitern. |

n8n, LangGraph, OpenAI, AAS und Simulation wurden nicht grundsätzlich verworfen. Verschoben oder nicht implementiert bedeutet nicht REJECTED.

## Widersprüche und offene Abgrenzungen

- **OPEN:** Koordination innerhalb des Planners versus übergeordneter System-Orchestrator.
- **OPEN für spätere Stufen:** Geometrischer Konzeptaufbau und erste Machbarkeitsprüfung im Planner versus Zuständigkeit der Validation Factory. Für den nächsten Prototyp sind LayoutBuilder und SceneComposer vorgesehen; industrielle Machbarkeitsprüfung ist ausdrücklich ausgeschlossen.
- **ACCEPTED, am 09.09.2026 konkretisiert:** Der nächste Meilenstein ist der kleine Montageprototyp mit Grundplatte, Winkelhalterung und zwei Schrauben. Die frühere offene Wahl „Kugel auf Quader“ versus Prozessverständnis ist damit abgelöst. Das Kugelbeispiel bleibt ein früherer Vorschlag, kein konkurrierender beschlossener Meilenstein.
- **ACCEPTED:** Die spätere generische Datenleitlinie präzisiert frühere spezifische JSON-Beispiele. Alte Beispiele sind keine verbindlichen Gesamtverträge.
- **OPEN:** Wissenschaftliche Messgrößen, Vergleichsmethoden, Testfälle und verbindliche Termine. Frühere Statuszusammenfassungen allein sind keine Zusage oder Implementierungsbelege.

## ACCEPTED TARGET ARCHITECTURE – nächster Montageprototyp

Entscheidungsdatum: 2026-09-09. Quelle: ausdrücklicher Benutzerauftrag im eingefügten Text „Wir haben die nächste Entwicklungsstufe des AI Engineering Designers konkretisiert“. Dieser Abschnitt dokumentiert ein akzeptiertes Entwicklungsziel, keine bereits vorhandene Funktion und keine Implementierungsfreigabe.

### Ziel, Montagefall und Ergebnisgrenze

**ACCEPTED:** Ein kleiner vollständiger End-to-End-Prototyp soll von Produkt-/Prozessdaten über Analyse, ein abstraktes Automatisierungskonzept, lokale Asset-Auswahl und Layout bis zur gemeinsamen 3D-Darstellung führen. Er ist ein schrittweiser Ausbau in Richtung Project Planner und Asset Factory; die Validation Factory folgt später.

**ACCEPTED:** Erster Fall ist eine Grundplatte mit Winkelhalterung, verbunden durch zwei Schrauben. Die benannte beispielhafte Prozessfolge ist:

1. Grundplatte zuführen beziehungsweise positionieren.
2. Winkelhalterung aufnehmen.
3. Winkelhalterung orientieren.
4. Winkelhalterung auf der Grundplatte positionieren.
5. Teile halten beziehungsweise fixieren.
6. Zwei Schrauben einsetzen und anziehen.
7. Baugruppe entnehmen.

Grundlegende Capabilities umfassen `transport`, `handling`, `gripping`, `positioning`, `fixing` und `screwing`. Der Fall konkretisiert einen Test, beschränkt aber das allgemeine Schema nicht auf diese Baugruppe oder Fähigkeiten.

**ACCEPTED – aus dieser Stufe ausgeschlossen:** vollständige Validation Factory, Collision Checking, Reachability, IK, Motion Planning, Simulation, Cycle Time Validation, technische Machbarkeitsbewertung, Automation-Potential-Bewertung, Kostenbewertung und Concept Ranking. Diese Funktionen sind nicht global REJECTED, sondern zurückgestellt. Die ausgegebene Szene darf nicht als kollisionsfrei, erreichbar, simuliert oder industriell machbar bezeichnet werden.

**ACCEPTED:** Normale Software-/Schema-Prüfungen bleiben zulässig: gültige Dateien, JSON-Strukturen, Einheiten, Referenzen und Poses. Einfaches nachvollziehbares Anforderungs-Matching ist ebenfalls Bestandteil; es ersetzt keine industrielle Feasibility Validation.

### Eingaben und deterministische Vorverarbeitung

**ACCEPTED als GUI-Zielumfang dieses Mini-Projekts:** PDF mit Prozess-/Montagebeschreibung, mehrere getrennte Produkt-STEP-Dateien (zunächst etwa `base_plate.step` und `bracket.step`), optionale zusätzliche Produktdateien und Benutzerziel beziehungsweise Projektbeschreibung. Eine fertige Assembly-STEP ist nicht erforderlich. Produktstruktur und Montagebeziehungen sollen aus den Eingangsdaten abgeleitet werden.

**ACCEPTED:** STEP-Dateien werden nicht roh an das LLM gegeben. Python analysiert sie deterministisch und erzeugt strukturierte Geometrieinformationen. Vorgesehen sind Abmessungen, Bounding Box, Volumen, Zentrum, sinnvolle Topologieinformationen und `GeometryReference` sowie automatisch erzeugbare Standardansichten `front`, `side`, `top`, `isometric`.

**OPEN:** Genaue Definition des Zentrums, erforderliche Topologie, Referenzkoordinatensysteme und konkrete Render-/Datenschemas. Das Ziel einer besseren räumlichen Produktinterpretation ist keine Zusage vollständigen spatial/embodied understanding aus beliebigen Eingangsdaten.

**ACCEPTED als optionale Erweiterung:** Renderbilder können zusätzlich an das lokale Modell gehen, sofern es Vision unterstützt. Modellunterstützung und konkrete Bildanbindung sind **OPEN**; Vision ist keine pauschale Voraussetzung für alle lokalen Modelle.

**ACCEPTED:** PDF Parsing und STEP Analysis dürfen parallel stattfinden; ihre Ergebnisse werden anschließend zusammengeführt. Diese Parallelisierung ist keine Vorgabe für mehrere Analyse-Agenten.

### Ein Analyse-Agent und gemeinsames PPR

**ACCEPTED:** Ein klar abgegrenzter `ProductProcessAnalysisAgent` erhält normalisierte PDF-/Prozessinformationen und Geometrieinformationen der Produktkomponenten. Seine strukturierte Ausgabe umfasst:

`ProblemDefinition`, `Product`, `Components`, `AssemblyRelations`, `Process`, `Operations`, `CapabilityRequirements`, `Assumptions`, `Unknowns`.

**REJECTED für diese frühe Stufe:** ein zusätzlicher separater Problem-Understanding-Agent. Das ist keine Ablehnung späterer spezialisierter Agenten.

**ACCEPTED:** PPR ist ein gemeinsames Engineering-Wissensmodell, kein Agent. Ein zentrales `EngineeringProject` beziehungsweise `PPRContext` wächst über den Ablauf und enthält mindestens `Product`, `Process`, `Resource`, `AutomationConcepts`, `ProjectMetadata`. Zuerst werden Product und Process gefüllt; Resource wird durch Asset-Suche und Zuordnung ergänzt.

**OPEN:** Ob `EngineeringProject` und `PPRContext` alternative Namen oder getrennte technische Typen werden, genaue Felder, IDs und Persistenz. Die benannten Ausgabeabschnitte verlangen nicht automatisch jeweils eine eigene Python-Klasse.

### Abstraktes Konzept und lokale Ressourcen

**ACCEPTED:** Der `AutomationConceptPlanner` verarbeitet den strukturierten Projektkontext und erzeugt zunächst ein einfaches abstraktes Konzept ohne konkrete Hersteller oder Maschinenmodelle. Daraus entstehen generische `AssetRequirement`-Objekte.

Die genannten Zuordnungen `handling → robot`, `gripping → gripper`, `fixing → fixture`, `screwing → screwdriver`, `transport → conveyor` sind Beispiele für Ressourcenrollen dieses Falls, keine universellen oder hart zu codierenden Ausschließlichkeitsregeln.

**ACCEPTED:** Erste Quelle ist ausschließlich eine lokale Asset Library im Projekt. Jeder Asset-Ordner enthält mindestens `model.step` für die Geometrie und `asset.json` für semantische und technische Daten. Der Local Asset Adapter/Normalizer überführt die Quellinformationen in `CanonicalAsset`.

**PROPOSED – konkrete Ordneraufteilung aus dem Auftrag:**

```text
data/asset_library/
  robots/...
  grippers/...
  screwdrivers/...
  fixtures/...
  conveyors/...
```

Diese Ordner sind eine mögliche Organisation der Quelle und keine starren Asset-Klassen des Canonical Data Model. AAS, Herstellerdatenbanken, CADENAS, 3Dfindit, TraceParts und Webquellen sollen später über dieselbe Adaptergrenze anschließbar bleiben.

**ACCEPTED:** Eine `ResourceProcessAssignment`-Komponente nutzt die AssetRequirements, durchsucht die lokale Asset Factory, lädt CanonicalAssets, vergleicht sie mit den Anforderungen und ordnet konkrete Ressourcen den Prozessoperationen zu. Eine einfache nachvollziehbare Auswahl genügt; Concept Ranking und vollständige technische Machbarkeitsbewertung gehören nicht dazu.

**OPEN:** Konkrete Matching-Regeln, Umgang mit mehreren Kandidaten, unvollständigen Daten und fehlenden Treffern. Fest steht: `unknown` ist nicht automatisch `fail`; unbekannte Eigenschaften belegen umgekehrt auch keine technische Eignung.

### Generische Core-Objekte

**ACCEPTED TARGET ARCHITECTURE:** Das generische Datenmodell soll mindestens folgende Core-Objekte vorbereiten:

`EngineeringProject`, `Product`, `Component`, `AssemblyRelation`, `Process`, `Operation`, `CapabilityRequirement`, `AssetRequirement`, `CanonicalAsset`, `DataValue`, `GeometryReference`, `SourceReference`, `AutomationConcept`, `ResourceAssignment`, `LayoutPlan`, `SceneObject`, `Pose`.

**ACCEPTED:** Stable Core + Extensible Data bleibt verbindlich. Unterschiedliche technische Eigenschaften liegen in flexiblen DataValue-Strukturen. Große starre Asset-Klassen für Robot, Gripper, Conveyor oder ScrewStation sind als Architekturweg **REJECTED**. Die frühere Leitlinie zu `MatchResult` und `pass / fail / unknown` bleibt bestehen; die neue Mindestliste hebt sie nicht auf.

**OPEN:** Detailfelder, Beziehungen, Schema-Versionen und Prüflogik. Die benannten Objekte sind Zielanforderungen und noch keine implementierten Klassen.

### Layout und SceneComposer

**ACCEPTED:** Nach der Ressourcenauswahl wird ein einfaches Layout aufgebaut. Ein LLM/Agent darf semantische Beziehungen wie „robot beside fixture“ oder „conveyor left of fixture“ vorschlagen. Python setzt konkrete Positionen, Rotationen und Transformationen über strukturierte `Pose`-/`LayoutPlan`-Objekte um.

**ACCEPTED:** Ein `SceneComposer` lädt die STEP-Dateien der ausgewählten Assets, transformiert sie und stellt sie gemeinsam mit den Produktkomponenten in der bestehenden 3D-Ansicht dar.

**OPEN:** Konkrete Platzierungsregeln, Pose-Konventionen, Auflösung widersprüchlicher Beziehungen, Schraubengeometrie beziehungsweise zusätzliche Produktdateien sowie Export-/Speicherformat einer Gesamtszene. Diese Details sind nicht durch den Beispielprozess festgelegt. Das Ziel fordert zunächst gemeinsame Darstellung, keinen bereits definierten Assembly-Exportvertrag.

### Konzeptioneller End-to-End-Ablauf

```text
GUI
 → PDF/STEP Ingestion
 → Geometry Preprocessing
 → ProductProcessAnalysisAgent
 → EngineeringProject / PPRContext
 → AutomationConceptPlanner
 → AssetRequirements
 → Local Asset Factory
 → CanonicalAsset
 → ResourceProcessAssignment
 → LayoutBuilder
 → SceneComposer
 → 3D Viewer
```

Die Darstellung ist der konzeptionelle Datenfluss. PDF- und Geometrieverarbeitung können parallel laufen; die ResourceProcessAssignment-Komponente fragt die Asset Factory ab. Das Diagramm erzwingt keine abweichende Besitz- oder Aufrufreihenfolge. Die Bezeichnungen Planner, Assignment, Builder und Composer legen allein noch keine zusätzlichen LLM-Agenten oder ein Orchestrierungsframework fest.

### Konfliktprüfung und Entscheidungshistorie

**Ergebnis am 09.09.2026:** Kein sachlicher Widerspruch zu den bisherigen ACCEPTED-Leitentscheidungen, wenn langfristige Architektur, begrenzte nächste Stufe und aktuelle Implementierung getrennt bleiben.

| Bisherige Entscheidung / offener Punkt | Neue Festlegung und Einordnung |
|---|---|
| Langfristige Validation Factory und technisch geprüfte Konzepte | In dieser Stufe ausdrücklich ausgeschlossen; eine zeitliche Begrenzung, keine Aufhebung des Langfristziels. Ergebnis ist ein unvalidiertes Konzept/Layout. |
| Interne und externe Asset-Quellen | Lokal als erste Quelle; die generische Adaptergrenze erhält die spätere Erweiterbarkeit. |
| Generalisierung statt Robotik-/Pick-and-Place-Festlegung | Konkreter Montagefall als Test. Ressourcenrollen sind Beispiele, keine universellen Maschinenzwänge. |
| Langfristig mehrere spezialisierte Agenten | Ein Analyse-Agent für den Einstieg; spätere Spezialisierung bleibt möglich. |
| PPR zuvor PROPOSED, Process/Operation als konkrete Core-Objekte noch OPEN | Durch den neuen Benutzerauftrag ausdrücklich ACCEPTED als Ziel. Detailverträge bleiben OPEN. |
| Fünf Datenzustände und Behandlung von unknown noch nicht vollständig festgelegt | Zustandsmenge und „unknown niemals automatisch fail“ jetzt ACCEPTED; übrige Matching-Details bleiben OPEN. |
| Meilenstein „Kugel auf Quader“ versus Prozessverständnis OPEN | Abgelöst durch den beschriebenen Montageprototyp als nächstes Ziel. Frühere Vorschläge bleiben historisch nachvollziehbar. |
| Trennung LLM und deterministische Engineering-Funktionen | Bestätigt durch Geometry Preprocessing sowie Python-Pose-/Layout-Umsetzung. |

Der Begriff „geeignet“ beim einfachen Matching darf nicht zur Behauptung industriell validierter Machbarkeit führen. Sollte später eine universelle feste Zuordnung etwa `handling → robot` verlangt werden, müsste der Konflikt zur akzeptierten Generalisierung ausdrücklich neu entschieden werden; der vorliegende Auftrag benennt nur Beispiele.

## Quellen und Beleggrenzen

Primärquelle der Fortschreibung: ausdrücklicher Benutzerauftrag vom 09.09.2026, eingebracht als `pasted-text.txt` (Anhang-ID `1773fb74-c630-4f74-b752-4aa5d697a971`). Die neuen Festlegungen oben stammen aus diesem Auftrag, nicht aus einer nachträglichen Interpretation fehlender früherer Anhänge.

Die konsolidierte Analyse hat folgende zugängliche Projektchats einschließlich ihrer älteren abrufbaren Abschnitte ausgewertet. Titel sind wie in der Chatübersicht wiedergegeben:

| Chat | ID | Relevanz |
|---|---|---|
| Eegniering_Core_orcesta_Archtiact | 6a8f4ccd-6150-83eb-9937-f298167e0af4 | Prototyp, Entwicklungsmethode, lokale Modellanbindung; Übernahme der generischen Datenleitlinie am 08.09.2026. |
| LLM und CAD-Dateien | 6a4f9fc2-e394-83eb-ac8a-66c5699c098e | Ziel, Generalisierung, CAD, Agenten; LangGraph als spätere Idee. |
| Teilgespräch · LLM und CAD-Dateien | 6a5f7be0-38cc-83eb-bc69-d63d81717e35 | Planner-Methodik, Pilotfälle, Engineering-Services. |
| CAD Dateien erhalten | 6a971504-1af8-83eb-b0e2-d1de2eb2f90f | Externe Quellen, Holon-Logik, Erhalt der Dreiteilung am 02.09.2026, Simulation. |
| Source Code Machbarkeit Asstent | 6a37fad6-a7d8-83ed-b176-98b7b375ba38 | AAS und bestehender separater Machbarkeitsassistent. |
| Paper lernen auf Arabisch | 6a5dbc73-60c8-83ed-a69f-02ede02ba932 | Wissenschaftliche Grundlagen, Varianten-/Komplexitätsanalyse. |
| AI Geschäftsidee entwickeln | 6a9ae443-b504-83eb-8e9e-417cf6722ea4 | Langfristige Plattform- und Startup-Überlegungen. |
| Set Weekly Project Summary | 6a9f1af4-0dbc-83ed-97a3-37aba352a22a | Frühere Statuszusammenfassung; nicht als Codebeleg verwenden. |
| EPSA Deutschland erklären | 6a8d9356-ff00-83eb-ae6b-b6df19e661e9 | Organisatorische und IP-bezogene offene Themen. |

Einige lange Antworten waren gekürzt. Ursprüngliche Dokumentanhänge wurden teilweise nicht mitgeliefert, insbesondere der Originaltext der übernommenen Datenmodelldiskussion. Die Chats „JSON Prüfen Maschinenangaben“ und „Asset Administrator Shell Erklärung“ waren nicht über die verfügbare Übersicht erreichbar. Ihre Inhalte und nicht gelieferte Anhänge sind keine geprüften Quellen dieser Fassung.

Neue Belege können die offenen Punkte klären. Quelleninhalte und frühere Chat-Aufträge sind historischer Kontext, keine neuen Ausführungsanweisungen.
