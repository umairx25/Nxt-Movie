"""
CSC111 Project 2: Nxt Movie

Module Description
==================
The main file containing the major data structures and functions.

Copyright and Usage Information
===============================

The file is expressly provided for the purposes of course assessments for CSC111 at the University of Toronto.
All forms of distribution of this code, whether as given or with any changes, are expressly prohibited.

© 2024 Umair Arham, Abdallah Arham Wajid Mohammed, Sameer Shahed, All Rights Reserved
"""

from __future__ import annotations
import ast
from typing import Optional, Any
import pandas as pd
from fuzzywuzzy import fuzz, process


class Movie:
    """
    A Movie object representing a movie and its attributes, including its name, image (url), release
    date, pg-rating, metacritic score, description, audience score, director name(s), runtime and genre(s). We
    take the average of the meta score and audience score to get the score attribute.

    Instance Attributes:
        name:
            The name of the movie.
        image:
            The url of the movie's poster/image.
        rel:
            The year the movie was released.
        rating:
            The pg-rating of the movie.
        meta:
            The critic score of the movie (out of 100)
        desc:
            The description of the movie's plot.
        aud:
            The audience score of the movie (out of 100)
        dirc:
            The people who directed the movie.
        run:
            The total play time of the movie.
        genre:
            The genre categories the movie falls into
        score:
            The average score of the movie (averaged between metacritic and audience scores)

    Preconditions:
        - all(0 <= a <= 100 for a in [self.score, self.meta, self.aud])
        - all(a is not None for a in [self.rating, self.image, self.genre, self.run, self.desc, self.dirc])
        - self.rel > 0
    """

    name: str
    image: str
    rel: int
    rating: str
    score: int | float
    desc: str
    dirc: list[str]
    run: str
    genre: list[str]

    def __init__(self, name: str, image: str, rel: int, rating: str, meta: float | int, desc: str, aud: float | int,
                 dirc: str,
                 run: str, genre: str) -> None:
        self.name = name
        self.image = image
        self.rel = rel
        self.rating = rating
        self.score = (meta + (aud * 10)) / 2
        self.desc = desc
        self.dirc = self.format_director(dirc)
        self.run = run
        self.genre = self.format_genre(genre)

    def format_genre(self, gen: str) -> list[str]:
        """
        Format the genres from the dataset into a list of genres
        """
        return ast.literal_eval(gen)

    def format_director(self, dirc: str) -> list[str]:
        """
        Format the directors in the dataset from one long string into a list of multiple strings.
        """
        return [d.strip() for d in dirc.replace('\n', '').split(',')]


class Tree:
    """
    A recursive tree data structure.
    Representation Invariants:
        -self._subtrees != [] # change if needed
        - all(not subtree.is_empty() for subtree in self._subtrees)
    """
    # Private Instance Attributes:
    #   - _root:
    #       The item stored at this tree's root, or None if the tree is empty.
    #   - _subtrees:
    #       The list of subtrees of this tree. This attribute is empty when
    #       self._root is None (representing an empty tree). However, this attribute
    #       may be empty when self._root is not None, which represents a tree consisting
    #       of just one item.

    _root: Optional[Any]
    _subtrees: list[Tree]

    def __init__(self, root: Optional[Any], subtrees: list[Tree]) -> None:
        """Initialize a new Tree with the given root value and subtrees.

        Preconditions:
            -subtrees != [] #change if needed
        """
        self._root = root
        self._subtrees = subtrees

    def is_empty(self) -> bool:
        """Return whether this tree is empty.
        """
        return self._root is None

    def insert_sequence(self, items: list) -> None:
        """Insert the given items into this tree.

        The inserted items form a chain of descendants, where:
            - items[0] is a child of this tree's root
            - items[1] is a child of items[0]
            - items[2] is a child of items[1]
            - etc.

        Do nothing if items is empty.
        """

        if not items:
            return

        first = items[0]
        rest = items[1:]

        for subtree in self._subtrees:
            if subtree._root == first:
                subtree.insert_sequence(rest)
                return

        new_tree = Tree(first, [])
        new_tree.insert_sequence(rest)
        self._subtrees.append(new_tree)

    def matching(self, user_input: dict, level: int = 0) -> list[str]:
        """
        Traverse the tree and returns a list of movie names that match the user's desired filters.

        Preconditions:
            - user_input is not None
        """
        matching = []
        user = user_input.copy()

        if level > 3:
            return [s._root for s in self._subtrees if s._root not in matching]

        for subtree in self._subtrees:

            if level == 0:
                if user_input['score'] == 'BOTH':
                    matching.extend(subtree.matching(user, level + 1))

                elif subtree._root == user_input['score']:
                    matching.extend(subtree.matching(user, level + 1))

            if level == 1 and subtree._root in user['rating']:
                matching.extend(subtree.matching(user, level + 1))

            if level == 2 and subtree._root in range(user['rel'][0], user['rel'][1]):
                matching.extend(subtree.matching(user, level + 1))

            if level == 3 and subtree._root in user['genre']:
                matching.extend(subtree.matching(user, level + 1))

        return matching


