import os
from pprint import pprint

import numpy as np
import pydicom
from pydicom import FileDataset


class DicomHandler:
    def __init__(self, dicom_dir: str):
        self.dcm_data_dir = dicom_dir
        self._dicom_list = self._get_dcm_files()

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

    def get_rtdose(self, data: FileDataset) -> float:
        if data.Modality == "RTDOSE":
            dose = data.RTDOSE
            return dose

    def get_metadata(self) -> dict[str, ...]:
        image = self._dicom_list[0]

        return {
            "PatientName": image.PatientName,
            "PatientAge": image.PatientAge,
            "PatientSex": image.PatientSex,
            "BodyPartExamined": image.BodyPartExamined,
            "SliceThickness": image.SliceThickness,
            "PatientPosition": image.PatientPosition,
        }


