import os
import numpy as np
import pydicom
from pydicom import FileDataset
import SimpleITK as sitk

from src.patient import Patient

class DicomHandler:
    def __init__(self, pat: Patient):
        self._pat = pat

        self.dcm_ct_data_dir = self._pat.get_active_ct_path()
        print(f"Active CT-Path: {self.dcm_ct_data_dir}")

        if not self.dcm_ct_data_dir:
            raise ValueError("Patient has no CT path assigned (None)")

        self._dicom_list = self._get_dcm_files()
        if self._dicom_list:
            print("Found DICOM Files:")
            #print(self._dicom_list)

        # TODO: rt_dose_path bisher hardgecodede print Ausgabe nur zum Debuggen
        self.dose_path = self._pat.get_rt_dose_path()
        print(f"RT-Dose Path: {self.dose_path}")
        if self.dose_path:
            self.rt_dose = pydicom.dcmread(self.dose_path)
        else:
            self.rt_dose = None

        self.get_metadata_to_patient()

    def _get_dcm_files(self) -> list[FileDataset]:
        files = []

        for root, _, filenames in os.walk(self.dcm_ct_data_dir):
            for f in filenames:
                if not f.lower().endswith(".dcm"):
                    continue

                full_path = os.path.join(root, f)

                try:
                    ds = pydicom.dcmread(full_path)
                    files.append(ds)
                except Exception:
                    continue

        return files

    def _sort_dicom_list(self) -> None:
        self._dicom_list.sort(key=lambda ds: float(ds.ImagePositionPatient[2]))

    def create_ct_volume(self) -> np.ndarray[tuple[int, ...], np.dtype[...]]:
        """
        sorting CT slices and getting volume of data
        """
        self._sort_dicom_list()
        volume = np.stack([ds.pixel_array for ds in self._dicom_list])

        return volume

    def create_ct_volume_with_HU(self) -> np.ndarray[tuple[int, ...], np.dtype[...]]:
        """
        sorting CT slices and getting volume of data
        """
        self._sort_dicom_list()
        images = np.stack([ds.pixel_array for ds in self._dicom_list]).astype(np.int16)
        images[images == -2048] = 0

        for i, item in enumerate(self._dicom_list):
            images[i] = self._convert_to_HU(item, images[i])

        return images

    def _convert_to_HU(
        self, item: FileDataset, image: np.ndarray
    ) -> np.ndarray[tuple[int, ...], np.dtype[...]]:
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
        self._sort_dicom_list()
        dy, dx = map(float, self._dicom_list[0].PixelSpacing)
        dz = float(self._dicom_list[0].SliceThickness)

        return dx, dy, dz

    def get_modality(self, data: FileDataset) -> str:
        """
        classify modality
        Modalities can be "CT", "RTSTRUCT", "RTDOSE"

        :param data: FileDataset
        :return: Modality str of data
        """
        return data.Modality

    def get_rt_dose_volume(self):
        if self.rt_dose is None:
            return None

        dose = self.rt_dose.pixel_array.astype(np.float32)
        scaling = float(self.rt_dose.DoseGridScaling)

        return dose * scaling

    def get_dose_image(self):

        if self.rt_dose is None:
            return None

        dose = self.get_rt_dose_volume()

        dose_img = sitk.GetImageFromArray(dose)

        px, py = map(float, self.rt_dose.PixelSpacing)

        spacing = (px, py, 1.0)

        dose_img.SetOrigin(
            tuple(map(float, self.rt_dose.ImagePositionPatient))
        )

        dose_img.SetSpacing(spacing)

        return dose_img

    def get_metadata(self) -> dict[str, str]:
        image = self._dicom_list[0]

        return {
            "PatientName": image.PatientName,
            "PatientAge": image.PatientAge,
            "PatientSex": image.PatientSex,
            "BodyPartExamined": image.BodyPartExamined,
            "SliceThickness": image.SliceThickness,
            "PatientPosition": image.PatientPosition,
        }

    def get_metadata_to_patient(self):
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

        if image.__contains__("ImagePositionPatient"):
            self._pat.set_image_position_patient(image.ImagePositionPatient)

    def get_patient_image_position_patient(self):
        if self._pat.get_image_position_patient() is not None:
            return self._pat.get_image_position_patient()
        return None
