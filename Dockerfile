# Use official Python image as base
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy the application files into the container
COPY . .

# Install system dependencies for Selenium (Chrome + Driver)
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
