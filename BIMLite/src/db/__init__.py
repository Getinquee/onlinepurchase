__author__ = 'naveen.krishnan'

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from BIMLite.src.db.model import metadata


def initialize_database_connectivity(connection_url, echo=True, pool_recycle=-1):
    """ The consumer/ client of database operation must invoke initialize_database_connectivity at module level
    :param pool_recycle - this causes the pool to recycle connections after the given number of seconds has passed
                          It defaults to -1, or no timeout. Leave it default for most of the cases.
    """
    if connection_url is None:
        raise TypeError("Database connection URL must be supplied to initialize database engine.")
    global engine
    engine = create_engine(connection_url, echo=echo, pool_recycle=pool_recycle)
    global SessionFactory
    SessionFactory = sessionmaker(bind=engine)


def create_db_objects_from_models():
    """ Testing use only. Do not consume this API. """
    metadata.create_all(engine, checkfirst=False)


def drop_db_objects_from_models():
    """ Testing use only. Do not consume this API. """
    metadata.drop_all(engine, checkfirst=False)
    engine.dispose()


def initialize_session_factory(session_factory):
    """ Testing use only. Do not consume this API. """
    global SessionFactory
    SessionFactory = session_factory
    return SessionFactory


def create_session():
    if SessionFactory is None:
        raise TypeError("Not connected to database, you should invoke initialize_database_connectivity with a valid "
                        "connection URL prior to creating session")
    return scoped_session(SessionFactory)


def create_session_on_in_memory_database():
    """ Testing use only. Do not consume this API. """
    engine = create_engine('sqlite:///:memory:', echo=True)
    metadata.create_all(engine, checkfirst=False)
    session = scoped_session(sessionmaker(engine))
    return session


def create_session_factory_with_in_memory_database():
    """ Testing use only. Do not consume this API. """
    engine = create_engine('sqlite:///:memory:', echo=False)
    metadata.create_all(engine, checkfirst=False)
    return sessionmaker(engine)
