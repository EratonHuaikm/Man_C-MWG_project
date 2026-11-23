<p align="center">
  <img src="ailu_avatar.png" alt="AiLU — Universal API Sentinel" width="180" />
</p>

<h1 align="center">AiLU — AI_LOCAL_UNI • Universal API Sentinel</h1>

<p align="center">
  <strong>Strumento Android locale per diagnostica hardware, ispezione del kernel e audit di sicurezza perimetrale.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Versione-2.3.0-00c853?style=flat-square" alt="Versione 2.3.0" />
  <img src="https://img.shields.io/badge/Architettura-arm64--v8a-0f172a?style=flat-square" alt="Architettura arm64-v8a" />
  <img src="https://img.shields.io/badge/Moduli%20API-6%20Ufficiali-00c853?style=flat-square" alt="6 Moduli API" />
  <img src="https://img.shields.io/badge/Privacy-Zero--Cloud%20%7C%20100%25%20Locale-0f172a?style=flat-square" alt="Zero-Cloud" />
  <img src="https://img.shields.io/badge/Licenza-Free%20World-00c853?style=flat-square" alt="Free World" />
</p>

---

## Panoramica

**AiLU (AI_LOCAL_UNI • Universal API Sentinel)** è un'applicazione Android standalone progettata per eseguire un controllo completo dello stato del dispositivo interrogando direttamente le API native di Android, i socket POSIX e le interfacce del kernel Linux.

L'intera architettura è **Locale / Zero-Cloud** ed esegue le scansioni **su richiesta (on-demand)**: nessuna telemetria viene inviata all'esterno e nessun servizio pesante drena inutilmente la batteria in background. Ogni interrogazione — singola o globale — viene salvata in formato strutturato nel file locale `ailu_brain_memory.json`.

---

## I 6 Moduli API Ufficiali

Dall'hub principale è possibile ispezionare ogni singolo sottosistema oppure eseguire una scansione completa con **`AGGIORNA TUTTE LE API & SALVA JSON`**.

| # | Modulo | API / Interfacce Interrogate | Parametri e Controlli Rilevati |
| :-: | :--- | :--- | :--- |
| **1** | **Batteria & Power API** | `android.os.BatteryManager` | Percentuale carica (`EXTRA_LEVEL`), stato alimentazione (`EXTRA_STATUS`), temperatura interna °C (`EXTRA_TEMPERATURE`), tensione istantanea in mV (`EXTRA_VOLTAGE`), corrente istantanea in µA (`BATTERY_PROPERTY_CURRENT_NOW`), chimica cella (`EXTRA_TECHNOLOGY`). |
| **2** | **Stato Esatto RAM & ZRAM API** | `ActivityManager.MemoryInfo` + Kernel | Memoria totale (`MemTotal`), disponibile (`MemAvailable`), RAM attiva occupata (`RAM_USED`), PageCache & Buffers di sistema (`RAM_CACHE`), ZRAM / Swap totale (`SWAP_TOTAL`) e libera (`SWAP_FREE`). |
| **3** | **Archiviazione & StatFs API** | `android.os.StatFs` + POSIX `statvfs` | Capacità partizione totale, spazio usato e libero (GB e %), dimensione blocco I/O hardware (`getBlockSizeLong()`), inodes allocabili (`statvfs.f_favail`), percorso partizione dati attiva (`Environment.getDataDirectory()`). |
| **4** | **CPU, Kernel & Hardware API** | `android.os.Build` + Kernel Linux `sysfs` | Architettura ABI, core attivi, clock MHz e frequenza massima hardware CPU0 (`cpufreq/cpuinfo_max_freq`), versione esatta del kernel Linux (`Os.uname().release`), uptime dall'accensione (`SystemClock.elapsedRealtime()`). |
| **5** | **Rete, Socket MTU & DNS API** | `POSIX Socket` + `Kernel Net Sysfs` | Indirizzo IP locale (`Socket.getsockname()`), topologia NAT e isolamento RFC1918 (`NetworkInterface`), dimensione pacchetto MSS/MTU (`sys/class/net/mtu`), latenza stack TCP/IP interno (`NET_PING`), stato resolver DNS e visibilità processi user-space Zero-Cloud (`NET_DNS`). |
| **6** | **Opzioni Sviluppo & Porta 5555** | `Settings.Global` + `Local Socket` | Scanner esposizione demone ADB TCP/IP su `127.0.0.1:5555` (rilevamento rischio ADB Wi-Fi), stato Opzioni Sviluppatore (`DEVELOPMENT_SETTINGS_ENABLED`), stato ponte Debug USB (`ADB_ENABLED`), guida sicurezza perimetrale (`PERIMETER_GUIDE`). |