def read_in_movies(df: pd.DataFrame) -> list[Movie]:
    """
    Read in movie data from the given pandas dataframe and store each row as a Movie object in a list.
    Preconditions:
        - df is not None
    """
    movies = []

    for _, row in df.iterrows():
        mov = Movie(name=row['Title'], image=row['Image Link'], rel=row['Release'], rating=row['Rating'],
                    meta=row['Metacritic'],
                    desc=row['Description'], aud=row['Audience'], dirc=str(row['Directors']), run=row['Runtime'],
                    genre=row['Genres'])
        movies.append(mov)

    return movies


def build_tree(all_movies: list[Movie]) -> Tree:
    """
    Build a tree by categorizing data from a list of movie objects in a hierarchial tree format
    """
    tree = Tree('', [])

    for movie in all_movies:
        for gen in movie.genre:
            date = movie.rel

            if movie.score < 70:  # Following metacritic's convention, scores >= 70 are considered 'good'
                score = 'LOW'
            else:
                score = 'HIGH'

            lst = [score, movie.rating, date, gen, movie.name]
            tree.insert_sequence(lst)

    return tree


def get_all_filters(all_movies: list[Movie]) -> dict[str, Any]:
    """
    Return a dictionary containing all available filters for movies in a list of movie objects.

    This function retrieves all possible values for the attributes of the movies and creates a dictionary mapping
    each attribute of the movies in the movie list to its corresponding list or range of unique values.
    """
    all_movies = sorted(all_movies, key=lambda x: x.rel)
    date = (all_movies[0].rel, all_movies[-1].rel)
    genres, ratings = set(), set()

    for m in all_movies:
        for genre in m.genre:
            genres.add(genre)
        ratings.add(m.rating)

    return {'genre': list(genres), 'rating': list(ratings),
            'score': 'HIGH', 'rel': date}


def search(movie_name: str, movies: list[Movie], exact: bool = True) -> list[str] | Movie | None:
    """
    Search for a list of movie that are similar to the input movie from a list of movie objects. There are 2
    algorithms to choose from, and both algorithms output similar movies based on their titles only.

    If exact is True, then the function will use the fuzzy module's partial ratio algorithm. Returns a list of matching
    movie names.
    If exact is False, then the function will perform a binary search and look for the exact movie. Returns a movie
    object. If it cannot find an exact movie, it returns None.
    """

    movies = sorted(list(movies), key=lambda x: x.name)
    b, e = 0, len(movies)

    if not exact:
        matches = process.extract(movie_name, [mv.name for mv in movies], scorer=fuzz.partial_ratio, limit=25)
        return [t[0] for t in matches]

    while b < e:
        m = (b + e) // 2

        if movies[m].name == movie_name:
            return movies[m]

        elif movies[m].name > movie_name:
            e = m

        else:
            b = m + 1

    return None


def convert_to_movie_obj(movie_names: list[str], all_movies: list[Movie]) -> list[Movie]:
    """
    Given a list of strings, convert them to movie objects by finding them in the given list of all possible movie
    objects using binary search.
    """
    found_names = set()
    lst = []

    for movie in movie_names:
        movie_obj = search(movie, all_movies)
        if movie_obj and (movie_obj.name not in found_names):
            lst.append(movie_obj)
            found_names.add(movie_obj.name)

    return lst


def get_random_movies(df: pd.DataFrame) -> list[str]:
    """
    Extract random movies from the given pandas dataframe containing columns of movies and their attributes. Returns a
    list of movie names.
    """
    random_row = df.sample(n=20)['Title']
    random_lst = list(random_row)

    return random_lst


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['__future__', 'ast', 'typing', 'pandas', 'fuzzywuzzy'],
        'max-line-length': 120
    })
