if __name__ == '__main__':
    import json
    import argparse
    import logging.config
    from .server import run_server

    parser = argparse.ArgumentParser(description='stream logger server')
    parser.add_argument('-c', '--config', type=str, nargs='1', required=True, help='Config file path')
    parser.add_argument('-h', '--host', type=str, nargs='1', required=True, help='Connect to host.')
    parser.add_argument('-p', '--port', type=int, nargs='1', help='Port number.')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)
    logging.config.dictConfig(config)
    server_address = args.host if args.port is None else (args.host, args.port)
    run_server(server_address)
