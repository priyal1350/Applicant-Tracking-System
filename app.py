from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re
import PyPDF2  # For extracting text from PDF
from docx import Document  # For extracting text from Word files
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("Google API key is missing. Please check your .env file.")
    st.stop()  # Stop the app if the API key is missing
try:
    genai.configure(api_key=google_api_key)
except Exception as e:
    st.error(f"Failed to configure Gemini API: {e}")
    st.stop()  # Stop the app if configuration fails

# Functions
@st.cache_data
def input_file_setup(uploaded_file):
    if uploaded_file is not None:
        # Validate file type
        if uploaded_file.type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            st.error(f"Invalid file type: {uploaded_file.type}. Please upload a valid PDF or Word file.")
            return None
        
        try:
            # Extract text based on file type
            if uploaded_file.type == "application/pdf":
                # Extract text from PDF using PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            else:
                # Extract text from Word file using python-docx
                doc = Document(uploaded_file)
                text = "\n".join([para.text for para in doc.paragraphs])
            
            # Convert text to base64 (for compatibility with the rest of the code)
            text_bytes = text.encode('utf-8')
            file_parts = [
                {
                    "mime_type": "text/plain",
                    "data": base64.b64encode(text_bytes).decode()
                }
            ]
            return file_parts
        except Exception as e:
            st.error(f"Failed to process the file: {e}")
            return None
    else:
        raise FileNotFoundError("No file uploaded")

def get_gemini_response(input, file_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, file_content[0], prompt])
    return response.text

def make_links_clickable(response):
    url_pattern = r'(https?://[^\s]+)'
    clickable_text = re.sub(url_pattern, r'[\1](\1)', response)
    return clickable_text

def scrape_linkedin_job(url):
    # Set up Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Automatically download and set up ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the LinkedIn job URL
        logger.info("Fetching job description from LinkedIn...")
        driver.get(url)
        driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to load

        # Get the page source (fully rendered HTML)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extract job description
        job_description = soup.find('div', {'class': re.compile(r'description__text|jobs-description__content')})
        if job_description:
            # Extract only the job description text
            description_text = job_description.get_text(strip=True)
            
            # Remove unwanted sections (e.g., "How to Apply", "Note", etc.)
            unwanted_sections = ["How to Apply", "Note", "Submit your application by", "About Unified Mentor"]
            for section in unwanted_sections:
                description_text = description_text.split(section)[0].strip()
            
            return description_text
        else:
            return "Unable to fetch job description. Please check the URL or enter the job description manually."
    except Exception as e:
        return f"Failed to fetch job description: {e}"
    finally:
        driver.quit()

def fetch_job_description(url):
    if "linkedin.com" in url:
        try:
            job_description = scrape_linkedin_job(url)
            if job_description.startswith("Unable") or job_description.startswith("Failed"):
                st.warning(job_description)
                return ""
            return job_description
        except Exception as e:
            st.error(f"Failed to fetch job description: {e}")
            return ""
    else:
        st.warning("Unsupported platform. Please paste a LinkedIn job URL.")
        return ""

