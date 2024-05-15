
# Wake Word Engine
SOUNDS_PATH = 'sounds/'
WAKE_WORD = ["rasp", "berry", "barry", "razbear", "brad", "raster"]
TIMEOUT = 2
PHRASE_TIME_LIMIT = 5

# Whisper Model
WHISPER_CPP_PATH = "../whisper.cpp/"
WHISPER_MODEL_PATH = "/home/nkasmanoff/Desktop/whisper.cpp/models/ggml-tiny.en.bin"

# Vision Model
LLAMA_CPP_PATH = "../md-gguf/llama.cpp/"
MOONDREAM_MMPROJ_PATH = "../md-gguf/moondream2/moondream2-mmproj-f16.gguf"
MOONDREAM_MODEL_PATH = "../moondream-quants/moondream2-text-model.Q8.gguf"
VISION_MODEL = "moondream"

# Text Assistant
LOCAL_MODEL = "llama3:instruct"
STORE_CONVERSATIONS = True
CONDENSE_MESSAGES = False

SYSTEM_PROMPT = 'You are PiCard, a Raspbery Pi Voice Assistant. Please help users with brief answers.'
