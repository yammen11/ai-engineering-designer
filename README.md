# AI Engineering Designer – v0.1

Erster kleiner, sauber strukturierter Prototyp:

**PDF + STEP + Benutzerwunsch → 1 Engineering Agent → strukturierte CAD-Anweisung → CadQuery/OpenCascade → STEP-Datei → interaktive 3D-Anzeige**

Zusätzlich steht ein separates **Generic Data Model in Pydantic v2** unter
`aied.models` bereit. Datenverträge und Testbefehle: [Generic Data Model](docs/GENERIC_DATA_MODEL.md).
Ein [synthetisches JSON-Beispiel](examples/generic_project.json) zeigt die Verwendung.
Der bestehende v0.1-Workflow verwendet weiterhin unverändert `aied.schemas`.

## Warum diese Architektur?

Das LLM schreibt **nicht direkt rohe STEP-Geometrie**. Es liefert eine kontrollierte, strukturierte CAD-Anweisung. Die reale Geometrie wird deterministisch durch Python + CadQuery/OpenCascade erzeugt.

Damit bleibt die Software später:
- testbar
- reproduzierbar
- erweiterbar
- für weitere Agents und Tools vorbereitet

## Voraussetzungen

Empfohlen:
- Windows 10/11
- **Python 3.11 (64 Bit)**
- VS Code
- Internetzugang für die OpenAI API

## Installation

1. Projekt entpacken.
2. Ordner in VS Code öffnen.
3. `install.bat` doppelklicken.

Alternativ im VS-Code-Terminal:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## API-Key

Kopiere `.env.example` zu `.env` und trage ein:

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=
```

`OPENAI_MODEL` kann leer bleiben. Dann verwendet das Agents SDK sein Standardmodell.

## Start

```powershell
.venv\Scripts\activate
python app.py
```

oder `run.bat` doppelklicken.

## v0.1 kann

### Input
- PDF
- STEP
- zusätzlicher Benutzertext

### PDF
Der Text wird lokal mit PyMuPDF extrahiert.

### STEP
Die STEP-Datei wird lokal mit CadQuery/OpenCascade gelesen. Dem Agenten werden in v0.1 zunächst technische Metadaten gegeben:
- Bounding Box
- Anzahl Solids
- Volumen

### Agent
Ein einzelner Engineering Agent erhält:
- internen Prompt aus `prompts/engineering_agent.txt`
- PDF-Kontext
- STEP-Metadaten
- Benutzerwunsch

Er erzeugt eine typisierte `CadInstruction`.

### CAD-Ausgabe
v0.1 unterstützt:
- Box
- Cylinder
- Sphere
- vorhandene STEP-Datei kopieren

### Run-Ordner
Jeder Lauf bekommt eine eigene ID:

`data/outputs/<run_id>/`

Darin:
- `output.step`
- `run.json`

### 3D
Interaktiver Viewer:
- drehen
- zoomen
- verschieben
- Kamera zurücksetzen

## Demo-Modus

Ohne API-Key läuft die App trotzdem und erzeugt eine 100 × 60 × 20 mm Testbox.

Dadurch kannst du zuerst prüfen:

**GUI → Pipeline → CAD → STEP → 3D**

und erst danach OpenAI anschließen.

## Projektstruktur

```text
ai_engineering_designer_v0_1/
│
├── app.py
├── requirements.txt
├── install.bat
├── run.bat
├── .env.example
├── .gitignore
│
├── prompts/
│   └── engineering_agent.txt
│
├── data/
│   ├── inputs/
│   └── outputs/
│
└── src/
    └── aied/
        ├── config.py
        ├── schemas.py
        ├── agents/
        │   └── engineering_agent.py
        ├── services/
        │   ├── pdf_service.py
        │   ├── cad_service.py
        │   └── pipeline.py
        └── gui/
            ├── main_window.py
            ├── viewer3d.py
            └── styles.py
```

## Früh festgelegte Basis

### Einheit
- CAD-Längen: **mm**
- Winkel später: **deg**
- Masse später: **kg**
- Zeit später: **s**

### Daten zwischen AI und Engineering Core
Keine freien Textbefehle, sondern Pydantic-Schemas.

Beispiel:

```json
{
  "operation": "create_box",
  "box": {
    "length_mm": 200,
    "width_mm": 100,
    "height_mm": 20
  },
  "reason": "..."
}
```

### Jeder Run bleibt erhalten
Nichts wird automatisch überschrieben. Das ist wichtig für Evaluation, Debugging und Reproduzierbarkeit.

### GUI ist nicht der Engineering Core
Dateiverarbeitung, CAD und Agentenlogik liegen außerhalb der GUI. Dadurch kann später dieselbe Basis mit Desktop-GUI, Web-GUI, API, MCP oder n8n verwendet werden.

## Nächster Schritt v0.2

Erst wenn v0.1 lokal läuft:

1. echte CAD-Python-Funktionen als Agent-Tools:
   - `inspect_step()`
   - `create_box()`
   - `move_part()`
   - `rotate_part()`
   - `export_step()`
2. Input und Output gleichzeitig im Viewer
3. Translation/Rotation Datenmodell
4. Beispiel „Kugel mittig auf obere Fläche des Quaders“
5. automatische geometrische Validierung

**Erst danach** teilen wir den einen Agenten in Planner/CAD/Validation auf.
