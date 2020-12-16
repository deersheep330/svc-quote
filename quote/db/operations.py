import socket

from sqlalchemy.dialects.mysql import insert as __insert
from sqlalchemy import create_engine as __create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import postgresql, mysql

from ..db import Base

def get_db_hostname():
    try:
        socket.gethostbyname('db')
        print(f'db hostname = db')
        return 'db'
    except Exception as e:
        print(f'gethostbyname(\'db\') failed: {e}')
        print(f'db hostname = localhost')
        return 'localhost'

def get_api_hostname():
    try:
        socket.gethostbyname('api')
        print(f'api hostname = api')
        return 'api'
    except Exception as e:
        print(f'gethostbyname(\'api\') failed: {e}')
        print(f'api hostname = localhost')
        return 'localhost'

def create_engine(adapter, user, password, host, port, database):
    create_engine.adapter = adapter
    print(f'==> create_engine for {create_engine.adapter}')
    try:
        return create_engine.engine
    except AttributeError:
        print('create new engine')
        create_engine.engine = __create_engine(f'{adapter}://{user}:{password}@{host}:{port}/{database}',
                                               pool_pre_ping=True,
                                               pool_recycle=3600*7)
        create_engine.engine.execute('SET GLOBAL max_allowed_packet=67108864;')
        return create_engine.engine

def create_all_tables_from_orm(engine):
    Base.metadata.create_all(engine)

def start_session(engine):
    print('==> start_session()')
    try:
        session = start_session.session_maker()
        session.execute("SELECT 1")
    except AttributeError:
        print('create new session maker')
        start_session.session_maker = sessionmaker()
        start_session.session_maker.configure(bind=engine)
        session = start_session.session_maker()
        session.execute('SELECT 1')
    return session

def compile_query(query):
    """from http://nicolascadou.com/blog/2014/01/printing-actual-sqlalchemy-queries"""
    compiler = query.compile if not hasattr(query, 'statement') else query.statement.compile
    if create_engine.adapter == 'mysql+pymysql':
        return compiler(dialect=mysql.dialect())
    else:
        return compiler(dialect=postgresql.dialect())

def insert(session, model, _dict):

    table = model.__table__

    stmt = __insert(table).values(_dict)

    #print(compile_query(stmt))
    res = session.execute(stmt)
    print(f'{res.rowcount} row(s) matched')
