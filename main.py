from networkx.algorithms.cuts import volume

from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler
from src.DicomIndexer import DicomIndexer

#TODO: am Ende evtl anpassen, sodass man
# das Programm via shell aufrufen kann mit
# $python3 main.py --p ./data/RT/LungData_01

if __name__ == "__main__":
    # indexer.inspect_dataset("./data/RT") # to find out where the needed datafiles lie
    indexer = DicomIndexer("./data/RT")
    index = indexer.build()
    indexer.save()

    #data_path = "./data/RT/LUNG1-001/09-18-2008-StudyID-NA-69331/0.000000-NA-82046"
    study_uid = list(index["LUNG1-001"].keys())[0]

    ct_path = index["LUNG1-001"][study_uid]["ct"]

    d_handler = DicomHandler(ct_path)
    #d_handler = DicomHandler(data_path)
    #print(d_handler.get_metadata())

    #volume = d_handler.create_ct_volume() # mit windowing nur noch mit HU Werten!
    volume = d_handler.create_ct_volume_with_HU()
    voxelspacing = d_handler.get_voxelspacing()

    viewer = CTViewer(volume, voxelspacing)
    viewer.show()

