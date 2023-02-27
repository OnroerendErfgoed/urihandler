import logging

import pytest
from pyramid import testing
from pyramid.httpexceptions import HTTPNotAcceptable

from urihandler.handler import IUriHandler
from urihandler.handler import UriHandler
from urihandler.handler import _build_uri_handler
from urihandler.handler import get_uri_handler

logging.basicConfig(level=logging.DEBUG)


class TestHandler:

    def test_no_match(self, urihandler):
        req = testing.DummyRequest()
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/bunnies/koen", req)
        assert res is None

    def test_mounted_redirect(self, urihandler):
        req = testing.DummyRequest()
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/foobar/18", req)
        assert res == "http://localhost:5555/foobar/18"

    def test_redirect_with_mime_match(self, urihandler):
        req = testing.DummyRequest(accept="application/json")
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/foobar/18", req)
        assert res == "http://localhost:5555/foobar/18.json"

        req = testing.DummyRequest(accept="application/*")
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/foobar/18", req)
        assert res == "http://localhost:5555/foobar/18.json"

    def test_redirect_with_mime_no_match(self, urihandler):
        req = testing.DummyRequest(accept="application/pdf")
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/foobar/18", req)
        assert res == "http://localhost:5555/foobar/18"

    def test_redirect_default_set(self, urihandler):
        req = testing.DummyRequest()
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/pdf_default/18", req)
        assert res == "http://localhost:5555/pdf_default/18.pdf"

        req = testing.DummyRequest(accept="application/*")
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/pdf_default/18", req)
        assert res == "http://localhost:5555/pdf_default/18.json"

    def test_redirect_no_default(self, urihandler):
        req = testing.DummyRequest()
        req.host_url = "http://test.urihandler.org"
        with pytest.raises(HTTPNotAcceptable):
            urihandler.handle("http://test.urihandler.org/mime_no_default/18", req)

        req = testing.DummyRequest(accept="application/pdf")
        req.host_url = "http://test.urihandler.org"
        with pytest.raises(HTTPNotAcceptable):
            urihandler.handle("http://test.urihandler.org/mime_no_default/18", req)

    def test_unanchored_redirect(self, urihandler):
        req = testing.DummyRequest()
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle(
            "http://test.urihandler.org/something/override/me/987", req
        )
        assert res == "http://localhost:2222/me/987"

    def test_urn_redirect(self, urihandler):
        req = testing.DummyRequest()
        res = urihandler.handle("urn:x-barbar:area:51", req)
        assert res == "http://localhost:2222/area/51"

    def test_two_matches(self, urihandler):
        req = testing.DummyRequest()
        req.host_url = "http://test.urihandler.org"
        res = urihandler.handle("http://test.urihandler.org/foo/6/bar/66", req)
        assert res == "http://localhost:5555/foo/6/bar/66"


class MockRegistry:
    def __init__(self, settings=None):

        if settings is None:
            self.settings = {}
        else:  # pragma NO COVER
            self.settings = settings

        self.uri_handler = None

    def queryUtility(self, iface):
        return self.uri_handler

    def registerUtility(self, uri_handler, iface):
        self.uri_handler = uri_handler


class TestGetAndBuild:
    def test_get_uri_handler(self, handlerconfig):
        r = MockRegistry()
        UH = UriHandler(handlerconfig["uris"])
        r.registerUtility(UH, IUriHandler)
        UH2 = get_uri_handler(r)
        assert UH == UH2

    def test_build_uri_handler_already_exists(self, handlerconfig):
        r = MockRegistry()
        UH = UriHandler(handlerconfig["uris"])
        r.registerUtility(UH, IUriHandler)
        UH2 = _build_uri_handler(r, handlerconfig)
        assert UH == UH2

    def test_build_uri_handler(self, handlerconfig):
        r = MockRegistry()
        UH = _build_uri_handler(r, handlerconfig)
        assert isinstance(UH, UriHandler)
