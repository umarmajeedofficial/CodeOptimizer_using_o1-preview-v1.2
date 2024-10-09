# llama.py
from together import Together
from openai import OpenAI

# Initialize the clients for the models with API keys from Streamlit secrets
together_client = Together(base_url="https://api.aimlapi.com/v1", api_key=st.secrets["together"]["api_key"])
openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"], base_url="https://api.aimlapi.com")

def generate_code(user_question, language):
    # Your existing generate_code logic here

def break_down_problem(user_question):
    # Your existing break_down_problem logic here

def explain_code(code):
    # Your existing explain_code logic here

