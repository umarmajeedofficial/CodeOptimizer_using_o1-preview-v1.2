# openai.py
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"], base_url="https://api.aimlapi.com")

# Add any OpenAI-specific functions here if needed

