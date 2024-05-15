import speech_recognition as sr
import librosa
import os
from assistanttools.actions import get_llm_response, message_history, preload_model, generate_image_response
from assistanttools.transcribe_gguf import transcribe_gguf
import soundfile as sf
import json
import uuid
from assistanttools.utils import check_if_exit, check_if_ignore


class WakeWordListener:
    def __init__(self,
                 timeout,
                 phrase_time_limit,
                 sounds_path,
                 wake_word,
                 action_engine,
                 whisper_cpp_path,
                 whisper_model_path):

        self.timeout = timeout
        self.phrase_time_limit = phrase_time_limit
        self.sounds_path = sounds_path
        self.wake_word = wake_word
        self.action_engine = action_engine
        self.whisper_cpp_path = whisper_cpp_path
        self.whisper_model_path = whisper_model_path
        self.command_timeout = 5
        self.command_duration = 5

    def listen_for_wake_word(self):

        recognizer = sr.Recognizer()
        os.system(f"espeak 'Hello, I am ready to assist you.'")
        while True:
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(
                        source, timeout=self.timeout, phrase_time_limit=self.phrase_time_limit)
                except sr.WaitTimeoutError:
                    continue

            try:
                with open(f"{self.sounds_path}audio.wav", "wb") as f:
                    f.write(audio.get_wav_data())

                speech, rate = librosa.load(
                    f"{self.sounds_path}audio.wav", sr=16000)
                sf.write(f"{self.sounds_path}audio.wav", speech, rate)

                transcription = transcribe_gguf(whisper_cpp_path=self.whisper_cpp_path,
                                                model_path=self.whisper_model_path,
                                                file_path=f"{self.sounds_path}audio.wav")

                if any(x in transcription.lower() for x in self.wake_word):
                    os.system(f"espeak 'Yes?'")
                    self.action_engine.run_second_listener(timeout=self.command_timeout,
                                                           duration=self.command_duration)

            except sr.UnknownValueError:
                print("Could not understand audio")


class ActionEngine:
    def __init__(
            self,
            sounds_path,
            whisper_cpp_path,
            whisper_model_path,
            ollama_model,
            message_history,
            store_conversations,
            vision_model):
        self.sounds_path = sounds_path
        self.whisper_cpp_path = whisper_cpp_path
        self.whisper_model_path = whisper_model_path
        self.ollama_model = ollama_model
        self.message_history = message_history
        self.store_conversations = store_conversations
        self.vision_model = vision_model
        self.conversation_id = str(uuid.uuid4())

    def run_second_listener(self, timeout, duration):
        recognizer = sr.Recognizer()
        while True:
            with sr.Microphone() as source:
                print("Listening for command...")
                try:
                    audio = recognizer.listen(
                        source, timeout=timeout, phrase_time_limit=duration)
                except sr.WaitTimeoutError:
                    continue

            try:
                with open(f"{self.sounds_path}command.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                speech, rate = librosa.load(
                    f"{self.sounds_path}command.wav", sr=16000)
                sf.write(f"{self.sounds_path}command.wav", speech, rate)

                transcription = transcribe_gguf(whisper_cpp_path=self.whisper_cpp_path,
                                                model_path=self.whisper_model_path,
                                                file_path=f"{self.sounds_path}command.wav")

                if check_if_ignore(transcription):
                    continue

                if check_if_exit(transcription):
                    os.system(f"espeak 'Program stopped. See you later!'")
                    return

                else:
                    os.system(f"play -v .1 sounds/heard.wav")
                    response, self.message_history = get_llm_response(
                        transcription, self.message_history, model_name=self.ollama_model)

                # save appended message history to json
                if self.store_conversations:
                    with open(f"storage/{self.conversation_id}.json", "w") as f:
                        json.dump(self.message_history, f, indent=4)

            except sr.UnknownValueError:
                print("Could not understand audio")


if __name__ == "__main__":
    from config import SOUNDS_PATH, WAKE_WORD, WHISPER_CPP_PATH, \
        WHISPER_MODEL_PATH, LOCAL_MODEL, STORE_CONVERSATIONS, VISION_MODEL, \
        TIMEOUT, PHRASE_TIME_LIMIT

    preload_model(LOCAL_MODEL)
    action_engine = ActionEngine(sounds_path=SOUNDS_PATH,
                                 whisper_cpp_path=WHISPER_CPP_PATH,
                                 whisper_model_path=WHISPER_MODEL_PATH,
                                 ollama_model=LOCAL_MODEL,
                                 message_history=message_history,
                                 store_conversations=STORE_CONVERSATIONS,
                                 vision_model=VISION_MODEL)

    wake_word_listener = WakeWordListener(timeout=TIMEOUT,
                                          phrase_time_limit=PHRASE_TIME_LIMIT,
                                          sounds_path=SOUNDS_PATH,
                                          wake_word=WAKE_WORD,
                                          action_engine=action_engine,
                                          whisper_cpp_path=WHISPER_CPP_PATH,
                                          whisper_model_path=WHISPER_MODEL_PATH)

    wake_word_listener.listen_for_wake_word()
