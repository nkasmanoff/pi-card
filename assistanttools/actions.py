import ollama
import os
import requests
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from config import config
from .generate_detr import generate_bounding_box_caption, model, processor
from .generate_gguf import generate_gguf_stream
from .utils import check_if_vision_mode, dictate_ollama_stream, remove_parentheses
from .bert import load_model, predict_tool
from .play_spotify import play_spotify
load_dotenv()

if config['SYSTEM_PROMPT']:
    message_history = [{
        'role': 'system',
        'content': config['SYSTEM_PROMPT'],
    }]
else:
    message_history = []

sentence_stoppers = ['. ', '.\n', '? ', '! ', '?\n', '!\n', '.\n']


model, tokenizer = load_model()


def preload_model():
    print("Preparing models...")
    os.system(
        f"""curl http://localhost:11434/api/generate -d '{{\"model\": \"{config['LOCAL_MODEL']}\" , \"keep_alive\": \"15m\"}}'""")

    os.system(
        f"""curl http://localhost:11434/api/generate -d '{{\"model\": \"{config['RAG_MODEL']}\" , \"keep_alive\": \"15m\"}}'""")

    print("Model preloaded.")
    return


def get_llm_response(transcription, message_history, model_name='llama3:instruct', use_rag=True, GPIO=None):
    print("Here's what you said: ", transcription)
    transcription = remove_parentheses(transcription)
    use_rag_model = False
    if use_rag:
        predicted_tool = predict_tool(transcription, model, tokenizer)
        # Experimental idea for supplmenting with external data. Tool use may be better but this could start.
        if predicted_tool == 'check_weather':

            message_history = add_in_weather_data(
                message_history, transcription)
            use_rag_model = True
        elif predicted_tool == 'take_picture':
            response, message_history = generate_image_response(
                message_history, transcription)
            return response, message_history
        elif predicted_tool == 'check_news':
            message_history = add_in_news_data(message_history, transcription)
            use_rag_model = True
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

    stream = ollama.chat(model=model_name if not use_rag_model else config["RAG_MODEL"],
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

    try:
        newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
        top_headlines = newsapi.get_top_headlines(
            language='en',
            country='us')
    except:
        message_history.append({
            'role': 'user',
            'content': f"Can you tell me to check if the news tool is working?",
        })
        return message_history

    top_articles_str = ""
    for article in top_headlines['articles'][:3]:
        top_articles_str += article['title'] + "\n"

    top_articles_str = top_articles_str[:-1]

    prompt = f"""Here are some top news headlines as of today:

    {top_articles_str}

    Please answer the question below: 
    {transcription}
    """

    message_history.append({
        'role': 'user',
        'content': f"""{prompt}""",
    })
    return message_history


def generate_image_response(message_history, transcription):
    """
    Generate an image response.
    """
    if config['VISION_MODEL'] == 'none':
        response = "Camera is disabled. Please enable it if you want to use this feature."
        message_history.append({
            'role': 'user',
            'content': transcription,
        })
        message_history.append({
            'role': 'assistant',
            'content': response,
        })
        os.system(f"espeak '{response}'")

        return response, message_history

    elif config["VISION_MODEL"] == 'detr':
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
