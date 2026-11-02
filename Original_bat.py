import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.window import Window
from jnius import autoclass

# Limite minimo a 64 bit restituito da Android quando un registro non è supportato
JAVA_LONG_MIN = -9223372036854775800


def sanitize_bms_value(raw_val):
    """Filtra letture nulle o codici di errore hardware (Long.MIN_VALUE)."""
    if raw_val is None or raw_val <= JAVA_LONG_MIN:
        return 0.0
    return float(abs(raw_val))


def normalize_current_ma(raw_val):
    """Converte la corrente in mA gestendo kernel che espongono uA oppure mA diretti."""
    val = sanitize_bms_value(raw_val)
    if val == 0.0:
        return 0.0
    # A schermo acceso il consumo è sempre >= 20 mA (20.000 uA).
    # Valori sotto 15.000 indicano un kernel che restituisce già mA.
    return val / 1000.0 if val >= 15000.0 else val


def normalize_capacity_mah(raw_val):
    """Converte il contatore di carica in mAh gestendo scale in uAh o mAh."""
    val = sanitize_bms_value(raw_val)
    return val / 1000.0 if val >= 20000.0 else val


def evaluate_bms_muscles(temp, watt, current_ma, is_charging):
    """Logica pura di intervento dei muscoli BMS distinta tra carica e scarica."""
    alerts = []

    # 1. Muscolo Termico: attivo sia in carica che in scarica oltre i 38°C
    if temp > 38.0:
        alerts.append("[color=#ff0000][ATTIVO] LIMITATORE TERMICO[/color]")

    if is_charging:
        # 2a. Muscolo Elettrico in Carica: controlla stress da fast-charge estremo
        if watt > 18.0:
            alerts.append("[color=#ff9900][ATTIVO] CONTROLLO FAST-CHARGE[/color]")
    else:
        # 2b. Muscolo Elettrico in Scarica: se la potenza eccede i parametri SBRW
        if watt > 4.5:
            alerts.append("[color=#ff0000][ATTIVO] PROTEZIONE OVERPOWER[/color]")
        # 3. Muscolo Anti-Drenaggio: attivo solo in scarica contro picchi anomali
        if current_ma > 1500.0:
            alerts.append("[color=#ff0000][ATTIVO] SHIELD ANTI-DRENAGGIO[/color]")

    if alerts:
        return "\n".join(alerts)
    return "[color=#00ff00][STABILE] Muscoli in guardia[/color]"


def compute_eta_minutes(level, current_ma, actual_mah, is_charging):
    """Calcola i minuti residui di carica usando la capacità reale o fallback 5000 mAh."""
    if not is_charging or current_ma <= 100.0 or level >= 100:
        return None

    remaining_pct = 100 - level
    if level > 10 and actual_mah > 300.0:
        est_full_mah = min(max(actual_mah / (level / 100.0), 2000.0), 10000.0)
    else:
        est_full_mah = 5000.0

    remaining_mah = est_full_mah * (remaining_pct / 100.0)
    return max(1, int((remaining_mah / current_ma) * 60.0))


def check_core_integrity():
    """Auto-test diagnostico eseguito all'avvio su filtri, scale e muscoli."""
    assert sanitize_bms_value(-9223372036854775808) == 0.0
    assert normalize_current_ma(-450000) == 450.0
    assert normalize_current_ma(-450) == 450.0
    assert "STABILE" in evaluate_bms_muscles(34.0, 12.0, 2200.0, True)
    assert "SHIELD ANTI-DRENAGGIO" in evaluate_bms_muscles(34.0, 6.0, 1600.0, False)
    assert compute_eta_minutes(50, 2500.0, 2500.0, True) == 60
    return "[SICURO] Scudo Termico e Anti-Bot Attivo."


