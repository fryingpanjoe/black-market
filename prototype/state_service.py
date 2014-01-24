import sqlite3
import rpc

CONFIG_FILENAME = 'state-service-conf.json'


@rpc.rpc
def update_player_pos():
    pass


def main():
    config = {}
    with open(CONFIG_FILENAME) as config_file:
        config = json.load(config_file)

    conn = sqlite3.connect(config['database-filename'])

    try:
        rpc.start_server()
    finally:
        rpc.stop_server()
        conn.close()

if __name__ == '__main__':
    main()
