import random
import json
import os
import time

# --- Constantes ---
COLORES = ['red', 'green', 'blue', 'yellow']
# Nombre del archivo para guardar el récord
# Aseguramos que el directorio 'storage' exista en la ruta local.
HIGHSCORE_FILE = "storage/simon_highscore.json"

class SimonGame:
    """
    Clase que encapsula la lógica central del juego Simón Dice.
    Maneja la secuencia, el estado del juego, el puntaje y el récord.
    """
    # NOTA: on_delay_request fue eliminado, se centraliza la lógica de retardo en la UI.
    def __init__(self, on_update_score, on_game_over, on_sequence_done):
        # Callbacks a la interfaz de usuario (UI) para comunicación asíncrona
        self.on_update_score = on_update_score    # (score_text, high_score_text)
        self.on_game_over = on_game_over          # (final_score_text)
        self.on_sequence_done = on_sequence_done  # (sequence, flash_duration)
        
        # Estado del juego
        self.sequence = []          # Secuencia generada por Simon
        self.player_clicks = 0      # Clics del jugador en la ronda actual
        self.is_player_turn = False # Bandera de control de entrada del jugador
        self.score = 0
        self.high_score = self.load_high_score()
        self.flash_duration = 0.5   # Duración inicial del flash (segundos)

    def load_high_score(self):
        """Carga el récord guardado, o devuelve 0 si no existe."""
        # Se asegura de crear el directorio 'storage' si no existe
        os.makedirs(os.path.dirname(HIGHSCORE_FILE) or '.', exist_ok=True)
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
            except (IOError, json.JSONDecodeError):
                # En caso de error de lectura o JSON inválido, retorna 0
                return 0
        return 0

    def save_high_score(self):
        """Guarda el récord si el puntaje actual es mayor."""
        if self.score > self.high_score:
            self.high_score = self.score
            os.makedirs(os.path.dirname(HIGHSCORE_FILE) or '.', exist_ok=True)
            try:
                with open(HIGHSCORE_FILE, 'w') as f:
                    json.dump({'high_score': self.high_score}, f)
            except IOError:
                # Se imprime un error pero se permite que el juego continúe
                print(f"Error al guardar el récord en {HIGHSCORE_FILE}")

    def update_ui_score(self):
        """Llama al callback para actualizar el puntaje en la UI."""
        score_text = f"Puntaje: {self.score}"
        high_score_text = str(self.high_score)
        self.on_update_score(score_text, high_score_text)

    def set_player_turn(self, state: bool):
        """Establece si es el turno del jugador."""
        self.is_player_turn = state

    def start_game(self):
        """Inicia o reinicia el juego. Se llama al inicio y después de Game Over."""
        self.score = 0
        self.player_clicks = 0
        self.sequence = []
        self.is_player_turn = False
        self.flash_duration = 0.5
        self.update_ui_score()
        
        # CORRECCIÓN: Se elimina la llamada inmediata a next_round().
        # La UI (interfaz.py) ahora llamará a next_round() de forma asíncrona
        # después del retardo inicial.

    def next_round(self):
        """Prepara la siguiente ronda: agrega un color y muestra la secuencia."""
        self.is_player_turn = False
        
        # 1. Agregar un nuevo color a la secuencia
        new_color = random.choice(COLORES)
        self.sequence.append(new_color)
        
        # 2. Reiniciar el contador de clics del jugador
        self.player_clicks = 0
        
        # 3. Ajustar la dificultad (disminuir el tiempo de flash)
        if len(self.sequence) > 4:
            self.flash_duration = 0.4
        if len(self.sequence) > 8:
            self.flash_duration = 0.3
            
        # 4. Mostrar la secuencia en la UI.
        # La UI (interfaz.py) será responsable de agregar un retardo antes de esto si es necesario.
        self.on_sequence_done(self.sequence, self.flash_duration)

    def next_round_request(self):
        """
        Función para ser llamada por la UI después de un retardo (delayed_task) 
        para iniciar la siguiente ronda. 
        Esto evita anidar llamadas a run_task desde la lógica.
        """
        self.next_round()

    def check_player_press(self, pressed_color: str):
        """Verifica si el color presionado por el jugador es correcto."""
        if not self.is_player_turn:
            return

        # 1. Obtener el color esperado en la posición actual
        expected_color = self.sequence[self.player_clicks]
        
        if pressed_color == expected_color:
            self.player_clicks += 1
            
            # 2. Si el jugador completó la secuencia de la ronda
            if self.player_clicks == len(self.sequence):
                self.score += 1
                self.update_ui_score()
                self.is_player_turn = False
                
                # Devolvemos el control a la UI. La UI debe solicitar el retardo y la siguiente ronda.
                return True # Indica que la ronda fue completada exitosamente
            
            return True # Indica que el clic fue correcto, pero la ronda no ha terminado
        else:
            # 3. El jugador falló
            self.save_high_score()
            final_score_text = f"¡FALLASTE! Puntaje: {self.score}"
            self.on_game_over(final_score_text)
            return False # Indica que el clic fue incorrecto
