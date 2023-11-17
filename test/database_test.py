import os

import pytest

from app import database

config = {
    database.HOST: "localhost",
    database.USER: "joeavg",
    database.PASSWORD: "****",
    database.DATABASE: "valuabledata",
    database.UNIX_SOCKET: "/var/run/mysqld/mysqld.sock"
}


@pytest.fixture(params=[config])
def mock_env_vars(request, monkeypatch):
    print(request.param)
    for key, val in request.param.items():
        monkeypatch.setenv(key, val)


@pytest.mark.parametrize(argnames=["config"], argvalues=[[config]])
def test_datasource_init_from_env_vars(mock_env_vars, config):
    datasource = database.DataSource(config)
    assert datasource.get_host() == os.getenv(database.HOST)
    assert datasource.get_user() == os.getenv(database.USER)
    assert datasource.get_password() == os.getenv(database.PASSWORD)
    assert datasource.get_database() == os.getenv(database.DATABASE)
    assert datasource.get_unix_socket() == os.getenv(database.UNIX_SOCKET)