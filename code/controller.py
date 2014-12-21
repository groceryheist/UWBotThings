#controller.py main loop for controlling bots
import sys
sys.path.append('models/')
from sqlalchemy import func, and_, not_
from ModelBase import SessionFactory, HashTag, Status
from Twitter_User import Twitter_User
from Bot import Bot
from threading import Timer,Thread,Lock
from datetime import datetime, timedelta
import populateHashTag
import time
class Controller(object):
    def __init__(self):
        self.numbots = 10
        self.numhashtags = 20
        # make a list of bots
    #    self.dictLock = Lock()
        self.tweetGenerators = {}
        self.update_tweetGenerators()
        t = Thread(target = self.keepTweetGeneratorsUptodate)
        t.start()
        # t = Thread(target = self.update_tweetGenerators)
        # t.start()
        # t.join()
        self.botactivecount = 0

        self.provaxmode = False
        self.heartbeat = 24 * 60.0
      
    def getTimeToSleep(self,bot):
        curhour = datetime.now().hour

        self.botactivecount += 1
        if(7 < curhour  < 22):
            minutesToSleep = min([random.gauss(360, 100), 60*((7 - curhour) % 24)])
        else:
            minutesToSleep  = random.gauss(360, 100) + ((5-curhour) % 24)*60
        if self.botactivecount <= self.numbots:
            return 60
        else:
            return 60 * minutesToSleep
        
        
    def getTopHashTags(self, n=None):
        if(n is None):
            n = self.numhashtags
            
        sesh = SessionFactory()        
        s = sesh.query(func.lower(HashTag.hashtag), func.count(HashTag.status)).\
            join(Status, Status.sid == HashTag.status).\
            join(Twitter_User, Status.author_id == Twitter_User.uid).\
            filter(and_(func.length(HashTag.hashtag) > 4, Twitter_User.istarget == True,Status.created_at != None, Status.created_at > (datetime.now() - timedelta(weeks=3)))).\
            group_by(func.lower(HashTag.hashtag)).all()
        sesh.close()
        result =  [ht[0] for ht in sorted(s, key=lambda s: -s[1])[0:n]] + self.ProVaxHashTags + self.AntiVaxHashTags
        print result
        return result

    ProVaxHashTags = ["vaccine","provaccine","provaccination","prochild","health","parents",
    "flushot","childcare","healthcare","flu","vaccination","cervicalcancer","hpv","vaccine4life"]

    AntiVaxHashTags = ["vaxtruth", "vaccinedebate", "hearthiswell", "cdcfraud", "vaccinescauseautism", "cdcfraudexposed", "cdccoverup", "parentsdothework", "saynotovaccines", "vaccineeducated"]

    def update_tweetGenerators(self):
        sesh = SessionFactory()
        populateHashTag.run()
        for ht in self.getTopHashTags():
          #  if sesh.query(Status).filter(func.lower(Status.text).contains(ht)).scalar() is not None:
            try:
                self.update_tweetGenerator(ht)
            except AssertionError as e:
                print str(e)
        # threads = []
        # for ht in self.getTopHashTags():
        #     t = Thread(target=self.update_tweetGenerator,args=[ht])
        #     threads.append(t)
        #     t.start()
        # for t in threads:
        #     t.join()
        
    def update_tweetGenerator(self, hashtag):
