import streamlit as st
import pandas as pd
import random
import requests
import io
import time

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
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        border-left: 6px solid #2196F3;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .question-paragraph {
        line-height: 1.6;
        margin-bottom: 15px;
        font-size: 1.1em;
        color: var(--text-color);
    }
    .answer-section {
        margin-top: 25px;
        padding-top: 20px;
        border-top: 2px solid var(--border-color);
    }
    .answer-label {
        font-weight: bold;
        color: var(--text-color);
        margin-bottom: 15px;
        font-size: 1.1em;
        display: block;
    }
    
    /* Custom radio button styling */
    .stRadio > div {
        background-color: var(--background-color);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    /* Custom option styling */
    .option-item {
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 6px;
        border: 1px solid transparent;
        transition: all 0.3s ease;
        background-color: var(--background-color);
    }
    
    .option-item:hover {
        background-color: rgba(33, 150, 243, 0.1);
        border-color: #2196F3;
        transform: translateY(-1px);
    }
    
    .option-item.selected {
        background-color: rgba(33, 150, 243, 0.15);
        border-color: #2196F3;
        box-shadow: 0 2px 4px rgba(33, 150, 243, 0.2);
    }
    
    /* Radio button label styling */
    .stRadio label {
        font-size: 1em;
        color: var(--text-color) !important;
        padding: 10px;
        border-radius: 6px;
        transition: all 0.3s ease;
    }
    
    .stRadio label:hover {
        background-color: rgba(33, 150, 243, 0.1);
    }
    
    .stRadio [data-testid="stMarkdownContainer"] {
        color: var(--text-color) !important;
    }
    
    /* Dark mode variables */
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #0e1117;
            --secondary-background-color: #1e1e1e;
            --text-color: #fafafa;
            --border-color: #444;
        }
    }
    @media (prefers-color-scheme: light) {
        :root {
            --background-color: #ffffff;
            --secondary-background-color: #f8f9fa;
            --text-color: #31333F;
            --border-color: #ddd;
        }
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
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #2196F3;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Add rate limiting protection
if 'last_request' not in st.session_state:
    st.session_state.last_request = time.time()
else:
    current_time = time.time()
    if current_time - st.session_state.last_request < 1:  # 1 second between requests
        time.sleep(0.5)
    st.session_state.last_request = current_time

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

# Call initialization function
initialize_session_state()

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

# --- Display the actual question with answer section inside the box ---
question_text = str(row['Question'])

# Split question into paragraphs and display each as separate markdown
question_paragraphs = [p.strip() for p in question_text.split('\n') if p.strip()]

# Find the index of previously selected answer
previous_answer = st.session_state.user_answers.get(i)
if previous_answer is not None:
    try:
        selected_index = shuffled_options.index(previous_answer)
    except ValueError:
        selected_index = None
else:
    selected_index = None

# Create a container for the question and answer section
with st.container():
    # Display question in a styled container with answer section inside
    question_html = '''
    <div class="question-container">
        <div style="font-weight: bold; margin-bottom: 20px; color: var(--text-color); font-size: 1.2em;">Question:</div>
    '''
    
    for paragraph in question_paragraphs:
        question_html += f'<div class="question-paragraph">{paragraph}</div>'
    
    question_html += '''
        <div class="answer-section">
            <div class="answer-label">📝 Choose your answer:</div>
    '''
    
    st.markdown(question_html, unsafe_allow_html=True)
    
    # Add some spacing before the options
    st.markdown('<div style="margin-top: 10px;"></div>', unsafe_allow_html=True)
    
    # Display radio button inside the question container with custom styling
    user_answer = st.radio("", 
                           shuffled_options, 
                           index=selected_index,
                           key=f"q{i}",
                           label_visibility="collapsed")
    
    # Close the question container HTML
    st.markdown('</div></div>', unsafe_allow_html=True)

# Store the selected option
if user_answer is not None:
    st.session_state.user_answers[i] = user_answer

# --- Navigation buttons ---
st.markdown("---")
st.write("**Navigation:**")

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 1])
with nav_col1:
    if st.button("⬅️ Previous", disabled=(i == 0), use_container_width=True):
        st.session_state.current_q -= 1
        st.rerun()