---

## Memoria Locale JSON (`ailu_brain_memory.json`)

Ogni modulo dispone del comando **`INTERROGA ORA QUESTA API & SALVA NEL JSON`**, mentre la schermata Hub integra **`AGGIORNA TUTTE LE API & SALVA JSON`**.  
Tutte le letture vengono sincronizzate localmente in `ailu_brain_memory.json` per consentire audit offline, confronto temporale dei parametri e ispezione forense senza dipendenze cloud.

---

## Installazione (Release Ufficiale)

1. Vai nella sezione **[Releases](../../releases)** di questo repository.
2. Scarica l'artefatto verificato **`ailusentinel-2.3.0-arm64-v8a-release-universal.apk`** (`24.82 MB` / `24.817.039 byte`) insieme a **`SHA256SUMS.txt`**.
3. Verifica l'impronta crittografica SHA-256 prima dell'installazione (vedi sezione successiva).
4. Installa l'APK sul tuo dispositivo Android `arm64-v8a`.

### Compilazione da Sorgente

Il repository include i sorgenti completi per la ricompilazione trasparente tramite Buildozer (`main.py`, `buildozer.spec`, `ailu_avatar.png`):

```bash
buildozer -v android release
```

---

## Integrità Crittografica e Verifica SHA-256

Tutti i file rilasciati sono protetti da impronta crittografica **SHA-256**. Qualsiasi modifica, anche di un singolo bit, invalida immediatamente l'hash corrispondente.

```text
9cf7585f379f985c3f0cab87c0e0bcc05368449316592a8e10a6688744ad3039  ailu_avatar.png
edb247ce28aebb657f8da60ef6e1d9424135b9a3e9bac331b0d2090ae1b91d1a  ailusentinel-2.3.0-arm64-v8a-release-universal.apk
58fb6b5c4d1f64afde67d62c2881d4177bdb705255e7b0590bcd4b5d4fdf403f  buildozer.spec
52719445f0aa97d5ba1517165c46da91158ba338f247bd1cb03053ae78364454  main.py
```

### Come verificare i file scaricati

**Linux / macOS / Termux (Android):**
```bash
sha256sum -c SHA256SUMS.txt
```
Risultato atteso per ogni file: **`OK`**.

**Windows (PowerShell):**
```powershell
Get-FileHash .\ailusentinel-2.3.0-arm64-v8a-release-universal.apk -Algorithm SHA256
```

---

## Struttura del Repository

```text
.
├── main.py                  # Codice sorgente principale AiLU (UI + 6 Moduli API + JSON Memory)
├── buildozer.spec           # Configurazione ufficiale di build Android
├── ailu_avatar.png          # Icona e asset grafico ufficiale AiLU
├── SHA256SUMS.txt           # Manifest crittografico SHA-256 dei file
└── README.md                # Documentazione tecnica e guida alla verifica
```

---

## Licenza Free World & Esclusione di Responsabilità

Questo software è rilasciato come progetto **Free World** nell'ambito dell'ecosistema **AI-KM / SBRW-GE**:

* **Uso etico e sviluppo aperto:** chiunque può studiare, verificare, sviluppare e migliorare il codice sorgente in modo trasparente e corretto.
* **Divieto di appropriazione commerciale:** nessuno può appropriarsi del progetto, copiarlo per venderlo o brevettarlo come proprietà esclusiva di terzi.
* **Esclusione di responsabilità:** il creatore e il progetto AI-KM non sono responsabili per eventuali malfunzionamenti del sistema o del programma, né per danni diretti o indiretti a persone, dispositivi o proprietà derivanti da un uso improprio o non conforme. Chiunque utilizzi questo strumento lo fa sotto la propria esclusiva responsabilità.

---

<p align="center"><strong>Make World Green 🌍</strong></p>
v2.3.0
