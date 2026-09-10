# Generic Data Model

Implementiert am 10.09.2026 als separates Paket `src/aied/models/` mit Pydantic v2.
Der Auftrag umfasst ausschließlich Datenverträge, Beispiele und Tests.
`aied.schemas`, Agent, Pipeline, CAD-Services, GUI, Prompts und Konfiguration bleiben unverändert.
Der v0.1-Workflow verwendet weiterhin `CadInstruction`, `StepMetadata` und `RunRecord`.

Die Core-Objekte stammen aus `PROJECT_BRAIN.md`. Dort offene Detailfelder wurden für
diesen Implementierungsschritt bewusst klein konkretisiert. Sie sind hier als
Implementierungsvertrag dokumentiert, nicht als bereits früher beschlossene Architektur.
Es entstehen keine Planner, Source Adapter, Matching-Algorithmen oder Layout-Services.

Stabilisierung am 10.09.2026: Das bestehende Modell bleibt erhalten und wird auf
ausdrücklichen Benutzerauftrag um `Capability`, `Constraint`, `AssetInterface`
und `DataValue.confidence` ergänzt. Der generische Datenvertrag trägt jetzt `1.1`.

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
| `Capability` | Freier Typ in `capability`, optionale Bezeichnung in `name`, flexible `parameters: dict[str, DataValue]` sowie geerbte Eigenschaften, semantische ID und Quellen. |
| `Constraint` | Property-/Semantic Reference, Operator, qualifizierter DataValue-Vergleichswert und `strength` (`hard`/`soft`). |
| `CapabilityRequirement` | Freier Fähigkeitsname, erforderliche Eigenschaften in `properties` und optionale Liste `constraints`. |
| `AssetRequirement` | Optionale Ressourcenrolle, Stückzahl, CapabilityRequirements, Operation-IDs und optionale Liste `constraints`. |
| `AssetInterface` | Offener `interface_type`, optionaler frei benannter `standard`, technische Details in `properties` sowie semantische ID und Quellen. |
| `CanonicalAsset` | Freier Asset-Typ, Eigenschaften, Geometrie und Capabilities. Keine speziellen Robot-/Gripper-Unterklassen. |
| `AutomationConcept` | Optionaler Prozessbezug, AssetRequirements, ResourceAssignments und optionaler LayoutPlan. |
| `ResourceAssignment` | Verbindet eine AssetRequirement-ID mit einer Asset-ID und optional Operation-IDs/MatchResult. Eine Zuordnung ist keine Freigabe. |
| `MatchResult` | Requirement-/Asset-ID, `pass`, `fail` oder standardmäßig `unknown`, optionale Begründung und DataValue-Evidenz. |
| `LayoutPlan` | Liste von SceneObjects; noch keine berechnete oder geprüfte Geometrie. |
| `SceneObject` | Eine Instanz einer Komponente oder eines Assets mit eigener ID; `pose=null` bedeutet noch nicht platziert. |
| `Pose` | Translation in mm, Rotation in Grad, benanntes Referenzsystem. |
| `GeometryReference` | ID, URI/Pfad, optionales Format, Quelle und Eigenschaften; lädt keine Datei. |
| `SourceReference` | ID, freier Quellentyp, optional URI/Pfad, Fundstelle und Beschreibung. |
| `DataValue` | JSON-Wert mit Datenzustand, optional Einheit, semantischer ID, Quellen, Beschreibung, Ableitung und `confidence` in 0.0–1.0. |

Identifizierbare Engineering-Objekte besitzen außerdem optionale Namen,
Beschreibungen, `semantic_id`, `sources` und `properties: dict[str, DataValue]`.
Namen sind keine IDs. IDs werden vom Aufrufer vergeben und nicht automatisch generiert.
Capability-Namen, Asset-Typen und Beziehungstypen sind offen; es gibt keine feste
Zuordnung etwa von `handling` zu einem Roboter.

`CanonicalAsset.capabilities` ist eine Liste eigenständiger `Capability`-Objekte.
Parameter liegen beispielsweise unter `capability.parameters["payload"]`.
Mehrere Capabilities dürfen denselben Typ besitzen, benötigen innerhalb eines
Assets aber unterschiedliche IDs. Leere Parameter enthalten keine Aussage zu
Leistungsgrenzen. Die geerbten `properties` bleiben für weitere Eigenschaften verfügbar.

