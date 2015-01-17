import sys
sys.path.append('models/')
from ModelBase import SessionFactory
from Bot import Bot

if __name__ == '__main__':
    sesh = SessionFactory()
    bots = sesh.query(Bot).all()
    for b in bots:
        b.wakeUp(sesh)
        
        try:
            print b.alias
            st = b.api.update_status('test')
            b.api.destroy_status(st.id)
#            print unicode(b.alias + ','.join([msg.text for msg in b.api.direct_messages()]))
        except Exception as e:
            print unicode(b.alias + str(e))
