import pytest

from urihandler.handler import UriHandler

@pytest.fixture(scope="session")
def handlerconfig():
    cfg = {
        'uris': [
            {
                'match': '^/foobar/(?P<id>\d+)$',
                'mount': True,
                'redirect': 'http://localhost:5555/foobar/{id}'
            }, {
                'match': '^/bar/(?P<name>\w+)$',
                'redirect': 'http://localhost:5555/bar/{name}'
            } , {
                'match': '^urn:x-barbar:(?P<namespace>:\w+):(?P<id>\d+)$',
                'mount': False,
                'redirect': 'http://localhost:2222/{namespace}/{id}'
            }
        ]
    }
    return cfg


@pytest.fixture(scope="session")
def urihandler(handlerconfig):
    return UriHandler(handlerconfig['uris'])
