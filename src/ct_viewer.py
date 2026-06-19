import numpy as np
import matplotlib.image as mpimg
import SimpleITK as sitk

from src.patient import Patient
from src.helper.ui_theme import *
from src.dicom_handler import DicomHandler

PATIENT_VIEW_PATH = "./data/images/patient_planes.png"


class CTViewer:
    CMAP = "grey"
    INTERPOLATION = "nearest"

    def __init__(self, patient: Patient):
        self.overview_img = mpimg.imread(PATIENT_VIEW_PATH)

        self.pat = patient
        d_handler = DicomHandler(patient)
        self.volume = d_handler.create_ct_volume_with_HU()
        self.dx, self.dy, self.dz = d_handler.get_voxelspacing()
        # self.dose_volume = d_handler.get_rtdose()

        # TODO: Resampling-kacke nochmal genauer anschauen checke es gerade nicht
        # Bekky: ich hab das gefunden https://github.com/brenthuisman/dosia/blob/master/dicom/__init__.py
        # resampling RT Dose
        ct_img = self.get_ct_image(d_handler.get_patient_image_position_patient())
        dose_img = d_handler.get_dose_image()

        print("CT")
        print("Size:", ct_img.GetSize())
        print("Spacing:", ct_img.GetSpacing())
        print("Origin:", ct_img.GetOrigin())
        print("Direction:", ct_img.GetDirection())

        print()

        print("DOSE")
        print("Size:", dose_img.GetSize())
        print("Spacing:", dose_img.GetSpacing())
        print("Origin:", dose_img.GetOrigin())
        print("Direction:", dose_img.GetDirection())

        self.dose_resampled = sitk.Resample(dose_img, ct_img, sitk.Transform(), sitk.sitkLinear, 0.0, sitk.sitkFloat32)
        # self.dose_resampled = self.resample_to_reference(dose_img, ct_img)
        self.dose_volume = sitk.GetArrayFromImage(self.dose_resampled)

        self.window_center = 40
        self.window_width = 400

        self.z_idx = self.volume.shape[0] // 2
        self.y_idx = self.volume.shape[1] // 2
        self.x_idx = self.volume.shape[2] // 2

        self._create_figure()
        self._create_image_view()
        self._create_sliders()

    def _create_figure(self):
        # self.fig, self.axs = plt.subplots(2, 2, figsize=(FIG_WIDTH, FIG_HEIGHT), facecolor="black")
        self.fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT), constrained_layout=True)
        gs = self.fig.add_gridspec(2, 1, height_ratios=[4, 1])  # seperate space for global slider
        gs_top = gs[0].subgridspec(2, 2)
        gs_bottom = gs[1].subgridspec(2, 1)

        self.fig.canvas.manager.set_window_title(
            f"{self.pat.get_patient_name()} {self.pat.get_patient_age()} {self.pat.get_patient_sex()}")

        self.fig.text(
            0.02,
            0.925,
            f"Body Part: {self.pat.get_body_part_examined()} \nSlice Thickness: {self.pat.get_slice_thickness()} \nPatient Position: {self.pat.get_patient_position()}",
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

        for ax in [self.ax_axial, self.ax_sagittal, self.ax_coronal]:
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_frame_on(False)

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

    def create_image(self, axis, idx: int, view: str):
        # CT-Slice holen
        ct_slice, aspect = self._get_slice(view, idx)

        ct_slice = self.apply_window(
            ct_slice,
            self.window_center,
            self.window_width,
        )

        # CT darstellen
        ct_img = axis.imshow(
            ct_slice,
            cmap=self.CMAP,
            interpolation=self.INTERPOLATION,
            aspect=aspect,
        )

        # RTDOSE darüber legen
        if self.dose_volume is not None:
            dose_slice, _ = self._get_slice(view, idx)

            dose_img = axis.imshow(
                dose_slice,
                cmap="jet",
                alpha=0.35,
                vmin=0,
                vmax=np.max(self.dose_volume),
                aspect=aspect,
            )

        axis.set_title(view)

        return ct_img, dose_img

    # TODO: die Patient ImagePositionPatient stimmt irgendwie nicht, Datentyp übeprüfen
    # Bekky: hab ein paar Ergänzungen zur Typsicherheit im Setter gemacht, musst ggf auf
    # None abfragen, falls die Daten nicht vorhanden sind

    def get_ct_image(self, image_position_patient):
        img = sitk.GetImageFromArray(self.volume.astype(np.float32))
        # origin = self.pat.get_patient_position()
        spacing = (self.dx, self.dy, self.dz)

        # Übernahme origin aus image position pat von erstem ct
        if image_position_patient is not None:
            origin = tuple(float(v) for v in image_position_patient)
        else:
            # kp ob das sinnvoll ist aber was besseres fällt mir auch nicht ein
            origin = (0, 0, 0)

        img.SetSpacing(spacing)
        # img.SetOrigin((origin))
        img.SetOrigin(origin)
        img.SetDirection((1, 0, 0,
                          0, 1, 0,
                          0, 0, 1))
        return img

    # TODO: Resampling in Handler auslagern evtl.
    def resample_to_reference(self, moving, reference):
        resampler = sitk.ResampleImageFilter()

        resampler.SetReferenceImage(reference)
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetDefaultPixelValue(0)

        return resampler.Execute(moving)

    def _create_image_view(self):
        self.img_axial, self.dose_axial = self.create_image(
            self.ax_axial,
            self.z_idx,
            "Axial",
        )

        self.img_coronal, self.dose_coronal = self.create_image(
            self.ax_coronal,
            self.y_idx,
            "Coronal",
        )

        self.img_sagittal, self.dose_sagittal = self.create_image(
            self.ax_sagittal,
            self.x_idx,
            "Sagittal",
        )

        self.img_overview = self.ax_overview.imshow(self.overview_img)
        self.ax_overview.set_title("Overview")

        print("CT:", self.volume.shape)
        print("DOSE:", self.dose_volume.shape)

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
            "A",
            0,
            self.volume.shape[0] - 1,
            valinit=self.z_idx,
            valstep=1,
        )

        self.slider_y = Slider(
            self.ax_slider_y,
            "C",
            0,
            self.volume.shape[1] - 1,
            valinit=self.y_idx,
            valstep=1,
        )

        self.slider_x = Slider(
            self.ax_slider_x,
            "S",
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

        if self.dose_volume is not None:
            self.dose_axial.set_data(self.dose_volume[z, :, :])
            self.dose_sagittal.set_data(self.dose_volume[:, :, x])
            self.dose_coronal.set_data(self.dose_volume[:, y, :])

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
