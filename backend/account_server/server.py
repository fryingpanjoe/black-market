import json
import hashlib
import time
import account_server.store as store

TOKEN_TTL = 24 * 60 * 60


class HttpServer(object):

    def __init__(self, store):
        self.store = store

    def add_user(self, name, password, email):
        user_id = self.store.add_user(name, password, email)
        if user_id:
            expire_time = int(time.time() + TOKEN_TTL)
            token_hash = hashlib.sha1()
            token_hash.update(name)
            token_hash.update(email)
            token_hash.update(expire_time)
            token = '%s:%s:%s' % (user_id, expire_time, token_hash.hexdigest())
            return json.dumps({'access_token': token})
        else:
            return json.dumps({'status': 'login failed'})


class HttpServer(RPCServer):

    def __init__(self, store):
        self.store = store

    @expose('add_user')
    def add_user(self, name, password, email):
        user_id = self.store.add_user(name, password, email)
        if user_id:
            expire_time = int(time.time() + TOKEN_TTL)
            token_hash = hashlib.sha1()
            token_hash.update(name)
            token_hash.update(email)
            token_hash.update(expire_time)
            token = '%s:%s:%s' % (user_id, expire_time, token_hash.hexdigest())
            return json.dumps({'access_token': token})
        else:
            return json.dumps({'status': 'login failed'})
