# Use an official Python runtime as a parent image
FROM debian:latest

RUN apt-get update && apt-get install -y \
alsa-base alsa-utils
RUN aplay -l
RUN arecord -l

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

# Verify installations
RUN python --version
RUN pip --version
RUN g++ --version

# Install ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Clone the whisper.cpp and llama repositories
RUN git clone https://github.com/ggerganov/whisper.cpp
RUN cd /app/whisper.cpp && make

# Copy the start script into the Docker image and make it executable
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Run start.sh when the container launches
CMD ["/app/start.sh"]