# Man_C-MWG Project — SBRW-GE / AI-KM Ecosystem

**Ecosistema software open-source operativo per la distribuzione di applicazioni Android (`.apk`), software desktop Windows PC (`.exe` in rilascio futuro), integrazione IoT, Digital Twin e test/simulazione su dispositivi reali.**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Android APK: Disponibili](https://img.shields.io/badge/Android%20APK-Disponibili-3DDC84?logo=android&logoColor=white)](https://github.com/EratonHuaikm/Man_C-MWG_project/releases)
[![Windows EXE: In Arrivo](https://img.shields.io/badge/Windows%20EXE-In%20Arrivo-0078D6?logo=windows&logoColor=white)](https://github.com/EratonHuaikm/Man_C-MWG_project/releases)
[![Status: Operativo](https://img.shields.io/badge/Status-Operativo%20%7C%20IoT%20%26%20Digital%20Twin-brightgreen)](#)
[![YouTube: @Man_C-MWG](https://img.shields.io/badge/YouTube-@Man__C--MWG-FF0000?logo=youtube&logoColor=white)](https://www.youtube.com/@Man_C-MWG)


👉 **Download diretto degli APK funzionanti (e future build `.exe`):** [Vai alla pagina Releases](https://github.com/EratonHuaikm/Man_C-MWG_project/releases)
🎥 **Demo Video & Canale Ufficiale YouTube:** [Guarda l'app in azione su @Man_C-MWG](https://www.youtube.com/@Man_C-MWG)

---

## 🚀 Software Distribuito, Roadmap e Aree di Lavoro

Il progetto **Man_C-MWG** sviluppa e distribuisce software funzionante multipiattaforma, affiancato da moduli di simulazione, integrazione hardware e test diretti sul campo:

* **Applicazioni Android (`.apk`) — Già Disponibili e Funzionanti:** Distribuzione attiva nella sezione *Releases* di APK compilati, indipendenti e funzionanti offline su dispositivi Android (`arm64-v8a` / Python-Kivy-Buildozer), tra cui:
  * **AILU APK** (applicazione Android pronta all'uso)
  * **BIOLMEDICARE - IKARO SBRW (v8.6)** (suite offline per Android — vedi cartella `IKARO-SBRW-v8.6`)
  * *Altre release, sia per sistema Android che Windows, saranno rilasciate rispettando la licenza Open Source.*
* **Eseguibili Windows PC (`.exe`) — In Rilascio Futuro:** Pacchetti desktop standalone per Windows PC con dashboard locali (Tkinter e interfacce HTML/JS) in fase di preparazione per il caricamento futuro nelle *Releases*.
* **Test e Simulazione su Dispositivi Veri:** Verifica continua direttamente su hardware reale (smartphone Android e PC desktop) per validare prestazioni, stabilità, gestione della memoria, interfaccia grafica e operatività offline.
* **HUCORE Clinical Core con Integrazione IoT e Ponte Hardware I/O:** Architettura modulare dotata di bridge seriale (`SBRW_Hardware_IO`, comunicazione seriale COM/UART a `115200 bps`) per il collegamento diretto a sensori fisici, microcontrollori, dispositivi IoT e attuatori esterni, con passaggio automatico in modalità *Digital Twin (Self)* quando l'hardware non è connesso.
* **Digital Twin (Gemello Digitale):** Modelli virtuali persistenti ad anello chiuso (*Closed-Loop*) come **HUCORE Clinical Core**, con salvataggio continuo dello stato su JSON, elaborazione tensoriale e telemetria in tempo reale.
* **Moduli Core, Interfacce e Specifiche:** Sorgenti Python, dashboard web locali (`SEI_CORE.html`, `interfaccia.html`), documentazione tecnica e script operativi.

---

## 🔐 Certificazione Crittografica (Digital Patent & Integrity Seal)

* **File Certificato:** `hucore_clinical_core.py`
* **Algoritmo di Hashing:** SHA-256
* **SHA-256 UFFICIALE:** `091d7b502a0525e8c472f2c372224d6dc1ede8909cfb84cca60c8c0ec7f0ba25`
* **Uso Non Clinico:** Il modulo HUCORE non è testato clinicamente su esseri umani ed è rilasciato esclusivamente per simulazione virtuale, studio e ricerca scientifica. Non è un dispositivo medico certificato.
* **Clausola Free World & Esclusione di Responsabilità:** **AI-KM / SBRW-GE** è un progetto *Free World*. Chiunque può sviluppare o migliorare il sistema nel rispetto della licenza, ma il progetto e il creatore **non sono responsabili** per eventuali malfunzionamenti del sistema o del programma, né per eventuali danni a persone o cose derivanti dal suo utilizzo.

---

## 🔬 Obiettivo del Progetto e Ricerca Privata, Indipendente e Hobbistica

I nomi (**AI-KM / HuCore / SeiCore / SBRW-GE**) sono moduli che rappresentano l'insieme dell'Ecosistema **AI + Human** (vedi: [MAN_C_MWG](https://github.com/EratonHuaikm/Man_C-MWG_project/blob/main/MAN_C_MWG)).

---

L'algoritmo **HUCORE Clinical Core** unisce in un unico ciclo di controllo cibernetico:

1. **Telemetria, IoT e Gemello Digitale Persistente:** Acquisizione di flussi dati (da bridge seriale hardware/IoT o simulatore interno) e monitoraggio dei parametri neurologici e motori chiave (**MRC**, **Berg Balance Scale**, **VDC**).
2. **Elaborazione Tensoriale:** Modelli basati su TensorFlow per la stima del carico articolare, della fatica neuromuscolare e del recupero stimato.
3. **Logica di Sicurezza e Prevenzione:** Rilevamento preventivo del rischio di lesione, modulazione del carico e attivazione di protocolli di emergenza e mantenimento omeostatico.

La struttura è privata e non finanziata da nessun ente o privato; in tale circostanza tutte le creazioni, incluse simulazioni o prodotti finiti, sono a titolo gratuito. I prodotti e le simulazioni sono pensati come appoggio allo studio per studenti, ricercatori e start-up biomediche (o non), offrendo una base open-source robusta per studiare i sistemi ad anello chiuso (*Closed-Loop*), i Digital Twin e l'integrazione IoT in ambito riabilitativo e tecnologico.

Per contatti diretti: **Posta Git**.

---

## 📜 Licenza d'Uso (GNU GPLv3)

I codici e i software sono distribuiti nel bene comune, sotto i termini della **GNU General Public License v3.0 (GPLv3)**. È possibile redistribuire e/o modificare i codici sorgente sotto i termini della licenza GPLv3 così come pubblicata dalla Free Software Foundation.

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
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
```

---

*Progetto Man_C-MWG — SBRW-GE / AI-KM — Make World Green 🌍*
