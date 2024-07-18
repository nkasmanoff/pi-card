import speech_recognition as sr
import RPi.GPIO as GPIO
import os
GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)

GPIO.setup(2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

while True:
    # when the button is pressed, record audio
    if GPIO.input(2) == GPIO.LOW:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
            print("Done listening.")
            # save audio to .wav
            with open("audio.wav", "wb") as f:
                f.write(audio.get_wav_data())
            os.system("espeak 'Done.'")
