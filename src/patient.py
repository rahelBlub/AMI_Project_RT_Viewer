## TODO: Patienten für jeden Ordner anlegen und am Anfang im Viewer auswählbar

class Patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id

        self.ct_studies = []
        self.mr_studies = []

        self.rtstruct = []
        self.seg = []
        self.dose = []

    def has_ct(self):
        return len(self.ct_studies) > 0

    def has_mr(self):
        return len(self.mr_studies) > 0

    def has_dose(self):
        return len(self.dose) > 0