# Importaciones necesarias de Kivy y Python
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout 
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty # Importar para Game Over Fade
import random
import os

# Definimos las constantes para el juego
COLORES = ['blue', 'red', 'yellow', 'green']

# NOTA: Estos archivos .wav deben existir en la carpeta.
# Cargamos los sonidos una sola vez al inicio
SONIDOS = {
    'blue': SoundLoader.load('sound1.wav'),
    'red': SoundLoader.load('sound2.wav'),
    'yellow': SoundLoader.load('sound3.wav'),
    'green': SoundLoader.load('sound4.wav'),
}

# Colores brillantes para el efecto "flash"
COLORES_FLASH = {
    'blue': (0.3, 0.7, 1.0, 1),
    'red': (1.0, 0.5, 0.5, 1),
    'yellow': (1.0, 1.0, 0.5, 1),
    'green': (0.5, 1.0, 0.5, 1),
}

# La clase principal de la pantalla, hereda de BoxLayout
class SimonScreen(BoxLayout, Screen):
    score_label = None
    game_sequence = []
    player_sequence = []
    game_running = False
    
    # Mapeo de nombres a los objetos Button (para el flash)
    button_map = {}
    
    # Propiedad para controlar la opacidad del Game Over (usado en simon.kv)
    game_over_opacity = NumericProperty(0) 
    
    # Variables para controlar la velocidad y dificultad
    flash_duration = 0.4   # Duración inicial ajustada (un poco más rápido que 0.5)
    delay_sequence = 0.25  # Pausa de seguridad entre flashes
    min_flash_duration = 0.1 # Velocidad mínima que puede alcanzar

    def __init__(self, **kwargs):
        super().__init__(**kwargs) 

    def on_kv_post(self, base_widget):
        """Esta función se llama después de que Kivy ha aplicado el .kv."""
        self.score_label = self.ids.score_label
        
        self.button_map = {
            'blue': self.ids.btn_blue,
            'red': self.ids.btn_red,
            'yellow': self.ids.btn_yellow,
            'green': self.ids.btn_green,
        }
        
        # Inicio automático del juego
        Clock.schedule_once(self.start_game_auto, 0)


    def start_game_auto(self, dt):
        """Función auxiliar para el inicio automático."""
        self.start_game(None)
        
    def start_game(self, instance):
        if self.game_running and instance: # Evita reiniciar si ya está corriendo, a menos que sea un reinicio manual
            return
        
        print("Juego iniciado/reiniciado.")
        
        # 1. Ocultar la capa de Game Over
        self.game_over_opacity = 0
        self.ids.game_over_overlay.disabled = True
        
        # 2. Reiniciar variables del juego
        self.game_running = True
        self.game_sequence = []
        self.player_sequence = []
        self.score_label.text = "Puntaje: 0"
        
        # 3. Restaurar la dificultad inicial
        self.flash_duration = 0.4 
        
        # 4. Iniciar la primera ronda
        self.play_next_round(0) 

    def play_next_round(self, dt): 
        self.player_sequence = []
        
        # 🚀 Lógica de Dificultad Progresiva (Se acelera cada 3 rondas)
        current_level = len(self.game_sequence)
        if current_level > 1 and current_level % 3 == 0:
            # Disminuimos la duración del flash, pero no menos de la velocidad mínima
            self.flash_duration = max(self.min_flash_duration, self.flash_duration - 0.05)
            print(f"¡Dificultad aumentada! Nueva duración del flash: {self.flash_duration:.2f}s")

        # Añade un nuevo color aleatorio a la secuencia
        new_color = random.choice(COLORES)
        self.game_sequence.append(new_color)
        print(f"Nueva secuencia: {self.game_sequence}")
        
        # Inicia la secuencia de flashes después de un segundo de pausa
        Clock.schedule_once(self.flash_sequence, 1.0) 

    def flash_sequence(self, dt):
        # Función recursiva para mostrar la secuencia con un retardo
        def flash(color_index):
            if color_index < len(self.game_sequence):
                color = self.game_sequence[color_index]
                self.flash_button(color)
                
                # Programar el siguiente flash usando la duración y el delay actualizados
                delay = self.flash_duration + self.delay_sequence
                Clock.schedule_once(lambda dt: flash(color_index + 1), delay) 
            else:
                print("Tu turno.")
                
        flash(0)

    def flash_button(self, color_name):
        button = self.button_map[color_name]
        
        # Guardar el color original antes de cambiarlo
        original_color = button.background_color
        
        # Cambia el color a flash
        button.background_color = COLORES_FLASH[color_name]
        
        # Reproduce el sonido de forma segura
        try:
            sound = SONIDOS[color_name]
            if sound:
                sound.stop()
                sound.play() 
            else:
                print(f"ADVERTENCIA: Sonido para '{color_name}' no cargado.")
        except Exception as e:
            print(f"ERROR al intentar reproducir sonido para '{color_name}': {e}")
        
        # Programa la vuelta al color original usando self.flash_duration
        Clock.schedule_once(lambda dt: self.reset_button_color(button, original_color, color_name), self.flash_duration)

    def reset_button_color(self, button, original_color, color_name):
        button.background_color = original_color

    def on_button_press(self, color_name):
        if not self.game_running:
            return
            
        print(f"Presionado: {color_name}")
        self.player_sequence.append(color_name)
        
        # Comprobar si la jugada es correcta
        index = len(self.player_sequence) - 1
        
        if self.player_sequence[index] == self.game_sequence[index]:
            # Flash y sonido al presionar (retroalimentación instantánea)
            self.flash_button(color_name) 
            
            if len(self.player_sequence) == len(self.game_sequence):
                # Ronda completa y correcta
                self.score_label.text = f"Puntaje: {len(self.game_sequence)}"
                print("¡Ronda superada!")
                # Inicia la siguiente ronda después de una pausa
                Clock.schedule_once(self.play_next_round, 1.5)
        else:
            # Incorrecto
            self.game_over()

    def game_over(self):
        print("¡Juego Terminado! Secuencia incorrecta.")
        self.game_running = False
        
        # 1. Actualizar el marcador
        self.score_label.text = f"¡FALLASTE! Puntaje: {len(self.game_sequence) - 1}"
        
        # 2. Mostrar la capa de Game Over (haciéndola visible y habilitando el botón)
        self.game_over_opacity = 0.8
        self.ids.game_over_overlay.disabled = False


class SimonApp(App):
    def build(self):
        self.title = "Simón Dice"
        return SimonScreen()

if __name__ == '__main__':
    # Verificar que los archivos de sonido existen y son válidos
    missing_sounds = [f'sound{i+1}.wav' for i, c in enumerate(COLORES) if SONIDOS[c] is None]
    
    if missing_sounds:
        print("-----------------------------------------------------------------------")
        print("ADVERTENCIA: ¡Faltan o no se pudieron cargar archivos de sonido!")
        print("Asegúrate de que estos archivos .wav estén en la misma carpeta:")
        for sound in missing_sounds:
            print(f"- {sound}")
        print("El juego continuará, pero sin sonido para estos colores.")
        print("-----------------------------------------------------------------------")
    
    SimonApp().run()
