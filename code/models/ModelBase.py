# base class for sqlalchemy models
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
import ModelConfig as modelconfig
# import ModelBase

from sqlalchemy import BigInteger, Text, DateTime, Boolean, Column
from sqlalchemy import Integer, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()


class Twitter_User(Base):
    __tablename__ = 'twitter_user'
    uid = Column(BigInteger, primary_key=True)
    user_name = Column(Text)
    profile = Column(Text)
    created_at = Column(DateTime)
    rawjson = Column(JSON)
    user_id = Column(BigInteger)
    num_followers = Column(Integer)
    istarget = Column(Boolean)
    statuses_count = Column(Integer)
#    print 'test'
#    statuses = relationship("Status",backref='twitter_user')

    def __repr__(self):
        return """<twitter_user(id='%s',user_name='%s',profile='%s',
    created_at='%s',rawjson='%s',user_id='%s',num_followers='%s',
    istarget='%s',statuses_count='%s')>""" % (self.uid,
                                              self.user_name,
                                              self.profile,
                                              self.created_at,
                                              self.rawjson,
                                              self.user_id,
                                              self.num_followers,
                                              self.istarget,
                                              self.statuses_count)


class Status(Base):
    __tablename__ = 'status'

    sid = Column(BigInteger, primary_key=True)
    txt = Column(Text)
    status_reply_id = Column(BigInteger, ForeignKey('status.sid'))
    status_reply_id_holding = Column(BigInteger)
    author_id = Column(BigInteger, ForeignKey('twitter_user.uid'))
    retweet_id = Column(BigInteger, ForeignKey('status.sid'))
    retweet_id_holding = Column(BigInteger)
    user_reply_id = Column(BigInteger)    # ,ForeignKey('twitter_user.uid'))
    retweet_count = Column(BigInteger)
    rawjson = Column(JSON)
    created_at = Column(DateTime)
    trend_name = Column(Text)
    trend_query = Column(Text)
    url = Column(Text)
    is_truncated = Column(Boolean)
    ForeignKeyConstraint([trend_name, trend_query],
                         ['trend.trend_name', 'trend.trend_query'])

    retweets = relationship("Status", foreign_keys=[retweet_id])
    replies = relationship("Status", foreign_keys=[status_reply_id])

    def __repr__(self):
        return """<Status(sid='%s',txt='%s',status_reply_id='%s',
    status_reply_id_holding='%s',
    author_id='%s',retweet_id='%s',retweet_id_holding='%s',user_reply_id='%s',
    retweet_count='%s',rawjson='%s',created_at='%s',trend_name='%s',
    trend_query='%s',retweets='%s',replies='%s,url='%s',is_truncated='%s'""" % (
      self.sid,
      self.txt,
      self.status_reply_id,
      self.status_reply_id_holding,
      self.author_id,
      self.retweet_id,
      self.retweet_id_holding,
      self.user_reply_id,
      self.retweet_count,
      self.rawjson,
      self.created_at,
      self.trend_name,
      self.trend_query,
      self.retweets,
      self.replies,
      self.url,
      self.is_truncated)

    @staticmethod
    def StatusFromTweepy(tweepyStatus, verbose=False, trend=None):
        if(trend is not None):
            trend_name = trend.trend_name
            query = trend.query
        else:
            trend_name = None
            query = None

        if(hasattr(tweepyStatus,'retweeted_status')):
            retweeted_id = tweepyStatus.retweeted_status.id
        else:
            retweeted_id = None

        return Status(sid=tweepyStatus.id,
                      txt=tweepyStatus.text,
                      status_reply_id_holding=tweepyStatus.in_reply_to_user_id,
                      status_reply_id=None,
                      author_id=tweepyStatus.author.id,
                      retweet_id=None,
                      retweet_id_holding=retweeted_id,
                      retweet_count=tweepyStatus.retweet_count,
                      user_reply_id=tweepyStatus.in_reply_to_status_id,                      
                      rawjson=tweepyStatus._json,
                      created_at=tweepyStatus.created_at,
                      trend_name=trend_name,
                      trend_query=query,
                      url=None,
                      is_truncated=None
                      )

    @staticmethod
    def StatusFromOldRecord(record):
        print("making status")
        return Status(sid=record.id,
                      txt=record.txt,
                      status_reply_id_holding=record.status_reply_id,
                      status_reply_id=None,
                      author_id=record.author_id,
                      retweet_id=None,
                      retweet_id_holding=record.retweet_id,
                      user_reply_id=record.user_reply_id,
                      retweet_count=record.retweet_count,
                      rawjson=record.rawjson,
                      created_at=record.created_at,
                      trend_name=record.trend_name,
                      trend_query=record.trend_query,
                      url=None,
                      is_truncated=None)


class Bot(Base):
    __tablename__ = 'bot'
    uid = Column(BigInteger, ForeignKey('twitter_user.uid'),
                 primary_key=True)

    access_key = Column(Text)
    access_secret = Column(Text)
    email = Column(Text)
    password = Column(Text)
    alias = Column(Text)


class Trend(Base):
    __tablename__ = 'trend'
    trend_name = Column(Text, primary_key=True)
    query = Column(Text, primary_key=True)
    created_at = Column(DateTime)
    as_of = Column(DateTime)


    def __repr__(self):
        return """<Trend(trend_name='%s',query='%s',created_at='%s'
    ,as_of ='%s'""" % (self.trend_name,
                       self.query,
                       self.created_at,
                       self.as_of)


config = modelconfig.modelconfig()


engine = create_engine(config.connectionString, echo=config.echo)

# uncomment to create db
Base.metadata.create_all(engine)

SessionFactory = sessionmaker(bind=engine)
