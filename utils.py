import sqlalchemy
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker

def create_sql_engine(database_name):
    '''
    Create sqlalchemy engine for postgres database
    @param database_name: str, name of database
    @return: sqlalchemy engine
    '''
    return sqlalchemy.create_engine('postgresql://localhost/' + database_name,
                                     echo         = False,
                                     connect_args = {"host": '/var/run/postgresql/'})

@contextmanager
def session_scope(engine):
    '''
    Create a sqlalchemy session and close it when finished
    @param engine: sqlalchemy engine
    @return: None
    '''
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()