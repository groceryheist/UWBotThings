
import json

class modelconfig(object):
    def __init__(self,path = 'modelconfig.json'):
        try:
            config = json.loads(open(path,mode='r').read())

            self.connectionString = config['connectionString']
            self.echo = config['echo']

        except Exception as e:
            print("loading model config failed")
            print(str(e))

    def __str__(self):
        return json.dumps({'connectionString':self.connectionString,'echo':self.echo})
