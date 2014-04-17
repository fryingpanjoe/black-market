from bm_proto import bm_base_pb2
from bm_proto import bm_user_pb2
from bm_proto import bm_entity_pb2
from bm_proto import bm_probe_pb2


def main():
    message = bm_base_pb2.Message()
    login_request = message.Extensions[bm_user_pb2.UserLoginRequest.user_login_request]
    login_request.username = 'username'
    login_request.password = 'password'

    data = message.SerializeToString()

    new_message = bm_base_pb2.Message()
    new_message.ParseFromString(data)

    print new_message

    print 'field desc', bm_user_pb2.UserLoginRequest.user_login_request
    print 'field desc index', bm_user_pb2.UserLoginRequest.user_login_request.index
    print 'field desc number', bm_user_pb2.UserLoginRequest.user_login_request.number

    print 'other field desc number', bm_entity_pb2.EntityMessage.entity_message.number
    print 'another field desc number', bm_probe_pb2.ProbeDispatchRequest.probe_dispatch_request.number

    for (desc, value) in new_message.ListFields():
        print 'desc', desc
        print 'value', value
        print 'name', desc.name
        print 'full_name', desc.full_name
        print 'extension', desc.is_extension
        print 'extension_scope', desc.extension_scope


if __name__ == '__main__':
    main()
