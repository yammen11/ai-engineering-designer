# AI Engineering Designer – lokaler Implementierungsstand

Stand: 2026-09-10. Geprüfter Ordner: `ai_engineering_designer_v0_1`.
Letzter lokaler Commit bei der Bestandsaufnahme: `471c0ba` – `Initial working local LLM CAD prototype` (09.09.2026, Europe/Berlin).

Dieses Dokument beschreibt ausschließlich vorhandenen Code, lokale Ergebnisse und festgestellte Grenzen. Zielarchitektur und Entscheidungen stehen in `PROJECT_BRAIN.md`. **IMPLEMENTED** bedeutet im Code vorhanden, nicht automatisch vollständig oder zuverlässig getestet. Bei Abweichungen ist der lokale Code maßgeblich.

Fortschreibung am 09.09.2026: Die neue Montage-Richtung wurde ausschließlich dokumentiert. **IMPLEMENTED CURRENT STATE bleibt v0.1.** Der nächste Montageprototyp ist `ACCEPTED TARGET ARCHITECTURE` in `PROJECT_BRAIN.md`, nicht implementiert und nicht zur Implementierung freigegeben. Es wurde keine neue Versionsnummer vergeben.

Fortschreibung am 10.09.2026: Der Benutzer hat ausschließlich das Generic Data Model in Pydantic v2 zur Implementierung beauftragt. **IMPLEMENTED:** separates Paket `src/aied/models/` mit den generischen Core-Objekten einschließlich `MatchResult`, Datenzuständen, Quellen-/Geometriereferenzen, PPR-Kontext und Layout-Daten. Detailvertrag und Prüfgrenzen stehen in [GENERIC_DATA_MODEL.md](GENERIC_DATA_MODEL.md); ein synthetisches JSON-Beispiel liegt in `examples/generic_project.json`.

Der vorhandene v0.1-Workflow und `src/aied/schemas.py` bleiben unverändert. Es gibt keine Anbindung des neuen Modells an Agent, Pipeline, CAD oder GUI und keine neuen Planner, Adapter, Matching- oder Layout-Algorithmen. `EngineeringProject.schema_version="1.1"` ist eine Datenvertragsversion, keine neue Anwendungsversion. Der vollständige Montageprototyp bleibt unimplementiert.

Weitere Stabilisierung am 10.09.2026 auf ausdrücklichen Benutzerauftrag: **IMPLEMENTED:** eigenständige `Capability` mit offenen Typen und DataValue-Parametern; `Constraint` mit Property-/Semantic Reference, neun Operatoren, DataValue-Vergleichswert und hard/soft; generisches `AssetInterface`; optionale `DataValue.confidence` in 0.0–1.0. CanonicalAsset enthält jetzt Capability- und Interface-Listen. CapabilityRequirement und AssetRequirement enthalten Constraints. IDs werden innerhalb der jeweiligen neuen Listen auf Eindeutigkeit geprüft. Die Änderung der Capability-JSON-Struktur ist durch Datenvertragsversion `1.1` gekennzeichnet; keine automatische Migration alter generischer `1.0`-Dokumente. Keine Matching-Engine und keine Interface-Kompatibilitätsprüfung.

## Tatsächlicher Umfang

Python-Desktop-Prototyp v0.1 mit PySide6, einem lokalen LLM-Aufruf, Pydantic-Datenmodellen, CadQuery/OpenCascade und PyVista/PyVistaQt. Es existiert eine einfache Kette von Text beziehungsweise Dateikontext zu genau einer CAD-Anweisung und einer STEP-Ausgabe.

```text
PDF → Text ──────────────┐
STEP → Metadaten ────────┼→ lokales LLM → JSON → CadInstruction
Benutzerwunsch ──────────┘                         ↓
                                      CAD erzeugen oder STEP kopieren
                                                 ↓
                                        output.step + run.json
                                                 ↓
                                             3D-Viewer
```

