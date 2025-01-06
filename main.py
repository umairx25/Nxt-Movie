"""
CSC111 Project 2: Nxt Movie

Module Description
==================
The file contains the functions generating the main user interface.

Copyright and Usage Information
===============================

The file is expressly provided for the purposes of course assessments for CSC111 at the University of Toronto.
All forms of distribution of this code, whether as given or with any changes, are expressly prohibited.

© 2024 Umair Arham, Abdallah Arham Wajid Mohammed, Sameer Shahed, All Rights Reserved
"""
import ast

import streamlit as st
# from firebase_admin import firestore
import pandas as pd

import sql_db
import trees
import login
import scraper
import recommender


def update_session_state() -> None:
    """
    Updates streamlit's session state on every rerun of the script. Everytime the user interacts with
    the GUI, streamlit reruns the app, thus it is crucial to use session_state functionality to ensure
    the data is not lost.

    Session State Variables:
        - st.session_state['key']: stores the movies that need to be displayed, ensures the displayed movies
        are not lost when refreshed
        - st.session_state['favs']: Stores the movies the user has liked. If the user signed in via firebase, it loads
        in the movies the user already liked that were stored in the database.
        - st.session_state['user']: The username of the user. If the user is a guest, firebase is not involved.
        Otherwise, data is extracted/altered from their profile as needed.
        - st.session_state['data']: Contains a pandas dataframe which includes all the cosine similarities data of all
        the movies.
        - st.session_state['movies']: A list of all the movie objects in the dataset.
    """
    if 'key' not in st.session_state:
        st.session_state['key'] = set()

    if 'favs' not in st.session_state:
        st.session_state['favs'] = set()

    if 'toggle_status' not in st.session_state:
        st.session_state['toggle_status'] = {}

    if 'user' not in st.session_state:
        st.session_state['user'] = ''  # Initialize user to None
        # try:
        #     login.initialize_firebase()
        #
        # except ValueError:  # Only initialize firebase once to avoid ValueError
        #     pass

    if 'data' not in st.session_state and 'movies' not in st.session_state:
        conn = sql_db.connect_to_db()
        df = pd.read_sql('SELECT * FROM movies', conn)
        df.drop(columns='id', axis=1, inplace=True)
        st.session_state['data'] = recommender.create_data_frame(df)
        st.session_state['movies'] = trees.read_in_movies(df)

    # Check if the user is not signed in yet
    if not st.session_state['user']:
        username = login.login_form()
        st.session_state['user'] = username

        if username and username != 'Guest':
            conn = sql_db.connect_to_db()
            cursor = conn.cursor()
            query = 'SELECT liked_movies FROM users WHERE username = ?;'
            cursor.execute(query, username)

            try:
                favourites = ast.literal_eval(cursor.fetchone()[0])
                print('Favourites: ', favourites)
                for movie in set(trees.convert_to_movie_obj(favourites, st.session_state['movies'])):
                    st.session_state['favs'].add(movie)
                    st.session_state['toggle_status'][movie.name] = True

            except Exception as e:
                st.session_state['favs'] = set()

    if st.session_state['key'] == set() and st.session_state['user']:
        st.session_state['key'] = trees.convert_to_movie_obj(trees.get_random_movies(st.session_state['data']),
                                                             st.session_state['movies'])


def run_gui() -> None:
    """
    The main user interface framework. Constructs a search bar which uses fuzzy search to find matching movies,
    and various elements to allow the user to filter for their desired movies. When filtering, at least one genre and
    one rating must be inputted. Clicking the Submit Filters button initiates the recommendation_engine_filters function
    and returns the recommended movies. The My Favourites button simply displays all the movies the user has liked. The
    Filter by Favourites button initiates the recommendation_engine function to display recommendations based on the
    movies the user liked.
    """

    if st.session_state['user']:
        # Set page title and search bar
        st.title('NxtMovie')

        col1, col2 = st.columns([7, 1])
        search_input = col1.text_input('Enter a movie to search')
        col2.write('')
        col2.write('')

        if col2.button('Search'):
            matched_movies = trees.search(search_input, st.session_state['movies'], exact=False)
            st.session_state['key'] = trees.convert_to_movie_obj(matched_movies, st.session_state['movies'])

        st.divider()

        # Set the filters
        all_filters = trees.get_all_filters(st.session_state['movies'])
        date_range = (all_filters['rel'][0], all_filters['rel'][1])

        genre = st.multiselect('Genres', sorted(all_filters['genre']))
        release_date = st.slider('Release Dates', date_range[0], date_range[1], (date_range[0], date_range[1]), step=1)
        rating = st.multiselect('Pg_Rating', sorted(all_filters['rating']))
        score = st.selectbox('Score', ['High', 'Low', 'Both'])

        col1, col2, col3 = st.columns(3)

        if col1.button('Submit Filters', help='Click to get recommendations based on your filters'):
            if not genre or not rating:
                st.warning('Please input genre and pg-ratings')

            user_filters = {'genre': genre, 'rating': rating, 'score': score.upper(), 'rel': release_date}
            tree = trees.build_tree(st.session_state['movies'])
            filtered_movies = trees.convert_to_movie_obj(tree.matching(user_filters), st.session_state['movies'])

            filtered_movies = recommender.recommendation_engine_filters(filtered_movies)
            # top_movies = recommender.recommendation_engine(filtered_movies, True)
            st.session_state['key'] = trees.convert_to_movie_obj(filtered_movies, st.session_state['movies'])

        if col2.button('My Favourites', help='Click to see all movies you favorited'):
            st.session_state['key'] = st.session_state['favs']

        if col3.button('Filter by My Favourites', help='Click to see recommendations based on your liked movies'):
            recs = recommender.recommendation_engine(st.session_state['favs'], st.session_state['data'],
                                                     st.session_state['movies'])
            recs = trees.convert_to_movie_obj(recs, st.session_state['movies'])
            st.session_state['key'] = recs

        st.divider()
        st.header('Top Picks For You:')
        st.write("")
        st.write("")


