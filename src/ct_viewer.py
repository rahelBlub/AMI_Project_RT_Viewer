import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider
import matplotlib.image as mpimg

class CTViewer:
    CMAP = "grey"
    INTERPOLATION = "nearest"
    PATIENT_VIEW_PATH = "./data/images/patient_planes.png"

    def __init__(self, volume: np.ndarray[tuple[int, ...], np.dtype[...]], voxelspacing: tuple[float, float, float], dose_volume=None, dose_alpha=0.4):
        self.overview_img = mpimg.imread("./data/images/patient_planes.png")
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
        self._create_images()
        self._create_sliders()

    def _create_figure(self):
        self.fig, self.axs = plt.subplots(2, 2, figsize=(10, 8))

        self.ax_axial = self.axs[0, 0]
        self.ax_sagittal = self.axs[0, 1]
        self.ax_coronal = self.axs[1, 1]
        self.ax_overview = self.axs[1, 0]

        #plt.subplots_adjust(bottom=0.25)

    def _create_images(self):
        self.img_axial = self.ax_axial.imshow(
            self.apply_window(
                self.volume[self.z_idx, :, :],
                self.window_center,
                self.window_width,
            ),
            cmap=self.CMAP,
            interpolation=self.INTERPOLATION,
            aspect=self.dy / self.dx,
        )
        self.ax_axial.set_title("Axial")

        self.img_sagittal = self.ax_sagittal.imshow(
            self.apply_window(self.volume[:, :, self.x_idx],
                              self.window_center,
                              self.window_width,
                              ),
            cmap=self.CMAP,
            interpolation=self.INTERPOLATION,
            aspect=self.dz / self.dy,
        )
        self.ax_sagittal.set_title("Sagittal")

        self.img_coronal = self.ax_coronal.imshow(
            self.apply_window(self.volume[:, self.y_idx, :], self.window_center, self.window_width),
            cmap=self.CMAP,
            interpolation=self.INTERPOLATION,
            aspect=self.dz / self.dx,
        )
        self.ax_coronal.set_title("Coronal")

        self.img_overview = self.ax_overview.imshow(self.overview_img)
        self.ax_overview.set_title("Overview")

    def _create_sliders(self):

        #TODO: FRONTEND - Die Slider überlagern die Bilder
        ax_slider_z = plt.axes((0.15, 0.15, 0.65, 0.03))
        self.slider_z = Slider(
            ax_slider_z,
            "Axial",
            0,
            self.volume.shape[0] - 1,
            valinit=self.z_idx,
            valstep=1,
        )

        ax_slider_y = plt.axes((0.15, 0.10, 0.65, 0.03))
        self.slider_y = Slider(
            ax_slider_y,
            "Coronal",
            0,
            self.volume.shape[1] - 1,
            valinit=self.y_idx,
            valstep=1,
        )

        ax_slider_x = plt.axes((0.15, 0.05, 0.65, 0.03))
        self.slider_x = Slider(
            ax_slider_x,
            "Sagittal",
            0,
            self.volume.shape[2] - 1,
            valinit=self.x_idx,
            valstep=1,
        )

        ax_wc = plt.axes((0.15, 0.20, 0.65, 0.03))
        self.slider_wc = Slider(
            ax_wc,
            "Center",
            -1000,
            1000,
            valinit=self.window_center,
        )

        ax_ww = plt.axes((0.15, 0.25, 0.65, 0.03))
        self.slider_ww = Slider(
            ax_ww,
            "Width",
            1,
            3000,
            valinit=self.window_width,
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
