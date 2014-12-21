import math
import threading
from model import Base
from sqlalchemy import BigInteger, Text, Column, ForeignKey,and_,or_
import sys
sys.path.append("..")
import tweepy
from ModelBase import Status, Twitter_User, Bot, SessionFactory, Follows
import apiKeys
import json
import random
import time
from datetime import datetime

class BotUserListener(tweepy.StreamListener):
    timouts = 0
    def __init__(self, api):
        self.api = api
        self.numAdded = 0
        self.lastspam = None
       

    def on_error(self, status_code):
        if(status_code == 420):
            time.sleep(2**self.timeouts)
            self.timeouts += 1
        print status_code

             
    def on_data(self, raw_data):

        super(BotUserListener,self).on_data(raw_data)
        data = json.loads(raw_data)
        if 'limit' in data:
            if self.on_limit(data['limit']['track']) is False:
                return False
        
    def on_limit(self, track):
        print(track)
        return        
    
    def on_status(self, status):
        self.timeouts = 0
        sesh = SessionFactory()
        sesh.add(Status.StatusFromTweepy(status))
        sesh.commit()
        sesh.close()

        #TODO: Write more "I am not a bot" messages
    def on_direct_message(self, message):
        self.timeouts = 0
        print 'messages recieved'
        print message        
        jmsg = message._json
        if(jmsg['text'].contains("bot")):
            self.api.send_direct_message(
                text="Dude, I am not a fucking bot. Can I be any clearer?" + str(random.randint(0,1000)),
                user=message.user)



class Bot(Bot):
    #tweets are good tweets to make
    #target users are users for retweeting or following
    #awake time is the amount of time the bot stays active in seconds

    curtime = 0
    def nextEventTime(self,mu,sigma):
        print self.curtime
        print mu
        self.curtime += random.gauss(mu,sigma)
        return self.curtime
    
    def awakeLoop(self, tweets, targetUsers, awakeTime=1800, spamTweet=None):
        # use rest API to get my statuses and make some tweets
        # number of tweets to make is a function of activity
        # activity level is the proportion of possible actions to make
#        sesh = essionFactory()

        tweetEvents=tweets[0:int(math.ceil((self.activity_level*len(tweets))))]
   #     print tweetEvents
        if(spamTweet is not None):
            tweetEvents=[spamTweet] + tweetEvents
            
      #  print tweetEvents
        #engagewith every target user
        userinteractionEvents = targetUsers
        
        #handle my most recent retweets, relies, messages

        myMentions = self.api.mentions_timeline(count = 200, since = self.lastmention)

 #       mychanges = sesh.merge(self)
        if len(myMentions) > 0:
            self.lastmention = min([m.id for m in myMentions])

        else:
            self.lastmention = None
  #      mychanges.lastmention = self.lastmention
        
        newFollowers = self.addFollowers()

        
        Status.AddManyStatusFromTweepy(myMentions)
        mentionEvents = random.sample(myMentions, int(math.floor(self.activity_level * min([len(myMentions),20.0]))))

        myMessages = self.api.direct_messages(since = self.lastmessage, count = 200)

        if len(myMessages) > 0:
            self.lastmessage = min([m.id for m in myMessages])
        else:
            self.lastmessage = None
   #     mychanges.lastmessage = self.lastmessage

        print type(tweetEvents)
        print type(userinteractionEvents)
        print type(mentionEvents)
        print type(myMessages)
        totalEvents = len(tweetEvents) + len(userinteractionEvents)
        totalEvents += len(mentionEvents) + len(myMessages)
        totalEvents += len(newFollowers)
                                                                          
        mu = float(awakeTime)/float(totalEvents)
        sigma = mu * 0.2

        actions = []
        
        #create event timings
        for newFollower in newFollowers:
            print ('user:%s is following back user%s')%(self.alias, newFollower)
            actions.append( (self.AddFollow, [newFollower]) )

        for message in tweetEvents:
            actions.append( (self.makeStatus, [message]) )

        for user in userinteractionEvents:
            actions.append((self.engageUser, [user]))


        for mention in mentionEvents:
            actions.append((self.respondToMention, [mention]))
        
        for message in myMessages:
            actions.append((self.respondToMessage, [message]))

        random.shuffle(actions)
        events = [threading.Timer(self.nextEventTime(mu, sigma), a[0], a[1]) for a in actions]
        def runAllEvents(events):
            print 'running events'
            for e in events:
                e.start()
            for e in events:
                e.join()
                
        t = threading.Thread(target=runAllEvents,args=[events])
        t.start()
        t.join()
       # sesh.commit()
       # sesh.close()

    def respondToMessage(self, message):

        if('bot' in message.text.lower()):
            if hasattr(self,'botMessages'):
                botMsgs = ["You're kidding!","I'm not a bot dude!","WTF I'm not a fucking bot jerk!","Fuck Off I'm blocking you! I'm not a bot"]
                if(len(botMsgs) < botMessages):
                    toSend = botMsgs[-1]
                else:
                    toSend = botMsgs[botMessages]
                self.api.send_direct_message(user_id = message.sender.id , text=toSend)
                self.botMessages+=1                
            else:
                self.botMessages=1
        else:
            self.api.send_direct_message(user_id=message.sender.id, text=self.getResponseTweet())

        
    def addFollow(self,id):
        self.follow(targetUid = id)
        
    def addFollowers(self):
        sesh = SessionFactory()
