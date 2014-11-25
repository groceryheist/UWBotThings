
import botUtil
import sys
sys.path.append("models/")
from ModelBase import SessionFactory, Status
from Twitter_User import Twitter_User
import tweepy
import logging
import time
consumer_key = 'BefDhm8Lfs1jBrS22JRsZER44'
consumer_secret = 'eAg2miijN0hFy1r9e5oCHGzc10qw2NTozQLAacGEZS5jYYt8bF'
access_token = '2892408134-ypFUlpxCBscL70OM1gYROlFTtEGqzSOtEHo8jL8'
access_token_secret = 'M8LRPWTnUTUwUfHFjFcOYQ7N6jpecrDlw2l7exHJeGgkF'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)



with botUtil.botUtil() as bu:
    count = 0
    chunksize = 1000
    sesh = SessionFactory()
    cur = bu.listStatuses(chunksize=chunksize,ignoreTrends=True)
    cur.itersize = chunksize
    while(True):
        statuses = cur.fetchmany(size=chunksize)
        if(not statuses):
            break
        for record in statuses: 
            statusToAdd = Status.StatusFromOldRecord(record)
            statusRecord = sesh.query(Status).filter(Status.sid==statusToAdd.sid).scalar()
            if(statusRecord is None):
               
                ## retweetId = statusToAdd.retweet_id
                ## if(retweetId is not None):
                ##     retweet = sesh.query(Status).filter(Status.sid == retweetId).scalar()
                ##     if(retweet is None):
                ##         try:
                ##             sesh.add(Status.StatusFromTweepy(api.get_status(id=retweetId)))
                ##             time.sleep(5)
                ##         except tweepy.TweepError as e:
                ##             logging.warning("page doesn't exist for status %s, originalTweet:%s"%(retweetId,statusToAdd.sid))
                ##             logging.warning(str(e))
                ##             statusToAdd.retweet_id = None
                ##             if("limit" in str(e)):
                ##                 print "sleeping"
                ##                 time.sleep(600)

                ## replyUserId = statusToAdd.user_reply_id           

                ## if(replyUserId is not None):
                ##     replyUser = sesh.query(Twitter_User).filter(Twitter_User.uid == replyUserId).scalar()

                ##     if replyUser is None:
                ##         sesh.add(Twitter_User.UserFromTweepy(api.get_user(replyUserId)))
                ##         time.sleep(5)

                author = sesh.query(Twitter_User).filter(
                    Twitter_User.uid == statusToAdd.author_id).scalar()

                if(author is not None):
                    sesh.add(statusToAdd)
                else:
                    logging.info("twitter user %s missing from DB" % statusToAdd.author_id)
                    try:
                        user = Twitter_User.UserFromTweepy(api.get_user(statusToAdd.author_id))
                        time.sleep(5)
                        print("making status and user")
                        sesh.add(user)
                        sesh.commit()
                        sesh.add(statusToAdd)
                    except tweepy.TweepError:
                        logging.warning("couldn't download user %s" % statusToAdd.author_id)
                    count += 1

        sesh.commit()
    print count
