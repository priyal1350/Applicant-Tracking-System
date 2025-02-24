# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium and ChromeDriver
RUN apt-get update && apt-get install -y chromium-browser chromium-driver 

# Set environment variables for Selenium
ENV PATH="/usr/lib/chromium-browser/:${PATH}"

# Copy the rest of the application files
COPY . .

# Expose the port for Streamlit
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
