from networkx.algorithms.cuts import volume

from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler
from src.dicom_indexer import DicomIndexer
from src.patient_handler import PatientHandler

import matplotlib as mpl

#TODO: am Ende evtl anpassen, sodass man
# das Programm via shell aufrufen kann mit
# $python3 main.py --p ./data/RT/LungData_01

if __name__ == "__main__":
    indexer = DicomIndexer("./data/RT")
    index = indexer.build()
    indexer.save()

    pat_list = indexer.get_patient_list()

    pat_handler = PatientHandler(pat_list[3], indexer.get_json_file_dir())
    cur_pat = pat_handler.get_pat_obj()

    viewer = CTViewer(cur_pat)
    viewer.show()

    # List all rcParams keys
    # all_keys = mpl.rcParams.keys()
    # print(len(all_keys), "keys found")
    # print(list(all_keys))

