import ijson
from src.patient import Patient


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
                            if ct:
                                print("ct files found!")
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
                            # TODO: hardcode raus!
                            print("dose file:", dose)
                            self.patient_obj.set_rt_dose_path(dose["path"])
                            #print(self.patient_obj.get_rt_dose_series())

                        for plan in study_data.get("rtplan", []):
                            self.patient_obj.add_rtplan(plan)
                            #print(self.patient_obj.get_rt_plan_sereies())

                        for seg in study_data.get("seg", []):
                            self.patient_obj.set_seg_data_available()
                            self.patient_obj.add_seg(seg)
                            #print(self.patient_obj.get_segmantation_series())

                        #self.patient_obj.resolve_relationships()

        except FileNotFoundError:
            print("JSON File not found!!!")

    def get_pat_obj(self):
        return self.patient_obj
