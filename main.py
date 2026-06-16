import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import pydicom
import os

folder = "./RT/LUNG1-001/09-18-2008-StudyID-NA-69331/0.000000-NA-82046/"

files = [pydicom.dcmread(os.path.join(folder, f))
         for f in os.listdir(folder)
         if f.endswith(".dcm")]

# Nach Slice-Position sortieren
files.sort(key=lambda x: float(x.ImagePositionPatient[2]))

volume = np.stack([f.pixel_array for f in files])

# Voxelspacing
dy, dx = map(float, files[0].PixelSpacing)
dz = float(files[0].SliceThickness)

print(volume.shape)  # (z, y, x)

# Startpositionen
z_idx = volume.shape[0] // 2
y_idx = volume.shape[1] // 2
x_idx = volume.shape[2] // 2

# -----------------------------
# Figure + Layout
# -----------------------------

fig, axs = plt.subplots(2, 2, figsize=(10, 8))

ax_axial = axs[0, 0]
ax_sagittal = axs[0, 1]
ax_coronal = axs[1, 0]
axs[1, 1].axis('off')  # unten rechts leer

plt.subplots_adjust(bottom=0.25)

# -----------------------------
# Initiale Bilder
# -----------------------------

img_axial = ax_axial.imshow(
    volume[z_idx, :, :],
    cmap='gray',
    interpolation='nearest',
    aspect=dy/dx
)
ax_axial.set_title("Axial")

img_sagittal = ax_sagittal.imshow(
    volume[:, :, x_idx],
    cmap='gray',
    interpolation='nearest',
    aspect=dz/dy
)
ax_sagittal.set_title("Sagittal")

img_coronal = ax_coronal.imshow(
    volume[:, y_idx, :],
    cmap='gray',
    interpolation='nearest',
    aspect=dz/dx
)
ax_coronal.set_title("Coronal")

# -----------------------------
# Slider
# -----------------------------

ax_slider_z = plt.axes([0.15, 0.15, 0.65, 0.03])
slider_z = Slider(ax_slider_z, 'Axial', 0, volume.shape[0]-1,
                  valinit=z_idx, valstep=1)

ax_slider_y = plt.axes([0.15, 0.10, 0.65, 0.03])
slider_y = Slider(ax_slider_y, 'Coronal', 0, volume.shape[1]-1,
                  valinit=y_idx, valstep=1)

ax_slider_x = plt.axes([0.15, 0.05, 0.65, 0.03])
slider_x = Slider(ax_slider_x, 'Sagittal', 0, volume.shape[2]-1,
                  valinit=x_idx, valstep=1)

# -----------------------------
# Update-Funktion
# -----------------------------

def update(val):
    z = int(slider_z.val)
    y = int(slider_y.val)
    x = int(slider_x.val)

    img_axial.set_data(volume[z, :, :])
    img_sagittal.set_data(volume[:, :, x])
    img_coronal.set_data(volume[:, y, :])

    fig.canvas.draw_idle()

slider_z.on_changed(update)
slider_y.on_changed(update)
slider_x.on_changed(update)

plt.show()