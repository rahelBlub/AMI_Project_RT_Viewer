import numpy as np
import matplotlib.image as mpimg
import SimpleITK as sitk

from src.patient import Patient
from src.helper.ui_theme import *
from src.dicom_handler import DicomHandler

PATIENT_VIEW_PATH = "./data/images/patient_planes.png"
WINDOW_CENTER = 40
WINDOW_WIDTH = 400


class CTViewer:
    CMAP = "grey"
    INTERPOLATION = "nearest"

    def __init__(self, patient: Patient):
        self.overview_img = mpimg.imread(PATIENT_VIEW_PATH)

        self.pat = patient
        d_handler = DicomHandler(patient)

        self.ct_volume = d_handler.create_ct_volume_with_HU()
        self.dx, self.dy, self.dz = d_handler.get_voxelspacing()

        if self.pat.get_rt_dose_path():
            self.ct_img = d_handler.get_ct_image(self.ct_volume, self.dx, self.dy, self.dz)
            self.dose_img = d_handler.get_dose_image()
            #self.dose_img = d_handler.get_sitk_dose_image()
            self.dose_volume = d_handler.get_rt_dose_volume()
            self.resampled_dose_volume = d_handler.resample_dose_volume(self.dose_img, self.ct_img)

            # test des von sitk generierten image
            #dose_sitk = sitk.GetArrayFromImage(self.dose_volume)
            dose_sitk = self.resampled_dose_volume
            print("sitk_image min, max: ", dose_sitk.min(), dose_sitk.max())

            #self.resampled_dose_volume = self.dose_img.CopyInformation(self.ct_img)
            print("dose_volume:", self.dose_volume.shape)
            print(np.min(self.dose_volume), np.max(self.dose_volume))
            print("resampled_dose_volume:", self.resampled_dose_volume.shape)
            print(np.min(self.resampled_dose_volume), np.max(self.resampled_dose_volume))

        self.window_center = WINDOW_CENTER
        self.window_width = WINDOW_WIDTH

        self.z_idx = self.ct_volume.shape[0] // 2
        self.y_idx = self.ct_volume.shape[1] // 2
        self.x_idx = self.ct_volume.shape[2] // 2

        # Variablen für Gy-Dosis Skala
        self.dose_axial = None
        self.dose_coronal = None
        self.dose_sagittal = None
        self.dose_colorbar = None

        self.iso_axial = None
        self.iso_sagittal = None
        self.iso_coronal = None

    def show_image_data(self):

        print("CT")
        print("Size:", self.ct_img.GetSize())
        print("Spacing:", self.ct_img.GetSpacing())
        print("Origin:", self.ct_img.GetOrigin())
        print("Direction:", self.ct_img.GetDirection())
        print("TransformIndexToPhysikalPoint:")
        print(self.ct_img.TransformIndexToPhysicalPoint((0, 0, 0)))
        print(self.ct_img.TransformIndexToPhysicalPoint(
            tuple(s - 1 for s in self.ct_img.GetSize())
        ))

        print()

        print("DOSE")
        print("Size:", self.dose_img.GetSize())
        print("Spacing:", self.dose_img.GetSpacing())
        print("Origin:", self.dose_img.GetOrigin())
        print("Direction:", self.dose_img.GetDirection())
        print("TransformIndexToPhysikalPoint:")
        print(self.dose_img.TransformIndexToPhysicalPoint((0, 0, 0)))
        print(self.dose_img.TransformIndexToPhysicalPoint(
            tuple(s - 1 for s in self.dose_img.GetSize())
        ))

    def _create_figure(self):
        #self.fig = plt.subplots(2, 2, figsize=(FIG_WIDTH, FIG_HEIGHT))
        self.fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))

        # self.fig.subplots_adjust(
        #     left=0.03, right=0.97,
        #     top=0.92, bottom=0.18,
        #     hspace=0.35, wspace=0.1,
        # )
        #
        # gs = self.fig.add_gridspec(
        #     2, 2,
        #     left=0.03, right=0.97,
        #     top=0.92, bottom=0.22,
        #     hspace=0.35, wspace=0.1,
        # )

        gs = self.fig.add_gridspec(2, 1, height_ratios=[4, 1])
        gs_top = gs[0].subgridspec(2, 2)
        gs_bottom = gs[1].subgridspec(2, 1)

        self.fig.canvas.manager.set_window_title(
            f"{self.pat.get_patient_name()} {self.pat.get_patient_age()} {self.pat.get_patient_sex()}"
        )

        self.fig.text(
            0.02,
            0.925,
            f"Body Part: {self.pat.get_body_part_examined()} \nSlice Thickness: {self.pat.get_slice_thickness()} \nPatient Position: {self.pat.get_patient_position()} \nModality: {self.pat.get_modality()}",
            fontsize=11,
            color="w",
        )

        # Bilder im oberen Grid anordnen
        self.ax_axial = self.fig.add_subplot(gs_top[0, 0])
        self.ax_sagittal = self.fig.add_subplot(gs_top[0, 1])
        self.ax_coronal = self.fig.add_subplot(gs_top[1, 0])
        self.ax_overview = self.fig.add_subplot(gs_top[1, 1])

        for ax in [self.ax_axial, self.ax_sagittal, self.ax_coronal, self.ax_overview]:
            ax.axis("off")

        # Achsen-Slider unter Bilder anordnen
        # self.ax_slider_z = self.slider_below(self.ax_axial, self.fig)
        # self.ax_slider_y = self.slider_below(self.ax_coronal, self.fig)
        # self.ax_slider_x = self.slider_below(self.ax_sagittal, self.fig)
        self.ax_slider_z = self._slider_ax(self.ax_axial, self.fig)
        self.ax_slider_y = self._slider_ax(self.ax_coronal, self.fig)
        self.ax_slider_x = self._slider_ax(self.ax_sagittal, self.fig)

        # # extra Slider im unteren Grid anordnen
        self.ax_window = self.fig.add_subplot(gs_bottom[0])
        self.ax_slices = self.fig.add_subplot(gs_bottom[1])
        # Window-Slider ganz unten
        # self.ax_window = self.fig.add_axes([0.05, 0.10, 0.88, 0.018])
        # self.ax_slices = self.fig.add_axes([0.05, 0.06, 0.88, 0.018])

        # for ax in [self.ax_axial, self.ax_sagittal, self.ax_coronal]:
        #     ax.set_xticks([])
        #     ax.set_yticks([])
        #     ax.set_frame_on(False)

        self.status_text = self.fig.text(
            0.5, 0.01,
            "",
            fontsize=10,
            color="w",
            ha="center",
            va="bottom",
            fontfamily="monospace",
        )


    def _add_overlay_title(self, ax, text: str):
        ax.text(
            0.02, 0.97, text,
            transform=ax.transAxes,
            fontsize=11, color="white",
            va="top", ha="left",
            bbox=dict(
                facecolor="black",
                alpha=0.45,
                edgecolor="none",
                pad=3,
            ),
        )

    def _update_dose_stats(self, view: str, idx: int):
        dose_slice, _ = self._get_dose_slice(view, idx)
        valid = dose_slice[dose_slice > 0]

        if valid.size == 0:
            stats = f"{view} — keine Dosiswerte in dieser Schicht"
        else:
            stats = (
                f"{view}  |  "
                f"Min: {valid.min():.2f} Gy  "
                f"Max: {valid.max():.2f} Gy  "
                f"Mean: {valid.mean():.2f} Gy"
            )
        self.status_text.set_text(stats)

    def _on_hover(self, event):

        for ax, dose_attr, view, idx in [
            (self.ax_axial, "dose_axial", "Axial", self.z_idx),
            (self.ax_sagittal, "dose_sagittal", "Sagittal", self.x_idx),
            (self.ax_coronal, "dose_coronal", "Coronal", self.y_idx),
        ]:
            if event.inaxes == ax:
                x, y = int(event.xdata or 0), int(event.ydata or 0)
                dose_slice, _ = self._get_dose_slice(view, idx)

                h, w = dose_slice.shape
                if 0 <= y < h and 0 <= x < w:
                    val = dose_slice[y, x]
                    label = f"{view}  |  x={x} y={y}  →  {val:.2f} Gy"
                else:
                    label = ""

                self.status_text.set_text(label)
                self.fig.canvas.draw_idle()
                return

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

    def create_image(self, axis, idx: int, view: str):
        ct_slice, aspect = self._get_ct_slice(view, idx)

        ct_slice = self.apply_window(
            ct_slice,
            self.window_center,
            self.window_width,
        )

        img = axis.imshow(
            ct_slice,
            cmap=self.CMAP,
            interpolation=self.INTERPOLATION,
            aspect=aspect,
        )

        # axis.set_title(view)
        self._add_overlay_title(axis, view)

        return img


    def add_dose_image_to_view(self, axis, idx: int, view: str):
        dose_slice, aspect = self._get_dose_slice(view, idx)
        global_max = np.max(self.resampled_dose_volume)
        threshold = 0.05 * global_max

        dose_slice = self.apply_window(
            dose_slice,
            self.window_center,
            self.window_width,
        )

        img_dose = axis.imshow(
            dose_slice,
            cmap="jet",
            alpha=0.6,
            vmin=threshold,
            vmax=np.max(self.resampled_dose_volume),
            aspect=aspect,
        )

        # RT Dose Colorbar
        if self.dose_img is not None:
            self.dose_colorbar = self.fig.colorbar(
                img_dose,
                ax=[axis],
                location="right",
                shrink=0.85,
                pad=0.02,
            )
            self.dose_colorbar.set_label("Dose [Gy]")

        return img_dose

    def add_dose_iso_to_view(self, axis, idx: int, view: str):
        dose_slice, aspect = self._get_dose_slice(view, idx)

        global_max = np.max(self.resampled_dose_volume)
        threshold = 0.05 * global_max

        levels = [
            0.1 * global_max,
            0.2 * global_max,
            0.5 * global_max,
            0.8 * global_max,
        ]

        slice_max = np.max(dose_slice)
        levels = [lvl for lvl in levels if threshold < lvl <= slice_max]

        if not levels:
            return None

        dose_slice = self.apply_window(
            dose_slice,
            self.window_center,
            self.window_width,
        )

        isoline = axis.contour(
            dose_slice,
            levels=levels,
            colors=["blue", "green", "yellow", "red"][:len(levels)],
            linewidths=0.5,
        )

        return isoline

    def _create_image_view(self):
        ## Image Axial
        self.img_axial = self.create_image(
            self.ax_axial,
            self.z_idx,
            "Axial",
        )
        if self.dose_volume is not None:
            self.dose_axial = self.add_dose_image_to_view(
                self.ax_axial,
                self.z_idx,
                "Axial",
            )
            self.iso_axial = self.add_dose_iso_to_view(
                self.ax_axial,
                self.z_idx,
                "Axial",
            )

        ## Image Coronal
        self.img_coronal = self.create_image(
            self.ax_coronal,
            self.y_idx,
            "Coronal",
        )
        self.dose_coronal = self.add_dose_image_to_view(
            self.ax_coronal,
            self.y_idx,
            "Coronal",
        )
        self.iso_coronal = self.add_dose_iso_to_view(
            self.ax_coronal,
            self.y_idx,
            "Coronal",
        )

        ## Image Sagittal
        self.img_sagittal = self.create_image(
            self.ax_sagittal,
            self.x_idx,
            "Sagittal",
        )
        self.dose_sagittal = self.add_dose_image_to_view(
            self.ax_sagittal,
            self.x_idx,
            "Sagittal",
        )
        self.iso_sagittal = self.add_dose_iso_to_view(
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
        return fig.add_axes([bbox.x0, bbox.y0 - offset, bbox.width, height])

    @staticmethod
    def _slider_ax(ref_ax, fig, height=0.018):
        pos = ref_ax.get_position()
        return fig.add_axes(
            [pos.x0, pos.y0 - 0.045, pos.width, height],
            facecolor=FIG_BG,  # aus ui_theme
        )

    def _create_sliders(self):

        self.slider_z = Slider(
            self.ax_slider_z,
            "A",
            0,
            self.ct_volume.shape[0] - 1,
            valinit=self.z_idx,
            valstep=1,
        )

        self.slider_y = Slider(
            self.ax_slider_y,
            "C",
            0,
            self.ct_volume.shape[1] - 1,
            valinit=self.y_idx,
            valstep=1,
        )

        self.slider_x = Slider(
            self.ax_slider_x,
            "S",
            0,
            self.ct_volume.shape[2] - 1,
            valinit=self.x_idx,
            valstep=1,
        )

        self.slider_wc = create_slider(
            self.ax_window,
            "Window Center",
            -1000,
            1000,
            self.window_center,
            SLIDER_ACTIVE,
        )

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

        self.img_axial.set_data(
            self.apply_window(
                self.ct_volume[z, :, :], self.window_center, self.window_width
            )
        )
        self.img_sagittal.set_data(
            self.apply_window(
                self.ct_volume[:, :, x], self.window_center, self.window_width
            )
        )
        self.img_coronal.set_data(
            self.apply_window(
                self.ct_volume[:, y, :], self.window_center, self.window_width
            )
        )

        if self.dose_volume is not None:
            self.dose_axial.set_data(self.resampled_dose_volume[z, :, :])
            self.dose_sagittal.set_data(self.resampled_dose_volume[:, :, x])
            self.dose_coronal.set_data(self.resampled_dose_volume[:, y, :])

            self.dose_colorbar.update_normal(self.dose_axial)

            # Isolinien für alle drei Ansichten neu zeichnen
            for iso_attr, ax_attr, view, idx in [
                ("iso_axial", "ax_axial", "Axial", z),
                ("iso_sagittal", "ax_sagittal", "Sagittal", x),
                ("iso_coronal", "ax_coronal", "Coronal", y),
            ]:
                iso = getattr(self, iso_attr)
                if iso:
                    for coll in iso.collections:
                        coll.remove()
                setattr(
                    self,
                    iso_attr,
                    self.add_dose_iso_to_view(getattr(self, ax_attr), idx, view),
                )

                self.z_idx, self.y_idx, self.x_idx = z, y, x
                self._update_dose_stats("Axial", z)

        self.fig.canvas.draw_idle()

    def show(self):

        self._create_figure()
        self._create_image_view()
        self._create_sliders()
        self._update_dose_stats("Axial", self.z_idx)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover)
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