`CanonicalAsset.interfaces` enthält mehrere `AssetInterface`-Objekte mit je Asset
eindeutigen IDs. `interface_type` kann beispielsweise `mechanical`, `electrical`,
`communication`, `pneumatic`, `hydraulic`, `software` oder ein zukünftiger Typ sein.
Auch Standards sind freie Bezeichner; es gibt keine feste Normenliste und keine
automatische Aussage über Kompatibilität.

## Constraints

Eine `Constraint` benötigt eine ID, mindestens eine nichtleere `property_ref`
oder `semantic_ref`, einen Operator und `value: DataValue`. Beide Referenzen dürfen
gemeinsam dieselbe Zieleigenschaft bezeichnen. `semantic_ref` bezeichnet die
Zieleigenschaft; die geerbte `semantic_id` beschreibt die Constraint selbst.
Die Referenzen sind Bezeichner ohne implementierte Pfadauflösung.

```python
from aied.models import Constraint, DataValue

limit = Constraint(
    id="mass-limit", property_ref="mass", operator="<=", strength="soft",
    value=DataValue(status="estimated", value=2, unit="kg", confidence=0.6),
)
```

`strength` ist `hard` (Standard) oder `soft`, ohne Ranking, Gewichtung oder
automatische Auswertung. Wert und Einheit stehen gemeinsam in `value`; ein
zusätzliches, möglicherweise widersprüchliches Constraint-Einheitenfeld existiert nicht.

| Operator | Form des vorhandenen Vergleichswerts |
|---|---|
| `=`, `!=` | Beliebiger nicht-null JSON-Wert. |
| `>`, `>=`, `<`, `<=` | Numerischer Wert, kein Boolescher Wert oder Zahlenstring. |
| `between` | Zwei numerische inklusive Grenzen `[lower, upper]` mit `lower <= upper`. |
| `in` | Nichtleere JSON-Liste von Alternativen; die Zieleigenschaft soll eines ihrer Elemente sein. |
| `contains` | JSON-Element oder Textfragment, das in der Zieleigenschaft enthalten sein soll. |

Unbekannte oder nicht anwendbare Vergleichswerte bleiben als entsprechender
`DataValue` mit `null` darstellbar, auch für `between` und `in`. Es erfolgt nur
Strukturprüfung. Typkompatibilität mit tatsächlichen Asset-Werten,
Einheitenumrechnung, Grenzwertvergleich und Aggregation sind nicht implementiert.
Bestehende Anforderungs-`properties` bleiben gültig und werden nicht automatisch
in Constraints übersetzt. Constraint-IDs sind je Anforderung eindeutig.

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

`confidence` ist optional (`None`) und akzeptiert endliche Zahlen einschließlich
0.0 und 1.0; Boolesche Werte und Zahlenstrings sind unzulässig. Es ist eine vom
Ersteller angegebene Vertrauensangabe, kein kalibrierter Eignungsnachweis. Das Feld
ändert weder Datenzustand noch Matching-Ergebnis und ist bei allen Datenzuständen
zulässig. Fehlende Confidence wird nicht automatisch ergänzt.

## Strukturprüfung und Grenzen

Unbekannte Modellfelder sind verboten (`extra="forbid"`); Erweiterungen gehören
in die dafür vorgesehenen Wörterbücher. IDs und deren Schlüssel dürfen nicht leer
oder ausschließlich Leerraum sein. Stückzahlen akzeptieren keine Booleschen Werte,
Zahlenstrings oder gebrochenen Zahlen.

Besitzende Container prüfen eindeutige IDs für Komponenten, Montagebeziehungen,
Operationen, Capabilities, Interfaces, Constraints, CapabilityRequirements, Anforderungen, Zuordnungen, Ressourcen,
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

`EngineeringProject.schema_version="1.1"` bezeichnet ausschließlich diesen neuen
Datenvertrag, nicht eine neue Anwendungsversion. Andere Versionen werden abgelehnt.
Die frühere Capability-Map aus Vertrag `1.0` wird nicht stillschweigend akzeptiert:
Sie ist durch die Liste eigenständiger Capability-Objekte ersetzt. Vorhandene
generische Dokumente müssen explizit angepasst werden (IDs/Typen vergeben,
Parameter übernehmen, Schema-Version setzen). Es existiert keine automatische
Migration. Die Legacy-v0.1-RunRecords sind davon unabhängig und unverändert.
`PPRContext` wird nicht als zweiter Typ oder
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
