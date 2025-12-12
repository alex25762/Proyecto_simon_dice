# simon_main.py (versión para interfaz antigua sin barra inferior)

import random

# ============================================================================
#  CONFIGURACIÓN DE COLORES Y SONIDOS
# ============================================================================

COLORES = ["green", "red", "yellow", "blue"]

# Mapeo recomendado según tu sonidos.py (sound1.wav – sound4.wav)
SIMON_SOUNDS_MAP = {
    "green": "sound1.wav",
    "red": "sound2.wav",
    "yellow": "sound3.wav",
    "blue": "sound4.wav",
}

# ============================================================================
#  CLASE PRINCIPAL DEL JUEGO
# ============================================================================

class SimonGame:
    def __init__(
        self,
        on_update_score=None,
        on_game_over=None,
        on_sequence_done=None,
        on_delay_request=None,
        on_update_high_score=None,
        flash_duration=0.35
    ):
        # Callbacks conectados desde la interfaz Flet
        self.on_update_score = on_update_score
        self.on_game_over = on_game_over
        self.on_sequence_done = on_sequence_done
        self.on_delay_request = on_delay_request
        self.on_update_high_score = on_update_high_score

        # Configuración interna
        self.flash_duration = flash_duration

        # Estado del juego
        self.sequence = []          # Secuencia generada por el juego
        self.player_index = 0       # Índice de avance del jugador
        self.score = 0              # Puntuación
        self.high_score = 0         # Record Puntuación
        self.game_active = False    # Estado del juego

    # ============================================================================
    #  MÉTODOS PÚBLICOS
    # ============================================================================

    def start_game(self):
        """Inicia un nuevo juego desde cero."""
        self.sequence = []
        self.player_index = 0
        self.score = 0
        self.game_active = True
        
        self._update_score_text()
        self._update_high_score_text()
        
        # Empezar con la primera ronda
        self._delay(lambda: self._add_step_to_sequence(), 0.6)

    def check_player_press(self, color_pressed):
        """
        Verifica si el jugador presionó el color correcto.
        Devuelve True si es correcto.
        """
        if not self.game_active:
            return False

        correcto = (color_pressed == self.sequence[self.player_index])

        if correcto:
            # Avanzamos
            self.player_index += 1

            # ¿Completó la secuencia?
            if self.player_index >= len(self.sequence):
                # Aumentar puntaje
                self.score += 1
                self._update_score_text()

                # Avanzar de ronda
                self.player_index = 0
                self._delay(self._add_step_to_sequence, 0.8)

            return True

        # INCORRECTO → GAME OVER
        self._game_over()
        return False

    # ============================================================================
    #  MÉTODOS INTERNOS
    # ============================================================================

    def _update_score_text(self):
        if self.on_update_score:
            self.on_update_score(f"Puntaje: {self.score}")
    
    def _update_high_score_text(self):
        if self.on_update_high_score:
            self.on_update_high_score(f"Récord: {self.high_score}")

    def _game_over(self):
        self.game_active = False
        if self.score > self.high_score:
            self.high_score = self.score
            self._update_high_score_text() # Notificar a la UI que el récord ha cambiado
        if self.on_game_over:
            self.on_game_over(f"Game Over — Puntaje final: {self.score}")

    

    def _add_step_to_sequence(self):
        """Agrega un nuevo color a la secuencia y pasa su reproducción a la interfaz."""
        if not self.game_active:
            return
        
        nuevo_color = random.choice(COLORES)
        self.sequence.append(nuevo_color)

        # Reproducir la secuencia en la interfaz
        if self.on_sequence_done:
            self.on_sequence_done(self.sequence, self.flash_duration)

    def _delay(self, action, seconds):
        """Solicita a la UI que ejecute algo después del retraso."""
        if self.on_delay_request:
            self.on_delay_request(action, seconds)

