# use sql alchemy to interface with the db

from ModelBase import Twitter_User, SessionFactory, Status
import sys
sys.path.append("..")
import json


class Twitter_User(Twitter_User):

    @staticmethod
    def UserFromTweepy(tweepyUser, isTarget=False, verbose=False):
        uid = tweepyUser.id
        name = tweepyUser.screen_name
        user_id = tweepyUser.id
        created_at = tweepyUser.created_at
        profile = tweepyUser.description
        rawjson = json.dumps(tweepyUser._json)
        followers_count = tweepyUser.followers_count
        statuses_count = tweepyUser.statuses_count
        if(verbose):
            print("create user object for %s, %s" % (uid, name))

        return Twitter_User(created_at=created_at, user_name=name,
                            profile=profile, uid=uid,
                            num_followers=followers_count,
                            user_id=user_id, rawjson=rawjson,
                            istarget=isTarget,
                            statuses_count=statuses_count)
    @staticmethod
    def UserFromPostgres(user):
        uid = user.id
        user_name = user.user_name
        profile = user.profile
        created_at = user.created_at
        rawjson = user.rawjson
        user_id = user.user_id
        num_followers = user.num_followers
        isTarget = user.istarget
        statuses_count = user.statuses_count
        return Twitter_User(uid=uid, user_name=user_name, profile=profile,
                            created_at=created_at,
                            rawjson=rawjson,
                            user_id=user_id,
                            num_followers=num_followers,
                            istarget=isTarget,
                            statuses_count=statuses_count)

    def GetKnownStatuses(self, sesh=None):
        if sesh is None:
            sesh = SessionFactory()

        return sesh.query(Status).filter(Status.author_id == self.uid)
