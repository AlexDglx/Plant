import json
import urllib, requests
from datetime import datetime

class jsonConfigFile:
    #read json file
    def readJson(jsonPath:str) -> dict:
        with open(jsonPath, "r") as file:
            a = json.load(file)
            file.close()
        return a
    #write date and time - for last modification
    def writeJson(jsonPath:str,newData:dict) -> any:
        with open(jsonPath,"w") as newJson:
            json.dump(newData,newJson,indent=4)
            newJson.close()

def Send_message(message: dict):

    token = jsonConfigFile.readJson('telegram_cred.json')
    api_key = token['telegram']['ApiKey']
    chat_id = token['telegram']['chat_id']

    
    url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (
    
    api_key, chat_id, urllib.parse.quote_plus(f'{message["Title"]}\n\n{message["Body"]}'))
    _ = requests.get(url, timeout=10)