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
    
    /* Timer styling */
    .timer-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        color: white;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .timer-warning {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    }
    .timer-critical {
        background: linear-gradient(135deg, #ff0000 0%, #8b0000 100%);
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
    
    /* Style metric cards for dark mode */
    [data-testid="metric-container"] {
        background-color: var(--secondary-background-color);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 10px;
    }

        /* Results table styling - ADD THIS */
    .results-table-container {
        margin: 10px 0;
        width: 100%;
    }

    .results-table {
        border-collapse: collapse;
        width: 100%;
        font-family: Arial, sans-serif;
        font-size: 0.9em;
        margin: 0 auto;
        /* CSS Variables for theming */
        --border-color: #ccc;
        --header-bg: #fafafa;
        --row-even-bg: #fafafa;
        --text-color: #000;
        --bg-color: #fff;
    }

    /* Dark mode overrides for table */
    @media (prefers-color-scheme: dark) {
        .results-table {
            --border-color: #555;
            --header-bg: #333;
            --row-even-bg: #2a2a2a;
            --text-color: #fff;
            --bg-color: #1e1e1e;
        }
    }

    .results-table {
        background-color: var(--bg-color);
        color: var(--text-color);
    }

    /* Force center alignment for ALL table cells */
    .results-table th,
    .results-table td {
        border: 1px solid var(--border-color);
        padding: 8px;
        text-align: center;
        vertical-align: middle;
    }

    .results-table th {
        background-color: var(--header-bg);
        font-weight: bold;
        text-align: center;
    }

    .results-table tr:nth-child(even) {
        background-color: var(--row-even-bg);
    }
</style>
""", unsafe_allow_html=True)

# Initialize ALL session state variables at the beginning
def initialize_session_state():
    """Initialize all session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.shuffled_options = {}
        st.session_state.quiz_completed = False
        st.session_state.quiz_submitted = False
        st.session_state.scenario_groups = {}
        st.session_state.loading_shown = False
        st.session_state.questions_loaded = False
        st.session_state.questions_df = pd.DataFrame()
        # Timer variables
        st.session_state.exam_started = False
        st.session_state.exam_start_time = None
        st.session_state.exam_duration = 3 * 60 * 60  # 3 hours in seconds
        st.session_state.time_up = False
        st.session_state.auto_submitted = False
        st.session_state.last_timer_update = 0

# Call initialization function
initialize_session_state()

# Timer functions
def start_exam_timer():
    """Start the exam timer"""
    if not st.session_state.exam_started:
        st.session_state.exam_started = True
        st.session_state.exam_start_time = time.time()
        st.session_state.time_up = False
        st.session_state.auto_submitted = False

def get_remaining_time():
    """Calculate remaining time"""
    if not st.session_state.exam_started or st.session_state.time_up:
        return 0
    
    elapsed = time.time() - st.session_state.exam_start_time
    remaining = st.session_state.exam_duration - elapsed
    
    if remaining <= 0:
        st.session_state.time_up = True
        if not st.session_state.auto_submitted and not st.session_state.quiz_submitted:
            st.session_state.auto_submitted = True
            st.session_state.quiz_submitted = True
        return 0
    
    return remaining

def format_time(seconds):
    """Format seconds into HH:MM:SS"""
    if seconds <= 0:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# Add refresh button and title in the same row
col1, col2 = st.columns([3, 1])
with col1:
    st.title("Initial and Periodic Inspection and Testing of Electrical Installations (2391-052)")
with col2:
    if st.button("🔄 Refresh Questions", type="secondary"):
        # Clear cache and reset ONLY what's necessary
        st.cache_data.clear()
        st.session_state.questions_loaded = False
        st.session_state.questions_df = pd.DataFrame()
        st.session_state.scenario_groups = {}
        st.rerun()

# Show loading message only when actually loading
if not st.session_state.questions_loaded and not st.session_state.loading_shown:
    loading_placeholder = st.empty()
    loading_placeholder.info("🔄 Loading questions...")
    st.session_state.loading_shown = True

# Configuration with shorter cache time - UPDATED SECURE VERSION
@st.cache_data(ttl=300)
def load_questions_data():
    # Try Google Sheets first
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1OhPzpNeKII4Fn1UQCQQvjFTjkiMtma-fPfY2eVIOi4c/edit?usp=sharing"
    
    try:
        # Convert Google Sheets URL to CSV export URL
        csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')
        
        # Add timeout and better error handling for production
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()
        
        # Read CSV data
        questions_df = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        questions_df = questions_df.fillna('')
        
        # Validate required columns exist
        required_columns = ['Question', 'OptionA', 'OptionB', 'OptionC', 'OptionD', 'CorrectAnswer']
        missing_columns = [col for col in required_columns if col not in questions_df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {missing_columns}")
            return pd.DataFrame()
            
        return questions_df
    
    except requests.exceptions.Timeout:
        st.error("Timeout loading questions from Google Sheets. Please try again.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"Network error loading questions: {e}")
        # Fallback to local Excel file
        try:
            questions_df = pd.read_excel("2391-052_practice.xlsx")
            questions_df = questions_df.fillna('')
            return questions_df
        except Exception as e2:
            st.error(f"Failed to load questions from both sources: {e2}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return pd.DataFrame()

# Load questions only if not already loaded
if not st.session_state.questions_loaded or st.session_state.questions_df.empty:
    questions_df = load_questions_data()
    
    if not questions_df.empty:
        st.session_state.questions_df = questions_df
        st.session_state.questions_loaded = True
        
        # Clear loading message after data is loaded
        if 'loading_placeholder' in locals():
            loading_placeholder.empty()
        st.session_state.loading_shown = False
    else:
        st.error("No questions could be loaded. Please check your data source.")
        st.stop()

# Use the questions from session state
questions_df = st.session_state.questions_df
num_questions = len(questions_df)

# Show last update time (stays visible)
st.caption(f"Questions: {num_questions} | Last updated: {time.strftime('%H:%M:%S')}")

# --- Exam Timer Display ---
if not st.session_state.quiz_submitted:
    remaining_time = get_remaining_time()
    
    # Check if time is up and auto-submit
    if st.session_state.time_up and not st.session_state.quiz_submitted:
        st.session_state.quiz_submitted = True
        st.rerun()
    
    # Start timer automatically when user starts answering or show start button
    if not st.session_state.exam_started:
        st.warning("⏰ **Exam Timer**: 3 hours | Click 'Start Exam Timer' to begin")
        if st.button("🚀 Start Exam Timer", type="primary"):
            start_exam_timer()
            st.rerun()
    else:
        # Display timer with appropriate styling
        timer_class = "timer-container"
        if remaining_time < 1800:  # 30 minutes
            timer_class += " timer-warning"
        if remaining_time < 600:   # 10 minutes
            timer_class += " timer-critical"
        
        timer_html = f"""
        <div class="{timer_class}">
            <div style="font-size: 1.1em;">⏰ EXAM TIME REMAINING</div>
            <div style="font-size: 1.8em; margin: 10px 0;">{format_time(remaining_time)}</div>
            <div style="font-size: 0.9em;">3 Hour Time Limit</div>
        </div>
        """
        st.markdown(timer_html, unsafe_allow_html=True)

# --- Pre-process scenario groups ---
def build_scenario_groups(df):
    scenario_groups = {}
    for idx, row in df.iterrows():
        scenario = str(row.get('Scenario', '')).strip()
        if scenario and scenario != 'nan' and scenario != '':
            if scenario not in scenario_groups:
                scenario_groups[scenario] = []
            scenario_groups[scenario].append(idx)
    return scenario_groups

# Build scenario groups if not already built
if not st.session_state.scenario_groups:
    st.session_state.scenario_groups = build_scenario_groups(questions_df)

# --- Current question ---
i = st.session_state.current_q

# Check if we have a valid question index
if i >= len(questions_df):
    st.session_state.current_q = 0
    i = 0
    st.rerun()

row = questions_df.iloc[i]

# --- Check if this is the last question ---
is_last_question = i == num_questions - 1

# --- Shuffle options only once per question ---
if i not in st.session_state.shuffled_options:
    options = [str(row['OptionA']), str(row['OptionB']), str(row['OptionC']), str(row['OptionD'])]
    # Filter out empty options
    options = [opt for opt in options if opt and opt != 'nan']
    shuffled_options = random.sample(options, len(options))
    st.session_state.shuffled_options[i] = shuffled_options

shuffled_options = st.session_state.shuffled_options[i]

# --- Display Question Header FIRST ---
st.subheader(f"Question {i+1} of {num_questions}")

# --- Display Scenario (if available) ---
current_scenario = str(row.get('Scenario', '')).strip()
current_scenario_indices = []
current_scenario_position = 0
total_scenario_questions = 0

if current_scenario and current_scenario != 'nan' and current_scenario != '':
    # Get scenario indices from pre-built groups
    current_scenario_indices = st.session_state.scenario_groups.get(current_scenario, [])
    
    if current_scenario_indices:
        try:
            current_scenario_position = current_scenario_indices.index(i) + 1
            total_scenario_questions = len(current_scenario_indices)
            
            # Split scenario into paragraphs
            scenario_paragraphs = [p.strip() for p in current_scenario.split('\n') if p.strip()]
            
            # Build scenario HTML
            scenario_html = '''
            <div class="scenario-container">
                <div class="scenario-header">📖 SCENARIO</div>
            '''
            
            for paragraph in scenario_paragraphs:
                scenario_html += f'<div class="scenario-content">{paragraph}</div>'
            
            scenario_html += f'<div class="scenario-progress">Scenario Question {current_scenario_position} of {total_scenario_questions}</div>'
            scenario_html += '</div>'
            
            st.markdown(scenario_html, unsafe_allow_html=True)
        except Exception as e:
            st.warning("Could not load scenario information")

# --- Display the actual question with paragraph support ---
st.write("**Question:**")
question_text = str(row['Question'])

# Split question into paragraphs and display each as separate markdown
question_paragraphs = [p.strip() for p in question_text.split('\n') if p.strip()]

# Display question in a styled container
question_html = '<div class="question-container">'
for paragraph in question_paragraphs:
    question_html += f'<div class="question-paragraph">{paragraph}</div>'
question_html += '</div>'

st.markdown(question_html, unsafe_allow_html=True)

# --- Find the index of previously selected answer ---
previous_answer = st.session_state.user_answers.get(i)
if previous_answer is not None:
    try:
        selected_index = shuffled_options.index(previous_answer)
    except ValueError:
        selected_index = None
else:
    selected_index = None

# --- Display radio button ---
user_answer = st.radio("Choose your answer:", 
                       shuffled_options, 
                       index=selected_index,
                       key=f"q{i}")

# Store the selected option
if user_answer is not None:
    st.session_state.user_answers[i] = user_answer
    # Auto-start timer when user starts answering
    if not st.session_state.exam_started:
        start_exam_timer()

# --- Navigation buttons ---
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Previous", disabled=(i == 0)):
        st.session_state.current_q -= 1
        st.rerun()
with col2:
    if is_last_question:
        if st.button("Next", disabled=True):
            pass
    else:
        if st.button("Next"):
            st.session_state.current_q += 1
            st.rerun()
with col3:
    answered_count = len(st.session_state.user_answers)
    submit_disabled = answered_count == 0 or st.session_state.time_up
    
    submit_label = "Submit Quiz"
    if st.session_state.time_up:
        submit_label = "Time's Up!"
    
    if st.button(submit_label, type="primary", disabled=submit_disabled):
        st.session_state.quiz_submitted = True
        st.rerun()

# --- Scenario Navigation ---
if current_scenario_indices and len(current_scenario_indices) > 1:
    st.write("---")
    st.write("**Scenario Navigation:**")
    
    scenario_cols = st.columns(len(current_scenario_indices))
    
    for idx, q_idx in enumerate(current_scenario_indices):
        with scenario_cols[idx]:
            is_current_scenario_q = q_idx == i
            is_answered = q_idx in st.session_state.user_answers
            
            label = f"Q{idx + 1}"
            button_type = "primary" if is_current_scenario_q else "secondary"
            
            if st.button(label, key=f"scenario_nav_{current_scenario}_{q_idx}", type=button_type, use_container_width=True):
                st.session_state.current_q = q_idx
                st.rerun()

# --- Progress Section ---
answered_count = len(st.session_state.user_answers)
progress_percentage = answered_count / num_questions if num_questions > 0 else 0

st.progress(progress_percentage)
st.write(f"Progress: {answered_count}/{num_questions} questions answered")
st.write(f"Current question: {i+1}/{num_questions}")

# --- Useful Information Section ---
st.write("---")

# Use 4 columns for compact layout
col_info1, col_info2, col_info3, col_info4 = st.columns(4)

with col_info1:
    completion_rate = (answered_count / num_questions) * 100 if answered_count > 0 else 0
    st.metric("Completed", f"{completion_rate:.0f}%")

with col_info2:
    remaining = num_questions - answered_count
    st.metric("Remaining", remaining)

with col_info3:
    if is_last_question:
        st.metric("Status", "Final")
    elif answered_count == num_questions:
        st.metric("Status", "Done")
    else:
        st.metric("Status", f"{i+1}/{num_questions}")

with col_info4:
    if answered_count == num_questions:
        st.metric("Submit", "✅ Ready")
    elif answered_count > 0:
        st.metric("Submit", "🟡 Partial")
    else:
        st.metric("Submit", "❌ No")

# --- Quick Stats ---
if answered_count > 0:
    st.info(f"📊 **Quick Stats**: You've answered {answered_count} questions. {remaining} questions remaining. You can submit anytime!")
    
    if answered_count < num_questions:
        st.warning(f"⚠️ Note: You haven't answered all questions. You can still submit with {answered_count}/{num_questions} answered.")

# --- Compact Question Navigator ---
if not st.session_state.quiz_submitted:
    questions_per_row = 10
    num_rows = (num_questions + questions_per_row - 1) // questions_per_row
    
    for row_num in range(num_rows):
        start_q = row_num * questions_per_row
        end_q = min((row_num + 1) * questions_per_row, num_questions)
        
        cols = st.columns(questions_per_row)
        
        for col_idx, q_num in enumerate(range(start_q, end_q)):
            with cols[col_idx]:
                is_current = q_num == i
                is_answered = q_num in st.session_state.user_answers
                
                has_scenario = False
                scenario_value = str(questions_df.iloc[q_num].get('Scenario', ''))
                if scenario_value.strip() and scenario_value != 'nan':
                    has_scenario = True
                
                label = f"{q_num + 1}"
                if has_scenario:
                    label = f"📖{q_num + 1}"
                
                button_type = "primary" if is_current else "secondary"
                
                if st.button(label, key=f"nav_{q_num}", type=button_type, use_container_width=True):
                    st.session_state.current_q = q_num
                    st.rerun()

# --- Results page after submission ---
if st.session_state.quiz_submitted:
    # Show auto-submission message if time was up
    if st.session_state.time_up and st.session_state.auto_submitted:
        st.error("⏰ **TIME'S UP!** Your exam has been automatically submitted.")
    
    # Calculate score
    correct_count = 0
    results = []
    
    for q_index in range(num_questions):
        row = questions_df.iloc[q_index]
        user_answer = st.session_state.user_answers.get(q_index, "Not answered")
        correct_answer = str(row['CorrectAnswer'])
        is_correct = user_answer == correct_answer
        
        if is_correct:
            correct_count += 1
        
        results.append({
            'Question Number': q_index + 1,
            'Scenario': str(row.get('Scenario', '')),
            'Question': str(row['Question']),
            'Your Answer': user_answer,
            'Correct Answer': correct_answer,
            'Status': '✅ Correct' if is_correct else '❌ Incorrect'
        })
    
    # Calculate percentage
    percentage_score = (correct_count / num_questions) * 100
    pass_threshold = 75
    
    # Display results
    st.write("## Quiz Submitted! Here are your results:")
    
    answered_count = len(st.session_state.user_answers)
    st.write(f"**Submission Summary**: You submitted with {answered_count}/{num_questions} questions answered.")
    
    if percentage_score >= pass_threshold:
        st.balloons()
        st.success(f"🎉 **CONGRATULATIONS!** 🎉")
        st.success(f"## Final Score: {correct_count}/{num_questions} ({percentage_score:.1f}%)")
        st.success("### 🏆 You have PASSED the assessment! 🏆")
    else:
        st.error(f"## Final Score: {correct_count}/{num_questions} ({percentage_score:.1f}%)")
        st.warning(f"### ❌ You did not pass this time")
        st.info(f"**Required pass mark:** {pass_threshold}%")
        st.info(f"**Your score:** {percentage_score:.1f}%")
        st.info("**Keep practicing and try again!**")
    
    # Progress bar showing pass/fail status
    st.write("### Pass/Fail Status:")
    if percentage_score >= pass_threshold:
        st.progress(percentage_score/100, text=f"PASSED - {percentage_score:.1f}%")
    else:
        st.progress(percentage_score/100, text=f"FAILED - {percentage_score:.1f}% (Need {pass_threshold}%)")
    
    # Display all questions and answers
    st.write("## Detailed Results:")
    
    for result in results:
        with st.container():
            # Display scenario if available
            scenario_value = result['Scenario']
            if scenario_value.strip() and scenario_value != 'nan':
                scenario_paragraphs = [p.strip() for p in scenario_value.split('\n') if p.strip()]
                
                scenario_html = '''
                <div class="scenario-container">
                    <div class="scenario-header">📖 SCENARIO</div>
                '''
                
                for paragraph in scenario_paragraphs:
                    scenario_html += f'<div class="scenario-content">{paragraph}</div>'
                
                scenario_html += '</div>'
                st.markdown(scenario_html, unsafe_allow_html=True)
            
            st.write(f"### Question {result['Question Number']}")
            st.write("**Question:**")
            
            # Display question with paragraphs in results
            question_text = result['Question']
            question_paragraphs = [p.strip() for p in question_text.split('\n') if p.strip()]
            
            question_html = '<div class="question-container">'
            for paragraph in question_paragraphs:
                question_html += f'<div class="question-paragraph">{paragraph}</div>'
            question_html += '</div>'
            
            st.markdown(question_html, unsafe_allow_html=True)
            
            # Color coding for answers
            st.write("**Your Answer:**")
            if result['Status'] == '✅ Correct':
                st.success(f"{result['Your Answer']} ✅")
                st.success(f"**Correct Answer:** {result['Correct Answer']}")
            else:
                st.error(f"{result['Your Answer']} ❌")
                st.success(f"**Correct Answer:** {result['Correct Answer']}")
            
            # Show hint if available
            if result['Status'] == '❌ Incorrect':
                hint = questions_df.iloc[result['Question Number']-1].get('Hint')
                if pd.notna(hint) and str(hint).strip():
                    st.info(f"💡 **Hint:** {hint}")
            
            st.write("---")
    
    # Option to restart
    st.write("---")
    if st.button("Start New Quiz", type="primary"):
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.shuffled_options = {}
        st.session_state.quiz_completed = False
        st.session_state.quiz_submitted = False
        st.session_state.exam_started = False
        st.session_state.exam_start_time = None
        st.session_state.time_up = False
        st.session_state.auto_submitted = False
        st.rerun()