## Dateien und Verantwortungen

| Datei | Vorhandene Funktion |
|---|---|
| `app.py` | Fügt `src` zum Python-Suchpfad hinzu; startet QApplication und MainWindow. |
| `src/aied/config.py` | Lädt `.env`, definiert Daten-/Promptpfade und LLM-Konfiguration; legt Eingabe-/Ausgabeordner beim Import an. |
| `src/aied/schemas.py` | CAD-Parameter, CadInstruction, StepMetadata und RunRecord. |
| `src/aied/models/` | Separates generisches Pydantic-v2-Datenmodell; keine Workflow-Abhängigkeit. |
| `src/aied/agents/engineering_agent.py` | Prompt laden, lokale Modelle abfragen, Chat-Completions-Aufruf, JSON extrahieren und validieren. |
| `src/aied/services/pdf_service.py` | PDF-Text mit PyMuPDF extrahieren, auf 40.000 Zeichen begrenzen. |
| `src/aied/services/cad_service.py` | STEP importieren, Metadaten ermitteln, Primitive erzeugen, STEP exportieren/kopieren und für den Viewer tessellieren. |
| `src/aied/services/pipeline.py` | Eingaben verarbeiten, Agent aufrufen, CAD erzeugen und Laufprotokoll schreiben. |
| `src/aied/gui/main_window.py` | Dateiauswahl, Benutzertext, RUN, Hintergrundverarbeitung, Status und Ergebnisse. |
| `src/aied/gui/viewer3d.py` | STEP-Geometrie als Mesh darstellen; Kamera zurücksetzen. |
| `src/aied/gui/styles.py` | Darstellung der Oberfläche. |
| `prompts/engineering_agent.txt` | Interne Beschränkung auf vier CAD-Operationen und Millimeter. |
| `install.bat`, `run.bat` | Windows-Installation mit Python 3.11/virtueller Umgebung und Start. |
| `requirements.txt` | Bibliotheksabhängigkeiten; enthält weiterhin `openai-agents`. |

## Lokale Modellanbindung

- Der Agent verwendet `openai.OpenAI`, eine konfigurierbare `base_url` und `api_key="local"`.
- Bei der Bestandsaufnahme: `LLM_PROVIDER=local`, `LLM_BASE_URL=http://localhost:1234/v1`, `LLM_MODEL` leer. Das sind zeitgebundene Konfigurationswerte, keine dauerhafte Modellfestlegung.
- `get_model_name()` fragt die Modellliste ab. Ohne konfigurierte Modell-ID wird die erste zurückgegebene ID verwendet. Eine leere Modellliste führt zum Fehler.
- Der Aufruf nutzt `client.chat.completions.create(...)` mit System-/Benutzertext und Temperatur 0.1.
- JSON wird per Prompt angefordert, aus der Antwort extrahiert und anschließend durch Pydantic geprüft. Es wird kein API-seitig erzwungenes JSON-Schema übergeben.
- Es gibt genau eine Agent-Funktion. Keine Agentenübergaben, Tool-Calling-Schleife, LangGraph-, n8n-, MCP- oder FastAPI-Anbindung.
- `LLM_PROVIDER == "local"` wählt den Modellaufruf. Jeder andere Wert führt in den derzeit fehlerhaften Demo-Zweig; es gibt keinen aktiven OpenAI-Cloud-Zweig.
- `openai` und `demo` kommen noch als erlaubte RunRecord-Modi beziehungsweise GUI-Anzeigetexte vor. Das belegt keinen funktionierenden aktuellen Providerpfad.

## Datenmodell

