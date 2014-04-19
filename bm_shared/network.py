import logging
import socket
import select
import struct
import zlib

LOG = logging.getLogger(__name__)

COMPRESSION_LEVEL = 1


def compress_data(data):
    return zlib.compress(data, COMPRESSION_LEVEL)


def decompress_data(data):
    return zlib.decompress(data)


class WireProtocolError(RuntimeError):
    pass


class WriteBuffer(object):

    def __init__(self, max_size=None):
        self.buffer = ''
        self.max_size = max_size

    def get_buffer_data(self):
        return self.buffer

    def get_buffer_size(self):
        return len(self.buffer)

    def is_empty(self):
        return len(self.buffer) == 0

    def can_write(self, length=1):
        return (self.max_size is None or
                self.max_size >= len(self.buffer) + length)

    def write_raw(self, data):
        if self.can_write(len(data)):
            self.buffer += data
            return True
        else:
            return False

    def write_string(self, data):
        return (self.can_write(2 + len(data)) and
                self.write_uint16(len(data)) and
                self.write_raw(data))

    def write_int16(self, data):
        return self.can_write(2) and self.write_raw(struct.pack('!h', data))

    def write_uint16(self, data):
        return self.can_write(2) and self.write_raw(struct.pack('!H', data))

    def write_int32(self, data):
        return self.can_write(4) and self.write_raw(struct.pack('!i', data))

    def write_uint32(self, data):
        return self.can_write(4) and self.write_raw(struct.pack('!I', data))

    def write_float(self, data):
        return self.can_write(4) and self.write_raw(struct.pack('!f', data))


class ReadBuffer(object):

    def __init__(self, buf=None):
        if buf:
            self.buffer = buf
        else:
            self.buffer = ''

    def get_buffer_data(self):
        return self.buffer

    def get_buffer_size(self):
        return len(self.buffer)

    def feed(self, data):
        self.buffer += data

    def peek(self, length):
        if self.can_read(length):
            return self.buffer[:length]
        else:
            return None

    def can_read(self, length=1):
        return len(self.buffer) >= length

    def skip(self, length):
        if self.can_read(length):
            self.buffer = self.buffer[length:]

    def read_raw(self, length):
        if self.can_read(length):
            data = self.buffer[:length]
            self.buffer = self.buffer[length:]
            return data
        else:
            return None

    def read_string(self):
        if not self.can_read(2):
            return None
        length = struct.unpack('!H', self.peek(2))[0]
        if self.can_read(2 + length):
            self.skip(2)
            return self.read_raw(length)
        else:
            return None

    def read_int16(self):
        data = self.read_raw(2)
        if data:
            data = struct.unpack('!h', data)[0]
        return data

    def read_uint16(self):
        data = self.read_raw(2)
        if data:
            data = struct.unpack('!H', data)[0]
        return data

    def read_int32(self):
        data = self.read_raw(4)
        if data:
            data = struct.unpack('!i', data)[0]
        return data

    def read_uint32(self):
        data = self.read_raw(2)
        if data:
            data = struct.unpack('!I', data)[0]
        return data


class Channel(object):

    MAX_PACKET_ID = 256
    MAX_PACKET_SIZE = 8192
    MAX_RECEIVE_SIZE = 8192

    def __init__(self, sock):
        self.sock = sock

        # in- and outbound buffers
        self.write_buffer = WriteBuffer()
        self.read_buffer = ReadBuffer()

        # keep track of last sent packet id
        self.send_packet_id = 1

        # keep track of last received packet id
        self.recv_packet_id = None

        # in- and outbound queues
        self.inbox = []
        self.outbox = []

    def write_packet(self, packet_data):
        compressed_packet_data = compress_data(packet_data)
        #LOG.debug(
        #    'Compression %d -> %d bytes, compression factor %f',
        #    len(packet_data), len(compressed_packet_data),
        #    float(len(compressed_packet_data)) / len(packet_data))
        self.write_buffer.write_int32(self.send_packet_id)
        self.write_buffer.write_string(compressed_packet_data)
        self.send_packet_id = (self.send_packet_id + 1) % self.MAX_PACKET_ID

    def write_messages(self):
        writer = WriteBuffer(self.MAX_PACKET_SIZE)
        for message in self.outbox:
            serialized_message = message.SerializeToString()
            if not writer.write_string(serialized_message):
                if len(serialized_message) > self.MAX_PACKET_SIZE:
                    # message will never fit in a packet
                    raise WireProtocolError(
                        'Message size %d too big' % (len(serialized_message),))
                else:
                    # write packet and continue with the next message
                    self.write_packet(writer.get_buffer_data())
                    writer = WriteBuffer(self.MAX_PACKET_SIZE)
                    if not writer.write_string(serialized_message):
                        raise WireProtocolError('Failed to write message')
        # write remaining data
        if not writer.is_empty():
            self.write_packet(writer.get_buffer_data())
        # no outbound messages left
        self.outbox = []

    def send_data(self):
        try:
            # serialize and send all outbound messages
            if self.outbox:
                self.write_messages()
            # check if we have anything to send, and try to send it
            if not self.write_buffer.is_empty():
                # check if the socket is writable
                _, writable, _ = select.select([], [self.sock], [], 0)
                if writable:
                    bytes_sent = self.sock.send(
                        self.write_buffer.get_buffer_data())
                    if bytes_sent == 0:
                        # failed to send - probably disconnected
                        return False
                    self.write_buffer.skip(bytes_sent)
            return True
        except socket.error:
            LOG.exception('Socket error')
            return False

    def on_packet_received(self, packet_data):
        reader = ReadBuffer(packet_data)
        while reader.can_read():
            message = reader.read_string()
            if message:
                envelope = MessageEnvelope()
                envelope.ParseFromString(message)
                self.inbox.append(envelope)
            else:
                break
        if reader.can_read():
            LOG.warning(
                '%d bytes of unparsed packet data' %
                (reader.get_buffer_size(),))
        # ready for next packet
        self.recv_packet_id = None

    def on_data_received(self):
        if self.recv_packet_id:
            packet_data = self.read_buffer.read_string()
            if packet_data:
                self.on_packet_received(decompress_data(packet_data))
        else:
            self.recv_packet_id = self.read_buffer.read_int32()

    def receive_data(self):
        try:
            # check if there's anything on the socket
            readable, _, _ = select.select([self.sock], [], [], 0)
            if readable:
                data = self.sock.recv(self.MAX_RECEIVE_SIZE)
                if data:
                    self.read_buffer.feed(data)
                    self.on_data_received()
                else:
                    # client disconnected
                    return False
            return True
        except socket.error:
            LOG.exception('Socket error')
            return False

    def synchronize(self):
        return self.send_data() and self.receive_data()

    def send_message(self, uri=None, reply_to=None, payload=None,
                     status_code=None):
        envelope = MessageEnvelope()
        if uri:
            envelope.uri = uri
        if reply_to:
            envelope.reply_to = reply_to
        if payload:
            envelope.payload = payload
        if status_code:
            envelope.status_code = status_code
        self.outbox.append(envelope)

    def receive_messages(self):
        while self.inbox:
            yield self.inbox.pop()


