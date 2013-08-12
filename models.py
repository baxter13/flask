from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from database import Base, engine

class Persons(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
        
    def __repr__(self):
        return self.name
        
class Authors(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    shelfs = relationship("Shelfs", backref="authors")
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return self.name
        
class Books(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    shelfs = relationship("Shelfs", backref="books")
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name
        
class Shelfs(Base):
    __tablename__ = 'shelfs'
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    
    def __init__(self, author_id, book_id):
        self.author_id = author_id
        self.book_id = book_id