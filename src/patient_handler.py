import ijson
#from src.patient import Patient
from src.putzies import Patient


class PatientHandler:
    def __init__(self, patient_name, json_file_dir):
        self.patientName = patient_name
        self.json_file_dir = json_file_dir

        self.patient_obj = Patient(patient_name)

        self.check_json_file()

    def check_json_file(self):
        try:
            with open(self.json_file_dir, "r") as file:

                cur_patient = ijson.items(file, self.patientName)

                for json_item in cur_patient:

                    for study_uid, study_data in json_item.items():

                        self.patient_obj.set_sop_instance_iud(study_uid)

                        for ct in study_data.get("ct", []):
                            self.patient_obj.set_ct_data_available()
                            self.patient_obj.add_ct(ct)

                        for mr in study_data.get("mr", []):
                            self.patient_obj.set_mr_data_available()
                            self.patient_obj.add_mr(mr)

                        for rtstruct in study_data.get("rtstruct", []):
                            self.patient_obj.set_rt_struct_data_available()
                            self.patient_obj.add_rtstruct(rtstruct)

                        for dose in study_data.get("dose", []):
                            self.patient_obj.set_rt_dose_data_available()
                            self.patient_obj.add_rtdose(dose)

                        for plan in study_data.get("rtplan", []):
                            self.patient_obj.add_rtplan(plan)

                        for seg in study_data.get("seg", []):
                            self.patient_obj.set_seg_data_available()
                            self.patient_obj.add_seg(seg)

        except FileNotFoundError:
            print("JSON File not found!!!")

    # def check_json_file(self):
    #     try:
    #         with open(self.json_file_dir, "r") as file:
    #             cur_patient = ijson.items(file, self.patientName)
    #
    #             for json_item in cur_patient:
    #                 # print(f"JSON item for {self.patientName}")
    #                 # print(json_item)
    #                 for data in json_item:
    #                     # print(f"SOP Instance UID: {data}")
    #                     self.patient_obj.set_sop_instance_iud(data)
    #                     for plan_data in json_item[data]:
    #                         # print(plan_data)
    #                         match plan_data:
    #                             case "ct":
    #                                 self.patient_obj.set_ct_data_available()
    #                                 self.patient_obj.set_ct_path(json_item[data]["ct"])
    #                             case "mr":
    #                                 self.patient_obj.set_mr_data_available()
    #                                 self.patient_obj.set_mr_path(json_item[data]["mr"])
    #                             case "rtstruct":
    #                                 self.patient_obj.set_rt_struct_data_available()
    #                                 self.patient_obj.set_rt_struct_path(
    #                                     json_item[data]["rtstruct"]
    #                                 )
    #                             case "dose":
    #                                 self.patient_obj.set_rt_dose_data_available()
    #                                 self.patient_obj.set_rt_dose_path(
    #                                     json_item[data]["dose"]
    #                                 )
    #                             case "seg":
    #                                 self.patient_obj.set_seg_data_available()
    #                                 self.patient_obj.set_seg_path(
    #                                     json_item[data]["seg"]
    #                                 )
    #                             case _:
    #                                 break
    #     except FileNotFoundError:
    #         print("JSON File not found!!!")

    def get_pat_obj(self):
        return self.patient_obj