class Client(object):

    def __init__(self):
        self.server_socket = None
        self.channel = None

    def is_connected(self):
        return self.server_socket

    def connect(self, address, port):
        LOG.info('Connecting to server %s:%d', address, port)
        self.server_socket = socket.create_connection((address, port))
        if self.server_socket:
            self.channel = Channel(self.server_socket)
            return True
        else:
            LOG.info('Failed to connect to server %s:%d', address, port)
            return False

    def disconnect(self):
        LOG.info('Disconnecting from server')
        self.server_socket.close()
        self.server_socket = None
        self.channel = None

    def send_message(self, uri=None, reply_to=None, payload=None,
                     status_code=None):
        self.channel.send_message(
            uri=uri, reply_to=reply_to, payload=payload,
            status_code=status_code)

    def read_from_server(self):
        if self.channel.receive_data():
            for message in self.channel.receive_messages():
                self.on_received_message_from_server(message)
        else:
            LOG.info('Server closed the connection')
            self.disconnect()
            self.on_disconnected_from_server()

    def write_to_server(self):
        if not self.channel.send_data():
            LOG.info('Broken socket, disconnecting')
            self.disconnect()
            self.on_disconnected_from_server()

    def on_received_message_from_server(self, message):
        raise NotImplementedError

    def on_disconnected_from_server(self):
        raise NotImplementedError


class Server(object):

    def __init__(self):
        self.server_socket = None
        self.client_sockets = []
        self.channels = {}

    def start_server(self, port, address='', backlog=10):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((address, port))
        self.server_socket.listen(backlog)

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None

    def accept_pending_clients(self):
        readable, _, _ = select.select([self.server_socket], [], [], 0)
        if readable:
            client_socket, address = self.server_socket.accept()
            self.client_sockets.append(client_socket)
            client_id = client_socket.fileno()
            self.channels[client_id] = Channel(client_socket)
            self.on_client_disconnected(client_id)
            LOG.info('Client %d connected', client_id)

    def broadcast_message(self, uri=None, reply_to=None, payload=None,
                          status_code=None):
        for channel in self.channels.itervalues():
            channel.send_message(
                uri=uri, reply_to=reply_to, payload=payload,
                status_code=status_code)

    def send_message(self, client_id, uri=None, reply_to=None, payload=None,
                     status_code=None):
        self.channels[client_id].send_message(
            uri=uri, reply_to=reply_to, payload=payload,
            status_code=status_code)

    def read_from_clients(self):
        readable, _, _ = select.select(self.client_sockets, [], [], 0)
        for sock in readable:
            client_id = sock.fileno()
            channel = self.channels[client_id]
            if channel.receive_data():
                for message in channel.receive_messages():
                    self.on_received_message_from_client(client_id, message)
            else:
                LOG.info('Client %d disconnected', client_id)
                self.client_sockets.remove(sock)
                del self.channels[client_id]
                self.on_client_disconnected(client_id)

    def write_to_clients(self):
        _, writable, _ = select.select([], self.client_sockets, [], 0)
        for sock in writable:
            client_id = sock.fileno()
            if not self.channels[client_id].send_data():
                LOG.info(
                    'Broken socket to client %d, disconnecting', client_id)
                self.client_sockets.remove(sock)
                del self.channels[client_id]
                self.on_client_disconnected(client_id)

    def on_client_disconnected(self, client_id):
        raise NotImplementedError

    def on_received_message_from_client(self, client_id, message):
        raise NotImplementedError
