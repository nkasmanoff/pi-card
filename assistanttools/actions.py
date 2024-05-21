import ollama
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from config import config
from .generate_detr import generate_bounding_box_caption, model, processor
from .generate_gguf import generate_gguf_stream
from .utils import check_if_vision_mode, dictate_ollama_stream, remove_parentheses
load_dotenv()

message_history = [{
    'role': 'user',
    'content': config['SYSTEM_PROMPT'],
}]

sentence_stoppers = ['. ', '.\n', '? ', '! ', '?\n', '!\n', '.\n']


def preload_model(model_name="llama3:instruct"):
    print("Preparing model...")
    os.system(
        f"curl http://localhost:11434/api/chat -d '{{\"model\": \"{model_name}\"}}'")

    print("Model preloaded.")
    return


def get_llm_response(transcription, message_history, model_name='llama3:instruct', use_rag=True):
    print("Here's what you said: ", transcription)
    transcription = remove_parentheses(transcription)
    if use_rag:
        # Experimental idea for supplmenting with external data. Tool use may be better but this could start.
        if 'weather' in transcription:
            os.system(f"espeak 'Getting weather data.'")
            message_history = add_in_weather_data(
                message_history, transcription)
        elif check_if_vision_mode(transcription):
            os.system(f"espeak 'Getting image data.'")
            response, message_history = generate_image_response(
                message_history, transcription)
            return response, message_history
        elif "news" in transcription:
            os.system(f"espeak 'Getting news data.'")
            message_history = add_in_news_data(message_history, transcription)

        else:
            message_history.append({
                'role': 'user',
                'content': transcription,
            })

    if config['CONDENSE_MESSAGES'] and len(message_history) > config['TRAILING_MESSAGE_COUNT'] + 1:
        # remove all but the first and last n messages
        msg_history = message_history[:1] + \
            message_history[-config['TRAILING_MESSAGE_COUNT']:]

    else:
        msg_history = message_history

    stream = ollama.chat(model=model_name,
                         stream=True, messages=msg_history)

    response = dictate_ollama_stream(stream)

    message_history.append({
        'role': 'assistant',
        'content': response,
    })

    return response, message_history


def add_in_weather_data(message_history, transcription):
    """
    Add in weather data to the message history.
    """

    api_key = os.getenv("TOMORROWIO_API_KEY")
    headers = {"accept": "application/json"}

    rt_url = f"https://api.tomorrow.io/v4/weather/realtime?location=new%20york&apikey={api_key}"
    rt_response = requests.get(rt_url, headers=headers)
    data = rt_response.json()['data']
    temp = data['values']['temperature']
    humidity = data['values']['humidity']
    precipitation = data['values']['precipitationProbability']
    cloudCover = data['values']['cloudCover']

    location = rt_response.json()['location']['name']

    message_history.append({
        'role': 'user',
        'content': f"""Current weather data:

        Location: {location}
        T: {temp} C
        Humidity: {humidity}%
        Rain Prob: {precipitation}%
        Cloud Cover: {cloudCover}%

        Question:
        {transcription}

        Answer:
        """,
    })
    return message_history


def add_in_news_data(message_history, transcription):

    url = "https://news.ycombinator.com/"

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news = soup.find_all('tr', class_='athing')
    top_articles = ""
    for n in news[:1]:
        top_articles += n.text + "\n"

    message_history.append({
        'role': 'user',
        'content': f"""Here are the top articles on HackerNews:

        {top_articles}


        Question:
        {transcription}

        Answer:
        """,
    })
    return message_history


def generate_image_response(message_history, transcription):
    """
    Generate an image response.
    """
    if config["VISION_MODEL"] == 'detr':
        caption = generate_bounding_box_caption(model, processor)

        message_history.append({
            'role': 'user',
            'content': f"""Here is the image description:

            {caption}

            Question:
            {transcription}

            Answer:
            """,
        })
        stream = ollama.chat(model=config["LOCAL_MODEL"],
                             stream=True, messages=message_history)

        response = dictate_ollama_stream(stream)

    elif config["VISION_MODEL"] == 'moondream':
        os.system(f"espeak 'Taking a picture.'")

        os.system("libcamera-still -o images/detr-image.jpg")
        os.system(f"espeak 'Analyzing the image.'")

        prompt = '"<image>\n\nQuestion: What do you see?\n\nAnswer: "'
        response = ""
        word = ""

        for chunk in generate_gguf_stream(llama_cpp_path=config["LLAMA_CPP_PATH"],
                                          model_path=config["MOONDREAM_MODEL_PATH"],
                                          mmproj_path=config["MOONDREAM_MMPROJ_PATH"],
                                          image_path="images/image.jpg",
                                          prompt=prompt,
                                          temp=0.):
            word += chunk
            if ' ' in chunk:
                os.system(f"espeak '{word}'")
                response += word
                word = ""

        os.system(f"espeak '{word}'")

    message_history.append({
        'role': 'user',
        'content': transcription,
    })
    message_history.append({
        'role': 'assistant',
        'content': response,
    })

    return response, message_history