def display_movies(top_movies: list[trees.Movie]) -> None:
    """
    Given a list of movies, displays the name, images, genre, directors, release date,
    description of all the movies. Each movie has a toggle button associated with it,
    and if turned on, adds the movie to the user's favourites. If toggle is turned off from
    an on-state, it is removed from user's favourites. If the user is registered via email,
    the information is updated on the firebase database.
    """

    top = top_movies.copy()

    for movie in top:
        full_link = scraper.format_movie(movie.name, 'https://www.metacritic.com/movie/')
        col1, col2 = st.columns([3, 4])
        col1.subheader(f"[{movie.name}](%s)" % full_link + f" ({movie.rel})")
        col1.image(movie.image, width=None)

        col2.write(movie.desc)
        col1.write(f':gray[Runtime: {movie.run}]')
        col1.write(f':gray[Rating: {movie.rating}]')
        col1.write(f':gray[Score: {movie.score}]')
        gen, dirc = ', '.join(movie.genre), ', '.join(movie.dirc)
        col2.write(f':gray[Genres: {gen}]')
        col2.write(f':gray[Directed by: {dirc}]')

        # Retrieve the toggle status from the toggle_status dictionary or default to False
        toggle_status = st.session_state['toggle_status'].get(movie.name, False)

        # Render the toggle widget with the retrieved status
        toggle_status = col2.toggle('Favorite', toggle_status, key=movie)

        # Update the toggle status in the toggle_status dictionary
        st.session_state['toggle_status'][movie.name] = toggle_status

        if toggle_status:
            st.session_state['favs'].add(movie)

            if st.session_state['user'] != 'Guest':
                username = st.session_state['user']
                favourites = list({f.name for f in st.session_state['favs']})
                conn= sql_db.connect_to_db()
                cursor = conn.cursor()
                query = "UPDATE users SET liked_movies = ? WHERE username = ?"
                cursor.execute(query, (str(favourites), username))
                cursor.commit()
                cursor.close()

                # db = firestore.client()
                # doc_ref = db.collection("users").document(st.session_state['user'])
                # doc_ref.set(
                #     {"username": st.session_state['user'], "favourites": {f.name for f in st.session_state['favs']}})

        elif movie in st.session_state['favs']:
            st.session_state['favs'].discard(movie)

            if st.session_state['user'] != 'Guest':
                username = st.session_state['user']
                favourites = list({f.name for f in st.session_state['favs']})
                conn = sql_db.connect_to_db()
                cursor = conn.cursor()
                query = "UPDATE users SET liked_movies = ? WHERE username = ?"
                cursor.execute(query, (str(favourites), username))
                cursor.commit()
                cursor.close()


                # db = firestore.client()
                # doc_ref = db.collection("users").document(st.session_state['user'])
                # doc_ref.set(
                #     {"username": st.session_state['user'], "favourites": {f.name for f in st.session_state['favs']}})

        st.divider()


if __name__ == "__main__":
    update_session_state()
    run_gui()
    display_movies(st.session_state['key'])

    # To run the program, open your terminal and enter: streamlit run 'main.py'
    # To test python TA, please comment out the code above and uncomment the python TA code below

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': ['firebase_admin', 'trees', 'login', 'scraper', 'recommender', 'streamlit', 'pandas'],
    #     'allowed-io': ['run_gui', 'display_movies', 'update_session_state'],
    #     'max-line-length': 120
    # })