#        bot = sesh.mergeno(self)
        myFollowers = self.api.followers_ids(count=5000)
        newFollowers = []
        for f in myFollowers:
            if sesh.query(Follows).filter(and_(Follows.usera == f, Follows.userb == self.uid)).scalar() is None:
                sesh.add(Follows(usera = f, userb = self.uid))
            if sesh.query(Follows).filter(and_(Follows.usera == f, Follows.userb == self.uid)).scalar() is None:
                newFollowers.append(f)
        sesh.commit()
        sesh.close()
        return newFollowers

    def getResponseTweet(self):
        return random.sample(["I'm not really sure I understand?","Where did you get that idea? Love that!","Awesome thoughts on that front.", "Where is your info coming from?", "Haha...love your opinions.", "Not following?", "Really?", "Right?!", "Not sure I'm following.", "Thanks for reaching out!", "Appreciate the interest!", "No way! Cool!", "Thanks for that.", "Muchas gracias.", "Haha", "yep yep.", "Muy bien!", "Haha. Nice!", "Radical.", "Radically glorious!", "Didn't think of that...but cool.", "Not sure?"], 1)[0]
    
    def respondToMention(self, mention):
        self.makeStatus( '@' + mention.user.screen_name + ' ' + self.getResponseTweet())

    def engageUser(self, user):
        sesh = SessionFactory()
        bot = sesh.merge(self)
        user = sesh.merge(user)
        bot.wakeUp(sesh)
        try:
            s = bot.api.user_timeline(user_id=user.uid, count=1)[0]
            bot.api.retweet(s.id)

            if random.randint(0, 5) % 3 == 1:
                bot.api.update_status(text = self.getOutReachTweet(user.user_name),in_reply_to_status_id = s.id)
        except Exception as e:
            print(str(e))
            print('for bot:%s, user:%s, status:%s'%(bot, user.uid, s.id))
            
        print ('user:%s is following user%s')%(bot.alias, user.user_name)
        self.follow(targetUid = user.uid)

    def getOutReachTweet(self,screen_name):
        ts =["Hey [user] love your thoughts!", "[user] you're ideas here are spot on.", "[user] thanks for a refreshing perspective.","[user] Thanks for pushing me to think differently?", "[user] awesome combo of info and hilarity!", "[user] your tweets are spot on. Nice work.", "[user] Rad stuff! Cool thoughts. Yo", "[user], really liking your perspective here.", "hey [user], interesting thoughts!", "[user]--great tweet content!", "[user] your tweeting skills are legendary!", "Seriously cool stuff :) [user]","Nice work [user]"]
        return random.sample(ts,1)[0].replace('[user]','@'+screen_name)
        
    def makeStatus(self, message):
        print 'trying to tweet:' + message
        try:
            self.api.update_status(status=message)
        except Exception as e:
            print 'exception maing status in Bot.py line 225'
            print str(e)
            print message
            print self
    
    def wakeUp(self, sesh):

        self.lastawake = datetime.now()
        auth = tweepy.OAuthHandler(apiKeys.consumer_key,
                                        apiKeys.consumer_secret)

        auth.set_access_token(self.access_key,
                              self.access_secret)
        self.api = tweepy.API(auth)
        sesh.commit()
    
    def activateUserStream(self, listener=None):
        if listener is None:
            listener = BotUserListener(self.api)
        self.userStream = tweepy.Stream(self.api.auth, listener)
        self.userStream.userstream(stall_warnings=True, replies=True, async=True)

    def sendDirectMesssage(self, text, target):
        #try:
            self.api.send_direct_message(text=text,user_id=target.uid)
        # except TweepError as e:
        #     if e['code'] == 151:
        #         return True
        #     else: return False
#        return False
            

    def follow(self, target = None, targetUid = None):
        sesh = SessionFactory()
        bot = sesh.merge(self)
        if(bot.uid != targetUid):
            if target is not None:
                targetUid = target.uid
            if targetUid is not None:
                if hasattr(bot,'api'):
                    bot.api.create_friendship(user_id=targetUid)
                else:
                    bot.wakeUp(sesh)
                    bot.api.create_friendship(user_id=targetUid)
                    
            else:
                raise Exception("bad argument passed to follow")

            #sesh.merge(self)
            if sesh.query(Follows).filter(and_(Follows.usera == self.uid, Follows.userb == targetUid)).scalar() is None:
                sesh.add(Follows(usera = self.uid, userb = targetUid))
                sesh.commit()
            sesh.close()

    

    def closeUserStream(self):
        self.userStream.disconnect()