# Function to extract name from resume text using Gemini API
def extract_name_from_resume(text):
    prompt = """
    Extract the candidate's name from the following resume text. Return only the name:
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt, text])
    return response.text.strip()

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

# Sidebar for instructions
st.sidebar.title("Instructions")
st.sidebar.markdown("""
1. Paste a LinkedIn job URL or manually enter the job description.
2. Upload one or more resumes in PDF or Word format.
3. Click one of the buttons to analyze your resume(s).
""")

# Job Description Input
job_url = st.text_input("Paste LinkedIn Job URL (optional):")
if job_url:
    # Fetch job description from LinkedIn URL
    job_description = fetch_job_description(job_url)
    input_text = st.text_area("Job Description:", value=job_description, key="input")
else:
    # Allow manual input if no URL is provided
    input_text = st.text_area("Job Description:", key="input")

# Resume Upload (Multiple Files)
uploaded_files = st.file_uploader("Upload your resume(s) (PDF or Word)...", type=["pdf", "docx"], accept_multiple_files=True)

# Extract names from resumes
resume_names = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_content = input_file_setup(uploaded_file)
        if file_content:
            text = base64.b64decode(file_content[0]["data"]).decode('utf-8')
            name = extract_name_from_resume(text)
            resume_names.append(name if name else "Unnamed Resume")

# Buttons
submit1 = st.button("Tell Me About the Resume(s)")
submit2 = st.button("How Can I Improvise my Skills")
submit3 = st.button("Percentage match and Rank Resumes")

# Prompts
input_prompt1 = """
You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
You are an expert career counselor with a deep understanding of the job market, skill development, and online certifications. 
Your task is to evaluate the resume and suggest how the candidate can improve their skills to better align with the job description. 
Provide specific certifications, online courses (with clickable links), or skill improvement strategies that can help the candidate.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. Your response MUST start with the percentage in the format "Percentage Match: X%", where X is the percentage.
Then, list the keywords missing and finally provide your thoughts.
"""

# Function to extract percentage from response
def extract_percentage(response):
    # Search for a percentage value in the response
    match = re.search(r'Percentage Match: (\d+)%', response)
    if match:
        return float(match.group(1))
    return 0  # Default to 0 if no percentage is found

# Function to rank resumes based on match percentage
def rank_resumes(resume_responses):
    ranked_resumes = sorted(
        resume_responses.items(),
        key=lambda x: x[1]['percentage'] if x[1]['percentage'] is not None else 0,
        reverse=True
    )
    return ranked_resumes

# Display responses
def display_response(submit_button, prompt, input_text, uploaded_files, resume_names, success_message):
    if submit_button:
        if uploaded_files:
            resume_responses = {}
            progress_bar = st.progress(0)
            for i, uploaded_file in enumerate(uploaded_files):
                progress_bar.progress((i + 1) / len(uploaded_files))
                with st.spinner(f"Processing {resume_names[i]}..."):
                    file_content = input_file_setup(uploaded_file)
                    if file_content is None:
                        continue  # Skip invalid files
                    response = get_gemini_response(prompt, file_content, input_text)
                    
                    # Extract percentage only for input_prompt3
                    if prompt == input_prompt3:
                        percentage = extract_percentage(response)
                    else:
                        percentage = None  # No percentage for other prompts
                    
                    resume_responses[resume_names[i]] = {
                        "response": response,
                        "percentage": percentage
                    }
            
            if submit3:  # Rank resumes for percentage match
                ranked_resumes = rank_resumes(resume_responses)
                st.subheader("Ranked Resumes:")
                for rank, (resume, data) in enumerate(ranked_resumes, start=1):
                    st.write(f"{rank}. {resume} - Match Percentage: {data['percentage']}%")
                    st.markdown(data['response'])
                    st.download_button(
                        label=f"Download Analysis for {resume}",
                        data=data['response'],
                        file_name=f"{resume}_analysis.txt",
                        mime="text/plain"
                    )
            else:
                for resume, data in resume_responses.items():
                    st.subheader(f"{resume} - {success_message}")
                    st.markdown(data['response'])
                    st.download_button(
                        label=f"Download Analysis for {resume}",
                        data=data['response'],
                        file_name=f"{resume}_analysis.txt",
                        mime="text/plain"
                    )
        else:
            st.write("Please upload the resume(s).")

display_response(submit1, input_prompt1, input_text, uploaded_files, resume_names, "The Response is")
display_response(submit2, input_prompt2, input_text, uploaded_files, resume_names, "Suggestions for Improvement:")
display_response(submit3, input_prompt3, input_text, uploaded_files, resume_names, "The Response is")

# Reset button
if st.button("Reset"):
    st.experimental_rerun()