import os
import time
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

def update_movie_params(movie: Movie, record, cur, conn):
    resolution_width, resolution_height = movie.get_resolution()
    if resolution_width != record[2] or resolution_height != record[3]:
        print("Resolution mismatch")
        try:
            query = sql.SQL("UPDATE {field} SET resolution_width = %s, resolution_height = %s WHERE movie_name = %s AND release_year = %s").format(field = sql.Identifier(db_name))
            cur.execute(query, (int(movie.get_resolution()[0]), int(movie.get_resolution()[1]), movie.get_name(), int(movie.get_year())))
            conn.commit()
        except psycopg2.Error as e:
            raise(e)
    elif movie.external_subtitles != record[4]:
        print("External subtitles mismatch")
        try:
            query = sql.SQL("UPDATE {field} SET external_subtitles = %s WHERE movie_name = %s AND release_year = %s").format(field = sql.Identifier(db_name))
            cur.execute(query, (movie.external_subtitles, movie.get_name(), int(movie.get_year())))
            conn.commit()
        except psycopg2.Error as e:
            raise(e)
    elif movie.get_file_size() != record[5]:
        print("File size mismatch")
        try:
            query = sql.SQL("UPDATE {field} SET file_size = %s WHERE movie_name = %s AND release_year = %s").format(field = sql.Identifier(db_name))
            cur.execute(query, (movie.get_file_size(), movie.get_name(), int(movie.get_year())))
            conn.commit()
        except psycopg2.Error as e:
            raise(e)

def add_movie(movie: Movie, cur, conn):
    print(f"Movie {movie.get_name()} not found in the database")
    try:
        query = sql.SQL("INSERT INTO {field} (movie_name, release_year, resolution_width, resolution_height, external_subtitles, file_size) VALUES (%s, %s, %s, %s, %s, %s)").format(field = sql.Identifier(db_name))
        cur.execute(query, (movie.get_name(), movie.get_year(), int(movie.get_resolution()[0]), int(movie.get_resolution()[1]), movie.external_subtitles, movie.get_file_size()))
        conn.commit()
    except psycopg2.Error as e:
        raise(e)

def sync():
    print("Syncing...")
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        host=db_host,
        password=db_password,
        port=db_port
    )
    cur = conn.cursor()
    cur.execute("SELECT movie_name, release_year, resolution_width, resolution_height, external_subtitles, file_size FROM movies;")
    database_records: list = cur.fetchall()
    print(database_records)
    movie_manager = MovieManager(movie_paths)
    movie_manager.process_files()
    current_movies: list = movie_manager.get_movie_list()
    print(database_records.__len__())
    print(current_movies.__len__())

    if database_records.__len__() == 0:
        print("No records found in the database")
        for movie in current_movies:
            add_movie(movie, cur, conn)
        return

    # assumes that current_movies list has more movies than database_records
    for movie in current_movies:
        movie_exists = False
        for record in database_records:
            if movie.get_name() == record[0] and str(movie.get_year()) == str(record[1]):
                movie_exists = True
                print("Match found " + movie.get_name() + str(record))
                # check for any changes in resolution or external subtitles for movie
                update_movie_params(movie, record, cur, conn)
        if not movie_exists:
            print("adding: " + movie.get_name())
            add_movie(movie, cur, conn)

    cur.close()
    conn.close()

if __name__ == "__main__":
    sync()