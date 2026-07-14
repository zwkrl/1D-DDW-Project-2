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
    expression = expression.strip()

    if expression == "":
        return False, "Enter a mathematical expression."

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

st.header("Create New Question")
with st.form("new_question"):
    expression = st.text_input("Write a Math expression:")
    expression

    # TODO: Task 2
    # create an object instance of EvaluateExpression class
    # pass on the math expression to the object
    #
    # evaluator = None
    ### your code ###
    evaluator = EvaluateExpression(expression)

    # TODO: Task 3
    # call the evaluate() method of the EvaluateExpression object
    # and store it
    #
    # answer = None
    ### your code ###
    answer = evaluator.evaluate()

    st.write("Answer:", answer)

    selected_users = st.multiselect("Select Users to answer this challenge.", users["username"])
    submit = st.form_submit_button("Create Question")

if submit and expression and expression != "" and selected_users != []:
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

            


