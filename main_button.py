from assistanttools.transcribe_gguf import transcribe_gguf
from faster_whisper import WhisperModel
import RPi.GPIO as GPIO
import pyaudio
import wave
import time
from assistanttools.actions import get_llm_response, message_history, preload_model
from assistanttools.utils import check_if_ignore
from config import config

preload_model(config["LOCAL_MODEL"])


def transcribe_audio(file_path):
    return transcribe_gguf(whisper_cpp_path=config["WHISPER_CPP_PATH"],
                           model_path=config["WHISPER_MODEL_PATH"],
                           file_path=file_path)


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def record_audio(GPIO):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 16000
    MAX_RECORD_SECONDS = 15
    WAVE_OUTPUT_FILENAME = "sounds/audio.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("* recording")
    # record while button is pressed
    frames = []
    start_time = time.time()
    while GPIO.input(2) == GPIO.LOW and time.time() - start_time < MAX_RECORD_SECONDS:
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


while True:
    if GPIO.input(2) == GPIO.LOW:
        print("Button was pushed!")
        record_audio(GPIO)
        transcription = transcribe_audio(
            file_path="/home/nkasmanoff/Desktop/pi-card/sounds/audio.wav")
        if check_if_ignore(transcription):
            print("insufficient audio")
            continue

        _, message_history = get_llm_response(
            transcription,
            message_history,
            model_name=config["LOCAL_MODEL"], GPIO=GPIO)
