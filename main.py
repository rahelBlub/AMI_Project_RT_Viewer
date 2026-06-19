from networkx.algorithms.cuts import volume

from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler
from src.dicom_indexer import DicomIndexer
from src.patient_handler import PatientHandler

#TODO: am Ende evtl anpassen, sodass man
# das Programm via shell aufrufen kann mit
# $python3 main.py --p ./data/RT/LungData_01

if __name__ == "__main__":
    # indexer.inspect_dataset("./data/RT") # to find out where the needed datafiles lie
    indexer = DicomIndexer("./data/RT")
    index = indexer.build()
    indexer.save()

    pat_list = indexer.get_patient_list()

    pat_handler = PatientHandler(pat_list[0], indexer.get_json_file_dir())
    cur_pat = pat_handler.get_pat_obj()

    d_handler = DicomHandler(cur_pat)
    print("hier")
    # patients = list(index.keys())
    # print(patients)
    #
    # # Bekky: hab idx = 0 weil der existiert immer
    # study_uid = list(index[patients[0]].keys())[0]
    # ct_path = index[patients[0]][study_uid]["ct"]
    #
    # #p7_uid = list(index[patients[6]].keys())[0]
    # #mr_path = index[patients[6]][p7_uid]["mr"]
    #
    # d_handler = DicomHandler(ct_path)
    # #d_handler = DicomHandler(mr_path)
    # #print(d_handler.get_metadata())
    #
    # #volume = d_handler.create_ct_volume() # mit windowing nur noch mit HU Werten!
    # volume = d_handler.create_ct_volume_with_HU()
    # voxelspacing = d_handler.get_voxelspacing()
    # metadata = d_handler.get_metadata()
    #
    # viewer = CTViewer(volume, voxelspacing, metadata)
    # viewer.show()

