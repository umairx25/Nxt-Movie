import os

import pyodbc
from dotenv import load_dotenv


def connect_to_db():
    """
    Connects to the Azure SQL Database using SQL Authentication.
    Returns the connection object if successful.
    """
    load_dotenv()
    server = os.getenv('server')
    database = os.getenv('database')
    username = os.getenv('user')
    password = os.getenv('password')

    # Build the connection string
    connection_string = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'Authentication=SQLPassword;'
    )

    try:
        cnxn = pyodbc.connect(connection_string)
        print("Connection successful!")
        return cnxn
    except pyodbc.Error as e:
        print(f"Failed to connect to the database. Error: {e}")
        raise

def insert_data_into_table(data):
    cursor = connect_to_db().cursor()

    for d in data:
        try:
            query = (f"INSERT INTO movies (title, image, release, rating, metacritic, description, "
                     f"audience, directors, runtime, genres) VALUES (?, ?, ?, ?,?,?,?,?,?,?)")
            cursor.execute(query, (d['title'],
                                   d['image'],
                                   d['release'],
                                   d['rating'],
                                   d['metacritic'],
                                   d['description'],
                                   d['audience'],
                                   d['directors'].replace("\n", "").replace("\t", "").replace("\b", "").replace("  ",
                                                                                                                "").strip(),
                                   d['runtime'],
                                   d['genres']))

        except Exception as e:
            print("Insert data into table: " + e)
            print(d['title'])

    cursor.commit()


# Test the connection
if __name__ == "__main__":
    conn = connect_to_db()
