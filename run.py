from flask import Flask, url_for, render_template, request, redirect, session
from database import db_session
from settings import *
import sqlite3
import random
import re
from forms import Adduser_from, Addauthor_from, Addbook_from
from models import Persons, Authors, Books, Shelfs

app = Flask(__name__)
app.config.from_object(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

#ENCODING USER'S PASSWORD
def password_encode(password, key=135):
    enc_password = ''
    pwd = list(password)
    pwd = [ord(x)*135 for x in pwd]
    for p in pwd:
        enc_password += str(p)+'&'
    enc_password += 'k'+str(key)
    return enc_password

#DECODING USER'S PASSWORD
def password_decode(password):
    key = int(password.split('k',1)[1])
    password = password.split('k',1)[0]
    temp_pwd = []
    for i in xrange(1, password.count('&')+1):
        temp_pwd.append(password.split('&',1)[0])
        password = password.split('&',1)[1]
    temp_pwd = [chr(int(x)/key) for x in temp_pwd]
    for x in temp_pwd:
        password += str(x)
    return password
    
    
#LOGIN PAGE
@app.route('/login', methods=['GET', 'POST'])
def login():
    ER_MESSAGE = ''
    if request.method == 'POST':
        user_name = request.form['user_name']
        user_password = password_encode(request.form['user_password'])
        user = Persons.query.filter(Persons.name == user_name, Persons.password == user_password).first()
        if not (user == None):
            session['user_name'] = user_name
            return redirect(url_for('library_main'))
        else:
            ER_MESSAGE = 'Login unsuccessful!'
    variables = {'STATIC_URL' : url_for('static', filename=''), 'ER_MESSAGE' : ER_MESSAGE}
    return render_template('login_page.html', **variables)

#LOGOUT
@app.route('/logout')
def logout():
    session.pop('user_name', None)
    return redirect(url_for('library_main'))

#SESSION HANDLER
def settings(key):
    try:
        USER = session['user_name']
        SETTINGS = {'USER': session['user_name'], 'MESSAGE': 'Nice to see you here', 'STATIC_URL': url_for('static', filename='')}
    except:
        SETTINGS = {'USER': '', 'MESSAGE': 'Nice to see you here', 'STATIC_URL': url_for('static', filename='')}
    return SETTINGS[key]
    
#VALIDATION
def validator(**inputs):
    errors = 0
    for i in inputs.keys():
        if len(inputs[i])<3:
            errors += 1
    try:
        if not (re.match(r'\w+@\w+', inputs['user_email'])):
            errors += 1
    except:
        pass


    #VALIDATION RESULT
    if errors:
        return False
    else:
        return True

#CHECK&DELETE FOR ZOMBIES-BOOKS
def zombie_book():
    for book in Books.query.all():
        if Shelfs.query.filter(Shelfs.book_id == book.id).first() == None:
            db_session.delete(book)
    db_session.commit()

    
#MAIN PAGE
@app.route('/', methods=['GET', 'POST'])
def library_main():
    
    #SETTINGS
    search = None
    
    #GET ALL ITEMS
    persons = Persons.query.all()
    books_list = Books.query.order_by(Books.id.desc())
    authors_list = Authors.query.all()[:10]
    random.shuffle(authors_list)

    #GET BOOKS&AUTHORS RELATIONS
    books_main = []
    url_authors = []
    for book in books_list[:10]:
        book_authors_ids = Shelfs.query.filter(Shelfs.book_id == book.id)
        for ids in book_authors_ids:
            url_authors.append('<a href=\"'+str(ids.author_id)+'\">'+str(Authors.query.get(ids.author_id))+'</a>')
        books_main.append((book, url_authors))
        url_authors = []

    #SEARCH MODULE
    search_result = []
    search_is = False
    if request.method == 'POST':
        search_is = True
        search = request.form['text_box']
        if search:
            try:
                search_result += ['Author: <a href=\"'+str(author.id)+'\">'+str(author)+'</a>' for author in Authors.query.filter(Authors.name.like('%'+search+'%'))]
                search_result += ['Book: '+str(book) for book in Books.query.filter(Books.name.like('%'+search+'%'))]
            except:
                pass
        else:
            search_is = False

                            
    variables = {'authors_list' : authors_list,
                 'books_list' : books_list[:10],
                 'search_result' : search_result,
                 'MESSAGE' : settings('MESSAGE'),
                 'USER' : settings('USER'),
                 'persons' : persons,
                 'STATIC_URL' : settings('STATIC_URL'),
                 'books_main' : books_main,
                 'search_is' : search_is,
                 'search_query' : search,
                 }
    return render_template('main.html', **variables)

#PAGE WITH AUTHORS LIST
@app.route('/authors_all', methods=['GET', 'POST'])
def library_authors_all():
    
    #SETTINGS
    search = None
    
    #GET ALL ITEMS
    authors_list = Authors.query.all()

    #SEARCH&ACTIONS MODULE
    search_result = []
    if request.method == 'POST':
        elem_id = None
        search = None
        new_name = None
        edit_id = None
   
    #RENAME AUTHOR     
        try:
            new_name = request.form['input_new_name']
            edit_id = request.form['edit_hidden_input']
        except:
            pass
        
        if new_name and edit_id:
            author = Authors.query.get(edit_id)
            author.name = new_name
            db_session.commit()
    
    #DELETE AUTHOR    
        try:
            elem_id = request.form['elem_id']
        except:
            pass
        
        if elem_id:
            elem_id = request.form['elem_id']
            author = Authors.query.get(elem_id)
            db_session.delete(author)
            for author in Shelfs.query.filter(Shelfs.author_id == elem_id):
                db_session.delete(author)
            db_session.commit()
            
            zombie_book()

     #SEARCH AUTHOR
        try:
            search = request.form['search']
        except:
            pass    
            
        if search:            
            for author in authors_list:
                if search and search.lower() in str(author).lower():
                    author = Authors.query.filter(Authors.name == str(author)).first()
                    search_result.append(author)
        
        if search_result:
            authors_list = search_result
                            
    variables = {'authors_list' : authors_list,
                 'search_result' : search_result,
                 'MESSAGE' : settings('MESSAGE'),
                 'USER' : settings('USER'),
                 'STATIC_URL' : settings('STATIC_URL'),
                 'search_query' : search,
                 }
    return render_template('authors_all.html', **variables)

#PAGE WITH BOOKS LIST
@app.route('/books_all', methods=['GET', 'POST'])
def library_books_all():
    
    #SETTINGS
    search = None
    
    #GET ALL ITEMS
    books_list = Books.query.all()
    authors_list = Authors.query.all()

    #GET BOOKS&AUTHORS RELATIONS
    books_main = []
    url_authors = []
    for book in books_list:
        book_authors_ids = Shelfs.query.filter(Shelfs.book_id == book.id)
        for ids in book_authors_ids:
            url_authors.append('<a href=\"'+str(ids.author_id)+'\">'+str(Authors.query.get(ids.author_id))+'</a>')
        books_main.append((book, url_authors))
        url_authors = []

    #SEARCH MODULE
    search_result = []
    search_is = False
    if request.method == 'POST':
        elem_id = None
        search = None
        new_name = None
        edit_id = None
    
    #RENAME BOOK
        try:
            new_name = request.form['input_new_name']
            edit_id = request.form['edit_hidden_input']
        except:
            pass
        
        if new_name and edit_id:
            book = Books.query.get(edit_id)
            book.name = new_name
            db_session.commit()
    
    #DELETE BOOK  
        try:
            elem_id = request.form['elem_id']
        except:
            pass
                    
        if elem_id:
            book = Books.query.get(elem_id)
            db_session.delete(book)
            for book in Shelfs.query.filter(Shelfs.book_id == elem_id):
                db_session.delete(book)            
            db_session.commit()
            return elem_id
            
     #SEARCH BOOK
        try:
            search = request.form['search']
        except:
            pass
        
        if search:        
            for book in Books.query.filter(Books.name.like('%'+search+'%')):
                book_authors_ids = Shelfs.query.filter(Shelfs.book_id == book.id)
                url_authors = []
                for ids in book_authors_ids:
                    url_authors.append('<a href=\"'+str(ids.author_id)+'\">'+str(Authors.query.get(ids.author_id))+'</a>')
                search_result.append((book, url_authors))
                    
            if search_result:
                books_main = search_result
            
                            
    variables = {'authors_list' : authors_list,
                 'books_list' : books_list,
                 'search_result' : search_result,
                 'MESSAGE' : settings('MESSAGE'),
                 'USER' : settings('USER'),
                 'STATIC_URL' : settings('STATIC_URL'),
                 'books_main' : books_main,
                 'search_query' : search,
                 }
    return render_template('books_all.html', **variables)


#UNIQUE AUTHOR PAGE
@app.route('/<author_pid>/', methods=['GET', 'POST'])
def library_author(author_pid):
    
    form = Addbook_from(request.form)    
    if request.method == 'POST':
        elem_id = None
    
    #UNLINK BOOK FROM AUTHOR    
        try:
            elem_id = request.form['edit_hidden_input']
        except:
            pass
                    
        if elem_id:
            book = Books.query.get(elem_id)
            shelf = Shelfs.query.filter(Shelfs.book_id == book.id, Shelfs.author_id == author_pid).first()
            db_session.delete(shelf)
            db_session.commit()
            
            zombie_book()
            
    #ADD&LINK NEW BOOK TO AUTHOR
        try:
            book_name = form.book_name.data
        except:
            pass
        
        if book_name:
            if validator() and not Books.query.filter(Books.name == book_name).first():
                db_session.add(Books(book_name))
                db_session.commit()
            
            if validator():
                db_session.add(Shelfs(author_pid, Books.query.filter(Books.name == book_name).first().id))
                db_session.commit()
    
    author = Authors.query.filter(Authors.id == author_pid).first()
    books_ids = Shelfs.query.filter(Shelfs.author_id == author_pid)
    books_list = []
    
    for ids in books_ids:
        books_list.append(Books.query.get(ids.book_id))

    variables = {'author' : author,
                'books_list' : books_list,
                'form' : form,
                'MESSAGE' : settings('MESSAGE'),
                'USER' : settings('USER'),
                'STATIC_URL' : settings('STATIC_URL'),
                 }
    return render_template('author.html', **variables)

#ADD USER PAGE
@app.route('/add_user/', methods=['GET', 'POST'])
def library_add_user():
    ER_MESSAGE = ''    
    form = Adduser_from(request.form)
    
    if request.method == 'POST':
        inputs = {'user_name':form.user_name.data, 'user_email':form.user_email.data, 'user_password':form.user_password.data} 
        if validator(**inputs):
            db_session.add(Persons(form.user_name.data, form.user_email.data, password_encode(form.user_password.data)))
            db_session.commit()
            return redirect(url_for('library_main'))
        else:
            ER_MESSAGE = 'En error while adding user! Syntax error or maybe he is already exists in database!'
            
    variables = {'form' : form,
                 'MESSAGE' : settings('MESSAGE'),
                 'USER' : settings('USER'),
                 'STATIC_URL' : settings('STATIC_URL'),
                 'ER_MESSAGE' : ER_MESSAGE
                 }
    return render_template('admin_add_user.html', **variables)

#ADD AUTHOR PAGE
@app.route('/add_author/', methods=['GET', 'POST'])
def library_add_author():
    ER_MESSAGE = ''    
    form = Addauthor_from(request.form)
    if request.method == 'POST':
        inputs = {'user_name':form.author_name.data}
        if validator(**inputs) and not Authors.query.filter(Authors.name == form.author_name.data).first():
            db_session.add(Authors(form.author_name.data))
            db_session.commit()
            return redirect(url_for('library_authors_all'))
        else:
            ER_MESSAGE = 'En error while adding author! Syntax error or maybe he is already exists in database!'
    
    message = 'Add author interface'
    variables = {'form' : form,
                 'MESSAGE' : settings('MESSAGE'),
                 'USER' : settings('USER'),
                 'STATIC_URL' : settings('STATIC_URL'),
                 'ER_MESSAGE' : ER_MESSAGE
                 }
    return render_template('admin_add_author.html', **variables)


if __name__ == '__main__':
    app.run(host=HOST, port=80, debug=DEBUG)