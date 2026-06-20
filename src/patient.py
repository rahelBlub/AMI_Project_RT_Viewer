import re
import pydicom

class Patient:
    def __init__(self, patient_id):
        self.patient_id = patient_id # TODO: ID nicht Name sonder die uid

        self.ct_series = []
        self.mr_series = []

        self.rt_structs = []
        self.rt_doses = []
        self.rt_plans = []
        self.segmentations = []

        self.mapped_sets = []

        self.active_set = None

        self.active_ct_index = 0
        self.active_dose_index = 0

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

        self._seg_path: str | None = None
        self._rt_dose_path: str | None = None
        self._rt_struct_path: str | None = None
        self._mr_path: str | None = None
        self._ct_path: str | None = None

    ## SETTER for Sereies -----------------------------------------------------

    def add_ct(self, ct):
        self.ct_series.append(ct)

    # def add_ct(self, path, sop_uid, frame_uid):
    #     self.ct_series.append({
    #         "path": path,
    #         "sop_uid": sop_uid,
    #         "frame_uid": frame_uid,
    #     })

    def add_mr(self, mr):
        self.mr_series.append(mr)

    # def add_mr(self, path, sop_uid, frame_uid):
    #     self.mr_series.append({
    #         "path": path,
    #         "sop_uid": sop_uid,
    #         "frame_uid": frame_uid,
    #     })

    def add_rtstruct(self, rtstruct):
        self.rt_structs.append(rtstruct)

    # def add_rtstruct(self, path, sop_uid):
    #     self.rtstructs.append({
    #         "path": path,
    #         "sop_uid": sop_uid,
    #     })

    def add_rtdose(self, dose):
        self.rt_doses.append(dose)

    # def add_rtdose(self, path, sop_uid):
    #     self.rtdoses.append({
    #         "path": path,
    #         "sop_uid": sop_uid,
    #     })


    def add_rtplan(self, plan):
        self.rt_plans.append(plan)

    # def add_rtplan(self, path, sop_uid):
    #     self.rtplans.append({
    #         "path": path,
    #         "sop_uid": sop_uid,
    #     })

    def add_seg(self, seg):
        self.segmentations.append(seg)

    # def add_seg(self, path, sop_uid):
    #     self.segmentations.append({
    #         "path": path,
    #         "sop_uid": sop_uid,
    #     })

    # SETTER for Patient data----------------------------------------------------

    def set_sop_instance_iud(self, in_iud):
        self._sop_instance_iud = in_iud

    def set_active_set(self, idx: int):
        self.active_set = self.mapped_sets[idx]

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

    def set_image_position_patient(self, in_var):
        self._image_position_patient = in_var

    ### SETTER for Paths --------------------------------------------------

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


   ### SETTER for Bool -----------------------------------------------------

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


    # GETTER----------------------------------------------------

    def get_active_ct(self):
        if not self.ct_series:
            return None
        return self.ct_series[self.active_ct_index]

    def get_active_ct_path(self):
        ct = self.get_active_ct()
        return ct["path"] if ct else None

    # def get_active_ct_path(self):
    #     if self.active_set:
    #         return self.active_set["ct"]["path"]
    #     return None

    def get_active_dose_path(self):
        if self.active_set:
            return self.active_set["dose"]["path"]
        return None

    ### GETTER of Series -------------------------------------------------------------

    def get_ct_series(self) :
        return self.ct_series

    def get_mr_series(self):
        return self.mr_series

    def get_rt_struct_series(self) :
        return self.rt_structs

    def get_rt_dose_series(self):
        return self.rt_doses

    def get_rt_plan_series(self):
        return self.rt_plans

    def get_segmentation_series(self):
        return self.segmentations

    def get_mapped_sets(self):
        return self.mapped_sets

    ### GETTER for Patient variables -----------------------------------------------

    def get_patient_id(self):
        return self.patient_id

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

    ### GETTER for Bool Variables ------------------------------------------------

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

    ### GETTER for Dataset Paths -------------------------------------------------

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

