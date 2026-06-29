# Projekt2: RT-Viewer

---
## Setup

```shell
git clone https://github.com/rahelBlub/AMI_Project_RT_Viewer.git
```
Es wurde der **gesamte** RT Datensatz aus dem exterenn Workspace in folgendes Verzeichnis geladen:

````
AMI-Project RT-Viewer\data\RT
````

Als nächstes müssen die requirements.txt installiert werden.

```bash
pip install -r .\requirements.txt
```
````shell
# create virtual enviroment /.venv :
python3 -m venv .venv

#activate virtual enviroment:
source .venv/bin/activate
````

Mit Starten der `main.py` wird das Programm ausgeführt.


```bash
python main.py
```
Daraufhinn erfolgt eine Auflistung aller Datensätze und eine Abfrage, welcher Patient ausgewählt werden soll. 
Damit ist der Datensatz gemeint.

````
Verfügbare Patienten:

[1] VdQuNEovq74GZdUJixmOfGgV8
[2] LUNG1-001
[3] LUNG1-010
[4] Pancreas-CT-CB_001
[5] Pancreas-CT-CB_002
[6] Pancreas-CT-CB_003
[7] VS-SEG-001
[8] VS-SEG-002
[9] VS-SEG-003
[10] VS-SEG-004
[11] VS-SEG-005

Patient auswählen: 4
````
Wir haben vorrangig mit dem *Pancreas-CT-CB_001* gearbeitet, da dieses RT-Dosen beinhaltet.

Falls mehrer CT-Sätze in dem Datensatz gefunden wurden, erscheint eine weitere Abfrage, welcher genutzt werden soll:

````
Verfügbare CT-Sets:

[1] PANCREAS DI, iDose (3)
[2] Aligned CB07
[3] 
[4] Aligned resampled CB02
[5] 

CT-Set auswählen: 1
````

Hier haben wir immer den ersten Satz genutzt.

Anschließend wird das Fenster des CT Viewers geöffent:

<img src="data/images/CT_View.png">

Mit den jeweilige Slidern unter den Bildern wird durch die einzelnen Schnittbilder des Datensatzes iteriert. 
Gleichzeitig passt sich die Dosisverteilung an. Die Intensität der Dosis wird einmal durch die Skala auf der rechten Seite des Bildes verdeutlicht 
und weiter am linken unteren Bildrand in Gy angezeigt, wenn mit der Maus über die entsprechende Bildstelle gehovert wird.

Am unteren Rand des Fensters befinden sich die beiden Slider, welche der Einstellung des Window Center und Window Width dienen.

## Aufgabenstellung

<table>
<tr>
<th style="text-align:left;"> 
Gegeben:

DICOM Radiotherapy Datensätze mit

- Planungs-Daten (CT, MRT, CB-CT)
- RT-Dose und RT-Structure-Set

Anforderungen:
- Anzeige als orthogonale MPR + HU-Einstellfenster
- Anzeige einer Liste alle Strukturen mit DICOM-Metadaten
- An-/Ausschalten der Strukturen (aus RT-Structure-Set)
- Dosisanzeige als transparente Colourwash bzw. Isolinien + Legende
- Anzeige der Dosis Min/Max/Mean einer Schicht + aktuelle Dosis Maus über Bild
 
Herausforderungen:

- Radiotherapy Daten analysieren und auswerten
- Strukturen in orthogonalen MPRs anzeigen</th>
<th> <img src="data/images/ziel_gui.png" width="400"> </th>
</tr>
</table>




