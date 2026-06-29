import os
import json
from typing import Any

import pydicom
from collections import defaultdict


class DicomIndexer:
    """
    Klasse zum Erzeugen der dicom_index.json
    """
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

        if not self._is_json_complete():
            self.build()
            self.save()
        else:
            pass

    def build(self) -> defaultdict[Any, defaultdict[Any, dict[str, list[Any]]]]:
        """
        Geht durch die Projektfiles, und schreibt Modalities, Dateipfade, uid und Beschreibung in einen dict
        :return:
        """
        for path, _, files in os.walk(self.root):

            for f in files:
                full_path = os.path.join(str(path), str(f))

                try:
                    ds = pydicom.dcmread(full_path, stop_before_pixels=True)
                except Exception as e:
                    print("Exception in dicom_indexer.build(): ", e)
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
        """ speichert die Daten aus dem dict in einer json """
        with open(self._json_file_name, "w") as f:
            json.dump(self.index, f, indent=2)

    def get_json_file_dir(self):
        """
        returns full json-file directory path
        """
        return self._json_file_name

    def get_patient_list(self) -> list[str]:
        """ gibt die komplette Liste der verfügbaren Patienten zurück """
        return self._patient_list

    def _is_json_complete(self) -> bool:
        """ geht durch die json und prüft, ob die Anzahl der Patienten noch
         mit der Menge der Daten in der json übereinstimmt, also ob neue Daten dazugekommen sind oder
         gelöscht wurden"""
        data_dir = "./data/RT"
        dir_list = os.listdir(data_dir)

        try:
            with open(self._json_file_name, "r") as file:
                data = json.load(file)
                data_list = data.keys()
                self._patient_list = [str(item) for item in data_list]

                return len(data) == len(dir_list)

        except FileNotFoundError:
            print("No JSON File - new will be generated")
            return False

    @staticmethod
    def select_patient(patient_list: list[str]) -> str:
        """ Terminal UI um einen Patienten aus den Daten auszuwählen """
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
