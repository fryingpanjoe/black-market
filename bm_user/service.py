import json
import hashlib
import time
import bm_shared.rpc
import store as store

TOKEN_TTL = 24 * 60 * 60


class UserService(bm_shared.rpc.RPCService):

    def __init__(self, store):
        self.store = store

    @rpc('bm://user/add-user')
    def add_user(self, client_id, message):
        LOG.info('Client %d called add-user')
        request = UserRegisterRequest()
        request.ParseFromString(message.payload)
        user_id = self.store.add_user(
            request.name, request.password, request.email)
        if user_id:
            expire_time = int(time.time() + TOKEN_TTL)
            token_hash = hashlib.sha1()
            token_hash.update(request.name)
            token_hash.update(request.email)
            token_hash.update(expire_time)
            token = '%s:%s:%s' % (user_id, expire_time, token_hash.hexdigest())
            return json.dumps({'access_token': token})
        else:
            return json.dumps({'status': 'login failed'})
