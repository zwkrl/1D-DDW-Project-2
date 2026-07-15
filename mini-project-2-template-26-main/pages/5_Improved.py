import math
import time
from html import escape

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Improved Challenge",
    layout="wide",
)


DATABASE_FILE = "Mini Project 2 - Instructor Database.xlsx"
REQUIRED_SHEETS = (
    "Users",
    "Questions",
    "Challenges",
    "Challenge-Users",
    "Timerecord",
)
DIFFICULTY_ORDER = ("Easy", "Intermediate", "Hard")
DIFFICULTY_DESCRIPTIONS = {
    "Easy": "One basic addition or subtraction operation.",
    "Intermediate": "Multiple operations or multiplication and division.",
    "Hard": "Brackets or a longer multi-step calculation.",
}


def apply_dashboard_theme():
    """Apply the dark neon dashboard styling for this page."""
    st.markdown(
        """
        <style>
        :root {
            --panel: rgba(10, 18, 31, 0.88);
            --panel-soft: rgba(16, 25, 42, 0.78);
            --border: rgba(148, 163, 184, 0.16);
            --purple: #a855f7;
            --violet: #7c3aed;
            --blue: #3b82f6;
            --green: #4ade80;
            --text-soft: #94a3b8;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 62% 4%, rgba(59, 130, 246, 0.10), transparent 26rem),
                radial-gradient(circle at 18% 18%, rgba(168, 85, 247, 0.10), transparent 24rem),
                #030812;
            color: #f8fafc;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] label,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stMetricLabel"] p,
        [data-testid="stCaptionContainer"] p {
            color: #cbd5e1 !important;
        }

        [data-testid="stAppViewContainer"] h1,
        [data-testid="stAppViewContainer"] h2,
        [data-testid="stAppViewContainer"] h3 {
            color: #f8fafc !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #050b16 0%, #07101c 100%);
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] a {
            color: #cbd5e1 !important;
        }

        [data-testid="stSidebarNav"] li[aria-selected="true"] {
            background: linear-gradient(90deg, rgba(79, 70, 229, 0.34), rgba(168, 85, 247, 0.22));
            border: 1px solid rgba(168, 85, 247, 0.26);
            border-radius: 0.55rem;
        }

        .block-container {
            max-width: 1240px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }

        .improved-brand {
            color: #f8fafc;
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            margin: 0.25rem 0 1.25rem;
        }

        .improved-brand span {
            color: var(--purple);
            margin-right: 0.4rem;
        }

        .hero-title {
            color: #f8fafc;
            font-size: clamp(2.4rem, 5vw, 4.6rem);
            font-style: italic;
            font-weight: 900;
            letter-spacing: -0.055em;
            line-height: 1.02;
            margin: 0.5rem 0 0.75rem;
        }

        .hero-title span {
            background: linear-gradient(90deg, #c026d3, #8b5cf6, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-copy {
            color: #cbd5e1;
            font-size: 1.12rem;
            margin-bottom: 1.6rem;
        }

        .hero-copy strong {
            color: #a78bfa;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(145deg, var(--panel), var(--panel-soft));
            border: 1px solid var(--border) !important;
            border-radius: 1.1rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.24);
        }

        div[data-testid="stMetric"] {
            background: rgba(15, 23, 42, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.10);
            border-radius: 0.9rem;
            padding: 0.75rem 1rem;
        }

        div[data-testid="stMetricValue"] {
            color: var(--green);
        }

        div[data-testid="stMetricValue"],
        div[data-testid="stMetricValue"] * {
            color: #4ade80 !important;
            -webkit-text-fill-color: #4ade80 !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #cbd5e1 !important;
        }

        .section-label {
            color: #a78bfa;
            font-size: 0.75rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            margin-bottom: 0.3rem;
        }

        .step-heading {
            align-items: center;
            display: flex;
            gap: 0.85rem;
            margin: 0.15rem 0 1rem;
        }

        .step-number {
            align-items: center;
            background: linear-gradient(145deg, #4f46e5, #a855f7);
            border: 1px solid rgba(196, 181, 253, 0.35);
            border-radius: 0.8rem;
            box-shadow: 0 0 24px rgba(139, 92, 246, 0.22);
            color: white;
            display: flex;
            flex: 0 0 2.55rem;
            font-size: 1rem;
            font-weight: 850;
            height: 2.55rem;
            justify-content: center;
        }

        .step-kicker {
            color: #a78bfa;
            font-size: 0.7rem;
            font-weight: 850;
            letter-spacing: 0.14em;
            line-height: 1.2;
        }

        .step-title {
            color: #f8fafc;
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            line-height: 1.3;
        }

        .supporting-copy {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 0.85rem;
        }

        .expression-card {
            background:
                radial-gradient(circle at 88% 45%, rgba(124, 58, 237, 0.22), transparent 12rem),
                rgba(8, 15, 28, 0.90);
            border: 1px solid rgba(139, 92, 246, 0.24);
            border-radius: 1rem;
            margin: 0.8rem 0 1rem;
            padding: 1.35rem 1.5rem;
        }

        .expression-card .label {
            color: #8b5cf6;
            font-size: 0.8rem;
            font-weight: 800;
            letter-spacing: 0.12em;
        }

        .expression-card .expression {
            color: #f8fafc;
            font-size: clamp(2rem, 4vw, 3.2rem);
            font-weight: 800;
            letter-spacing: 0.04em;
            margin-top: 0.35rem;
        }

        .status-chip {
            background: rgba(124, 58, 237, 0.14);
            border: 1px solid rgba(168, 85, 247, 0.25);
            border-radius: 999px;
            color: #c4b5fd;
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 700;
            padding: 0.25rem 0.7rem;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="input"] > div {
            background: rgba(8, 15, 28, 0.92);
            border-color: rgba(139, 92, 246, 0.34);
        }

        div[data-baseweb="select"] *,
        [data-testid="stSelectbox"] * {
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] svg {
            fill: #a78bfa !important;
        }

        div[data-baseweb="input"] input {
            color: #f8fafc !important;
            -webkit-text-fill-color: #f8fafc !important;
        }

        div[data-baseweb="input"] input::placeholder,
        [data-testid="stNumberInput"] input::placeholder,
        input[placeholder]::placeholder {
            color: #f1f5f9 !important;
            -webkit-text-fill-color: #f1f5f9 !important;
            font-weight: 650 !important;
            opacity: 1 !important;
        }

        div[data-baseweb="popover"] > div,
        ul[role="listbox"] {
            background: #0b1220 !important;
            border: 1px solid rgba(139, 92, 246, 0.34) !important;
            box-shadow: 0 20px 55px rgba(0, 0, 0, 0.55) !important;
        }

        li[role="option"] {
            background: #0b1220 !important;
            color: #e2e8f0 !important;
        }

        li[role="option"] > div,
        li[role="option"] span {
            color: #e2e8f0 !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {
            background: linear-gradient(90deg, rgba(79, 70, 229, 0.46), rgba(168, 85, 247, 0.30)) !important;
        }

        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(90deg, #4f46e5, #a855f7);
            border: 0;
            border-radius: 0.8rem;
            color: white;
            font-weight: 750;
            min-height: 2.8rem;
            transition: transform 120ms ease, box-shadow 120ms ease;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            box-shadow: 0 0 28px rgba(168, 85, 247, 0.32);
            color: white;
            transform: translateY(-1px);
        }

        .st-key-cancel_attempt button {
            background: transparent !important;
            border: 1px solid rgba(148, 163, 184, 0.28) !important;
            box-shadow: none !important;
            color: #cbd5e1 !important;
        }

        .st-key-cancel_attempt button:hover {
            background: rgba(148, 163, 184, 0.08) !important;
            border-color: rgba(196, 181, 253, 0.50) !important;
        }

        [data-testid="stAlert"] {
            border-radius: 0.9rem;
        }

        [data-testid="stAlert"] p {
            color: #e0e7ff !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_stopwatch_time(elapsed_time):
    """Format elapsed seconds as minutes, seconds, and hundredths."""
    total_hundredths = round(elapsed_time * 100)
    minutes, remaining_hundredths = divmod(total_hundredths, 6000)
    seconds, hundredths = divmod(remaining_hundredths, 100)
    return f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"


def display_live_timer(start_time):
    """Render the active stopwatch continuously until the challenge ends."""
    start_time_ms = int(start_time * 1000)
    timer_element_id = f"improved-live-timer-{start_time_ms}"
    initial_time = format_stopwatch_time(max(0, time.time() - start_time))
    st.html(
        f"""
        <div id="{timer_element_id}" class="timer-card">
            <span class="timer-icon">◷</span>
            <span class="timer-value">{initial_time}</span>
        </div>
        <style>
            #{timer_element_id} {{
                align-items: center;
                background: rgba(124, 58, 237, 0.14);
                border: 1px solid rgba(168, 85, 247, 0.28);
                border-radius: 14px;
                color: #c084fc;
                display: flex;
                font: 800 22px system-ui, sans-serif;
                gap: 9px;
                justify-content: center;
                min-height: 52px;
                width: 175px;
            }}
            #{timer_element_id} .timer-icon {{ font-size: 26px; }}
        </style>
        <script>
            (() => {{
            const startedAt = {start_time_ms};
            const timer = document.querySelector("#{timer_element_id} .timer-value");

            function updateTimer() {{
                const elapsedMilliseconds = Math.max(
                    0,
                    Date.now() - startedAt,
                );
                const minutes = String(
                    Math.floor(elapsedMilliseconds / 60000),
                ).padStart(2, "0");
                const seconds = String(
                    Math.floor((elapsedMilliseconds % 60000) / 1000),
                ).padStart(2, "0");
                const hundredths = String(
                    Math.floor((elapsedMilliseconds % 1000) / 10),
                ).padStart(2, "0");
                timer.textContent = `${{minutes}}:${{seconds}}.${{hundredths}}`;
            }}

            updateTimer();
            if (window.improvedTimerInterval) {{
                clearInterval(window.improvedTimerInterval);
            }}
            window.improvedTimerInterval = setInterval(updateTimer, 50);
            }})();
        </script>
        """,
        width="content",
        unsafe_allow_javascript=True,
    )


def display_paused_timer(elapsed_time):
    """Display the final recorded duration without relying on JavaScript."""
    formatted_time = format_stopwatch_time(elapsed_time)

    st.html(
        f"""
        <div id="improved-paused-timer">
            <span class="timer-icon">&#9719;</span>
            <span>{formatted_time}</span>
        </div>
        <style>
            #improved-paused-timer {{
                align-items: center;
                background: rgba(124, 58, 237, 0.14);
                border: 1px solid rgba(168, 85, 247, 0.35);
                border-radius: 14px;
                color: #c084fc;
                display: flex;
                font: 800 22px system-ui, sans-serif;
                gap: 9px;
                justify-content: center;
                min-height: 52px;
                width: 175px;
            }}
            #improved-paused-timer .timer-icon {{ font-size: 26px; }}
        </style>
        """,
        width="content",
    )


def read_tables(filename):
    """Read the tables needed by the challenge page."""
    return {
        sheet_name: pd.read_excel(filename, sheet_name=sheet_name)
        for sheet_name in REQUIRED_SHEETS
    }


def classify_difficulty(expression):
    """Classify a challenge using its operation count and grouping."""
    expression = str(expression)
    operator_count = sum(expression.count(operator) for operator in "+-*/")
    has_brackets = "(" in expression or ")" in expression
    has_advanced_operator = "*" in expression or "/" in expression

    if has_brackets or operator_count >= 4:
        return "Hard"
    if has_advanced_operator or operator_count >= 2:
        return "Intermediate"
    return "Easy"


def get_available_challenges(user_id, associations, challenges, questions):
    """Return the questions assigned to one user."""
    user_associations = associations.loc[
        associations["user_id"] == user_id,
        ["challenge_id"],
    ]
    available = user_associations.merge(
        challenges[["id", "question_id"]],
        left_on="challenge_id",
        right_on="id",
        how="inner",
    )
    available = available.merge(
        questions[["id", "expression", "answer"]],
        left_on="question_id",
        right_on="id",
        how="inner",
        suffixes=("_challenge", "_question"),
    )
    available = available.drop_duplicates(subset="challenge_id").copy()
    available["difficulty"] = available["expression"].map(classify_difficulty)
    available["difficulty_rank"] = available["difficulty"].map(
        {difficulty: rank for rank, difficulty in enumerate(DIFFICULTY_ORDER)}
    )
    return available.sort_values(["difficulty_rank", "challenge_id"])


def next_record_id(records):
    """Create an ID safely even if rows were previously deleted."""
    if records.empty:
        return 0
    return int(records["id"].max()) + 1


def save_time_record(filename, records, challenge_id, user_id, elapsed_time):
    """Append a completed attempt and update the existing Excel sheet."""
    new_record = pd.DataFrame(
        [
            {
                "id": next_record_id(records),
                "challenge_id": challenge_id,
                "user_id": user_id,
                "elapsed_time": elapsed_time,
            }
        ]
    )
    updated_records = pd.concat([records, new_record], ignore_index=True)

    with pd.ExcelWriter(filename, mode="a", if_sheet_exists="replace") as writer:
        updated_records.to_excel(writer, sheet_name="Timerecord", index=False)


def initialize_state():
    """Set up state that must survive Streamlit reruns."""
    defaults = {
        "improved_active_challenge_id": None,
        "improved_active_user_id": None,
        "improved_correct_answer": None,
        "improved_expression": None,
        "improved_difficulty": None,
        "improved_start_time": None,
        "improved_submit_time": None,
        "improved_last_elapsed_time": None,
        "improved_feedback": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_active_challenge():
    """Reset the current attempt without changing the selected user."""
    st.session_state["improved_active_challenge_id"] = None
    st.session_state["improved_active_user_id"] = None
    st.session_state["improved_correct_answer"] = None
    st.session_state["improved_expression"] = None
    st.session_state["improved_difficulty"] = None
    st.session_state["improved_start_time"] = None
    st.session_state["improved_submit_time"] = None
    if "improved_answer" in st.session_state:
        del st.session_state["improved_answer"]


def start_challenge(challenge):
    """Store the selected challenge and start its timer."""
    st.session_state["improved_active_challenge_id"] = int(
        challenge["challenge_id"]
    )
    st.session_state["improved_active_user_id"] = int(
        st.session_state["improved_user_id"]
    )
    st.session_state["improved_correct_answer"] = float(challenge["answer"])
    st.session_state["improved_expression"] = str(challenge["expression"])
    st.session_state["improved_difficulty"] = str(challenge["difficulty"])
    st.session_state["improved_start_time"] = time.time()
    st.session_state["improved_submit_time"] = None
    st.session_state["improved_last_elapsed_time"] = None
    st.session_state["improved_feedback"] = None
    if "improved_answer" in st.session_state:
        del st.session_state["improved_answer"]


def capture_submit_time():
    """Capture the click time before Streamlit processes the submitted answer."""
    if st.session_state.get("improved_submit_time") is None:
        st.session_state["improved_submit_time"] = time.time()


def display_feedback():
    """Show feedback once after a rerun."""
    feedback = st.session_state.get("improved_feedback")
    if feedback is None:
        return

    message_type, message = feedback
    if message_type == "success":
        st.success(message)
        last_elapsed_time = st.session_state.get("improved_last_elapsed_time")
        if last_elapsed_time is not None:
            st.caption("STOPWATCH PAUSED AT SUBMISSION")
            display_paused_timer(last_elapsed_time)
    elif message_type == "error":
        st.error(message)
    else:
        st.info(message)
    st.session_state["improved_feedback"] = None
    st.session_state["improved_last_elapsed_time"] = None


apply_dashboard_theme()

st.markdown(
    """
    <div class="hero-title">Ready to <span>level up?</span></div>
    <div class="hero-copy">
        Pick a challenge, beat the timer, and <strong>prove your skills.</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    tables = read_tables(DATABASE_FILE)
