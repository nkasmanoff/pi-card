import re
import os


def check_if_vision_mode(transcription):
    """
    Check if the transcription is a command to enter vision mode.
    """
    return any([x in transcription.lower() for x in ["photo", "picture", "image", "snap", "shoot"]])


def check_if_exit(transcription):
    """
    Check if the transcription is an exit command.
    """
    return any([x in transcription.lower() for x in ["stop", "exit", "quit"]])


def check_if_ignore(transcription):
    """
    Check if the transcription should be ignored. 
    This happens if the whisper prediction is "you" or "." or "", or is some sound effect like wind blowing, usually inside parentheses.
    These are things caused by having the fan so close to the microphone, definitely need to fix.
    """
    if transcription.strip() == "you" or transcription.strip() == "." or transcription.strip() == "":
        return True
    if re.match(r"\(.*\)", transcription):
        return True
    return False


def dictate_ollama_stream(stream, early_stopping=False, max_spoken_tokens=250):
    response = ""
    streaming_word = ""
    for i, chunk in enumerate(stream):
        text_chunk = chunk['message']['content']
        streaming_word += text_chunk
        response += text_chunk
        if i > max_spoken_tokens:
            early_stopping = True
            break

        if is_complete_word(text_chunk):
            streaming_word_clean = streaming_word.replace(
                '"', "").replace("\n", " ").replace("'", "").replace("*", "").replace('-', '').replace(':', '').replace('!', '')
            os.system(f"espeak '{streaming_word_clean}'")
            streaming_word = ""
    if not early_stopping:
        streaming_word_clean = streaming_word.replace(
            '"', "").replace("\n", " ").replace("'", "").replace("*", "").replace('-', '').replace(':', '').replace('!', '')

        os.system(f"espeak '{streaming_word_clean}'")

    return response


def is_complete_word(text_chunk):
    """
    Given the subword outputs from streaming, as these chunks are added together, check if they form a coherent word. If so, return the word.
    """
    if ' ' in text_chunk:
        return True
    return False


def remove_parentheses(transcription):
    """
    Remove parentheses and their contents from the transcription.
    """
    return re.sub(r"\(.*\)", "", transcription).strip()
