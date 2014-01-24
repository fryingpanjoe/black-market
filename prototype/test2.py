import logging.config
import rpc

# setup logging immediately
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)


@rpc.rpc
def add(a, b):
    return a + b


@rpc.rpc
def sub(a, b):
    return a - b


def main():
    try:
        rpc.start_server('localhost', 8000, background=False)
    finally:
        rpc.stop_server()


if __name__ == '__main__':
    main()
