# =====================================================================
# PROJECT: SBRW-GE Public Interface Bait (Choose Clean Adaptive Card)
# LICENSE: GNU General Public License v3.0 (GPLv3)
# WATERMARK SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
# =====================================================================
# As the creator's spokesperson, I leave this communication: 
# The security of our project and the Core, and its extraordinary 
# multiple functionalities in every aspect, regarding Green Energy, 
# is a mission to protect the planet. No one can use it without 
# consent and sustainability parameters.
# =====================================================================

from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.graphics import Color, RoundedRectangle, Line

# Configurazione globale dello spazio visivo (Sfondo scuro Choose)
Window.clearcolor = get_color_from_hex("#05080D")

# =====================================================================
# MODULO INTERNO 1: CARD CENTRALE ADATTIVA E PULITA
# =====================================================================
class AdaptiveCard(BoxLayout):
    def __init__(self, bg_color="#0A0F1A", border_color="#38BDF8", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 25
        self.spacing = 18
        
        # Dimensioni flessibili ma bloccate in percentuale sullo schermo per evitare scompensi
        self.size_hint = (0.99, None)
        self.height = 2150

        # Canvas pulito e nativo per la card con angoli arrotondati e bordo neon
        with self.canvas.before:
            Color(*get_color_from_hex(bg_color))
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[24])
            Color(*get_color_from_hex(border_color))
            self.border_line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 44), width=6.5)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_line.rounded_rectangle = (self.x, self.y, self.width, self.height,8)


class UIComponentsModule(AnchorLayout):
    def __init__(self, **kwargs):
        super(UIComponentsModule, self).__init__(**kwargs)
        self.anchor_x = 'center'
        self.anchor_y = 'center'

        neon_green = get_color_from_hex("#00FF66")
        neon_blue = get_color_from_hex("#38BDF8")
        text_gray = (0.7, 0.7, 0.7, 1)

        # Istanza della Card Centrale Adattiva
        self.card = AdaptiveCard()

        # --- PIANO 1: Stringa animata superiore (Typewriter) ---
        self.target_text = "[b]_ AI-KM SeiCore/Hucore_[/b]"
        self.current_index = 0

        self.title_label = Label(
            text='',
            markup=True,
            font_size='20sp',
            color=neon_green,
            size_hint=(1, 0.25),
            halign='center',
            valign='middle'
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        self.card.add_widget(self.title_label)

        # --- PIANO 2: Stringa secondaria animata inferiore (Benvenuto) ---
        self.welcome_label = Label(
            text='_[i] Welcome > SBRW-GE Make World Green[/i]',
            markup=True,
            font_size='14sp',
            color=text_gray,
            size_hint=(1, 0.2),
            halign='center',
            valign='middle'
        )
        self.welcome_label.bind(size=self.welcome_label.setter('text_size'))
        self.card.add_widget(self.welcome_label)

        # Etichetta di stato del perimetro
        self.status_label = Label(
            text='New World - New Energy / Status: Perimetro Sicuro [OK]',
            font_size='15sp',
            color=neon_green,
            size_hint=(1, 0.35),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        self.card.add_widget(self.status_label)

        # Pulsante d'interazione in stile Choose incapsulato pulito
        self.action_button = Button(
            text='Esegui VERIFICA Base',
            font_size='16sp',
            background_normal='',
            background_color=(0, 1, 0.4, 1),
            color=(0.05, 0.08, 0.12, 1),
            bold=True,
            size_hint=(1, 0.3)
        )
        self.card.add_widget(self.action_button)

        # Aggiunta della card centrata nel layout principale
        self.add_widget(self.card)

        # Avvio dell'effetto di scrittura a schermo per il piano superiore
        Clock.schedule_interval(self.typewriter_effect, 0.08)

    def typewriter_effect(self, dt):
        if self.current_index < len(self.target_text):
            self.current_index += 1
            self.title_label.text = self.target_text[:self.current_index]
        else:
            return False


# =====================================================================
# MODULO INTERNO 2: CONTROLLER & APPLICATION LAUNCHER
# =====================================================================
class SBRWApp(App):
    def build(self):
        self.title = 'AI-KM Bait Engine'
        
        # Inizializzazione del modulo UI interno
        self.root_layout = UIComponentsModule()
        
        # Binding del controller sugli eventi del modulo UI
        self.root_layout.action_button.bind(on_press=self.handle_action_trigger)
        
        return self.root_layout

    def handle_action_trigger(self, instance):
        # Logica di controllo isolata nel modulo principale
        self.root_layout.status_label.text = 'Status: SBRW-GE BASE CORE ATTIVA.'


if __name__ == '__main__':
    SBRWApp().run()
