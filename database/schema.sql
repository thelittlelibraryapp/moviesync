-- MovieSync Database Schema
-- Run this in Supabase SQL Editor to set up the database

-- Movies table
CREATE TABLE movies (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  year INTEGER NOT NULL,
  runtime_seconds INTEGER NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Fingerprints table (stores Chromaprint audio fingerprints)
CREATE TABLE fingerprints (
  id SERIAL PRIMARY KEY,
  movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
  timestamp_seconds INTEGER NOT NULL,
  fingerprint_data TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fingerprints_movie_timestamp
  ON fingerprints(movie_id, timestamp_seconds);

-- Comments table
CREATE TABLE comments (
  id SERIAL PRIMARY KEY,
  movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
  timestamp_seconds INTEGER NOT NULL,
  username TEXT NOT NULL CHECK (char_length(username) BETWEEN 1 AND 50),
  text TEXT NOT NULL CHECK (char_length(text) BETWEEN 1 AND 280),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_comments_movie_timestamp
  ON comments(movie_id, timestamp_seconds);

-- Seed data: Top 10 movies
INSERT INTO movies (title, year, runtime_seconds) VALUES
  ('The Shawshank Redemption', 1994, 8520),
  ('The Godfather', 1972, 10500),
  ('The Dark Knight', 2008, 9120),
  ('Pulp Fiction', 1994, 9240),
  ('Forrest Gump', 1994, 8520),
  ('The Matrix', 1999, 8160),
  ('Inception', 2010, 8880),
  ('Goodfellas', 1990, 8760),
  ('Fight Club', 1999, 8340),
  ('Interstellar', 2014, 10140);