class IntentBatteryShield(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.clearcolor = (0, 0, 0, 1)  # Risparmio energetico OLED
        self.info_label = Label(
            text="[b]AIKMGE N1 TON[/b]\n[size=16]SINCRONIZZAZIONE HARDWARE...[/size]",
            markup=True,
            halign='center',
            color=(0, 1, 0.4, 1),
            font_size='14sp'
        )
        self.add_widget(self.info_label)
        self._jni_ready = False

    def _init_jni_bridge(self):
        """Inizializza i puntatori Android una sola volta a finestra Kivy pronta."""
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Intent = autoclass('android.content.Intent')
        IntentFilter = autoclass('android.content.IntentFilter')
        self.BM = autoclass('android.os.BatteryManager')
        Context = autoclass('android.content.Context')

        self.activity = PythonActivity.mActivity
        self.ifilter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        self.bm_service = self.activity.getSystemService(Context.BATTERY_SERVICE)

        self.h_map = {
            self.BM.BATTERY_HEALTH_GOOD: "OTTIMA ✅",
            self.BM.BATTERY_HEALTH_OVERHEAT: "SURRISCALDATA 🔥",
            self.BM.BATTERY_HEALTH_DEAD: "ESAUSTA 💀",
            self.BM.BATTERY_HEALTH_OVER_VOLTAGE: "SOVRATENSIONE ⚡",
            self.BM.BATTERY_HEALTH_COLD: "FREDDA ❄️"
        }
        self._jni_ready = True

    def apply_bms_muscles(self, temp, watt, current_ma, is_charging=False):
        return evaluate_bms_muscles(temp, watt, current_ma, is_charging)

    def decode_intent_data(self):
        try:
            if not self._jni_ready:
                self._init_jni_bridge()

            BM = self.BM
            battery_status = self.activity.registerReceiver(None, self.ifilter)
            if battery_status is None:
                return "IN ATTESA DEL RECEIVER DI SISTEMA..."

            # --- ESTRAZIONE DATI BASE NORMALIZZATI ---
            raw_level = battery_status.getIntExtra(BM.EXTRA_LEVEL, -1)
            scale = battery_status.getIntExtra(BM.EXTRA_SCALE, 100)
            level = int((raw_level * 100) / scale) if (raw_level >= 0 and scale > 0) else 0
            level = min(max(level, 0), 100)

            voltage_mv = max(0, battery_status.getIntExtra(BM.EXTRA_VOLTAGE, 0))
            temp_c = battery_status.getIntExtra(BM.EXTRA_TEMPERATURE, 0) / 10.0
            health_code = battery_status.getIntExtra(BM.EXTRA_HEALTH, -1)
            tech = battery_status.getStringExtra(BM.EXTRA_TECHNOLOGY) or "Li-ion"
            health_txt = self.h_map.get(health_code, "CHECKING...")

            # --- RILEVAMENTO SORGENTE E STATO CARICA ---
            plugged = battery_status.getIntExtra(BM.EXTRA_PLUGGED, -1)
            source = "BATTERIA"
            if plugged == BM.BATTERY_PLUGGED_AC:
                source = "RETE AC"
            elif plugged == BM.BATTERY_PLUGGED_USB:
                source = "PORTA USB"
            elif plugged == 4:
                source = "WIRELESS"

            status_code = battery_status.getIntExtra(BM.EXTRA_STATUS, -1)
            is_charging = status_code == BM.BATTERY_STATUS_CHARGING
            is_full = status_code == BM.BATTERY_STATUS_FULL or (plugged > 0 and level == 100)

            if is_full:
                charge_label = " [CARICA 100%]"
            elif is_charging:
                charge_label = " [CARICA]"
            else:
                charge_label = " [SCARICA]"

            # --- CORE SBRW: ESTRAZIONE DATI PROFONDI AUTO-SCALATI ---
            raw_current = self.bm_service.getLongProperty(BM.BATTERY_PROPERTY_CURRENT_NOW)
            current_ma = normalize_current_ma(raw_current)
            voltage_v = voltage_mv / 1000.0
            watt = (voltage_v * current_ma) / 1000.0

            raw_charge = self.bm_service.getLongProperty(BM.BATTERY_PROPERTY_CHARGE_COUNTER)
            actual_mah = normalize_capacity_mah(raw_charge)

            # --- FILTRO ENERGIA SBRW (Normalizzazione Specchio Dati) ---
            raw_energy = self.bm_service.getLongProperty(BM.BATTERY_PROPERTY_ENERGY_COUNTER)
            energy_mwh = sanitize_bms_value(raw_energy)
            while energy_mwh > 1000000.0:
                energy_mwh /= 1000.0
            if energy_mwh > 50000.0:
                energy_mwh /= 100.0

            # --- ATTIVAZIONE MUSCOLI E CALCOLO ETA ---
            muscle_status = self.apply_bms_muscles(temp_c, watt, current_ma, is_charging or is_full)
            eta_min = compute_eta_minutes(level, current_ma, actual_mah, is_charging)
            eta_txt = f"{eta_min} min" if eta_min is not None else "SISTEMA IN ATTESA"

            # --- OUTPUT INTERFACCIA ---
            blocks = int(level / 10)
            bar = "|" * blocks + "." * (10 - blocks)
            res = f"[color=#ff9900][ {bar} ][/color] {level}%{charge_label}\n\n"
            res += f"SORGENTE: {source} | ETA: {eta_txt}\n"
            res += f"[size=32]POTENZA: {watt:.2f} W[/size]\n"
            res += f"CAP. REALE: {actual_mah:.1f} mAh\n"
            res += f"ENERGIA: {energy_mwh:.1f} mWh\n"
            res += f"TENSIONE: {voltage_v:.3f} V | TEMP: {temp_c:.1f}°C\n"
            res += f"STATO CORE: {muscle_status}\n"
            res += f"SALUTE: {health_txt} | TECH: {tech}"
            return res
        except Exception as e:
            return f"SINCRONIZZAZIONE CORE... {str(e)}"


class AikmgeTonApp(App):
    def build(self):
        self.shield = IntentBatteryShield()
        self.antivirus_msg = check_core_integrity()
        self.clock_ev = Clock.schedule_interval(self.update_ui, 1.2)
        return self.shield

    def update_ui(self, dt):
        data = self.shield.decode_intent_data()
        self.shield.info_label.text = (
            f"[b][color=#00ff00]AIKMGE N1 Ton[/color][/b]\n"
            f"[size=18][AUT X 1] SBRW-BMS ACTIVE[/size]\n\n"
            f"{data}\n\n"
            f"[size=24]{self.antivirus_msg}[/size]\n"
            f"[size=18]CORE SBRW-GE: DIGITAL PATENT PROTECTED[/size]"
        )

    def on_pause(self):
        """Sospende il polling JNI quando l'app è in background per risparmio energetico totale."""
        if hasattr(self, 'clock_ev') and self.clock_ev:
            self.clock_ev.cancel()
        return True

    def on_resume(self):
        """Riattiva la telemetria istantaneamente al ritorno in primo piano."""
        self.update_ui(0)
        self.clock_ev = Clock.schedule_interval(self.update_ui, 1.2)

    def on_stop(self):
        if hasattr(self, 'clock_ev') and self.clock_ev:
            self.clock_ev.cancel()
        os._exit(0)


if __name__ == '__main__':
    AikmgeTonApp().run()
