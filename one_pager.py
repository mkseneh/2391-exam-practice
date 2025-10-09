import streamlit as st
import pandas as pd
import random
import requests
import io
import time
import datetime

# Security headers and configuration
st.set_page_config(
    page_title="Electrical Installations Quiz",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add dark mode compatible CSS
st.markdown("""
<style>
    /* Scenario container with dark mode support */
    .scenario-container {
        background-color: var(--background-color);
        border-left: 5px solid #4CAF50;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid var(--border-color);
    }
    .scenario-header {
        color: #4CAF50;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .scenario-content {
        color: var(--text-color);
        line-height: 1.6;
        font-size: 1em;
        margin-bottom: 8px;
    }
    .scenario-progress {
        background-color: rgba(76, 175, 80, 0.1);
        padding: 8px 15px;
        border-radius: 20px;
        font-size: 0.9em;
        color: #4CAF50;
        margin-top: 10px;
        display: inline-block;
    }
    
    /* Question container with dark mode support */
    .question-container {
        background-color: var(--secondary-background-color);
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        border-left: 4px solid #2196F3;
        border: 1px solid var(--border-color);
    }
    .question-paragraph {
        line-height: 1.6;
        margin-bottom: 12px;
        font-size: 1.05em;
        color: var(--text-color);
    }
    
    /* Check Answer button styling */
    .check-answer-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.9em;
        margin: 5px 0;
    }
    .check-answer-btn:hover {
        background-color: #45a049;
    }
    
    /* Result styling */
    .correct-answer {
        color: #4CAF50;
        font-weight: bold;
        margin: 5px 0;
    }
    .incorrect-answer {
        color: #f44336;
        font-weight: bold;
        margin: 5px 0;
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --secondary-background-color: #262730;
            --text-color: #fafafa;
            --border-color: #555;
        }
    }
    @media (prefers-color-scheme: light) {
        :root {
            --background-color: #f0f8ff;
            --secondary-background-color: #f8f9fa;
            --text-color: #31333F;
            --border-color: #ddd;
        }
    }
    
    /* Ensure radio buttons are readable */
    .stRadio > div {
        color: var(--text-color);
    }
    
    /* Make all text readable in dark mode */
    .stApp {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
def initialize_session_state():
    """Initialize all session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.user_answers = {}
        st.session_state.answer_checked = {}
        st.session_state.shuffled_options = {}
        st.session_state.questions_loaded = False
        st.session_state.questions_df = pd.DataFrame()
        st.session_state.scenario_groups = {}

# Call initialization function
initialize_session_state()

# Add refresh button and title
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Electrical Installations Quiz - Practice Mode")
with col2:
    if st.button("🔄 Refresh Questions", type="secondary"):
        st.cache_data.clear()
        st.session_state.questions_loaded = False
        st.session_state.questions_df = pd.DataFrame()
        st.session_state.scenario_groups = {}
        st.rerun()

# Show loading message
if not st.session_state.questions_loaded:
    loading_placeholder = st.empty()
    loading_placeholder.info("🔄 Loading questions...")

# Load questions function
@st.cache_data(ttl=300)
def load_questions_data():
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1OhPzpNeKII4Fn1UQCQQvjFTjkiMtma-fPfY2eVIOi4c/edit?usp=sharing"
    
    try:
        csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()
        
        questions_df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        questions_df = questions_df.fillna('')
        
        required_columns = ['Question', 'OptionA', 'OptionB', 'OptionC', 'OptionD', 'CorrectAnswer']
        missing_columns = [col for col in required_columns if col not in questions_df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return pd.DataFrame()
            
        return questions_df
    
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return pd.DataFrame()

# Load questions
if not st.session_state.questions_loaded or st.session_state.questions_df.empty:
    questions_df = load_questions_data()
    
    if not questions_df.empty:
        st.session_state.questions_df = questions_df
        st.session_state.questions_loaded = True
        if 'loading_placeholder' in locals():
            loading_placeholder.empty()
    else:
        st.error("No questions could be loaded. Please check your data source.")
        st.stop()

# Use the questions from session state
questions_df = st.session_state.questions_df
num_questions = len(questions_df)

# Show question count
st.caption(f"Total Questions: {num_questions}")

# Build scenario groups if not already built
def build_scenario_groups(df):
    scenario_groups = {}
    for idx, row in df.iterrows():
        scenario = str(row.get('Scenario', '')).strip()
        if scenario and scenario != 'nan' and scenario != '':
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(idx)
    return scenario_groups

if not st.session_state.scenario_groups:
    st.session_state.scenario_groups = build_scenario_groups(questions_df)

# Display all questions at once
for i in range(num_questions):
    row = questions_df.iloc[i]
    
    # Create a container for each question
    with st.container():
        st.write("---")
        st.subheader(f"Question {i+1}")
        
        # Display Scenario (if available)
        current_scenario = str(row.get('Scenario', '')).strip()
        if current_scenario and current_scenario != 'nan' and current_scenario != '':
            scenario_paragraphs = [p.strip() for p in current_scenario.split('\n') if p.strip()]
            
            scenario_html = '''
            <div class="scenario-container">
                <div class="scenario-header">📖 SCENARIO</div>
            '''
            
            for paragraph in scenario_paragraphs:
                scenario_html += f'<div class="scenario-content">{paragraph}</div>'
            scenario_html += '</div>'
            
            st.markdown(scenario_html, unsafe_allow_html=True)
        
        # Display the question
        st.write("**Question:**")
        question_text = str(row['Question'])
        question_paragraphs = [p.strip() for p in question_text.split('\n') if p.strip()]
        
        question_html = '<div class="question-container">'
        for paragraph in question_paragraphs:
            question_html += f'<div class="question-paragraph">{paragraph}</div>'
        question_html += '</div>'
        
        st.markdown(question_html, unsafe_allow_html=True)
        
        # Shuffle options only once per question
        if i not in st.session_state.shuffled_options:
            options = [str(row['OptionA']), str(row['OptionB']), str(row['OptionC']), str(row['OptionD'])]
            options = [opt for opt in options if opt and opt != 'nan']
            shuffled_options = random.sample(options, len(options))
            st.session_state.shuffled_options[i] = shuffled_options
        
        shuffled_options = st.session_state.shuffled_options[i]
        
        # Display radio button for answer selection
        answer_key = f"q_{i}"
        user_answer = st.radio(
            "Choose your answer:",
            shuffled_options,
            key=answer_key,
            index=None  # Start with no selection
        )
        
        # Store the selected answer
        if user_answer:
            st.session_state.user_answers[i] = user_answer
        
        # Check Answer button
        col1, col2 = st.columns([1, 4])
        with col1:
            check_disabled = i not in st.session_state.user_answers
            if st.button("Check Answer", key=f"check_{i}", disabled=check_disabled, type="primary"):
                st.session_state.answer_checked[i] = True
                st.rerun()
        
        # Show result if answer was checked
        if st.session_state.answer_checked.get(i, False):
            correct_answer = str(row['CorrectAnswer'])
            user_answer = st.session_state.user_answers.get(i, "")
            
            if user_answer == correct_answer:
                st.markdown(f'<div class="correct-answer">✅ Correct! Well done.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="incorrect-answer">❌ Incorrect. The correct answer is: {correct_answer}</div>', unsafe_allow_html=True)
                
                # Show hint if available
                hint = row.get('Hint')
                if pd.notna(hint) and str(hint).strip():
                    st.info(f"💡 **Hint:** {hint}")

# Summary at the bottom
st.write("---")
st.subheader("Quiz Summary")

checked_count = len([k for k, v in st.session_state.answer_checked.items() if v])
correct_count = 0

for i in range(num_questions):
    if st.session_state.answer_checked.get(i, False):
        row = questions_df.iloc[i]
        correct_answer = str(row['CorrectAnswer'])
        user_answer = st.session_state.user_answers.get(i, "")
        if user_answer == correct_answer:
            correct_count += 1

if checked_count > 0:
    accuracy = (correct_count / checked_count) * 100
    st.metric("Questions Checked", f"{checked_count}/{num_questions}")
    st.metric("Correct Answers", f"{correct_count}/{checked_count}")
    st.metric("Accuracy", f"{accuracy:.1f}%")
else:
    st.info("Select answers and click 'Check Answer' buttons to see your progress.")

# Reset button
if st.button("Reset All Answers", type="secondary"):
    st.session_state.user_answers = {}
    st.session_state.answer_checked = {}
    st.session_state.shuffled_options = {}
    st.rerun()