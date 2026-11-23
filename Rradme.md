# AIKMGE N1 Ton — SBRW-BMS SYMBIOTE

**Versione:** `3.0.0` | **Licenza:** `GNU GPL v3.0 & GVN (Open Source)` | **Architettura:** `Pure Sandbox v3` | **Rete:** `Zero Internet` | **Privilegi:** `Zero Root`

**AIKMGE N1 Ton** è un progetto **Open Source** e **Free World** di telemetria hardware, gestione energetica (BMS) e protezione termica per dispositivi Android, progettato per operare in totale autonomia locale senza permessi di root e senza alcuna connessione a server esterni.

---

## Architettura: Core Madre, Moduli Aggiuntivi e Contenuti Premium

Il progetto è strutturato su due livelli distinti, entrambi coperti dalle medesime tutele legali (**GNU GPL v3.0**, **GVN** e clausola **Free World AI-KM**):

1. **Core Madre (`main.py` madre & `buildozer.spec` madre)**: costituisce il motore originario del sistema, comprendente l'HUD Kivy Pure Sandbox, la telemetria BMS, il filtro di impedenza interna ($\text{IRR}$), il protocollo binario con verifica **CRC-16** / **Anti-Replay** e il Digital Twin **APWM**.
2. **Moduli Aggiuntivi e Contenuti Premium (integrati nell'APK in fase di compilazione)**: l'eseguibile Android (`AIKMGE_N1_Ton_Universal.apk`) include i **contenuti premium** e le evoluzioni native integrate durante la compilazione in corso, tutti ugualmente protetti da **GNU GPL v3.0** e **GVN**:
   * **Eco-VPN (`SbrwEcoVpnService`)**: servizio VPN locale (*sinkhole*) gestito automaticamente dal governor di sistema (`SandboxEcoController`) per il risparmio energetico e termico, senza instradamento di dati verso l'esterno.
   * **Bio-Lock (`SbrwAccessibilityService`)**: servizio di accessibilità **cieco** (`canRetrieveWindowContent="false"`) dedicato esclusivamente al blocco schermo (`GLOBAL_ACTION_LOCK_SCREEN`) preservando lo sblocco biometrico.
   * **Scudo LCD**: controllo dinamico della luminosità del display con ripristino automatico delle impostazioni utente.
   * **Ponte USB-OTG & APWM Digital Twin**: rilevamento hardware nativo di periferiche USB-OTG con scambio frame e controllo integrità **CRC-16**.
   * **Foreground Bar**: notifica persistente a basso consumo con telemetria in tempo reale di batteria, potenza, temperatura, stato VPN e OTG.

---

## Installazione su Android

1. Scarica **`AIKMGE_N1_Ton_Universal.apk`** dalla sezione **Releases**.
2. Verifica l'integrità dei file tramite gli hash SHA-256 riportati nella tabella qui sotto.
3. Installa l'APK sul dispositivo (abilitando l'installazione da origini sconosciute se richiesto).
4. **Attivazione ECO-VPN**: apri l'app e tocca **ATTIVA ECO-VPN** per concedere il consenso VPN di sistema. Il pulsante passerà a **`ECO-VPN: PRONTO`** (gestito automaticamente dal governor).
5. **Attivazione BIO-LOCK (Android 13+)**:
   * Poiché l'app è installata fuori dal Play Store, Android blocca di default l'interruttore di Accessibilità (*"Impostazioni con limitazioni"*).
   * Vai in **Impostazioni > App > AIKMGE N1 Ton** > tocca i **tre puntini (⋮)** in alto a destra (o scorri in fondo su Android 14/15) > **Consenti impostazioni con limitazioni**.
   * Torna in **Impostazioni > Accessibilità > App scaricate > AIKMGE N1 Ton** e attiva il servizio.

---

## File della Release e Verifica Integrità (SHA-256)

> **Nota sulla verifica degli hash:** Gli hash SHA-256 dei sorgenti sono calcolati sul **`main.py` madre** e sul **`buildozer.spec` madre**. Nell'APK (`AIKMGE_N1_Ton_Universal.apk`) sono inclusi i **contenuti premium** e i moduli evolutivi integrati durante la compilazione in corso, tutti protetti da **GNU GPL v3.0** e **GVN**.

| File | Ruolo | SHA-256 |
| :--- | :--- | :--- |
| `AIKMGE_N1_Ton_Universal.apk` | Pacchetto Android compilato (Core + Evoluzioni + Contenuti Premium) | `1be91b9260ae2e06c976899cb0111b01683c2e0babf080049dc851248e7e7766` |
| `A.png` | Icona ufficiale del progetto | `1d9bfb9bec1b564e2b2fee84d63417ba840aff262d5229ddae94f303d86246d9` |
| `main.py` | Sorgente Core madre | `23e575746746e6e491ce0def593480c189cb93d4eb125ef67accfc2bb2e2f313` |
| `buildozer.spec` | Configurazione Buildozer madre | `65fdbe1d18973fddaef60bbf3f516457af56bc41b0180cc3f95ad3d7768bd6b0` |

Per verificare automaticamente tutti i file scaricati tramite `SHA256SUMS.txt`:

```bash
sha256sum -c SHA256SUMS.txt
```

---

## Licenza Open Source — GNU GPL v3.0, GVN & Clausola Free World AI-KM

### 1. Licenza Open Source (GNU GPL v3.0 & GVN)
Questo progetto — inclusi il Core madre, i moduli aggiuntivi e i contenuti premium integrati nell'APK in compilazione — è **software libero e Open Source**, distribuito e protetto sotto licenza **GNU General Public License v3.0 (GNU GPLv3)** e **GVN**.
* Chiunque è libero di eseguire, studiare, condividere, sviluppare e migliorare il codice sorgente utilizzandolo correttamente.
* In conformità con il principio di **copyleft forte** della GNU GPL v3.0, qualsiasi opera derivata, modifica o ridistribuzione deve mantenere il codice sorgente aperto e pubblico sotto la medesima licenza **GNU GPL v3.0**, citando sempre l'autore e il progetto originale.
* Il testo integrale della licenza GNU GPL v3.0 è consultabile su [gnu.org/licenses/gpl-3.0](https://www.gnu.org/licenses/gpl-3.0.html).

### 2. Clausola Free World AI-KM
* **AI-KM** è un progetto **Free World**.
* **Nessuno può appropriarsi, copiare per scopi commerciali/rivendita, chiudere il codice o brevettare** questo progetto, il Core madre, i contenuti premium o i suoi moduli evolutivi.

### 3. Esonero di Responsabilità (Disclaimer)
* Il software, i binari e la documentazione sono forniti **"AS-IS"** (così come sono), senza garanzie esplicite o implicite di alcun tipo.
* Lo Sviluppatore/Ideatore e **AI-KM** **non sono responsabili** per eventuali malfunzionamenti del sistema o del programma, né per eventuali danni diretti o indiretti a persone, dispositivi o proprietà derivanti dall'uso, dall'installazione o dalla modifica del software. Ogni utente utilizza il sistema sotto la propria esclusiva responsabilità.

---

**Make World Green 🌍**
