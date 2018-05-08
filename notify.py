import requests 
class Line_Notify:
    
    def __init__(self ,token):
        self.__token = token
        self.__api = 'https://notify-api.line.me/api/notify'
        #self.__message=''
        
        
    def notify(self,message):
        return self.__notify(message)
        
    def __notify(self,message):
        payload = {'message': message}
        headers = {'Authorization': 'Bearer ' + self.__token}  # 発行したトークン
        line_notify = requests.post(self.__api, data=payload, headers=headers)
        return line_notify
 