import logging
import socket
import select
import struct
import zlib

LOG = logging.getLogger(__name__)


DEFAULT_COMPRESSION_LEVEL = 1


def compress_data(data, compression_level=DEFAULT_COMPRESSION_LEVEL):
    return zlib.compress(data, compression_level)


def decompress_data(data):
    return zlib.decompress(data)


class CompressionMethod(object):

    NONE = 0
    ZLIB = 1


class PacketType(object):

    DATA = 1
    MULTI_DATA = 2
    HEARTBEAT = 3


class WireProtocolError(RuntimeError):
    pass


class BufferOverflow(WireProtocolError):
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

    def can_write_string(self, data):
        return self.can_write(2 + len(data))

    def ensure_can_write(self, length=1):
        if not self.can_write(length):
            raise BufferOverflow('Buffer overflow: %d bytes' % (length,))

    def write_raw(self, data):
        self.ensure_can_write(len(data))
        self.buffer += data

    def write_string(self, data):
        self.ensure_can_write(2 + len(data))
        self.write_uint16(len(data))
        self.write_raw(data)

    def write_int8(self, data):
        self.write_raw(struct.pack('!b', data))

    def write_uint8(self, data):
        self.write_raw(struct.pack('!B', data))

    def write_int16(self, data):
        self.write_raw(struct.pack('!h', data))

    def write_uint16(self, data):
        self.write_raw(struct.pack('!H', data))

    def write_int32(self, data):
        self.write_raw(struct.pack('!i', data))

    def write_uint32(self, data):
        self.write_raw(struct.pack('!I', data))

    def write_float(self, data):
        self.write_raw(struct.pack('!f', data))


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

    def read_int8(self):
        data = self.read_raw(1)
        if data:
            data = struct.unpack('!b', data)[0]
        return data

    def read_uint8(self):
        data = self.read_raw(1)
        if data:
            data = struct.unpack('!B', data)[0]
        return data

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


def serialize_packet(max_packet_size, packet_type, packet_id, recv_packet_id,
                     payload='', compress=False):
    write_buffer = WriteBuffer(max_packet_size)
    write_buffer.write_uint8(packet_type)
    write_buffer.write_uint16(packet_id)
    write_buffer.write_uint16(recv_packet_id)
    if compress:
        compressed_payload = compress_data(payload)
        #LOG.debug(
        #    'Compression %d -> %d bytes, compression factor %f',
        #    len(payload), len(compressed_payload),
        #    float(len(compressed_payload)) / len(payload))
        write_buffer.write_uint8(CompressionMethod.ZLIB)
        write_buffer.write_string(compressed_payload)
    else:
        write_buffer.write_uint8(CompressionMethod.NONE)
        write_buffer.write_string(payload)
    return write_buffer.get_buffer_data()


def deserialize_packet(packet_data):
    read_buffer = ReadBuffer(packet_data)
    packet_type = read_buffer.read_uint8()
    packet_id = read_buffer.read_uint16()
    recv_packet_id = read_buffer.read_uint16()
    compression_method = read_buffer.read_uint8()
    payload = read_buffer.read_string()

    if compression_method == CompressionMethod.NONE:
        # no decompress
        pass
    elif compression_method == CompressionMethod.ZLIB:
        payload = decompress_data(payload)
    else:
        raise WireProtocolError(
            'Bad compression method %d' % (compression_method,))

    if packet_type == PacketType.DATA:
        payloads = [payload]
    elif packet_type == PacketType.MULTI_DATA:
        payloads = []
        multi_reader = ReadBuffer(payload)
        while multi_reader.can_read():
            payloads.append(multi_reader.read_string())
    elif packet_type == PacketType.HEARTBEAT:
        payloads = []
    else:
        raise WireProtocolError('Bad packet type %d' % (packet_type,))

    return (packet_id, recv_packet_id, payloads)


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

    def _write_packet(self, packet_type, packet_id, recv_packet_id, payload='',
                      compress=False):
        packet = serialize_packet(
            self.MAX_PACKET_SIZE,
            packet_type,
            packet_id,
            recv_packet_id,
            payload=payload,
            compress=compress)
        #LOG.debug('Sending %d packet bytes', len(packet))
        self.write_buffer.write_string(packet)

    def _prepare_next_packet(self):
        self.send_packet_id = (self.send_packet_id + 1) % self.MAX_PACKET_ID

    def _write_and_prepare_next_packet(self, packet_type, payload='',
                                       compress=False):
        self._write_packet(
            self.MAX_PACKET_SIZE,
            packet_type,
            self.send_packet_id,
            self.recv_packet_id,
            payload=payload,
            compress=compress)
        self._prepare_next_packet()

    def send_heartbeat(self):
        self._write_and_prepare_next_packet(PacketType.HEARTBEAT)

    def send_data(self, payload, compress=False):
        self._write_and_prepare_next_packet(
            PacketType.DATA,
            payload=payload,
            compress=compress)

    def send_multi_data(self, payloads, compress=False):
        writer = WriteBuffer(self.MAX_PACKET_SIZE)
        for payload in payloads:
            try:
                writer.write_string(payload)
            except BufferOverflow:
                self._write_and_prepare_next_packet(
                    PacketType.MULTI_DATA,
                    payload=writer.get_buffer_data(),
                    compress=compress)
                self._prepare_next_packet()
                writer = WriteBuffer(self.MAX_PACKET_SIZE)
                writer.write_string(payload)
            except:
                raise
            if not writer.write_string(payload):
                if len(payload) > self.MAX_PACKET_SIZE:
                    # payload will never fit in packet
                    raise WireProtocolError(
                        'Payload too big: %d bytes' % (len(payload),))
                else:

        packet_sent = self._write_packet(
            PacketType.DATA,
            self.send_packet_id,
            self.recv_packet_id,
            packet_data,
            compress=compress)
        if packet_sent:
            self._prepare_next_packet()
        return packet_sent

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
