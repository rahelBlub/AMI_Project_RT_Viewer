from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler
from src.dicom_indexer import DicomIndexer
from src.patient_handler import PatientHandler

# TODO: am Ende evtl anpassen, sodass man
# das Programm via shell aufrufen kann mit
# $python3 main.py --p ./data/RT/LungData_01

# TODO: https://github.com/brenthuisman/dosia/blob/master/dicom/__init__.py

if __name__ == "__main__":
    indexer = DicomIndexer("./data/RT")

    pat_list = indexer.get_patient_list()
    print(pat_list)

    pat_handler = PatientHandler(pat_list[3], indexer.get_json_file_dir())
    cur_pat = pat_handler.get_pat_obj()

    viewer = CTViewer(cur_pat)
    viewer.show()

    # mr_viewer = MRViewer()