# TODO: relationships funktionieren nicht, -> hardcoden der Pfade
    def resolve_relationships(self):

        self.mapped_sets = []

        for ct in self.ct_series:
            ct_ds = pydicom.dcmread(ct["path"], stop_before_pixels=True)
            ct_frame = ct_ds.FrameOfReferenceUID

            # RTSTRUCT direkt über FrameOfReferenceUID
            struct = next(
                (s for s in self.rt_structs
                 if ct_frame in pydicom.dcmread(s["path"], stop_before_pixels=True)
                 .ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID),
                None
            )

            # RTDOSE erstmal direkt nehmen (1:1 oder später matching)
            dose = self.rt_doses[0] if self.rt_doses else None

            self.mapped_sets.append({
                "ct": ct,
                "struct": struct,
                "dose": dose
            })

    # def resolve_relationships(self):
    #     """
    #     Links RTDOSE → RTPLAN → RTSTRUCT → CT
    #     based on DICOM UIDs (not filenames).
    #     """
    #
    #     for dose in self.rtdoses:
    #
    #         dose_ds = pydicom.dcmread(dose["path"], stop_before_pixels=True)
    #         # debugging prints
    #         dose_path = dose["path"]
    #         print(f"Dose-Path: {dose_path}")
    #
    #         # -------------------------
    #         # 1. RTPLAN finden
    #         # -------------------------
    #         plan_uid = None
    #
    #         if "ReferencedRTPlanSequence" in dose_ds:
    #             plan_uid = dose_ds.ReferencedRTPlanSequence[0].ReferencedSOPInstanceUID
    #             print(f"Plan-UID: {plan_uid}")
    #
    #             print("RTPLANS:")
    #             for p in self.rtplans:
    #                 print(p)
    #
    #         plan = next(
    #             (p for p in self.rtplans if p["sop_uid"] == plan_uid),
    #             None
    #         )
    #
    #         if not plan:
    #             continue
    #
    #         plan_ds = pydicom.dcmread(plan["path"], stop_before_pixels=True)
    #         # debugging prints
    #         plan_path = dose["path"]
    #         print(f"Plan-Path: {plan_path}")
    #
    #         # -------------------------
    #         # 2. RTSTRUCT finden
    #         # -------------------------
    #         struct_uid = None
    #
    #         if "ReferencedStructureSetSequence" in plan_ds:
    #             struct_uid = plan_ds.ReferencedStructureSetSequence[0].ReferencedSOPInstanceUID
    #
    #         struct = next(
    #             (s for s in self.rtstructs if s["sop_uid"] == struct_uid),
    #             None
    #         )
    #
    #         if not struct:
    #             continue
    #
    #         struct_ds = pydicom.dcmread(struct["path"], stop_before_pixels=True)
    #         # debugging prints
    #         struct_path = struct["path"]
    #         print(f"Dose-Path: {struct_path}")
    #
    #         # -------------------------
    #         # 3. CT über FrameOfReferenceUID
    #         # -------------------------
    #         ref_frame = None
    #
    #         if "ReferencedFrameOfReferenceSequence" in struct_ds:
    #             ref_frame = struct_ds.ReferencedFrameOfReferenceSequence[0].FrameOfReferenceUID
    #
    #         ct = None
    #         for c in self.ct_series:
    #             ct_ds = pydicom.dcmread(c["path"], stop_before_pixels=True)
    #
    #             if ct_ds.FrameOfReferenceUID == ref_frame:
    #                 ct = c
    #                 break
    #
    #         # -------------------------
    #         # 4. Mapping speichern
    #         # -------------------------
    #         self.mapped_sets.append({
    #             "dose": dose,
    #             "plan": plan,
    #             "struct": struct,
    #             "ct": ct
    #         })