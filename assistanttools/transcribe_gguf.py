import subprocess
import re
import librosa

import soundfile as sf


def transcribe_gguf(whisper_cpp_path, model_path, file_path):
    command = f"./{whisper_cpp_path}main -m {model_path} -f {file_path}"
    print("Command: ", command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    process.wait()
    output = process.stdout.read()
    output = output.decode('utf-8')
    output = re.sub(r'\[.*?\]', '', output)
    output = re.sub(' +', ' ', output)
    output = output.replace('\n', ' ')
    output = output.strip()

    return output


if __name__ == '__main__':

    # take an image with the camera
    # Load the audio file in librosa
    audio_path = "/home/nkasmanoff/Desktop/whisper.cpp/samples/jfk.wav"

    output = transcribe_gguf(whisper_cpp_path="../whisper.cpp/",
                             model_path="/home/nkasmanoff/Desktop/whisper.cpp/models/ggml-base.en.bin",
                             file_path=audio_path)

    print("Output: ", output)
