def signup(db, name, password, retype):
  if not (name and password and retype):
    message='Sorry, all fields required.'
  elif db.execute('SELECT * FROM users WHERE name=:name', {'name':name}).rowcount>0:
    message='Sorry, this username already exists.'
  elif password!=retype:
    message='Sorry, retyped password not match.'
  else:
    result=db.execute('INSERT INTO users (name, password) VALUES (:name, :password) RETURNING id',
      {'name':name, 'password':password}).fetchall()
    db.commit()
    return True, result[0][0] #id
  return False, message

def signin(db, name, password):
  if not (name and password):
    message='Sorry, all fields required.'
  else:
    result=db.execute('SELECT * FROM users WHERE name=:name and password=:password', {'name':name, 'password':password}).fetchall()
    if not result:
      message='Sorry, username and/or password not correct.'
    else:
      return True, result[0][0] #id
  return False, message
