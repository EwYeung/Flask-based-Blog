import requests
from faker import Faker
from appsrc.config import db, HOME
from random import randint
import json

## prefix
#HOME = 'http://localhost:5000'

faker = Faker()
faker.seed_instance(99) 
#bot 


class Apitest():
    default_password = 123456

    def __init__(self, bot):
        self.name = bot['username']
        self.password = bot['password']
        self.auth = ''
        
    def new_register(self, new_name):
        self.name = new_name
        self.password = Apitest.default_password
        reg_form = {
            "username": self.name,
            "password": self.password
        }
        reg_request = requests.post(HOME + '/register', reg_form)
        print(reg_request)

    def bot_login(self):
        login_data = {
            "username": self.name,
            "password": self.password
        }
        try:
            login_response = requests.post(HOME + '/login', login_data)
        except login_response.status as error:
            if error == 400:
                pass

        self.auth = login_response.headers["Authorization"]


    def bot_comment(self, post):
        pass

    def bot_like(self, post):
        pass

    def bot_subscribe(self, user):
        pass

    def bot_post(self):
        pass

    def bot_search(self):
        pass

if __name__ == '__main__':
    bot = Apitest()
    