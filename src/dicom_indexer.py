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

        self.root = root
        self.index = defaultdict(lambda: defaultdict(dict))
        self.has_rt_dose = False
        self.has_rt_structure = False

    def build(self):
        for path, _, files in os.walk(self.root):

            for f in files:
                full_path = os.path.join(path, f)

                try:
                    ds = pydicom.dcmread(full_path, stop_before_pixels=True)
                except:
                    continue

                patient = ds.get("PatientID", "UNKNOWN")
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

        return self.index

    def save(self, filename="dicom_index.json"):
        with open(filename, "w") as f:
            json.dump(self.index, f, indent=2)

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
