"""
CSC111 Project 2: Nxt Movie

Module Description
==================
The user login page built using streamlit, powered by firebase for authentication

Copyright and Usage Information
===============================

The file is expressly provided for the purposes of course assessments for CSC111 at the University of Toronto.
All forms of distribution of this code, whether as given or with any changes, are expressly prohibited.

© 2024 Umair Arham, Abdallah Arham Wajid Mohammed, Sameer Shahed, All Rights Reserved
"""

import streamlit as st
import sql_db


def verify_email(email: str) -> bool:
    """
    Checks if a user with the given email exists in the database.

    Args:
        email (str): The email to check.

    Returns:
        bool: True if the email exists, False otherwise.
    """
    conn = None
    try:
        conn = sql_db.connect_to_db()
        cursor = conn.cursor()

        # Query to check if email exists
        query = "SELECT 1 FROM users WHERE email = ?"
        cursor.execute(query, email)
        result = cursor.fetchone()
        return result is not None

    except Exception as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        # Ensure the database connection is closed
        if 'conn' in locals() and conn:
            conn.close()


def sign_in_with_password(email: str, password: str):
    """
    Takes in an email and password, and uses the firebase authenticator to verify the login credentials (contained in a
    .env file). Returns the json object associated with email if login is successful, otherwise displays a warning on
    the streamlit application.
    False
    """

    try:
        cursor = sql_db.connect_to_db().cursor()
        query = "SELECT password FROM users WHERE email = ?"
        cursor.execute(query, email)
        db_password = cursor.fetchone()[0]
        cursor.close()

    except Exception as e:
        return False

    return db_password == password


def login_form() -> str:
    """
    Creates a sign-in page for users to create account/log in. If the given email is not already in the database,
    a new account is created for the user. First time users must input a username. If the email already exists,
    the login action is triggered. The sign_in_with_password function is called to verify the login and return
    username. The username and an empty set is added to the firestore db. If the user chooses a guest sign in,
    'Guest' is returned.
    """
    placeholder = st.empty()

    with placeholder.form("Credentials"):

        st.title('Nxt Movie')
        email = st.text_input("Email", key="email", help='Please enter a valid email ')
        username = st.text_input("Username", key="username", help='You must enter a username when making a new account')
        password = st.text_input("Password", type="password", key="password",
                                 help='Password must be at least 6 characters')
        signup = st.form_submit_button("Sign Up/ Login")
        guest = st.form_submit_button('Guest', help='Continue as a guest')

        st.code(
            'Instructions \n 📋 To Login, enter your email and password. \n 📋 To Sign Up, enter an email, '
            'and create a username and password. \n 📋 Passwords must be at '
            'least 6 characters long. ')

        if guest:
            placeholder.empty()
            return 'Guest'

        if signup:
            if not email:
                st.warning('Please enter a valid email')
                return ''

            elif len(password) < 6:
                st.warning('Your password must be at least 6 characters long')
                return ''

            elif not verify_email(email):

                if not username:
                    st.warning('Please enter a valid username')
                    return ''

                cursor = sql_db.connect_to_db().cursor()
                query = "INSERT INTO users(username, email, password, liked_movies) VALUES (?, ?, ?, ?)"
                cursor.execute(query, username, email, password, "")
                cursor.close()
                return username

            else:
                correct_pwd = sign_in_with_password(email, password)
                if correct_pwd:
                    placeholder.empty()
                    cursor = sql_db.connect_to_db().cursor()
                    query = "SELECT username FROM users WHERE email = ? AND password = ?"
                    cursor.execute(query, email, password)
                    display_name = cursor.fetchone()[1]
                    cursor.close()

                    return display_name

        return ''


if __name__ == "__main__":
    result = verify_email('test@gmail.com')
    print(result)
