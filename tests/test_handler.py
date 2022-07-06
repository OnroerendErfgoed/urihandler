import logging

from pyramid import testing

from urihandler.handler import IUriHandler
from urihandler.handler import UriHandler
from urihandler.handler import _build_uri_handler
from urihandler.handler import get_uri_handler

logging.basicConfig(level=logging.DEBUG)


class TestHandler:
    def test_urihandler_exists(self, urihandler):
        assert urihandler

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