| Klasse | Inhalt |
|---|---|
| BoxParameters | Positive Länge, Breite und Höhe; jeweils höchstens 100.000 mm. |
| CylinderParameters | Positiver Radius bis 50.000 mm und Höhe bis 100.000 mm. |
| SphereParameters | Positiver Radius bis 50.000 mm. |
| CadInstruction | Operation, optionale Geometrieparameter und Begründung mit 1–1.000 Zeichen. |
| StepMetadata | Dateiname, Bounding-Box-Abmessungen, Solid-Anzahl und Volumen. |
| RunRecord | Run-ID, Modus, Benutzerwunsch, optionale Eingabepfade/STEP-Metadaten, Anweisung und Ausgabepfad. |

Erlaubte Operationen: `create_box`, `create_cylinder`, `create_sphere`, `copy_input_step`.

Seit 10.09.2026 sind `EngineeringProject`, `Product`, `Component`, `AssemblyRelation`, `Process`, `Operation` als Prozessobjekt, `CapabilityRequirement`, `AssetRequirement`, `CanonicalAsset`, `MatchResult`, `DataValue`, `GeometryReference`, `SourceReference`, `AutomationConcept`, `ResourceAssignment`, `LayoutPlan`, `SceneObject` und `Pose` im separaten Paket `aied.models` vorhanden. `DataStatus` enthält `known`, `unknown`, `estimated`, `derived`, `not_applicable`; `MatchStatus` enthält `pass`, `fail`, `unknown`. Semantische IDs, Einheiten und Quellen werden gespeichert, aber nicht normalisiert oder extern aufgelöst. Die oben genannten v0.1-Klassen verwenden dieses neue Modell noch nicht.

## Eingaben, CAD und GUI

- Mindestens PDF, STEP oder nichtleerer Text ist erforderlich.
- PDF-Verarbeitung liest Text; keine OCR, Bildinterpretation oder besondere Tabellenextraktion.
- STEP-Kontext für das LLM enthält Bounding Box, Solid-Anzahl und Volumen, nicht die vollständige Geometrie oder Baugruppenstruktur.
- Quader werden in X/Y zentriert mit Unterseite bei Z=0 erzeugt; Zylinder werden in Z extrudiert; Kugeln entstehen am Workplane-Ursprung.
- `copy_input_step` kopiert die Datei und verlangt einen Eingabepfad.
- Der Viewer tesselliert STEP-Geometrie. Beim Laden wird die vorherige Szene gelöscht; Input und Output sind abwechselnd, nicht gemeinsam dargestellt.
- Ein QObject-Worker in einem QThread führt die Pipeline aus. Fehler werden als Meldung und Traceback angezeigt.
- Das Textfeld heißt auch „Feedback“, aber es gibt keinen gespeicherten mehrstufigen Dialogkontext oder automatischen Replanning-Loop.

## Persistenz und vorhandene Ergebnisse

Nach der Anweisungserzeugung wird eine Run-ID aus Datum/Uhrzeit und UUID-Anteil erzeugt. `data/outputs/<run_id>/` enthält die STEP-Ausgabe und bei abgeschlossener Protokollierung `run.json`.

RunRecord speichert keine vollständige Prompt-/Modellversion, keinen extrahierten PDF-Text, keine Rohantwort und keinen fachlichen ValidationReport. Es gibt kein gesondertes persistiertes Fehlerprotokoll für jeden fehlgeschlagenen Lauf.

Bestandsaufnahme am 09.09.2026:

- 14 STEP-Dateien in 14 Run-Ordnern, davon zwölf mit `run.json`.
- Die zwölf Protokolle enthalten einen historischen Demo-Lauf und elf lokale LLM-Läufe.
- Alle zwölf Protokolle haben `pdf_file`, `step_file` und `step_metadata` auf `null`.
- `data/inputs/` enthält nur `.gitkeep`; ausgewählte Dateien werden nicht automatisch dorthin kopiert.

