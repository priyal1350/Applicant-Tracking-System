# Applicant Tracking System (ATS) Resume Expert

🚀 **Applicant Tracking System (ATS) Resume Expert** is a Streamlit-based web application designed to help job seekers optimize their resumes for Applicant Tracking Systems (ATS). It analyzes resumes against job descriptions using the **Google Gemini API**, providing insights into how well a resume matches a job description, suggests improvements, and ranks multiple resumes based on their compatibility.

---

## Features

- **Resume Analysis**: Upload your resume (PDF or Word) and get a detailed analysis of how well it matches a job description.
- **Job Description Fetching**: Paste a LinkedIn job URL to automatically fetch the job description.
- **Skill Improvement Suggestions**: Get actionable advice on how to improve your skills to better align with the job description.
- **Percentage Match**: See how well your resume matches the job description in percentage terms.
- **Rank Resumes**: Rank multiple resumes based on their compatibility with the job description.

---

## How to Use

```plaintext
### 1. **Clone the Repository**
   git clone https://github.com/your-username/Applicant-Tracking-System.git
   cd Applicant-Tracking-System

### 2. **Set Up Environment**
   - Create a .env file in the root directory and add your Google API key:
     GOOGLE_API_KEY=your_api_key_here

### 3. **Install Dependencies**
   Install the required Python packages:
   pip install -r requirements.txt

### 4. **Run the Application**
   streamlit run app.py

### 5. **Open the App**
   - The app will open in your browser at http://localhost:8501.

