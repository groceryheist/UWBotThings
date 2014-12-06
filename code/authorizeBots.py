import tweepy
import sys
sys.path.append('models/')
from ModelBase import Bot, SessionFactory
from Twitter_User import Twitter_User
import apiKeys


def AuthorizeBot(alias):
    
    auth = tweepy.OAuthHandler(apiKeys.consumer_key,
                               apiKeys.consumer_secret)
    sesh = SessionFactory()
    redirect_url = auth.get_authorization_url()

    print alias + redirect_url
    code = raw_input()
    auth.get_access_token(code)
    api = tweepy.API(auth)
    user = Twitter_User.UserFromTweepy(api.me())
    if(sesh.query(Twitter_User).filter(Twitter_User.uid == user.uid).scalar() is None):
        sesh.add(user)
        sesh.commit()
    bot = Bot(uid=user.uid, access_secret = auth.access_token.secret, access_key=auth.access_token.key, alias = alias)
    sesh.add(bot)
    print(bot)
    print('ok')
    if(raw_input()[0] == 'y'):
        sesh.commit()
        sesh.close()


while(True):
    AuthorizeBot( raw_input() )
