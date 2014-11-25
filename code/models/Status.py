
from ModelBase import Status


class Status(Status):

    @staticmethod
    def StatusFromTweepy(tweepyStatus, verbose=False, trend=None):
        if(trend is not None):
            trend_name = trend.trend_name
            query = trend.query
        return Status(sid=tweepyStatus.id,
                      txt=tweepyStatus.text,
                      status_reply_id=tweepyStatus.in_reply_to_status_id,
                      author_id=tweepyStatus.author.id,
                      retweet_id=tweepyStatus.retweet.id,
                      retweet_count=tweepyStatus.retweet_count,
                      user_reply_id=tweepyStatus.in_reply_to_user_id,
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
                      status_reply_id=record.status_reply_id,
                      author_id=record.author_id,
                      retweet_id=record.retweet_id,
                      user_reply_id=record.user_reply_id,
                      retweet_count=record.retweet_count,
                      rawjson=record.rawjson,
                      created_at=record.created_at,
                      trend_name=record.trend_name,
                      trend_query=record.trend_query,
                      url=None,
                      is_truncated=None)
