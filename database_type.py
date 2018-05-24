from sqlalchemy import create_engine

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class Freshman(Base):
    __tablename__ = 'freshmanbonus'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(Integer, primary_key=True)
    userid = Column(String(250))
    bonusCounter = Column(Integer)
    def __repr__(self):
        return "<Person(userid='%s', bonusCounter='%d')>" % (
                                self.userid, self.bonusCounter)

