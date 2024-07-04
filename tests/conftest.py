import pytest

from urihandler.handler import UriHandler


@pytest.fixture(scope="session")
def handlerconfig():
    cfg = {
        "uris": [
            {
                "match": r"^/foobar/(?P<id>\d+)$",
                "mount": True,
                "redirect": {
                    "default": "http://localhost:5555/foobar/{id}",
                    "text/html": "http://localhost:5555/foobar/{id}",
                    "application/json": "http://localhost:5555/foobar/{id}.json",
                },
            },
            {
                "match": r"^/bar/(?P<name>\w+)$",
                "redirect": "http://localhost:5555/bar/{name}",
            },
            {
                "match": r"^urn:x-barbar:(?P<namespace>\w+):(?P<id>\d+)$",
                "mount": False,
                "redirect": "http://localhost:2222/{namespace}/{id}",
            },
            {
                "match": r"override/(?P<namespace>\w+)/(?P<id>\d+)$",
                "redirect": "http://localhost:2222/{namespace}/{id}",
            },
            {
                "match": r"^/foo/(?P<foo_id>\d+)/bar/(?P<bar_id>\d+)$",
                "mount": True,
                "redirect": "http://localhost:5555/foo/{foo_id}/bar/{bar_id}",
            },
            {
                "match": r"^/pdf_default/(?P<id>\d+)$",
                "mount": True,
                "redirect": {
                    "default": "http://localhost:5555/pdf_default/{id}.pdf",
                    "text/html": "http://localhost:5555/pdf_default/{id}",
                    "application/json": "http://localhost:5555/pdf_default/{id}.json",
                    "application/pdf": "http://localhost:5555/pdf_default/{id}.pdf",
                },
            },
            {
                "match": r"^/mime_no_default/(?P<id>\d+)$",
                "mount": True,
                "redirect": {
                    "text/html": "http://localhost:5555/pdf_default/{id}",
                    "application/json": "http://localhost:5555/pdf_default/{id}.json",
                },
            },
        ]
    }
    return cfg


@pytest.fixture(scope="session")
def urihandler(handlerconfig):
    return UriHandler(handlerconfig["uris"])
