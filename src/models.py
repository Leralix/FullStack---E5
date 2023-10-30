from sqlalchemy import Column, Integer,Boolean, String, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'table_test_user'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    is_checked = Column(Boolean, default=False)


