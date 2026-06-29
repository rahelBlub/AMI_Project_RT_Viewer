from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QGridLayout, QSlider, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from src.patient import Patient

SPINE_COLOR = {"Axial": "#00cc44", "Sagittal": "#ff3333", "Coronal": "#3399ff"}

class ViewPanel(QWidget):

    def __init__(self, view: str, n_slices: int, pat: Patient = None, parent=None):
        super().__init__(parent)
        self.view = view
        self.pat = pat
        self.setStyleSheet("background-color: #111111;")

        self.fig = Figure(facecolor="#111111")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#111111")
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        for spine in self.ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(SPINE_COLOR[view])
            spine.set_linewidth(2.5)

        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setStyleSheet("border: solid")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, n_slices - 1)
        self.slider.setValue(n_slices // 2)
        self.slider.setStyleSheet("border: none; margin: 2px 4px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.canvas)
        layout.addWidget(self.slider)

        if pat is not None:
            self.fig.text(
                0.02, 0.02,
                f"Body Part: {self.pat.get_body_part_examined()}\n"
                f"Slice Thickness: {self.pat.get_slice_thickness()}\n"
                f"Patient Position: {self.pat.get_patient_position()}\n"
                f"Modality: {self.pat.get_modality()}",
                fontsize=9,
                color="w",
                va="bottom",
                transform=self.fig.transFigure,
            )
