import os
from movie_manager import Movie
from movie_manager import MovieManager
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
movie_paths = os.getenv("MOVIE_PATHS")

if movie_paths:
    movie_paths: list = movie_paths.split(',')
    print("movie_paths: ", movie_paths)


def sync():
    print("Syncing...")
    print("DB_NAME: ", db_name)
    print("DB_USER: ", db_user)
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        host=db_host,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()
    cur.execute("SELECT movie_name, release_year, resolution_width, resolution_height, external_subtitles FROM movies")
    database_records: list = cur.fetchall()
    print("records: ", database_records)
    movie_manager = MovieManager(movie_paths)
    movie_manager.process_files()
    current_movies: list = movie_manager.get_movie_list()

    for record in database_records:
        for movie in current_movies:
            movie_name = movie.get_name()
            movie_year = movie.get_year()
            if movie_name == record[0] and movie_year == str(record[1]):
                print("Match found for movie: ", movie_name)
                # Extract resolution for readability and debugging
                resolution_width, resolution_height = movie.get_resolution()
                # Check for mismatch
                if resolution_width != record[2] or resolution_height != record[3]:
                    print("Resolution mismatch")
                    cur.execute("""
                                UPDATE movies SET resolution_width = 720, resolution_height = 464 WHERE movie_name = '10 Things I Hate About You' AND release_year = 1999;
                                """)
                    # query = sql.SQL("UPDATE {field} SET resolution_width = %s, resolution_height = %s WHERE movie_name = %s AND release_year = %s").format(field = sql.Identifier(db_name))

                    # cur.execute(query, (int(movie.get_resolution()[0]), int(movie.get_resolution()[1]), movie_name, int(movie_year)))

if __name__ == "__main__":
    print("hello")
    sync()