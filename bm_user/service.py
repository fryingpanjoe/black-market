import hashlib
import time
import bm_proto
import bm_shared.rpc
#import store as store

TOKEN_TTL = 24 * 60 * 60
SECRET = "My cans, my precious antique cans!"


class UserService(bm_shared.rpc.RPCService):

    def __init__(self, store):
        self.store = store

    @bm_shared.rpc.rpc('bm://user/add-user')
    def add_user(self, client_id, request):
        #LOG.info('Client %d called add-user')
        request = bm_proto.UserRegisterRequest()
        request.ParseFromString(request.message.payload)
        user_id = self.store.add_user(
            request.name, request.password, request.email)
        if user_id:
            expire_time = int(time.time() + TOKEN_TTL)
            token_hash = hashlib.sha1()
            token_hash.update(request.name)
            token_hash.update(request.email)
            token_hash.update(expire_time)
            token_hash.update(SECRET)
            token = '%s:%s:%s' % (user_id, expire_time, token_hash.hexdigest())
            request.reply(status_code=200, payload=token)
        else:
            request.reply(status_code=400)