| Lokaler Beleg | Ergebnis / Bedeutung |
|---|---|
| `data/outputs/20260903_235557_a6ca13d7/run.json` | Quader 20 × 40 × 60 mm; entsprechender STEP-Körper vorhanden. |
| `data/outputs/20260909_002130_15bd48a6/run.json` | Kugelradius 4 cm wurde zu 40 mm; STEP-Abmessungen 80 × 80 × 80 mm. |
| `data/outputs/20260909_002151_78a4d14d/run.json` | Kugelradius 10 cm wurde zu 100 mm; STEP-Abmessungen 200 × 200 × 200 mm. |
| `data/outputs/20260909_002336_e4b23954/run.json` | Wunsch nach zwei Kugeln; nur eine Kugel mit Radius 20 mm ausgegeben. |
| `data/outputs/20260903_235857_1f1824e3/run.json` | Explizite 150 cm wurden eigenmächtig auf 150 mm reduziert. |
| `data/outputs/20260909_002222_6750a268/run.json` | Nicht vorgegebene Breite und Höhe wurden als plausible Maße ergänzt. |

Die historischen Protokolle belegen erfolgreiche einfache Geometrieerzeugung, nicht allgemeine Auftragstreue oder aktuelle End-to-End-Zuverlässigkeit.

## Bekannte technische Probleme

1. **Demo-Aufruf fehlerhaft:** In `pipeline.py` wird `_demo_instruction(user_request)` aufgerufen, obwohl `_demo_instruction()` keine Argumente akzeptiert. Der Nicht-local-Zweig führt damit zu einem TypeError. Ein früherer gespeicherter Demo-Erfolg widerspricht diesem heutigen Codefehler nicht.
2. **Quaderparameterprüfung fehlerhaft:** In `CadInstruction.validate_parameters()` steht bei fehlenden Box-Parametern eine wirkungslose Variablenannotation statt einer Fehlermeldung. `create_box` ohne `box` wird akzeptiert und scheitert später beim Zugriff auf Parameter. Zylinder und Kugel besitzen die entsprechende Fehlermeldung.
3. **Auftragserfüllung wird nicht geprüft:** Anzahl der Objekte, geforderte Maße, Einheiten und räumliche Beziehungen werden nicht mit der Ausgabe verglichen. Gespeicherte Zweikugel- und 150-cm-Anfragen zeigen konkrete Abweichungen.
4. **Annahmen sind nicht strukturiert markiert:** Das Modell ergänzt fehlende Maße; diese werden als gewöhnliche Zahlen gespeichert. Ein freier `reason` ersetzt keinen Datenzustand oder Quellenbeleg.
5. **Keine fachliche/geometrische Ergebnisvalidierung in der Pipeline:** Es gibt keine separate Prüfung auf Kollision, Erreichbarkeit, Auftragstreue oder technische Machbarkeit nach der Erzeugung. Erfolgreicher Export und Viewer-Import ersetzen diese Prüfung nicht.
6. **Metadaten können unvollständig sein:** `inspect_step()` verwendet `obj.val()` für die Bounding Box und zählt/summiert Solids separat. Fehler bei einer Solid-Volumenberechnung werden still übersprungen; eine solche unvollständige Summe wird nicht als unsicher gekennzeichnet.
7. **Protokollierung ist unvollständig:** Zwei historische Ausgaben haben kein RunRecord. Bei Fehlern nach dem STEP-Export kann eine Datei ohne abgeschlossenen Datensatz zurückbleiben.

## Unterschiede zur Dokumentation und Zielarchitektur

