import os
import pydicom
from collections import defaultdict
import json

from scipy.stats import false_discovery_control


class DicomIndexer:

    def __init__(self, root):
        #TODO: schauen ob Verzeichnis schon existiert,
        # damit es nicht mehrfach komplett laufen muss
        # mit hashing abfragen ob sich was geändert hat
        self._patient_list: list[str] = []

        self.root = root
        self.index = defaultdict(lambda: defaultdict(dict))
        self.has_rt_dose = False
        self.has_rt_structure = False
        self._json_file_name = "dicom_index.json"

    def build(self):
        for path, _, files in os.walk(self.root):

            for f in files:
                full_path = os.path.join(path, f)

                try:
                    ds = pydicom.dcmread(full_path, stop_before_pixels=True)
                except:
                    continue

                patient = ds.get("PatientID", "UNKNOWN")
                if self._patient_list.count(patient) == 0:
                    self._patient_list.append(patient)

                study = ds.get("StudyInstanceUID", "NO_STUDY")
                modality = ds.get("Modality", "UNKNOWN")
                study_desc = ds.get("StudyDescription", study)

                entry = self.index[patient][study]

                match modality:
                    case "CT":
                        entry["ct"] = path
                    case "MR":
                        entry["mr"] = path
                    case "RTSTRUCT":
                        entry["rtstruct"] = full_path
                    case "RTDOSE":
                        entry["dose"] = full_path
                    case "SEG":
                        entry["seg"] = full_path
                    case _:
                        break

        return self.index

    def save(self):
        with open(self._json_file_name, "w") as f:
            json.dump(self.index, f, indent=2)

    def get_json_file_dir(self):
        """
        returns full json-file directory path
        """
        return self._json_file_name

    def get_patient_list(self) -> list[str]:
        return self._patient_list

    @staticmethod
    def inspect_dataset(root):
        for path, _, files in os.walk(root):

            for f in files:
                try:
                    ds = pydicom.dcmread(
                        os.path.join(path, f),
                        stop_before_pixels=True
                    )

                    print(
                        f"{ds.Modality:10}",
                        ds.get("SeriesDescription", "---"),
                        path
                    )

                    break

                except Exception:
                    pass
