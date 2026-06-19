import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import axes
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.widgets import Slider
import matplotlib.image as mpimg

from src.helper.dict_to_list import dict_to_list
from src.helper.ui_theme import *

PATIENT_VIEW_PATH = "./data/images/patient_planes.png"


class CTViewer:
    CMAP = "grey"
    INTERPOLATION = "nearest"

    def __init__(self, volume: np.ndarray[tuple[int, ...], np.dtype[...]], voxelspacing: tuple[float, float, float], metadata: dict, dose_volume=None, dose_alpha=0.4):
        self.overview_img = mpimg.imread("./data/images/patient_planes.png")
        self.metadata: dict[str, str] = metadata
        self.volume = volume
        self.dx, self.dy, self.dz = voxelspacing

        self.dose_volume = dose_volume
        self.dose_alpha = dose_alpha

        self.window_center = 40
        self.window_width = 400

        self.z_idx = volume.shape[0] // 2
        self.y_idx = volume.shape[1] // 2
        self.x_idx = volume.shape[2] // 2

        self._create_figure()
        self._create_image_view()
        self._create_sliders()

    def _create_figure(self):
        #self.fig, self.axs = plt.subplots(2, 2, figsize=(FIG_WIDTH, FIG_HEIGHT), facecolor="black")
        self.fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
        gs = self.fig.add_gridspec(2, 1, height_ratios=[4, 1]) # seperate space for global slider
        gs_top = gs[0].subgridspec(2, 2)
        gs_bottom = gs[1].subgridspec(2, 1)
        #
        # for ax in self.axs.flat:
        #     ax.set_facecolor(AX_BG)
        #     ax.set_xticks([])
        #     ax.set_yticks([])

        # {
        #     0 "PatientName": image.PatientName,
        #     1 "PatientAge": image.PatientAge,
        #     2 "PatientSex": image.PatientSex,
        #     3 "BodyPartExamined": image.BodyPartExamined,
        #     4 "SliceThickness": image.SliceThickness,
        #     5 "PatientPosition": image.PatientPosition,
        # }

        metadata_list = dict_to_list(self.metadata)
        # aus dem Alter '0' am Anfang und Buchstaben generell entfernen:
        metadata_list[1] = re.sub(r'^0+|[A-Za-z]+$', '', metadata_list[1])

        self.fig.canvas.manager.set_window_title(metadata_list[0] + " " + metadata_list[1] + " " + metadata_list[2])

        self.fig.text(
            0.02,
            0.925,
            "Body Part: "
            + metadata_list[3]
            + "\nSlice Thickness: "
            + metadata_list[4]
            + "\nPatient Position: "
            + metadata_list[5],
            fontsize=12,
            color='w'
        )

        # Bilder im oberen Grid anordnen
        self.ax_axial = self.fig.add_subplot(gs_top[0, 0])
        self.ax_sagittal = self.fig.add_subplot(gs_top[0, 1])
        self.ax_coronal = self.fig.add_subplot(gs_top[1, 0])
        self.ax_overview = self.fig.add_subplot(gs_top[1, 1])

        # Achsen-Slider unter Bilder anordnen
        self.ax_slider_z = self.slider_below(self.ax_axial, self.fig)
        self.ax_slider_y = self.slider_below(self.ax_coronal, self.fig)
        self.ax_slider_x = self.slider_below(self.ax_sagittal, self.fig)

        # extra Slider im unteren Grid anordnen
        self.ax_window = self.fig.add_subplot(gs_bottom[0])
        self.ax_slices = self.fig.add_subplot(gs_bottom[1])

        # self.ax_axial = self.axs[0, 0]
        # self.ax_sagittal = self.axs[0, 1]
        # self.ax_coronal = self.axs[1, 1]
        # self.ax_overview = self.axs[1, 0]

        self.ax_axial.axis("off")
        self.ax_sagittal.axis("off")
        self.ax_coronal.axis("off")
        self.ax_overview.axis("off")

    def _get_slice(self, view: str, idx: int):
        if view == "Axial":
            return self.volume[idx, :, :], self.dy / self.dx

        if view == "Coronal":
            return self.volume[:, idx, :], self.dz / self.dx

        if view == "Sagittal":
            return self.volume[:, :, idx], self.dz / self.dy

        raise ValueError("Unknown view")

    def create_image(self, axis, idx: int, title: str):
        image, aspect = self._get_slice(title, idx)

        img = axis.imshow(
            self.apply_window(image, self.window_center, self.window_width),
            cmap=self.CMAP,
            interpolation=self.INTERPOLATION,
            aspect=aspect,
        )

        axis.set_title(title)

        return img

    def render_dose(self, ax, dose):
        return ax.imshow(
            dose,
            cmap=DOSE_COLORMAP,
            alpha=DOSE_ALPHA
        )

    def render_seg(self, ax, seg):
        return ax.imshow(
            seg,
            cmap=SEG_COLORMAP,
            alpha=SEG_ALPHA
        )

    def _create_image_view(self):
        self.img_axial = self.create_image(
            self.ax_axial,
            self.z_idx,
            "Axial",
        )

        self.img_coronal = self.create_image(
            self.ax_coronal,
            self.y_idx,
            "Coronal",
        )

        self.img_sagittal = self.create_image(
            self.ax_sagittal,
            self.x_idx,
            "Sagittal",
        )

        self.img_overview = self.ax_overview.imshow(self.overview_img)
        self.ax_overview.set_title("Overview")

    # get image positions for slider orientation
    @staticmethod
    def slider_below(ax, fig, height=0.02, offset=0.04):
        bbox = ax.get_position()

        return fig.add_axes([
            bbox.x0,
            bbox.y0 - offset,
            bbox.width,
            height
        ])

    def _create_sliders(self):

        self.slider_z = Slider(
            self.ax_slider_z,
            "Axial",
            0,
            self.volume.shape[0] - 1,
            valinit=self.z_idx,
            valstep=1,
        )

        self.slider_y = Slider(
            self.ax_slider_y,
            "Coronal",
            0,
            self.volume.shape[1] - 1,
            valinit=self.y_idx,
            valstep=1,
        )

        self.slider_x = Slider(
            self.ax_slider_x,
            "Sagittal",
            0,
            self.volume.shape[2] - 1,
            valinit=self.x_idx,
            valstep=1,
        )

        self.slider_wc = create_slider(
            self.ax_window,
            "Window Center",
            -1000,
            1000,
            self.window_center,
            SLIDER_ACTIVE)

        self.slider_ww = create_slider(
            self.ax_slices,
            "Window Width (HU)",
            1,
            3000,
            self.window_width,
            SLIDER_ACTIVE,

        )

        self.slider_z.on_changed(self._update)
        self.slider_y.on_changed(self._update)
        self.slider_x.on_changed(self._update)
        self.slider_wc.on_changed(self._update)
        self.slider_ww.on_changed(self._update)

    def _update(self, val):
        z = int(self.slider_z.val)
        y = int(self.slider_y.val)
        x = int(self.slider_x.val)
        self.window_center = self.slider_wc.val
        self.window_width = self.slider_ww.val

        self.img_axial.set_data(self.apply_window(self.volume[z, :, :], self.window_center, self.window_width))
        self.img_sagittal.set_data(self.apply_window(self.volume[:, :, x], self.window_center, self.window_width))
        self.img_coronal.set_data(self.apply_window(self.volume[:, y, :], self.window_center, self.window_width))

        self.fig.canvas.draw_idle()

    def show(self):
        plt.show()

    @staticmethod
    def apply_window(image, center, width):
        lower = center - width / 2
        upper = center + width / 2

        return image.clip(lower, upper)

    def change_cmap(self, new_cmap="grey"):
        """
        change cmap variable, default = "grey"

        Possible values:
        "gray" | "grey", "binary", "bone", "gist_gray", "viridis",
        "plasma", "inferno", "magma", "cividis", "coolwarm", "bwr",
        "seismic", "RdBu", "PiYG", "Blues", "Greens", "Reds", "Purples",
        "Oranges", "YlGnBu", "jet", "rainbow", "turbo", "nipy_spectral"
        """
        self.CMAP = new_cmap

    def change_interpolation(self, new_interpolation="nearest"):
        """
        change interpolation variable, default = "nearest"

        Possible values:
        'none', 'auto', 'nearest', 'bilinear', 'bicubic', 'spline16',
        'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
        'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos',
        'blackman'
        """
        self.INTERPOLATION = new_interpolation
