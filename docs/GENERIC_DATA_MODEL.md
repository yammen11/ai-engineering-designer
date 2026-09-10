# Generic Data Model

Implementiert am 10.09.2026 als separates Paket `src/aied/models/` mit Pydantic v2.
Der Auftrag umfasst ausschließlich Datenverträge, Beispiele und Tests.
`aied.schemas`, Agent, Pipeline, CAD-Services, GUI, Prompts und Konfiguration bleiben unverändert.
Der v0.1-Workflow verwendet weiterhin `CadInstruction`, `StepMetadata` und `RunRecord`.

Die Core-Objekte stammen aus `PROJECT_BRAIN.md`. Dort offene Detailfelder wurden für
diesen Implementierungsschritt bewusst klein konkretisiert. Sie sind hier als
Implementierungsvertrag dokumentiert, nicht als bereits früher beschlossene Architektur.
Es entstehen keine Planner, Source Adapter, Matching-Algorithmen oder Layout-Services.

## Verwendung

Import mit `src` im Python-Suchpfad (wie beim bestehenden App-Start):

```python
from aied.models import DataValue, EngineeringProject

project = EngineeringProject(
    id="project-1",
    metadata={"goal": DataValue(status="known", value="Montage untersuchen")},
)
payload = project.model_dump_json(indent=2)
restored = EngineeringProject.model_validate_json(payload)
json_schema = EngineeringProject.model_json_schema()
```

`examples/generic_project.json` ist ein synthetisches Beispiel mit Grundplatte,
Winkelhalterung, zwei Schrauben, einer ausgewählten Prozessoperation und einem
noch ungeprüften Ressourcenbezug. Es ist weder der vollständige Montageprozess
noch ein Nachweis technischer Eignung. Die referenzierten STEP-Dateien müssen
zum Validieren des JSON nicht vorhanden sein.

## Objekte und Beziehungen

| Objekt | Vertrag |
|---|---|
| `EngineeringProject` | Projekt-ID, Metadaten, optional Product/Process, Resources und AutomationConcepts. Ein leeres Projekt mit ID ist gültig. |
| `Product` | Besitzt Components und AssemblyRelations. |
| `Component` | Generischer Produktbestandteil, positive ganzzahlige Stückzahl, Geometriereferenzen. |
| `AssemblyRelation` | Benannter Beziehungstyp zwischen zwei verschiedenen Komponenten des Produkts; optionale relative Pose. |
| `Process` | Besitzt Operations; Vorgänger werden über Operation-IDs bezeichnet. |
| `Operation` | Komponentenbezüge, Vorgänger und CapabilityRequirements. Kein CAD-Befehl. |
| `CapabilityRequirement` | Freier Fähigkeitsname und erforderliche Eigenschaften in `properties`. |
| `AssetRequirement` | Optionale Ressourcenrolle, Stückzahl, CapabilityRequirements und Operation-IDs. |
| `CanonicalAsset` | Freier Asset-Typ, Eigenschaften, Geometrie und Capabilities. Keine speziellen Robot-/Gripper-Unterklassen. |
| `AutomationConcept` | Optionaler Prozessbezug, AssetRequirements, ResourceAssignments und optionaler LayoutPlan. |
| `ResourceAssignment` | Verbindet eine AssetRequirement-ID mit einer Asset-ID und optional Operation-IDs/MatchResult. Eine Zuordnung ist keine Freigabe. |
| `MatchResult` | Requirement-/Asset-ID, `pass`, `fail` oder standardmäßig `unknown`, optionale Begründung und DataValue-Evidenz. |
| `LayoutPlan` | Liste von SceneObjects; noch keine berechnete oder geprüfte Geometrie. |
| `SceneObject` | Eine Instanz einer Komponente oder eines Assets mit eigener ID; `pose=null` bedeutet noch nicht platziert. |
| `Pose` | Translation in mm, Rotation in Grad, benanntes Referenzsystem. |
| `GeometryReference` | ID, URI/Pfad, optionales Format, Quelle und Eigenschaften; lädt keine Datei. |
| `SourceReference` | ID, freier Quellentyp, optional URI/Pfad, Fundstelle und Beschreibung. |
| `DataValue` | JSON-Wert mit Datenzustand, optional Einheit, semantischer ID, Quellen, Beschreibung und Ableitung. |

Identifizierbare Engineering-Objekte besitzen außerdem optionale Namen,
Beschreibungen, `semantic_id`, `sources` und `properties: dict[str, DataValue]`.
Namen sind keine IDs. IDs werden vom Aufrufer vergeben und nicht automatisch generiert.
Capability-Namen, Asset-Typen und Beziehungstypen sind offen; es gibt keine feste
Zuordnung etwa von `handling` zu einem Roboter.

`CanonicalAsset.capabilities` ist ein Wörterbuch von Fähigkeitsnamen zu
DataValue-Eigenschaften, beispielsweise `{"handling": {"payload": ...}}`.
Ein vorhandener Fähigkeitsname mit leerem Eigenschaftswörterbuch enthält keine
Aussage zu Leistungsgrenzen. Erforderliche Eigenschaften definieren noch keinen
Vergleichsoperator: Einheitennormalisierung, Grenzwertvergleich und Aggregation
bleiben Aufgaben einer späteren Matching-Komponente.

## Datenzustände

