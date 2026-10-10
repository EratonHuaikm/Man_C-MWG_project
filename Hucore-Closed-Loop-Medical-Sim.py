# ==============================================================================
# SBRW-GE | HUCORE DIGITAL TWIN - MOTORE ATTIVO CON PERSISTENZA DI STATO
# "Libero Open Source a qualsiasi entità interessata, Studenti o Start Up, 
# Nel bene comune, Umano e medico. Progetto non testato (solo virtualmente). MWG"
# ==============================================================================

import time
import os
import json
from collections import deque
import numpy as np
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("[SISTEMA AI-KM: ONLINE]")
print("[HUCORE DIGITAL TWIN ATTIVO: MOTORE PERSISTENTE IN LOOP CHIUSO AVVIATO]\n")

class Hucore_TensorBiomeccanico:
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


class Hucore_PredittoreLesioni:
    def __init__(self):
        self.finestra_storica = deque(maxlen=10)

    def valuta_rischio_lesione(self, mrc, berg, integrita):
        self.finestra_storica.append((mrc, berg, integrita))
        if len(self.finestra_storica) < 2:
            return 0.0 
        mrc_trend = self.finestra_storica[0][0] - self.finestra_storica[-1][0]
        berg_drop = self.finestra_storica[0][1] - self.finestra_storica[-1][1]
        return (mrc_trend * 10.0) + (berg_drop * 2.5) + (100.0 - integrita)


class Hucore_PazientePersistente:
    def __init__(self, file_stato="cartella_clinica_paziente.json"):
        self.file_stato = file_stato
        self.carica_o_inizializza()

    def carica_o_inizializza(self):
        """Carica lo stato clinico precedente o inizializza il paziente critico se è il primo accesso."""
        if os.path.exists(self.file_stato):
            with open(self.file_stato, 'r') as f:
                dati = json.load(f)
                self.mrc = dati.get("mrc", 2)
                self.berg = dati.get("berg", 32)
                self.vdc = dati.get("vdc", 32.0)
                self.integrita = dati.get("integrita", 80.0)
                print(f"[MEMORIA CORE] Cartella clinica precedente caricata con successo.")
        else:
            # Stato critico iniziale assoluto per la prima presa in carico
            self.mrc = 2
            self.berg = 32
            self.vdc = 32.0
            self.integrita = 80.0
            print(f"[MEMORIA CORE] Nessun record precedente. Inizializzazione nuovo paziente critico.")
        
        self.in_trattamento = True

    def salva_stato(self):
        """Salva in modo persistente i progressi raggiunti per la prossima seduta."""
        dati = {
            "mrc": self.mrc,
            "berg": self.berg,
            "vdc": self.vdc,
            "integrita": self.integrita
        }
        with open(self.file_stato, 'w') as f:
            json.dump(dati, f, indent=4)
        print(f"[MEMORIA CORE] Stato clinico salvato permanentemente su file.")

    def aggiorna_stato_terapeutico(self, coeff_terapia):
        if coeff_terapia > 1.0: # Intervento d'urgenza / TENS
            self.berg = min(56, self.berg + 2)
            self.mrc = min(5, self.mrc + 1)
            self.vdc = min(55.0, self.vdc + 3.0)
            self.integrita = min(100.0, self.integrita + 4.0)
        else: # Mantenimento controllato
            self.integrita = max(0.0, self.integrita - 1.0)

        if self.mrc <= 1 or self.berg < 20:
            self.in_trattamento = False

    def stampa_stato(self):
        print(f" [PAZIENTE LIVE] MRC: {self.mrc}/5 | Berg: {self.berg}/56 | VDC: {self.vdc} m/s | Integrità: {self.integrita:.1f}%")


if __name__ == "__main__":
    tensor_bio = Hucore_TensorBiomeccanico()
    predittore = Hucore_PredittoreLesioni()

    # Istanzia il paziente caricando la memoria reale persistente
    paziente = Hucore_PazientePersistente()

    print("="*65)
    print(" AVVIO DIGITAL TWIN: SESSIONE CLINICA PERSISTENTE IN LOOP CHIUSO ")
    print("="*65)
    print("Il Core riprende la seduta dal punto esatto in cui si era interrotto.\n")

    ciclo = 1
    while paziente.in_trattamento and ciclo <= 5:
        print(f"\n--- CICLO CLINICO ATTIVO #{ciclo} ---")
        paziente.stampa_stato()

        # 1. Elaborazione Tensoriale
        cinematica = tensor_bio.elabora_cinematica(paziente.mrc, paziente.berg, paziente.vdc)
        print(f" [HUCORE TENSOR] Carico Articolare: {cinematica[0]:.2f} | Fatica Neuromuscolare: {cinematica[1]:.2f}")

        # 2. Predizione Rischio
        rischio = predittore.valuta_rischio_lesione(paziente.mrc, paziente.berg, paziente.integrita)
        print(f" [PREDIZIONE] Indice di Rischio Clinico: {rischio:.1f}")

        # 3. Decisione Core
        if paziente.mrc <= 2 or paziente.berg < 40 or paziente.vdc < 40.0:
            coeff = 1.5
            decisione = "INTERVENTO URGENTE: Scarico motorio e stimolazione antalgica (TENS)."
        else:
            coeff = 0.8
            decisione = "EQUILIBRIO CLINICO: Mantenimento e potenziamento controllato."

        print(f" [CORE DECISIONE] {decisione}")
        
        # 4. Evoluzione e chiusura loop
        paziente.aggiorna_stato_terapeutico(coeff)
        print(f" [ATTUATORE] Terapia erogata. Risposta biologica registrata.")

        time.sleep(1.0)
        ciclo += 1

    # Salvataggio automatico dello stato evoluto al termine della seduta
    paziente.salva_stato()

    print("\n" + "="*65)
    print(" SESSIONE CLINICA SALVATA. IL PAZIENTE MANTIENE I PROGRESSI ACQUISITI. MWG 🌍")
    print("="*65)
