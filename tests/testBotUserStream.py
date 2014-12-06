import time
import sys
import unittest
import random
sys.path.append("../code/")
sys.path.append("../code/models/")


from ModelBase import SessionFactory
from Bot import Bot, BotUserListener
import tweepy


class TestBotUserStream(unittest.TestCase):
    
    def setUp(self):
        self.sesh = SessionFactory()
        self.testbotA = self.sesh.query(Bot).filter(
            Bot.alias == 'testvaxBot').first()
        self.testbotB = self.sesh.query(Bot).filter(
            Bot.alias == 'Bernardo,Officer').first()
        self.sesh.commit()
        self.sesh.close()
    def teardown(self):
        self.sesh.close()
    # def test_wakeUp(self):
    #     self.testbotA.wakeUp()
    #     print(self.testbotA)
        
    #     #test that we can wake up
    #     self.assertTrue(hasattr(
    #         self.testbotA,'api'))
        
    #     time.sleep(5)
    #     #test that we can run a search
    #     self.assertEqual(len(self.testbotA.api.search(q='bieber', count=1)), 1)

    
class TestDirectMessage(unittest.TestCase):

    class testListener(BotUserListener):

        def __init__(self, Api, testObj):
            self.testObj = testObj
            super(TestDirectMessage.testListener, self).__init__(self)

        def on_connect(self):
             self.testObj.ImReady()

        def on_data(self,raw_data):
            super(TestDirectMessage.testListener,self).on_data(raw_data)
            print raw_data                                                               
            
        def on_direct_message(self, message):
            print "simple message partly recieved"
            self.testObj.testDMCallback()
            super(TestDirectMessage.testListener, self).on_direct_message(message = message)


#       def on_connect(self):
#           self.testObj.ImReady()

    def setUpClassOnce(self):
        self.sesh = SessionFactory()
        self.testbotA = self.sesh.query(Bot).filter(
            Bot.alias == 'testvaxBot').first()
        self.testbotB = self.sesh.query(Bot).filter(
            Bot.alias == 'Bernardo,Officer').first()
        self.isComplete = False
        self.readyBots = 0
        self.count = 0
        self.testbotA.wakeUp()
        self.testbotB.wakeUp()
        #self.testbotA.follow(self.testbotB)
        #self.testbotB.follow(self.testbotA)
        print ("creating stream B")
        self.testbotB.activateUserStream(TestDirectMessage.testListener(self.testbotB.api, self))
        self.testbotB.closeUserStream()
        self.testbotB.activateUserStream(TestDirectMessage.testListener(self.testbotB.api, self))
       # print ('creating stream A')
#       self.testbotA.activateUserStream(TestDirectMessage.testListener(self.testbotA.api, self))



    def testDMCallback(self):
        self.count += 1
        if(self.count == 1):
            self.testbotB.closeUserStream()
            self.testbotA.activateUserStream(TestDirectMessage.testListener(self.testbotA.api,self))
            
        if(self.count == 2):                
            self.testbotA.closeUserStream()

            self.isComplete = True

            
    def ImReady(self):
        print ('im ready')
        self.readyBots += 1
        if self.readyBots == 1:
            self.testbotA.sendDirectMesssage(
                    target=self.testbotB, text='can you hear me bot?' + str(random.randint(0,1000)))
            print "message sent"

    def test_directMessage(self):
        self.setUpClassOnce()
        tries = 0
        while not self.isComplete and tries < 20:
            time.sleep(1)
        self.assertTrue(self.count == 2)

    def teardown(self):
        self.testbotA.closeUserStream()
        self.testBotB.closeUserStream()
        self.sesh.commit()
        self.sesh.close()
        
if __name__ == '__main__':
    unittest.main()