| Zustand | Zulässiger Wert |
|---|---|
| `known` | Nicht `null`. |
| `unknown` | Ausschließlich `null`; Standardzustand. |
| `estimated` | Nicht `null`. |
| `derived` | Nicht `null`; eine textuelle Ableitung kann angegeben werden. |
| `not_applicable` | Ausschließlich `null`. |

`0`, `false`, `""`, leere Listen und leere Objekte sind vorhandene Werte.
`DataValue(value=5)` benötigt deshalb zusätzlich einen passenden expliziten Zustand.
JSON-Skalare, Listen und Objekte sind zulässig; NaN, Infinity, Python-Objekte,
Bytes und nichttextuelle Objektschlüssel werden abgelehnt. Zahlenstrings werden
nicht automatisch in Zahlen umgewandelt. Ein Zustand beschreibt den gesamten
Wert; verschachtelte JSON-Nutzdaten besitzen keine automatisch abgeleiteten Einzelzustände.

Quellen und Ableitungsbeschreibungen sind optional, damit der Kontext schrittweise
aufgebaut werden kann. `known` allein ist daher kein unabhängig geprüfter Quellenbeleg.
Einheiten und semantische IDs werden gespeichert, nicht interpretiert.
Insbesondere wird `unknown` niemals automatisch zu `fail` oder `pass`.
`MatchResult` speichert ein explizites Ergebnis; es berechnet keines.

## Strukturprüfung und Grenzen

Unbekannte Modellfelder sind verboten (`extra="forbid"`); Erweiterungen gehören
in die dafür vorgesehenen Wörterbücher. IDs und deren Schlüssel dürfen nicht leer
oder ausschließlich Leerraum sein. Stückzahlen akzeptieren keine Booleschen Werte,
Zahlenstrings oder gebrochenen Zahlen.

Besitzende Container prüfen eindeutige IDs für Komponenten, Montagebeziehungen,
Operationen, CapabilityRequirements, Anforderungen, Zuordnungen, Ressourcen,
Konzepte und Szenenobjekte. Die ID-Namensräume gelten je Container/Objektart;
es gibt kein globales ID-Register. SourceReference und GeometryReference sind
eingebettete Referenzdaten ohne globalen Resolver.

Product prüft die Endpunkte seiner Beziehungen, Process die Vorgängerreferenzen,
AutomationConcept seine Anforderungszuordnungen und EngineeringProject die
übergreifenden Komponenten-, Prozess-, Operations-, Ressourcen- und Szenenbezüge.
Ein separat erzeugtes Objekt darf IDs enthalten, deren Ziele erst im zugehörigen
Container geprüft werden. Ein vollständiges EngineeringProject akzeptiert keine
hängenden Referenzen; noch unbekannte Beziehungen werden weggelassen.

Die Prüfung umfasst keine Prozessplanung oder mehrgliedrige Zyklenerkennung,
keine Mengenabdeckung von Zuordnungen, keine Eignung von Capabilities, keine
Auflösung von Koordinatenframes und keine technische/geometrische Machbarkeit.

Modelle und ihre Listen/Wörterbücher sind veränderbar. Nach Änderungen erneut
`EngineeringProject.model_validate(project)` aufrufen, bevor der Kontext an eine
andere Komponente übergeben wird. `revalidate_instances="always"` prüft dabei auch
vorhandene verschachtelte Modellinstanzen. Direkte Attribut-/Listenänderungen,
`model_construct()` und `model_copy(update=...)` sind keine Validierungsgrenzen.

## Pose und Versionierung

Für diesen Vertrag gilt ein rechtshändiges Koordinatensystem. Translation ist XYZ
in Millimetern; Rotation ist eine aktive extrinsische XYZ-Rotation in Grad:
`p_parent = Rz(rz) @ Ry(ry) @ Rx(rx) @ p_local + translation_mm`.
`frame_id` benennt das übergeordnete Referenzsystem (Standard `world`).
`Pose()` ist explizit die Identität; eine unbekannte Platzierung ist `None`.
Eine `AssemblyRelation.relative_pose` verwendet das lokale Frame ihrer
Elternkomponente; der Aufrufer muss dessen Namen in `frame_id` setzen.
Es werden keine Transformationen berechnet und keine Winkel normalisiert.

`EngineeringProject.schema_version="1.0"` bezeichnet ausschließlich diesen neuen
Datenvertrag, nicht eine neue Anwendungsversion. Andere Versionen werden abgelehnt.
Es existieren noch keine Migrationen. `PPRContext` wird nicht als zweiter Typ oder
Alias eingeführt; `EngineeringProject` erfüllt die Rolle des gemeinsamen Kontexts.

## Tests

Aus dem Projektordner:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Nur die Modelltests (ohne CAD-Abhängigkeiten):

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -p test_generic_models.py -v
```

Die Legacy-Tests prüfen bestehende Imports, alle vier CAD-Operationen,
RunRecord-JSON sowie STEP-Erzeugung und STEP-Kopie in temporären Verzeichnissen.
Der LLM-Aufruf wird dabei gemockt. Bei fehlenden CAD-Abhängigkeiten werden nur die
CAD-Integrationstests ausdrücklich übersprungen; Schema-Tests laufen weiterhin.
Kein GUI-/Live-LLM-Test. Die bereits dokumentierten Demo- und Box-Parameterfehler
werden durch diesen Auftrag nicht behoben.

Pydantic-Grundlage: [offizielle Dokumentation zu Modellkonfiguration und Validierung](https://pydantic.dev/docs/validation/latest/concepts/models/).
