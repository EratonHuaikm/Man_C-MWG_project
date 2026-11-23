#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py - HUD Kivy AIKMGE N1 Ton v3 | Pure-Sandbox Thermal-VPN + Sensor Hub + USB-OTG.
Sospende il clock OpenGL in on_pause() per azzerare il consumo grafico in background.
"""

import json
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label

from bms_core import ANDROID_ENV, BMSDigitalTwinEngine, check_core_integrity

ANDROID_SERVICE_CLASS = "org.sbrwge.aikmgeton.ServiceBmsmonitor"
ECO_JAVA_CLASS = "org.sbrwge.aikmgeton.SandboxEcoController"
POST_NOTIFICATIONS_PERM = "android.permission.POST_NOTIFICATIONS"


class IntentBatteryShield(BoxLayout):
    def __init__(self, callbacks: dict, **kwargs):
        super().__init__(orientation="vertical", spacing=6, padding=10, **kwargs)
        Window.clearcolor = (0, 0, 0, 1)

        self.info_label = Label(
            text="[b]AIKMGE N1 TON v3 // PURE SANDBOX[/b]\n[size=14]SINCRONIZZAZIONE...[/size]",
            markup=True,
            halign="center",
            valign="middle",
            color=(0, 1, 0.4, 1),
            font_size="12sp",
        )
        self.info_label.bind(size=self.info_label.setter("text_size"))
        self.add_widget(self.info_label)

        # Griglia 2x2 per i 4 moduli Sandbox avanzati (attivabili in 1 tap)
        grid = GridLayout(cols=2, spacing=6, size_hint_y=None, height="88dp")
        self.btn_vpn = self._make_btn("ATTIVA ECO-VPN", callbacks["vpn"])
        self.btn_lcd = self._make_btn("ATTIVA SCUDO LCD", callbacks["lcd"])
        self.btn_bio = self._make_btn("BLOCCO BIOMETRICO", callbacks["bio"])
        self.btn_usb = self._make_btn("PONTE USB-OTG", callbacks["usb"])
        for b in (self.btn_vpn, self.btn_lcd, self.btn_bio, self.btn_usb):
            grid.add_widget(b)
        self.add_widget(grid)

        self.btn_service = Button(
            text="FOREGROUND BAR: AVVIO...",
            size_hint_y=None,
            height="44dp",
            background_normal="",
            background_color=(0.0, 0.45, 0.25, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size="12sp",
        )
        self.btn_service.bind(on_release=lambda _b: callbacks["toggle_service"]())
        self.add_widget(self.btn_service)

        android_ctx = None
        self.status_file = Path(".sbrw_state/eco_status.json")
        if ANDROID_ENV:
            try:
                from jnius import autoclass
                android_ctx = autoclass("org.kivy.android.PythonActivity").mActivity
                self.status_file = Path(android_ctx.getFilesDir().getAbsolutePath()) / "eco_status.json"
            except Exception:
                android_ctx = None

        self.engine = BMSDigitalTwinEngine(android_ctx)

    @staticmethod
    def _make_btn(label: str, cb) -> Button:
        btn = Button(
            text=label,
            background_normal="",
            background_color=(0.15, 0.25, 0.45, 1),
            color=(1, 1, 1, 1),
            bold=True,
            font_size="11sp",
        )
        btn.bind(on_release=lambda _b: cb())
        return btn

    def _read_eco_status(self) -> dict:
        try:
            if self.status_file.is_file():
                return json.loads(self.status_file.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def render_snapshot(self) -> str:
        try:
            snap = self.engine.step()
            st = self._read_eco_status()

            vpn_ok = bool(st.get("vpn_consented", False))
            lcd_ok = bool(st.get("write_ok", False))
            bio_ok = bool(st.get("acc_ok", False))
            usb_st = str(st.get("usb_status", "OTG_ASSENTE"))

            self.btn_vpn.text = f"ECO-VPN: {'ON' if st.get('vpn_active') else 'PRONTO'}" if vpn_ok else "ATTIVA ECO-VPN"
            self.btn_vpn.background_color = (0.0, 0.45, 0.25, 1) if vpn_ok else (0.65, 0.35, 0.0, 1)

            self.btn_lcd.text = "SCUDO LCD: ATTIVO" if lcd_ok else "ATTIVA SCUDO LCD"
            self.btn_lcd.background_color = (0.0, 0.45, 0.25, 1) if lcd_ok else (0.65, 0.35, 0.0, 1)

            self.btn_bio.text = f"BIO-LOCK: ON ({st.get('bio_locks', 0)})" if bio_ok else "ATTIVA BIO-LOCK"
            self.btn_bio.background_color = (0.0, 0.45, 0.25, 1) if bio_ok else (0.20, 0.30, 0.45, 1)

            usb_ready = usb_st.startswith("OTG_TX_OK") or usb_st.startswith("OTG_PRONTO")
            self.btn_usb.text = usb_st[:18]
            self.btn_usb.background_color = (0.0, 0.45, 0.45, 1) if usb_ready else (0.20, 0.30, 0.45, 1)

            hr_txt = f"{snap.thermal_headroom * 100:.0f}%" if snap.thermal_headroom >= 0.0 else "N/D"
            hub_txt = f"DSP-HUB ({st.get('still_sec', 0)}s)" if st.get("sensor_hub") else "STANDARD"
            charge_label = " [CARICA]" if snap.is_charging else " [SCARICA]"
            filled = max(0, min(10, int(snap.level / 10)))
            bar = "|" * filled + "." * (10 - filled)

            res = "[color=#00ffff][b]PURE SANDBOX v3 | ZERO INTERNET | ZERO ROOT[/b][/color]\n"
            res += f"HUB: {hub_txt} | VPN DROP: {st.get('vpn_dropped', 0)} | WIFI: {st.get('wifi_state', '...')}\n"
            res += f"[size=11sp][color=#94a3b8]{st.get('last_action', 'Inizializzazione...')}[/color][/size]\n\n"
            res += f"[color=#ff9900][ {bar} ][/color] {snap.level}%{charge_label}\n"
            res += f"SORGENTE: {snap.source} | ETA: {snap.eta_txt}\n"
            res += f"[size=20sp][b]POTENZA: {snap.watt:.2f} W[/b][/size]\n"
            res += f"V: {snap.voltage_v:.3f}V | TEMP: {snap.temp_c:.1f}°C | THERMAL-HR: {hr_txt}\n"
            res += f"IRR: {snap.est_irr_ohm * 1000:.1f}mΩ | I_Filt: [color=#00ffff]{snap.filtered_ma:.1f}mA[/color]\n"
            res += f"STATO CORE: {snap.muscle_markup}\n\n"
            res += "[color=#ffff00]--- APWM DIGITAL TWIN / USB-OTG ---[/color]\n"
            res += f"TX: {snap.hex_packet}\nRX: {snap.mcu_response}"
            return res
        except Exception as exc:
            return f"SINCRONIZZAZIONE CORE... {exc}"


class AikmgeTonApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service_running = False
        self.shield = None
        self.antivirus_msg = ""
        self._ui_event = None

    def build(self):
        callbacks = {
            "vpn": lambda: self._invoke_java_setup("openVpnSetup"),
            "lcd": lambda: self._invoke_java_setup("openWriteSettingsSetup"),
            "bio": lambda: self._invoke_java_setup("openAccessibilitySetup"),
            "usb": lambda: self._invoke_java_setup("requestUsbOtgPermission"),
            "toggle_service": self.toggle_foreground_service,
        }
        self.shield = IntentBatteryShield(callbacks=callbacks)
        self.antivirus_msg = check_core_integrity()
        Clock.schedule_once(lambda _dt: self._init_android_foreground(), 0.4)
        self._start_ui_clock()
        return self.shield

    def _invoke_java_setup(self, method_name: str) -> None:
        if not ANDROID_ENV:
            return
        try:
            from jnius import autoclass
            act = autoclass("org.kivy.android.PythonActivity").mActivity
            cls = autoclass(ECO_JAVA_CLASS)
            getattr(cls, method_name)(act)
        except Exception:
            pass

    def _start_ui_clock(self) -> None:
        if self._ui_event is None:
            self._ui_event = Clock.schedule_interval(self.update_ui, 1.5)

    def _stop_ui_clock(self) -> None:
        if self._ui_event is not None:
            self._ui_event.cancel()
            self._ui_event = None

    def _init_android_foreground(self) -> None:
        if not ANDROID_ENV:
            self.service_running = True
            self._refresh_service_button()
            return
        try:
            from jnius import autoclass
            from android.permissions import check_permission, request_permissions

            BuildVersion = autoclass("android.os.Build$VERSION")
            if BuildVersion.SDK_INT >= 33 and not check_permission(POST_NOTIFICATIONS_PERM):
                request_permissions(
                    [POST_NOTIFICATIONS_PERM],
                    lambda _p, _g: Clock.schedule_once(lambda _dt: self.start_foreground_service(), 0.2),
                )
            else:
                self.start_foreground_service()
        except Exception:
            self.start_foreground_service()

    def start_foreground_service(self) -> None:
        if ANDROID_ENV:
            try:
                from jnius import autoclass
                service_cls = autoclass(ANDROID_SERVICE_CLASS)
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                service_cls.start(activity, "")
                self.service_running = True
            except Exception as exc:
                self.service_running = False
                self.shield.btn_service.text = f"ERRORE FOREGROUND: {exc}"
                return
        else:
            self.service_running = True
        self._refresh_service_button()

    def stop_foreground_service(self) -> None:
        if ANDROID_ENV:
            try:
                from jnius import autoclass
                service_cls = autoclass(ANDROID_SERVICE_CLASS)
                activity = autoclass("org.kivy.android.PythonActivity").mActivity
                service_cls.stop(activity)
            except Exception:
                pass
        self.service_running = False
        self._refresh_service_button()

    def toggle_foreground_service(self) -> None:
        if self.service_running:
            self.stop_foreground_service()
        else:
            self.start_foreground_service()

    def _refresh_service_button(self) -> None:
        if self.service_running:
            self.shield.btn_service.text = "FOREGROUND BAR: ATTIVO (TOCCA PER ARRESTARE)"
            self.shield.btn_service.background_color = (0.0, 0.45, 0.25, 1)
        else:
            self.shield.btn_service.text = "FOREGROUND BAR: SPENTO (TOCCA PER AVVIARE)"
            self.shield.btn_service.background_color = (0.55, 0.12, 0.16, 1)

    def update_ui(self, _dt) -> None:
        data = self.shield.render_snapshot()
        self.shield.info_label.text = (
            f"[b][color=#00ff00]AIKMGE N1 Ton | SBRW-BMS SYMBIOTE[/color][/b]\n"
            f"{data}\n\n"
            f"[size=11sp]{self.antivirus_msg}[/size]"
        )

    def on_pause(self) -> bool:
        self._stop_ui_clock()
        return True

    def on_resume(self) -> None:
        self._start_ui_clock()
        self.update_ui(0)


if __name__ == "__main__":
    AikmgeTonApp().run()
--------------------------------