# pylint: disable=redefined-outer-name
"""Tests for microservice"""
from unittest.mock import patch
import pytest
from falcon import testing
import service.microservice

CLIENT_HEADERS = {
    'ACCESS_KEY': '1234567'
}

FTP_HEADERS = {
    'X-SFTP-HOST':'localhost',
    'X-SFTP-HOST-KEY':'abcd',
    'X-SFTP-USER':'user',
    'X-SFTP-PASSWORD':'1234',
}

@pytest.fixture()
def client():
    """ client fixture """
    return testing.TestClient(app=service.microservice.start_service(), headers=CLIENT_HEADERS)

@pytest.fixture
def mock_env_access_key(monkeypatch):
    """ mock environment access key """
    monkeypatch.setenv("ACCESS_KEY", CLIENT_HEADERS["ACCESS_KEY"])

def test_post_missing_fields(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post with missing fields """
    response = client.simulate_post('/sftp')
    assert response.status_code == 400

def test_post_missing_headers(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post with missing headers """
    response = client.simulate_post(
        '/sftp',
        params={
            'remotepath': 'test',
            'filename': 'hello.txt'})
    assert response.status_code == 400

def test_post_bad_filename(client, mock_env_access_key):
    # pylint: disable=unused-argument,anomalous-backslash-in-string
    """ test post with bad filename """
    response = client.simulate_post(
        '/sftp',
        headers=FTP_HEADERS,
        params={
            'remotepath': 'test',
            'filename': 'Z#~Y\8$`x?|OV`/ScI^rM.vj6n(^'})

    assert response.status_code == 400

def test_post_write_failed(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post """
    with patch('service.resources.sftp.open') as mock_open:
        mock_file = MockFileObj()
        mock_open.return_value = mock_file
        response = client.simulate_post(
            '/sftp',
            body='error',
            headers=FTP_HEADERS,
            params={
                'remotepath': 'test',
                'filename': 'hello.txt'})

    assert response.status_code == 400

def test_post_write_host_failed(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post """
    with patch('service.resources.sftp.open') as mock_open:
        mock_file = MockFileObj()
        mock_open.return_value = mock_file
        response = client.simulate_post(
            '/sftp',
            body='host_error',
            headers={
                'X-SFTP-HOST':'localhost',
                'X-SFTP-HOST-KEY':'host-key-error',
                'X-SFTP-USER':'user',
                'X-SFTP-PASSWORD':'1234',
            },
            params={
                'remotepath': 'test',
                'filename': 'hello.txt'})

    assert response.status_code == 400

def test_post_generic_error(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post """
    with patch('service.resources.sftp.SFTP.transfer_file') as mock_put:
        mock_put.return_value = None
        response = client.simulate_post(
            '/sftp',
            body='hello',
            headers=FTP_HEADERS,
            params={
                'remotepath': 'test',
                'filename': 'hello.txt'})

    assert response.status_code == 400

def test_post_exception(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post """
    with patch('service.resources.sftp.pysftp.Connection') as mock_put:
        mock_connection = MockConnection()
        mock_put.return_value = mock_connection
        response = client.simulate_post(
            '/sftp',
            body='hello',
            headers=FTP_HEADERS,
            params={
                'remotepath': 'test',
                'filename': 'OSError.txt'})

    assert response.status_code == 400

def test_post(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post """
    with patch('service.resources.sftp.pysftp.Connection') as mock_put:
        mock_connection = MockConnection()
        mock_put.return_value = mock_connection
        response = client.simulate_post(
            '/sftp',
            body='hello',
            headers=FTP_HEADERS,
            params={
                'remotepath': 'test',
                'filename': 'hello.txt'})

    assert response.status_code == 200

def test_post_bundle(client, mock_env_access_key):
    # pylint: disable=unused-argument
    """ test post """
    with patch('service.resources.sftp.pysftp.Connection') as mock_put:
        mock_connection = MockConnection()
        mock_put.return_value = mock_connection
        response = client.simulate_post(
            '/sftp',
            body='hello',
            headers={
                'X-SFTP-BUNDLE':'MOCK'
            },
            params={
                'remotepath': 'test',
                'filename': 'hello.txt'})

    assert response.status_code == 200

# pylint: disable=no-self-use,unused-argument
class MockConnection():
    """ Mock Connection class """

    #pylint: disable=invalid-name
    def cd(self, remotepath=None):
        """ cd method """
        return None

    def chdir(self, remotepath):
        """ chdir method """
        return None

    # pylint: disable=too-many-arguments
    def put(self, localpath, remotepath=None, callback=None, confirm=True, preserve_mtime=False):
        """ put method """
        if "OSError" in localpath:
            raise OSError
        return 100

class MockFileObj():
    """ Mock Object class """
    def write(self, data):
        """ mock file write """
        if data in (b'error', 'host-key-error'):
            return None
        return 100

    def close(self):
        """ mock file close """
        return False
