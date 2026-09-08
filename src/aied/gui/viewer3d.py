from pathlib import Path

import pyvista as pv
from pyvistaqt import QtInteractor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from aied.services.cad_service import step_to_mesh_data


class StepViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.info_label = QLabel("Noch kein 3D-Modell geladen")
        self.info_label.setStyleSheet("color: #94a3b8;")

        self.reset_button = QPushButton("Kamera zurücksetzen")
        self.reset_button.clicked.connect(self.reset_camera)

        toolbar.addWidget(self.info_label, 1)
        toolbar.addWidget(self.reset_button)
        layout.addLayout(toolbar)

        self.plotter = QtInteractor(self)
        layout.addWidget(self.plotter.interactor, 1)

        self.plotter.set_background("#0a0f1a")
        self.plotter.show_axes()
        self.plotter.show_grid()

    def load_step(self, step_path: Path):
        vertices, faces = step_to_mesh_data(step_path)
        mesh = pv.PolyData(vertices, faces)

        self.plotter.clear()
        self.plotter.add_mesh(
            mesh,
            smooth_shading=True,
            show_edges=True,
            edge_color="#334155",
            color="#93c5fd",
        )
        self.plotter.show_axes()
        self.plotter.show_grid()
        self.plotter.reset_camera()
        self.plotter.render()

        self.info_label.setText(step_path.name)

    def reset_camera(self):
        self.plotter.reset_camera()
        self.plotter.render()

    def closeEvent(self, event):
        self.plotter.close()
        super().closeEvent(event)
