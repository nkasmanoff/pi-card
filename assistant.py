import speech_recognition as sr
import librosa
import os
from assistanttools.actions import get_llm_response, message_history, preload_model
from assistanttools.generate_gguf import generate_gguf_stream
from assistanttools.transcribe_gguf import transcribe_gguf
import soundfile as sf
import re
import json
import uuid


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
                    self.action_engine.run_second_listener(duration=5)

            except sr.UnknownValueError:
                print("Could not understand audio")


class ActionEngine:
    def __init__(
            self,
            sounds_path,
            whisper_cpp_path,
            whisper_model_path,
            llama_cpp_path,
            moondream_mmproj_path,
            moondream_model_path,
            ollama_model,
            message_history,
            store_conversations):
        self.sounds_path = sounds_path
        self.whisper_cpp_path = whisper_cpp_path
        self.whisper_model_path = whisper_model_path
        self.llama_cpp_path = llama_cpp_path
        self.moondream_mmproj_path = moondream_mmproj_path
        self.moondream_model_path = moondream_model_path
        self.ollama_model = ollama_model
        self.message_history = message_history
        self.store_conversations = store_conversations
        self.conversation_id = str(uuid.uuid4())

    def run_second_listener(self, duration):
        recognizer = sr.Recognizer()
        while True:
            with sr.Microphone() as source:
                print("Listening for command...")
                try:
                    audio = recognizer.listen(
                        source, timeout=2, phrase_time_limit=duration)
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

                if self.check_if_ignore(transcription):
                    continue

                if self.check_if_exit(transcription):
                    os.system(f"espeak 'Program stopped. See you later!'")
                    return

                elif self.check_if_vision_mode(transcription):
                    self.message_history.append({
                        "role": "user",
                        "content": transcription
                    })
                    os.system(f"espeak 'Taking a photo.'")
                    os.system("libcamera-still -o images/image.jpg")
                    os.system(f"espeak 'Photo taken. Please wait.'")

                    prompt = '"<image>\n\nQuestion: Describe this image.\n\nAnswer: "'
                    response = ""
                    word = ""
                    for chunk in generate_gguf_stream(llama_cpp_path=self.llama_cpp_path,
                                                      model_path=self.moondream_model_path,
                                                      mmproj_path=self.moondream_mmproj_path,
                                                      image_path="images/image.jpg",
                                                      prompt=prompt,
                                                      temp=0.):
                        word += chunk
                        if ' ' in chunk:
                            os.system(f"espeak '{word}'")
                            response += word
                            word = ""

                    os.system(f"espeak '{word}'")
                    self.message_history.append({
                        "role": "assistant",
                        "content": response,
                    })

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

    def check_if_ignore(self, transcription):
        """
        Check if the transcription should be ignored. This happens if the whisper prediction is "you" or "." or "", or is some sound effect like wind blowing, usually inside parentheses.
        """
        if transcription.strip() == "you" or transcription.strip() == "." or transcription.strip() == "":
            return True
        if re.match(r"\(.*\)", transcription):
            return True
        return False

    def check_if_exit(self, transcription):
        """
        Check if the transcription is an exit command.
        """
        return any([x in transcription.lower() for x in ["stop", "exit", "quit"]])

    def check_if_vision_mode(self, transcription):
        """
        Check if the transcription is a command to enter vision mode.
        """
        return any([x in transcription.lower() for x in ["photo", "picture", "image", "snap", "shoot"]])


if __name__ == "__main__":
    from config import SOUNDS_PATH, WAKE_WORD, WHISPER_CPP_PATH, \
        WHISPER_MODEL_PATH, LLAMA_CPP_PATH, MOONDREAM_MMPROJ_PATH, \
        MOONDREAM_MODEL_PATH, LOCAL_MODEL, STORE_CONVERSATIONS

    preload_model(LOCAL_MODEL)
    action_engine = ActionEngine(sounds_path=SOUNDS_PATH,
                                 whisper_cpp_path=WHISPER_CPP_PATH,
                                 whisper_model_path=WHISPER_MODEL_PATH,
                                 llama_cpp_path=LLAMA_CPP_PATH,
                                 moondream_mmproj_path=MOONDREAM_MMPROJ_PATH,
                                 moondream_model_path=MOONDREAM_MODEL_PATH,
                                 ollama_model=LOCAL_MODEL,
                                 message_history=message_history,
                                 store_conversations=STORE_CONVERSATIONS)

    wake_word_listener = WakeWordListener(timeout=2,
                                          phrase_time_limit=2,
                                          sounds_path=SOUNDS_PATH,
                                          wake_word=WAKE_WORD,
                                          action_engine=action_engine,
                                          whisper_cpp_path=WHISPER_CPP_PATH,
                                          whisper_model_path=WHISPER_MODEL_PATH)

    wake_word_listener.listen_for_wake_word()
