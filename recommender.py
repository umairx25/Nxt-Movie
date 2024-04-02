"""
CSC111 Project 2: Nxt Movie

Module Description
==================
The main recommendation algorithms and calculations using a Graph data structure

Copyright and Usage Information
===============================

The file is expressly provided for the purposes of course assessments for CSC111 at the University of Toronto.
All forms of distribution of this code, whether as given or with any changes, are expressly prohibited.

© 2024 Umair Arham, Abdallah Arham Wajid Mohammed, Sameer Shahed, All Rights Reserved
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import trees
from trees import Movie


def create_data_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in a pandas data dataframe containing columns of movies and their attributes. In the output dataframe, the
    left most column will contain all the movie names. For each movie in the input dataframe, it calculates the cosine
    similarity with every other movie based on genres, rating, and description, and stores the corresponding values
    under a new column titled by the movie name.
    """

    df['Combined_Text'] = df['Genres'] + ' ' + df['Rating'] + ' ' + df['Description']
    vectorizer = TfidfVectorizer()
    vectorized = vectorizer.fit_transform(df['Combined_Text'])
    similarities = cosine_similarity(vectorized)
    df2 = pd.DataFrame(similarities, columns=df['Title'], index=df['Title']).reset_index()

    return df2


def get_similar_movies(movie_name: str, dataframe: pd.DataFrame) -> list[str]:
    """
    Given a movie name and a pandas dataframe with the layout described for the return value of create_data_frame,
    return a list of recommended movie names based on the highest cosine similarity with the given movie.
    """

    # Get all the similarity scores corresponding to our target movie (movie_name)
    sim_scores_list = dataframe[movie_name].values.tolist()

    # Extract the names of all the titles the movie is being compared against, and remove the movie itself
    titles_list = dataframe['Title'].tolist()

    # Create a dictionary mapping titles to similarity scores
    mapping = dict(zip(titles_list, sim_scores_list))

    # Sort by highest cosine similarity scores
    sorted_mapping = sorted(mapping.items(), key=lambda x: x[1], reverse=True)

    return [s[0] for s in sorted_mapping if s != movie_name][:7]


def recommendation_engine(favs: list[Movie], dataframe: pd.DataFrame, all_movies: list[Movie]) -> list[str]:
    """
    Takes in a list of movie objects that the user has favourited, the list of all possible movie objects from the
    given dataset, and a pandas dataframe with the layout described for the return value of create_data_frame.

    For each movie in favs, it creates a list of similar movies from given dataframe whose Movie objects are
    then added to a weighted graph as nodes.

    The weights between every pair of movies are calculated using the algorithm implmented in
    calculate_similarity. The Pagerank algorithm is then used to calculate the importance of each movie based on the
    weights of all its edges. A list of names of movies with the highest importance are returned.
    """

    graph = nx.Graph()
    movie_obj = []

    for movie in favs:
        curr = get_similar_movies(movie.name, dataframe)
        curr = trees.convert_to_movie_obj(curr, all_movies)
        movie_obj.extend(curr)

    for movie1 in movie_obj:
        for movie2 in movie_obj:
            if movie1 != movie2:
                similarity = calculate_similarity(movie1, movie2)
                graph.add_edge(movie1.name, movie2.name, weight=similarity)

    pagerank_scores = nx.pagerank(graph)
    ranked_movies = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
    top_matches = [mov[0] for mov in ranked_movies[:20]]  # Select top matches

    return top_matches


def recommendation_engine_filters(filtered_movies: list[trees.Movie]) -> list[str]:
    """
    Find the top matching movies based on the user's filters. An edge is created
    between every filtered movie, and the calculate similarity function is used to compute
    their edge weights. The Pagerank algorithm is then used to identify the most centralized vertices,
    and the list of top movies according to Pagerank are then returned.
    """

    graph = nx.Graph()

    for m1 in filtered_movies:
        for m2 in filtered_movies:
            if m1 != m2:
                similarity = calculate_similarity(m1, m2)
                graph.add_edge(m1.name, m2.name, weight=similarity)

    # Run PageRank algorithm
    pagerank_scores = nx.pagerank(graph)
    ranked_movies = sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)
    top_matches = [movie[0] for movie in ranked_movies[:20]]

    return top_matches


def calculate_similarity(movie1: Movie, movie2: Movie) -> int | float:
    """
    Calculate similarity between two movies objects based on their attributes. The similarity between the genres is
    calculated using the Jaccard similarity coefficient. Closer release dates, higher score average between the movies,
    and same ratings result in higher edge weights.
    """
    genre1 = set(movie1.genre)
    genre2 = set(movie2.genre)

    # Calculate Jaccard similarity coefficient based on common genres
    intersection = len(genre1.intersection(genre2))
    union = len(genre1.union(genre2))
    similarity = intersection / union if union != 0 else 0

    # Weight is increased if they have better average score or common ratings
    average_score = (movie1.score + movie2.score) / 2
    rating = 1 if movie1.rating == movie2.rating else 0
    date_similairty = (abs(movie1.rel - movie2.rel)) / 100

    return abs((similarity * average_score) + rating - date_similairty)


# if __name__ == '__main__':
#     import python_ta
#
#     python_ta.check_all(config={
#         'extra-imports': ['pandas',
#                           'sklearn.metrics.pairwise', 'sklearn.feature_extraction.text', 'trees', 'networkx'],
#         'max-line-length': 120
#     })
