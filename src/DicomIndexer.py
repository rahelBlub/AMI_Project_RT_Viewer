import os
import pydicom
from collections import defaultdict
import json


class DicomIndexer:

    def __init__(self, root):
        self.root = root
        self.index = defaultdict(lambda: defaultdict(dict))

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

                entry = self.index[patient][study]

                if modality == "CT":
                    entry["ct"] = path

                elif modality == "MR":
                    entry["mr"] = path

                elif modality == "RTSTRUCT":
                    entry["rtstruct"] = full_path

                elif modality == "RTDOSE":
                    entry["dose"] = full_path

                elif modality == "SEG":
                    entry["seg"] = full_path

        return self.index

    def save(self, filename="dicom_index.json"):
        with open(filename, "w") as f:
            json.dump(self.index, f, indent=2)