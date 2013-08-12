from wtforms import Form, BooleanField, TextField, PasswordField, validators, fields
from database import db_session

class Adduser_from(Form):
    user_name = fields.TextField('Username', [validators.Length(min=2, max=50)])
    user_email = fields.TextField('E-mail', [validators.Length(min=6, max=50)])
    user_password = fields.PasswordField('Password', [validators.Length(min=6, max=50)])
    
class Addauthor_from(Form):
    author_name = TextField('Author\'s name', [validators.Length(min=2, max=50)])
    
class Addbook_from(Form):
    book_name = TextField('Book\'s name', [validators.Length(min=2, max=50)])