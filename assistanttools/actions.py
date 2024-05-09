import ollama
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

message_history = [{
    'role': 'system',
    'content': 'You are a helpful AI voice assistant hosted on a Raspberry Pi.',
}]

sentence_stoppers = ['. ', '.\n', '? ', '! ', '?\n', '!\n', '.\n']


def preload_model(model_name="llama3:instruct"):
    print("Preparing model...")
    os.system(
        f"curl http://localhost:11434/api/chat -d '{{\"model\": \"{model_name}\"}}'")

    print("Model preloaded.")
    return


def get_llm_response(transcription, message_history, streaming=True, model_name='llama3:instruct', max_spoken_tokens=300, use_rag=True, condense_messages=True):

    if condense_messages:
        message_history = [message_history[0]]

    if use_rag:
        # Experimental idea for supplmenting with external data. Tool use may be better but this could start.
        if 'weather' in transcription:
            os.system(f"espeak 'Getting weather data.'")
            message_history = add_in_weather_data(
                message_history, transcription)
        elif "news" in transcription:
            os.system(f"espeak 'Getting news data.'")
            message_history = add_in_news_data(message_history, transcription)

        else:
            message_history.append({
                'role': 'user',
                'content': transcription,
            })

    print("Now asking llm...")
    if streaming:
        num_sentences = 0
        stream = ollama.chat(model=model_name,
                             stream=True, messages=message_history)
        early_stopping = False
        response = ""
        streaming_word = ""
        for i, chunk in enumerate(stream):
            text_chunk = chunk['message']['content']
            print(text_chunk)
            streaming_word += text_chunk

            response += text_chunk

            if i > max_spoken_tokens:
                continue
            if ' ' in streaming_word:
                streaming_word_clean = streaming_word.replace(
                    '"', "").replace("\n", " ").replace("'", "").replace("*", "").replace('-', '').replace(':', '').replace('!', '')
                os.system(f"espeak '{streaming_word_clean}'")
                streaming_word = ""

            if any(p in response for p in sentence_stoppers) and num_sentences < 1:
                num_sentences += 1

        if not early_stopping:
            os.system(f"espeak '{streaming_word}'")

    else:

        response = ollama.chat(model='phi3:instruct',
                               stream=False, messages=message_history)
        response = response['message']['content']

        clean_response = response.replace(
            '"', "").replace("\n", " ").replace("'", "").replace("*", "")

        os.system(f"espeak '{clean_response}'")

    message_history.append({
        'role': 'assistant',
        'content': response,
    })

    return response, message_history


def check_if_word(text_chunk):
    """
    Given the subword outputs from streaming, as these chunks are added together, check if they form a coherent word. If so, return the word.
    """
    if ' ' in text_chunk:
        return text_chunk
    return ""


def add_in_weather_data(message_history, transcription):
    """
    Add in weather data to the message history.
    """

    api_key = os.getenv("TOMORROWIO_API_KEY")
    headers = {"accept": "application/json"}

    rt_url = f"https://api.tomorrow.io/v4/weather/realtime?location=new%20york&apikey={api_key}"
    rt_response = requests.get(rt_url, headers=headers)
    data = rt_response.json()['data']
    time = data['time']
    temp = data['values']['temperature']
    humidity = data['values']['humidity']
    precipitation = data['values']['precipitationProbability']
    cloudCover = data['values']['cloudCover']

    location = rt_response.json()['location']['name']

    message_history.append({
        'role': 'user',
        'content': f"""Here is the current weather data:        

        Location: {location}
        Time: {time}
        Temperature: {temp} C 
        Humidity: {humidity}%
        Precipitation Probability: {precipitation}%
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
    for n in news[:5]:
        top_articles += n.text + "\n"

    message_history.append({
        'role': 'user',
        'content': f"""Here are the top articles on HackerNews:        

        {top_articles}

        
        Question:
        Can you summarize what they are for me?

        Answer:
        """,
    })
    return message_history


def generate_image_response(model_name, transcription):
    """
    Generate an image response.
    """
    pass
