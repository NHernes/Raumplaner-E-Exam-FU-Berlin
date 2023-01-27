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
    pd.set_option('display.max_rows', None)
    if ".csv" in file_path:
        df = pd.read_csv(file_path, sep=";")
    elif ".xlsx" in file_path:
        df = pd.read_excel(file_path)

    df=df.sort_values(by=['Nachname'])
    df = df.reset_index(drop=True)

    #Validierung der Datei
    header=list(df.head(0))

    if not header==header_required:
        return None
    else:
        return len(df.index)


def emailtext_generieren(df):
    liste_durchgänge=[]
    #Ermitteln der vorhandenen Durchgänge
    for index,row in df.iterrows():
        durchgang=row["Durchgang"]
        
        schalter=False
        for eintrag in liste_durchgänge:
            if durchgang in eintrag.values():
                schalter=True
        if not schalter:
            liste_durchgänge.append({"Durchgang": durchgang})

    #Ermitteln der Orte je Durchgang
    for durchgang in liste_durchgänge:
        name_durchgang=durchgang.get("Durchgang")
        for index,row in df.iterrows():
            durchgang_aktuell=row["Durchgang"]
            if name_durchgang==durchgang_aktuell:
                ort_aktuell=row["Ort"]
                if ort_aktuell not in durchgang.values():
                    durchgang[ort_aktuell]=[]
    
    #Ermitteln der Personen je Ort je Durchgang
    for durchgang in liste_durchgänge:
        name_durchgang=durchgang.get("Durchgang")
        for index,row in df.iterrows():
            durchgang_aktuell=row["Durchgang"]
            if name_durchgang==durchgang_aktuell:
                ort_aktuell=row["Ort"]

                if ort_aktuell=="EEC 1" and "EEC 1" in durchgang.keys():
                    durchgang["EEC 1"].append(row["Nachname"])
                elif ort_aktuell=="EEC 2" and "EEC 2" in durchgang.keys():
                    durchgang["EEC 2"].append(row["Nachname"])

    mailtext=""
    for count,i in enumerate(liste_durchgänge):
        schlüssel=list(i.keys())
        textblock=f"<p>{schlüssel[0]} {count+1}:</p> \n <ul>"
        for key in schlüssel:
            if "Durchgang" not in key:
                zugeteilte_personen=i[key]

                listeneintrag=f"<li>{key}: {zugeteilte_personen[0]} bis {zugeteilte_personen[-1]}</li>"
                textblock=textblock+listeneintrag
        textblock=textblock+"</ul>"
        mailtext=mailtext+textblock

    return mailtext


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
        return bool(0)
    
    df['Durchgang'] = np.nan
    df['Ort'] = np.nan
    
    #Verteilung


    anzahl_tn=len(df.index)

    zähler_index=0
    zähler_durchgang=0
    #while zähler_index<anzahl_tn:
    for durchgang in konfiguration:
        eec1=150-int(puffergröße)
        eec2=180-int(puffergröße)

        zähler_durchgang+=1
        nummer_durchgang=f"Durchgang {zähler_durchgang}"
        räume=konfiguration[durchgang]

        def namensabgrenzung(raumgröße):
            
            if i>=(raumgröße-5):
                name_student_aktuell=df.at[zähler_index,'Nachname']
                try:
                    name_student_next=df.at[zähler_index+1,'Nachname']
                    if name_student_aktuell!=name_student_next:
                        #return True
                        return False
                except KeyError:
                    pass
        
        def namensabgrenzung_neu(raumgröße):
            raumgröße_ursprung=raumgröße
            zähler_index_namensprüfung=zähler_index
            anzahl_verringerung_raumgröße=0
            try:
                zähler_index_namensprüfung_ende=zähler_index_namensprüfung+raumgröße
                name_student_ende=df.at[zähler_index_namensprüfung_ende,'Nachname']
                name_student_aktuell=df.at[zähler_index_namensprüfung_ende-1,'Nachname']
                
                print(name_student_aktuell,name_student_ende)
                while name_student_aktuell == name_student_ende:
                    print(name_student_aktuell,name_student_ende)
                    zähler_index_namensprüfung_ende-=1
                    anzahl_verringerung_raumgröße+=1
                    name_student_ende=df.at[zähler_index_namensprüfung_ende,'Nachname']
                
                raumgröße_neu=raumgröße-anzahl_verringerung_raumgröße
                print(anzahl_verringerung_raumgröße,raumgröße, df.at[zähler_index_namensprüfung_ende,'Nachname'] )
                return  raumgröße_neu
            
            except Exception as e:
                print(str(e))
                return raumgröße_ursprung
                
            

        if räume==1:
            eec1=namensabgrenzung_neu(eec1)
            for i in range(0,eec1):

                if zähler_index==anzahl_tn:
                    break
                df.at[zähler_index,'Durchgang']=nummer_durchgang
                df.at[zähler_index,'Ort']="EEC 1"
                
                zähler_index+=1

                    
                

        
        if räume==2:
            eec2=namensabgrenzung_neu(eec2)
            for i in range(0,eec2):
                if zähler_index==anzahl_tn:
                    break
                df.at[zähler_index,'Durchgang']=nummer_durchgang
                df.at[zähler_index,'Ort']="EEC 2"
                
                zähler_index+=1

        
        if räume==3:
            eec1=namensabgrenzung_neu(eec1)
            for i in range(0,eec1):
                if zähler_index==anzahl_tn:
                    break
                df.at[zähler_index,'Durchgang']=nummer_durchgang
                df.at[zähler_index,'Ort']="EEC 1"
                
                zähler_index+=1

                

            eec2=namensabgrenzung_neu(eec2)
            print(eec2)
            for i in range(0,eec2):
                if zähler_index==anzahl_tn:
                    break
                df.at[zähler_index,'Durchgang']=nummer_durchgang
                df.at[zähler_index,'Ort']="EEC 2"
                
                zähler_index+=1

    for index,row in df.iterrows():
        if pd.isnull(df.at[index,"Durchgang"]):
            return bool(1)
        
    df.to_csv(f"(Verteilt) {filename}.csv",sep=";")
    
    email_text=emailtext_generieren(df)
    print(email_text)
    return email_text









eel.start("index.html",size=(850, 620))