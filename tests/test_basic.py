import logging
from livefyre.client import Client
import os

logging.basicConfig(level=logging.DEBUG)

LIVEFYRE_API_ENDPOINT = os.environ['LIVEFYRE_API_ENDPOINT']
CLIENT_ID = os.environ['LIVEFYRE_CLIENT_ID']
CLIENT_SECRET = os.environ['LIVEFYRE_CLIENT_SECRET']

client = Client(LIVEFYRE_API_ENDPOINT, CLIENT_ID, CLIENT_SECRET)

class TestSimple:
    def testCredentials(self):
        assert 'livefyre' in client.ping()
        
