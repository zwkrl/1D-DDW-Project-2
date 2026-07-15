import streamlit as st
from library import EvaluateExpression
import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
filename = ROOT_DIR / "Mini Project 2 - Instructor Database.xlsx"

def read_sheet(sheet_name: str) -> pd.DataFrame:
    """Read one worksheet and stop the page cleanly if it cannot be read."""
    try:
        return pd.read_excel(filename, sheet_name=sheet_name)
    except FileNotFoundError:
        st.error(f"Database file not found: {filename}")
    except ValueError:
        st.error(f'The worksheet "{sheet_name}" could not be found in the database.')
    except PermissionError:
        st.error("The Excel file is open or cannot be accessed. Close it and try again.")
    except Exception as error:
        st.error(f'Unable to read the "{sheet_name}" worksheet: {error}')

    st.stop()


def validate_expression(expression: str) -> tuple[bool, str]:
    """Check that the input follows the expression format supported by the project."""
    if not expression.strip():
        return False, "Math expression cannot be blank."

    if expression != expression.strip():
        return False, "Math expression cannot start or end with spaces."

    if "  " in expression or any(
        character.isspace() and character != " " for character in expression
    ):
        return False, "Use no more than one regular space between values."

    invalid_chars = [
        character
        for character in expression
        if character not in EvaluateExpression.valid_char
    ]
    if invalid_chars:
        return False, "Only numbers, decimal points, brackets, +, -, *, and / are allowed."

    # Split the input into number/operator/bracket tokens without using eval().
    spaced_expression = expression
    for operator in EvaluateExpression.operators:
        spaced_expression = spaced_expression.replace(operator, f" {operator} ")
    tokens = spaced_expression.split()

    if not tokens:
        return False, "Enter a mathematical expression."

    expecting_operand = True
    open_brackets = 0

    for token in tokens:
        if token == "(":
            if not expecting_operand:
                return False, "Add an operator before an opening bracket."
            open_brackets += 1

        elif token == ")":
            if expecting_operand:
                return False, "A closing bracket must come after a number or expression."
            if open_brackets == 0:
                return False, "There is an unmatched closing bracket."
            open_brackets -= 1
            expecting_operand = False

        elif token in "+-*/":
            if expecting_operand:
                return False, "Two operators cannot appear together, and the expression cannot start with an operator."
            expecting_operand = True

        else:
            if not expecting_operand:
                return False, "Add an operator between numbers or before an opening bracket."
            try:
                float(token)
            except ValueError:
                return False, f'"{token}" is not a valid number.'
            expecting_operand = False

    if open_brackets != 0:
        return False, "The brackets are not balanced."

    if expecting_operand:
        return False, "The expression cannot end with an operator."

    return True, ""


def calculate_answer(expression: str) -> tuple[float | None, str]:
    """Validate and evaluate an expression, returning an error message when needed."""
    is_valid, validation_error = validate_expression(expression)
    if not is_valid:
        return None, validation_error

    try:
        evaluator = EvaluateExpression(expression)
        answer = evaluator.evaluate()

        if answer is None:
            return None, "The expression could not be evaluated."

        return float(answer), ""
    except ZeroDivisionError:
        return None, "Division by zero is not allowed."
    except (TypeError, ValueError, IndexError, AttributeError):
        return None, "The expression is incomplete or incorrectly formatted."
    except Exception as error:
        return None, f"The expression could not be evaluated: {error}"


def normalize_expression(expression: str) -> str:
    # Spacing removed so that same formatting is the same as duplicate
    return "".join(expression.split())


def question_exists(expression: str, existing_questions: pd.DataFrame) -> bool:
    # Check if same exp already stored, returns True if any duplicates in the dataframe
    normalized_expression = normalize_expression(expression)
    return any(
        normalize_expression(str(existing_expression)) == normalized_expression
        for existing_expression in existing_questions["expression"]
    )

# Read user table
users = pd.read_excel(filename, sheet_name="Users")

# TODO: Task 1
# read the sheet with the name "Questions"
#
# question_data = None
### your code ###
question_data = pd.read_excel(filename, sheet_name="Questions")

st.header("Questions List")
st.write(question_data)
# Checks expression if already stored in Questions, returns True if it exists
st.header("Create New Question")
expression = st.text_input("Write a Math expression:")
st.caption(
    "Use digits, decimal points, brackets, and the operators +, -, *, or /."
)

answer = None
expression_error = ""
duplicate_question = False

if expression:
    answer, expression_error = calculate_answer(expression)
    if expression_error:
        st.warning(expression_error)
    else:
        st.success(f"Answer preview: {answer:g}")
        duplicate_question = question_exists(expression, question_data)
        if duplicate_question:
            st.warning("This question already exists and cannot be added again.")

selected_users = st.multiselect(
    "Select Users to answer this challenge.",
    users["username"],
)
# Create qn buttnon disabled if qn already exists
submit = st.button("Create Question", disabled=duplicate_question)

submission_is_valid = False

if submit:
    if answer is None and not expression_error:
        answer, expression_error = calculate_answer(expression)

    validation_errors = []

    if expression_error:
        validation_errors.append(expression_error)
    elif question_exists(expression, question_data):
        validation_errors.append(
            "This question already exists and cannot be added again."
        )
    if not selected_users:
        validation_errors.append("Select at least one user for the challenge.")

    if validation_errors:
        for validation_error in validation_errors:
            st.error(validation_error)
    else:
        submission_is_valid = True 
# Returns submission is valid to write into Excel

if submission_is_valid:
    # TODO: Task 4
    # read Challenges and Challenge-Users tables 
    # from the Excel file to update
    #
    # read the Challenges worksheet into challenge_data variable
    # challenge_data = None
    ### your code ###
    challenge_data = pd.read_excel(filename, sheet_name="Challenges")
    #
    # read the Challenge-Users worksheet into assoc_data variable
    # assoc_data = None
    ### your code ###
    assoc_data = pd.read_excel(filename, sheet_name="Challenge-Users")
    
    question_id = len(question_data)
    challenge_id = len(challenge_data)
    assoc_id = len(assoc_data)
    question_data.loc[question_id] = [question_id, expression, answer]
    challenge_data.loc[challenge_id] = [challenge_id, question_id]

    for user in selected_users:
        user_id = int(users.loc[users["username"] == user, "id"].iloc[0])
        assoc_data.loc[assoc_id] = [assoc_id, challenge_id, user_id]
        assoc_id += 1

    with pd.ExcelWriter(filename, mode='a', if_sheet_exists='replace') as f:
        pass
        # TODO: Task 5
        # update the Excel file with the new data
        #
        # update the Questions worksheet
        # question_data.to_excel(...)
        ### your code ###
        question_data.to_excel(f, sheet_name="Questions", index=False)
        
        #
        # update the Challenges worksheet
        # challenge_data.to_excel(...)
        ### your code ###
        challenge_data.to_excel(f, sheet_name="Challenges", index=False)
        #
        # update the Challenge-Users worksheet
        # assoc_data.to_excel(...)
        ### your code ###
        assoc_data.to_excel(f, sheet_name="Challenge-Users", index=False)

    # st.cache_data.clear()
    st.rerun()

            


