from dataclasses import dataclass
## TODO: Patienten für jeden Ordner anlegen und am Anfang im Viewer auswählbar


@dataclass
class Patient:
    def __init__(self, patient_name, json_file_dir):
        self.patient_name = patient_name
        self.sop_instance_iud = ""

        self.json_file_dir = json_file_dir

        self.ct_studies = []
        self.mr_studies = []

        self.rt_struct = []
        self.seg = []
        self.rt_dose = []

    def has_ct(self) -> bool:
        return len(self.ct_studies) > 0

    def has_mr(self) -> bool:
        return len(self.mr_studies) > 0

    def has_rt_dose(self) -> bool:
        return len(self.rt_dose) > 0

    def has_rt_struct(self) -> bool:
        return len(self.rt_struct) > 0

    # def check_json_file(self):
    #     try:
    #         with open(self.json_file_dir, 'r') as file:
    #             file.seek(self.patient_name)
    #
    #     except FileNotFoundError:
    #         print("JSON File not found!!!")
