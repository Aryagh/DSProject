class UserPassError(Exception):
    def __init__(self):
        print('user name or password is not correct')
