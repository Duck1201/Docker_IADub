import os
import subprocess
import whisper
from TTS.api import TTS
import argostranslate.package
import argostranslate.translate

os.environ["COQUI_TOS_AGREED"] = "1"

INPUT_DIR = "/input"
OUTPUT_DIR = "/output"
TEMP_DIR = "/temp"

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 🔥 LOAD MODELS (UMA VEZ SÓ)
print("🧠 Carregando Whisper...")
whisper_model = whisper.load_model("base")

print("🗣️ Carregando TTS...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")


# 🔧 Tradução
def ensure_translation_model():
    installed_languages = argostranslate.translate.get_installed_languages()

    has_en = any(l.code == "en" for l in installed_languages)
    has_pt = any(l.code == "pt" for l in installed_languages)

    if not (has_en and has_pt):
        print("⬇️ Baixando modelo en → pt...")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        package = next(
            p for p in available_packages
            if p.from_code == "en" and p.to_code == "pt"
        )

        argostranslate.package.install_from_path(package.download())


def get_translation():
    langs = argostranslate.translate.get_installed_languages()
    from_lang = next(l for l in langs if l.code == "en")
    to_lang = next(l for l in langs if l.code == "pt")
    return from_lang.get_translation(to_lang)


# 🎧 Gerar silêncio
def generate_silence(duration, output_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", "anullsrc=r=16000:cl=mono",
        "-t", str(duration),
        output_path
    ], check=True)


# 🎬 Processamento principal
def process_video(video_file, translation):
    print(f"\n🎥 Processando: {video_file}")

    video_path = os.path.join(INPUT_DIR, video_file)
    base_name = os.path.splitext(video_file)[0]

    audio_path = os.path.join(TEMP_DIR, f"{base_name}.wav")
    final_audio = os.path.join(TEMP_DIR, f"{base_name}_final.wav")
    final_video = os.path.join(OUTPUT_DIR, f"{base_name}_dublado.mp4")

    # 1. Extrair áudio
    print("🔊 Extraindo áudio...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        audio_path
    ], check=True)

    # 2. Transcrição com segments
    print("🧠 Transcrevendo...")
    result = whisper_model.transcribe(audio_path)
    segments = result["segments"]

    audio_parts = []
    current_time = 0.0

    # 3. Processar cada segmento
    for i, seg in enumerate(segments):
        start = seg["start"]
        end = seg["end"]
        text_en = seg["text"]

        print(f"➡️ Segmento {i}: {text_en}")

        # silêncio se necessário
        if start > current_time:
            silence_path = os.path.join(TEMP_DIR, f"silence_{i}.wav")
            silence_duration = start - current_time
            generate_silence(silence_duration, silence_path)
            audio_parts.append(silence_path)

        # tradução
        text_pt = translation.translate(text_en)

        # TTS
        seg_audio = os.path.join(TEMP_DIR, f"seg_{i}.wav")
        tts.tts_to_file(
            text=text_pt,
            file_path=seg_audio,
            speaker_wav=audio_path,
            language="pt"
        )

        audio_parts.append(seg_audio)
        current_time = end

    # 4. Concatenar tudo
    print("🔗 Concatenando áudio...")

    concat_list = os.path.join(TEMP_DIR, "concat.txt")
    with open(concat_list, "w") as f:
        for part in audio_parts:
            f.write(f"file '{part}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        final_audio
    ], check=True)

    # 5. Juntar com vídeo
    print("🎬 Renderizando vídeo final...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", final_audio,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-shortest",
        final_video
    ], check=True)

    print(f"✅ Final salvo em: {final_video}")


# 🚀 MAIN
if __name__ == "__main__":
    print("🚀 Iniciando pipeline...")

    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith((".mp4", ".mkv", ".avi"))]

    if not files:
        print("❌ Nenhum vídeo encontrado em /input")
        exit(1)

    ensure_translation_model()
    translation = get_translation()

    for video in files:
        try:
            process_video(video, translation)
        except Exception as e:
            print(f"❌ Erro ao processar {video}: {e}")