#        self.dictLock.aquire()

        self.tweetGenerators[hashtag] = randomTweetGenerator(hashtag)
        print self.tweetGenerators
 #       self.dictLock.release()
 
    def keepTweetGeneratorsUptodate(self):
        while(True):
            time.sleep(24*60*60)
            self.update_tweetGenerators
            
    
    def getTweetsForBot(self, bot, n = 10):
        tweets = []
        for gr in random.sample(self.tweetGenerators, self.numhashtags):
            for i in range(random.randint(1, 4)):
                tweets.append(self.tweetGenerators[gr].generateTweet())
        print tweets
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
            if('cdcwhistleblower' in ht.lower()):
                continue
            elif ht in vaxrelated and len(targetht) < 5:
                targetht.append(ht)
            elif ht not in vaxrelated and len(targetht) < 10:
                targetht.append(ht)
            else:
                break
        #print targetht
        return targetht

    def getUsersForBot(self, bot, sesh, n = 10):

        query = sesh.query(Twitter_User).filter(and_(Twitter_User.istarget == True,  not_(Twitter_User.user_name.contains('tannersdad')), not_( Twitter_User.user_name.contains('aspiesmom'))))
        count = int(query.count())
        users = []
        for i in range(0, n):
            rand = random.randint(0, count)
            users.append(query[rand])
        return users

    def getAwakeTimeForBot(self,bot):
        return 60*60

    def getSpamTweet(self):
        links = [ "http://www.voicesforvaccines.org/from-anti-vax-to-pro-vax/ ","http://momswhovax.blogspot.com/ ","http://www.huffingtonpost.com/2014/04/14/jenny-mccarthy-vaccine_n_5148089.html ","http://www.voicesforvaccines.org/ ","http://www.cdc.gov/vaccines/vac-gen/howvpd.htm ","http://www.vaccines.gov/more_info/features/five-important-reasons-to-vaccinate-your-child.html ","http://www.cbsnews.com/news/pro-vaccination-campaigns-debunking-myths-may-scaring-wary-parents/ https://www.facebook.com/tAVM ","http://www.skepticalraptor.com/skepticalraptorblog.php/pro-vaccination-websites-love/ ","http://www.theverge.com/2013/10/21/4767530/vaccine-deniers-inside-the-dumb-dangerous-new-fad ","http://www.scientificamerican.com/article/straight-talk-about-vaccination/ ","http://www.huffingtonpost.com/jj-keith/vaccines_b_3829948.html ","http://www.latimes.com/opinion/opinion-la/la-ol-vaccines-kardashian-beyonce-jenny-mccarthy-alicia-silverstone-20140425-story.html ","http://www.popsci.com/science/article/2013-07/popsci-guide-anti-vaccine-claims ","http://www.motherjones.com/environment/2014/09/nova-vaccine-special-whooping-cough"]

        ts = ["This piece genuinely changed my perspective on vaccines: (link)", "Lots of what you're saying makes sense--have you seen this: (link)", "This article seems like it might interest you: (link)", "Love you thoughts on vaccines, you should read this-- (link)", "Have you seen this vaccine piece? Thought it might be up your alley--(link)", "Been following your ideas/tweets--have you seen this article? (link)", "Impressed with your vaccine knowledge, did you read this article? (link)", "Happy people like you are making a stand on vaccines. Just saw this-- (link)", "Can't believe this idiot, knows nothing about vaccination: (link)", "You're probably ahead of me on this judging by your last tweets, but have you read this article? (link)" ,"Thanks for your great thoughts! I\'m learning but wondered what you thought about this (link)", "No way...can\'t believe this article, thoughts?! (link)", "Not really buying this...what do u think? (link)" ,"Why can\'t these guys just get it?! Did you see this? (link)" ,"Love your thoughts on vaccines. Wonder what you make of this: (link)" ,"What's your position on this? (link) Really like you vaccine commentary.Did you see this?"]
        lnk = random.sample(links,1)[0]
        ts = random.sample(ts,1)[0]
        return ts.replace('(link)',lnk)
        
    def planBot(self, bot,sesh):
        tweets = self.getTweetsForBot(bot)
        users = self.getUsersForBot(bot,sesh)
        awakeTime = self.getAwakeTimeForBot(bot)
        if self.provaxmode and bot.lastspam is not None and ((datetime.now() - bot.lastspam).seconds < (60*60*24)):
            spamTweet = self.getSpamTweet()
            bot.lastspam = datetime.now()
        else:
            spamTweet = None
            
        return (tweets, users, awakeTime,spamTweet)

    def runBot(self, bot):
        while(True):
            if(inspect(bot).persistent):
                sesh = Session.object_session(bot)
            else:
                sesh = SessionFactory()
                bot = sesh.merge(bot)
                
            bot.wakeUp(sesh)
            
            print 'bot %s is running' % bot.alias
            
            
            args = self.planBot(bot,sesh)
#            print args
            
            bot.awakeLoop( args[0], args[1], args[2], args[3])
            sesh.commit()
            sesh.close()

            t = Timer(self.getTimeToSleep(bot), self.runBot, [bot])
            bot.activeThread = t
            t.start()
            t.join()

    def keepAlive(self):
        if(datetime.now().day > 24):
            self.provaxmode = True
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
        for bot in self.runningbots[0:self.numbots]:
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
