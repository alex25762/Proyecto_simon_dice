
# interfaz.py (Con Overlay Manual para Game Over y ft.Colors con C mayúscula)

import flet as ft
from flet import ControlState
import threading
import time
# Importamos la lógica y las constantes (asumimos que simon_main.py usa COLORES en mayúscula)
from main import SimonGame, SIMON_SOUNDS_MAP, COLORES 

# Constantes de Flet para el diseño visual
FLET_COLORS = {
    'blue': ft.Colors.BLUE_700,
    'red': ft.Colors.RED_700,
    'yellow': ft.Colors.YELLOW_ACCENT_700,
    'green': ft.Colors.GREEN_700,
}
FLASH_COLOR = ft.Colors.WHITE

class SimonFletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Simón Dice con Flet"
        # Ajustamos la alineación de la página para centrar todo
        self.page.vertical_alignment = ft.MainAxisAlignment.SPACE_AROUND # Distribuye el espacio

        # Color de fondo de la página, cerca del azul/violeta oscuro del boceto
        self.page.bgcolor = ft.Colors.BLUE_GREY_900 # <-- CORREGIDO

        # Diccionarios de elementos UI y Audio
        self.buttons = {}
        self.audio_players = {}
        
        # 1. Inicializar la lógica del juego con los callbacks de la UI
        self.game = SimonGame(
            on_update_score=self.update_score_ui,
            on_game_over=self.handle_game_over_ui,
            on_sequence_done=self.run_flash_sequence,
            on_delay_request=self.execute_delayed_action,
            on_update_high_score=self.update_high_score_ui,
        )
        
        # 2. Configurar la UI
        # Esta llamada crea self.master_container
        self._setup_ui()
        
        # 3. Cargar audios
        self._load_audio()
        
        # ----------------------------------------------------
        #  REVERTIMOS CAMBIOS DE LA PRUEBA DE AISLAMIENTO
        # ----------------------------------------------------
        
        # Añadimos la UI completa a la página (self.master_container se define en _setup_ui)
        self.page.add(self.master_container) 
        self.page.update()
        
        # Iniciar el juego automáticamente
        self.game.start_game() 


    def _load_audio(self):
        """Carga los archivos WAV usando AudioPlayer."""
        for color, file_name in SIMON_SOUNDS_MAP.items():
            self.audio_players[color] = ft.Audio(src=file_name)
            self.page.overlay.append(self.audio_players[color])
        self.page.update()

    def _setup_ui(self):
        """Construye todos los elementos de la interfaz."""
        
        # Marcador de puntaje
        self.score_label = ft.Text("Puntaje: 0", size=30, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        self.high_score_label = ft.Text("Récord: 0", size=20, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
        
        # ETIQUETA NUEVA: Para mostrar la puntuación dentro del Overlay de Game Over
        self.game_over_label_dialog = ft.Text(
            "Puntuación: 0", 
            size=18, 
            color=ft.Colors.WHITE70, # <-- CORREGIDO
            text_align=ft.TextAlign.CENTER
        )
        
        # 🛑 ELIMINAMOS self.game_over_dialog (el antiguo ft.AlertDialog)

        
        # --- Creación de Botones y Cuadrícula Dinámica ---
        
        # 1. Crear todos los botones en el diccionario self.buttons
        for color_name in COLORES:
            btn = ft.Container(
                width=150, height=150,
                # CAMBIO: Agregamos una sombra interna para el efecto de brillo apagado
                bgcolor=FLET_COLORS[color_name],
                border_radius=ft.border_radius.all(75), # Hacerlo circular
                data=color_name,
                on_click=self.handle_button_click, 
                alignment=ft.alignment.center,
                # Ajustamos la sombra para un efecto de luz apagada (similar al boceto)
                shadow=ft.BoxShadow(
                    spread_radius=-10, 
                    blur_radius=25, 
                    color=FLET_COLORS[color_name], 
                    offset=ft.Offset(0, 0), 
                    blur_style=ft.ShadowBlurStyle.OUTER
                )
            )
            self.buttons[color_name] = btn
        
        # 2. Obtener la lista de los objetos de los botones
        button_list = list(self.buttons.values())
        
        # 3. Construir el Grid 2x2 de forma más concisa
        game_grid = ft.Column(
            controls=[
                ft.Row(
                    controls=button_list[0:2],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                ),
                ft.Row(
                    controls=button_list[2:4],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        # --- Elemento central del diseño ---
        self.center_circle = ft.Container(
            width=100,
            height=100,
            border_radius=ft.border_radius.all(50), # Círculo perfecto
            bgcolor=ft.Colors.BLUE_GREY_800, # <-- CORREGIDO
            alignment=ft.alignment.center,
            content=ft.Text("Simon", size=16, color=ft.Colors.WHITE54, weight=ft.FontWeight.BOLD) # <-- CORREGIDO
        )

        # La pila que superpone la cuadrícula de botones y el círculo central
        game_area_stack = ft.Stack(
            controls=[
                game_grid,
                self.center_circle # El círculo central se superpone
            ],
            # Eliminamos los tamaños fijos (width/height)
            alignment=ft.alignment.center # Centra el contenido de la pila
        )
        
        
        # Contenido principal de la aplicación (Récord, Área de Juego, Puntaje)
        # 1. Creamos la columna de controles
        app_content_column = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER_400), # <-- CORREGIDO
                            self.high_score_label,# Texto de récord
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5
                    ),
                    padding=ft.padding.only(top=30, bottom=30)
                ),
                game_area_stack, # Nuestra área de juego con botones y centro
                self.score_label, # Marcador de puntaje actual
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

        # 2. Envolvemos la columna en un Container para aplicar el bgcolor
        app_content = ft.Container(
            content=app_content_column,
            bgcolor=ft.Colors.BLUE_GREY_900, # <-- CORREGIDO
            expand=True # Aseguramos que el contenedor ocupe todo el espacio
        )
        
        # ----------------------------------------------------------------------------------
        # 🌟 OVERLAY MANUAL DE GAME OVER (Reemplazo de ft.AlertDialog)
        # ----------------------------------------------------------------------------------

        # 1. Definición del CONTENIDO del diálogo (lo que antes iba dentro del AlertDialog)
        dialog_content = ft.Column(
            [
                ft.Text("GAME OVER", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                # Etiqueta que actualiza la puntuación final
                self.game_over_label_dialog, 
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Volver a jugar",
                        on_click=self.restart_game_click,
                        style=ft.ButtonStyle(
                            bgcolor={ControlState.DEFAULT: ft.Colors.BLUE_ACCENT_700}, # <-- CORREGIDO
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(vertical=15, horizontal=20)
                        ),
                    ),
                    width=250, padding=ft.padding.only(bottom=10)
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        text="Menú Principal",
                        on_click=self.close_game_over_overlay, # Nuevo handler para cerrar el overlay
                        style=ft.ButtonStyle(
                            bgcolor={ControlState.DEFAULT: ft.Colors.BLUE_ACCENT_700}, # <-- CORREGIDO
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.padding.symmetric(vertical=15, horizontal=20)
                        ),
                    ),
                    width=250
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
        )

        # 2. Crea el OVERLAY principal
        self.game_over_overlay = ft.Container(
            content=ft.Container( # Un contenedor secundario para centrar la caja del diálogo
                content=dialog_content,
                width=300, # Ancho de la caja del diálogo
                height=350, # Altura de la caja del diálogo
                bgcolor=ft.Colors.BLUE_GREY_800, # <-- CORREGIDO
                border_radius=20,
                padding=25,
                alignment=ft.alignment.center
            ),
            # Configuraciones CRÍTICAS del Overlay
            alignment=ft.alignment.center, # Centrar la caja del diálogo en la pantalla
            expand=True, 
            visible=False, # **INICIALMENTE INVISIBLE**
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BLACK), # <-- CORREGIDO (ft.Colors.)
        )

        # ----------------------------------------------------------------------------------

        # La pila principal que superpone el contenido de la aplicación y el overlay
        main_stack = ft.Stack(
            controls=[
                app_content, # 1. Nuestro contenido de juego
                self.game_over_overlay, # 2. Nuestro nuevo diálogo manual (Overlay)
            ],
            expand=True
        )
        
        # El master_container envuelve la pila para expandirla
        self.master_container = ft.Container(
            content=main_stack,
            expand=True
        )

        # 🛑 NOTA: self.page.add(self.master_container) se llama en __init__


    # --- Callbacks de la Lógica del Juego ---

    def execute_delayed_action(self, action, delay_seconds):
        """Ejecuta una función (action) después de un retardo (delay_seconds)."""
        def delayed_function():
            time.sleep(delay_seconds)
            # Asegura que la acción se ejecute en el hilo principal de Flet
            self.page.run_thread(action) 

        threading.Thread(target=delayed_function, daemon=True).start()

    def run_flash_sequence(self, sequence, flash_duration):
        """Lanza un hilo para mostrar la secuencia de flashes del juego."""
        def sequence_thread():
            delay_sequence = 0.25 
            
            # Deshabilitar botones mientras la secuencia se muestra
            self.set_buttons_active(False) 
            
            for color in sequence:
                self.flash_button_ui(color, flash_duration)
                # Pausa entre un flash y el siguiente
                time.sleep(flash_duration + delay_sequence) 
            
            # Habilitar botones al finalizar la secuencia (turno del jugador)
            self.set_buttons_active(True)

        threading.Thread(target=sequence_thread, daemon=True).start()

    def flash_button_ui(self, color_name, duration):
        """Realiza el efecto visual y reproduce el sonido para un solo botón."""
        button = self.buttons[color_name]
        original_color = FLET_COLORS[color_name]
        
        # 1. Reproducir Sonido
        self.play_sound(color_name)
        
        # 2. Animación de Color
        def flash_animation():
            # Estado A: Brillante
            button.bgcolor = FLASH_COLOR 
            button.shadow = ft.BoxShadow(
                spread_radius=1, 
                blur_radius=20, 
                color=original_color, 
                offset=ft.Offset(0, 0), 
                blur_style=ft.ShadowBlurStyle.OUTER
            )
            self.page.update()
            
            time.sleep(duration) 
            
            # Estado B: Original
            button.bgcolor = original_color
            # Volvemos a la sombra original de luz apagada
            button.shadow = ft.BoxShadow(
                spread_radius=-10, 
                blur_radius=25, 
                color=original_color, 
                offset=ft.Offset(0, 0), 
                blur_style=ft.ShadowBlurStyle.OUTER
            )
            self.page.update()
        
        # Ejecutar la animación en el hilo de UI
        self.page.run_thread(flash_animation)

    def play_sound(self, color_name):
        """Reproduce el sonido asociado al color."""
        audio = self.audio_players.get(color_name)
        if audio:
            audio.seek(0)
            audio.play()

    def set_buttons_active(self, active):
        """Activa o desactiva la capacidad de hacer clic en los botones."""
        for btn in self.buttons.values():
            btn.disabled = not active
        self.page.update()

    def update_score_ui(self, score_text):
        """Callback: Actualiza el marcador de puntaje."""
        self.score_label.value = score_text
        self.page.update()

    def update_high_score_ui(self, high_score_text):
        """Callback: Actualiza el marcador de Récord."""
        self.high_score_label.value = high_score_text
        self.page.update()
    
    def _show_game_over_dialog(self, final_score_text):
        """Muestra el diálogo de Game Over, ahora es un overlay manual."""
        try:
            # El texto que llega es "Game Over — Puntaje final: X"
            score_value = final_score_text.split(': ')[-1]
        except:
            score_value = "???"
            
        # 1. Actualiza el contenido del overlay
        self.game_over_label_dialog.value = f"Tu puntuación es {score_value}"
        
        # 2. Hace el overlay visible
        self.game_over_overlay.visible = True
        
        # 3. Actualiza la página
        self.page.update()


    def handle_game_over_ui(self, final_score_text):
        """Callback: Muestra el Game Over."""
        print(f"--- GAME OVER: LLAMADA RECIBIDA --- {final_score_text}")
        # Actualizamos el puntaje principal
        self.score_label.value = final_score_text 
        self.set_buttons_active(False)
        # Llamamos al hilo principal de Flet para mostrar el overlay
        self.page.run_thread(lambda: self._show_game_over_dialog(final_score_text))


    # --- Handlers de Eventos de Flet ---

    def handle_button_click(self, e: ft.ControlEvent):
        """Manejador de clic de Flet, llama a la lógica del juego."""
        if e.control.disabled:
            return
            
        color_name = e.control.data 
        
        # La lógica verifica si el movimiento es correcto.
        self.game.check_player_press(color_name)
        
        # Retroalimentación inmediata: Flash y sonido para la pulsación del jugador
        threading.Thread(target=lambda: self.flash_button_ui(color_name, self.game.flash_duration), daemon=True).start()


    def close_game_over_overlay(self, e=None):
        """Oculta el overlay de Game Over, llamado por 'Menú Principal' o 'Volver a Jugar'."""
        self.game_over_overlay.visible = False
        self.page.update()

    def restart_game_click(self, e):
        """Manejador de clic del botón de Reinicio."""
        # Ocultar el overlay
        self.close_game_over_overlay() 
        # Iniciar el juego
        self.game.start_game()
        

def main(page: ft.Page):
    """Función principal que inicia la aplicación Flet."""
    SimonFletApp(page)

if __name__ == "__main__":
    # Inicia la aplicación en modo de escritorio (Desktop)
    ft.app(target=main)
