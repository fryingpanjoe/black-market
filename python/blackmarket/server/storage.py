from logging import getLogger
import sqlite3

LOG = getLogger(__name__)


class Store(object):
    def __init__(self, name):
        self.name = name

    def connect(self, *args):
        self.conn = sqlite3.connect(self.name, *args)

    def disconnect(self):
        self.conn.close()

    def new_cursor(self):
        return self.conn.cursor()


class PlayerStore(object):
    def __init__(self, store):
        self.store = store

    def create_tables(self):
        cursor = self.store.new_cursor()
        cursor.execute('''
            CREATE TABLE bm_galaxy (
                    galaxy_id           INTEGER PRIMARY KEY
                ,   galaxy_name         TEXT
                ,   galaxy_pos_x        REAL
                ,   galaxy_pos_y        REAL
                ,   galaxy_properties   TEXT
                )
            ''')
        cursor.execute('''
            CREATE TABLE bm_system (
                    system_id           INTEGER PRIMARY KEY
                ,   system_name         TEXT
                ,   system_pos_x        REAL
                ,   system_pos_y        REAL
                ,   system_properties   TEXT
                ,   system_galaxy_id    INTEGER
                ,   FOREIGN KEY(system_galaxy_id) REFERENCES bm_galaxy(galaxy_id)
                )
            ''')
        cursor.execute('''
            CREATE TABLE bm_planet (
                    planet_id           INTEGER PRIMARY KEY
                ,   planet_name         TEXT
                ,   planet_radius       REAL
                ,   planet_distance_x   REAL
                ,   planet_distance_y   REAL
                ,   planet_properties   TEXT
                ,   planet_system_id    INTEGER
                ,   FOREIGN KEY(planet_system_id) REFERENCES bm_system(system_id)
                )
            ''')
        cursor.execute('''
            create table bm_resource (
                    resource_id         INTEGER PRIMARY KEY
                ,   resource_type       INTEGER
                ,   resource_amount     REAL
                ,   resource_properties TEXT
                ,   resource_planet_id  INTEGER
                ,   FOREIGN KEY(resource_planet_id) REFERENCES bm_planet(planet_id)
                )
            ''')
        cursor.execute('''
            create table bm_service (
                    service_id          INTEGER PRIMARY KEY
                ,   service_type        INTEGER
                ,   service_amount      REAL
                ,   service_properties  TEXT
                ,   service_planet_id   INTEGER
                ,   FOREIGN KEY(service_planet_id) REFERENCES bm_planet(planet_id)
                )
            ''')


class WorldStore(object):
    def __init__(self, store):
        self.store = store

    def create_tables(self):
        cursor = self.store.new_cursor()
        cursor.execute('''
            CREATE TABLE bm_galaxy (
                    galaxy_id           INTEGER PRIMARY KEY
                ,   galaxy_name         TEXT
                ,   galaxy_pos_x        REAL
                ,   galaxy_pos_y        REAL
                ,   galaxy_properties   TEXT
                )
            ''')
        cursor.execute('''
            CREATE TABLE bm_system (
                    system_id           INTEGER PRIMARY KEY
                ,   system_name         TEXT
                ,   system_pos_x        REAL
                ,   system_pos_y        REAL
                ,   system_properties   TEXT
                ,   system_galaxy_id    INTEGER
                ,   FOREIGN KEY(system_galaxy_id) REFERENCES bm_galaxy(galaxy_id)
                )
            ''')
        cursor.execute('''
            CREATE TABLE bm_planet (
                    planet_id           INTEGER PRIMARY KEY
                ,   planet_name         TEXT
                ,   planet_radius       REAL
                ,   planet_distance_x   REAL
                ,   planet_distance_y   REAL
                ,   planet_properties   TEXT
                ,   planet_system_id    INTEGER
                ,   FOREIGN KEY(planet_system_id) REFERENCES bm_system(system_id)
                )
            ''')
        cursor.execute('''
            create table bm_resource (
                    resource_id         INTEGER PRIMARY KEY
                ,   resource_type       INTEGER
                ,   resource_amount     REAL
                ,   resource_properties TEXT
                ,   resource_planet_id  INTEGER
                ,   FOREIGN KEY(resource_planet_id) REFERENCES bm_planet(planet_id)
                )
            ''')
        cursor.execute('''
            create table bm_service (
                    service_id          INTEGER PRIMARY KEY
                ,   service_type        INTEGER
                ,   service_amount      REAL
                ,   service_properties  TEXT
                ,   service_planet_id   INTEGER
                ,   FOREIGN KEY(service_planet_id) REFERENCES bm_planet(planet_id)
                )
            ''')


class WorldStore(object):
    def __init__(self, store):
        self.store = store

    def create_tables(self):
        cursor = self.store.new_cursor()
        cursor.execute('''
            CREATE TABLE bm_galaxy (
                    galaxy_id           INTEGER PRIMARY KEY
                ,   galaxy_name         TEXT
                ,   galaxy_pos_x        REAL
                ,   galaxy_pos_y        REAL
                ,   galaxy_properties   TEXT
                )
            ''')
        cursor.execute('''
            CREATE TABLE bm_system (
                    system_id           INTEGER PRIMARY KEY
                ,   system_name         TEXT
                ,   system_pos_x        REAL
                ,   system_pos_y        REAL
                ,   system_properties   TEXT
                ,   system_galaxy_id    INTEGER
                ,   FOREIGN KEY(system_galaxy_id) REFERENCES bm_galaxy(galaxy_id)
                )
            ''')
        cursor.execute('''
            CREATE TABLE bm_planet (
                    planet_id           INTEGER PRIMARY KEY
                ,   planet_name         TEXT
                ,   planet_radius       REAL
                ,   planet_distance_x   REAL
                ,   planet_distance_y   REAL
                ,   planet_properties   TEXT
                ,   planet_system_id    INTEGER
                ,   FOREIGN KEY(planet_system_id) REFERENCES bm_system(system_id)
                )
            ''')
        cursor.execute('''
            create table bm_resource (
                    resource_id         INTEGER PRIMARY KEY
                ,   resource_type       INTEGER
                ,   resource_amount     REAL
                ,   resource_properties TEXT
                ,   resource_planet_id  INTEGER
                ,   FOREIGN KEY(resource_planet_id) REFERENCES bm_planet(planet_id)
                )
            ''')
        cursor.execute('''
            create table bm_service (
                    service_id          INTEGER PRIMARY KEY
                ,   service_type        INTEGER
                ,   service_amount      REAL
                ,   service_properties  TEXT
                ,   service_planet_id   INTEGER
                ,   FOREIGN KEY(service_planet_id) REFERENCES bm_planet(planet_id)
                )
            ''')


class UserStore(object):
    def __init__(self, store):
        self.store = store

    def create_tables(self):
        cursor = self.store.new_cursor()
        cursor.execute('''
            CREATE TABLE bm_user (
                    user_id             INTEGER PRIMARY KEY
                ,   user_first_name     TEXT
                ,   user_last_name      TEXT
                ,   user_email          TEXT
                ,   user_password       TEXT
                ,   user_properties     TEXT
                )
            ''')
