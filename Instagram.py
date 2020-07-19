from InstagramAPI import InstagramAPI
import pickle
import time
import getpass
import preprocessing as prep
from pprint import pprint
from db_connector import *
from User import *


class Worker:
    def __init__(self):
        self.user_name = "test1397511"
        try:
            self.api = self.load_api_pkl()
            assert self.api.isLoggedIn
        except (FileNotFoundError, AssertionError):
            self.api = self.login()
            self.save_api_to_pkl()
        except Exception as e:
            print({'error type': type(e),'\nstr': str(e)})
        #self.get_self_user_info()
        self.neo = NeoConnector()
        self.user = User()
        print(self.neo.driver)

    def login(self):
        api = InstagramAPI(self.user_name, "sabun123")
        while True:
            api.login()
            if api.LastResponse.status_code == 200:
                break
            if api.LastResponse.status_code == 429:
                print("sleep ...")
                time.sleep(60)
            if api.LastResponse.status_code == 400:
                print("please login in your browser and verify your account"
                      ", then try again in python code!")
                exit()
            else:
                print(api.LastResponse.status_code)
                break
        return api

    def load_api_pkl(self):
        file_address = "{}.pkl".format(self.user_name)
        with open(file_address, 'rb') as f:
            api = pickle.load(f)
        print('API loaded')
        return api

    def save_api_to_pkl(self):
        file_address = "{}.pkl".format(self.user_name)
        with open(file_address, 'wb') as f:
            pickle.dump(self.api, f, pickle.HIGHEST_PROTOCOL)

    def get_self_user_info(self):
        try:
            self.api.getSelfUsernameInfo()
            user_info = self.api.LastJson['user']
            my_props = ['pk', 'username', 'full_name']
            new_user_info = {my_key: user_info[my_key] for my_key in my_props}
            pprint(new_user_info)
        except Exception as e:
            print(type(e))
            print(str(e))

    def get_target_lists(self):
        with open("target_accounts.txt", "rb") as f:
            self.user_name_list = [account.decode("utf-8").strip() for account in f.readlines()]

    def get_hashtag_list(self):
        with open("hashtags.txt", "rb") as f:
            self.hashtag_list = [account.decode("utf-8").strip() for account in f.readlines()]

    def search_user(self, user_name):
        refined_user_info = None
        try:
            self.api.searchUsername(usernameName=user_name)
            assert self.api.LastResponse.status_code == 200
            user_info = self.api.LastJson['user']
            if user_name == user_info['username']:
                refined_user_info = prep.refine_user_info(user_info=user_info)
        except Exception as ex:
            print(ex.__doc__)
        return refined_user_info

    def get_user_feed(self, user_info):
        user_posts = None
        try:
            self.api.getUserFeed(usernameId=user_info['user_id'])
            assert self.api.LastResponse.status_code == 200
            user_posts = {
                'user_id': user_info['user_id'],
                'user_name': user_info['user_name'],
                'posts': self.api.LastJson['items']
            }
        except Exception as ex:
            print(ex.__doc__)
        return user_posts

    def get_hashtag_users(self, hashtag_posts):
        name = hashtag_posts['name']
        posts = hashtag_posts['posts']
        users = None
        for post in posts:
            id = post['taken_at']
            try:
                self.api.getUserFeed(usernameId=id)
                assert self.api.LastResponse.status_code == 200
                users.extend({
                    'user_id': user_info['user_id'],
                    'user_name': user_info['user_name'],
                    'posts': self.api.LastJson['items']
                })
            except Exception as ex:
                print(ex.__doc__)
        return {'name': name, 'users': users}

    def get_user_followers(self, user_info=None):
        user_followers = None
        try:
            self.api.getUserFollowers(usernameId=user_info['user_id'])
            assert self.api.LastResponse.status_code == 200
            user_followers = {
                'user_id': user_info['user_id'],
                'user_name': user_info['user_name'],
                'followers': prep.refine_user_list(user_list=self.api.LastJson['users'])
            }
        except Exception as ex:
            print(ex.__doc__)
        return user_followers

    def get_user_followings(self, user_info=None):
        user_followings = None
        try:
            self.api.getUserFollowings(usernameId=user_info['user_id'])
            assert self.api.LastResponse.status_code == 200
            user_followings = {
                'user_id': user_info['user_id'],
                'user_name': user_info['user_name'],
                'followings': prep.refine_user_list(user_list=self.api.LastJson['users'])
            }
        except Exception as ex:
                print(ex.__doc__)
        return user_followings

    def get_hashtag_post(self, hashtag):
        try:
            hashtag_info = []
            max_id = ''
            for i in range(3):
                self.api.getHashtagFeed(hashtag, maxid=max_id)
                last_post = self.api.LastJson['items']
                #self.users_and_likers(last_post, hashtag)
                hashtag_info.extend(last_post)
                if not self.api.LastJson['more_available']:
                    break
                print(i)
                max_id = self.api.LastJson['next_max_id']
            hashtag_posts = {'name': hashtag, 'posts': hashtag_info}
            return hashtag_posts
        except Exception as ex:
            print(ex.__doc__)

    def users_and_likers(self, last_posts, name):
        for post in last_posts:
            likers = self.get_likers(post)
            #self.neo.create_hashtag_likes_node(likers)
            user = self.get_hashtag_user(post, name)
            print(user)
            #self.neo.create_hashtag_user_node(user)
            #self.neo.create_hashtag_relationship()

    def get_hashtag_user(self, post, name):
        id = post['pk']
        print(id)
        try:
            self.api.getUserFeed(usernameId=id)
            assert self.api.LastResponse.status_code == 200
            users.extend({
                #'user_id': user_info['user_id'],
                'user_name': user_info['user_name'],
                'posts': self.api.LastJson['items']
            })
        except Exception as ex:
            print(ex.__doc__)
        return {'name': name, 'users': users}

    def get_likers(self, post):
            m_id = post['id']
            self.api.getMediaLikers(m_id)
            return(self.api.LastJson)

    def analyze_users(self):
        for user_name in self.user_name_list:
            user_info = self.search_user(user_name=user_name)
            ##Import personal data to mongodb
            pprint(user_info)
            self.user.create_user_document(user_info)
            ##make nodes
            self.neo.create_user_node(user_info=user_info)     ### problem

            ##import post data to mongodb
            user_posts = self.get_user_feed(user_info=user_info)
            self.user.create_user_post_document(user_posts)

            #user_info = prep.engagement_calculator(user_posts=user_posts, user_info=user_info)

            ##followers in neo4j
            user_followers = self.get_user_followers(user_info=user_info)
            self.neo.insert_follower_to_db(user_followers)

            ##followings in neo4j
            user_followings = self.get_user_followings(user_info=user_info)
            self.neo.insert_followings_to_db(user_followings)

    def analyze_hashtags(self):
        for hashtag in self.hashtag_list:
            hashtag_posts = self.get_hashtag_post(hashtag)
            self.user.create_hashtag_document(hashtag_posts)
            #users = self.get_hashtag_users(hashtag_posts)
            #self.user.create_user_hashtag_document(users)


if __name__ == '__main__':
    worker = Worker()
    worker.get_target_lists()
    worker.get_hashtag_list()
    #worker.analyze_users()
    worker.analyze_hashtags()
