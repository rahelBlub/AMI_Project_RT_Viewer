import os
import numpy as np
import pydicom
from pydicom import FileDataset
import SimpleITK as sitk

from src.patient import Patient


class DicomHandler:
    def __init__(self, pat: Patient):
        self._pat = pat

        self.dcm_data_dir = self._pat.get_ct_path()
        self._dicom_list = self._get_dcm_files()

        self.get_metadata_to_patient()

        self.ds = pydicom.dcmread(self._pat.get_rt_dose_path())

    def _get_dcm_files(self) -> list[FileDataset]:
        """
        creates a list of FileDataset, containing the dicom data
        """
        files = [
            pydicom.dcmread(os.path.join(self.dcm_data_dir, f))
            for f in os.listdir(self.dcm_data_dir)
            if f.endswith(".dcm")
        ]
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
        dose = self.ds.pixel_array.astype(np.float32)

        scaling = float(self.ds.DoseGridScaling)

        return dose * scaling

    # TODO: keine Ahnung was hier passiert, aber das image stimmt noch nicht mit dem CT-Datensatz überien
    def get_dose_image(self):
        dose = self.ds.pixel_array.astype(np.float32)
        dose *= float(self.ds.DoseGridScaling)

        dose_img = sitk.GetImageFromArray(dose)

        px, py = map(float, self.ds.PixelSpacing)
        spacing = (px, py, 1.0)

        dose_img.SetOrigin(self.ds.ImagePositionPatient)
        dose_img.SetSpacing(spacing)
        dose_img.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))

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
            self._pat.set_patient_sex("PatientSex")
        if image.__contains__("BodyPartExamined"):
            self._pat.set_body_part_examined("BodyPartExamined")
        if image.__contains__("SliceThickness"):
            self._pat.set_slice_thickness("SliceThickness")
        if image.__contains__("PatientPosition"):
            self._pat.set_patient_position("PatientPosition")
