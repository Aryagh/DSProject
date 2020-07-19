from pymongo import MongoClient
#from hashlib import sha256
#from time import time
#from pprint import pprint
#import errors


class User:
    def __init__(self):
        client = MongoClient("localhost", 27017)
        userDatabase = client['userDatabase']
        self.userCollection = userDatabase['userDataCollection']
        self.userPostCollection = userDatabase['userPostCollection']
        self.hashtagPostCollection = userDatabase['hashtagPostCollection']
        self.hashtagUserCollection = userDatabase['hashtagPostCollection']


    def create_hashtag_document(self, hashtag_info):
        name = hashtag_info['name']
        self.hashtagPostCollection.update({"name": name}, hashtag_info, upsert=True)
        '''result = self.userCollection.find_one({"name": name})
        if not result:
            self.userCollection.insert_one(hashtag_info)'''

    def create_user_hashtag_document(self, users):
        name = users['name']
        self.hashtagUserCollection.update(name, users, upsert=True)

    def create_user_post_document(self, user_info):
        user_id = user_info['user_id']
        result = self.userPostCollection.find_one({"user_id": user_id})
        if not result:
            self.userPostCollection.insert_one(user_info)

    def create_user_document(self, user_info):
        user_id = user_info['user_id']
        result = self.userCollection.find_one({"user_id": user_id})
        if not result:
            self.userCollection.insert_one(user_info)