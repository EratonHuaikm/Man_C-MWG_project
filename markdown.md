# [CORE TARGET TOOL] COMET

**Connessione PC-Smartphone in airgap logico totale. Bypass tracciamento protocollo MTP/PTP.**

## [SETUP HARDWARE & OS]
1. **Connessione Fisica:** Cavo USB diretto PC <-> Smartphone.
2. **Debug USB:** Rigorosamente ATTIVATO nelle Opzioni Sviluppatore Android.
3. **Configurazione USB Android:** Impostare su "Nessun trasferimento dati" / "Solo ricarica" (tel mod non trasf_file, USB mode colleg).
4. **Zero Indicizzazione:** Nessuna traccia nel file system manager o nei log eventi di sistema (Windows/Android).

## [ARCHITETTURA DIRECTORY]
*   **Android:** Utilizzare o creare la cartella denominata `COMET` nella memoria interna dello smartphone.
*   **PC Windows:** Il binario `COMET.exe` deve risiedere nella directory contenente i tool di trasporto (`P Tools`, `Adb file in adb.exe`).
*   **PC Windows (Output):** I file estratti dal telefono verranno salvati in una sottocartella generata automaticamente (`File, Ricevuti`) situata nella stessa root di `COMET.exe`.

## [ESECUZIONE DOWBLINK: ANDROID -> PC]
1. Posizionare il file da estrarre all'interno della cartella `COMET` (su dispositivo Android).
2. Avviare `COMET.exe` su PC (esecuzione obbligatoria tramite CMD come Amministratore).
3. Interfaccia tool: Cliccare su **[Ricevi]**.
4. Il file verrà trasferito bypassando l'indicizzazione e depositato su PC nella cartella `File, Ricevuti`. Aprire la cartella per accedere al payload.

## [ESECUZIONE UPLINK: PC -> ANDROID]
1. Avviare `COMET.exe` su PC (esecuzione tramite CMD come Amministratore).
2. Interfaccia tool: Cliccare su **[F]**.
3. Si aprirà l'esplora risorse di Windows. Navigare fino alla directory dove risiede il file target e cliccare su *Apri*.
4. Il file verrà caricato e preparato per lo spostamento tramite `P_Tools` all'interno di `COMET.exe`.
5. Interfaccia tool: Cliccare su **[Manda file]**.
6. Il file verrà iniettato in airgap direttamente nella cartella `COMET` su Android.

## [PROTOCOLLO DI TRASPORTO]
*   Stack operativo: `P Tools`, `Adb file` in `adb.exe`.
*   Il trasporto dati avviene integralmente fuori dai demoni standard del sistema operativo. Telemetria e MTP disabilitati via hardware.

## [INTEGRITÀ E SICUREZZA]
*   **Fonte Ufficiale:** Il file `COMET.exe` deve essere scaricato ESCLUSIVAMENTE da questo repository GitHub. Qualsiasi download proveniente da fonti esterne, mirror o forum di terze parti è da considerarsi compromesso e non autorizzato.
*   **Target File:** `COMET.exe`
*   **SHA-256 Hash:** `[58cc6c4aac668ec0e8353f3cf4cc93f2749a7c222fb4bf92bcb9bd34a306a4a2]`
*(Verificare rigorosamente l'hash prima dell'esecuzione per certificare che il binario non abbia subito iniezioni esterne o alterazioni).*

## [LICENZA E DIGITAL PATENT]
Software proprietario (Closed Core). Protetto da architettura di sicurezza blindata e vincolo di riservatezza assoluta.
È severamente vietata la decompilazione, l'alterazione, il reverse engineering e la distribuzione non autorizzata. Nessuna porzione del codice sorgente è di dominio pubblico. 
L'operatività del tool è vincolata ai parametri di sicurezza del C.
