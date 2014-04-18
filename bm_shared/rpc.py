import logging
import network

LOG = logging.getLogger(__name__)


class RPCError(RuntimeError):
    pass


class RPCHandlerFailed(RPCError):
    pass


class RPCUnhandledRequest(RPCError):
    pass


class RPCRequest(object):

    def __init__(self, server, client_id, message):
        self.server = server
        self.client_id = client_id
        self.message = message
        self.replied = False

    def reply(self, payload=None, status_code=200):
        self.server.send_message(
            reply_to=self.message.id, status_code=status_code, payload=payload)
        self.replied = True


def rpc(uri):
    def decorator(func):
        LOG.info('Registered handler for %s', uri)
        func.is_rpc = True
        func.uri = uri
        return func
    return decorator


class RPCServiceBase(object):

    MAX_REQUEST_SIZE = 1042
    # meta attribute
    # RPC_HANDLERS

    def can_handle(self, uri):
        return uri in self.RPC_HANDLERS

    def handle_request_from_client(self, request):
        handler = self.RPC_HANDLERS.get(request.message.uri)
        if handler:
            try:
                LOG.debug(
                    'Handling request from client %d to %s', request.client_id,
                    request.message.uri)
                return handler(request)
            except:
                LOG.error(
                    'Failed to handle request from %d to %s',
                    request.client_id, request.message.uri)
                raise RPCHandlerFailed(request.message.uri)
        else:
            LOG.warn('No route for %s', request.message.uri)
            raise RPCUnhandledRequest(request.message.uri)


class RPCServiceMeta(type):

    def __new__(cls, name, bases, attrs):
        rpc_handlers = {}
        for attrname, attrvalue in attrs.iteritems():
            is_rpc = getattr(attrvalue, 'is_rpc', False)
            if is_rpc:
                uri = getattr(attrvalue, 'uri', '')
                if uri:
                    rpc_handlers[uri] = attrvalue
                else:
                    LOG.warn('No URI defined for rpc %s', attrname)
        attrs['RPC_HANDLERS'] = rpc_handlers
        return super(RPCServiceMeta, cls).__new__(cls, name, bases, attrs)


class RPCService(RPCServiceBase):

    __metaclass__ = RPCServiceMeta


class RPCServer(network.Server):

    def __init__(self, *args, **kwargs):
        super(RPCServer, self).__init__(*args, **kwargs)
        self.services = []

    def add_service(self, service):
        self.services.append(service)

    def remove_service(self, service):
        self.services.remove(service)

    def on_client_disconnected(self, client_id):
        LOG.info('Client %d disconnected', client_id)

    def on_received_message_from_client(self, client_id, message):
        request = RPCRequest(self, client_id, message)
        for service in self.services:
            if service.can_handle(message.uri):
                try:
                    reply = service.handle_message_from_client(request)
                    if not request.replied:
                        request.reply(status_code=200, payload=reply)
                except RPCHandlerFailed:
                    LOG.exception(
                        'RPC call failed from client %d to %s', client_id,
                        message.uri)
                    request.reply(status_code=500)
                except RPCUnhandledRequest:
                    LOG.exception(
                        'RPC call not found from client %d to %s', client_id,
                        message.uri)
                    request.reply(status_code=404)
                return
        LOG.warn(
            'Unhandled message from client %d to %s', client_id, message.uri)
        request.reply(status_code=404)
