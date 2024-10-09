
# ui.py
import streamlit as st
import matplotlib.pyplot as plt

def create_ui(generate_code, break_down_problem, explain_code, load_feedback, save_feedback, analyze_feedback):
    st.markdown("<h1 style='text-align: center;'>Optimized Code Generator</h1>", unsafe_allow_html=True)
    
    # Dropdown menu for programming languages
    languages = ["Python", "Java", "C++", "JavaScript", "Go", "Ruby", "Swift"]
    st.sidebar.title("Input Section")
    language = st.sidebar.selectbox("Select Programming Language:", options=languages, index=0)
    
    # Main area for generated code and question input
    st.subheader("Generated Code:")
    code_container = st.empty()  # Placeholder for generated code

    with st.container():
        user_question = st.text_area("Enter your question:", placeholder="Type your question here...", height=150)
        
        if st.button("Submit"):
            with st.spinner("Thinking..."):
                code, ambiguous = generate_code(user_question, language)
                
                if ambiguous:
                    breakdown = break_down_problem(user_question)
                    st.sidebar.text_area("Ambiguity Detected:", value=breakdown, height=200, disabled=True)
                else:
                    explanation = explain_code(code)
                    code_container.code(code, language=language.lower())
                    st.sidebar.text_area("Code Explanation:", value=explanation, height=200, disabled=True)

                    # Feedback section
                    handle_feedback(user_question, code, explanation, save_feedback)

    # Feedback Analysis Section
    handle_feedback_analysis(load_feedback, analyze_feedback)

def handle_feedback(user_question, code, explanation, save_feedback):
    st.subheader("Feedback Section")
    feedback_col1, feedback_col2 = st.columns([1, 2])
    
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
        save_feedback(feedback_entry)
        st.success("Thank you for your feedback!")

def handle_feedback_analysis(load_feedback, analyze_feedback):
    st.subheader("Feedback Analysis")
    
    if st.button("Show Feedback Analysis"):
        feedback_data = load_feedback()
        if feedback_data:
            feedback_summary, sentiment_summary = analyze_feedback(feedback_data)
            plot_feedback(feedback_summary)
            plot_sentiment_analysis(sentiment_summary)
        else:
            st.warning("No feedback available for analysis.")

def plot_feedback(feedback_summary):
    plt.figure(figsize=(8, 5))
    plt.bar(feedback_summary['feedback'], feedback_summary['count'], color=['green', 'red'])
    plt.title('Feedback Summary')
    plt.xlabel('Feedback')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    st.pyplot(plt)

def plot_sentiment_analysis(sentiment_summary):
    plt.figure(figsize=(8, 5))
    plt.bar(sentiment_summary['sentiment'], sentiment_summary['count'], color=['blue', 'orange', 'gray'])
    plt.title('Sentiment Analysis of Comments')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    st.pyplot(plt)
