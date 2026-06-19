import matplotlib as mpl
from matplotlib.widgets import Slider
import matplotlib.pyplot as plt
from matplotlib import axes

mpl.rcParams["figure.facecolor"] = "#121212"
mpl.rcParams["axes.facecolor"] = "#121212"
mpl.rcParams["text.color"] = "white"
mpl.rcParams["xtick.color"] = "white"
mpl.rcParams["ytick.color"] = "white"

plt.rcParams["figure.constrained_layout.use"] = True
plt.rcParams["figure.facecolor"] = "black"

SLIDER_BG = "#1e1e1e"
SLIDER_ACTIVE = "#4CAF50"
TEXT_COLOR = "white"
SLIDER = "#3fa7ff"
TEXT = "#e0e0e0"
CT_COLORMAP = "gray"
DOSE_COLORMAP = "jet"
SEG_COLORMAP = "Reds"

FIG_BG = "#0e0e0e"
AX_BG = "#1a1a1a"

DOSE_ALPHA = 0.35
SEG_ALPHA = 0.25

FIG_WIDTH = 10
FIG_HEIGHT = 8

def create_slider(ax, label, vmin, vmax, vinit, color):
    slider = Slider(ax, label, vmin, vmax, valinit=vinit, color=color)

    slider.label.set_color(TEXT_COLOR)

    return slider

#def image_style():
    #plt.fig.set_facecolor("#1a1a1a")
    #ax.axis("off")
    # ax.set_xticks([])
    # ax.set_yticks([])
    # ax.axhline(y, color="red")
    # ax.axvline(x, color="red")

    # Dois overlay
    #ax.imshow(dose, cmap="jet", alpha=0.4)

    # segmentation
    #ax.imshow(seg_mask, cmap="Reds", alpha=0.3)