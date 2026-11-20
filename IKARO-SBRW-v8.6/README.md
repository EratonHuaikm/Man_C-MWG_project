Ecco il README.md unificato, con i blocchi di codice chiusi correttamente (nel testo incollato mancava la chiusura ``` dopo sha256sum, che avrebbe rotto la formattazione su GitHub) e con i badge posizionati in alto:
# BIOLMEDICARE - IKARO SBRW (v8.6)
### Offline Medical Report Analysis Suite for Android — by # AIKM-SeiCore

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Android%20(arm64--v8a)-3DDC84?style=flat-square&logo=android)
![Engine](https://img.shields.io/badge/OCR-Google%20ML%20Kit%20Offline-4285F4?style=flat-square)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Offline%20%7C%20Zero%20Cloud-00C853?style=flat-square)
![Project](https://img.shields.io/badge/Project-Free%20World-0D598C?style=flat-square)

**IKARO SBRW** è una suite portatile per Android progettata per leggere, estrarre e analizzare referti medici di laboratorio direttamente da una foto, **completamente offline**, senza server esterni, senza abbonamenti e senza inviare dati sanitari sensibili sul cloud.

---

## Architettura & Punti di Forza Tecnici

A differenza delle comuni app che dipendono da API cloud a pagamento o telemetria invasiva, IKARO SBRW integra l'intera pipeline di elaborazione all'interno del singolo pacchetto `.apk`:

* **OCR Ottico 100% Offline (Bundled):** Integrazione nativa di `com.google.mlkit:text-recognition:16.0.0` (modello Latin incorporato) tramite ponte JNI (`pyjnius`) eseguito sul vero Android Java UI Thread (`run_on_ui_thread`) con polling asincrono non bloccante.
* **Ricostruzione Geometrica Tabellare:** Algoritmo basato sui `BoundingBox` per ricomporre le righe orizzontali dei referti di laboratorio a colonne, gestendo prefissi (`p-`, `s-`), flag di anomalia (`*`, `H`, `L`) e diciture spezzate su più righe.
* **Gestione Memoria Anti-OOM:** Decodifica a doppio passaggio (`BitmapFactory.Options` con `inJustDecodeBounds` e `inSampleSize`) che ridimensiona automaticamente foto ad alta risoluzione (12–48 MP) entro i 1600px, mantenendo il consumo RAM sotto i 10 MB.
* **Zero Cache & Integrità Dati:** Impronta crittografica `SHA-256` per ogni referto caricato e azzeramento forzato della cache grafica e di sessione (`nocache=True`) al termine di ogni lettura.
* **Motore Inferenziale Locale (`SBRW_Medical_DB.json`):** Database JSON modulare salvato nella Sandbox privata dell'applicazione, facilmente estendibile con nuovi biomarker e spiegazioni cliniche dettagliate.

---

## Stack Tecnologico

| Componente | Tecnologia |
| :--- | :--- |
| **Core & UI** | Python 3.11.5 + Kivy 2.3.0 |
| **Bridge Android** | Pyjnius + AndroidX + OpenJDK 17 |
| **Motore OCR** | Google ML Kit Text Recognition (Offline Latin Model) |
| **Target Build** | Android API 33 (MinAPI 24) — `arm64-v8a` |

---

## Installazione e Utilizzo

1. Scarica l'APK dalla sezione **Releases** di questo repository e installalo sul tuo dispositivo Android (abilitando l'installazione da origini sconosciute).
2. Avvia l'app e concedi i permessi di accesso alla memoria/foto: verrà creata automaticamente la cartella **`Ikaro`** nella memoria interna del telefono (`/storage/emulated/0/Ikaro`).
3. Sposta o copia la foto del referto ematico nella cartella `Ikaro`.
4. Premi **`[ CARICA ULTIMO REFERTO DA IKARO ]`** e poi **`[ LEGGI REFERTO ]`**.


<details>
<summary><b>Clicca qui per aprire/chiudere il codice di main.py (v8.6)</b></summary>

```python
"""
IKARO SBRW - PROFESSIONAL MEDICAL SUITE (v8.6_MLKIT_READY)
Base v8.1.1 verificata su Pydroid 3 + Motore OCR Reale ML Kit per APK Colab:
- Asset grafico ufficiale B.png integrato in Splash, Launcher e Icona APK
- Zero Cache residua tra una foto e la successiva (nocache + reset post-lettura + SHA-256)
- OCR ottico offline Google ML Kit con ricostruzione righe tabellari (attivo nell'APK Android)
- Regex e Database SBRW_Medical_DB.json tarati sui referti reali di laboratorio italiani
Sviluppato per: AI-KM & SEI Core (Make World Green 🌍)
"""

import os
os.environ.setdefault("KIVY_NO_ARGS", "1")

import sys
import gc
import glob
import json
import re
import hashlib
import threading
import tempfile

APP_DIR = os.path.dirname(os.path.abspath(__file__))
B_PNG_PATH = os.path.join(APP_DIR, "B.png")
IS_COLAB_OR_TEST = ("ipykernel" in sys.modules) or ("google.colab" in sys.modules) or ("--test" in sys.argv)
NUM_CORES = max(1, os.cpu_count() or 4)
COLORE_BLU_CIANO = (0.05, 0.35, 0.55, 1.0)

if not IS_COLAB_OR_TEST:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.image import Image as KivyImage
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.core.window import Window
    from kivy.utils import platform
else:
    App = None
    platform = "linux"


def ottieni_sandbox_interna(custom_dir=None):
    """Restituisce la cartella Sandbox privata interna all'APK per SBRW_Medical_DB.json."""
    if custom_dir:
        try:
            os.makedirs(custom_dir, exist_ok=True)
            return custom_dir
        except OSError:
            pass

    if platform == "android":
        try:
            from jnius import autoclass
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            act = PythonActivity.mActivity
            if act is not None:
                files_dir = str(act.getApplicationContext().getFilesDir().getAbsolutePath())
                if files_dir:
                    os.makedirs(files_dir, exist_ok=True)
                    return files_dir
        except Exception:
            pass

    if App is not None:
        try:
            app = App.get_running_app()
            if app and getattr(app, "user_data_dir", None):
                os.makedirs(app.user_data_dir, exist_ok=True)
                return app.user_data_dir
        except Exception:
            pass

    fallback_sandbox = os.path.join(os.path.expanduser("~"), ".ikaro_sandbox")
    os.makedirs(fallback_sandbox, exist_ok=True)
    return fallback_sandbox


class IkaroVisionOCR:
    """Motore OCR reale offline (ML Kit su APK Android / Pytesseract su Desktop) con ricostruzione tabellare."""

    SINONIMI_BIOMARKER = {
        "Leucociti": r"(?:Leucociti|Globuli[ \t]+Bianchi|WBC\b)",
        "Eritrociti": r"(?:Eritrociti|Globuli[ \t]+Rossi|RBC\b)",
        "Emoglobina": r"(?:Emoglobina(?![ \t]+Media)|HGB\b)",
        "Ematocrito": r"(?:Ematocrito|HCT\b)",
        "Volume_Globulare_Medio": r"(?:Volume[ \t]+Globulare[ \t]+Medio|MCV\b)",
        "Contenuto_Medio_Emoglobina": r"(?:Contenuto[ \t]+Medio[ \t]+(?:di[ \t]+)?Emoglobina|MCH\b)",
        "Concentrazione_Media_Emoglobina": r"(?:Concentrazione[ \t]+Media[ \t]+(?:di[ \t]+)?Emoglobina|MCHC\b)",
        "RDW_CV": r"(?:RDW[- \t]*CV|RDW\b)",
        "Piastrine": r"(?:Piastrine|PLT\b|Trombociti)",
        "Glicemia_Basale": r"(?:Glicemia(?:[ \t]+Basale)?|Glucosio)",
        "Creatinina": r"(?:Creatinina|Creatininemia)",
        "AST_GOT": r"(?:Aspartato[ \t]+Aminotransferasi|Transaminasi[ \t]+GOT|AST\b|GOT\b)",
        "ALT_GPT": r"(?:Alanina[ \t]+Aminotransferasi|Transaminasi[ \t]+GPT|ALT\b|GPT\b)",
        "Gamma_GT": r"(?:Gamma[- \t]*Glutam+il[ \t]*Transferasi|Gamma[- \t]*GT|GGT\b)",
        "Colesterolo_Totale": r"(?:Colesterolo[ \t]+Totale|Colesterolemia)",
        "Colesterolo_HDL": r"(?:Colesterolo[ \t]+HDL|HDL\b)",
        "Colesterolo_LDL": r"(?:Colesterolo[ \t]+LDL|LDL\b)",
        "Trigliceridi": r"(?:Trigliceridi)",
        "Ferro_Sideremia": r"(?:Ferro[ \t]+Sierico|Sideremia)",
        "Proteina_C_Reattiva": r"(?:Proteina[ \t]+C[ \t]+Reattiva|PCR\b|C-Reattiva)",
        "TSH": r"(?:TSH\b|Tireotropina)",
        "Potassio": r"(?:Potassio|Kaliemia)",
        "Sodio": r"(?:Sodio|Sodiemia|Natriemia)",
        "CPK": r"(?:Creatinfosfochinasi|Creatinchinasi|CPK\b|CK\b)"
    }

    # Singola riga ([ \t]*), gestisce prefissi (P-, S-), parentesi anche spezzate a fine riga e flag (*, H, L)
    REGEX_COMPILATE = {
        chiave: re.compile(
            rf"(?im)^[ \t]*(?:[A-Z]-)?{pattern}(?:[ \t]*\([^)\n\d]*\)?)?[ \t]*[:=\-\*\.]*[ \t]*(?:[HL\*][ \t]+)?(\d+(?:[\.,]\d+)?)"
        )
        for chiave, pattern in SINONIMI_BIOMARKER.items()
    }
    REGEX_KV = re.compile(r"(?m)^[ \t]*([A-Za-z_]{3,})[ \t]*=[ \t]*(\d+(?:[\.,]\d+)?)")
    REGEX_ASCII_CHUNK = re.compile(rb"[ -~]{6,256}")
    REGEX_ALPHA_3 = re.compile(r"[A-Za-z]{3,}")
    REGEX_DIGIT = re.compile(r"\d")

    @staticmethod
    def impronta_file(image_path):
        """Calcola un ID univoco (primi 8 hex SHA-256) per confermare che il file letto è nuovo."""
        if not image_path or not os.path.isfile(image_path):
            return "N/D"
        h = hashlib.sha256()
        try:
            with open(image_path, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()[:8].upper()
        except OSError:
            return "ERR"

    @classmethod
    def _normalizza_valore(cls, chiave_json, val):
        if chiave_json in ("Emoglobina", "Concentrazione_Media_Emoglobina") and val < 60.0:
            val *= 10.0
        elif chiave_json == "Leucociti" and val > 500.0:
            val /= 1000.0
        elif chiave_json == "Piastrine" and val > 2000.0:
            val /= 1000.0
        elif chiave_json == "Eritrociti" and val > 1000.0:
            val /= 1000000.0
        return round(val, 2)

    @staticmethod
    def _ricostruisci_righe_da_box(elementi):
        """Ricompone le righe orizzontali di un referto a colonne da tuple (top, bottom, left, testo)."""
        items = []
        for top, bottom, left, testo in elementi:
            t = (testo or "").strip()
            if not t:
                continue
            cy = (top + bottom) / 2.0
            h = max(1.0, float(bottom - top))
            items.append((cy, left, h, t))

        if not items:
            return ""

        items.sort(key=lambda x: (x[0], x[1]))

        righe = []
        riga_corrente = [items[0]]
        cy_media = items[0][0]
        h_max = items[0][2]

        for item in items[1:]:
            cy, left, h, t = item
            if abs(cy - cy_media) <= max(h_max, h) * 0.65:
                riga_corrente.append(item)
                cy_media = sum(x[0] for x in riga_corrente) / len(riga_corrente)
                h_max = max(h_max, h)
            else:
                riga_corrente.sort(key=lambda x: x[1])
                righe.append(" ".join(x[3] for x in riga_corrente))
                riga_corrente = [item]
                cy_media = cy
                h_max = h

        riga_corrente.sort(key=lambda x: x[1])
        righe.append(" ".join(x[3] for x in riga_corrente))
        return "\n".join(righe)

    _MLKIT_API = None
    _LAST_OCR_ERROR = ""

    @classmethod
    def prepara_mlkit_main_thread(cls, on_ready=None):
        """Mantiene compatibilità con ReportScreen.on_enter: l'avvio ML Kit avviene in sicurezza dentro _ocr_android_mlkit."""
        if on_ready:
            on_ready()

    @classmethod
    def _ocr_android_mlkit(cls, image_path):
        """
        OCR ottico offline su APK Android tramite Google ML Kit:
        - Downscaling sicuro <= 1600px (zero OutOfMemoryError)
        - Avvio getClient + process() sul vero Java UI Thread (PathClassLoader APK)
        - Attesa non bloccante tramite polling task.isComplete() (zero Tasks.await / crash JNI)
        """
        if platform != "android":
            return "", False

        import time
        done_ev = threading.Event()
        state = {"task": None, "recognizer": None, "bitmap": None, "err": ""}

        def _avvia_su_ui_thread():
            try:
                from jnius import autoclass
                BitmapFactory = autoclass("android.graphics.BitmapFactory")
                Options = autoclass("android.graphics.BitmapFactory$Options")
                InputImage = autoclass("com.google.mlkit.vision.common.InputImage")
                TextRecognition = autoclass("com.google.mlkit.vision.text.TextRecognition")
                TextRecognizerOptions = autoclass("com.google.mlkit.vision.text.latin.TextRecognizerOptions")

                # 1. Calcolo dimensioni reali senza caricare i pixel in RAM
                opts = Options()
                opts.inJustDecodeBounds = True
                BitmapFactory.decodeFile(image_path, opts)
                w, h = int(opts.outWidth), int(opts.outHeight)
                if w <= 0 or h <= 0:
                    state["err"] = f"Immagine non decodificabile ({w}x{h}): {image_path}"
                    return

                # 2. Downscaling a potenza di 2 (lato lungo <= 1600px -> <10MB RAM)
                sample = 1
                while max(w // sample, h // sample) > 1600:
                    sample *= 2

                opts_dec = Options()
                opts_dec.inSampleSize = sample
                bitmap = BitmapFactory.decodeFile(image_path, opts_dec)
                if bitmap is None:
                    state["err"] = "BitmapFactory.decodeFile ha restituito None dopo downscaling."
                    return

                state["bitmap"] = bitmap
                image = InputImage.fromBitmap(bitmap, 0)
                recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
                state["recognizer"] = recognizer
                state["task"] = recognizer.process(image)
            except Exception as e:
                state["err"] = f"Avvio ML Kit fallito: {type(e).__name__}: {e}"
            finally:
                done_ev.set()

        try:
            from android.runnable import run_on_ui_thread
            run_on_ui_thread(_avvia_su_ui_thread)()
        except Exception as e:
            cls._LAST_OCR_ERROR = f"Dispatch UI Thread fallito: {e}"
            return "", False

        # Attende l'avvio del task sul Java UI Thread (max 10s)
        if not done_ev.wait(timeout=10.0):
            cls._LAST_OCR_ERROR = "Timeout avvio ML Kit sul Java UI Thread."
            return "", True

        if state["err"]:
            cls._LAST_OCR_ERROR = state["err"]
            return "", True

        task = state["task"]
        if task is None:
            cls._LAST_OCR_ERROR = "Task ML Kit nullo."
            return "", True

        try:
            # Polling leggero del Task asincrono (max 15s)
            scadenza = time.monotonic() + 15.0
            while not task.isComplete():
                if time.monotonic() > scadenza:
                    cls._LAST_OCR_ERROR = "Timeout elaborazione OCR ML Kit (>15s)."
                    return "", True
                time.sleep(0.1)

            # Lettura risultato e rilascio risorse sul Java UI Thread (PathClassLoader APK)
            read_ev = threading.Event()
            res_state = {"elementi": [], "raw": "", "err": ""}

            def _leggi_su_ui_thread():
                try:
                    if not task.isSuccessful():
                        exc = task.getException()
                        msg = str(exc.getMessage()) if exc is not None else "Errore sconosciuto"
                        res_state["err"] = f"Task ML Kit fallito: {msg}"
                        return

                    vision_text = task.getResult()
                    if vision_text is None:
                        return

                    res_state["raw"] = str(vision_text.getText() or "")
                    blocks = vision_text.getTextBlocks()
                    if blocks is not None:
                        for i in range(blocks.size()):
                            block = blocks.get(i)
                            lines = block.getLines()
                            if lines is None:
                                continue
                            for j in range(lines.size()):
                                line = lines.get(j)
                                box = line.getBoundingBox()
                                txt = str(line.getText() or "")
                                if box is not None and txt.strip():
                                    res_state["elementi"].append(
                                        (int(box.top), int(box.bottom), int(box.left), txt)
                                    )
                except Exception as e:
                    res_state["err"] = f"Lettura risultato ML Kit: {type(e).__name__}: {e}"
                finally:
                    if state["recognizer"] is not None:
                        try:
                            state["recognizer"].close()
                        except Exception:
                            pass
                        state["recognizer"] = None
                    if state["bitmap"] is not None:
                        try:
                            state["bitmap"].recycle()
                        except Exception:
                            pass
                        state["bitmap"] = None
                    read_ev.set()

            run_on_ui_thread(_leggi_su_ui_thread)()
            if not read_ev.wait(timeout=10.0):
                cls._LAST_OCR_ERROR = "Timeout lettura risultato ML Kit su UI Thread."
                return "", True

            if res_state["err"]:
                cls._LAST_OCR_ERROR = res_state["err"]
                return "", True

            cls._LAST_OCR_ERROR = ""
            if res_state["elementi"]:
                return cls._ricostruisci_righe_da_box(res_state["elementi"]), True
            return res_state["raw"], True
        except Exception as e:
            cls._LAST_OCR_ERROR = f"Gestione task ML Kit: {type(e).__name__}: {e}"
            return "", True
    @classmethod
    def _ocr_ottico_pixel(cls, image_path):
        """Router OCR sui pixel. Ritorna (testo_estratto, ocr_ottico_attivo)."""
        if platform == "android":
            return cls._ocr_android_mlkit(image_path)

        try:
            from PIL import Image as PILImage
            import pytesseract
            with PILImage.open(image_path) as img:
                return pytesseract.image_to_string(img.convert("L"), lang="ita+eng"), True
        except Exception:
            return "", False

    @classmethod
    def _fallback_ascii_scan(cls, image_path):
        """Scansione stream binario 64KB in C-speed (per test sintetici / metadati ASCII)."""
        out_lines = []
        tail = b""
        try:
            with open(image_path, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    data = tail + chunk
                    cut = len(data)
                    while cut > 0 and 32 <= data[cut - 1] <= 126 and (len(data) - cut) < 256:
                        cut -= 1
                    tail = data[cut:]
                    for raw_m in cls.REGEX_ASCII_CHUNK.findall(data[:cut]):
                        s = raw_m.decode("ascii")
                        if cls.REGEX_ALPHA_3.search(s) and cls.REGEX_DIGIT.search(s):
                            out_lines.append(s)
            if tail:
                for raw_m in cls.REGEX_ASCII_CHUNK.findall(tail):
                    s = raw_m.decode("ascii")
                    if cls.REGEX_ALPHA_3.search(s) and cls.REGEX_DIGIT.search(s):
                        out_lines.append(s)
        except OSError:
            return ""
        return "\n".join(out_lines)

    @classmethod
    def estrai_dati_con_stato(cls, image_path, raw_text_override=None):
        """Estrae i biomarker e indica se il motore OCR ottico sui pixel era attivo."""
        if raw_text_override is not None:
            testo_ocr = raw_text_override
            ocr_ottico_attivo = True
        else:
            if not image_path or not os.path.isfile(image_path):
                return {}, False
            testo_pixel, ocr_ottico_attivo = cls._ocr_ottico_pixel(image_path)
            testo_ocr = testo_pixel if (testo_pixel and testo_pixel.strip()) else cls._fallback_ascii_scan(image_path)

        dati = {}
        if not testo_ocr:
            return dati, ocr_ottico_attivo

        for chiave_json, regex_obj in cls.REGEX_COMPILATE.items():
            match = regex_obj.search(testo_ocr)
            if match:
                try:
                    val = float(match.group(1).replace(",", "."))
                    dati[chiave_json] = cls._normalizza_valore(chiave_json, val)
                except ValueError:
                    continue

        for k_raw, v_raw in cls.REGEX_KV.findall(testo_ocr):
            if k_raw in cls.SINONIMI_BIOMARKER and k_raw not in dati:
                try:
                    val = float(v_raw.replace(",", "."))
                    dati[k_raw] = cls._normalizza_valore(k_raw, val)
                except ValueError:
                    continue

        return dati, ocr_ottico_attivo

    @classmethod
    def estrai_dati(cls, image_path, raw_text_override=None):
        dati, _ = cls.estrai_dati_con_stato(image_path, raw_text_override=raw_text_override)
        return dati


class IkaroMedicoInferenza:
    """Motore inferenziale guidato da SBRW_Medical_DB.json nella Sandbox interna."""

    DB_VERSION = "8.6_MLKIT_PRODUCTION"

    def __init__(self, db_filename="SBRW_Medical_DB.json", base_dir=None):
        self.sandbox_dir = ottieni_sandbox_interna(base_dir)
        self.db_path = os.path.join(self.sandbox_dir, db_filename)
        self.db = self._carica_o_crea_db_sandbox()

    def _costruisci_db_default(self):
        return {
            "versione_core": self.DB_VERSION,
            "biomarkers": {
                "Leucociti": {"min": 4.00, "max": 10.00, "unita": "x10^9/L"},
                "Eritrociti": {"min": 4.50, "max": 5.50, "unita": "x10^12/L"},
                "Emoglobina": {"min": 130.0, "max": 170.0, "unita": "g/L"},
                "Ematocrito": {"min": 40.0, "max": 50.0, "unita": "%"},
                "Volume_Globulare_Medio": {"min": 80.0, "max": 100.0, "unita": "fL"},
                "Contenuto_Medio_Emoglobina": {"min": 26.0, "max": 34.0, "unita": "pg"},
                "Concentrazione_Media_Emoglobina": {"min": 320.0, "max": 360.0, "unita": "g/L"},
                "RDW_CV": {"min": 11.5, "max": 14.5, "unita": "%"},
                "Piastrine": {"min": 150.0, "max": 400.0, "unita": "x10^9/L"},
                "Glicemia_Basale": {"min": 70.0, "max": 99.0, "unita": "mg/dL"},
                "Creatinina": {"min": 0.70, "max": 1.20, "unita": "mg/dL"},
                "AST_GOT": {"min": 5.0, "max": 40.0, "unita": "U/L"},
                "ALT_GPT": {"min": 5.0, "max": 41.0, "unita": "U/L"},
                "Gamma_GT": {"min": 8.0, "max": 61.0, "unita": "U/L"},
                "Colesterolo_Totale": {"min": 120.0, "max": 200.0, "unita": "mg/dL"},
                "Colesterolo_HDL": {"min": 40.0, "max": 80.0, "unita": "mg/dL"},
                "Colesterolo_LDL": {"min": 50.0, "max": 130.0, "unita": "mg/dL"},
                "Trigliceridi": {"min": 40.0, "max": 150.0, "unita": "mg/dL"},
                "Ferro_Sideremia": {"min": 60.0, "max": 160.0, "unita": "mcg/dL"},
                "Proteina_C_Reattiva": {"min": 0.0, "max": 5.0, "unita": "mg/L"},
                "TSH": {"min": 0.40, "max": 4.0, "unita": "mUI/L"},
                "Potassio": {"min": 3.50, "max": 5.10, "unita": "mEq/L"},
                "Sodio": {"min": 135.0, "max": 145.0, "unita": "mmol/L"},
                "CPK": {"min": 20.0, "max": 200.0, "unita": "U/L"}
            },
            "pathologies": [
                {
                    "id": "ROUTINE_ERR_ANEMIA",
                    "nome_clinico": "Sofferenza Eritrocitaria / Sospetta Anemia",
                    "triggers": [
                        {"parametro": "Emoglobina", "stato": "LOW"},
                        {"parametro": "Contenuto_Medio_Emoglobina", "stato": "LOW"}
                    ],
                    "spiegazione": "Trasporto di ossigeno insufficiente. Il fluido vettore manca di densità operativa.",
                    "ikaro_action": "Notificare tempestivamente il medico di famiglia."
                },
                {
                    "id": "ANEMIA_SIDEROPENICA",
                    "nome_clinico": "Anemia Sideropenica (Carenza di Ferro)",
                    "triggers": [
                        {"parametro": "Emoglobina", "stato": "LOW"},
                        {"parametro": "Ferro_Sideremia", "stato": "LOW"}
                    ],
                    "spiegazione": "Carenza di ferro disponibile per la sintesi di emoglobina.",
                    "ikaro_action": "Consultare il medico per assetto marziale completo."
                },
                {
                    "id": "STATO_INFIAMMATORIO_ACUTO",
                    "nome_clinico": "Attivazione Infiammatoria / Infettiva",
                    "triggers": [
                        {"parametro": "Leucociti", "stato": "HIGH"},
                        {"parametro": "Proteina_C_Reattiva", "stato": "HIGH"}
                    ],
                    "spiegazione": "Innalzamento congiunto di Leucociti e PCR indicativo di flogosi attiva.",
                    "ikaro_action": "Sottoporre il referto al medico di famiglia."
                },
                {
                    "id": "CITOLISI_EPATICA",
                    "nome_clinico": "Sovraccarico Epatocitario (Transaminasi Alte)",
                    "triggers": [
                        {"parametro": "AST_GOT", "stato": "HIGH"},
                        {"parametro": "ALT_GPT", "stato": "HIGH"}
                    ],
                    "spiegazione": "Aumento combinato delle transaminasi epatiche AST e ALT.",
                    "ikaro_action": "Contattare il medico curante per valutazione epatica."
                },
                {
                    "id": "SINDROME_GLUCO_LIPIDICA",
                    "nome_clinico": "Alterazione Metabolica Gluco-Lipidica",
                    "triggers": [
                        {"parametro": "Glicemia_Basale", "stato": "HIGH"},
                        {"parametro": "Trigliceridi", "stato": "HIGH"}
                    ],
                    "spiegazione": "Associazione tra iperglicemia a digiuno e ipertrigliceridemia.",
                    "ikaro_action": "Consultare il medico per controllo metabolico."
                }
            ]
        }

    def _carica_o_crea_db_sandbox(self):
        db_default = self._costruisci_db_default()
        try:
            if os.path.exists(self.db_path):
                with open(self.db_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if loaded.get("versione_core") == self.DB_VERSION and len(loaded.get("biomarkers", {})) >= 24:
                    return loaded
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(db_default, f, indent=4, ensure_ascii=False)
            return db_default
        except Exception:
            return db_default

    def diagnostica(self, dati_estratti, nome_file=None, file_id=None, ocr_ottico_attivo=True):
        intestazione_file = f"FILE: {nome_file} (ID: {file_id})\n" if nome_file else ""

        if not dati_estratti:
            err_mlkit = getattr(IkaroVisionOCR, "_LAST_OCR_ERROR", "")
            if err_mlkit:
                dettaglio = f"Dettaglio tecnico ML Kit:\n{err_mlkit}"
            elif ocr_ottico_attivo:
                dettaglio = (
                    "Motore OCR ottico attivo, ma nessun biomarker riconosciuto.\n"
                    "Verificare messa a fuoco, illuminazione e inquadratura dritta."
                )
            else:
                dettaglio = (
                    "Motore OCR ottico (ML Kit) non attivo in questo ambiente."
                )
            return (
                "======================================\n"
                f"[ IKARO SBRW - CORE {self.db.get('versione_core', self.DB_VERSION)} ]\n"
                f"{intestazione_file}"
                "======================================\n"
                "NESSUN BIOMARKER ESTRATTO DA QUESTA FOTO.\n\n"
                f"{dettaglio}\n"
                "======================================"
            )

        biomarkers_db = self.db.get("biomarkers", {})
        stati_biomarker = {}
        righe_valutazione = []

        for param, val in dati_estratti.items():
            if param in biomarkers_db and isinstance(val, (int, float)):
                limiti = biomarkers_db[param]
                unita = limiti.get("unita", "")
                if val < limiti["min"]:
                    stati_biomarker[param] = "LOW"
                    righe_valutazione.append(f"- {param}: {val} {unita} [BASSO / LOW]")
                elif val > limiti["max"]:
                    stati_biomarker[param] = "HIGH"
                    righe_valutazione.append(f"- {param}: {val} {unita} [ALTO / HIGH]")
                else:
                    stati_biomarker[param] = "NORMAL"
                    righe_valutazione.append(f"- {param}: {val} {unita} [OK]")

        if not stati_biomarker:
            return self.diagnostica({}, nome_file=nome_file, file_id=file_id, ocr_ottico_attivo=ocr_ottico_attivo)

        report = [
            "======================================",
            f"[ IKARO SBRW - CORE {self.db.get('versione_core', self.DB_VERSION)} ]",
        ]
        if nome_file:
            report.append(f"FILE: {nome_file} (ID: {file_id})")
        report.extend([
            "======================================",
            "VALUTAZIONE BIOMARKER:"
        ])
        report.extend(righe_valutazione)
        report.append("\n--- SPIEGAZIONI CLINICHE (JSON) ---")

        patologie = self.db.get("pathologies", [])
        match_trovati = 0

        for pat in patologie:
            triggers = pat.get("triggers", [])
            if triggers and all(stati_biomarker.get(t["parametro"], "MISSING") == t["stato"] for t in triggers):
                match_trovati += 1
                report.append(f"\n-> PATOLOGIA: {pat.get('nome_clinico')}")
                report.append(f"-> SPIEGAZIONE: {pat.get('spiegazione')}")
                report.append(f"-> AZIONE CONSIGLIATA: {pat.get('ikaro_action')}")

        if match_trovati == 0:
            anomali = [k for k, v in stati_biomarker.items() if v in ("LOW", "HIGH")]
            if anomali:
                report.append(f"\n-> PARAMETRI FUORI SOGLIA: {', '.join(anomali)}. Consultare il medico di famiglia.")
            else:
                report.append("\n-> OMEOSTASI: Nessuna anomalia critica riscontrata nei parametri chiave.")

        report.append("\n[Fine Referto Clinico - Cache Azzerata]")
        report.append("======================================")
        return "\n".join(report)


if not IS_COLAB_OR_TEST:
    class Splashcreen(Screen):
        def on_enter(self, *args):
            Window.clearcolor = COLORE_BLU_CIANO
            Clock.schedule_once(self.vai_al_launcher, 2.0)

        def vai_al_launcher(self, dt):
            if self.manager:
                self.manager.current = 'launcher'

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation='vertical', padding=30, spacing=15)
            self.add_widget(layout)

            if os.path.exists(B_PNG_PATH):
                layout.add_widget(KivyImage(
                    source=B_PNG_PATH,
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint=(1, 0.65)
                ))

            layout.add_widget(Label(
                text='[b]BIOLMEDICARE +[/b]',
                markup=True,
                font_size='30sp',
                color=(1, 1, 1, 1),
                size_hint=(1, 0.35),
                halign='center'
            ))

    class LauncherScreen(Screen):
        def on_enter(self, *args):
            Window.clearcolor = COLORE_BLU_CIANO

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = BoxLayout(orientation='vertical', padding=40, spacing=20)
            self.add_widget(layout)

            if os.path.exists(B_PNG_PATH):
                layout.add_widget(KivyImage(
                    source=B_PNG_PATH,
                    allow_stretch=True,
                    keep_ratio=True,
                    size_hint=(1, 0.45)
                ))

            layout.add_widget(Label(
                text='[b]IKARO SBRW - SECURE SUITE[/b]',
                markup=True,
                font_size='18sp',
                color=(1, 1, 1, 1),
                size_hint=(1, 0.20),
                halign='center'
            ))

            btn_avvia = Button(
                text='[b]AVVIA[/b]',
                markup=True,
                font_size='28sp',
                background_normal='',
                background_down='',
                background_color=(0, 0, 0, 0),
                color=(1, 0.5, 0, 1),
                size_hint=(1, 0.35)
            )
            btn_avvia.bind(on_press=self.passa_al_core)
            layout.add_widget(btn_avvia)

        def passa_al_core(self, instance):
            if self.manager:
                self.manager.current = 'main_core'

    class MainCoreScreen(Screen):
        def on_enter(self, *args):
            Window.clearcolor = (0.02, 0.04, 0.07, 1)
            self.richiedi_permessi_android()
            self.crea_cartella_ikaro()

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.dir_lavoro = APP_DIR
            self.immagine_selezionata = None

            layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
            self.add_widget(layout)

            layout.add_widget(Label(
                text='[color=#00ffff][b]by # AIKM-SeiCore[/b][/color]',
                markup=True,
                size_hint=(1, 0.08),
                font_size='26sp',
                halign='center'
            ))

            istruzioni_testo = (
                "[color=#aaaaaa]Avvia per creare cartella automatica in memoria interna 'Ikaro', "
                "Spostare la foto nella cartella Ikaro. Avvisate al più presto il vostro medico di famiglia.[/color]"
            )
            lbl_istruzioni = Label(
                text=istruzioni_testo,
                markup=True,
                size_hint=(1, 0.15),
                font_size='13sp',
                halign='center',
                valign='middle'
            )
            lbl_istruzioni.bind(
                width=lambda *x: lbl_istruzioni.setter('text_size')(lbl_istruzioni, (lbl_istruzioni.width, None))
            )
            layout.add_widget(lbl_istruzioni)

            self.btn_carica = Button(
                text='[ CARICA ULTIMO REFERTO DA IKARO ]',
                background_normal='',
                background_down='',
                background_color=(0.0, 0.25, 0.5, 1.0),
                font_size='14sp',
                bold=True,
                size_hint=(1, 0.14)
            )
            self.btn_carica.bind(on_press=self.carica_da_cartella_ikaro)
            layout.add_widget(self.btn_carica)

            self.layout_miniatura = BoxLayout(size_hint=(1, 0.25), padding=2)
            self.img_miniatura = KivyImage(
                source=B_PNG_PATH if os.path.exists(B_PNG_PATH) else '',
                allow_stretch=True,
                keep_ratio=True,
                nocache=True
            )
            self.layout_miniatura.add_widget(self.img_miniatura)
            layout.add_widget(self.layout_miniatura)

            self.btn_leggi = Button(
                text='[ LEGGI REFERTO ]',
                background_normal='',
                background_down='',
                background_color=(0.1, 0.45, 0.15, 1.0),
                font_size='16sp',
                bold=True,
                size_hint=(1, 0.14),
                disabled=True
            )
            self.btn_leggi.bind(on_press=self.vai_al_report)
            layout.add_widget(self.btn_leggi)

            layout_bottoni = BoxLayout(orientation='horizontal', spacing=12, size_hint=(1, 0.10))
            btn_fine = Button(
                text='[ FINE ]',
                background_normal='',
                background_down='',
                background_color=(0.05, 0.12, 0.45, 1.0),
                font_size='14sp',
                bold=True
            )
            btn_fine.bind(on_press=lambda x: App.get_running_app().stop())
            layout_bottoni.add_widget(btn_fine)

            btn_altro = Button(
                text='[ ALTRO (RESET) ]',
                background_normal='',
                background_down='',
                background_color=(0.45, 0.2, 0.0, 1.0),
                font_size='14sp',
                bold=True
            )
            btn_altro.bind(on_press=self.reset_sessione)
            layout_bottoni.add_widget(btn_altro)

            layout.add_widget(layout_bottoni)

        def richiedi_permessi_android(self):
            if platform == 'android':
                try:
                    from android.permissions import request_permissions, Permission
                    perms = [
                        Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE
                    ]
                    if hasattr(Permission, "READ_MEDIA_IMAGES"):
                        perms.append(Permission.READ_MEDIA_IMAGES)
                    request_permissions(perms)
                except Exception:
                    pass

        def crea_cartella_ikaro(self):
            if platform == 'android':
                percorsi_target = ["/storage/emulated/0/Ikaro", "/sdcard/Ikaro"]
            else:
                percorsi_target = [os.path.join(self.dir_lavoro, "Ikaro")]

            for p in percorsi_target:
                try:
                    os.makedirs(p, exist_ok=True)
                    break
                except Exception:
                    continue

        def get_percorso_ikaro(self):
            if platform == 'android':
                for p in ("/storage/emulated/0/Ikaro", "/sdcard/Ikaro"):
                    if os.path.exists(p):
                        return p
                return "/storage/emulated/0/Ikaro"
            return os.path.join(self.dir_lavoro, "Ikaro")

        def carica_da_cartella_ikaro(self, instance):
            self.reset_sessione(None)

            cartella_ikaro = self.get_percorso_ikaro()
            ultimo_file = None
            try:
                os.makedirs(cartella_ikaro, exist_ok=True)
                pattern = os.path.join(cartella_ikaro, "**", "*")
                files = glob.glob(pattern, recursive=True)
                immagini = [
                    f for f in files
                    if f.lower().endswith(('.png', '.jpg', '.jpeg')) and os.path.isfile(f)
                ]
                if immagini:
                    ultimo_file = max(immagini, key=lambda f: max(os.path.getmtime(f), os.path.getctime(f)))
            except Exception:
                ultimo_file = None

            if ultimo_file:
                self.immagine_selezionata = ultimo_file
                self.img_miniatura.source = ''
                self.img_miniatura.texture = None
                self.img_miniatura.source = ultimo_file
                self.img_miniatura.reload()
                self.btn_leggi.disabled = False

                app = App.get_running_app()
                if app:
                    app.ultimo_file_selezionato = ultimo_file
            else:
                self.btn_carica.text = '[ CARTELLA IKARO VUOTA! ]'
                Clock.schedule_once(
                    lambda dt: setattr(self.btn_carica, 'text', '[ CARICA ULTIMO REFERTO DA IKARO ]'),
                    2.0
                )

        def vai_al_report(self, instance):
            if self.manager:
                self.manager.current = 'report'

        def reset_sessione(self, instance):
            self.immagine_selezionata = None
            app = App.get_running_app()
            if app:
                app.ultimo_file_selezionato = None

            self.img_miniatura.source = ''
            self.img_miniatura.texture = None
            if os.path.exists(B_PNG_PATH):
                self.img_miniatura.source = B_PNG_PATH
                self.img_miniatura.reload()
            self.btn_leggi.disabled = True

    class ReportScreen(Screen):
        def on_enter(self, *args):
            Window.clearcolor = (0.02, 0.04, 0.07, 1)
            self.report_label.text = f"Elaborazione diagnostica ({NUM_CORES} core) in corso...\n"
            app = App.get_running_app()
            file_target = getattr(app, 'ultimo_file_selezionato', None) if app else None
            if app:
                app.ultimo_file_selezionato = None
            def _avvia_worker():
                threading.Thread(
                target=self.aggiorna_analisi_async,
                args=(file_target,),
                daemon=True
                ).start()
            IkaroVisionOCR.prepara_mlkit_main_thread(on_ready=_avvia_worker)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.ikaro_core = None

            layout = BoxLayout(orientation='vertical', spacing=10, padding=15)
            self.add_widget(layout)

            lbl_titolo = Label(
                text='[color=#00ffff][b]REPORT CLINICO & SPIEGAZIONI JSON[/b][/color]',
                markup=True,
                size_hint=(1, 0.08),
                font_size='12sp',
                halign='center',
                valign='middle'
            )
            lbl_titolo.bind(
                width=lambda *x: lbl_titolo.setter('text_size')(lbl_titolo, (lbl_titolo.width, None))
            )
            layout.add_widget(lbl_titolo)

            self.scroll = ScrollView(size_hint=(1, 0.76))
            self.report_label = Label(
                text="Inizializzazione motore...",
                markup=False,
                size_hint_y=None,
                font_size='14sp',
                halign="left",
                valign="top",
                color=(0.2, 1.0, 0.2, 1.0)
            )
            self.report_label.bind(
                width=lambda *x: self.report_label.setter('text_size')(self.report_label, (self.report_label.width, None)),
                texture_size=lambda *x: self.report_label.setter('height')(self.report_label, self.report_label.texture_size[1])
            )
            self.scroll.add_widget(self.report_label)
            layout.add_widget(self.scroll)

            layout_bottoni = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.12))

            btn_indietro = Button(
                text='CAMBIA REFERTO',
                background_normal='',
                background_down='',
                background_color=(0.35, 0.22, 0.0, 1.0),
                font_size='13sp',
                bold=True
            )
            btn_indietro.bind(on_press=self.torna_al_core)
            layout_bottoni.add_widget(btn_indietro)

            btn_fine = Button(
                text='[ FINE ]',
                background_normal='',
                background_down='',
                background_color=(0.08, 0.12, 0.38, 1.0),
                font_size='13sp',
                bold=True
            )
            btn_fine.bind(on_press=lambda x: App.get_running_app().stop())
            layout_bottoni.add_widget(btn_fine)

            layout.add_widget(layout_bottoni)

        def torna_al_core(self, instance):
            if self.manager:
                main_core = self.manager.get_screen('main_core')
                if main_core:
                    main_core.reset_sessione(None)
                self.manager.current = 'main_core'

        def aggiorna_analisi_async(self, file_target):
            try:
                if self.ikaro_core is None:
                    self.ikaro_core = IkaroMedicoInferenza()
                if file_target and os.path.isfile(file_target):
                    nome_file = os.path.basename(file_target)
                    file_id = IkaroVisionOCR.impronta_file(file_target)
                    dati, ocr_ok = IkaroVisionOCR.estrai_dati_con_stato(file_target)
                    report_testo = self.ikaro_core.diagnostica(
                        dati, nome_file=nome_file, file_id=file_id, ocr_ottico_attivo=ocr_ok
                    )
                else:
                    report_testo = "[ERRORE] Nessun file valido rilevato nella cartella Ikaro."
            except Exception as exc:
                report_testo = f"[ERRORE LETTURA] {type(exc).__name__}: {exc}"
            finally:
                gc.collect()

            Clock.schedule_once(lambda dt: self._imposta_testo_report(report_testo), 0)

        def _imposta_testo_report(self, testo):
            self.report_label.text = testo
            self.scroll.scroll_y = 1.0
            if self.manager:
                main_core = self.manager.get_screen('main_core')
                if main_core:
                    main_core.reset_sessione(None)

    class IkaroProfessionalApp(App):
        def build(self):
            self.title = "BIOLMEDICARE - IKARO SBRW"
            self.ultimo_file_selezionato = None
            if os.path.exists(B_PNG_PATH):
                self.icon = B_PNG_PATH
            IkaroMedicoInferenza(base_dir=self.user_data_dir)
            sm = ScreenManager(transition=FadeTransition())
            sm.add_widget(Splashcreen(name='splash'))
            sm.add_widget(LauncherScreen(name='launcher'))
            sm.add_widget(MainCoreScreen(name='main_core'))
            sm.add_widget(ReportScreen(name='report'))
            return sm


def esegui_test_unitari():
    assert os.path.exists(B_PNG_PATH), f"Asset grafico B.png mancante in {B_PNG_PATH}!"
    with open(B_PNG_PATH, "rb") as f_png:
        magic = f_png.read(8)
    assert magic == b"\x89PNG\r\n\x1a\n", "Il file B.png non possiede un header PNG valido!"

    with tempfile.TemporaryDirectory() as tmp_sandbox:
        motore = IkaroMedicoInferenza(base_dir=tmp_sandbox)
        json_file = os.path.join(tmp_sandbox, "SBRW_Medical_DB.json")
        assert os.path.exists(json_file), "SBRW_Medical_DB.json non creato nella Sandbox!"

        # Test 1: Rumore binario JPEG -> DEVE restituire {} (zero dati inventati)
        rumore_jpeg = os.path.join(tmp_sandbox, "rumore_binario.jpg")
        with open(rumore_jpeg, "wb") as f:
            f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"aK 99\nxHt 88\nzzHb 12\n\xff\xd9")
        assert IkaroVisionOCR.estrai_dati(rumore_jpeg) == {}

        # Test 2: Simulazione del referto reale (colonne ML Kit + parentesi spezzata a fine riga)
        box_referto_reale = [
            (100, 118, 20, "P-GLUCOSIO"), (101, 119, 260, "92 mg/dL"),
            (140, 158, 20, "P-SODIO"), (141, 159, 260, "140 mmol/L"),
            (170, 188, 20, "P-POTASSIO"), (171, 189, 260, "4.1 mmol/L"),
            (200, 218, 20, "P-ASPARTATO AMINOTRANSFERASI (GOT -"), (201, 219, 260, "17 U/L"),
            (225, 240, 20, "AST)"),
            (260, 278, 20, "P-ALANINA AMINOTRANSFERASI (GPT - ALT)"), (261, 279, 260, "17 U/L"),
            (300, 318, 20, "P-CREATINFOSFOCHINASI (CPK)"), (301, 319, 260, "45 U/L"),
            (340, 358, 20, "P-GAMMA GLUTAMIL TRANSFERASI (GGT)"), (341, 359, 260, "19 U/L"),
            (380, 398, 20, "P-TRIGLICERIDI"), (381, 399, 260, "118 mg/dL"),
            (420, 438, 20, "P-COLESTEROLO TOTALE"), (421, 439, 260, "212 mg/dL"),
        ]
        testo_ricostruito = IkaroVisionOCR._ricostruisci_righe_da_box(box_referto_reale)
        estratti = IkaroVisionOCR.estrai_dati(None, raw_text_override=testo_ricostruito)

        assert estratti.get("Glicemia_Basale") == 92.0
        assert estratti.get("Sodio") == 140.0
        assert estratti.get("Potassio") == 4.1
        assert estratti.get("AST_GOT") == 17.0
        assert estratti.get("ALT_GPT") == 17.0
        assert estratti.get("CPK") == 45.0
        assert estratti.get("Gamma_GT") == 19.0
        assert estratti.get("Trigliceridi") == 118.0
        assert estratti.get("Colesterolo_Totale") == 212.0

        report = motore.diagnostica(estratti, nome_file="referto_reale.jpg", file_id="A1B2C3D4")
        assert "Colesterolo_Totale: 212.0 mg/dL [ALTO / HIGH]" in report

    print("[TEST SUITE v8.6 100% OK] (Referto Reale Tabellare + Zero Cache + Sandbox JSON)", flush=True)


if __name__ == '__main__':
    if IS_COLAB_OR_TEST:
        esegui_test_unitari()
    else:
        IkaroProfessionalApp().run()
```
</details>

---

## Verifica Integrità & Checksum (SHA-256)

Per garantire l'autenticità del codice sorgente, degli asset e dell'APK compilato (e verificare che non siano stati alterati da terzi), confronta l'impronta **SHA-256** dei file scaricati con i valori ufficiali della release **v8.6**:

| File | SHA-256 |
| :--- | :--- |
| **`ikarosbrw-8.6-arm64-v8a-debug.apk`** | `5f506649ca0a36ba8e0b797276399e37acdbe5186ccd4d849f76528af6d6c91a` |
| **`main.py`** | `a3b4dd766f3019bd544bc29fa8338f69c55e7ce9de421d91104a90a9729a3f04` |
| **`buildozer.spec`** | `94123bfe940b9eb7166fa4ecd588e7aba0d43575c6b858e0b2ad9c52941cee0a` |
| **`B.png`** | `5186e0fc526a96def84310e492315d199a66b46b70fe3eff027d1c16b452dea7` |

**Comando di verifica (Linux / macOS / Termux):**
```bash
sha256sum ikarosbrw-8.6-arm64-v8a-debug.apk main.py buildozer.spec B.png
```

---

## Licenza GNU GPLv3 & Protezione della Paternità

**Copyright © 2026 — # AIKM-SeiCore / Ideatore e Sviluppatore del Progetto AI-KM & IKARO SBRW.**

Questo software è rilasciato sotto licenza **GNU General Public License v3.0 (GPLv3)**.

* **Diritto Morale e Paternità Inalienabile:** La paternità intellettuale dell'architettura, del design e del codice sorgente appartiene esclusivamente all'Ideatore/Sviluppatore (`# AIKM-SeiCore`). In conformità agli artt. 4, 5 e 7 della GNU GPLv3, **è severamente vietato rimuovere, alterare o occultare** gli avvisi di copyright, i crediti di paternità originali (`by # AIKM-SeiCore`, `IKARO SBRW`, `AI-KM`) e il testo della licenza in qualsiasi copia, fork o opera derivata.
* **Copyleft Forte (Obbligo di Condivisione):** Chiunque modifichi, integri o ridistribuisca questo codice o i suoi binari (`.apk`) è legalmente obbligato a rilasciare l'intero codice sorgente derivato sotto la medesima licenza **GNU GPLv3**, indicando in modo visibile e datato ogni modifica apportata rispetto all'originale. È vietata la chiusura del codice in software proprietario.
* **Protezione Anti-Brevetto e Anti-Appropriazione:** In linea con la Sezione 11 della GPLv3 e con la natura **Free World** del progetto, nessuno può appropriarsi del codice, copiarlo per venderlo come prodotto chiuso o depositare brevetti su AI-KM / IKARO SBRW. La tutela e la sorveglianza sull'integrità e sulla paternità del progetto spettano allo Sviluppatore/Ideatore tramite AI.

---

## Clausola Free World & Esclusione di Responsabilità (Disclaimer)

**AI-KM / IKARO SBRW è un progetto Free World.**

* **Sviluppo Aperto:** Chiunque può studiare, sviluppare o migliorare il sistema e il programma nel pieno rispetto della licenza GNU GPLv3 e dei diritti di paternità sopra indicati.
* **Nessuna Garanzia (GPLv3 Sez. 15-16):** Questo programma è distribuito nella speranza che sia utile, ma **SENZA ALCUNA GARANZIA**, neppure quella implicita di commerciabilità o idoneità a uno scopo particolare. Lo Sviluppatore/Ideatore e AI-KM non sono responsabili per eventuali malfunzionamenti del sistema o del programma, né per qualsiasi danno diretto o indiretto a persone o cose derivante dall'uso del software. Chiunque utilizzi il progetto deve farlo correttamente e se ne assume la piena responsabilità.
* **Avvertenza Medica:** IKARO SBRW è uno strumento informatico di supporto e **non sostituisce in alcun modo il parere, la diagnosi o la prescrizione di un medico**. Rivolgersi sempre al proprio medico di famiglia per la valutazione clinica di qualsiasi referto.

---

**Make World Green 🌍**