except FileNotFoundError:
    st.error(f"Database file not found: {DATABASE_FILE}")
    st.stop()
except ValueError as error:
    st.error(f"The Excel database is missing required data: {error}")
    st.stop()

users = tables["Users"]
questions = tables["Questions"]
challenges = tables["Challenges"]
associations = tables["Challenge-Users"]
time_records = tables["Timerecord"]

if users.empty:
    st.warning("No users exist yet. Create a user on the Users page first.")
    st.stop()

initialize_state()

user_names = {
    int(row["id"]): f'{row["name"]} (@{row["username"]})'
    for _, row in users.iterrows()
}

with st.container(border=True):
    profile_column, available_column, completed_column = st.columns([2.2, 1, 1])

    with profile_column:
        st.markdown(
            """
            <div class="step-heading">
                <div class="step-number">1</div>
                <div>
                    <div class="step-kicker">PLAYER</div>
                    <div class="step-title">Choose who's playing</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        current_user_id = st.selectbox(
            "Choose player",
            options=list(user_names),
            format_func=lambda user_id: user_names[user_id],
            key="improved_user_id",
            label_visibility="collapsed",
        )
        current_user_id = int(current_user_id)

    available_challenges = get_available_challenges(
        current_user_id,
        associations,
        challenges,
        questions,
    )
    user_time_records = time_records.loc[
        time_records["user_id"] == current_user_id
    ]

    with available_column:
        st.metric("Available challenges", len(available_challenges))
    with completed_column:
        st.metric("Completed attempts", len(user_time_records))

current_user = users.loc[users["id"] == current_user_id].iloc[0]
with st.sidebar:
    st.caption("CURRENT PLAYER")
    st.markdown(f'**{escape(str(current_user["name"]))}**')
    st.caption(f'@{escape(str(current_user["username"]))}')
    st.divider()

active_user_id = st.session_state["improved_active_user_id"]
if active_user_id is not None and active_user_id != current_user_id:
    clear_active_challenge()
    st.session_state["improved_feedback"] = (
        "info",
        "The previous attempt was cancelled because you changed users.",
    )

display_feedback()

if available_challenges.empty:
    st.info("This user has no assigned challenges yet.")
    st.stop()

if st.session_state["improved_active_challenge_id"] is None:
    difficulty_options = [
        difficulty
        for difficulty in DIFFICULTY_ORDER
        if difficulty in set(available_challenges["difficulty"])
    ]
    difficulty_counts = available_challenges["difficulty"].value_counts()

    with st.container(border=True):
        st.markdown(
            """
            <div class="step-heading">
                <div class="step-number">2</div>
                <div>
                    <div class="step-kicker">CHALLENGE</div>
                    <div class="step-title">Choose your next challenge</div>
                </div>
            </div>
            <div class="supporting-copy">
                Pick a difficulty first. The expression stays hidden until the
                stopwatch starts.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="section-label">1. DIFFICULTY LEVEL</div>',
            unsafe_allow_html=True,
        )
        selected_difficulty = st.selectbox(
            "Choose difficulty",
            options=difficulty_options,
            format_func=lambda difficulty: (
                f"{difficulty} ({difficulty_counts[difficulty]} available)"
            ),
            label_visibility="collapsed",
            key="improved_difficulty_filter",
        )
        st.caption(DIFFICULTY_DESCRIPTIONS[selected_difficulty])

        filtered_challenges = available_challenges.loc[
            available_challenges["difficulty"] == selected_difficulty
        ]
        challenge_labels = {
            int(challenge_id): f"Challenge {int(challenge_id) + 1}"
            for challenge_id in filtered_challenges["challenge_id"]
        }

        st.markdown(
            '<div class="section-label">2. CHALLENGE</div>',
            unsafe_allow_html=True,
        )
        selected_challenge_id = st.selectbox(
            "Choose a challenge",
            options=list(challenge_labels),
            format_func=lambda challenge_id: challenge_labels[challenge_id],
            label_visibility="collapsed",
            key="improved_challenge_filter",
        )
        start_clicked = st.button(
            "Start challenge",
            use_container_width=True,
            key="start_improved_challenge",
        )

    if start_clicked:
        selected_challenge = filtered_challenges.loc[
            filtered_challenges["challenge_id"] == selected_challenge_id
        ].iloc[0]
        start_challenge(selected_challenge)
        st.rerun()
