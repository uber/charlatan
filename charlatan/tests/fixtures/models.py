from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///:memory:')
Session = sessionmaker(bind=engine)


class Toaster(Base):

    __tablename__ = "toasters"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    color_id = Column(String, ForeignKey('colors.name'))

    color = relationship("Color", backref='toasters')


class Color(Base):

    __tablename__ = "colors"

    id = Column(Integer, primary_key=True)
    name = Column(String)
