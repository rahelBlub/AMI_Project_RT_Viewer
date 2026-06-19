## TODO: Patienten für jeden Ordner anlegen und am Anfang im Viewer auswählbar

class Patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id

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

