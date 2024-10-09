import streamlit as st
import json
import os
from together import Together
from openai import OpenAI
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import time
import streamlit.components.v1 as components

# Initialize the clients for the models with API keys from Streamlit secrets
together_client = Together(
    base_url="https://api.aimlapi.com/v1",
    api_key=st.secrets["together"]["api_key"]
)
openai_client = OpenAI(
    api_key=st.secrets["openai"]["api_key"],
    base_url="https://api.aimlapi.com"  # Keeping the original base URL as per your setup
)

# File to store feedback
FEEDBACK_FILE = 'feedback_data.json'

# Load existing feedback if available
def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("Error decoding the feedback file. It might be corrupted.")
            return []
    return []

# Save feedback to the file
def save_feedback(feedback):
    existing_feedback = load_feedback()
    existing_feedback.append(feedback)
    try:
        with open(FEEDBACK_FILE, 'w') as f:
            json.dump(existing_feedback, f, indent=4)
    except IOError:
        st.error("Error saving feedback. Please try again.")

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
    try:
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
            max_tokens=1000,  # Adjusted to a reasonable token limit
        )

        code = openai_response.choices[0].message.content.strip()
        return code, False  # No ambiguity
    except Exception as e:
        st.error(f"Error generating code: {e}")
        return "", False

def break_down_problem(user_question):
    instruction = (
        f"Please break down the following question into smaller, manageable parts:\n\n{user_question}"
    )
    
    try:
        response = openai_client.chat.completions.create(
            model="o1-preview",
            messages=[{"role": "user", "content": instruction}],
            max_tokens=1000,
        )
    
        breakdown = response.choices[0].message.content.strip()
        return breakdown
    except Exception as e:
        st.error(f"Error breaking down the problem: {e}")
        return "Unable to break down the problem at this time."

def explain_code(code):
    instruction = (
        f"As a highly skilled software engineer, please provide a detailed line-by-line explanation of the following code:\n\n"
        f"{code}\n\nMake sure to explain what each line does and why it is used."
    )
    
    try:
        openai_response = openai_client.chat.completions.create(
            model="o1-preview",
            messages=[{"role": "user", "content": instruction}],
            max_tokens=1000,  # Adjusted to a reasonable token limit
        )
    
        explanation = openai_response.choices[0].message.content.strip()
        return explanation
    except Exception as e:
        st.error(f"Error explaining the code: {e}")
        return "Unable to explain the code at this time."

def analyze_feedback(feedback_data):
    df = pd.DataFrame(feedback_data)
    feedback_summary = df['feedback'].value_counts().reset_index()
    feedback_summary.columns = ['feedback', 'count']
    
    # Sentiment Analysis
    df['sentiment'] = df['comments'].apply(analyze_sentiment)
    sentiment_summary = df['sentiment'].value_counts().reset_index()
    sentiment_summary.columns = ['sentiment', 'count']

    return feedback_summary, sentiment_summary

# Dropdown menu for programming languages
languages = ["Python", "Java", "C++", "JavaScript", "Go", "Ruby", "Swift"]

# Create the Streamlit interface
st.set_page_config(page_title="Optimized Code Generator", layout="wide")

# Dynamic Welcome Message with Typewriter Effect
welcome_messages = [
    "Welcome, how can I help you?",
    "How can I assist you today?",
    "I am here to provide you with coding solutions for your problems.",
    "Need optimized code? You've come to the right place!",
    "Let's generate some efficient code together."
]

# HTML and JavaScript for Typewriter Animation
typewriter_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    .typewriter {{
        font-family: monospace;
        overflow: hidden;
        border-right: .15em solid #4CAF50;
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: .15em;
        animation: caret 0.75s step-end infinite;
        font-size: 24px;
    }}

    @keyframes caret {{
        50% {{ border-color: transparent; }}
    }}
</style>
</head>
<body>

<div class="typewriter" id="typewriter"></div>

<script>
    const messages = {welcome_messages};
    let count = 0;
    let index = 0;
    let currentMessage = '';
    let letter = '';

    const typewriterElement = document.getElementById('typewriter');

    function type() {{
        if (count === messages.length) {{
            count = 0;
        }}
        currentMessage = messages[count];
        if (index < currentMessage.length) {{
            letter = currentMessage.charAt(index);
            typewriterElement.innerHTML += letter;
            index++;
            setTimeout(type, 100);
        }} else {{
            setTimeout(erase, 2000);
        }}
    }}

    function erase() {{
        if (index > 0) {{
            currentMessage = messages[count];
            typewriterElement.innerHTML = currentMessage.substring(0, index-1);
            index--;
            setTimeout(erase, 50);
        }} else {{
            count++;
            setTimeout(type, 500);
        }}
    }}

    document.addEventListener("DOMContentLoaded", function() {{
        setTimeout(type, 1000);
    }});
