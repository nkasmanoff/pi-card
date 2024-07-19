import ollama
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from config import config
from .generate_detr import generate_bounding_box_caption, model, processor
from .generate_gguf import generate_gguf_stream
from .utils import check_if_vision_mode, dictate_ollama_stream, remove_parentheses
from .bert import load_model, predict_tool
from .play_spotify import play_spotify
load_dotenv()

message_history = [{
    'role': 'user',
    'content': config['SYSTEM_PROMPT'],
}]

sentence_stoppers = ['. ', '.\n', '? ', '! ', '?\n', '!\n', '.\n']


model, tokenizer = load_model()


def preload_model(model_name):
    print("Preparing model...")
    os.system(
        f"curl http://localhost:11434/api/chat -d '{{\"model\": \"{model_name}\"}}'")

    print("Model preloaded.")
    return


def get_llm_response(transcription, message_history, model_name='llama3:instruct', use_rag=True, GPIO=None):
    print("Here's what you said: ", transcription)
    transcription = remove_parentheses(transcription)
    if use_rag:
        predicted_tool = predict_tool(transcription, model, tokenizer)
        # Experimental idea for supplmenting with external data. Tool use may be better but this could start.
        if predicted_tool == 'check_weather':

            message_history = add_in_weather_data(
                message_history, transcription)
        elif predicted_tool == 'take_picture':
            response, message_history = generate_image_response(
                message_history, transcription)
            return response, message_history
        elif predicted_tool == 'check_news':
            message_history = add_in_news_data(message_history, transcription)
        elif predicted_tool == 'play_spotify':
            response, message_history = play_spotify(
                transcription, message_history)
            return response, message_history
        elif predicted_tool == 'no_tool_needed':
            message_history.append({
                'role': 'user',
                'content': transcription,
            })
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

    response = dictate_ollama_stream(stream, GPIO=GPIO)

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
    try:
        rt_response = requests.get(rt_url, headers=headers)
        data = rt_response.json()['data']

    except:
        message_history.append({
            'role': 'user',
            'content': f"""
            Context:
            Unable to connect to weather service. 

            Question:
            {transcription}
            """,
        })

        return message_history

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
    try:
        response = requests.get(url)

    except:
        message_history.append({
            'role': 'user',
            'content': f"Can you tell me if the wifi is working",
        })
        return message_history

    soup = BeautifulSoup(response.text, 'html.parser')

    news = soup.find_all('tr', class_='athing')
    top_articles = ""
    for n in news[:3]:
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
            'content': f"""Here is a description of the objects detected by an AI model:

            {caption}

            Question:
            Please summarize what this image saw.

            Answer:
            """,
        })
        stream = ollama.chat(model=config["LOCAL_MODEL"],
                             stream=True, messages=message_history)

        response = dictate_ollama_stream(stream)

    elif config["VISION_MODEL"] == 'moondream':
        os.system(f"espeak 'Taking a picture.'")

        os.system("libcamera-still -o images/image.jpg")
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
