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


def get_modality(cur_data_path: str) -> tuple[list[str], str | None, str | None]:
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

        #print(file, modality)
    return cur_ct_files, rtstruct, rtdose


def create_ct_volume(cur_ct_files: list[str] | list[FileDataset]) -> np.ndarray[tuple[int, ...], np.dtype[...]]:
    """
    sorting CT slices

    :param cur_ct_files:
    :return: volume
    """
    datasets = [pydicom.dcmread(f) for f in cur_ct_files]

    datasets.sort(
        key=lambda ds: float(ds.ImagePositionPatient[2])
    )

    volume = np.stack(
        [ds.pixel_array for ds in datasets]
    )

    return volume


def apply_hu(cur_volume, cur_ct_files: list[str]):
    """

    :param cur_volume:
    :param cur_ct_files:
    :return:
    """
    datasets = [pydicom.dcmread(f) for f in cur_ct_files]


if __name__ == '__main__':
    data_path = "../data/RT/LungData_01"
    ct_files, rt_struct, rt_dose = get_modality(data_path)
    print(ct_files)
    print(rt_struct)
    print(rt_dose)

    this_volume = create_ct_volume(ct_files)
    print(this_volume.shape)

