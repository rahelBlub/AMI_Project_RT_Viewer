from typing import Any
import ijson

from src.patient import Patient


class PatientHandler:
    """
    Klasse die Patienten aus der dicom_index.json ausliest
    und ein Objekt vom Typ "Patient" anlegt
    """
    def __init__(self, patient_name, json_file_dir):
        self.patientName = patient_name
        self.json_file_dir = json_file_dir

        # Patienten-Objekt anlegen
        self.patient_obj = Patient(patient_name)

        self._check_json_file()
        self._choose_active_set()

    def _check_json_file(self) -> None:
        """
        liest die Daten aus der json und übergibt die einzelnen
        Parameter in die Patientenklasse
        → Aufruf in __init__
        """
        try:
            with open(self.json_file_dir, "r") as file:

                cur_patient = ijson.items(file, self.patientName)

                for json_item in cur_patient:

                    for study_uid, study_data in json_item.items():
                        self.patient_obj.set_sop_instance_iud(study_uid)

                        for ct in study_data.get("ct", []):
                            self.patient_obj.set_ct_data_available()
                            self.patient_obj.add_ct(ct)
                            #print(self.patient_obj.get_ct_series())

                        for mr in study_data.get("mr", []):
                            self.patient_obj.set_mr_data_available()
                            self.patient_obj.add_mr(mr)
                            #print(self.patient_obj.get_mr_series())

                        for rtstruct in study_data.get("rtstruct", []):
                            self.patient_obj.set_rt_struct_data_available()
                            self.patient_obj.add_rtstruct(rtstruct)
                            #print(self.patient_obj.get_rt_struct_series())

                        for dose in study_data.get("dose", []):
                            self.patient_obj.set_rt_dose_data_available()
                            self.patient_obj.add_rtdose(dose)
                            #print(self.patient_obj.get_rt_dose_series())

                        for plan in study_data.get("rtplan", []):
                            self.patient_obj.add_rtplan(plan)
                            #print(self.patient_obj.get_rt_plan_sereies())

                        for seg in study_data.get("seg", []):
                            self.patient_obj.set_seg_data_available()
                            self.patient_obj.add_seg(seg)
                            #print(self.patient_obj.get_segmantation_series())

        except FileNotFoundError:
            print("JSON File not found!!!")

    def _choose_active_set(self) -> list[Any] | None:
        """
        Terminal UI zur Auswahl der Daten
        :return: Liste mit den Daten oder None
        → Aufruf in __init__
        """
        # CT Sets laden
        if self.patient_obj.get_ct_series():
            print("\nVerfügbare CT-Sets:\n")

            ct_set = self.patient_obj.get_ct_series()
            for i, ct in enumerate(ct_set, start=1):
                print(f"[{i}] {ct['description']}")

            # Auswahl welche CT Daten
            while True:
                try:
                    choice = int(input("\nCT-Set auswählen: "))

                    if 1 <= choice <= len(ct_set):
                        self.patient_obj.set_active_set(choice-1)

                        if self.patient_obj.has_rt_dose_available():
                            rt_dose_list = self.patient_obj.get_rt_dose_series()
                            self.patient_obj.set_rt_dose_path(rt_dose_list[0]["path"])
                        else:
                            print("Patient has no RT-Dose")

                        return ct_set[choice - 1]["path"]

                    print("Ungültige Auswahl.")

                except ValueError:
                    print("Bitte eine Zahl eingeben.")

        # MRT Daten laden
        elif self.patient_obj.get_mr_series():
            print("\nVerfügbare MR-Sets:\n")

            mr_set = self.patient_obj.get_mr_series()
            for i, mr in enumerate(mr_set, start=1):
                print(f"[{i}] {mr['description']}")

            # Auswahl welche MRT Daten
            while True:
                try:
                    choice = int(input("\nMR-Set auswählen: "))

                    if 1 <= choice <= len(mr_set):
                        self.patient_obj.set_active_set(choice - 1)

                        if self.patient_obj.has_rt_dose_available():
                            rt_dose_list = self.patient_obj.get_rt_dose_series()
                            self.patient_obj.set_rt_dose_path(rt_dose_list[0]["path"])
                        else:
                            print("Patient has no RT-Dose")

                        return mr_set[choice - 1]["path"]

                    print("Ungültige Auswahl.")

                except ValueError:
                    print("Bitte eine Zahl eingeben.")

        else:
            print("invalid Patient!")
            print("Patient has no CT or MR Set")
            return None

    def get_pat_obj(self):
        """gibt das Patient-Objekt zurück"""
        return self.patient_obj
