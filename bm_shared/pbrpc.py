import socket
import threading
import inspect
import logging
import functools
import SocketServer

LOG = logging.getLogger(__name__)


class RPCError(RuntimeError):
    pass


class RPCService(object):



class RPCDemux(SocketServer.BaseRequestHandler):

    def handle(self):
        global RPC_HANDLERS

        try:
            # read request call data
            request_data = self.request.recv(MAX_REQUEST_SIZE)

            # parse request
            call = json.loads(request_data)

            # handle request
            result = self.invoke_handler(
                RPC_HANDLERS[call['name']], call['args'])

            # build response
            response = {'status': 'ok'}
            if result:
                response['result'] = result
        except Exception, exc:
            # something went wrong
            LOG.exception('rpc failed')
            response = {'status': 'failed', 'reason': str(exc)}
        finally:
            # send response
            self.request.sendall(json.dumps(response))

    @staticmethod
    def invoke_handler(handler, args):
        # build function call arguments
        kwargs = handler.kwargs.copy()
        for arg, value in args.iteritems():
            # make sure args exists
            if arg not in handler.args:
                raise RPCError('invalid arg "{}"'.format(arg))
            kwargs[arg] = value

        # check missing args
        for arg in handler.args:
            if arg not in kwargs:
                raise RPCError('missing arg "{}"'.format(arg))

        # handle request
        LOG.debug('calling %s with %r', handler.name, kwargs)
        return handler.func(**kwargs)


class RPCService(SocketServer.BaseRequestHandler):

    MAX_REQUEST_SIZE = 1024
    RPC_HANDLERS = {}

    def expose(func):
        handler = RPCHandler.from_func(func)
        LOG.info('registered RPC %s', handler.name)
        RPC_HANDLERS[handler.name] = handler

    def handle(self):
        try:
            # read request call data
            request_data = self.request.recv(MAX_REQUEST_SIZE)

            # parse request
            call = json.loads(request_data)

            # handle request
            result = self.invoke_handler(
                RPC_HANDLERS[call['name']], call['args'])

            # build response
            response = {'status': 'ok'}
            if result:
                response['result'] = result
        except Exception, exc:
            # something went wrong
            LOG.exception('rpc failed')
            response = {'status': 'failed', 'reason': str(exc)}
        finally:
            # send response
            self.request.sendall(json.dumps(response))

    @staticmethod
    def invoke_handler(handler, args):
        # build function call arguments
        kwargs = handler.kwargs.copy()
        for arg, value in args.iteritems():
            # make sure args exists
            if arg not in handler.args:
                raise RPCError('invalid arg "{}"'.format(arg))
            kwargs[arg] = value

        # check missing args
        for arg in handler.args:
            if arg not in kwargs:
                raise RPCError('missing arg "{}"'.format(arg))

        # handle request
        LOG.debug('calling %s with %r', handler.name, kwargs)
        return handler.func(**kwargs)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class RPCServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def start(self, host, port, background=True):
        LOG.info('starting server on %s:%d', host, port)
        SERVER = ThreadedTCPServer((host, port), RPCDemux)
        if background:
            server_thread = threading.Thread(target=SERVER.serve_forever)
            # run as a daemon, exit when main thread
            server_thread.daemon = True
            server_thread.start()
            LOG.info('running server in thread %s', server_thread.name)
        else:
            LOG.info('running server in main thread')
            SERVER.serve_forever()


# shared server implementation
SERVER = None


def start_server(host, port, background=True):
    global SERVER

    LOG.info('starting server on %s:%d', host, port)
    SERVER = ThreadedTCPServer((host, port), RPCDemux)

    if background:
        server_thread = threading.Thread(target=SERVER.serve_forever)
        # run as a daemon, exit when main thread
        server_thread.daemon = True
        server_thread.start()
        LOG.info('running server in thread %s', server_thread.name)
    else:
        LOG.info('running server in main thread')
        SERVER.serve_forever()


def stop_server():
    global SERVER

    if SERVER:
        SERVER.shutdown()
        LOG.info('server stopped')
    else:
        LOG.info('server not running')
