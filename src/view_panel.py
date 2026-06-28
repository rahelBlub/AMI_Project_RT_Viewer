from PyQt6.QtWidgets import QWidget, QSlider, QVBoxLayout
from PyQt6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class ViewPanel(QWidget):
    """Canvas + Slider in einem Widget — Slider klebt automatisch drunter."""

    BORDER = {"Axial": "#00cc44", "Sagittal": "#ff3333", "Coronal": "#3399ff"}

    def __init__(self, view: str, n_slices: int, parent=None):
        super().__init__(parent)
        color = self.BORDER[view]
        self.view = view
        self.setStyleSheet(f"border: 2px solid {color}; border-radius: 4px;")

        self.fig = Figure(facecolor="#1a1a1a")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#111111")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setStyleSheet("border: none;")

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, n_slices - 1)
        self.slider.setValue(n_slices // 2)
        self.slider.setStyleSheet("QSlider { border: none; }")  # kein Rahmen auf Slider

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)          # 2 px Abstand Canvas → Slider
        layout.addWidget(self.canvas)
        layout.addWidget(self.slider)