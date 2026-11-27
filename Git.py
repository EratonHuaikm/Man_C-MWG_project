# =====================================================================
# [ SBRW-GE: FINAL OVERRIDE & SOVEREIGN SIGNATURE - LITE ENGINE ]
# =====================================================================

import base64
import io
import time
import traceback

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.image import Image as KivyImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

# [FIX 1] Importazione ottimizzata della gestione Texture in RAM
from kivy.graphics.texture import Texture
from kivy.core.image import Image as CoreImage

# --- DIPENDENZE ANDROID NATIVE (JAVA REFLECTION) ---
try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    BatteryManager = autoclass('android.os.BatteryManager')
    SettingsSystem = autoclass('android.provider.Settings$System')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
except Exception:
    PythonActivity = None

# =====================================================================
# BLOCCO 1: MOTORE CORE LITE (Logica Pura)
# =====================================================================
class SBRW_Lite_Core:
    def __init__(self):
        self.activity = PythonActivity.mActivity if PythonActivity else None
        self.battery_level = 100
        self.temperature = 0.0
        self.voltage = 0.0
        self.is_charging = False
        self.thermal_throttle_active = False
        self.original_brightness = -1
        self.original_timeout = -1
        
        if self.activity:
            self.battery_filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        self.permissions_granted = False

    def verify_and_request_permissions(self):
        if not self.activity: return False
        try:
            if not Settings.System.canWrite(self.activity):
                print("[AI-KM] Permesso WRITE_SETTINGS mancante. Richiesta in corso...")
                intent = Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS)
                intent.setData(Uri.parse("package:" + self.activity.getPackageName()))
                intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                self.activity.startActivity(intent)
                self.permissions_granted = False
                return False
            self.permissions_granted = True
            return True
        except Exception as e:
            print(f"[WARN] Impossibile verificare permessi (Versione Legacy): {e}")
            self.permissions_granted = True
            return True

    def fetch_sensors(self):
        if not self.activity: return
        try:
            battery_status = self.activity.registerReceiver(None, self.battery_filter)
            if battery_status:
                self.parse_telemetry(battery_status)
        except Exception as e:
            print(f"[ERR] Fallimento lettura sensori: {e}")

    def parse_telemetry(self, intent):
        try:
            level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            self.battery_level = int((level / float(scale)) * 100)
            self.temperature = intent.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) / 10.0
            self.voltage = intent.getIntExtra(BatteryManager.EXTRA_VOLTAGE, -1) / 1000.0
            status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
            self.is_charging = status in (BatteryManager.BATTERY_STATUS_CHARGING, BatteryManager.BATTERY_STATUS_FULL)
            
            self.analyze_and_react()
        except Exception as e:
            print(f"[ERR] Errore parsing telemetria: {e}")

    def analyze_and_react(self):
        if not self.permissions_granted or not self.activity: return
        content_resolver = self.activity.getContentResolver()
        
        if (self.temperature > 37.0 or self.battery_level < 20) and not self.is_charging:
            if not self.thermal_throttle_active:
                try:
                    self.original_brightness = SettingsSystem.getInt(content_resolver, SettingsSystem.SCREEN_BRIGHTNESS)
                    self.original_timeout = SettingsSystem.getInt(content_resolver, SettingsSystem.SCREEN_OFF_TIMEOUT)
                    SettingsSystem.putInt(content_resolver, SettingsSystem.SCREEN_BRIGHTNESS, 50) 
                    SettingsSystem.putInt(content_resolver, SettingsSystem.SCREEN_OFF_TIMEOUT, 15000)
                    self.thermal_throttle_active = True
                except: pass
        elif self.temperature <= 35.0 and self.battery_level > 20 and self.thermal_throttle_active:
            if self.original_brightness != -1:
                try:
                    SettingsSystem.putInt(content_resolver, SettingsSystem.SCREEN_BRIGHTNESS, self.original_brightness)
                    SettingsSystem.putInt(content_resolver, SettingsSystem.SCREEN_OFF_TIMEOUT, self.original_timeout)
                    self.thermal_throttle_active = False
                except: pass

