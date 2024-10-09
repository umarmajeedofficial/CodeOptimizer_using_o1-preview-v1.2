import streamlit as st
import json
import os
from together import Together
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob

# Initialize the clients for the models with API keys from Streamlit secrets
together_client = Together(base_url="https://api.aimlapi.com/v1", api_key=st.secrets["together"]["api_key"])
openai_client = OpenAI(api_key=st.secrets["openai"]["api_key"], base_url="https://api.aimlapi.com")

# File to store feedback
FEEDBACK_FILE = 'feedback_data.json'

# Load existing feedback if available
def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return []

# Save feedback to the file
def save_feedback(feedback):
    existing_feedback = load_feedback()
    existing_feedback.append(feedback)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(existing_feedback, f, indent=4)

# Function to perform sentiment analysis on comments
def analyze_sentiment(comment):
    blob = TextBlob(comment)
    sentiment = blob.sentiment.polarity  # Value between -1 and 1
    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Negative"
    else:
        return "Neutral"

def generate_code(user_question, language):
    response = together_client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        messages=[{"role": "user", "content": user_question}],
        max_tokens=1000,
    )
    
    llama_response = response.choices[0].message.content.strip()
    
    if "?" in llama_response:
        return llama_response, True  # Ambiguous response, needs clarification

    processed_string = llama_response.replace('"', '').replace("'", '').replace('\n', ' ')
    
    instruction = (
        f"As a highly skilled software engineer, please analyze the following question thoroughly and provide optimized "
        f"{language} code for the problem: {processed_string}. Make sure to give only code."
    )
    
    openai_response = openai_client.chat.completions.create(
        model="o1-preview",
        messages=[{"role": "user", "content": instruction}],
        max_tokens=10000,
    )

    code = openai_response.choices[0].message.content.strip()
    return code, False  # No ambiguity

def break_down_problem(user_question):
    instruction = (
        f"Please break down the following question into smaller, manageable parts:\n\n{user_question}"
    )
    
    response = openai_client.chat.completions.create(
        model="o1-preview",
        messages=[{"role": "user", "content": instruction}],
        max_tokens=1000,
    )

    breakdown = response.choices[0].message.content.strip()
    return breakdown

def explain_code(code):
    instruction = (
        f"As a highly skilled software engineer, please provide a detailed line-by-line explanation of the following code:\n\n"
        f"{code}\n\nMake sure to explain what each line does and why it is used."
    )
    
    openai_response = openai_client.chat.completions.create(
        model="o1-preview",
        messages=[{"role": "user", "content": instruction}],
        max_tokens=10000,
    )

    explanation = openai_response.choices[0].message.content.strip()
    return explanation

def analyze_feedback(feedback_data):
    df = pd.DataFrame(feedback_data)
    feedback_summary = df.groupby('feedback').size().reset_index(name='count')
    
    # Sentiment Analysis
    df['sentiment'] = df['comments'].apply(analyze_sentiment)
    sentiment_summary = df['sentiment'].value_counts().reset_index()
    sentiment_summary.columns = ['sentiment', 'count']

    return feedback_summary, sentiment_summary

# Dropdown menu for programming languages
languages = ["Python", "Java", "C++", "JavaScript", "Go", "Ruby", "Swift"]

# Create the Streamlit interface
st.set_page_config(page_title="Optimized Code Generator", layout="wide")

st.markdown("<h1 style='text-align: center;'>Optimized Code Generator</h1>", unsafe_allow_html=True)

# Create a sidebar layout for inputs
st.sidebar.title("Input Section")

# Sidebar inputs
language = st.sidebar.selectbox("Select Programming Language:", options=languages, index=0)

# Main area for generated code and question input
st.subheader("Generated Code:")
code_container = st.empty()  # Placeholder for generated code

# Use a container to allow scrolling
with st.container():
    # Create a placeholder for the input field at the bottom
    user_question = st.text_area("Enter your question:", placeholder="Type your question here...", height=150)
    
    # Submit button at the bottom of the main content
    if st.button("Submit"):
        with st.spinner("Thinking..."):
            # Check for ambiguities first
            code, ambiguous = generate_code(user_question, language)
            
            if ambiguous:
                # If ambiguous, break down the problem
                breakdown = break_down_problem(user_question)
                st.sidebar.text_area("Ambiguity Detected:", value=breakdown, height=200, disabled=True)
            else:
                explanation = explain_code(code)  # Get explanation using O1 model
                
                # Display the generated code
                code_container.code(code, language=language.lower())
                
                # Set the explanation output in the sidebar
                st.sidebar.text_area("Code Explanation:", value=explanation, height=200, disabled=True)

                # Feedback section
                st.subheader("Feedback Section")
                feedback_col1, feedback_col2 = st.columns([1, 2])  # Use columns for layout
                
                with feedback_col1:
                    st.markdown("**Was the generated code clear?**")
                    feedback = st.selectbox("", options=["Select Feedback", "👍 Yes", "👎 No"], index=0)
                
                with feedback_col2:
                    feedback_comments = st.text_area("Additional Comments:", placeholder="Any additional feedback?", height=100)
                
                if st.button("Submit Feedback"):
                    feedback_entry = {
                        "question": user_question,
                        "code": code,
                        "explanation": explanation,
                        "feedback": feedback,
                        "comments": feedback_comments
                    }
                    save_feedback(feedback_entry)  # Store feedback in the file
                    st.success("Thank you for your feedback!")

# Feedback Analysis Section
st.subheader("Feedback Analysis")

if st.button("Show Feedback Analysis"):
    feedback_data = load_feedback()
    if feedback_data:
        feedback_summary, sentiment_summary = analyze_feedback(feedback_data)
        
        # Create a bar chart for feedback
        plt.figure(figsize=(8, 5))
        plt.bar(feedback_summary['feedback'], feedback_summary['count'], color=['green', 'red'])
        plt.title('Feedback Summary')
        plt.xlabel('Feedback')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        st.pyplot(plt)

        # Create a bar chart for sentiment analysis
        plt.figure(figsize=(8, 5))
        plt.bar(sentiment_summary['sentiment'], sentiment_summary['count'], color=['blue', 'orange', 'gray'])
        plt.title('Sentiment Analysis of Comments')
        plt.xlabel('Sentiment')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        st.pyplot(plt)

    else:
        st.warning("No feedback available for analysis.")

# Custom CSS to enhance the UI
st.markdown("""
<style>
    .streamlit-expanderHeader {
        font-size: 18px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        width: 100%;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
    }
    h1 {
        color: #4CAF50;
    }
    h2 {
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

