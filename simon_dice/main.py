from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button

class SimonScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ejemplo: agregar un botón
        btn = Button(text="Iniciar Juego", size_hint=(0.3, 0.2), pos_hint={'center_x':0.5, 'center_y':0.5})
        self.add_widget(btn)

class SimonApp(App):
    def build(self):
        self.title = "Simón Dice"
        return SimonScreen()

if __name__ == '__main__':
    SimonApp().run()
