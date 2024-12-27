-- CREATE DATABASE movies;

-- \c movies

CREATE TABLE movies (
    movie_name VARCHAR(100) NOT NULL,
    release_year INT NOT NULL,
    PRIMARY KEY (movie_name, release_year),
    resolution_width INT,
    resolution_height INT,
    external_subtitles BOOLEAN DEFAULT FALSE
    file_size DOUBLE PRECISION,
);