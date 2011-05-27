Livefyre API Client
-------------------

::

    from livefyre.client import Client
    client = Client("http://api.livefyre.com", "...domain...", "...secret...")
    client.ping()

Running Tests
=============

::

    export LIVEFYRE_CLIENT_SECRET=...
    export LIVEFYRE_CLIENT_ID=...
    export LIVEFYRE_API_ENDPOINT=...
    
    python setup.py nosetests

