import datetime
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import eel
import numpy as np
import csv
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import os


eel.init("web")


@eel.expose
def datei_auswahl():
    global df,file_path,filename
    root = tk.Tk()
    root.withdraw()

    #Dateipfad erfragen
    file_path = filedialog.askopenfilename()
    print(file_path)
    filename=os.path.basename(file_path)
    filename=filename.replace(".xlsx","")
    filename=filename.replace(".csv","")

    header_required=['Login', 'Pin', 'Nachname', 'Vorname', 'Zedat-Benutzername', 'Matrikelnummer']
    #Unterscheiden zwischen csv und excel und Einlesen der Daten
    if ".csv" in file_path:
        df = pd.read_csv(file_path)
    elif ".xlsx" in file_path:
        df = pd.read_excel(file_path)
    
    #Validierung der Datei
    header=list(df.head(0))
    if not header==header_required:
        return None
    else:
        return len(df.index)

@eel.expose
def verteilung_python(konfiguration,anzahl_studierende,puffergröße):
    print(konfiguration,anzahl_studierende,puffergröße)
    #Check, ob zu wenig Räume ausgewählt wurden
    übersetzung_zahl_kapa={1:150,2:180,3:330}
    zähler_ausgewählte_plätze=0
    for key,item in konfiguration.items():
        for schlüssel,zahl in übersetzung_zahl_kapa.items():
            if item==schlüssel:
                zähler_ausgewählte_plätze=zähler_ausgewählte_plätze+zahl-int(puffergröße)
    
    anzahl_studierende=anzahl_studierende
    print(f"Plätze: {zähler_ausgewählte_plätze}, Studierende: {anzahl_studierende}")
    if zähler_ausgewählte_plätze<anzahl_studierende:
        print("hier")
        return bool(0)
    df['Durchgang'] = ""
    df['Ort'] = ""
    
    #Verteilung
    eec1=150-int(puffergröße)
    eec2=180-int(puffergröße)

    anzahl_tn=len(df.index)

    zähler_index=0
    zähler_durchgang=0
    while zähler_index<anzahl_tn:
        for durchgang in konfiguration:
            print(durchgang)
            zähler_durchgang+=1
            nummer_durchgang=f"Durchgang {zähler_durchgang}"
            räume=konfiguration[durchgang]
            
            
            if räume==1:
                for i in range(0,eec1):
                    if zähler_index==anzahl_tn:
                        break
                    df.at[zähler_index,'Durchgang']=nummer_durchgang
                    df.at[zähler_index,'Ort']="EEC 1"
                    zähler_index+=1
                    print(zähler_index)

            
            if räume==2:
                for i in range(0,eec2):
                    if zähler_index==anzahl_tn:
                        break
                    df.at[zähler_index,'Durchgang']=nummer_durchgang
                    df.at[zähler_index,'Ort']="EEC 2"
                    zähler_index+=1
                    print(zähler_index)
            
            if räume==3:
                for i in range(0,eec1):
                    if zähler_index==anzahl_tn:
                        break
                    df.at[zähler_index,'Durchgang']=nummer_durchgang
                    df.at[zähler_index,'Ort']="EEC 1"
                    zähler_index+=1
                    print(zähler_index)

                
                for i in range(0,eec2):
                    if zähler_index==anzahl_tn:
                        break
                    df.at[zähler_index,'Durchgang']=nummer_durchgang
                    df.at[zähler_index,'Ort']="EEC 2"
                    zähler_index+=1
                    print(zähler_index)


    df.to_csv(f"(Verteilt) {filename}.csv",sep=";")


    









eel.start("index.html",size=(700, 600))