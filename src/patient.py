from dataclasses import dataclass
## TODO: Patienten für jeden Ordner anlegen und am Anfang im Viewer auswählbar


@dataclass
class Patient:
    def __init__(self, patient_name):
        self._patient_name = patient_name
        self._sop_instance_iud = ""

        self._has_ct_studies = False
        self._has_mr_studies = False
        self._has_rt_struct = False
        self._has_rt_dose = False
        self._has_seg = False

        self._ct_path = ""
        self._mr_path = ""
        self._rt_struct_path = ""
        self._rt_dose_path = ""
        self._seg_path = ""

    # SETTER----------------------------------------------------

    def set_ct_data_available(self):
        self._has_ct_studies = True

    def set_mr_data_available(self):
        self._has_mr_studies = True

    def set_rt_struct_data_available(self):
        self._has_rt_struct = True

    def set_rt_dose_data_available(self):
        self._has_rt_dose = True

    def set_seg_data_available(self):
        self._has_seg = True

    def set_sop_instance_iud(self, in_iud):
        self._sop_instance_iud = in_iud

    def set_ct_path(self, in_path):
        self._ct_path = in_path

    def set_mr_path(self, in_path):
        self._mr_path = in_path

    def set_rt_struct_path(self, in_path):
        self._rt_struct_path = in_path

    def set_rt_dose_path(self, in_path):
        self._rt_dose_path = in_path

    def set_seg_path(self, in_path):
        self._seg_path = in_path

    # GETTER----------------------------------------------------
    def get_ct_data_available(self) -> bool:
        return self._has_ct_studies

    def get_mr_data_available(self) -> bool:
        return self._has_mr_studies

    def get_rt_struct_available(self) -> bool:
        return self._has_rt_struct

    def get_rt_dose_available(self) -> bool:
        return self._has_rt_dose

    def get_seg_available(self) -> bool:
        return self._has_seg

    def get_ct_path(self) -> str:
        return self._ct_path

    def get_mr_path(self) -> str:
        return self._mr_path

    def get_rt_struct_path(self) -> str:
        return self._rt_struct_path

    def get_rt_dose_path(self) -> str:
        return self._rt_dose_path

    def get_seg_path(self) -> str:
        return self._seg_path
