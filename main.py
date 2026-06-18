from src.ct_viewer import CTViewer
from src.dicom_handler import DicomHandler

if __name__ == "__main__":
    data_path = "./data/RT/LungData_01"

    d_handler = DicomHandler(data_path)

    volume = d_handler.create_ct_volume()
    voxelspacing = d_handler.get_voxelspacing()

    viewer = CTViewer(volume, voxelspacing)
    viewer.show()
