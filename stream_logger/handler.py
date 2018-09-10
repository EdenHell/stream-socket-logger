from logging.handlers import SocketHandler
import struct


class StreamHandler(SocketHandler):

    def __init__(self, host, port=None, *, producer=None):
        """
        Initializes the handler with a specific host address and port.

        When the attribute *closeOnError* is set to True - if a socket error
        occurs, the socket is silently closed and then reopened on the next
        logging call.
        """
        super().__init__(host, port)
        self.producer = producer or __package__.split('.')[0]

    def serialization(self, record):
        producer = self.producer.encode()
        text = self.format(record).encode()
        return struct.pack('!B', len(producer)) + producer + struct.pack('!L', len(text)) + text

    def emit(self, record):
        """
        Emit a record.
        Serialize the record and writes it to the socket in binary format.
        If there is an error with the socket, silently drop the packet.
        If there was a problem with the socket, re-establishes the
        socket.
        """
        # noinspection PyBroadException
        try:
            self.send(self.serialization(record))
        except Exception:
            self.handleError(record)
