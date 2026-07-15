import streamlit as st
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
filename = ROOT_DIR / "Mini Project 2 - Instructor Database.xlsx"

# Checks the username and full name, returns validation error if wrong
def validate_user(username, name, existing_users):
    errors = []
    # Reject blank usernames
    if not username.strip():
        errors.append("Username cannot be blank.")
    # Reject trailing spaces
    elif username != username.strip():
        errors.append("Username cannot start or end with spaces.")
    # Allow only letters, nums, underscores and hyphens for username
    elif not all(character.isalnum() or character in "_-" for character in username):
        errors.append(
            "Username can contain only letters, numbers, underscores, and hyphens."
        )
    # Check duplicate usernames
    elif username.casefold() in {
        str(existing_username).casefold()
        for existing_username in existing_users["username"]
    }:
        errors.append("That username already exists.")

    if not name.strip():
        errors.append("Full name cannot be blank.")
    elif name != name.strip():
        errors.append("Full name cannot start or end with spaces.")
    elif "  " in name or any(
        character.isspace() and character != " " for character in name
    ):
        errors.append("Use only one space between parts of the full name.")
    elif not all(part.isalpha() for part in name.split(" ")):
        errors.append("Full name can contain only letters and single spaces.")

    return errors


users = pd.read_excel(filename, sheet_name="Users")
users

with st.form("new_user", clear_on_submit=True):
    new_username = st.text_input("New Username:")
    new_name = st.text_input("Full Name:")
    st.caption(
        "Usernames may use letters, numbers, underscores, and hyphens. "
        "Names may use letters with one space between words."
    )

    submit = st.form_submit_button("Update User Table")

if submit:
    # Raise error if any error identified
    validation_errors = validate_user(new_username, new_name, users)
    if validation_errors:
        for validation_error in validation_errors:
            st.error(validation_error)
    else:
        users.loc[len(users)] = [len(users), new_username, new_name]
        with pd.ExcelWriter(filename, mode='a', if_sheet_exists='replace') as f:
            users.to_excel(f, sheet_name="Users", index=False)
        # st.cache_data.clear()
        st.rerun()


