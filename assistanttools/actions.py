import ollama
import os
import requests
from dotenv import load_dotenv
load_dotenv()

message_history = [{
    'role': 'system',
    'content': 'You are a helpful AI voice assistant. Replies should be no more than two sentences.',
}]


def get_llm_response(transcription, message_history, streaming=True, model_name='mistral:instruct', max_spoken_tokens=300, use_rag=True):
    if use_rag:
        # Experimental idea for supplmenting with external data. Tool use may be better but this could start.
        if 'weather' in transcription:
            print("using tool")
            message_history = add_in_weather_data(
                message_history, transcription)
        else:
            message_history.append({
                'role': 'user',
                'content': transcription,
            })
    print("Now asking llm...")
    if streaming:

        stream = ollama.chat(model=model_name,
                             stream=True, messages=message_history)

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
                    '"', "").replace("\n", " ").replace("'", "").replace("*", "").replace('-', '').replace(':', '')

                os.system(f"espeak '{streaming_word_clean}'")
                streaming_word = ""

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
    location = rt_response.json()['location']['name']

    message_history.append({
        'role': 'user',
        'content': f"""Here is the current weather data. Use this to answer my questions: 
        
        Location: {location}
        Time: {time}
        Temperature: {temp} degrees Celsius
 
        Question:
        {transcription}
        """,
    })
    return message_history