with nav_col2:
    if st.button("🔄 Restart", use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.shuffled_options = {}
        st.session_state.quiz_completed = False
        st.session_state.quiz_submitted = False
        st.rerun()
with nav_col3:
    if is_last_question:
        if st.button("Next ➡️", disabled=True, use_container_width=True):
            pass
    else:
        if st.button("Next ➡️", use_container_width=True):
            st.session_state.current_q += 1
            st.rerun()
with nav_col4:
    answered_count = len(st.session_state.user_answers)
    submit_disabled = answered_count == 0
    submit_label = "✅ Submit Quiz" if answered_count == num_questions else f"Submit ({answered_count}/{num_questions})"
    
    if st.button(submit_label, type="primary", disabled=submit_disabled, use_container_width=True):
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
            icon = "🎯" if is_current_scenario_q else "📖"
            
            if st.button(f"{icon} {label}", key=f"scenario_nav_{current_scenario}_{q_idx}", type=button_type, use_container_width=True):
                st.session_state.current_q = q_idx
                st.rerun()

# --- Progress Section ---
st.write("---")
st.write("**Progress Overview:**")

answered_count = len(st.session_state.user_answers)
progress_percentage = answered_count / num_questions if num_questions > 0 else 0

# Progress bar with better styling
col_prog1, col_prog2 = st.columns([3, 1])
with col_prog1:
    st.progress(progress_percentage, text=f"Progress: {answered_count}/{num_questions} questions answered")
with col_prog2:
    st.metric("Completion", f"{progress_percentage:.1%}")

# --- Quick Stats ---
st.write("**Quick Stats:**")
stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

with stats_col1:
    completion_rate = (answered_count / num_questions) * 100 if answered_count > 0 else 0
    st.metric("Questions Answered", f"{answered_count}/{num_questions}")

with stats_col2:
    remaining = num_questions - answered_count
    st.metric("Remaining", remaining)

with stats_col3:
    if answered_count == num_questions:
        st.metric("Status", "✅ Complete")
    elif answered_count > 0:
        st.metric("Status", "🟡 In Progress")
    else:
        st.metric("Status", "❌ Not Started")

with stats_col4:
    current_position = f"{i+1}/{num_questions}"
    st.metric("Current", current_position)

if answered_count > 0 and answered_count < num_questions:
    st.info(f"📊 You've answered {answered_count} questions. {remaining} questions remaining. You can submit anytime!")
elif answered_count == num_questions:
    st.success("🎉 All questions answered! You're ready to submit your quiz!")

# --- Compact Question Navigator ---
if not st.session_state.quiz_submitted:
    st.write("---")
    st.write("**Question Navigator:**")
    
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
                icon = "🎯" if is_current else ("✅" if is_answered else "📝")
                if has_scenario:
                    icon = "📖" + icon
                
                button_type = "primary" if is_current else "secondary"
                
                if st.button(f"{icon}", key=f"nav_{q_num}", type=button_type, use_container_width=True, 
                           help=f"Question {q_num + 1}" + (" (Current)" if is_current else "") + (" (Answered)" if is_answered else "")):
                    st.session_state.current_q = q_num
                    st.rerun()

# --- Results page after submission ---
if st.session_state.quiz_submitted:
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
    st.write("## 🎯 Quiz Submitted! Here are your results:")
    
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
    if st.button("🔄 Start New Quiz", type="primary", use_container_width=True):
        st.session_state.current_q = 0
        st.session_state.user_answers = {}
        st.session_state.shuffled_options = {}
        st.session_state.quiz_completed = False
        st.session_state.quiz_submitted = False
        st.rerun()