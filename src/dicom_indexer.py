import os
import pydicom
from collections import defaultdict
import json


class DicomIndexer:

    def __init__(self, root):
        self._patient_list: list[str] = []

        self.root = root
        self.index = defaultdict(
            lambda: defaultdict(
                lambda: {
                    "ct": [],
                    "mr": [],
                    "dose": [],
                    "rtstruct": [],
                    "rtplan": [],
                    "seg": []
                }
            )
        )

        self.has_rt_dose = False
        self.has_rt_structure = False
        self._json_file_name = "dicom_index.json"

        if not self.is_json_complete():
            self.build()
            self.save()
        else:
            pass

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

                entry = self.index[patient][study]

                if modality == "CT":
                    if path not in [x["path"] for x in entry["ct"]]:
                        entry["ct"].append({
                            "path": path,
                            "series_uid": ds.get("SeriesInstanceUID"),
                            "description": ds.get("SeriesDescription", "")
                        })

                elif modality == "MR":
                    if path not in [x["path"] for x in entry["mr"]]:
                        entry["mr"].append({
                            "path": path,
                            "series_uid": ds.get("SeriesInstanceUID"),
                            "description": ds.get("SeriesDescription", "")
                        })

                elif modality == "RTDOSE":
                    entry["dose"].append({
                        "path": full_path,
                        "sop_uid": ds.get("SOPInstanceUID")
                    })

                elif modality == "RTSTRUCT":
                    entry["rtstruct"].append({
                        "path": full_path,
                        "sop_uid": ds.get("SOPInstanceUID"),
                        "description": ds.get("StructureSetLabel", "")
                    })

                elif modality == "RTPLAN":
                    entry["rtplan"].append({
                        "path": full_path,
                        "sop_uid": ds.get("SOPInstanceUID")
                    })

                elif modality == "SEG":
                    entry["seg"].append({
                        "path": full_path,
                        "description": ds.get("SeriesDescription", "")
                    })

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
                    ds = pydicom.dcmread(os.path.join(path, f), stop_before_pixels=True)

                    print(f"{ds.Modality:10}", ds.get("SeriesDescription", "---"), path)

                    break

                except Exception:
                    pass

    def is_json_complete(self) -> bool:
        data_dir = "./data/RT"
        dir_list = os.listdir(data_dir)

        try:
            with open(self._json_file_name, "r") as file:
                data = json.load(file)
                data_list = data.keys()
                self._patient_list = [str(item) for item in data_list]

                return len(data) == len(dir_list)

        except FileNotFoundError:
            print("JSON File not found!!!")
            return False

    @staticmethod
    def select_patient(patient_list: list[str]) -> str:
        print("\nVerfügbare Patienten:\n")

        for i, patient in enumerate(patient_list, start=1):
            print(f"[{i}] {patient}")

        while True:
            try:
                choice = int(input("\nPatient auswählen: "))

                if 1 <= choice <= len(patient_list):
                    return patient_list[choice - 1]

                print("Ungültige Auswahl.")

            except ValueError:
                print("Bitte eine Zahl eingeben.")