</script>

</body>
</html>
"""

# Display the dynamic welcome message
components.html(typewriter_html, height=50)

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
    user_question = st.text_area(
        "Enter your question:",
        placeholder="Type your question here...",
        height=150
    )
    
    # Submit button at the bottom of the main content
    submit_button = st.button("Submit", key="submit_button")
    
    if submit_button:
        if not user_question.strip():
            st.warning("Please enter a question before submitting.")
        else:
            with st.spinner("Thinking..."):
                # Check for ambiguities first
                code, ambiguous = generate_code(user_question, language)
                
                if ambiguous:
                    # If ambiguous, break down the problem
                    breakdown = break_down_problem(user_question)
                    st.sidebar.text_area(
                        "Ambiguity Detected:",
                        value=breakdown,
                        height=200,
                        disabled=True
                    )
                else:
                    explanation = explain_code(code)  # Get explanation using OpenAI
                    
                    # Display the generated code
                    code_container.code(code, language=language.lower())
                    
                    # Set the explanation output in the sidebar
                    st.sidebar.text_area(
                        "Code Explanation:",
                        value=explanation,
                        height=200,
                        disabled=True
                    )

                    # Feedback section
                    st.subheader("Feedback Section")
                    feedback_col1, feedback_col2 = st.columns([1, 2])  # Use columns for layout
                    
                    with feedback_col1:
                        st.markdown("**Was the generated code clear?**")
                        feedback_options = ["Select Feedback", "👍 Yes", "👎 No"]
                        feedback = st.selectbox("", options=feedback_options, index=0, key="feedback_select")
                    
                    with feedback_col2:
                        feedback_comments = st.text_area(
                            "Additional Comments:",
                            placeholder="Any additional feedback?",
                            height=100,
                            key="feedback_comments"
                        )
                    
                    feedback_submit = st.button("Submit Feedback", key="submit_feedback")
                    
                    if feedback_submit:
                        if feedback == "Select Feedback":
                            st.warning("Please select a feedback option.")
                        else:
                            feedback_entry = {
                                "question": user_question,
                                "code": code,
                                "explanation": explanation,
                                "feedback": feedback,
                                "comments": feedback_comments
                            }
                            save_feedback(feedback_entry)  # Store feedback in the file
                            st.success("Thank you for your feedback!")
                            # Optionally, clear the feedback fields
                            # st.session_state["feedback_select"] = "Select Feedback"
                            # st.session_state["feedback_comments"] = ""

# Feedback Analysis Section
st.subheader("Feedback Analysis")

show_analysis = st.button("Show Feedback Analysis", key="show_analysis")

if show_analysis:
    feedback_data = load_feedback()
    if feedback_data:
        feedback_summary, sentiment_summary = analyze_feedback(feedback_data)
        
        # Create a bar chart for feedback
        fig_feedback, ax_feedback = plt.subplots(figsize=(8, 5))
        ax_feedback.bar(feedback_summary['feedback'], feedback_summary['count'], color=['green', 'red'])
        ax_feedback.set_title('Feedback Summary')
        ax_feedback.set_xlabel('Feedback')
        ax_feedback.set_ylabel('Count')
        ax_feedback.set_xticks(range(len(feedback_summary['feedback'])))
        ax_feedback.set_xticklabels(feedback_summary['feedback'], rotation=45)
        st.pyplot(fig_feedback)

        # Create a bar chart for sentiment analysis
        fig_sentiment, ax_sentiment = plt.subplots(figsize=(8, 5))
        ax_sentiment.bar(sentiment_summary['sentiment'], sentiment_summary['count'], color=['blue', 'orange', 'gray'])
        ax_sentiment.set_title('Sentiment Analysis of Comments')
        ax_sentiment.set_xlabel('Sentiment')
        ax_sentiment.set_ylabel('Count')
        ax_sentiment.set_xticks(range(len(sentiment_summary['sentiment'])))
        ax_sentiment.set_xticklabels(sentiment_summary['sentiment'], rotation=45)
        st.pyplot(fig_sentiment)
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
        background-color: #4CAF50 !important; /* Green */
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        padding: 10px 20px !important;
        text-align: center !important;
        text-decoration: none !important;
        display: inline-block !important;
        font-size: 16px !important;
        margin: 4px 2px !important;
        cursor: pointer !important;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        width: 100% !important;
        border-radius: 5px !important;
        padding: 10px !important;
        margin-bottom: 10px !important;
    }
    h1 {
        color: #4CAF50;
    }
    h2 {
        color: #555;
    }
</style>
""", unsafe_allow_html=True)
