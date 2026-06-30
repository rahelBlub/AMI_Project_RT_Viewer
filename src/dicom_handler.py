import os
import numpy as np
from typing import Any
import pydicom
from pydicom import FileDataset
import SimpleITK as sitk
from SimpleITK import Image

from src.patient import Patient


class DicomHandler:
    """
    Läd die Daten aus den dicom Files und verarbeitet diese
    """

    def __init__(self, pat: Patient):
        self._pat = pat

        self.dcm_ct_data_dir = self._pat.get_active_ct_path()

        if not self.dcm_ct_data_dir:
            raise ValueError("Patient has no CT path assigned (None)")
        else:
            print(f"Active CT-Path: {self.dcm_ct_data_dir}")

        self._dicom_list = self._get_dcm_files()
        # Prüfen, ob die Slices in z-Richtung korrekt sortiert sind
        first_z = float(self._dicom_list[0].ImagePositionPatient[2])
        last_z = float(self._dicom_list[-1].ImagePositionPatient[2])
        print(f"Before sorting: first z = {first_z}, last z = {last_z}")

        if first_z > last_z:
            print("CT slices are stored in descending order -> reversing.")
            self._dicom_list.reverse()
        else:
            print("CT slices are already in ascending order.")

        first_z = float(self._dicom_list[0].ImagePositionPatient[2])
        last_z = float(self._dicom_list[-1].ImagePositionPatient[2])
        print(f"After sorting: first z = {first_z}, last z = {last_z}")

        self.dose_path = self._pat.get_rt_dose_path()
        if self.dose_path:
            self.rt_dose = pydicom.dcmread(self.dose_path)
            self.rt_dose_image = sitk.ReadImage(self.dose_path)
        else:
            self.rt_dose = None

        self.get_metadata_to_patient()

    def _get_dcm_files(self) -> list[FileDataset]:
        """
        sucht alle Files vom Typ .dcm und gibt die einzelnen FileDatasets in einer Liste zurück
        :return: Liste mit den Dicom Datasets
        """
        files = []

        for root, _, filenames in os.walk(self.dcm_ct_data_dir):

            for f in filenames:
                if not f.lower().endswith(".dcm"):
                    continue

                full_path = os.path.join(root, f)

                try:
                    ds = pydicom.dcmread(full_path)
                    files.append(ds)
                except Exception as e:
                    print("Exception in dicom_handler._get_dcm_files(): ", e)
                    continue

        return files

    def _sort_dicom_list(self) -> None:
        """
        Sortiert die Liste nach ImagePositionPatient
        """
        self._dicom_list.sort(key=lambda ds: float(ds.ImagePositionPatient[2]))

    def create_ct_volume(self) -> np.ndarray[tuple[int, ...], np.dtype[Any]]:
        """
        sorting CT slices and getting volume of data
        """
        self._sort_dicom_list()
        volume = np.stack([ds.pixel_array for ds in self._dicom_list])

        return volume

    def create_ct_volume_with_HU(self) -> np.ndarray:
        """
        sorting CT slices and getting volume of data
        """
        self._sort_dicom_list()
        images = np.stack([ds.pixel_array for ds in self._dicom_list]).astype(np.int16)
        images[images == -2048] = 0

        for i, item in enumerate(self._dicom_list):
            images[i] = self._convert_to_HU(item, images[i])

        return images

    def _convert_to_HU(self, item: FileDataset, image: np.ndarray) -> np.ndarray:
        """
        Convert the pixel values to Hounsfield Units (HU)
        https://github.com/shujuecn/Radiverse/blob/main/src/radiverse/windowing.py#L23
        """
        intercept = item.RescaleIntercept
        slope = item.RescaleSlope

        if slope != 1:
            image = slope * image.astype(np.float64)
        image += np.int16(intercept)

        return image

    def get_voxelspacing(self) -> tuple[float, float, float]:
        """
        Kalkuiert das Voxelspacing
        :return: Die x, y, z Werte in einem Tuple
        """
        self._sort_dicom_list()
        dy, dx = map(float, self._dicom_list[0].PixelSpacing)
        dz = float(self._dicom_list[0].SliceThickness)

        return dx, dy, dz

    ## RT Dose Volume Handling ------------------------------------

    def resample_dose_volume(self, dose_img: Image, ct_img: Image) -> np.ndarray:
        """
        Passt die Größe der Dosis auf die Größe des CT Bildes an
        :param dose_img:
        :param ct_img:
        :return: das Bild als np.array
        """
        dose_resampled = sitk.Resample(
            dose_img, ct_img, sitk.Transform(), sitk.sitkLinear, 0.0, sitk.sitkFloat32
        )
        print()
        print("DOSE resampled")
        print("Size:", dose_resampled.GetSize())
        print("Spacing:", dose_resampled.GetSpacing())
        print("Origin:", dose_resampled.GetOrigin())
        print("Direction:", dose_resampled.GetDirection())
        print("TransformIndexToPhysikalPoint:")
        print(dose_resampled.TransformIndexToPhysicalPoint((0, 0, 0)))
        print(
            dose_resampled.TransformIndexToPhysicalPoint(
                tuple(s - 1 for s in dose_img.GetSize())
            )
        )
        print()

        return sitk.GetArrayFromImage(dose_resampled)

    def get_rt_dose_volume(self) -> np.ndarray | None:
        """gibt das Volumen der RT Dosis zurück"""
        if self.rt_dose is None:
            return None

        dose = self.rt_dose.pixel_array.astype(np.float32)
        scaling = float(self.rt_dose.DoseGridScaling)

        return dose * scaling

    def get_sitk_dose_image(self) -> Image:
        """gibt das RT Dosis Image zurück"""
        return self.rt_dose_image

    def get_dose_image(self) -> Image | None:
        """gibt die RT Dosis zurück"""
        if self.rt_dose is None:
            return None

        dose = self.get_rt_dose_volume()
        dose_img = sitk.GetImageFromArray(dose)

        px, py = map(float, self.rt_dose.PixelSpacing)

        offsets = [float(v) for v in self.rt_dose.GridFrameOffsetVector]
        if len(offsets) > 1:
            pz = offsets[1] - offsets[0]
        else:
            pz = 1.0
        spacing = (px, py, pz)

        dose_img.SetOrigin(tuple(map(float, self.rt_dose.ImagePositionPatient)))
        dose_img.SetSpacing(spacing)
        # dose_img.SetDirection(
        #     (1, 0, 0, 0, 1, 0, 0, 0, 1)
        # )  # → direction aus CT Refernz übernehmen!

        return dose_img

    def get_metadata_to_patient(self):
        """Übergibt die Metadaten in das Patient-Objekt"""
        image = self._dicom_list[0]

        if image.__contains__("PatientAge"):
            self._pat.set_patient_age(image.PatientAge)
        if image.__contains__("PatientSex"):
            self._pat.set_patient_sex(image.PatientSex)
        if image.__contains__("BodyPartExamined"):
            self._pat.set_body_part_examined(image.BodyPartExamined)
        if image.__contains__("SliceThickness"):
            self._pat.set_slice_thickness(image.SliceThickness)
        if image.__contains__("PatientPosition"):
            self._pat.set_patient_position(image.PatientPosition)
        if image.__contains__("Modality"):
            self._pat.set_modality(image.Modality)
        if image.__contains__("ImagePositionPatient"):
            self._pat.set_image_position_patient(image.ImagePositionPatient)
        if image.__contains__("FrameOfReferenceUID"):
            self._pat.set_frame_of_reference_uid(image.FrameOfReferenceUID)

    def get_ct_image(
        self, ct_volume: np.ndarray, dx: float | int, dy: float | int, dz: float | int
    ) -> Image:
        """
        Läd das CT Bild mit Volumen, x, y, und z Koordinaten,
        setzt Ursprung, Spacing und Richtung und gibt
        das Image zurück
        """
        img = sitk.GetImageFromArray(ct_volume.astype(np.float32))
        origin = self._pat.get_image_position_patient()
        spacing = (dx, dy, dz)

        if origin is None:
            origin = (0, 0, 0)

        img.SetSpacing(spacing)
        img.SetOrigin(origin)
        img.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
        return img
