from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow, QGridLayout, QSlider, QLabel,
    QVBoxLayout, QHBoxLayout, QWidget
)
import numpy as np
import matplotlib.image as mpimg

from src.patient import Patient
from src.dicom_handler import DicomHandler

PATIENT_VIEW_PATH = "./data/images/patient_planes.png"
WINDOW_CENTER = 40
WINDOW_WIDTH = 400


class ViewPanel(QWidget):
    BORDER = {"Axial": "#00cc44", "Sagittal": "#ff3333", "Coronal": "#3399ff"}
    SPINE_COLOR = {"Axial": "#00cc44", "Sagittal": "#ff3333", "Coronal": "#3399ff"}

    def __init__(self, view: str, n_slices: int, pat: Patient = None, parent=None):
        super().__init__(parent)
        self.view = view
        self.pat = pat
        color = self.BORDER[view]
        self.setStyleSheet(f"border: 2px solid {color}; border-radius: 4px;")
        self.setStyleSheet("background-color: #111111;")

        self.fig = Figure(facecolor="#111111")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#111111")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        for spine in self.ax.spines.values():
            spine.set_visible(True)
            spine.set_edgecolor(self.SPINE_COLOR[view])
            spine.set_linewidth(2.5)
        self.fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setStyleSheet("border: none;")

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



