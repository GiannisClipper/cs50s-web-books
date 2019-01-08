import os
from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import db_books, users

app=Flask(__name__)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
# Set up database
engine=create_engine(os.getenv("DATABASE_URL"))
db=scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
  try:
    if not session['user_name']:
      raise Exception
    return render_template('book_search.html', user_name=session['user_name'], title='', author='', year='', isbn='', books=[])
  except:
    return render_template('signin.html', message='', name='', password='')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
  session['user_name']=None
  session['user_id']=None
  if request.method=='POST':
    ok, message=users.signup(db, request.form.get('name'), request.form.get('password'), request.form.get('retype'))
    if ok:
      session['user_id']=message
      session['user_name']=request.form.get('name')
      return render_template('book_search.html', user_name=session['user_name'], title='', author='', year='', isbn='', books=[])
    else:
      return render_template('signup.html', message=message, name=request.form.get('name'), password=request.form.get('password'), retype=request.form.get('retype'))
  else:
    return render_template('signup.html', message='', name='', password='', retype='')

@app.route("/signin", methods=['GET', 'POST'])
def signin():
  session['user_name']=None
  session['user_id']=None
  if request.method=='POST':
    ok, message=users.signin(db, request.form.get('name'), request.form.get('password'))
    if ok:
      session['user_id']=message
      session['user_name']=request.form.get('name')
      return render_template('book_search.html', user_name=session['user_name'], title='', author='', year='', isbn='', books=[])
    else:
      return render_template('signin.html', message=message, name= request.form.get('name'), password=request.form.get('password'))
  else:
    return render_template('signin.html', message='', name='', password='')

@app.route("/signout")
def signout():
  _=session.get('user_name')
  session['user_name']=None
  session['user_id']=None
  return render_template('signout.html', user_name=_)

@app.route("/book_search", methods=['GET', 'POST'])
def book_search():
  if not session['user_name']:
    return render_template('signin.html', message='', name='', password='')
  int0=lambda x: int(x) if x.isdigit() else 0
  if request.method=='POST':
    books=db.execute('SELECT * FROM books WHERE title LIKE :title AND author LIKE :author AND (:year=0 OR year=:year) AND isbn LIKE :isbn LIMIT 20',
      {'title':request.form.get('title')+'%', 'author':request.form.get('author')+'%', 'year':int0(request.form.get('year')), 'isbn':request.form.get('isbn')+'%'}).fetchall()
    return render_template('book_search.html', user_name=session['user_name'], title=request.form.get('title'), author=request.form.get('author'), year=request.form.get('year'), isbn=request.form.get('isbn'), books=books)
  else:
    return render_template('book_search.html', user_name=session['user_name'], title='', author='', year='', isbn='', books=[])

@app.route("/book_page/<int:id>", methods=['GET'])
def book_page(id):
  books=db.execute('SELECT * FROM books WHERE id=:id', {'id':id}).fetchall()
  if books:
    import requests
    res=requests.get('https://www.goodreads.com/book/review_counts.json', params={'key':'f6LP1gCONQdBlA6pkr6ICQ', 'isbns':books[0][4]})
    greads_ratings_count=res.json()['books'][0]['work_ratings_count'] if res.ok else None
    greads_ratings_avg=res.json()['books'][0]['average_rating'] if res.ok else None
    reviews=db.execute('SELECT users.name, review, rating FROM reviews LEFT JOIN users ON users.id=reviews.user_id WHERE reviews.book_id=:id ORDER BY reviews.id', {'id':books[0][0]}).fetchall()
    return render_template('book_page.html', user_name=session['user_name'], id=books[0][0], title=books[0][1], author=books[0][2], year=books[0][3], isbn=books[0][4], greads_ratings_count=greads_ratings_count, greads_ratings_avg=greads_ratings_avg, reviews=reviews, 
      reviewable=False if session['user_name'] in map(lambda x: x[0], reviews) else True)
  else:
    return render_template('book_page.html', user_name=session['user_name'], id=None, title=None, author=None, year=None, isbn=None, greads_ratings_count=None, greads_ratings_avg=None, reviews=[], reviewable=False)

@app.route("/review_submit", methods=['POST'])
def review_submit():
  book_id=request.form.get('book_id')
  review=request.form.get('review')
  rating=request.form.get('rating')
  if review and rating:
    db.execute('INSERT INTO reviews (user_id, book_id, review, rating) VALUES (:user_id, :book_id, :review, :rating)',
      {'user_id':session['user_id'], 'book_id':int(book_id), 'review':review, 'rating':int(rating)})
    db.commit()
  return book_page(book_id)

@app.route("/tables_list")
def tables_list():
  return str(db_books.tables_list(db))

@app.route("/tables_config")
def tables_config():
  db_books.tables_config(db)
  return str(db_books.tables_list(db))

if __name__=='__main__':
  app.run(debug=True)