- README und `.env.example` beschreiben noch OpenAI-Key/Agents-SDK und automatischen Demo-Betrieb; der Code verwendet inzwischen die lokale Modellanbindung. README-Aussagen sind daher nicht durchgehend aktuelle Implementierungswahrheit.
- Im Prompt wird auf Prüfungen im Engineering Core verwiesen. Der aktuelle Core erzeugt Geometrie, enthält aber keinen eigenständigen fachlichen Validation-Workflow.
- Asset Factory, Project Planner und Validation Factory sind nicht als vollständige Module vorhanden.
- Keine Asset-Bibliothek, externen Source Adapter, AAS-/BaSyx-/MQTT-Anbindung oder Integration des separaten Machbarkeitsassistenten.
- Keine generische Prozessplanung, Konzeptvarianten, Capability-Zuordnung oder Bewertung/Ranking.
- Keine Mehrteilanordnung, allgemeine Translation/Rotation, Kollisionsprüfung, IK, Motion Planning, URDF-/USD-Ausgabe oder Simulation.
- Separater erster Datenvertrag mit Schema-Version und Quellenreferenzen vorhanden; keine Migration, Persistenzanbindung oder Quellennormalisierung für das Generic Data Model.
- `.gitignore` ignoriert `.env`, `.venv`, Python-Caches und Run-Ausgaben. Eingabedateien unter `data/inputs/` sind derzeit nicht allgemein ausgeschlossen.
- `tests/test_generic_models.py` prüft die neuen Datenverträge; `tests/test_legacy_workflow.py` prüft bestehende Schemas und die lokale Pipeline mit gemocktem LLM und echtem CAD in temporären Verzeichnissen.

### Abgleich mit dem neu akzeptierten Montage-Ziel

Die folgenden Unterschiede sind fehlende Implementierung, keine Arbeitsaufträge. Der vollständige Zielumfang steht ausschließlich in `PROJECT_BRAIN.md`.

| Bereich | IMPLEMENTED CURRENT STATE / konkrete Lücke |
|---|---|
| Mehrere Produktdateien | GUI und Pipeline verwalten einen optionalen STEP-Pfad; kein Mehrdatei-Produktimport. AssemblyRelation und mehrere GeometryReferences sind als separate Datenverträge vorhanden. |
| Geometry Preprocessing | Bounding-Box-Abmessungen, Volumen und Solid-Anzahl vorhanden; keine strukturierte Zentrum-/Topologieausgabe oder automatisch gespeicherte Standardansichten. GeometryReference ist nur als Datenvertrag vorhanden. |
| ProductProcessAnalysisAgent | Nicht vorhanden. `run_engineering_agent()` liefert ausschließlich CadInstruction; der API-Aufruf übergibt Text, keine Renderbilder. |
| EngineeringProject / PPRContext | EngineeringProject mit optionalem Product/Process, Resources, AutomationConcepts und DataValue-Metadaten implementiert; keine Agent-/Workflow-Anbindung und kein zweiter PPRContext-Typ. |
| Datenzustände und Referenzen | DataValue, SourceReference und GeometryReference implementiert. Unbekannte/nicht anwendbare Werte müssen null sein; bekannte/geschätzte/abgeleitete Werte dürfen nicht null sein. |
| Abstraktes Automatisierungskonzept | AutomationConcept und generische AssetRequirements als Datenverträge vorhanden; kein AutomationConceptPlanner. |
| Lokale Asset Factory | CanonicalAsset als Datenvertrag vorhanden; weiterhin keine lokale Asset Library und kein Local Asset Adapter/Normalizer. |
| Ressourcen-/Prozesszuordnung | ResourceAssignment und MatchResult als Datenverträge vorhanden; kein ResourceProcessAssignment-Service oder Anforderungs-Matching. |
| Layout | LayoutPlan, SceneObject und Pose als Datenverträge vorhanden; kein LayoutBuilder oder Transformationsalgorithmus. |
| Gemeinsame Szene | Kein SceneComposer. Der Viewer lädt eine STEP-Datei und löscht die vorherige Darstellung. |

Der heutige Code enthält weiterhin keine industrielle Validation, Simulation oder Bewertung. Ihr Ausschluss aus der nächsten Zielstufe ändert nichts an den dokumentierten heutigen Softwarefehlern; diese wurden nicht behoben.

## Verifikationsumfang

