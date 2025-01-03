import os

import pyodbc
from dotenv import load_dotenv

def connect_to_db():
    load_dotenv()
    server = os.getenv('server')
    database = os.getenv('database')
    username = os.getenv('username')
    password = os.getenv('password')
    link = ('DRIVER={ODBC Driver 18 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)

    # Specifying the ODBC driver, server name, database, etc. directly
    cnxn = pyodbc.connect(link)
    return cnxn

def insert_data_into_table(data):
    cursor = connect_to_db().cursor()

    for d in data:
        try:
            query = (f"INSERT INTO movies (title, image, release, rating, metacritic, description, "
                     f"audience, directors, runtime, genres) VALUES (?, ?, ?, ?,?,?,?,?,?,?)")
            cursor.execute(query, ( d['title'],
                                            d['image'],
                                            d['release'],
                                            d['rating'],
                                            d['metacritic'],
                                            d['description'],
                                            d['audience'],
                                            d['directors'].replace("\n", "").replace("\t", "").replace("\b", "").replace("  ", "").strip(),
                                            d['runtime'],
                                            d['genres'] ) )

        except Exception as e:
            print(e)
            print(d['title'])

    cursor.commit()
