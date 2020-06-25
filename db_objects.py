# import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Sequence

# from uuid import uuid4


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    name = Column(String(20))
    complete_folowers = relationship('CompleteFolower', back_populates='user')

    def __repr__(self):
        return "<User (name='%s')>" % self.name


class CompleteFolower(Base):
    __tablename__ = 'complete_folowers'

    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String(50))
    viewed = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship(User, primaryjoin=user_id == User.id)

    def __repr__(self):
        return "<Folower URL(url='%s')>" % self.url


def connect_db(DB_PATH):
    engine = create_engine(DB_PATH)
    Base.metadata.create_all(engine)
    session = sessionmaker(engine)
    return session()

def create_user(name):
    user = User(name=name)
    return user

def create_folower_url(user, url):
    folower_url = CompleteFolower(url=url, user=user)
    return folower_url


DB_PATH = 'sqlite:///db_folowers.sqlite3'


if __name__ == '__main__':
    session = connect_db(DB_PATH)
    # user = session.query(User).filter(User.name=='nastya_pro_sugaring').first().complete_folowers
    # count = len(user.complete_folowers)
    