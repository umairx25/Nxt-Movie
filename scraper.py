"""
CSC111 Project 2: Nxt Movie

Module Description
==================
The file extracts movie data from metacritic.com to populate the database.

Copyright and Usage Information
===============================

The file is expressly provided for the purposes of course assessments for CSC111 at the University of Toronto.
All forms of distribution of this code, whether as given or with any changes, are expressly prohibited.

© 2024 Umair Arham, Abdallah Arham Wajid Mohammed, Sameer Shahed, All Rights Reserved
"""

import re
from typing import Optional, Any
import pandas as pd
import bs4
from bs4 import BeautifulSoup as bs
import requests


def format_movie(movie: str, movie_link: str) -> str:
    """
    Formats the given movie name to match the format of the given webpage.
    """
    formatted_name = movie.lower()
    formatted_name = formatted_name.replace(" ", "-")
    formatted_name = formatted_name.replace("(", "")
    formatted_name = formatted_name.replace(")", "")
    formatted_name = formatted_name.replace("/", "")
    formatted_name = formatted_name.replace(",", "")
    formatted_name = formatted_name.replace("'", "")
    formatted_name = formatted_name.replace(":", "")

    full_link = movie_link + formatted_name + "/"

    return full_link


def get_soup_item(link: str) -> requests.Response:
    """
    Creates a request to load to the given link into a beautiful soup object.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
                      'Mobile/15E148'
    }
    return requests.get(link, headers=headers)


def rel_date(soup: bs4.BeautifulSoup) -> list[int]:
    """
    Returns a list of all the movie release dates from the given webpage.
    """

    date_list = []
    date_elements = soup.find_all(class_="c-finderProductCard")

    for d in date_elements:
        new_date_element = d.find('div', class_="c-finderProductCard_meta")
        title = new_date_element.text.strip() if new_date_element else None

        if title:
            date_match = re.search(r'\w+\s\d{1,2},\s\d{4}', title)
            if date_match:
                release_date = date_match.group(0)
                year = release_date.split(',')[1].lstrip()
                date_list.append(int(year))

    return date_list


def get_title(soup: bs4.BeautifulSoup) -> list[str]:
    """
    Returns a list of all the movie titles from the given webpage.
    """
    titles = []
    _titles = soup.find_all(class_='c-finderProductCard')

    for card in _titles:
        title_element = card.find('div', class_='c-finderProductCard_title')
        title = title_element.text.strip() if title_element else None

        if title:
            title = title.split('. ')[1] if '. ' in title else title
            titles.append(title)
        else:
            titles.append('Problem')

    return titles


def get_image(soup: bs4.BeautifulSoup, default_image: str) -> list[str]:
    """
    Returns a list of URLs corresponding to all the movie images/posters from the given webpage. If no image is found
    the default image is appended to the return list.
    """
    lst_images = []

    image_elements = soup.find_all(class_='c-finderProductCard_img')

    for img_element in image_elements:
        img_tag = img_element.find('img')

        if img_tag and 'src' in img_tag.attrs:
            image_url = img_tag['src']
            lst_images.append(image_url)
        else:
            lst_images.append(default_image)

    return lst_images


def get_rating(soup: bs4.BeautifulSoup) -> list[str]:
    """
    Returns a list of all the PG ratings of movies from the given webpage. If an invalid rating is encountered,
    the movie is deemed unrated.
    """

    rating_elements = soup.find_all(class_='c-finderProductCard_meta')
    ratings = []

    for rating_element in rating_elements:
        try:
            rating_text = rating_element.text.strip().split()[-1] if rating_element else None
            if rating_text and rating_text != 'Metascore' and all(
                    s in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'] for s in rating_text):
                ratings.append('Unrated')
            else:
                ratings.append(rating_text)
        except IndexError:
            ratings = []

    return ratings


def get_score(soup: bs4.BeautifulSoup) -> list[float]:
    """
    Returns a list of all the metascores of movies from the given webpage.
    """

    score_elements = soup.find_all(class_='c-finderProductCard_meta g-outer-spacing-top-auto')
    scores = []

    for score_element in score_elements:
        score_text = score_element.text.strip().split('Metascore')[0] if score_element else None
        if score_text:
            scores.append(float(score_text.lstrip()))

    return scores


def get_desc(soup: bs4.BeautifulSoup) -> list[str]:
    """
    Returns a list of all the movie descriptions from the given webpage.
    """

    desc_elements = soup.find_all(class_='c-finderProductCard_description')
    descriptions = []

    for desc_element in desc_elements:
        description = desc_element.text.strip() if desc_element else None
        if description:
            descriptions.append(description)

    return descriptions


def user_score(soup: bs4.BeautifulSoup) -> float:
    """
    Returns the audience score corresponding to the movie from the given webpage.
    """
    user_score_div = soup.find('div', class_='c-siteReviewScore_user')

    if user_score_div:
        user_score_span = user_score_div.find('span')
        user_sc = user_score_span.text.strip() if user_score_span else 0

    else:
        user_sc = 0

    return float(user_sc) if user_sc != 'tbd' else 0


def director_name(soup: bs4.BeautifulSoup) -> str:
    """
     Returns all the director names corresponding to the movie from the given webpage.
    """
    director_div = soup.find('div', class_="c-productDetails_staff")

    try:
        dir_name = director_div.find('div',
                                     class_='c-crewList g-inner-spacing-bottom-small c-productDetails_staff_directors')
        name = dir_name.text.split('Directed By:')[1].strip()

    except AttributeError:
        name = ''

    return name


def get_runtime(soup: bs4.BeautifulSoup) -> str:
    """
     Returns the run time corresponding to the movie from the given webpage.
    """

    time_div = soup.find('div', class_="c-heroMetadata")
    try:
        metadata_items = time_div.find_all('li', class_='c-heroMetadata_item')
        runtime = None

        for item in metadata_items:
            span = item.find('span')
            if span and 'h' in span.text:
                runtime = span.text.strip()

    except AttributeError:
        runtime = ''

    return runtime


def get_genre(soup: bs4.BeautifulSoup) -> list[str]:
    """
    Returns a list of genres corresponding to the movie from the given webpage. Returns an empty list if no genres are
    found.
    """

    genre_ul = soup.find('ul', class_='c-genreList')
    genres = []

    try:
        for li in genre_ul.find_all('li', class_='c-genreList_item'):
            span = li.find('span', class_='c-globalButton_label')
            if span:
                genres.append(span.text.strip())

    except AttributeError:
        genres = []

    return genres


def get_links(titles: list[str]) -> dict[str, Any]:
    """
    Stores specific information for each individual movie page in a dictionary with different attributes
    separated into key-value pairs, given a list of movie titles.
    """
    aud_score = []
    director = []
    time = []
    genre_ = []

    for tl in titles:
        movie = format_movie(tl, 'https://www.metacritic.com/movie/')
        new_soup = bs(get_soup_item(movie).content, 'html.parser')
        aud_score.append(user_score(new_soup))
        director.append(director_name(new_soup))
        time.append(get_runtime(new_soup))
        genre_.append(get_genre(new_soup))

    return {'aud_score': aud_score, 'director': director, 'time': time, 'genre_': genre_}


def scrape_data(dest_file: str, base_link: str, start: Optional[int] = 1, end: Optional[int] = 669) -> None:
    """
    Scrapes data from the given website. Starts from the given start page, ending at the end page, extracting
    data from each page. Utilizes get_links to extract detailed info for every specific movie. Stores the
    extracted data in a dictionary, and uses pandas to store the data in a csv file.
    """

    page_number = start
    max_pages = end

    name_dict = {'Title': [], 'Image Link': [], 'Release': [], 'Rating': [],
                 'Metacritic': [], 'Description': [], 'Audience': [],
                 'Directors': [], 'Runtime': [],
                 'Genres': []}

    while page_number <= max_pages:
        soup = bs(get_soup_item(base_link + str(page_number)).content, 'html.parser')

        titles = get_title(soup)
        movie_info = get_links(titles)

        name_dict['Title'].extend(titles)
        name_dict['Image Link'].extend(get_image(soup, 'https://i.ytimg.com/vi/g13gs5a8HZ4/hqdefault.jpg'))
        name_dict['Release'].extend(rel_date(soup))
        name_dict['Rating'].extend([r for r in get_rating(soup) if r != 'Metascore'])
        name_dict['Metacritic'].extend(get_score(soup))
        name_dict['Description'].extend(get_desc(soup))
        name_dict['Audience'].extend(movie_info['aud_score'])
        name_dict['Directors'].extend(movie_info['director'])
        name_dict['Runtime'].extend(movie_info['time'])
        name_dict['Genres'].extend(movie_info['genre_'])

        page_number += 1

    df = pd.DataFrame(name_dict)

    # Further data cleaning
    df = df[(df['Audience'] != '0.0') & (df['Genres'] != '[]') & (df['Release'] != '')]

    df.to_csv(dest_file, mode='a', index=False)


if __name__ == "__main__":
    # These are the base urls used for scraping
    BASE_LINK = 'https://www.metacritic.com/browse/movie/?releaseYearMin=1910&releaseYearMax=2024&page='
    MOVIE_LINK = 'https://www.metacritic.com/movie/'
    DEFAULT_IMG = 'https://i.ytimg.com/vi/g13gs5a8HZ4/hqdefault.jpg'

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ['re', 'typing', 'pandas', 'bs4', 'requests'],
        'allowed-io': ['login_form', 'sign_in_with_password'],
        'max-line-length': 120
    })
