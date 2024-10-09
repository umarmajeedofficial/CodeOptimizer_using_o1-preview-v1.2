# feedback.py
import json
import os
import pandas as pd
from textblob import TextBlob

# File to store feedback
FEEDBACK_FILE = 'feedback_data.json'

def load_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    return []

def save_feedback(feedback):
    existing_feedback = load_feedback()
    existing_feedback.append(feedback)
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(existing_feedback, f, indent=4)

def analyze_feedback(feedback_data):
    # Your existing analyze_feedback logic here

def analyze_sentiment(comment):
    blob = TextBlob(comment)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Negative"
    else:
        return "Neutral"

