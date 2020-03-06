# pylint: disable=redefined-outer-name
"""Tests for microservice"""
import os
import pytest
from falcon import testing
import service.microservice

@pytest.fixture()
def client():
    """ client fixture """
    access_key = os.environ.get('ACCESS_KEY')
    return testing.TestClient(
        app=service.microservice.start_service(), headers={'ACCESS_KEY': access_key})

def test_post(client):
    """ test post """
    with open('examples/tests/mocks/sftp_post_data.txt', 'r') as file_obj:
        sftp_data = file_obj.read()
    assert sftp_data

    sftp_host = os.environ.get('SFTP_HOST')
    sftp_bundle = 'TEST'
    sftp_dir = '/OOC/test'
    sftp_filename = 'TEST-CI.txt'
    response = client.simulate_post('/sftp',
                                    body=sftp_data,
                                    headers={
                                        'X-SFTP-HOST': sftp_host,
                                        'X-SFTP-BUNDLE': sftp_bundle
                                        },
                                    params={
                                        'remotepath': sftp_dir,
                                        'filename': sftp_filename})
    assert response.status_code == 200
