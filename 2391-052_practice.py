import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import random
import requests
import io
import time
import datetime
import html

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

# --- Mangsam Learning visual layer ---
st.markdown("""
<style>
:root {
    --m-bg: #000000;
    --m-panel: #111111;
    --m-control: #151515;
    --m-control-hover: #202020;
    --m-border: #414141;
    --m-ring: #2b2b2b;
    --m-text: #f4f4f4;
    --m-muted: #909090;
}

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    background: var(--m-bg) !important;
    color: var(--m-text) !important;
}

.stApp {
    font-family: Arial, Helvetica, sans-serif !important;
}

[data-testid="stHeader"] {
    background: rgba(0, 0, 0, .96) !important;
}

#MainMenu,
footer,
[data-testid="stToolbar"] {
    visibility: hidden !important;
}

.block-container {
    width: min(1100px, 100%) !important;
    max-width: 1100px !important;
    padding-top: 2.1rem !important;
    padding-bottom: 3rem !important;
}

/* ---------- page header ---------- */

.mangsam-title {
    width: min(760px, 100%);
    margin: 10px auto 24px;
    text-align: center;
}

.mangsam-title .kicker {
    margin-bottom: 8px;
    color: var(--m-muted);
    font-size: .70rem;
    font-weight: 700;
    letter-spacing: .10em;
    text-transform: uppercase;
}

.mangsam-title h1 {
    margin: 0;
    color: #ffffff;
    font-size: clamp(2rem, 4vw, 2.75rem);
    line-height: 1.15;
}

.mangsam-title p {
    margin: 10px 0 0;
    color: #a5a5a5;
    font-size: 1rem;
}

/* ---------- compact utility controls ---------- */

.mangsam-control-label {
    width: min(760px, 100%);
    margin: 14px auto 7px;
    color: #9b9b9b;
    font-size: .70rem;
    font-weight: 800;
    letter-spacing: .08em;
    text-transform: uppercase;
}

.mangsam-timer {
    width: 100%;
    min-height: 42px;
    padding: 0 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    box-sizing: border-box;
    border: 1px solid #303030;
    border-radius: 10px;
    background: #101010;
    color: #f3f3f3;
}

.mangsam-timer .timer-name {
    font-size: .84rem;
    font-weight: 700;
}

.mangsam-timer strong {
    margin-left: auto;
    font-size: 1rem;
    letter-spacing: .03em;
}

.mangsam-timer .timer-note {
    color: var(--m-muted);
    font-size: .74rem;
}

.mangsam-timer.timer-warning {
    border-color: #6f562d;
}

.mangsam-timer.timer-critical {
    border-color: #7f3030;
}

/* ---------- Streamlit controls ---------- */

div[data-testid="stButton"] > button {
    min-height: 42px !important;
    border: 1px solid var(--m-border) !important;
    border-radius: 9px !important;
    background: var(--m-control) !important;
    color: var(--m-text) !important;
    box-shadow: none !important;
    font-weight: 700 !important;
}

div[data-testid="stButton"] > button:hover:not(:disabled) {
    background: var(--m-control-hover) !important;
    border-color: #666666 !important;
}

div[data-testid="stButton"] > button:disabled {
    background: #101010 !important;
    color: #666666 !important;
    border-color: #292929 !important;
}

div[data-testid="stTextInput"] input {
    min-height: 42px !important;
    border: 1px solid var(--m-border) !important;
    border-radius: 9px !important;
    background: var(--m-control) !important;
    color: #ffffff !important;
    box-shadow: none !important;
    font-size: 16px !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #777777 !important;
    box-shadow: 0 0 0 1px #777777 !important;
}

div[data-testid="stTextInput"] input::placeholder {
    color: #777777 !important;
}

/* ---------- question ---------- */

.mangsam-question-meta {
    width: max-content;
    max-width: 100%;
    margin: 20px auto 12px;
    padding: 6px 12px;
    box-sizing: border-box;
    border: 1px solid #292929;
    border-radius: 999px;
    background: #101010;
    color: #ededed;
    font-size: .82rem;
    font-weight: 750;
}

/* One continuous question card: question first, answers directly below. */
.question-container {
    width: 100% !important;
    margin: 0 !important;
    padding: 28px 30px 12px !important;
    box-sizing: border-box !important;
    border: 1px solid #303030 !important;
    border-bottom: 0 !important;
    border-radius: 14px 14px 0 0 !important;
    background: var(--m-panel) !important;
    box-shadow: 0 12px 32px rgba(0, 0, 0, .72) !important;
}

.question-paragraph {
    margin-bottom: 10px !important;
    color: #ffffff !important;
    font-size: 1.32rem !important;
    font-weight: 700 !important;
    line-height: 1.38 !important;
}

.question-paragraph:last-child {
    margin-bottom: 0 !important;
}

.answer-prompt {
    margin-top: 22px;
    color: #a6a6a6;
    font-size: .78rem;
    font-weight: 700;
}

/* Streamlit defaults radio widgets to content-width. Force the whole answer
   area to stretch so it forms the lower half of the question card. */
div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {
    width: 100% !important;
    max-width: 100% !important;
}

div[data-testid="stRadio"] {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 0 18px !important;
    padding: 0 30px 28px !important;
    box-sizing: border-box !important;
    border: 1px solid #303030 !important;
    border-top: 0 !important;
    border-radius: 0 0 14px 14px !important;
    background: var(--m-panel) !important;
}

div[data-testid="stRadio"] [role="radiogroup"] {
    width: 100% !important;
    max-width: 100% !important;
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) !important;
    gap: 10px !important;
}

div[data-testid="stRadio"] [role="radiogroup"] > * {
    width: 100% !important;
    max-width: 100% !important;
}

div[data-testid="stRadio"] [role="radiogroup"] label {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 50px !important;
    margin: 0 !important;
    padding: 13px 15px !important;
    display: flex !important;
    align-items: center !important;
    box-sizing: border-box !important;
    border: 1px solid #3b3b3b !important;
    border-radius: 9px !important;
    background: #181818 !important;
    color: #f5f5f5 !important;
}

div[data-testid="stRadio"] [role="radiogroup"] label:hover {
    background: #222222 !important;
    border-color: #666666 !important;
}

div[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
    background: #232d38 !important;
    border-color: #6a9bc8 !important;
    box-shadow: inset 0 0 0 1px #6a9bc8 !important;
}

/* ---------- scenarios ---------- */

.scenario-container {
    margin: 0 0 14px !important;
    padding: 18px 20px !important;
    border: 1px solid #343434 !important;
    border-left: 3px solid #777777 !important;
    border-radius: 12px !important;
    background: #0d0d0d !important;
    box-shadow: none !important;
}

.scenario-header {
    color: #d7d7d7 !important;
    font-size: .76rem !important;
    letter-spacing: .06em;
}

.scenario-content {
    color: #e6e6e6 !important;
}

.scenario-progress {
    background: #1b1b1b !important;
    color: #bdbdbd !important;
}

/* ---------- compact progress ---------- */

.mangsam-progress {
    width: max-content;
    max-width: 100%;
    margin: 16px auto 0;
    padding: 6px 12px;
    box-sizing: border-box;
    border: 1px solid #292929;
    border-radius: 999px;
    background: #101010;
    color: #9f9f9f;
    font-size: .78rem;
    font-weight: 700;
}

[data-testid="stCaptionContainer"] {
    color: var(--m-muted) !important;
}

hr {
    border-color: #292929 !important;
}

/* ---------- per-question answer feedback ---------- */

.answer-feedback {
    width: 100%;
    margin: 12px 0 16px;
    padding: 14px 16px;
    box-sizing: border-box;
    border: 1px solid #343434;
    border-radius: 10px;
    background: #111111;
    color: #f5f5f5;
    font-size: .96rem;
    line-height: 1.45;
}

.answer-feedback.correct {
    border-color: #29563a;
    background: #0f1b14;
}

.answer-feedback.wrong {
    border-color: #663838;
    background: #1b1111;
}

.answer-feedback .feedback-title {
    font-weight: 800;
}

.answer-feedback.correct .feedback-title {
    color: #7ddc9a;
}

.answer-feedback.wrong .feedback-title {
    color: #ff9696;
}

.answer-feedback .correct-answer {
    margin-top: 6px;
    color: #ededed;
    font-weight: 700;
}

/* Checked questions stay readable even though the radio is locked. */
div[data-testid="stRadio"] [role="radiogroup"] label:has(input:disabled) {
    opacity: 1 !important;
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 10px !important;
        padding-right: 10px !important;
    }

    .mangsam-title {
        margin-top: 4px;
    }

    .mangsam-title h1 {
        font-size: 1.65rem;
    }

    .mangsam-title p {
        font-size: .88rem;
    }

    .mangsam-timer {
        gap: 8px;
        padding: 0 10px;
    }

    .mangsam-timer .timer-note {
        display: none;
    }

    .question-container {
        padding: 20px 18px 10px !important;
    }

    .question-paragraph {
        font-size: 1.12rem !important;
        line-height: 1.35 !important;
    }

    div[data-testid="stRadio"] {
        padding: 0 18px 20px !important;
    }

    div[data-testid="stRadio"] [role="radiogroup"] > label {
        min-height: 46px !important;
        padding: 11px 12px !important;
    }
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
        st.session_state.checked_questions = set()
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

# --- Mangsam-style header / navigation ---
components.html(
    """
    <style>
        html, body {
            margin: 0;
            background: transparent;
        }

        a {
            min-height: 30px;
            display: inline-flex;
            align-items: center;
            padding: 0;
            border: 0;
            background: transparent;
            color: #f4f4f4;
            font: 700 14px Arial, Helvetica, sans-serif;
            text-decoration: none;
            cursor: pointer;
        }

        a:hover {
            color: #ffffff;
            text-decoration: underline;
        }
    </style>

    <a href="https://learn.mangsam.co.uk/" target="_top">
        &#8592; Mangsam Learning
    </a>
    """,
    height=32,
)

st.markdown(
    """<div class="mangsam-title"><div class="kicker">Skilled Trades · City &amp; Guilds 2391-052</div><h1>Electrical Installations Practice Quiz</h1><p>Initial and Periodic Inspection and Testing</p></div>""",
    unsafe_allow_html=True,
)

# Keep refresh available, but out of the page header so it cannot clip.
refresh_spacer, refresh_col = st.columns([5, 1])
with refresh_col:
    if st.button("Refresh questions", type="secondary", use_container_width=True):
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

# --- Exam Timer Display ---
if not st.session_state.quiz_submitted:
    remaining_time = get_remaining_time()

    timer_status_col, timer_action_col = st.columns([5, 1])

    with timer_status_col:
        if not st.session_state.exam_started:
            st.markdown(
                """
                <div class="mangsam-timer">
                    <span class="timer-name">Exam timer</span>
                    <strong>03:00:00</strong>
                    <span class="timer-note">Not started</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            timer_class = "mangsam-timer"
            if remaining_time < 1800:
                timer_class += " timer-warning"
            if remaining_time < 600:
                timer_class += " timer-critical"

            st.markdown(
                f"""
                <div class="{timer_class}">
                    <span class="timer-name">Exam timer</span>
                    <strong>{format_time(remaining_time)}</strong>
                    <span class="timer-note">3 hour limit</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with timer_action_col:
        if not st.session_state.exam_started:
            if st.button("Start Timer", type="secondary", use_container_width=True):
                start_exam_timer()
                st.rerun()
        else:
            st.markdown(
                '<div style="height:42px"></div>',
                unsafe_allow_html=True,
            )

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

# --- Compact Go to question control ---
if not st.session_state.quiz_submitted:
    st.markdown(
        '<div class="mangsam-control-label">Go to question</div>',
        unsafe_allow_html=True,
    )

    goto_input_col, goto_button_col = st.columns([5, 1])

    with goto_input_col:
        goto_value = st.text_input(
            "Go to question",
            key="goto_question_number",
            label_visibility="collapsed",
            placeholder=f"Question number (1-{num_questions})",
        )

    with goto_button_col:
        goto_clicked = st.button(
            "Go",
            key="goto_button",
            use_container_width=True,
        )

    if goto_clicked:
        try:
            requested_question = int(str(goto_value).strip())
        except ValueError:
            requested_question = 0

        if 1 <= requested_question <= num_questions:
            st.session_state.current_q = requested_question - 1
            st.rerun()
        else:
            st.warning(f"Enter a question number from 1 to {num_questions}.")

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

# --- Compact question status ---
answered_count = len(st.session_state.user_answers)
st.markdown(
    f"""<div class="mangsam-question-meta">Question {i + 1} of {num_questions}</div>""",
    unsafe_allow_html=True,
)

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
question_text = str(row['Question'])

# Split question into paragraphs and display each as separate markdown
question_paragraphs = [p.strip() for p in question_text.split('\n') if p.strip()]

# Display question in a styled container
question_html = '<div class="question-container">'
for paragraph in question_paragraphs:
    question_html += f'<div class="question-paragraph">{paragraph}</div>'
question_html += '<div class="answer-prompt">Choose your answer:</div></div>'

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

# --- Display answer options ---
question_checked = i in st.session_state.checked_questions

user_answer = st.radio(
    "Choose your answer:",
    shuffled_options,
    index=selected_index,
    key=f"q{i}",
    label_visibility="collapsed",
    width="stretch",
    disabled=question_checked,
)

# Store the selected option, but do not reveal the answer until Check Answer.
if user_answer is not None and not question_checked:
    st.session_state.user_answers[i] = user_answer

    # Auto-start timer when the learner begins answering.
    if not st.session_state.exam_started:
        start_exam_timer()

# --- Per-question Check Answer, matching the Mangsam quiz flow ---
check_disabled = user_answer is None or question_checked

if st.button(
    "Check Answer",
    key=f"check_answer_{i}",
    disabled=check_disabled,
    use_container_width=True,
):
    st.session_state.user_answers[i] = user_answer
    st.session_state.checked_questions.add(i)
    st.rerun()

# Reveal only this question's result. No end-of-quiz results dump.
if question_checked:
    selected_answer = st.session_state.user_answers.get(i)
    correct_answer = str(row["CorrectAnswer"])

    if selected_answer == correct_answer:
        st.markdown(
            """
            <div class="answer-feedback correct">
                <div class="feedback-title">Correct</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        safe_correct_answer = html.escape(correct_answer)
        st.markdown(
            f"""
            <div class="answer-feedback wrong">
                <div class="feedback-title">Incorrect</div>
                <div class="correct-answer">Correct answer: {safe_correct_answer}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Mangsam-style question navigation ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button(
        "← Previous Question",
        disabled=(i == 0),
        use_container_width=True,
    ):
        st.session_state.current_q -= 1
        st.rerun()

with col2:
    if st.button(
        "Skip Question",
        disabled=is_last_question,
        use_container_width=True,
    ):
        st.session_state.current_q += 1
        st.rerun()

with col3:
    if st.button(
        "Next Question →",
        disabled=(not question_checked or is_last_question),
        use_container_width=True,
    ):
        st.session_state.current_q += 1
        st.rerun()

# --- Compact progress ---
answered_count = len(st.session_state.user_answers)
remaining = num_questions - answered_count

st.markdown(
    f"""<div class="mangsam-progress">{answered_count} of {num_questions} answered · {remaining} remaining</div>""",
    unsafe_allow_html=True,
)
