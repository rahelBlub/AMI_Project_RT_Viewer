import os
import cv2
import numpy as np
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
from scipy import ndimage as ndi
import math
import pydicom
from pydicom import FileDataset
import skimage as ski
from skimage import morphology, measure


class DicomHandler:
    def __init__(self, dicom_dir: str):
        self._dicom_list, self.rt_struct, self.rt_dose = self.get_modality(dicom_dir)

    def get_modality(
        self, cur_data_path: str
    ) -> tuple[list[str], str | None, str | None]:
        """
        Dateien klassifizieren

        :param cur_data_path:
        :return: paths to ct_files, rtstruct, rtdose as tuple
        """
        cur_ct_files = []
        rtstruct = None
        rtdose = None

        data_list = os.listdir(cur_data_path)

        for file in data_list:
            path = os.path.join(cur_data_path, file)

            ds = pydicom.dcmread(path)

            modality = ds.Modality

            if modality == "CT":
                cur_ct_files.append(path)

            elif modality == "RTSTRUCT":
                rtstruct = path

            elif modality == "RTDOSE":
                rtdose = path

            # print(file, modality)
        return cur_ct_files, rtstruct, rtdose

    def create_ct_volume(self) -> np.ndarray[tuple[int, ...], np.dtype[...]]:
        """
        sorting CT slices

        :return: volume
        """
        datasets = [pydicom.dcmread(f) for f in self._dicom_list]

        datasets.sort(key=lambda ds: float(ds.ImagePositionPatient[2]))

        volume = np.stack([ds.pixel_array for ds in datasets])

        return volume


def apply_hu(cur_volume, cur_ct_files: list[str]):
    """

    :param cur_volume:
    :param cur_ct_files:
    :return:
    """
    datasets = [pydicom.dcmread(f) for f in cur_ct_files]


if __name__ == "__main__":
    data_path = "../data/RT/LungData_01"
    d_handler = DicomHandler(dicom_dir=data_path)

    this_volume = d_handler.create_ct_volume()
    print(this_volume.shape)
