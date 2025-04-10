# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (fixes Chrome errors)
RUN apt-get update && apt-get install -y \
    wget curl unzip xdg-utils libnss3 libgconf-2-4 fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome and ChromeDriver (fixed with proper dependencies)
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb

RUN CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip \
    && unzip chromedriver_linux64.zip -d /usr/local/bin/ \
    && rm chromedriver_linux64.zip \
    && chmod +x /usr/local/bin/chromedriver

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose the port for Streamlit
EXPOSE $PORT

# Run the application (fixed for Render)
CMD streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
