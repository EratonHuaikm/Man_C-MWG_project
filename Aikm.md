# AIKMGE N1 Ton - SBRW-GE Sovereign Core (Beta)

[![Core Status](https://img.shields.io/badge/CORE-PROTECTED%20%F0%9F%8C%8D-00ff00?style=flat-square)]()
[![Engine](https://img.shields.io/badge/ENGINE-C%2B%2B17%20%2F%20PYTHON%20BMS-blue?style=flat-square)]()
[![Platform](https://img.shields.io/badge/PLATFORM-ANDROID%20NDK%20%2F%20PYDROID-orange?style=flat-square)]()
[![Digital Patent](https://img.shields.io/badge/STATUS-DIGITAL%20PATENT%20PROTECTED-purple?style=flat-square)]()

> **⚠️ NOTA SULLA VERSIONE BETA:** Questa release pubblica opera nel rispetto dei vincoli di sicurezza e dei limiti imposti dai produttori hardware Android. La **variante madre del Core SBRW-GE**, invece, opera a livello nativo superando totalmente tali restrizioni commerciali per il controllo diretto dei flussi energetici.

**AIKMGE N1 Ton** è un sistema avanzato di gestione e protezione energetica (**BMS - Battery Management System**) basato su un'architettura ibrida ad alta efficienza. Progettato per operare in ambiente Android, unisce moduli nativi e logica di controllo in tempo reale per monitorare, regolare e proteggere l'integrità del dispositivo.

## 🚀 Caratteristiche Principali

* **Telemetria Energetica e Fisica Reale:** Monitoraggio continuo di tensione ($\text{V}$), corrente filtrata ($\text{mA}$), potenza istantanea ($\text{W}$) e accumulo energetico ($\text{mWh}$).
* **Controllo dell'Impedenza (IRR):** Campionamento della resistenza interna della cella per valutare in tempo reale lo stato di salute e l'efficienza complessiva.
* **Digital Twin APWM:** Firmware virtuale per la modulazione degli impulsi e la gestione dei cicli di pulizia/preservazione della batteria.
* **Interfaccia OLED-Friendly:** UI minimale a bassissimo consumo energetico sviluppata con Kivy e ottimizzata per display a matrice nera.
* **Sicurezza del Perimetro:** Gestione tramite loopback ADB locale (porta 5555) e isolamento dei processi di controllo in background H24.

## ⚙️ Struttura del Sistema e Dualismo Tecnologico

Il sottosistema di gestione energetica e telemetria hardware (**AIKMGE N1 Ton**) è distribuito su due livelli architetturali complementari all'interno della repository:

* **Matrice Logica Originale (`.py` - Python/Kivy/JNI):** Rappresenta l'algoritmo di riferimento puro. Definisce le formule di normalizzazione delle correnti (`uA`/`mA`), il filtraggio degli errori di registro a 64-bit (`JAVA_LONG_MIN`), il calcolo predittivo dell'ETA di carica e la macchina a stati dei **Muscoli BMS**.
* **Eseguibile Nativo Android (`.apk` - C++17 NDK):** Disponibile nella sezione *Releases* (`v3.5-beta`)[span_0](start_span)[span_0](end_span), costituisce la traduzione compilata ad alte prestazioni per l'esecuzione diretta su architettura ARM. Riduce l'overhead della macchina virtuale, garantendo letture a bassa latenza dai nodi `sysfs` e dal `BatteryManager` di sistema.

## 🛡️ Specifiche dei Muscoli BMS (SBRW-BMS Active)

Il motore decisionale interviene in tempo reale distinguendo dinamicamente lo stato di **Carica** dallo stato di **Scarica**:

* **Muscolo Termico:** Soglia di guardia fissata a `38.0 °C` (attivo in ogni stato operativo per prevenire la degradazione chimica delle celle Li-ion).
* **Muscolo Elettrico in Carica:** Attivazione del controllo *Fast-Charge* quando la potenza in ingresso supera i `18.0 W`.
* **Muscolo Elettrico in Scarica (Overpower):** Protezione attiva contro assorbimenti superiori a `4.5 W`.
* **Shield Anti-Drenaggio:** Intervento automatico in scarica su picchi anomali di corrente superiori a `1500.0 mA`.

## 🔒 Sicurezza e Risparmio Energetico

* **Zero Cloud Dependence:** Tutta l'elaborazione telemetrica avviene localmente sul dispositivo in totale isolamento.
* **Ciclo di Vita Ottimizzato:** Sospensione automatica dei thread di polling in background (`on_pause`) per azzerare il consumo parassita a schermo spento, con riattivazione istantanea al risveglio (`on_resume`).
* **Auto-Test Diagnostico:** Verifica dell'integrità matematica dei filtri e delle scale eseguita ad ogni avvio prima dell'attivazione dell'interfaccia grafica.

## 📱 Requisiti di Installazione

1. **Dispositivo Android** con supporto al debug USB / loopback locale attivo.
2. **Ambiente di esecuzione:** 
   * Può essere eseguito direttamente come pacchetto APK nativo precompilato (`AIKMGE_N1_Ton_SBRW`)[span_1](start_span)[span_1](end_span)[span_2](start_span)[span_2](end_span).
   * Oppure interpretato tramite script in ambienti di sviluppo mobile (es. *Pydroid 3* con Kivy).

## 🛠️ Struttura del Codice (Open Source)

Il codice sorgente principale si basa su un'interazione pulita e priva di sovraccarichi con i servizi di sistema Android (`BatteryManager`), gestendo in modo nativo la normalizzazione dei dati hardware per prevenire eccezioni di registro e garantire stabilità operativa.

```python
# Esempio di normalizzazione del flusso energetico all'interno del nucleo
def normalize_current_ma(raw_val):
    val = sanitize_bms_value(raw_val)
    if val == 0.0:
        return 0.0
    return val / 1000.0 if val >= 15000.0 else val
```

**Licenza:** GNU General Public License v3.0 (GPL-3.0)[span_3](start_span)[span_3](end_span)[span_4](start_span)[span_4](end_span)[span_5](start_span)[span_5](end_span)[span_6](start_span)[span_6](end_span)[span_7](start_span)[span_7](end_span)[span_8](start_span)[span_8](end_span)  
**Status:** CORE SBRW-GE - DIGITAL PATENT PROTECTED[span_9](start_span)[span_9](end_span)  
Make World Green 🌍[span_10](start_span)[span_10](end_span)
