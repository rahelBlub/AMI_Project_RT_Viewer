# Projekt2: RT-Viewer

### Gegeben:
DICOM Radiotherapy Datensätze mit
- Planungs-Daten (CT, MRT, CB-CT)
- RT-Dose und RT-Structure-Set

### Anforderungen:
- Anzeige als orthogonale MPR + HU-Einstellfenster
- Anzeige einer Liste alle Strukturen mit DICOM-Metadaten
- An-/Ausschalten der Strukturen (aus RT-Structure-Set)
- Dosisanzeige als transparente Colourwash bzw. Isolinien + Legende
- Anzeige der Dosis Min/Max/Mean einer Schicht + aktuelle Dosis Maus über Bild
 
### Herausforderungen:
- Radiotherapy Daten analysieren und auswerten
- Strukturen in orthogonalen MPRs anzeigen


## Shell Commands:

````shell
pip install -r .\requirements.txt
````

````shell
# create virtual enviroment /.venv :
python3 -m venv .venv

#activate virtual enviroment:
source .venv/bin/activate
````
