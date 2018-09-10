import os
import logging
import struct
import errno
from socketserver import StreamRequestHandler
from socketserver import ThreadingTCPServer, ThreadingUnixStreamServer

request_queue_size = 30


class LogRecordStreamHandler(StreamRequestHandler):
    """Handler for a streaming logging request.

    This basically logs the record using whatever logging policy is
    configured locally.
    """

    def handle(self):
        while True:
            producer = self.receive_one(1, '!B')
            if producer is None:
                break
            text = self.receive_one(4, '!L')
            if text is None:
                break
            logger = logging.getLogger(producer.decode())
            logger.info(text.decode())

    def receive_one(self, size, fmt):
        chunk = self.connection.recv(size)
        if len(chunk) < size:
            return
        slen = struct.unpack(fmt, chunk)[0]
        chunk = self.connection.recv(slen)
        while len(chunk) < slen:
            chunk = chunk + self.connection.recv(slen - len(chunk))
        return chunk


def run_server(server_address):
    if type(server_address) is str:
        try:
            os.makedirs(os.path.dirname(server_address))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        try:
            os.remove(server_address)
        except OSError as e:
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise
        server = ThreadingUnixStreamServer(server_address, LogRecordStreamHandler, False)
    else:
        server = ThreadingTCPServer(server_address, LogRecordStreamHandler, False)
    with server:
        server.request_queue_size = request_queue_size
        # server.socket.settimeout(0)
        try:
            server.server_bind()
            server.server_activate()
        except Exception:
            server.server_close()
            raise
        server.serve_forever(0.1)


if __name__ == '__main__':
    import json
    import argparse
    import logging.config

    parser = argparse.ArgumentParser(description='stream logger server')
    parser.add_argument('host', type=str, help='Connect to host.')
    parser.add_argument('-p', '--port', type=int, help='Port number.')
    parser.add_argument('-c', '--config', type=str, help='Config file path')
    args = parser.parse_args()
    if args.config is not None:
        with open(args.config) as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    run_server(args.host if args.port is None else (args.host, args.port))
