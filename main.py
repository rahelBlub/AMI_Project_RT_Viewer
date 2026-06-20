from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler
from src.dicom_indexer import DicomIndexer
from src.patient_handler import PatientHandler


# TODO: https://github.com/brenthuisman/dosia/blob/master/dicom/__init__.py

if __name__ == "__main__":
    indexer = DicomIndexer("./data/RT")

    pat_list = indexer.get_patient_list()
    print(pat_list)

    selected_patient = indexer.select_patient(pat_list)

    print(f"\nLade Patient: {selected_patient}")

    pat_handler = PatientHandler(selected_patient, indexer.get_json_file_dir())
    cur_pat = pat_handler.get_pat_obj()
    print(f"Patient Name: {cur_pat.get_patient_name()}")

    print(f"mapped set: {cur_pat.get_mapped_sets()}")

    #d_handler = DicomHandler(cur_pat)
    viewer = CTViewer(cur_pat)
    viewer.show()

    # mr_viewer = MRViewer()
