from model import Base
from sqlalchemy import BigInteger, Text, Column, ForeignKey



class Bot(Base):
    __tablename__ = 'bot'
    uid = Column(BigInteger, ForeignKey('Twitter_User.uid'),
                 primary_key=True)

    access_key = Column(Text)
    access_secret = Column(Text)
    email = Column(Text)
    password = Column(Text)
    alias = Column(Text)
