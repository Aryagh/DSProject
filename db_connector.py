from neo4j.v1 import GraphDatabase, basic_auth
from pprint import pprint
from User import *


class NeoConnector:
    def __init__(self):
        db_port = "bolt://localhost:7687"
        db_auth = ("neo4j", "12345")
        self.driver = GraphDatabase.driver(db_port, auth=basic_auth(db_auth[0], db_auth[1]))
        self.user = User()

    def run_query(self):
        with self.driver.session() as session:
            query = """ CREATE (b:BOOk) set b.uid = 22 """
            result = session.run(query)
            print(result)

    def get_result(self):
        with self.driver.session() as session:
            query = """ match(n) return n.name as name"""
            result = session.run(query).data()
            names = [r['name'] for r in result]
            print(names)

    def create_user_node(self, user_info):
        query = """ merge (u:I_USER  {uid:{uid_}}) set u+={user_info} """
        with self.driver.session() as session:
            session.run(query, uid_=user_info['user_id'], user_info=user_info)

    def create_hashtag_user_node(self, hashtag):
        query = """ merge (h:I_HASHTAG {name:{name}})  """
        with self.driver.session() as session:
            session.run(query, name=hashtag)

    def create_hashtag_likes_node(self, hashtag_post):
        query = """ merge (h:I_HASHTAG {post_pk:{post}}) """ ##how save posts???
        posts = hashtag_post['posts']
        name = hashtag_post['name']
        for post in posts:
            with self.driver.session() as session:
                session.run(query, post=post['pk'])
                self.create_hashtag_relationship(name, post['pk'])

    def create_hashtag_relationship(self, name, post_pk):
        query = """
        match(u1 {name: {name}})
        match(u2 {post_pk: {post_pk}})
        merge(u2)-[r:FOLLOWS]->(u1)"""
        with self.driver.session() as session:
            session.run(query, post_pk=post_pk, name=name).data()

    def get_user_info(self, uid):
        query = """match(u:I_USER{uid:{uid_}}) return u{.*} as user_info"""
        with self.driver.session() as session:
            result = session.run(query, uid_=uid).data()
            output = result[0]['user_info']
            pprint(output)

    def insert_follower_to_db(self, user_followers):
        source_user_id = user_followers['user_id']
        followers_data = user_followers['followers']
        for follower in followers_data:
            follower_user_id = follower['user_id']
            self.create_user_node(user_info=follower)
            self.create_relationship(source_user_id=source_user_id, follower_user_id=follower_user_id)

    def insert_followings_to_db(self, user_followings):
        source_user_id = user_followings['user_id']
        followings_data = user_followings['followings']
        for following in followings_data:
            following_user_id = following['user_id']
            self.create_user_node(user_info=following)
            self.create_relationship(source_user_id=source_user_id, follower_user_id=following_user_id)

    def create_relationship(self, source_user_id=None, follower_user_id=None):
        query = """
        match(u1 {uid: {source_user_id}})
        match(u2 {uid: {follower_user_id}})
        merge(u2)-[r:FOLLOWS]->(u1)"""
        with self.driver.session() as session:
            session.run(query, follower_user_id=follower_user_id, source_user_id=source_user_id).data()


if __name__ == "__main__":
    neo = NeoConnector()
    #neo.run_query()
    neo.get_result()
    neo.get_user_info(uid=2186371055)
