from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class UserTable(Base):
    __tablename__ = 'table_test_user'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))


def create_table(engine):
    Base.metadata.create_all(engine)


def add_value(engine, value):
    Session = sessionmaker(bind=engine)
    session = Session()
    nouvelle_valeur = UserTable(name=value)
    session.add(nouvelle_valeur)
    session.commit()
