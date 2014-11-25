import sys
sys.path.append('models/')
from Twitter_User import Twitter_User
from ModelBase import SessionFactory
import botUtil

with botUtil.botUtil() as bu:
    count = 0
    chunksize = 1000
    sesh = SessionFactory()
    allusers = bu.listUsers(chunksize=chunksize)

    for user in allusers:
        userToAdd = Twitter_User.UserFromPostgres(user)
        if(sesh.query(Twitter_User).filter(Twitter_User.uid == userToAdd.uid)
           .count() < 1):
            sesh.add(userToAdd)
            count += 1
        if (count % chunksize) == 0:
            sesh.commit()

    sesh.commit()
    print count
