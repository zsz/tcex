import logging
from copy import copy
from typing import Any

from MySQLdb import Connection
from MySQLdb import MySQLError
from MySQLdb import connect

HOST = "TCEX_HOSTNAME"
USER = "TCEX_USERNAME"
PASSWORD = "TCEX_PASSWORD"
DATABASE = "TCEX_DATABASE"
UNIX_SOCKET = "TCEX_UXSOCKET"


class DataSource:
    def __init__(self, config):
        self.config = copy(config)

    def get_host(self) -> str:
        return self.config[HOST]

    def get_user(self) -> str:
        return self.config[USER]

    def get_password(self) -> str:
        return self.config[PASSWORD]

    def get_database(self) -> str:
        return self.config[DATABASE]

    def get_unix_socket(self) -> str:
        return self.config[UNIX_SOCKET]
    
    def get_connection(self) -> Connection:
        return connect(
            host=self.get_host(),
            user=self.get_user(),
            password=self.get_password(),
            database=self.get_database(),
            unix_socket=self.get_unix_socket()
        )


FETCH_TABLE_NAMES_SQL_TEMPLATE = """SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = %(table_schema)s
"""


def get_table_names(data_source: DataSource, schema: str) -> list[str]:
    """
    Loads the database table names of the given schema. The database connection is specified by the
    provided datasource.
    :param data_source: the datasource to connect the DB
    :param schema: the scheme name
    :return: a list of table names
    """

    connection = None
    try:
        connection = data_source.get_connection()

        cursor = connection.cursor()
        cursor.execute(FETCH_TABLE_NAMES_SQL_TEMPLATE, dict(table_schema=schema))
        return next(zip(*cursor.fetchall()))
    except MySQLError as err:
        logging.error("Unable to fetch table names: %s", err.__str__())
        return []
    finally:
        if connection:
            connection.close()


FETCH_TABLE_CONTENT_SQL_TEMPLATE = """SELECT * 
FROM {table_name}
"""

"""
Representation of a database dump. Keys are the table names and their 
associated value as a pair of column names as tuple and the corresponding records as tuples.
"""
db_dump = dict[str, tuple[tuple[..., str], tuple[..., Any]]]


def get_tables_content(data_source: DataSource, table_names: list[str]) -> db_dump:
    """
    Gets the database table content (select all) with some metadata like column names.
    :param data_source: the datasource to connect the DB
    :param table_names: the name of the database tables which content to be returned
    :return: a database dump
    """

    connection = None
    try:
        connection = data_source.get_connection()
        cursor = connection.cursor()
        table_desc_and_data = {}
        for table_name in table_names:
            cursor.execute(FETCH_TABLE_CONTENT_SQL_TEMPLATE.format(**dict(table_name=table_name)))
            columns = next(zip(*cursor.description))
            data = cursor.fetchall()
            table_desc_and_data[table_name] = (columns, data)
        return table_desc_and_data
    except MySQLError as err:
        logging.error("Unable to fetch table content: %s", err.__str__())
        return {}
    finally:
        if connection:
            connection.close()
