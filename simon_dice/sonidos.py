import numpy as np
from scipy.io.wavfile import write
 
def generar_sonido(frecuencia, duracion=0.5, nombre_archivo="sonido.wav"):
    sample_rate = 44100
    t = np.linspace(0, duracion, int(sample_rate * duracion), False)
    nota = np.sin(frecuencia * t * 2 * np.pi)
    envelope = np.ones_like(nota)
    attack = int(0.1 * sample_rate)
    release = int(0.2 * sample_rate)
    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[-release:] = np.linspace(1, 0, release)
    nota = nota * envelope
    audio = nota * (2**15 - 1)
    audio = audio.astype(np.int16)
    write(nombre_archivo, sample_rate, audio)
    print(f"Sonido generado: {nombre_archivo} ({frecuencia} Hz)")
 
def main():
    print("Generador de sonidos para Simon Dice")
    print("========================================")
    sonidos = [
        (440, "sound1.wav"),
        (523, "sound2.wav"),
        (659, "sound3.wav"),
        (784, "sound4.wav")
    ]
    for freq, nombre in sonidos:
        generar_sonido(frecuencia=freq, nombre_archivo=nombre)
    print("========================================")
    print("Todos los sonidos han sido generados")
    print("Archivos creados: sound1.wav, sound2.wav, sound3.wav, sound4.wav")
 
if __name__ == "__main__":
    try:
        import numpy as np
        from scipy.io.wavfile import write
    except ImportError:
        print("Error: Faltan dependencias")
        print("Instala con: pip install numpy scipy")
        exit(1)
    main()