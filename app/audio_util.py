from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

def reduce_silence_in_mp3(input_path, output_path, silence_thresh=-40, min_silence_len=1000, silence_removal_factor=0.8):
    """
    Reduce el silencio en un archivo MP3.
    
    :param input_path: Ruta al archivo MP3 de entrada
    :param output_path: Ruta donde guardar el archivo procesado
    :param silence_thresh: Umbral de silencio (dBFS); cuanto más bajo, más sensible
    :param min_silence_len: Duración mínima del silencio en ms para considerarlo como tal
    :param silence_removal_factor: Factor de reducción del silencio (0 = elimina todo, 1 = no cambia)
    """
    print("Cargando archivo...")
    audio = AudioSegment.from_mp3(input_path)

    print("Dividiendo audio por silencios...")
    chunks = split_on_silence(
        audio,
        silence_thresh=silence_thresh,
        min_silence_len=min_silence_len,
        keep_silence=int(min_silence_len * silence_removal_factor)  # Acortamos el silencio
    )

    print("Uniendo fragmentos...")
    combined = AudioSegment.empty()
    for chunk in chunks:
        combined += chunk

    print(f"Guardando archivo procesado en {output_path}...")
    combined.export(output_path, format="mp3")

    print("Proceso completado.")

def duration_mp3(path_mp3):
    audio = AudioSegment.from_file(path_mp3)
    duracion_ms = len(audio)
    duracion_segundos = int(duracion_ms / 1000)
    horas = duracion_segundos // 3600
    minutos = (duracion_segundos % 3600) // 60
    segundos = duracion_segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# Ejemplo de uso
if __name__ == "__main__":
    input_file = os.path.join(END_AUDIO_DIR, f'podcast_20250510_1801.mp3')
    output_file = os.path.join(END_AUDIO_DIR, "prueba_sin_silencios.mp3")

    reduce_silence_in_mp3(
        input_file,
        output_file,
        silence_thresh=-45,         # ajusta según nivel de ruido de fondo
        min_silence_len=800,        # considera silencios de al menos 800ms
        silence_removal_factor=0.6  # elimina el 60% del silencio original
    )