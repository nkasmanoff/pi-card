# Pi-C.A.R.D

<img src="assets/assistant.png" height="200">
<img src="assets/assistant-gpio.png"  height="200">

## Table of Contents

-   [Demos](#demos)
-   [Introduction](#introduction)
-   [Usage](#usage)
-   [Hardware](#hardware)
-   [Setup](#setup)
-   [Roadmap](#roadmap)

## Demos

(Some better videos coming soon)

## Introduction

Pi-Card is an AI powered assistant running entirely on a Raspberry Pi. It is capable of doing anything a standard LLM (like ChatGPT) can do in a conversational setting.
In addition, if there is a camera equipped, you can also ask Pi-card to take a photo, describe what it sees, and then ask questions about that image.

### Why Pi-card?

Raspberry **Pi** - **C**amera **A**udio **R**ecognition **D**evice.

<img src="assets/picard-facepalm.jpg" height="300">

Please submit an issue or pull request if you can think of a better way to force this acronym.

### How does it work?

Pi-Card runs entirely on your Raspberry Pi.

**With a wake word**. Once the `main.py`, the system will listen for your wake word. Once your wake word has been said, you are officially in a conversation. Within this conversation you do not need to constantly repeat the wake word. The system will continue to listen for your commands until you say something like "stop", "exit", or "goodbye".

**With a button**. If you can get your hands on a breadboard, some wires, and a button, using a button to to handle the conversation is a much smoother (in my experience) way to interact. This is done by pressing the button, and then speaking your command. The button is a simple GPIO button, and can be set up by following the instructions in the `main_button.py` file.

The chatbot has a configurable memory of the conversation, meaning if you want the assistant to repeat something it said, or elaborate on a previous topic, you can do so. For quicker responses, you can set the memory to a smaller number in the `config.py` file.

### How useful is it?

The system is designed to be a fun project that can be a _somewhat_ helpful AI assistant. Since everything is done locally, the system will not be as capable, or as fast, as cloud based systems. However, the system is still capable of a lot of improvements to be made.

### Why isn't this an app?

The main reason for this is that I wanted to create a voice assistant that is completely offline and doesn't require any internet connection. This is mostly because I wanted to ensure that the user's privacy is protected and that the user's data is not being sent to any third party servers. I also want to know how capable voice assistants can be in a completely offline setting.

## Usage

After downloading the repository, installing the requirements, and following the other setup instructions, you can run the main program by running the following command:

```bash
python main.py
```

or

```bash
python main_button.py
```

Once the program is running, you can start a conversation with the assistant by saying the wake word. The default wake word is "hey assistant", but you can change this in the `config.py` file. If the button version is in place, you can press the button to start a conversation, or interrupt the assistant at any time.

## Setup

### Software

To keep this system as fast and lean as possible, we use cpp implementations of the audio transcription and vision language models. These are done with the wonderful libraries [whisper.cpp](https://github.com/ggerganov/whisper.cpp) for the audio transcription and [llama.cpp](https://github.com/ggerganov/llama.cpp) for the vision language model.

In both cases, please clone these repositories wherever you like, and add their paths to the `config.py` file.

Once cloned, please go to each repository, and follow the setup instructions to get the models running. Some pointers are given below:

For llama.cpp, we are using the vision language model capabilities, which are slightly different from the standard setup. You will need to follow the setup instructions for [LlaVA](https://github.com/ggerganov/llama.cpp/blob/master/examples/llava/README.md), but update the model to be used to be one better suited for this device, [Moondream2](https://moondream.ai)

To install Moondream, you'll need to go to HuggingFace model hub, and download the model. I did so using python, with the following commands. Once again, make sure the vision model path is added to the `config.py` file.

```python
from huggingface_hub import snapshot_download
model_id="vikhyatk/moondream2"
snapshot_download(repo_id=model_id, local_dir=your/local/path, local_dir_use_symlinks=False, revision="main")
```

#### Tools

To make pi-card a bit more like a real assistant, there are a couple tools it has access to. These are done through [tool-bert](https://huggingface.co/nkasmanoff/tool-bert), a fine-tuned version of BERT deciding when to access external info. More info on how to make a version of this can be found [here](https://github.com/nkasmanoff/tool-bert)

The model is easy to install, but to enable tool access, take a look at .env.example file for context on what keys and secrets are necessary.

For whisper.cpp, you will need to follow the quick-start guide in the [README](https://github.com/ggerganov/whisper.cpp?tab=readme-ov-file#quick-start).

Since this project is depending on openly available models, depending on the ones used, the limitations of this assistant will be the same as limitations of the models.

### Hardware

The hardware setup is quite simple. You will need a Raspberry Pi 5 Model B, a USB microphone, a speaker, and a camera.

The USB microphone and speaker can be plugged into the Raspberry Pi's USB ports. The camera can be connected to the camera port on the Raspberry Pi.

I used the following hardware for my setup:

-   [Raspberry Pi 5 Kit](https://www.amazon.com/dp/B0CRSNCJ6Y?psc=1&ref=ppx_yo2ov_dt_b_product_details)
-   [USB Microphone](https://www.amazon.com/dp/B087PTH787?psc=1&ref=ppx_yo2ov_dt_b_product_details)
-   [Speaker](https://www.amazon.com/dp/B075M7FHM1?ref=ppx_yo2ov_dt_b_product_details&th=1)
-   [Camera](https://www.amazon.com/dp/B012V1HEP4?ref=ppx_yo2ov_dt_b_product_details&th=1)
-   [Camera Connector](https://www.amazon.com/dp/B0716TB6X3?psc=1&ref=ppx_yo2ov_dt_b_product_details)
-   [Button](https://www.amazon.com/DIYables-Button-Arduino-ESP8266-Raspberry/dp/B0BXKN4TY6)
-   [Breadboard](https://www.amazon.com/dp/B09VKYLYN7?psc=1&ref=ppx_yo2ov_dt_b_product_details)

Please note Pi 5's have a new camera port, hence the new camera connector. At the same time, while this project is focused on making this work on a Raspberry Pi 5, it should
work on other devices as well.

For setting up the GPIO button, I found the first couple minutes of [this tutorial](https://youtu.be/IHvtJvgM_eQ?si=VZzhElu5yYTt7zcV) great.

Feel free to use your own, this is what worked for me!

## Benchmarks

This table is a VERY approximate benchmark of the response times of various models.

### Transcription Models

| Model             | Load Time | Total Time |
| ----------------- | --------- | ---------- |
| Whisper Tiny (en) | 0.113s    | 1.76s      |
| Whisper Base (en) | 0.159s    | 3.36s      |

### Large Language Models

Since this one varies based on how large the conversation / response is, just putting the approximate tokens per second metrics here.

| Model                                                                                | Prompt     | Eval      | ~ Time to Respond |
| ------------------------------------------------------------------------------------ | ---------- | --------- | ----------------- |
| [Phi 3 Instruct](https://ollama.com/library/phi3:instruct) (3B) (Q4_0)               | 4.65 tok/s | 3.8 tok/s | 3.5s              |
| [Llama 3 Instruct](https://ollama.com/library/llama3.1:8b-instruct-q4_0) (8B) (Q4_0) | 2.37s      | 2.00s     | 5.0s              |
| [Qwen2 Instruct](https://ollama.com/library/qwen2:1.5b-instruct) (1.5B) (Q4_0)       | -          | -         | 1.0s              |
| [Picard](https://ollama.com/noahpunintended/picard) (0.5B) (fp16)                    | -          | -         | 0.9s              |

(time to respond ~= prompt eval duration)

### Vision Language Model

| Model      | Load Image In Context Time | Start Generating Time |
| ---------- | -------------------------- | --------------------- |
| Moondream2 | 62s                        | 3.5s                  |

Meaning that for vision language models, the biggest bottleneck is loading all of the "silent" image tokens in the llm memory. For moondream, this is 729 image tokens, so understandable it takes a bit of time.

This is the May revision of Moondream2, I haven't used it much recently, but if this model is changed to use pooling layers, it's latency should drop significantly and it would be a huge improvement.

## Overclocking

Do this at your own risk!

One way I have found to speed up all of the numbers above is by overclocking my Raspberry Pi. You can do so by following the instructions [here](https://www.tomshardware.com/how-to/overclock-raspberry-pi-5). I would NOT recommend going all the way up to 3.0 GHz, and it is possible your machine won't even let you do so. I have only managed to raise mine to 2.6 GHz, it has crashed once, but otherwise works, and speeds up all the benchmarks above in what I think is roughly proportional to the improved clock speed.

I would recommend doing this if you are comfortable with the chance of burning out the device, extra power consumption. Make sure you have a good cooling system in place.

## Roadmap

Coming soon, but I plan to add notes here on things currently implemented, and what can be done in the future. Some quick notes on it are below

-   [x] Basic conversation capabilities
-   [x] Camera capabilities
-   [x] Benchmark response times
-   [x] Test overclocking
-   [x] Figure out how to speed up whisper times
-   [x] Add more external services
-   [x] Add ability to interrupt assistant, and ask new question
-   [x] Use a custom tuned model
-   [ ] New YouTube videos
-   [ ] Use a moondream model with image token pooling
-   [ ] Improve external service function model (tool-bert)
-   [ ] Test when connected to a portable power source
-   [ ] Formal write-up of how I did fine-tuning and porting over (since I already forgot how)
-   [ ] Dockerize repo for testing on more devices


## Building the Docker Image

To build the Docker image, navigate to the directory containing the Dockerfile and run the following command:

```bash
sudo docker build -t pi-card .
```

## Running the Docker Container (recommended)

To run the Docker container via `docker compose`, run the following command:

```bash
sudo docker compose up
```

## Running the Docker Container (not recommended)

To run the Docker container, run the following command:

```bash
sudo docker run -it --device /dev/snd pi-card
```
