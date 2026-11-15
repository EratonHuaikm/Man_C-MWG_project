---

## 🔐 Certificazione Crittografica (Digital Patent & Integrity Seal)

* **File Certificato:** `hucore_clinical_core.py`
* **Algoritmo di Hashing:** SHA-256
* **SHA-256 UFFICIALE:** `091d7b502a0525e8c472f2c372224d6dc1ede8909cfb84cca60c8c0ec7f0ba25`

---

## ⚠️ Avviso Importante: Natura della Repository (Solo Simulazione)

Questo repository pubblico contiene esclusivamente una **versione di simulazione (Digital Twin Self-Mode)** del modulo **HUCORE Clinical Core**. 

* **Natura del Codice Pubblico:** Il codice sorgente qui presente implementa un ambiente virtuale dimostrativo, utile per la ricerca accademica, la didattica, la prototipazione rapida e la visualizzazione grafica tramite interfaccia Tkinter.
* **Core Produttivo Riservato:** Il motore clinico avanzato, i moduli hardware proprietari di livello industriale e le ottimizzazioni definitive **non sono pubblicati su GitHub** e rimangono protetti dal vincolo di riservatezza assoluta del progetto.
* **Progetto Non Testato clinicamente su esseri umani:** Questo software è rilasciato esclusivamente per finalità di simulazione virtuale, studio e ricerca scientifica. Non è un dispositivo medico certificato.

---

## 🔬 Obiettivo del Progetto e Ricerca Scientifica

L'algoritmo unisce in un unico ciclo di controllo cibernetico:
1. **Telemetria e Gemello Digitale Persistente:** Monitoraggio dei parametri neurologici e motori chiave (**MRC**, **Berg Balance Scale**, **VDC**).
2. **Elaborazione Tensoriale:** Modelli basati per la stima del carico articolare e della fatica neuromuscolare.
3. **Logica di Sicurezza e Prevenzione:** Rilevamento preventivo del rischio di lesione e attivazione di protocolli di emergenza e mantenimento omeostatico.

La struttura è pensata per offrire a studenti, ricercatori e start-up biomediche una base open-source robusta per studiare i sistemi ad anello chiuso (*Closed-Loop*) in ambito riabilitativo.

---

## 📜 Licenza d'Uso (GNU GPLv3)

Questo software di simulazione è distribuito nel bene comune, umano e medico, sotto i termini della **GNU General Public License v3.0 (GPLv3)**.

È possibile redistribuire e/o modificare il codice sorgente sotto i termini della licenza GPLv3 così come pubblicata dalla Free Software Foundation. 

