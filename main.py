import speech_recognition as sr
import librosa
import os
from assistanttools.actions import get_llm_response, message_history, preload_model
from faster_whisper import WhisperModel
import soundfile as sf
import json
import uuid
from assistanttools.utils import check_if_exit, check_if_ignore


model = WhisperModel("base.en")


def transcribe_audio(file_path):
    segments, _ = model.transcribe(file_path)
    segments = list(segments)  # The transcription will actually run here.
    transcript = " ".join([x.text for x in segments]).strip()
    print("Transcription: ", transcript)
    return transcript


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

    def listen_for_wake_word(self):

        recognizer = sr.Recognizer()
        os.system(f"espeak 'Hello. How can I help you today?'")
        while True:
            with sr.Microphone() as source:
                try:
                    audio = recognizer.listen(
                        source, timeout=self.timeout // 3, phrase_time_limit=self.phrase_time_limit // 2)
                except sr.WaitTimeoutError:
                    continue

            try:
                with open(f"{self.sounds_path}audio.wav", "wb") as f:
                    f.write(audio.get_wav_data())

                speech, rate = librosa.load(
                    f"{self.sounds_path}audio.wav", sr=16000)
                sf.write(f"{self.sounds_path}audio.wav", speech, rate)

                transcription = transcribe_audio(
                    file_path=f"{self.sounds_path}audio.wav")

                if any(x in transcription.lower() for x in self.wake_word):
                    os.system(f"espeak 'Yes?'")
                    self.action_engine.run_second_listener(timeout=self.timeout,
                                                           duration=self.phrase_time_limit)

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

                transcription = transcribe_audio(
                    file_path=f"{self.sounds_path}command.wav")

                if check_if_ignore(transcription):
                    continue

                if check_if_exit(transcription):
                    os.system(f"espeak 'Program stopped. See you later!'")
                    return

                else:
                    os.system(f"play -v .1 sounds/notification.wav")
                    _, self.message_history = get_llm_response(
                        transcription, self.message_history, model_name=self.ollama_model)

                # save appended message history to json
                if self.store_conversations:
                    with open(f"storage/{self.conversation_id}.json", "w") as f:
                        json.dump(self.message_history, f, indent=4)

            except sr.UnknownValueError:
                print("Could not understand audio")


if __name__ == "__main__":
    from config import config
    preload_model(config["LOCAL_MODEL"])
    action_engine = ActionEngine(sounds_path=config["SOUNDS_PATH"],
                                 whisper_cpp_path=config["WHISPER_CPP_PATH"],
                                 whisper_model_path=config["WHISPER_MODEL_PATH"],
                                 ollama_model=config["LOCAL_MODEL"],
                                 message_history=message_history,
                                 store_conversations=config["STORE_CONVERSATIONS"],
                                 vision_model=config["VISION_MODEL"])

    wake_word_listener = WakeWordListener(timeout=config["TIMEOUT"],
                                          phrase_time_limit=config["PHRASE_TIME_LIMIT"],
                                          sounds_path=config["SOUNDS_PATH"],
                                          wake_word=config["WAKE_WORD"],
                                          action_engine=action_engine,
                                          whisper_cpp_path=config["WHISPER_CPP_PATH"],
                                          whisper_model_path=config["WHISPER_MODEL_PATH"])

    wake_word_listener.listen_for_wake_word()
