import sys
from PyQt6.QtWidgets import QApplication

from src.viewer_ct import CTViewer
from src.dicom_indexer import DicomIndexer
from src.patient_handler import PatientHandler


if __name__ == "__main__":

    indexer = DicomIndexer("./data/RT")

    pat_list = indexer.get_patient_list()

    selected_patient = indexer.select_patient(pat_list)
    print(f"\nLade Patient: {selected_patient}")

    pat_handler = PatientHandler(selected_patient, indexer.get_json_file_dir())
    cur_pat = pat_handler.get_pat_obj()
    print(f"Patient Name: {cur_pat.get_patient_name()}")
    print(f"Patient RT-DOSE: {cur_pat.get_rt_dose_series()}")
    print(f"RT-DOSE-Path: {cur_pat.get_rt_dose_path()}")

    if cur_pat.get_ct_series():
        app = QApplication(sys.argv)
        ct_viewer = CTViewer(cur_pat)
        ct_viewer.show_image_data()
        ct_viewer.show()
        sys.exit(app.exec())
    else:
        raise ValueError("Patient has no CT-series!")
        # mr_viewer = MRViewer(cur_pat)
