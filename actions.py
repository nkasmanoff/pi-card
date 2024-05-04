import ollama
import os

message_history = [{
    'role': 'system',
    'content': 'You are a helpful AI voice assistant. Replies should be no more than two sentences.',
}]


def get_llm_response(transcription, message_history, streaming=True, model_name='phi3:instruct', max_spoken_tokens=300):
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
            streaming_word += text_chunk

            response += text_chunk

            if i > max_spoken_tokens:
                continue
            if ' ' in streaming_word:
                streaming_word_clean = streaming_word.replace(
                    '"', "").replace("\n", " ").replace("'", "").replace("*", "").replace('-', '').replace(':', '')

                os.system(f"espeak '{streaming_word_clean}'")
                streaming_word = ""

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
