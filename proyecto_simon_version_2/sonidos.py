import numpy as np
import os
print("--- INICIO DE SCRIPT DE SONIDOS ---")

def generar_sonido(frecuencia, duracion=0.5, nombre_archivo="sonido.wav"):
    """
    Genera una nota de onda sinusoidal con ataque/decaimiento y la guarda como archivo WAV.
    """
    try:
        from scipy.io.wavfile import write
    except ImportError:
        # Esto debería manejarse en generate_all_sounds, pero es una seguridad extra.
        print(f"Error: No se pudo importar scipy para generar {nombre_archivo}.")
        return

    sample_rate = 44100
    # Generar el vector de tiempo
    t = np.linspace(0, duracion, int(sample_rate * duracion), False)
    
    # Generar la onda sinusoidal
    nota = np.sin(frecuencia * t * 2 * np.pi)
    
    # Aplicar un envolvente (Attack-Release) para evitar clics
    envelope = np.ones_like(nota)
    attack = int(0.1 * sample_rate)
    release = int(0.2 * sample_rate)
    
    # Rampa de ataque (fade-in)
    if attack > 0:
        envelope[:attack] = np.linspace(0, 1, attack)
        
    # Rampa de decaimiento (fade-out)
    if release > 0 and len(envelope) > release:
        envelope[-release:] = np.linspace(1, 0, release)
        
    # Aplicar el envolvente a la nota
    nota = nota * envelope
    
    # Escalar a formato de audio de 16 bits
    audio = nota * (2**15 - 1)
    audio = audio.astype(np.int16)
    
    # Escribir el archivo WAV
    write(nombre_archivo, sample_rate, audio)
    print(f"Sonido generado: {nombre_archivo} ({frecuencia} Hz)")

def generate_all_sounds():
    """
    Función principal para generar todos los archivos de sonido requeridos por el juego.
    """
    try:
        from scipy.io.wavfile import write
    except ImportError:
        print("-----------------------------------------------------------------------")
        print("ERROR DE GENERACIÓN DE SONIDO: Faltan dependencias críticas.")
        print("Asegúrate de tener instalados 'numpy' y 'scipy'.")
        print("Instala con: pip install numpy scipy")
        print("-----------------------------------------------------------------------")
        return False

    print("Generador de sonidos para Simon Dice")
    print("========================================")
    
    # 💡 ¡NUEVAS FRECUENCIAS! Más distantes para un sonido más "Simon Dice"
    sonidos_a_generar = [
        (466, "sound1.wav"),  # Frecuencia 1
        (587, "sound2.wav"),  # Frecuencia 2
        (740, "sound3.wav"),  # Frecuencia 3
        (932, "sound4.wav")   # Frecuencia 4 (más alta)
    ]
    
    for freq, nombre in sonidos_a_generar:
        generar_sonido(frecuencia=freq, nombre_archivo=nombre)
        
    print("========================================")
    print("Todos los sonidos nuevos han sido generados (sound1.wav - sound4.wav).")
    return True

if __name__ == "__main__":
    generate_all_sounds()
