import streamlit as st
import ollama
from config import config

# https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
st.title("Pi-CARD Chat")


def generate_response():
    use_rag_model = False
    response = ollama.chat(
        model=config["LOCAL_MODEL"] if not use_rag_model else config["RAG_MODEL"],
        stream=True,
        messages=st.session_state.messages,
    )
    for partial_resp in response:
        token = partial_resp["message"]["content"]
        st.session_state["full_message"] += token
        yield token


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": config["SYSTEM_PROMPT"],
        }
    ]

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
        {"role": "assistant", "content": st.session_state["full_message"]}
    )
