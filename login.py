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

from typing import Any
import json
import ast
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
from dotenv import load_dotenv


def initialize_firebase() -> None:
    """
    Initialize a firebase app using credentials (contained in a .env file) from a Google firebase account
    """
    load_dotenv()
    cred = ast.literal_eval(os.getenv('CRED'))
    firebase_admin.initialize_app(credentials.Certificate(cred))


def sign_in_with_password(email: str, password: str) -> Any:
    """
    Takes in an email and password, and uses the firebase authenticator to verify the login credentials (contained in a
    .env file). Returns the json object associated with email if login is successful, otherwise displays a warning on
    the streamlit application.

    >>> verify = sign_in_with_password('test@gmail.com', 'CSC111')
    >>> not verify
    False
    """

    load_dotenv()
    api_key = os.getenv('KEY')
    rest_api_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    payload = json.dumps({
        "email": email,
        "password": password,
        "returnSecureToken": True
    })

    r = requests.post(rest_api_url, params={"key": api_key}, data=payload)

    try:
        return r.json()['email']

    except KeyError:
        st.warning('Login failed, please make sure your email and password are correct')
        return None


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

            if len(password) < 6:
                st.warning('Your password must be at least 6 characters long')
                return ''

            try:
                user = auth.get_user_by_email(email)
                correct_pwd = sign_in_with_password(email, password)

                if correct_pwd:
                    placeholder.empty()
                    return user.display_name

            except auth.UserNotFoundError:  # If the user is not found, means we create an account for them
                if not username:
                    st.warning('Please enter a valid username')
                    return ''

                try:
                    db = firestore.client()
                    doc_ref = db.collection('users').document('test')
                    doc_ref.set({"username": username, "email": email, "favourites": set()})
                    auth.create_user(display_name=username, email=email, password=password)
                    st.success('Account created successfully')
                    placeholder.empty()
                    return username

                except ValueError:
                    return ''

        return ''


# if __name__ == "__main__":
#     import python_ta
#     import doctest
#
#     doctest.testmod(verbose=True)
#
#     python_ta.check_all(config={
#         'extra-imports': ['typing', 'json', 'streamlit', 'firebase_admin', 'requests', 'dotenv', 'os', 'ast'],
#         'allowed-io': ['login_form', 'sign_in_with_password'],
#         'max-line-length': 120
#     })
