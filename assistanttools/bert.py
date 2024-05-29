from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification

key_tools = ['take_picture', 'no_tool_needed',
             'check_news', 'check_weather', 'play_spotify']


def get_id2tool_name(id, key_tools):
    return key_tools[id]


def remove_any_non_alphanumeric_characters(text):
    return ''.join(e for e in text if e.isalnum() or e.isspace())


if __name__ == "__main__":
    import time

    tokenizer = AutoTokenizer.from_pretrained("google-bert/bert-base-uncased")
    model = AutoModelForSequenceClassification.from_pretrained(
        "nkasmanoff/tool-bert")

    model.eval()

    questions = ["Who is the best captain in star trek", "tell me a joke",
                 'take a photo', 'check the weather', 'play some music', 'please tell me a joke', 'What is the news', 'When did the US declare independence', 'What is the capital of France', 'What is the capital of the United States', 'What is the capital of the United States of America',]
    for question in questions:

        start = time.time()
        question = remove_any_non_alphanumeric_characters(question)
        inputs = tokenizer(question, return_tensors="pt")

        outputs = model(**inputs)

        logits = outputs.logits
        stop = time.time()
        print(question)
        print(get_id2tool_name(logits.argmax().item(), key_tools))
        print(f"Time taken: {stop-start}")
        print('-----')