# =====================================================================
# BLOCCO 2: UI (Schermata Intro) IN-MEMORY
# =====================================================================
def crea_texture_sovrana_ram():
    """
    [FIX 1] Costruisce una texture OpenGL 1x6 pixel. 
    La GPU di Android espanderà questi 6 pixel a tutto schermo
    calcolando istantaneamente il gradiente sfumato a costo CPU zero.
    """
    # Struttura Byte: (Rosso, Verde, Blu, Alpha) - Dal basso verso l'alto
    buf = bytes([
        0, 0, 255, 51,      # Fondo: Blu abissale
        0, 146, 70, 82,     # Verde SBRW
        255, 0, 0, 113,     # Rosso termico
        255, 165, 0, 144,   # Arancione
        255, 255, 0, 175,   # Giallo radiante
        255, 255, 255, 205  # Cima: Luce bianca pura
    ])
    
    tex = Texture.create(size=(1, 6), colorfmt='rgba')
    tex.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
    return tex

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # 1. Sfondo Bandiera da GPU (Nessun file, nessuna CPU)
        tex_sfondo = crea_texture_sovrana_ram()
        self.sfondo = KivyImage(
            texture=tex_sfondo, 
            allow_stretch=True, 
            keep_ratio=False, 
            opacity=0, 
            pos_hint={'y': 1}
        )
        layout.add_widget(self.sfondo)
        
        # 2. Testo Sovrano
        msg = ("[SISTEMA AI-KM: ATTIVO]\n\nAIKM.\nHuCore.\n\nSBRW-GE\nSEI_Core Zero-Trust: INVIOLATA\nDigital Patent:\n\nMake-World-Green.\nVersione Beta Depontenziata.")
        self.testo = Label(text=msg, color=(0, 1, 0, 1), font_size='17sp', bold=True, halign='center', valign='middle', opacity=0)
        layout.add_widget(self.testo)
        
        # 3. Sigillo sicuro in RAM [FIX 2] (Anti-Crash, Zero Permessi Disco)
        tex_sigillo = None
        try:
            from sigillo_data import sigillo_base64
            # Decodifica base64 in un buffer di memoria RAM
            data_io = io.BytesIO(base64.b64decode(sigillo_base64))
            core_img = CoreImage(data_io, ext='png')
            tex_sigillo = core_img.texture
        except Exception:
            # Fallback texture trasparente 1x1 se il modulo manca
            tex_sigillo = Texture.create(size=(1, 1), colorfmt='rgba')
            tex_sigillo.blit_buffer(b'\x00\x00\x00\x00', colorfmt='rgba', bufferfmt='ubyte')
            
        self.sigillo = KivyImage(
            texture=tex_sigillo, 
            opacity=0, 
            size_hint=(0.95, 0.95), 
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        layout.add_widget(self.sigillo)
        
        self.add_widget(layout)
        
    def on_enter(self, *args):
        # Animazioni fluide
        anim_sfondo = Animation(pos_hint={'y': 0}, opacity=1, duration=3) + Animation(opacity=0, duration=2)
        anim_sfondo.start(self.sfondo)
        
        anim_testo = Animation(opacity=1, duration=3) + Animation(opacity=0, duration=2)
        anim_testo.start(self.testo)
        
        anim_sigillo = Animation(opacity=0, duration=4) + Animation(opacity=1, duration=0.5) + Animation(opacity=1, duration=2) + Animation(opacity=0, duration=1.5)
        anim_sigillo.start(self.sigillo)
        
        Clock.schedule_once(self.pass_to_main, 9)

    def pass_to_main(self, dt):
        self.manager.current = 'main'

# =====================================================================
# BLOCCO 3: UI (Schermata Main Telemetria)
# =====================================================================
class LiteMatrixUI(Screen):
    def __init__(self, core_engine, **kwargs):
        super().__init__(**kwargs)
        self.core = core_engine
        
        layout = BoxLayout(orientation='vertical')
        self.lbl_status = Label(
            text="[color=#00ff00]SBRW-LITE: ONLINE (GOOGLE SANDBOX)[/color]", 
            markup=True, font_size='14sp', size_hint=(1, 0.2)
        )
        self.lbl_telemetry = Label(
            text="Inizializzazione sensori e verifica policy...", 
            markup=True, halign='center', font_size='12sp'
        )
        layout.add_widget(self.lbl_status)
        layout.add_widget(self.lbl_telemetry)
        
        self.add_widget(layout)
        self.refresh_event = None

    def on_enter(self, *args):
        self.core.verify_and_request_permissions()
        self.refresh_event = Clock.schedule_interval(self.refresh_ui, 1.0)

    def on_leave(self, *args):
        if self.refresh_event:
            self.refresh_event.cancel()

    def refresh_ui(self, dt):
        self.core.fetch_sensors()
        
        status_charge = "~ IN CARICA" if self.core.is_charging else " × SCARICA"
        perm_txt = "[color=#33ff33]OK[/color]" if self.core.permissions_granted else "[color=#ff3333]NEGATI[/color]"
        throttle_txt = "[color=#ff3333]ATTIVO (LIMITAZIONE HW)[/color]" if self.core.thermal_throttle_active else "[color=#33ff33]RIPOSO[/color]"
        
        self.lbl_telemetry.text = (
            f"[b]STATO VITALI:[/b] {status_charge}\n"
            f"[b]LIVELLO:[/b] {self.core.battery_level}%\n"
            f"[b]TEMPERATURA:[/b] {self.core.temperature}°C\n"
            f"[b]TENSIONE:[/b] {self.core.voltage} V\n"
            f"[color=#888888]-------------------------------------[/color]\n"
            f"[b]PERMESSI SISTEMA:[/b] {perm_txt}\n"
            f"[b]INTERVENTO GREEN:[/b] {throttle_txt}\n"
        )

# =====================================================================
# BLOCCO 4: MOTORE KIVY PRINCIPALE (State Machine)
# =====================================================================
class SBRW_Unified_App(App):
    def build(self):
        Window.clearcolor = (0.02, 0.05, 0.02, 1)
        self.core = SBRW_Lite_Core()
        
        sm = ScreenManager(transition=FadeTransition(duration=1.5))
        
        intro = IntroScreen(name='intro')
        main = LiteMatrixUI(core_engine=self.core, name='main')
        
        sm.add_widget(intro)
        sm.add_widget(main)
        
        return sm

if __name__ == '__main__':
    try:
        SBRW_Unified_App().run()
    except Exception as e:
        print(f"Errore fatale: {traceback.format_exc()}")