class CTViewer(QMainWindow):
    CMAP = "grey"
    INTERPOLATION = "nearest"

    def __init__(self, patient: Patient):
        super().__init__()
        self.setWindowTitle(
            f"{patient.get_patient_name()}  {patient.get_patient_age()}  {patient.get_patient_sex()}"
        )
        self.setStyleSheet("background-color: #1a1a1a; color: white;")

        self.overview_img = mpimg.imread(PATIENT_VIEW_PATH)
        self.pat = patient
        d_handler = DicomHandler(patient)

        self.ct_volume = d_handler.create_ct_volume_with_HU()
        self.dx, self.dy, self.dz = d_handler.get_voxelspacing()

        self.dose_volume = None
        self.resampled_dose_volume = None
        self.ct_img = None
        self.dose_img = None

        if self.pat.get_rt_dose_path():
            self.ct_img = d_handler.get_ct_image(self.ct_volume, self.dx, self.dy, self.dz)
            self.dose_img = d_handler.get_dose_image()
            self.dose_volume = d_handler.get_rt_dose_volume()
            self.resampled_dose_volume = d_handler.resample_dose_volume(self.dose_img, self.ct_img)
            print("sitk_image min, max: ", self.resampled_dose_volume.min(), self.resampled_dose_volume.max())
            print("dose_volume:", self.dose_volume.shape)
            print("resampled_dose_volume:", self.resampled_dose_volume.shape)

        self.window_center = WINDOW_CENTER
        self.window_width = WINDOW_WIDTH

        self.z_idx = self.ct_volume.shape[0] // 2
        self.y_idx = self.ct_volume.shape[1] // 2
        self.x_idx = self.ct_volume.shape[2] // 2

        self.dose_axial = None
        self.dose_coronal = None
        self.dose_sagittal = None
        self.dose_colorbar = None
        self.iso_axial = None
        self.iso_sagittal = None
        self.iso_coronal = None

        self.dose_colorbars = []

        # --- ViewPanels ---
        self.panel_axial    = ViewPanel("Axial",    self.ct_volume.shape[0], self.pat)
        self.panel_sagittal = ViewPanel("Sagittal", self.ct_volume.shape[2], self.pat)
        self.panel_coronal  = ViewPanel("Coronal",  self.ct_volume.shape[1], self.pat)

        # Slider-Referenzen direkt aus den Panels
        self.slider_z = self.panel_axial.slider
        self.slider_x = self.panel_sagittal.slider
        self.slider_y = self.panel_coronal.slider

        # Axes-Referenzen direkt aus den Panels
        self.ax_axial    = self.panel_axial.ax
        self.ax_sagittal = self.panel_sagittal.ax
        self.ax_coronal  = self.panel_coronal.ax

        # --- Overview Panel ---
        self.panel_overview = QWidget()
        self.panel_overview.setStyleSheet("border: 1px solid #444; border-radius: 4px;")
        ov_fig = Figure(facecolor="#111111")
        ov_ax = ov_fig.add_subplot(111)
        ov_ax.imshow(self.overview_img)
        ov_ax.set_xticks([]); ov_ax.set_yticks([])
        ov_ax.set_title("Overview", color="white", fontsize=10)
        ov_ax.set_facecolor("#111111")
        ov_fig.subplots_adjust(left=0, right=1, top=0.92, bottom=0)
        ov_canvas = FigureCanvasQTAgg(ov_fig)
        ov_canvas.setStyleSheet("border: none;")
        ov_layout = QVBoxLayout(self.panel_overview)
        ov_layout.setContentsMargins(0, 0, 0, 0)
        ov_layout.addWidget(ov_canvas)

        # --- Grid Layout ---
        grid = QGridLayout()
        grid.setSpacing(6)
        grid.addWidget(self.panel_axial,    0, 0)
        grid.addWidget(self.panel_sagittal, 0, 1)
        grid.addWidget(self.panel_coronal,  1, 0)
        grid.addWidget(self.panel_overview, 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 1)

        # --- Globale Sliders (Window Center / Width) ---
        self.slider_wc = QSlider(Qt.Orientation.Horizontal)
        self.slider_wc.setRange(-1000, 1000)
        self.slider_wc.setValue(self.window_center)

        self.slider_ww = QSlider(Qt.Orientation.Horizontal)
        self.slider_ww.setRange(1, 3000)
        self.slider_ww.setValue(self.window_width)

        lbl_style = "border: none; color: white; font-size: 11px;"
        bottom = QHBoxLayout()
        bottom.setContentsMargins(8, 4, 8, 4)
        bottom.addWidget(QLabel("Window Center", styleSheet=lbl_style))
        bottom.addWidget(self.slider_wc)
        bottom.addWidget(QLabel("Window Width (HU)", styleSheet=lbl_style))
        bottom.addWidget(self.slider_ww)

        # --- Status Label ---
        self.status_label = QLabel("")
        self.status_label.setStyleSheet(
            "border: none; color: #aaa; font-family: monospace; font-size: 11px; padding: 2px 8px;"
        )

        # --- Root Layout ---
        root = QVBoxLayout()
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(4)
        root.addLayout(grid)
        root.addLayout(bottom)
        root.addWidget(self.status_label)

        central = QWidget()
        central.setLayout(root)
        self.setCentralWidget(central)

        # --- Signals verbinden ---
        self.slider_z.valueChanged.connect(self._update)
        self.slider_y.valueChanged.connect(self._update)
        self.slider_x.valueChanged.connect(self._update)
        self.slider_wc.valueChanged.connect(self._update)
        self.slider_ww.valueChanged.connect(self._update)

        # Hover
        self.panel_axial.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.panel_sagittal.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.panel_coronal.canvas.mpl_connect("motion_notify_event", self._on_hover)

        # Initiales Zeichnen
        self._draw_all()

    # ------------------------------------------------------------------ helpers

    def _get_ct_slice(self, view: str, idx: int):
        if view == "Axial":
            return self.ct_volume[idx, :, :], self.dy / self.dx
        if view == "Coronal":
            return self.ct_volume[:, idx, :], self.dz / self.dx
        if view == "Sagittal":
            return self.ct_volume[:, :, idx], self.dz / self.dy
        raise ValueError("Unknown view")

    def _get_dose_slice(self, view: str, idx: int):
        if view == "Axial":
            return self.resampled_dose_volume[idx, :, :], self.dy / self.dx
        if view == "Coronal":
            return self.resampled_dose_volume[:, idx, :], self.dz / self.dx
        if view == "Sagittal":
            return self.resampled_dose_volume[:, :, idx], self.dz / self.dy
        raise ValueError("Unknown view")

    @staticmethod
    def apply_window(image, center, width):
        return image.clip(center - width / 2, center + width / 2)

    def _add_overlay_title(self, ax, text: str):
        ax.text(
            0.02, 0.97, text,
            transform=ax.transAxes,
            fontsize=11, color="white",
            va="top", ha="left",
            bbox=dict(facecolor="black", alpha=0.45, edgecolor="none", pad=3),
        )

    # ------------------------------------------------------------------ drawing

    def _draw_ct(self, ax, view: str, idx: int):
        ct_slice, aspect = self._get_ct_slice(view, idx)
        ct_slice = self.apply_window(ct_slice, self.window_center, self.window_width)
        img = ax.imshow(ct_slice, cmap=self.CMAP, interpolation=self.INTERPOLATION, aspect=aspect)
        self._add_overlay_title(ax, view)
        return img

    def _draw_dose(self, ax, view: str, idx: int, fig: Figure):
        dose_slice, aspect = self._get_dose_slice(view, idx)
        global_max = np.max(self.resampled_dose_volume)
        threshold = 0.05 * global_max
        img_dose = ax.imshow(
            dose_slice,
            cmap="jet", alpha=0.6,
            vmin=threshold,
            vmax=global_max,
            aspect=aspect,
        )
        return img_dose

    def _draw_iso(self, ax, view: str, idx: int):
        dose_slice, _ = self._get_dose_slice(view, idx)
        global_max = np.max(self.resampled_dose_volume)
        threshold = 0.05 * global_max
        levels = [l for l in [0.1, 0.2, 0.5, 0.8] if threshold < l * global_max <= np.max(dose_slice)]
        levels = [l * global_max for l in levels]
        if not levels:
            return None
        dose_win = self.apply_window(dose_slice, self.window_center, self.window_width)
        return ax.contour(
            dose_win, levels=levels,
            colors=["blue", "green", "yellow", "red"][:len(levels)],
            linewidths=0.5,
        )

    def _draw_all(self):
        has_dose = self.dose_volume is not None

        for panel, view, idx in [
            (self.panel_axial,    "Axial",    self.z_idx),
            (self.panel_sagittal, "Sagittal", self.x_idx),
            (self.panel_coronal,  "Coronal",  self.y_idx),
        ]:
            panel.ax.cla()
            panel.ax.set_xticks([])
            panel.ax.set_yticks([])
            for spine in panel.ax.spines.values():
                spine.set_visible(False)

        self.img_axial    = self._draw_ct(self.ax_axial,    "Axial",    self.z_idx)
        self.img_sagittal = self._draw_ct(self.ax_sagittal, "Sagittal", self.x_idx)
        self.img_coronal  = self._draw_ct(self.ax_coronal,  "Coronal",  self.y_idx)

        if has_dose:
            self.dose_axial    = self._draw_dose(self.ax_axial,    "Axial",    self.z_idx, self.panel_axial.fig)
            self.dose_sagittal = self._draw_dose(self.ax_sagittal, "Sagittal", self.x_idx, self.panel_sagittal.fig)
            self.dose_coronal  = self._draw_dose(self.ax_coronal,  "Coronal",  self.y_idx, self.panel_coronal.fig)

            # Colorbar in allen drei Panels
            for panel, dose_img in [
                (self.panel_axial, self.dose_axial),
                (self.panel_sagittal, self.dose_sagittal),
                (self.panel_coronal, self.dose_coronal),
            ]:
                cb = panel.fig.colorbar(
                    dose_img, ax=panel.ax,
                    location="right", shrink=0.85, pad=0.02,
                )
                cb.set_label("Dose [Gy]", color="white")
                cb.ax.yaxis.set_tick_params(color="white")
                for lbl in cb.ax.get_yticklabels():
                    lbl.set_color("white")

            # Referenz auf axiale Colorbar für update_normal
            self.dose_colorbar = self.panel_axial.fig.axes[-1]

            self.iso_axial    = self._draw_iso(self.ax_axial,    "Axial",    self.z_idx)
            self.iso_sagittal = self._draw_iso(self.ax_sagittal, "Sagittal", self.x_idx)
            self.iso_coronal  = self._draw_iso(self.ax_coronal,  "Coronal",  self.y_idx)

            self._update_dose_stats("Axial", self.z_idx)

        for panel in [self.panel_axial, self.panel_sagittal, self.panel_coronal]:
            panel.canvas.draw_idle()

    # ------------------------------------------------------------------ update

    def _update(self):
        z = self.slider_z.value()
        y = self.slider_y.value()
        x = self.slider_x.value()
        self.window_center = self.slider_wc.value()
        self.window_width  = self.slider_ww.value()
        self.z_idx, self.y_idx, self.x_idx = z, y, x

        self.img_axial.set_data(
            self.apply_window(self.ct_volume[z, :, :], self.window_center, self.window_width))
        self.img_sagittal.set_data(
            self.apply_window(self.ct_volume[:, :, x], self.window_center, self.window_width))
        self.img_coronal.set_data(
            self.apply_window(self.ct_volume[:, y, :], self.window_center, self.window_width))

        if self.dose_volume is not None:
            self.dose_axial.set_data(self.resampled_dose_volume[z, :, :])
            self.dose_sagittal.set_data(self.resampled_dose_volume[:, :, x])
            self.dose_coronal.set_data(self.resampled_dose_volume[:, y, :])
            #self.dose_colorbar.update_normal(self.dose_axial)
            for cb, dose_img in zip(self.dose_colorbars, [self.dose_axial, self.dose_sagittal, self.dose_coronal]):
                cb.update_normal(dose_img)

            for iso_attr, ax, view, idx in [
                ("iso_axial",    self.ax_axial,    "Axial",    z),
                ("iso_sagittal", self.ax_sagittal, "Sagittal", x),
                ("iso_coronal",  self.ax_coronal,  "Coronal",  y),
            ]:
                iso = getattr(self, iso_attr)
                if iso:
                    iso.remove()
                setattr(self, iso_attr, self._draw_iso(ax, view, idx))

            self._update_dose_stats("Axial", z)

        for panel in [self.panel_axial, self.panel_sagittal, self.panel_coronal]:
            panel.canvas.draw_idle()

    # ------------------------------------------------------------------ status

    def _update_dose_stats(self, view: str, idx: int):
        if self.resampled_dose_volume is None:
            return
        dose_slice, _ = self._get_dose_slice(view, idx)
        valid = dose_slice[dose_slice > 0]
        if valid.size == 0:
            stats = f"{view} — keine Dosiswerte in dieser Schicht"
        else:
            stats = (f"{view}  |  Min: {valid.min():.2f} Gy  "
                     f"Max: {valid.max():.2f} Gy  Mean: {valid.mean():.2f} Gy")
        self.status_label.setText(stats)

    def _on_hover(self, event):
        mapping = [
            (self.panel_axial.ax,    "Axial",    self.z_idx),
            (self.panel_sagittal.ax, "Sagittal", self.x_idx),
            (self.panel_coronal.ax,  "Coronal",  self.y_idx),
        ]
        if self.resampled_dose_volume is None:
            return
        for ax, view, idx in mapping:
            if event.inaxes == ax and event.xdata is not None:
                x, y = int(event.xdata), int(event.ydata)
                dose_slice, _ = self._get_dose_slice(view, idx)
                h, w = dose_slice.shape
                if 0 <= y < h and 0 <= x < w:
                    val = dose_slice[y, x]
                    self.status_label.setText(
                        f"{view}  |  x={x} y={y}  →  {val:.2f} Gy"
                    )
                return

    # ------------------------------------------------------------------ public

    def show_image_data(self):
        if self.ct_img is None:
            return
        print("CT")
        print("Size:", self.ct_img.GetSize())
        print("Spacing:", self.ct_img.GetSpacing())
        print("Origin:", self.ct_img.GetOrigin())
        if self.dose_img is not None:
            print("DOSE")
            print("Size:", self.dose_img.GetSize())
            print("Spacing:", self.dose_img.GetSpacing())
            print("Origin:", self.dose_img.GetOrigin())

    def change_cmap(self, new_cmap="grey"):
        self.CMAP = new_cmap

    def change_interpolation(self, new_interpolation="nearest"):
        self.INTERPOLATION = new_interpolation