Für die anschließende Stabilisierung am 10.09.2026:

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **33 Tests bestanden**, keine übersprungenen Tests, Laufzeit 16,600 s, Exitcode 0.
- 28 Modelltests einschließlich aller neun Constraint-Operatoren, Operandformen, Property-/Semantic References, hard/soft, offener Capability-/Interface-Typen, Provenance, Confidence-Grenzen, neuer Listen-IDs und JSON-Roundtrips. Die fünf bestehenden Legacy-Tests blieben unverändert und bestanden einschließlich echter STEP-Erzeugung und STEP-Kopie mit gemocktem LLM.
- `git diff --check` erfolgreich; keine Änderungen an Agents, Pipeline, GUI, CAD-Services, Prompts, Legacy-Schemas, `base.py` oder `spatial.py`. Keine GUI-/Live-LLM-Prüfung.

Für die ursprüngliche Generic-Data-Model-Erweiterung am 10.09.2026:

- `.venv\Scripts\python.exe -m unittest discover -s tests -v`: **26 Tests bestanden**, keine übersprungenen Tests, Laufzeit 6,389 s, Exitcode 0; Python 3.11.9 und Pydantic 2.13.5.
- 21 Modelltests prüfen Datenzustände, JSON-Typen/Roundtrips, JSON-Schema-Erzeugung, Erweiterbarkeit, Referenzen, Stückzahlen, Posen, Revalidierung und einen von Workflow/CAD/GUI unabhängigen Import.
- Fünf Legacy-Tests prüfen bestehende Schema-Imports, vier CAD-Operationen, RunRecord-Roundtrips und zwei Pipeline-Läufe mit gemocktem Agenten. Ein Quader wurde tatsächlich als STEP exportiert und eingelesen (20 × 40 × 60 mm, ein Solid, 48.000 mm³); eine erzeugte Kugel-STEP wurde bytegleich kopiert. Alle Testausgaben liegen in automatisch bereinigten temporären Verzeichnissen.
- Ein vorheriger Gesamtlauf wurde wegen verzögertem CAD-Import abgebrochen. Ein anschließender Diagnoselauf meldete erfolgreiche Tests, endete aber nach einem Timeout mit Exitcode 1. Erst der oben genannte normale Wiederholungslauf belegt den uneingeschränkten Testerfolg.
- Kein GUI- oder Live-LLM-Test. Der vorhandene Demo-Fehler und die fehlende Box-Parameterprüfung wurden nicht behoben. Bestehende Workflow-Quelldateien sind unverändert.

Bei der vorangegangenen rein lesenden Analyse:

- Alle 14 lokalen Python-Dateien wurden erfolgreich syntaktisch geparst.
- Die fehlerhafte Annahme von `create_box` ohne Parameter wurde isoliert reproduziert.
- Funktionssignatur und Aufruf im Demo-Zweig wurden verglichen; das Argumentzahlproblem ist im Code belegt.
- Die vorhandenen 14 STEP-Dateien wurden eingelesen. Die ausgegebenen Prüfdaten zeigten jeweils einen Solid und `isValid() == True`; Bounding Boxes wurden ermittelt. Der Prüfprozess endete anschließend ohne weiteren Fehltext mit Exitcode 1. Das ist kein uneingeschränkt erfolgreicher Gesamttest und keine im Produkt implementierte Validation.
- Es wurde kein neuer LLM-/GUI-End-to-End-Lauf gestartet und keine neue CAD-Ausgabe erzeugt.

Bei Erstellung dieser Dokumentation wurden Schema, Pipeline und Konfiguration erneut gelesen. Bekannte Probleme wurden dokumentiert, nicht behoben. Source Code und bestehende CAD-Ergebnisse blieben unverändert.

Beim späteren Dokumentationsabgleich zur Montage-Richtung wurden die vorhandenen Klassen, Funktionen, STEP-Pfade und der Viewer-Wechsel lesend geprüft sowie das Fehlen von `data/asset_library/` festgestellt. Keine erneuten Laufzeittests, keine neuen CAD-Ausgaben und keine Source-Code-Änderung.
