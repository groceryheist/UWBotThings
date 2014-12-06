#controller.py main loop for controlling bots
import sys
sys.path.append('models/')
from sqlalchemy import func
from ModelBase import SessionFactory, HashTag, Status
from Twitter_User import Twitter_User
from Bot import Bot

class Controller(object):
    def __init__(self):
        # make a list of bots
        
        self.tweetGenerators = {}
        self.update_tweetGenerators()
        self.provaxmode = False
        self.heartbeat = 24 * 60.0
      
    def getTimeToSleep(self,bot):
        curhour = datetime.now().hour
        if(7 < curhour  < 22):
            minutesToSleep = min([random.gauss(360, 100), 60*((7 - curhour) % 24)])
        else:
            minutesToSleep  = random.gauss(360, 100) + ((5-curhour) % 24)*60
        return minutesToSleep * 60
        
    def getTopHashTags(self, n = 40):
        sesh = SessionFactory()
        s = sesh.query(HashTag.hashtag, func.count(HashTag.status)).\
            join(Status, Status.sid == HashTag.status).\
            join(Twitter_User, Status.author_id == Twitter_User.uid).\
            filter(Twitter_User.istarget ==True).\
            group_by(HashTag.hashtag).all()
        sesh.close()
        return [ht[0] for ht in sorted(s, key=lambda s: -s[1])[0:n]]

    ProVaxHashTags = ["vaccine","provaccine","provaccination","prochild","health","parents",
    "flushot","childcare","healthcare","flu","vaccination","cervicalcancer","hpv","vaccine4life"]

    AntiVaxHashTags = ["vaxtruth", "vaccinedebate", "hearthiswell", "cdcfraud", "vaccinescauseautism", "cdcfraudexposed", "cdccoverup", "cdcwhistleblower","parentsdothework", "saynotovaccines", "vaccineeducated"]

    def update_tweetGenerators(self):
        for ht in self.getTopHashTags():
            self.update_tweetGenerator(ht)
    
    def update_tweetGenerator(self, hashtag):
        self.tweetGenerators[hashtag] = randomTweetGenerator(hashtag)
    
    
    def getTweetsForBot(self, bot, n = 5):
        tweets = []
        for gr in random.sample(self.tweetGenerators,10):
            for i in range(random.randint(0, 5)):
                tweets.append(self.tweetGenerators[gr].generateTweet())
        return tweets[0:5]

    def getTargetHashTags(self,bot):
        targetht = []
        if not self.provaxmode:
            vaxrelated = self.AntiVaxHashTags
        else:
            vaxrelated = self.ProVaxHashTags
            
        #take up to 5 antivax tags
        topht = self.getTopHashTags(n=400)
        for ht in topht:
            if ht in vaxrelated and len(targetht) < 5:
                targetht.append(ht)
            elif ht not in vaxrelated and len(targetht) < 10:
                targetht.append(ht)
            else:
                break
        print targetht
        return targetht

    def getUsersForBot(self, bot, sesh, n = 5):

        query = sesh.query(Twitter_User).filter(Twitter_User.istarget == True)
        count = int(query.count())
        users = []
        for i in range(0, n):
            rand = random.randint(0, count)
            users.append(query[rand])
        return users

    def getAwakeTimeForBot(self,bot):
        return 30*60
    
    def planBot(self, bot,sesh):
        tweets = self.getTweetsForBot(bot)
        users = self.getUsersForBot(bot,sesh)
        awakeTime = self.getAwakeTimeForBot(bot)
        return (tweets, users, awakeTime)

    def runBot(self, bot):
        while(True):
            if(inspect(bot).persistent):
                sesh = Session.object_session(bot)
            else:
                sesh = SessionFactory()
                bot = sesh.merge(bot)
                
            bot.wakeUp(sesh)
            
            print 'bot %s is running'%bot.alias
            
            
            args = self.planBot(bot,sesh)
#            print args
            
            bot.awakeLoop( args[0], args[1], args[2])
            sesh.commit()
            sesh.close()

            t = Timer(self.getTimeToSleep(bot), self.runBot, [bot])
            bot.activeThread = t
            t.start()
            t.join()

    def keepAlive(self):
        for bot in self.runningbots:
            sesh = SessionFactory()
            bot = sesh.merge(bot)
            if bot.lastawake is not None and ((datetime.now() - bot.lastawake).seconds / 60.0) < self.heartbeat:
                if hasattr('bot', 'activeThread'):
                    bot.activeThread.cancel()
                    self.runBot(bot)
            time.sleep(self.heartbeat / 2.0)
        
    def run(self):
        #initial loop
        sesh = SessionFactory()
        bots = sesh.query(Bot)

        events = []
        self.runningbots = bots.filter(Bot.botrole == 'score').all()
        print self.runningbots
        for bot in self.runningbots:
            events.append(Timer(self.getTimeToSleep(bot), self.runBot,[bot]))
        sesh.commit()
        sesh.close()
        for e in events:
            print('starting main loop')
            e.start()

        
        #watch each bot every 6 hours and start a new thread if they are dead
        keepBotsAliveThread = Thread(target=self.keepAlive)
        keepBotsAliveThread.start()
        keepDBAliveThread = Thread(target=self.keepDbAlive)
        keepDBAliveThread.start()
        keepBotsAliveThread.join()
        
    def keepDbAlive(self):
        sesh = SessionFactory()
        sesh.query(Bot).first()
        sesh.close()
        time.sleep(60)
        
if __name__ == '__main__':
    from HelloMarkov import randomTweetGenerator
    ctr = Controller()
    while(True):
        import random

        from threading import Timer,Thread
        import time
        from datetime import datetime
        from sqlalchemy import inspect
        from sqlalchemy.orm import Session

        try:
            t = Thread(target = ctr.run)
            t.start()
            t.join()
        except Exception as e:
              print str(e)
              time.sleep(60)
