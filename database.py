from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import DATABASE

engine = create_engine('sqlite:///'+DATABASE, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base(engine)
Base.query = db_session.query_property()

#DB INITIALIZATION
def init_db():
    Base.metadata.create_all(bind=engine)
    
# tables = ['persons', 'authors', 'books', 'shelf']  - all tables in db (use for fast clear)
def clear_db(*tables):
    import models
    connection = engine.connect()
    queries = []
    for t in tables:
        queries.append('DROP TABLE if exists '+t)
    map (connection.execute, queries)