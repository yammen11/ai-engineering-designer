from pathlib import Path
import traceback

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QFrame,
    QLabel,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QMessageBox,
    QSplitter,
)

from aied.services.pipeline import execute_pipeline
from aied.gui.viewer3d import StepViewer


class PipelineWorker(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, pdf_path, step_path, user_request):
        super().__init__()
        self.pdf_path = pdf_path
        self.step_path = step_path
        self.user_request = user_request

    def run(self):
        try:
            result = execute_pipeline(
                pdf_path=self.pdf_path,
                step_path=self.step_path,
                user_request=self.user_request,
            )
            self.finished.emit(result)
        except Exception:
            self.failed.emit(traceback.format_exc())


def make_card():
    frame = QFrame()
    frame.setObjectName("Card")
    return frame


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.pdf_path: Path | None = None
        self.step_path: Path | None = None
        self.last_output_step: Path | None = None
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("AI Engineering Designer – v0.1")
        self.resize(1450, 900)
        self.setMinimumSize(1100, 720)

        root = QWidget()
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(22, 18, 22, 22)
        root_layout.setSpacing(14)

        title = QLabel("AI Engineering Designer")
        title.setObjectName("Title")
        subtitle = QLabel(
            "v0.1 · PDF + STEP + Text → Engineering Agent → CadQuery/OpenCascade → STEP → 3D"
        )
        subtitle.setObjectName("Subtitle")

        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        splitter = QSplitter()
        root_layout.addWidget(splitter, 1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 8, 0)
        left_layout.setSpacing(12)

        input_card = make_card()
        input_layout = QVBoxLayout(input_card)

        section = QLabel("1 · Eingaben")
        section.setObjectName("SectionTitle")
        input_layout.addWidget(section)

        grid = QGridLayout()

        pdf_btn = QPushButton("PDF auswählen")
        pdf_btn.clicked.connect(self.choose_pdf)
        self.pdf_label = QLabel("Keine PDF ausgewählt")
        self.pdf_label.setObjectName("PathLabel")

        step_btn = QPushButton("STEP auswählen")
        step_btn.clicked.connect(self.choose_step)
        self.step_label = QLabel("Keine STEP-Datei ausgewählt")
        self.step_label.setObjectName("PathLabel")

        grid.addWidget(pdf_btn, 0, 0)
        grid.addWidget(self.pdf_label, 0, 1)
        grid.addWidget(step_btn, 1, 0)
        grid.addWidget(self.step_label, 1, 1)

        input_layout.addLayout(grid)

        self.show_input_step_btn = QPushButton("Input STEP im 3D-Viewer anzeigen")
        self.show_input_step_btn.setEnabled(False)
        self.show_input_step_btn.clicked.connect(self.show_input_step)
        input_layout.addWidget(self.show_input_step_btn)

        prompt_card = make_card()
        prompt_layout = QVBoxLayout(prompt_card)

        section2 = QLabel("2 · Zusätzlicher Wunsch / Feedback")
        section2.setObjectName("SectionTitle")
        prompt_layout.addWidget(section2)

        hint = QLabel(
            "Beispiel: „Erzeuge eine Platte 200 × 100 × 20 mm.“ "
            "Der interne Agent-Prompt liegt separat unter prompts/."
        )
        hint.setWordWrap(True)
        hint.setObjectName("Subtitle")
        prompt_layout.addWidget(hint)

        self.user_prompt = QTextEdit()
        self.user_prompt.setPlaceholderText(
            "Beschreibe hier, was das System mit PDF/STEP tun oder erzeugen soll..."
        )
        self.user_prompt.setMinimumHeight(150)
        prompt_layout.addWidget(self.user_prompt)

        run_card = make_card()
        run_layout = QVBoxLayout(run_card)

        section3 = QLabel("3 · Pipeline")
        section3.setObjectName("SectionTitle")
        run_layout.addWidget(section3)

        self.run_button = QPushButton("▶  RUN")
        self.run_button.setObjectName("PrimaryButton")
        self.run_button.clicked.connect(self.start_pipeline)
        run_layout.addWidget(self.run_button)

        self.status_label = QLabel("Bereit.")
        self.status_label.setObjectName("Subtitle")
        self.status_label.setWordWrap(True)
        run_layout.addWidget(self.status_label)

        output_card = make_card()
        output_layout = QVBoxLayout(output_card)

        section4 = QLabel("4 · Ergebnis")
        section4.setObjectName("SectionTitle")
        output_layout.addWidget(section4)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText(
            "Nach RUN erscheinen hier Run-ID, Agent-Entscheidung und Output-Pfad."
        )
        output_layout.addWidget(self.result_text)

        self.show_output_btn = QPushButton("Output STEP im 3D-Viewer anzeigen")
        self.show_output_btn.setEnabled(False)
        self.show_output_btn.clicked.connect(self.show_output_step)
        output_layout.addWidget(self.show_output_btn)

        left_layout.addWidget(input_card)
        left_layout.addWidget(prompt_card)
        left_layout.addWidget(run_card)
        left_layout.addWidget(output_card, 1)

        right_card = make_card()
        right_layout = QVBoxLayout(right_card)

        viewer_title = QLabel("Interaktive 3D-Ansicht")
        viewer_title.setObjectName("SectionTitle")
        right_layout.addWidget(viewer_title)

        viewer_hint = QLabel(
            "3D-Modell mit Maus drehen, zoomen und verschieben."
        )
        viewer_hint.setObjectName("Subtitle")
        right_layout.addWidget(viewer_hint)

        self.viewer = StepViewer()
        right_layout.addWidget(self.viewer, 1)

        splitter.addWidget(left)
        splitter.addWidget(right_card)
        splitter.setSizes([500, 900])

    def choose_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "PDF auswählen",
            "",
            "PDF Files (*.pdf)",
        )
        if file_name:
            self.pdf_path = Path(file_name)
            self.pdf_label.setText(str(self.pdf_path))

    def choose_step(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "STEP auswählen",
            "",
            "STEP Files (*.step *.stp)",
        )
        if file_name:
            self.step_path = Path(file_name)
            self.step_label.setText(str(self.step_path))
            self.show_input_step_btn.setEnabled(True)

    def show_input_step(self):
        if not self.step_path:
            return
        try:
            self.viewer.load_step(self.step_path)
            self.set_status("Input-STEP wurde geladen.", "good")
        except Exception as exc:
            QMessageBox.critical(
                self,
                "STEP-Fehler",
                f"Die STEP-Datei konnte nicht angezeigt werden:\n\n{exc}",
            )

    def show_output_step(self):
        if not self.last_output_step:
            return
        try:
            self.viewer.load_step(self.last_output_step)
        except Exception as exc:
            QMessageBox.critical(
                self,
                "STEP-Fehler",
                f"Der Output konnte nicht angezeigt werden:\n\n{exc}",
            )

    def start_pipeline(self):
        user_request = self.user_prompt.toPlainText().strip()

        if not self.pdf_path and not self.step_path and not user_request:
            QMessageBox.information(
                self,
                "Eingabe fehlt",
                "Bitte mindestens PDF, STEP oder einen Textwunsch angeben.",
            )
            return

        self.run_button.setEnabled(False)
        self.set_status("Pipeline läuft …", "busy")
        self.result_text.setPlainText("")

        self.worker_thread = QThread(self)
        self.worker = PipelineWorker(
            self.pdf_path,
            self.step_path,
            user_request,
        )

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.pipeline_finished)
        self.worker.failed.connect(self.pipeline_failed)

        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.failed.connect(self.worker_thread.quit)

        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    def pipeline_finished(self, record):
        self.run_button.setEnabled(True)
        self.last_output_step = Path(record.output_step)
        self.show_output_btn.setEnabled(True)

        if record.mode == "local":

            mode_text = "LOCAL LLM"

        elif record.mode == "openai":

            mode_text = "OpenAI Agent"

        else:

            mode_text = "DEMO MODE"

        self.result_text.setPlainText(
            f"Run ID: {record.run_id}\n"
            f"Modus: {mode_text}\n\n"
            f"Agent/CAD-Anweisung:\n"
            f"{record.instruction.model_dump_json(indent=2)}\n\n"
            f"Output STEP:\n{record.output_step}"
        )

        try:
            self.viewer.load_step(self.last_output_step)
        except Exception as exc:
            self.set_status(
                f"STEP wurde erzeugt, aber 3D-Anzeige meldet: {exc}",
                "bad",
            )
            return

        self.set_status(
            f"Erfolgreich. Output: {record.output_step}",
            "good",
        )

    def pipeline_failed(self, details):
        self.run_button.setEnabled(True)
        self.set_status("Pipeline ist fehlgeschlagen.", "bad")
        self.result_text.setPlainText(details)

        QMessageBox.critical(
            self,
            "Pipeline-Fehler",
            "Die Pipeline ist fehlgeschlagen.\n\n"
            "Die genaue Fehlermeldung steht links im Ergebnisfeld.\n"
            "Kopiere sie vollständig und sende sie mir.",
        )

    def set_status(self, text: str, kind: str):
        object_name = {
            "good": "StatusGood",
            "busy": "StatusBusy",
            "bad": "StatusBad",
        }.get(kind, "Subtitle")

        self.status_label.setObjectName(object_name)
        self.status_label.setText(text)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
