from networkx.algorithms.cuts import volume

from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler

#TODO: am Ende evtl anpassen, sodass man
# das Programm via shell aufrufen kann mit
# $python3 main.py --p ./data/RT/LungData_01

if __name__ == "__main__":
    data_path = "./data/RT/LUNG1-001/09-18-2008-StudyID-NA-69331/0.000000-NA-82046"

    d_handler = DicomHandler(data_path)

    #volume = d_handler.create_ct_volume()
    volume = d_handler.create_ct_volume_with_HU()
    voxelspacing = d_handler.get_voxelspacing()

    viewer = CTViewer(volume, voxelspacing)
    viewer.show()

