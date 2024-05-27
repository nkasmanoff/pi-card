# Use an official Python runtime as a parent image
FROM debian:latest

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install git, curl, and make
RUN apt-get update && apt-get install -y \
build-essential \
cmake \
curl \
espeak \
git \
libsndfile1 \
make \
portaudio19-dev \
python3 \
python3-pip \
python3-venv

# Create a virtual environment and activate it
RUN python3 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# hack to make python3 the default python
RUN ln -s /app/venv/bin/python3 /app/venv/bin/python

# Verify installations
RUN python --version
RUN pip --version
RUN g++ --version

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download the Moondream model
# RUN python download_moondream_model.docker.py

# TODO Build llama with moondream model?
# Clone the whisper.cpp and llama repositories
RUN git clone https://github.com/ggerganov/whisper.cpp
# RUN git clone https://github.com/ggerganov/llama.cpp
# RUN git clone https://github.com/vikhyat/moondream

# Download the whisper.cpp model
# RUN bash /app/whisper.cpp/models/download-ggml-model.sh base.en

# Build whisper.cpp
RUN cd /app/whisper.cpp && make

# Build llama.cpp
# RUN cd /app/llama.cpp && make && make llama-cli
# RUN cd /app/llama.cpp && make

# RUN cd /app

# Run app.py when the container launches
CMD ["python", "main.py"]
