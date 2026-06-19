class Patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id

        self.ct_series = []
        self.mr_series = []

        self.rtstructs = []
        self.rtdoses = []
        self.rtplans = []
        self.segmentations = []

        self._patient_name: str = patient_id
        self._sop_instance_iud: str | None = None
        self._patient_age: int | None = None
        self._patient_sex: str | None = None
        self._body_part_examined: str | None = None
        self._slice_thickness: str | None = None
        self._patient_position: str | None = None

        self._image_position_patient: str | None = None

        self._has_ct_studies: bool = False
        self._has_mr_studies: bool = False
        self._has_rt_struct: bool = False
        self._has_rt_dose: bool = False
        self._has_seg: bool = False

        self._ct_path: str | None = None
        self._mr_path: str | None = None
        self._rt_struct_path: str | None = None
        self._rt_dose_path: str | None = None
        self._seg_path: str | None = None

    def add_ct(self, ct):
        self.ct_series.append(ct)

    def add_mr(self, mr):
        self.mr_series.append(mr)

    def add_rtstruct(self, rtstruct):
        self.rtstructs.append(rtstruct)

    def add_rtdose(self, dose):
        self.rtdoses.append(dose)

    def add_rtplan(self, plan):
        self.rtplans.append(plan)

    def add_seg(self, seg):
        self.segmentations.append(seg)

        # SETTER----------------------------------------------------

    def set_sop_instance_iud(self, in_iud):
        self._sop_instance_iud = in_iud

    def set_patient_age(self, age: str) -> None:
        if age != "":
            self._patient_age = int(re.sub(r"^0+|[A-Za-z]+$", "", age))

    def set_patient_sex(self, sex: str) -> None:
        if sex != "":
            self._patient_sex = sex

    def set_body_part_examined(self, body_part: str) -> None:
        if body_part != "":
            self._body_part_examined = body_part

    def set_slice_thickness(self, thickness: str) -> None:
        if thickness != "":
            self._slice_thickness = thickness

    def set_patient_position(self, position: str) -> None:
        if position != "":
            self._patient_position = position

    def set_ct_data_available(self) -> None:
        self._has_ct_studies = True

    def set_mr_data_available(self) -> None:
        self._has_mr_studies = True

    def set_rt_struct_data_available(self) -> None:
        self._has_rt_struct = True

    def set_rt_dose_data_available(self) -> None:
        self._has_rt_dose = True

    def set_seg_data_available(self) -> None:
        self._has_seg = True

    def set_ct_path(self, in_path) -> None:
        self._ct_path = in_path

    def set_mr_path(self, in_path) -> None:
        self._mr_path = in_path

    def set_rt_struct_path(self, in_path) -> None:
        self._rt_struct_path = in_path

    def set_rt_dose_path(self, in_path) -> None:
        self._rt_dose_path = in_path

    def set_seg_path(self, in_path) -> None:
        self._seg_path = in_path

    def set_image_position_patient(self, in_var):
        self._image_position_patient = in_var

        # GETTER----------------------------------------------------

    def get_patient_name(self) -> str | None:
        return self._patient_name

    def get_patient_age(self) -> int | None:
        return self._patient_age

    def get_patient_sex(self) -> str | None:
        return self._patient_sex

    def get_body_part_examined(self) -> str | None:
        return self._body_part_examined

    def get_slice_thickness(self) -> str | None:
        return self._slice_thickness

    def get_patient_position(self) -> str | None:
        return self._patient_position

    def has_ct_data_available(self) -> bool:
        return self._has_ct_studies

    def has_mr_data_available(self) -> bool:
        return self._has_mr_studies

    def has_rt_struct_available(self) -> bool:
        return self._has_rt_struct

    def has_rt_dose_available(self) -> bool:
        return self._has_rt_dose

    def has_seg_available(self) -> bool:
        return self._has_seg

    def get_ct_path(self) -> str | None:
        return self._ct_path

    def get_mr_path(self) -> str | None:
        return self._mr_path

    def get_rt_struct_path(self) -> str | None:
        return self._rt_struct_path

    def get_rt_dose_path(self) -> str | None:
        return self._rt_dose_path

    def get_seg_path(self) -> str | None:
        return self._seg_path

    def get_image_position_patient(self):
        return self._image_position_patient
