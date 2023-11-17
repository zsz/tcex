import pytest

from app import database

config = {
    database.HOST: "localhost",
    database.USER: "joeavg",
    database.PASSWORD: "****",
    database.DATABASE: "valuabledata",
    database.UNIX_SOCKET: "/var/run/mysqld/mysqld.sock"
}


@pytest.mark.parametrize(argnames=["config"], argvalues=[[config]])
def test_datasource_config(config):
    datasource = database.DataSource(config)
    assert datasource.get_host() == config[database.HOST]
    assert datasource.get_user() == config[database.USER]
    assert datasource.get_password() == config[database.PASSWORD]
    assert datasource.get_database() == config[database.DATABASE]
    assert datasource.get_unix_socket() == config[database.UNIX_SOCKET]