```text
HUCORE Clinical Core (Simulation Edition)
Copyright (C) 2026 SBRW-GE / Make World Green 🌍
Official SHA-256: 091d7b502a0525e8c472f2c372224d6dc1ede8909cfb84cca60c8c0ec7f0ba25

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

# ==============================================================================
# SBRW-GE | HUCORE CLINICAL CORE - DIGITAL TWIN PERSISTENTE CON UI (TKINTER)
# "Libero Open Source a qualsiasi entità interessata, Studenti o Start Up, 
# Nel bene comune, Umano e medico. Progetto non testato (solo virtualmente). MWG"
# ------------------------------------------------------------------------------
# SHA-256 UFFICIALE:
# 091d7b502a0525e8c472f2c372224d6dc1ede8909cfb84cca60c8c0ec7f0ba25
# ==============================================================================

import random
import time
import threading
import sys
import tkinter as tk
import json
import os
from collections import deque
from PIL import Image, ImageTk
import numpy as np
import tensorflow as tf
import serial

# Soppressione log TensorFlow per pulizia terminale
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# ==============================================================================
# --- MODULO I/O HARDWARE (PONTE CON IL MONDO FISICO) ---
# ==============================================================================

class SBRW_Hardware_IO:
    def __init__(self, porta='COM3', baudrate=115200):
        self.porta = porta
        self.baudrate = baudrate
        self.connessione_attiva = False
        self.seriale = None
        self.dati_fisici_correnti = [0.0, 0.0, 0.0]

    def inizializza_ponte(self):
        try:
            self.seriale = serial.Serial(self.porta, self.baudrate, timeout=0.1)
            self.connessione_attiva = True
            print(f"[I/O HARDWARE] Ponte stabilito su {self.porta} a {self.baudrate} bps.")
            
            self.thread_lettura = threading.Thread(target=self._leggi_flusso_sensori, daemon=True)
            self.thread_lettura.start()
            return True
        except serial.SerialException as e:
            print(f"[I/O WARNING] Nessun hardware rilevato su {self.porta}. Interfaccia attiva in modalità Digital Twin (Self).")
            self.connessione_attiva = False
            return False

    def _leggi_flusso_sensori(self):
        while self.connessione_attiva and self.seriale.is_open:
            try:
                if self.seriale.in_waiting > 0:
                    linea = self.seriale.readline().decode('utf-8').strip()
                    valori = linea.split(',')
                    if len(valori) == 3:
                        self.dati_fisici_correnti = [float(v) for v in valori]
            except Exception:
                pass 
            time.sleep(0.01) 

    def ottieni_telemetria(self):
        return self.dati_fisici_correnti

    def invia_comando_attuatore(self, tipo_terapia, intensita):
        if not self.connessione_attiva or not self.seriale.is_open:
            return
        comando = f"CMD:{tipo_terapia.replace(' ', '_')}:{intensita:.2f}\n"
        self.seriale.write(comando.encode('utf-8'))
        print(f"[I/O HARDWARE] Impulso fisico erogato: {comando.strip()}")

    def chiudi_ponte(self):
        self.connessione_attiva = False
        if self.seriale and self.seriale.is_open:
            self.invia_comando_attuatore("STOP_EMERGENZA", 0.0)
            self.seriale.close()
            print("[I/O HARDWARE] Ponte disconnesso.")


# ==============================================================================
# --- MODULI TENSORIALI CLINICI E BIOMECCANICI ---
# ==============================================================================

class MappaturaBiomeccanicaTensor:
    def __init__(self):
        self.w_carico_articolare = tf.Variable([[1.2], [-0.5], [0.8]], dtype=tf.float32) 
        self.w_fatica_neuromuscolare = tf.Variable([[0.9], [-0.2], [1.5]], dtype=tf.float32)  
        self.w_recupero_stimato = tf.Variable([[-0.8], [1.5], [-0.5]], dtype=tf.float32) 

    @tf.function
    def _calcola_grafo(self, input_fisico):
        carico = tf.matmul(input_fisico, self.w_carico_articolare, transpose_a=True)
        fatica = tf.matmul(input_fisico, self.w_fatica_neuromuscolare, transpose_a=True)
        recupero = tf.matmul(input_fisico, self.w_recupero_stimato, transpose_a=True)
        return tf.concat([carico, fatica, recupero], axis=1)

    def elabora_cinematica(self, mrc, berg, vdc):
        input_fisico = tf.constant([[float(mrc) * 16.0], [float(berg) * 1.78], [float(vdc)]], dtype=tf.float32)
        stato_biomeccanico = self._calcola_grafo(input_fisico)
        return stato_biomeccanico.numpy()[0]


class PredittoreLesioniML:
    def __init__(self):
        self.finestra_storica = deque(maxlen=10)

    def valuta_rischio_lesione(self, mrc, berg, integrita):
        self.finestra_storica.append((mrc, berg, integrita))
        if len(self.finestra_storica) < 2:
            return 0.0 
        mrc_trend = self.finestra_storica[0][0] - self.finestra_storica[-1][0]
        berg_drop = self.finestra_storica[0][1] - self.finestra_storica[-1][1]
        return (mrc_trend * 10.0) + (berg_drop * 2.5) + (100.0 - integrita)


class ModulazioneCaricoMotorio:
    def calcola_bilanciamento(self, mrc, berg, vdc):
        if mrc <= 2 or berg < 40 or vdc < 40.0:
            return 1.5, "INTERVENTO URGENTE: Scarico motorio e stimolazione antalgica (TENS)."
        else:
            return 0.8, "EQUILIBRIO CLINICO: Mantenimento e potenziamento controllato."


# ==============================================================================
# --- MOTORE LOGICO DEL PAZIENTE (PERSISTENZA REALE) E DEL CORE MEDICO ---
# ==============================================================================

class Paziente_Persistente:
    def __init__(self, id_clinico="HUCORE-001", hardware_link=None, file_stato="cartella_clinica_paziente.json"):
        self.id = id_clinico
        self.hardware = hardware_link
        self.file_stato = file_stato
        self.in_trattamento = True
        self.stabilita_raggiunta = False
        self.carica_o_inizializza()

    def carica_o_inizializza(self):
        if os.path.exists(self.file_stato):
            with open(self.file_stato, 'r') as f:
                dati = json.load(f)
                self.mrc = dati.get("mrc", 2)
                self.berg = dati.get("berg", 32)
                self.vdc = dati.get("vdc", 32.0)
                self.integrita = dati.get("integrita", 80.0)
                print(f"[MEMORIA CORE] Cartella clinica {self.id} caricata con successo.")
        else:
            self.mrc = 2
            self.berg = 32
            self.vdc = 32.0
            self.integrita = 80.0
            print(f"[MEMORIA CORE] Nessun record precedente. Inizializzazione nuovo paziente critico.")

    def salva_stato(self):
        dati = {"mrc": self.mrc, "berg": self.berg, "vdc": self.vdc, "integrita": self.integrita}
        with open(self.file_stato, 'w') as f:
            json.dump(dati, f, indent=4)

    def ciclo_esercizio_motorio(self):
        if not self.in_trattamento: return 
        print(f"\n[!] Paziente {self.id} in esecuzione schema motorio...")
        self.integrita = max(0.0, self.integrita - 0.5)

    def ricevi_terapia_core(self, tipo_intervento, intensita, coeff):
        if not self.in_trattamento: return

        print(f"\n[+] SBRW Core eroga: {tipo_intervento} (Potenza calcolata: {intensita:.1f})...")
        if self.hardware and self.hardware.connessione_attiva:
            self.hardware.invia_comando_attuatore(tipo_intervento, intensita)
        
        if coeff > 1.0: 
            self.berg = min(56, self.berg + 2)
            self.mrc = min(5, self.mrc + 1)
            self.vdc = min(55.0, self.vdc + 3.0)
            self.integrita = min(100.0, self.integrita + 4.0)
        else: 
            self.integrita = max(0.0, self.integrita - 1.0)

        self._verifica_stabilita()
        self.salva_stato()

    def _verifica_stabilita(self):
        if self.mrc == 5 and self.berg >= 40 and self.vdc >= 44.0:
            self.stabilita_raggiunta = True
            print("\n" + "="*60)
            print("[!] TARGET CLINICO RAGGIUNTO: Paziente in fase di mantenimento attivo.")
            print("="*60)
        else:
            self.stabilita_raggiunta = False

        if self.mrc <= 1 or self.berg < 20:
            self.in_trattamento = False
            print("\n[--- STOP CLINICO ---] Rischio caduta fatale. Seduta interrotta.")

    def stampa_stato(self):
        stato_str = "MANTENIMENTO" if self.stabilita_raggiunta else "URGENZA ATTIVA"
        print(f"Stato: {stato_str} | MRC: {self.mrc}/5 | Berg: {self.berg}/56 | VDC: {self.vdc:.1f} m/s | Integrità: {self.integrita:.1f}%")


class SBRW_Clinical_Core:
    def __init__(self):
        self.nome = "SBRW-CLINICAL"
        self.mappatura_bio = MappaturaBiomeccanicaTensor()
        self.predittore_lesioni = PredittoreLesioniML()
        self.modulatore = ModulazioneCaricoMotorio()
        
    def analizza_e_intervieni(self, paziente):
        if not paziente.in_trattamento: return

        cinematica = self.mappatura_bio.elabora_cinematica(paziente.mrc, paziente.berg, paziente.vdc)
        print(f"[{self.nome}][TENSOR BIOMECCANICO] Carico Articolare: {cinematica[0]:.2f} | Fatica: {cinematica[1]:.2f}")

        rischio = self.predittore_lesioni.valuta_rischio_lesione(paziente.mrc, paziente.berg, paziente.integrita)
        print(f"[{self.nome}][PREDIZIONE] Indice di Rischio: {rischio:.1f}")

        if rischio > 40.0:
            print(f"[{self.nome}][⚠️ ALLARME LESIONE] Rischio biomeccanico rilevato!")

        coeff, status_terapia = self.modulatore.calcola_bilanciamento(paziente.mrc, paziente.berg, paziente.vdc)
        print(f"[{self.nome}][MODULAZIONE] {status_terapia}")
            
        if coeff > 1.0:
            paziente.ricevi_terapia_core("RILASCIO MIOFASCIALE & TENS", 15.0 * coeff, coeff)
        else:
            paziente.ricevi_terapia_core("MANTENIMENTO TONO MUSCOLARE", 15.0 * coeff, coeff)


# ==============================================================================
# --- DASHBOARD CLINICA IN SELF (TKINTER UI) ---
# ==============================================================================

class ReindirizzaLog:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class SBRW_ClinicalDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("SBRW-GE | Telemetria Motoria e Clinica Persistente")
        self.root.geometry("900x600")
        self.root.configure(bg="#0a0a0a")
        
        self.canvas = tk.Canvas(self.root, width=400, height=600, bg="#0a0a0a", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT)
        
        try:
            self.img = Image.open("paziente_postura.png")
            self.img = self.img.resize((400, 600), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(self.img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.bg_image)
        except Exception:
            self.canvas.create_text(200, 300, text="[Mappa Biomeccanica 3D]", fill="#00ffcc", font=("Consolas", 12))

        self.ginocchio_indicatore = self.canvas.create_oval(180, 400, 220, 440, fill="#005500", outline="")
        self.colonna_indicatore = self.canvas.create_oval(190, 150, 210, 280, fill="#005500", outline="")

        self.log_box = tk.Text(self.root, width=60, height=35, bg="#050505", fg="#00ffcc", font=("Consolas", 9))
        self.log_box.pack(side=tk.RIGHT, padx=10, pady=10)
        
        sys.stdout = ReindirizzaLog(self.log_box)
        
        print("[SISTEMA CLINICO SBRW-GE ONLINE]")
        print("Inizializzazione Vettori I/O e Loop Persistente...")

        self.hardware = SBRW_Hardware_IO('COM3')
        self.hardware.inizializza_ponte()

        self.paziente = Paziente_Persistente(hardware_link=self.hardware)
        self.core_medico = SBRW_Clinical_Core()
        
        self.thread_esecuzione = threading.Thread(target=self.esecuzione_clinica, daemon=True)
        self.thread_esecuzione.start()
        
        self.aggiorna_grafica()

    def aggiorna_grafica(self):
        if hasattr(self, 'paziente') and self.paziente.in_trattamento:
            if self.paziente.mrc <= 2 or self.paziente.berg < 35:
                colore = "#ff0000"
            elif self.paziente.mrc < 5 or self.paziente.berg < 40:
                colore = "#ffaa00"
            else:
                colore = "#00aa00"
                
            self.canvas.itemconfig(self.ginocchio_indicatore, fill=colore)
            
            if self.paziente.stabilita_raggiunta:
                self.canvas.itemconfig(self.colonna_indicatore, fill="#00ffff")
            else:
                self.canvas.itemconfig(self.colonna_indicatore, fill="#005500")
                
        self.root.after(300, self.aggiorna_grafica)

    def esecuzione_clinica(self):
        ciclo = 1
        while self.paziente.in_trattamento and ciclo <= 10:
            print(f"\n--- SESSIONE RIABILITATIVA: FASE {ciclo} ---")
            
            self.paziente.ciclo_esercizio_motorio()
            self.paziente.stampa_stato()
            
            if not self.paziente.in_trattamento:
                break
                
            time.sleep(1.5) 
            self.root.after(0, self.aggiorna_colore, self.colonna_indicatore, "#ffffff")
            
            self.core_medico.analizza_e_intervieni(self.paziente)
            
            time.sleep(0.5)
            self.root.after(0, self.aggiorna_colore, self.colonna_indicatore, "#005500")
            
            time.sleep(1.5)
            ciclo += 1
            
        print("\n" + "="*50)
        print(" SESSIONE CLINICA CONCLUSA. STATO SALVATO.")
        print(" È possibile chiudere l'interfaccia o riavviare per la seduta successiva.")
        print("="*50 + "\n")

        if self.hardware:
            self.hardware.chiudi_ponte()

    def aggiorna_colore(self, elemento, colore):
        self.canvas.itemconfig(elemento, fill=colore)

if __name__ == "__main__":
    root = tk.Tk()
    app = SBRW_ClinicalDashboard(root)
    root.mainloop()
