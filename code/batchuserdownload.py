#script to download user data to /db flat file
import helloTwitter as ht, botUtil as bu
import tweepy
import sys,io,time
sys.path.append("./models")
from Twitter_User import Twitter_User
from ModelBase import SessionFactory

class batchuserdownload(object):
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
            pc += 1

    def usage(self,argv):
        print "USAGE: python %s -f <userids file> -b <authenticated bot alias>"%(argv[0])

    def __init__(self,argv):
        self.parseparams(argv)


    def runV2(self):

        session = SessionFactory()
        with io.open(self.filename) as fs:
            for line in fs.readlines():
                if(session.query(Twitter_User)
                   .filter(str(Twitter_User.uid) == line.strip())
                   .count() == 0):
                    try:
                        user_result = self.bot.api.get_user(line)
                        tu = Twitter_User.UserFromTweepy(user_result,
                                                         isTarget=True,
                                                         verbose=True)
                        session.add(tu)
                        session.commit()
                        time.sleep(5)
                    except Exception as e:
                        print 'fetching user data for %s' % line
                        print str(e)
                        time.sleep(5)

    def run(self):
        self.bu = bu.botUtil()
        with io.open(self.filename) as fs:
            for line in fs.readlines():
                if(not self.bu.isUserInDb(line)):
                    try:
                        user_result = self.bot.api.get_user(line)
                        self.bu.writeUser(user_result)
                        time.sleep(5.1)
                    except Exception as e:
                        print 'fetching user data for %s'%line
                        print e
                        



batchuserdownload(sys.argv).runV2()

                

                
