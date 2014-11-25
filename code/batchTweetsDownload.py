# download all tweets from a user
import helloTwitter as ht
import tweepy
import sys
import io
import time
import logging
sys.path.append("models/")
from Twitter_User import Twitter_User
from ModelBase import SessionFactory,Status
import codecs

class getTweets(object):
    consumer_key = 'BefDhm8Lfs1jBrS22JRsZER44'
    consumer_secret = 'eAg2miijN0hFy1r9e5oCHGzc10qw2NTozQLAacGEZS5jYYt8bF'

    def parseparams(self,argv):
        pc = 0
        while(pc < len(argv)):
            param = argv[pc]
            if param == '-f':
                pc += 1
                self.filename = argv[pc]
            if param == '-b':
                pc += 1
                self.bot = ht.Bot(argv[pc])
            if param == '-s':
                pc += 1
                self.startingwith = argv[pc]
            pc += 1

    def usage(self,argv):
        print "USAGE: python %s -f <userids file> -b <authenticated bot alias> -s [Optional] <starting with user id>"%(argv[0])

    def __init__(self,argv):
        self.parseparams(argv)

    def pullEntireTimeline(self, api, user, limit=None, fromStatus=None):
        sesh = SessionFactory()
        has_results = True

        if(fromStatus is not None):
            max_id = fromStatus - 1
        else:
            max_id = -1
        added = 0
        while(has_results and added < limit):
            print added, limit
            print(max_id)
            try:
                if(max_id < 0):
                    current_page = api.user_timeline(id=user.uid, count=200)
                else:
                    current_page = api.user_timeline(id=user.uid, max_id=max_id, count=200)

                has_results = len(current_page) > 0

            except tweepy.TweepError as e:
                print(str(e))
                if('limit' in str(e)):
                    time.sleep(600)
                else:
                    break

            if(has_results):
                # don't request the latest status
                max_id = min([item.id for item in current_page]) - 1

                print 'writing page of status for %s,%s' % (user.user_name, user.uid)

                for result in current_page:
                    status = Status.StatusFromTweepy(result)
                    if(sesh.query(Status).filter(Status.sid == status.sid).scalar()
                       is None and user.uid == status.author_id):
                        logging.info( 'writing status:%s' % status.sid)
                        sesh.add(status)
                        added += 1
                sesh.commit()
            time.sleep(5)

    def run(self):
        pageSize = 200
        maxTweets = 1000
        current_page = 0
        started = not hasattr(self,'startingwith')
        with io.open(self.filename) as fs:
            while(current_page*pageSize < maxTweets):
                fs.seek(0)
                sesh = SessionFactory()

                for line in fs.readlines():
                    uid = int(line.strip())
                    user = sesh.query(Twitter_User).filter(
                        Twitter_User.uid == uid).scalar()

                    if(user is None):
                        try:
                            tweepyUser = self.bot.api.get_user(uid)
                            user = Twitter_User.UserFromTweepy(tweepyUser)
                            sesh.add(user)
                            time.sleep(5)

                        except tweepy.TweepError as e:
                            print("can't find user %s" % uid)
                            print(str(e))
                            break

                    numUsersStatusesDown = user.statuses_count

                    usersStatuses = user.GetKnownStatuses(sesh)
#                    print unicode(usersStatuses.first()).encode('utf-8')
                    if not started:
                        started = line.strip() == self.startingwith

                    if started:
                        oldestStatus = usersStatuses.order_by(
                            Status.sid.asc()).first()
                        if(oldestStatus is not None):
                            fromStatus = oldestStatus.sid
                        else:
                            fromStatus = None
                        print unicode(fromStatus).encode('utf-8')

                        if(numUsersStatusesDown < maxTweets and
                           numUsersStatusesDown < usersStatuses.count()):
                            self.pullEntireTimeline(api=self.bot.api,
                                                    limit=pageSize,
                                                    user=user,
                                                    fromStatus=fromStatus
                                                    )
                    sesh.commit()
                sesh.close()

getTweets(sys.argv).run()
