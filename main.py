from networkx.algorithms.cuts import volume

from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler

#TODO: am Ende evtl anpassen, sodass man
# das Programm via shell aufrufen kann mit
# $python3 main.py --p ./data/RT/LungData_01

if __name__ == "__main__":
    data_path = "./data/RT/LungData_01"

    d_handler = DicomHandler(data_path)

    #volume = d_handler.create_ct_volume() # mit windowing nur noch mit HU Werten!
    volume = d_handler.create_ct_volume_with_HU()
    voxelspacing = d_handler.get_voxelspacing()

    viewer = CTViewer(volume, voxelspacing)
    viewer.show()

