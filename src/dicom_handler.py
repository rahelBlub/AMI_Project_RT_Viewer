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

        if not self.dcm_ct_data_dir:
            raise ValueError("Patient has no CT path assigned (None)")
        else:
            print(f"Active CT-Path: {self.dcm_ct_data_dir}")

        self._dicom_list = self._get_dcm_files()
        #print(self._dicom_list)

        # TODO rt_dose als dicom file einlesen oder als image über sitk ?
        self.dose_path = self._pat.get_rt_dose_path()
        if self.dose_path:
            self.rt_dose = pydicom.dcmread(self.dose_path)
            self.rt_dose_image = sitk.ReadImage(self.dose_path)
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

    ## RT Dose Volume Handling ------------------------------------

    def resample_dose_volume(self, dose_img, ct_img):
        dose_resampled = sitk.Resample(dose_img, ct_img, sitk.Transform(), sitk.sitkLinear, 0.0,
                                       sitk.sitkFloat32)
        print()
        print("DOSE resampled")
        print("Size:", dose_resampled.GetSize())
        print("Spacing:", dose_resampled.GetSpacing())
        print("Origin:", dose_resampled.GetOrigin())
        print("Direction:", dose_resampled.GetDirection())
        print("TransformIndexToPhysikalPoint:")
        print(dose_resampled.TransformIndexToPhysicalPoint((0, 0, 0)))
        print(dose_resampled.TransformIndexToPhysicalPoint(
            tuple(s - 1 for s in dose_img.GetSize())
        ))
        print()

        # resampled_dose = sitk.GetArrayFromImage(dose_resampled)
        # resampled_dose *= float(self.rt_dose.DoseGridScaling)
        # return resampled_dose
        return sitk.GetArrayFromImage(dose_resampled)

    def get_rt_dose_volume(self):
        if self.rt_dose is None:
            return None

        dose = self.rt_dose.pixel_array.astype(np.float32)
        scaling = float(self.rt_dose.DoseGridScaling)

        return dose * scaling

    def get_sitk_dose_image(self):
        return self.rt_dose_image

    def get_dose_image(self):
        if self.rt_dose is None:
            return None

        dose = self.get_rt_dose_volume()
        dose_img = sitk.GetImageFromArray(dose)

        # TODO pz hardgecoded hingepfuscht, aber funktioniert halbwegs
        px, py = map(float, self.rt_dose.PixelSpacing)
        pz = 4.0
        # z_pos = self.rt_dose.GridFrameOffsetVector
        # pz = z_pos[1] - z_pos[0]
        # offsets = np.array(self.rt_dose.GridFrameOffsetVector, dtype=np.float32)
        # pz = np.mean(np.diff(offsets))
        spacing = (px, py, pz)

        dose_img.SetOrigin(tuple(map(float, self.rt_dose.ImagePositionPatient)))
        dose_img.SetSpacing(spacing)
        dose_img.SetDirection((1,0,0,0,1,0,0,0,1)) # -> direction aus CT Refernz übernehmen!

        print("FrameOfReferenceUID from rt_dose:", self.rt_dose.FrameOfReferenceUID)
        print("ImagePositionPatient from rt_dose:", self.rt_dose.ImagePositionPatient)
        print("GridOffSetVector:", self.rt_dose.GridFrameOffsetVector[:5])
        print(self.rt_dose.GridFrameOffsetVector[-5:])
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
        if image.__contains__("FrameOfReferenceUID"):
            self._pat.set_frame_of_reference_uid(image.FrameOfReferenceUID)

    def get_ct_image(self, ct_volume ,dx, dy, dz):
        img = sitk.GetImageFromArray(ct_volume.astype(np.float32))
        origin = self._pat.get_image_position_patient()
        spacing = (dx, dy, dz)
        # TODO: debug print Ausgaben löschen
        print("FrameOfReferenceUID  ct origin:", self._pat.get_frame_of_reference_uid())
        print(f"ImagePositionPatient ct origin: {origin}")

        if origin is None:
                origin = (0, 0, 0)

        img.SetSpacing(spacing)
        img.SetOrigin(origin)
        img.SetDirection((1, 0, 0, 0, 1, 0, 0, 0, 1))
        return img
