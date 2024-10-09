# app.py
import streamlit as st
from ui import create_ui
from llama import generate_code, break_down_problem, explain_code
from openai import openai_client
from feedback import load_feedback, save_feedback, analyze_feedback

def main():
    st.set_page_config(page_title="Optimized Code Generator", layout="wide")
    create_ui(generate_code, break_down_problem, explain_code, load_feedback, save_feedback, analyze_feedback)

if __name__ == "__main__":
    main()