else:
    challenge_number = st.session_state["improved_active_challenge_id"] + 1
    active_difficulty = escape(str(st.session_state["improved_difficulty"]))
    with st.container(border=True):
        title_column, timer_column = st.columns([4, 1])
        with title_column:
            st.markdown(
                f"""
                <div class="step-heading">
                    <div class="step-number">3</div>
                    <div>
                        <div class="step-kicker">ACTIVE CHALLENGE</div>
                        <div class="step-title">Challenge {challenge_number}</div>
                    </div>
                </div>
                <span class="status-chip">{active_difficulty} &bull; TIMER RUNNING</span>
                """,
                unsafe_allow_html=True,
            )
        with timer_column:
            display_live_timer(st.session_state["improved_start_time"])

        expression = escape(str(st.session_state["improved_expression"]))
        st.markdown(
            f"""
            <div class="expression-card">
                <div class="label">CALCULATE</div>
                <div class="expression">{expression}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("ⓘ The timer is running. Solve and submit your answer!")

        with st.form("improved_submit_answer", enter_to_submit=True):
            user_answer = st.text_input(
                "Your answer",
                key="improved_answer",
                placeholder="Type your answer...",
            )
            st.caption("Press Enter or click Submit answer when you're ready.")
            answer_clicked = st.form_submit_button(
                "Submit answer  ➤",
                use_container_width=True,
                on_click=capture_submit_time,
            )

        if st.button("↻  Cancel this attempt", key="cancel_attempt"):
            clear_active_challenge()
            st.session_state["improved_feedback"] = (
                "info",
                "The challenge was cancelled. No time was recorded.",
            )
            st.rerun()

    if answer_clicked:
        if not user_answer.strip():
            st.session_state["improved_submit_time"] = None
            st.session_state["improved_feedback"] = (
                "error",
                "Enter an answer before submitting.",
            )
            st.rerun()

        try:
            numeric_answer = float(user_answer)
        except ValueError:
            st.session_state["improved_submit_time"] = None
            st.session_state["improved_feedback"] = (
                "error",
                "Enter a valid numerical answer.",
            )
            st.rerun()

        correct_answer = st.session_state["improved_correct_answer"]
        is_correct = math.isclose(
            numeric_answer,
            correct_answer,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )

        if not is_correct:
            st.session_state["improved_submit_time"] = None
            st.session_state["improved_feedback"] = (
                "error",
                "That answer is not correct yet. Try again—the timer is still running.",
            )
            st.rerun()

        start_time = st.session_state["improved_start_time"]
        submit_time = st.session_state["improved_submit_time"] or time.time()
        elapsed_time = round(
            max(0, submit_time - start_time),
            2,
        )
        try:
            save_time_record(
                DATABASE_FILE,
                time_records,
                st.session_state["improved_active_challenge_id"],
                current_user_id,
                elapsed_time,
            )
        except PermissionError:
            st.error(
                "The database could not be updated. Close the Excel file and submit again."
            )
        else:
            clear_active_challenge()
            st.session_state["improved_last_elapsed_time"] = elapsed_time
            st.session_state["improved_feedback"] = (
                "success",
                f"Correct! Your recorded time is {elapsed_time:.2f} seconds.",
            )
            st.rerun()
