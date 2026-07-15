import math
import time

import pandas as pd
import streamlit as st


DATABASE_FILE = "Mini Project 2 - Instructor Database.xlsx"
REQUIRED_SHEETS = (
    "Users",
    "Questions",
    "Challenges",
    "Challenge-Users",
    "Timerecord",
)


def read_tables(filename):
    """Read the tables needed by the challenge page."""
    return {
        sheet_name: pd.read_excel(filename, sheet_name=sheet_name)
        for sheet_name in REQUIRED_SHEETS
    }


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
    return available.drop_duplicates(subset="challenge_id")


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
        "improved_start_time": None,
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
    st.session_state["improved_start_time"] = None
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
    st.session_state["improved_start_time"] = time.time()
    st.session_state["improved_feedback"] = None
    if "improved_answer" in st.session_state:
        del st.session_state["improved_answer"]


def display_feedback():
    """Show feedback once after a rerun."""
    feedback = st.session_state.get("improved_feedback")
    if feedback is None:
        return

    message_type, message = feedback
    if message_type == "success":
        st.success(message)
    elif message_type == "error":
        st.error(message)
    else:
        st.info(message)
    st.session_state["improved_feedback"] = None


st.title("Improved Challenge")
st.caption("Choose your user, start a challenge, then submit your answer.")

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
current_user_id = st.selectbox(
    "1. Who is taking the challenge?",
    options=list(user_names),
    format_func=lambda user_id: user_names[user_id],
    key="improved_user_id",
)
current_user_id = int(current_user_id)

active_user_id = st.session_state["improved_active_user_id"]
if active_user_id is not None and active_user_id != current_user_id:
    clear_active_challenge()
    st.session_state["improved_feedback"] = (
        "info",
        "The previous attempt was cancelled because you changed users.",
    )

display_feedback()

available_challenges = get_available_challenges(
    current_user_id,
    associations,
    challenges,
    questions,
)

if available_challenges.empty:
    st.info("This user has no assigned challenges yet.")
    st.stop()

st.metric("Available challenges", len(available_challenges))

if st.session_state["improved_active_challenge_id"] is None:
    challenge_labels = {
        int(row["challenge_id"]): (
            f'Challenge {int(row["challenge_id"]) + 1}: {row["expression"]}'
        )
        for _, row in available_challenges.iterrows()
    }

    with st.form("improved_select_challenge"):
        selected_challenge_id = st.selectbox(
            "2. Which challenge would you like to attempt?",
            options=list(challenge_labels),
            format_func=lambda challenge_id: challenge_labels[challenge_id],
        )
        start_clicked = st.form_submit_button("Start challenge")

    if start_clicked:
        selected_challenge = available_challenges.loc[
            available_challenges["challenge_id"] == selected_challenge_id
        ].iloc[0]
        start_challenge(selected_challenge)
        st.rerun()
else:
    challenge_number = st.session_state["improved_active_challenge_id"] + 1
    st.subheader(f"Challenge {challenge_number}")
    st.info(f'Calculate: **{st.session_state["improved_expression"]}**')
    st.caption("The timer is running until you submit a correct answer.")

    if st.button("Cancel this attempt"):
        clear_active_challenge()
        st.session_state["improved_feedback"] = (
            "info",
            "The challenge was cancelled. No time was recorded.",
        )
        st.rerun()

    with st.form("improved_submit_answer"):
        user_answer = st.number_input(
            "3. Enter your answer",
            value=None,
            key="improved_answer",
        )
        answer_clicked = st.form_submit_button("Submit answer")

    if answer_clicked:
        if user_answer is None:
            st.session_state["improved_feedback"] = (
                "error",
                "Enter an answer before submitting.",
            )
            st.rerun()

        correct_answer = st.session_state["improved_correct_answer"]
        is_correct = math.isclose(
            float(user_answer),
            correct_answer,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )

        if not is_correct:
            st.session_state["improved_feedback"] = (
                "error",
                "That answer is not correct yet. Try again—the timer is still running.",
            )
            st.rerun()

        elapsed_time = max(
            0,
            int(time.time() - st.session_state["improved_start_time"]),
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
            st.session_state["improved_feedback"] = (
                "success",
                f"Correct! Your recorded time is {elapsed_time} seconds.",
            )
            st.rerun()
