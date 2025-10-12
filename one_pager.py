import streamlit as st
import pandas as pd
import random
import requests
import io
import time
import datetime
import json
from typing import Dict, List, Optional

# Security headers and configuration
st.set_page_config(
    page_title="Electrical Installations Quiz",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"  # Changed to expanded for navigation
)

# Add dark mode compatible CSS with additional styles
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
    
    /* Progress bar styling */
    .progress-container {
        margin: 10px 0;
    }
    
    /* Navigation buttons */
    .nav-btn {
        width: 100%;
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
    
    /* Timer styling */
    .timer {
        font-size: 1.1em;
        font-weight: bold;
        color: #2196F3;
        padding: 8px 12px;
        border-radius: 4px;
        background-color: rgba(33, 150, 243, 0.1);
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Constants
QUESTIONS_PER_PAGE = 10

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
        st.session_state.current_page = 0
        st.session_state.quiz_mode = "study"  # "study" or "test"
        st.session_state.start_time = None
        st.session_state.quiz_finished = False
        st.session_state.progress_data = load_saved_progress()

# Data validation functions
def validate_question_data(df):
    """Validate the structure and content of questions"""
    if df.empty:
        st.error("No questions data found!")
        return False
    
    # Check required columns
    required_columns = ['Question', 'OptionA', 'OptionB', 'OptionC', 'OptionD', 'CorrectAnswer']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {missing_columns}")
        return False
    
    # Check for empty questions
    empty_questions = df['Question'].isna() | (df['Question'].str.strip() == '')
    if empty_questions.any():
        st.warning(f"Found {empty_questions.sum()} empty questions")
    
    # Validate correct answers exist in options
    validation_errors = []
    for idx, row in df.iterrows():
        correct_answer = str(row['CorrectAnswer'])
        options = [str(row[f'Option{chr(65+i)}']) for i in range(4)]
        options = [opt for opt in options if opt and opt != 'nan' and opt.strip() != '']
        
        if correct_answer not in options and correct_answer != '':
            validation_errors.append(f"Question {idx+1}: Correct answer '{correct_answer}' not found in options")
    
    if validation_errors:
        for error in validation_errors[:5]:  # Show first 5 errors
            st.error(error)
        if len(validation_errors) > 5:
            st.error(f"... and {len(validation_errors) - 5} more errors")
        return False
    
    return True

# Progress tracking functions
def calculate_score():
    """Calculate detailed score breakdown"""
    if not st.session_state.answer_checked:
        return None
    
    correct = 0
    total_checked = len([k for k, v in st.session_state.answer_checked.items() if v])
    
    for i, checked in st.session_state.answer_checked.items():
        if checked and i in st.session_state.user_answers:
            row = st.session_state.questions_df.iloc[i]
            if st.session_state.user_answers[i] == str(row['CorrectAnswer']):
                correct += 1
    
    return {
        'correct': correct,
        'total_checked': total_checked,
        'accuracy': (correct / total_checked * 100) if total_checked > 0 else 0,
        'total_questions': len(st.session_state.questions_df)
    }

def save_progress():
    """Save user progress to session state and simulate local storage"""
    progress = {
        'timestamp': datetime.datetime.now().isoformat(),
        'answers': st.session_state.user_answers.copy(),
        'checked': st.session_state.answer_checked.copy(),
        'score': calculate_score(),
        'quiz_mode': st.session_state.quiz_mode,
        'current_page': st.session_state.current_page
    }
    st.session_state.progress_data = progress
    return progress

def load_saved_progress():
    """Load saved progress from session state"""
    # In a real app, you might load from file/database
    # For now, we'll use session state
    return getattr(st.session_state, 'progress_data', None)

def export_results():
    """Export quiz results to CSV"""
    results = []
    for i in range(len(st.session_state.questions_df)):
        row = st.session_state.questions_df.iloc[i]
        user_answer = st.session_state.user_answers.get(i, 'Not answered')
        correct_answer = str(row['CorrectAnswer'])
        is_correct = user_answer == correct_answer if user_answer != 'Not answered' else False
        
        results.append({
            'Question_Number': i + 1,
            'Question': row['Question'],
            'User_Answer': user_answer,
            'Correct_Answer': correct_answer,
            'Is_Correct': is_correct,
            'Was_Checked': st.session_state.answer_checked.get(i, False),
            'Scenario': row.get('Scenario', '')
        })
    
    return pd.DataFrame(results)

# Navigation functions
def get_current_page_questions():
    """Get questions for current page"""
    start_idx = st.session_state.current_page * QUESTIONS_PER_PAGE
    end_idx = min(start_idx + QUESTIONS_PER_PAGE, len(st.session_state.questions_df))
    return list(range(start_idx, end_idx))

def scroll_to_question(question_id):
    """Simulate scroll to question (Streamlit doesn't support direct scroll)"""
    st.session_state.current_page = question_id // QUESTIONS_PER_PAGE
    st.rerun()

# Timer functions
def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    return str(datetime.timedelta(seconds=int(seconds)))

def update_timer():
    """Update and display timer"""
    if st.session_state.start_time and not st.session_state.quiz_finished:
        elapsed = time.time() - st.session_state.start_time
        return elapsed
    return 0

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
        
        return questions_df
    
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return pd.DataFrame()

# Build scenario groups
def build_scenario_groups(df):
    scenario_groups = {}
    for idx, row in df.iterrows():
        scenario = str(row.get('Scenario', '')).strip()
        if scenario and scenario != 'nan' and scenario != '':
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(idx)
    return scenario_groups

# Initialize session state
initialize_session_state()

# Sidebar for navigation and controls
with st.sidebar:
    st.header("⚡ Quiz Controls")
    
    # Quiz mode selection
    quiz_mode = st.radio(
        "Quiz Mode:",
        ["Study Mode", "Timed Test"],
        index=0 if st.session_state.quiz_mode == "study" else 1,
        key="mode_selector"
    )
    
    st.session_state.quiz_mode = "study" if quiz_mode == "Study Mode" else "test"
    
    # Timed quiz controls
    if st.session_state.quiz_mode == "test":
        if not st.session_state.start_time and not st.session_state.quiz_finished:
            if st.button("🚀 Start Timed Quiz", type="primary"):
                st.session_state.start_time = time.time()
                st.session_state.quiz_finished = False
                st.session_state.user_answers = {}
                st.session_state.answer_checked = {}
                st.rerun()
        
        if st.session_state.start_time:
            elapsed = update_timer()
            st.markdown(f'<div class="timer">⏱️ {format_time(elapsed)}</div>', unsafe_allow_html=True)
            
            if st.button("⏹️ Finish Quiz", type="secondary"):
                st.session_state.quiz_finished = True
                save_progress()
                st.rerun()
    
    st.header("🧭 Navigation")
    
    # Quick jump to questions
    if st.session_state.questions_loaded:
        question_numbers = list(range(1, len(st.session_state.questions_df) + 1))
        selected_q = st.selectbox("Jump to question:", question_numbers)
        
        if st.button("Go to Question"):
            scroll_to_question(selected_q - 1)
    
    # Progress overview
    st.header("📊 Progress")
    if st.session_state.questions_loaded:
        total_questions = len(st.session_state.questions_df)
        checked_count = len([k for k, v in st.session_state.answer_checked.items() if v])
        
        if total_questions > 0:
            progress = checked_count / total_questions
            st.progress(progress)
            st.write(f"**{checked_count}/{total_questions}** questions checked")
            
            score = calculate_score()
            if score and score['total_checked'] > 0:
                st.write(f"**Correct:** {score['correct']}/{score['total_checked']}")
                st.write(f"**Accuracy:** {score['accuracy']:.1f}%")
    
    # Export results
    if st.session_state.questions_loaded and any(st.session_state.answer_checked.values()):
        st.header("💾 Export")
        if st.button("📊 Export Results to CSV"):
            results_df = export_results()
            csv = results_df.to_csv(index=False)
            
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"quiz_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="download_csv"
            )

# Main content area
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Electrical Installations Quiz")
    st.subheader("Practice Mode" if st.session_state.quiz_mode == "study" else "Timed Test Mode")
with col2:
    if st.button("🔄 Refresh Questions", type="secondary"):
        st.cache_data.clear()
        st.session_state.questions_loaded = False
        st.session_state.questions_df = pd.DataFrame()
        st.session_state.scenario_groups = {}
        st.session_state.user_answers = {}
        st.session_state.answer_checked = {}
        st.session_state.shuffled_options = {}
        st.session_state.current_page = 0
        st.rerun()

# Show loading message
if not st.session_state.questions_loaded:
    loading_placeholder = st.empty()
    loading_placeholder.info("🔄 Loading questions...")

# Load questions
if not st.session_state.questions_loaded or st.session_state.questions_df.empty:
    questions_df = load_questions_data()
    
    if not questions_df.empty and validate_question_data(questions_df):
        st.session_state.questions_df = questions_df
        st.session_state.questions_loaded = True
        st.session_state.scenario_groups = build_scenario_groups(questions_df)
        
        # Load saved progress if available
        if st.session_state.progress_data:
            st.session_state.user_answers = st.session_state.progress_data.get('answers', {})
            st.session_state.answer_checked = st.session_state.progress_data.get('checked', {})
            st.session_state.current_page = st.session_state.progress_data.get('current_page', 0)
        
        if 'loading_placeholder' in locals():
            loading_placeholder.empty()
    else:
        st.error("No valid questions could be loaded. Please check your data source.")
        st.stop()

# Use the questions from session state
questions_df = st.session_state.questions_df
num_questions = len(questions_df)

# Show question count and pagination info
st.caption(f"Total Questions: {num_questions} | Page {st.session_state.current_page + 1}/{(num_questions // QUESTIONS_PER_PAGE) + 1}")

# Pagination controls
if num_questions > QUESTIONS_PER_PAGE:
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    with col1:
        if st.button("⬅️ Previous", disabled=st.session_state.current_page == 0):
            st.session_state.current_page -= 1
            st.rerun()
    with col2:
        if st.button("Next ➡️", disabled=(st.session_state.current_page + 1) * QUESTIONS_PER_PAGE >= num_questions):
            st.session_state.current_page += 1
            st.rerun()
    with col4:
        if st.button("💾 Save Progress", type="secondary"):
            progress = save_progress()
            st.success("Progress saved successfully!")

# Display questions for current page
current_questions = get_current_page_questions()

for i in current_questions:
    row = questions_df.iloc[i]
    global_index = i
    
    # Create a container for each question
    with st.container():
        st.write("---")
        
        # Question header with status indicator
        col_head1, col_head2 = st.columns([3, 1])
        with col_head1:
            st.subheader(f"Question {global_index + 1}")
        with col_head2:
            if st.session_state.answer_checked.get(global_index, False):
                user_answer = st.session_state.user_answers.get(global_index, "")
                correct_answer = str(row['CorrectAnswer'])
                if user_answer == correct_answer:
                    st.markdown("✅ **Answered Correctly**")
                else:
                    st.markdown("❌ **Needs Review**")
            elif global_index in st.session_state.user_answers:
                st.markdown("📝 **Answer Saved**")
            else:
                st.markdown("⏳ **Not Answered**")
        
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
        
        # Shuffle options only once per question (except in test mode)
        if global_index not in st.session_state.shuffled_options:
            options = [str(row['OptionA']), str(row['OptionB']), str(row['OptionC']), str(row['OptionD'])]
            options = [opt for opt in options if opt and opt != 'nan' and opt.strip() != '']
            
            # Don't shuffle in test mode to maintain consistency
            if st.session_state.quiz_mode == "test":
                st.session_state.shuffled_options[global_index] = options
            else:
                st.session_state.shuffled_options[global_index] = random.sample(options, len(options))
        
        shuffled_options = st.session_state.shuffled_options[global_index]
        
        # Display radio button for answer selection
        answer_key = f"q_{global_index}"
        user_answer = st.radio(
            "Choose your answer:",
            shuffled_options,
            key=answer_key,
            index=shuffled_options.index(st.session_state.user_answers[global_index]) if global_index in st.session_state.user_answers else None
        )
        
        # Store the selected answer
        if user_answer:
            st.session_state.user_answers[global_index] = user_answer
            # Auto-save progress in test mode
            if st.session_state.quiz_mode == "test":
                save_progress()
        
        # Check Answer button (disabled in test mode until quiz is finished)
        col1, col2 = st.columns([1, 4])
        with col1:
            check_disabled = (global_index not in st.session_state.user_answers or 
                            (st.session_state.quiz_mode == "test" and not st.session_state.quiz_finished))
            
            if st.button("Check Answer", key=f"check_{global_index}", disabled=check_disabled, type="primary"):
                st.session_state.answer_checked[global_index] = True
                save_progress()
                st.rerun()
        
        # Show result if answer was checked
        if st.session_state.answer_checked.get(global_index, False):
            correct_answer = str(row['CorrectAnswer'])
            user_answer = st.session_state.user_answers.get(global_index, "")
            
            if user_answer == correct_answer:
                st.markdown(f'<div class="correct-answer">✅ Correct! Well done.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="incorrect-answer">❌ Incorrect. The correct answer is: {correct_answer}</div>', unsafe_allow_html=True)
                
                # Show hint if available
                hint = row.get('Hint')
                if pd.notna(hint) and str(hint).strip():
                    st.info(f"💡 **Hint:** {hint}")

# Final summary and quiz completion
st.write("---")
st.subheader("Quiz Summary")

score = calculate_score()
if score and score['total_checked'] > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions Checked", f"{score['total_checked']}/{num_questions}")
    with col2:
        st.metric("Correct Answers", f"{score['correct']}/{score['total_checked']}")
    with col3:
        st.metric("Accuracy", f"{score['accuracy']:.1f}%")
    
    # Performance feedback
    if score['accuracy'] >= 80:
        st.success("🎉 Excellent work! You're mastering the material.")
    elif score['accuracy'] >= 60:
        st.info("👍 Good progress! Keep practicing to improve.")
    else:
        st.warning("📚 Keep studying! Review the material and try again.")
else:
    st.info("Select answers and click 'Check Answer' buttons to see your progress.")

# Reset button
if st.button("🔄 Reset All Answers", type="secondary"):
    st.session_state.user_answers = {}
    st.session_state.answer_checked = {}
    st.session_state.shuffled_options = {}
    st.session_state.quiz_finished = False
    st.session_state.start_time = None
    st.rerun()

# Footer
st.markdown("---")
st.caption("⚡ Electrical Installations Quiz | Practice and master your skills")
