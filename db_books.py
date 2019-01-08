import csv

def tables_list(db):
  return db.execute('''
  SELECT table_name
  FROM information_schema.tables
  WHERE table_schema='public'
  AND table_type='BASE TABLE';
  ''').fetchall()

def tables_config(db):
  db.execute('''
  CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT
  );
  ''')

  db.execute('''
  CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    year INT,
    isbn TEXT
  );
  ''')

  db.execute('''
  CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    book_id INT REFERENCES books(id),
    rating INT,
    review TEXT
  );
  ''')

  db.commit()

  if db.execute('SELECT * FROM books LIMIT 1').rowcount==0:
    stream=open('books.csv', 'r')
    first_row=True
    for isbn, title, author, year in csv.reader(stream):
      if first_row:
        first_row=False
        continue
      db.execute('INSERT INTO books (title, author, year, isbn) VALUES (:title, :author, :year, :isbn)',
                 {'title':title, 'author':author, 'year':int(year), 'isbn':isbn})
    db.commit()
    stream.close()
