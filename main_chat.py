import streamlit as st
import ollama
from config import config
from assistanttools.actions import preload_model, predict_tool, add_in_weather_data, add_in_news_data, generate_image_response, play_spotify
# https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
st.title("Pi-CARD Chat")

def generate_response():
    use_rag_model = False
    message = st.session_state.messages[-1]["content"]
    predicted_tool = predict_tool(message)

    if predicted_tool == 'check_weather':
        st.session_state.messages = add_in_weather_data(
            st.session_state.messages, message)
        use_rag_model = True
    elif predicted_tool == 'take_picture':
        response, st.session_state.messages = generate_image_response(
            st.session_state.messages, message)
        yield response
    elif predicted_tool == 'check_news':
        st.session_state.messages = add_in_news_data(
            st.session_state.messages, message)
        use_rag_model = True
    elif predicted_tool == 'play_spotify':
        response, st.session_state.messages = play_spotify(
            message, st.session_state.messages)
        yield response

    response = ollama.chat(model=config["LOCAL_MODEL"] if not use_rag_model else config["RAG_MODEL"],
                        stream=True, messages=st.session_state.messages)
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        st.session_state["full_message"] += token
        yield token


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{
        'role': 'system',
        'content': f'{config['SYSTEM_PROMPT']}',
    }]

for i, msg in enumerate(st.session_state.messages):
    if i == 0:
        continue
    if msg["role"] == "user":
        st.chat_message(msg["role"], avatar="🧑‍💻").write(msg["content"])
    else:
        st.chat_message(msg["role"], avatar="🐈").write(msg["content"])


if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user", avatar="🧑‍💻").write(prompt)
    st.session_state["full_message"] = ""
    st.chat_message("assistant", avatar="🐈").write_stream(generate_response)
    st.session_state.messages.append(
        {"role": "assistant", "content": st.session_state["full_message"]})
