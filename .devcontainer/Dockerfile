FROM mcr.microsoft.com/devcontainers/python:3.12

# Ensures logs are flushed straight to terminal
ENV PYTHONUNBUFFERED=1

# Install useful system tools
RUN sudo apt-get update && sudo apt-get install -y \
    curl \
    poppler-utils \
    git \
    && sudo rm -rf /var/lib/apt/lists/*

# Install Node.js (v20 LTS)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Upgrade pip
RUN pip install --upgrade pip
