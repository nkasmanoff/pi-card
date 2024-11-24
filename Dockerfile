# Use an official Python runtime as a parent image
FROM debian:latest

# Install all system dependencies in one layer
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    libsndfile1 \
    ffmpeg \
    cmake \
    pkg-config \
    libgpiod2 \
    python3-full \
    python3-pip \
    python3-venv \
    alsa-utils \
    libasound2 \
    libasound2-plugins \
    wget \
    gcc \
    swig \
    libmariadb-dev \
    libasound2-dev \
    pulseaudio \
    pulseaudio-utils \
    && rm -rf /var/lib/apt/lists/*

# Set audio environment variables for USB Audio (card 2)
# Note these are hardcoded for the USB Audio device and where you plug it in (check aplay -l)
ENV AUDIODEV=plughw:2,0  
ENV AUDIODRIVER=alsa
ENV PULSE_SERVER=/run/user/1000/pulse/native
ENV ALSA_CARD=2  

# Create ALSA configuration for USB Audio
RUN echo 'pcm.!default { \n\
    type plug \n\
    slave.pcm "hw:2,0" \n\
    }\n\
    \n\
    ctl.!default { \n\
    type hw \n\
    card 2 \n\
    }' > /etc/asound.conf

# Configure espeak-specific environment
ENV ESPEAK_AUDIO_OUTPUT=alsa
ENV ESPEAK_RATE=175
ENV ESPEAK_VOICE=en

# Set working directory
WORKDIR /app

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Create and activate virtual environment
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip
# Install Python dependencies in the virtual environment
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install RPi.GPIO



# Create necessary directories

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV SOUNDS_PATH=/app/sounds/
ENV WHISPER_CPP_PATH=/app/whisper.cpp/
ENV MOONDREAM_PATH=/app/moondream-quants/

# Clone and build whisper.cpp
RUN git clone https://github.com/ggerganov/whisper.cpp.git && \
    cd whisper.cpp && \
    make && \
    chmod +x main

# Create a symbolic link to make it accessible
RUN ln -s /app/whisper.cpp/main /usr/local/bin/whisper

# Download whisper tiny model
RUN cd whisper.cpp/models && \
    ./download-ggml-model.sh tiny.en


# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]