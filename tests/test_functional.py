import json
import os

import pytest
from webtest import TestApp


@pytest.fixture()
def app():
    settings = {
        "urihandler.config": os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test.yaml"
        )
    }
    from urihandler import main

    return TestApp(main({}, **settings))


class TestFunctional:
    def test_redirect(self, app):
        res = app.get("/foobar/18", status=303)
        assert res.status == "303 See Other"

    def test_redirect_accept_header_json(self, app):
        res = app.get("/foobar/18", headers={"Accept": "application/json"}, status=303)
        assert res.status == "303 See Other"
        assert res.location == "http://localhost:5555/foobar/18.json"

    def test_redirect_accept_header_html(self, app):
        res = app.get("/foobar/18", headers={"Accept": "text/html"}, status=303)
        assert res.status == "303 See Other"
        assert res.location == "http://localhost:5555/foobar/18"

    def test_redirect_accept_header_wildcard(self, app):
        res = app.get("/foobar/18", headers={"Accept": "*/*"}, status=303)
        assert res.status == "303 See Other"
        assert res.location == "http://localhost:5555/foobar/18"

    def test_redirect_not_allowed(self, app):
        res = app.post("/foobar/18", status=405)
        assert res.status == "405 Method Not Allowed"

    def test_redirect_no_match(self, app):
        res = app.get("/test", status=404)
        assert res.status == "404 Not Found"

    def test_handle(self, app):
        res = app.get("/handle?uri=http://localhost/foobar/18", status=303)
        assert res.status == "303 See Other"

    def test_handle_no_match(self, app):
        res = app.get("/handle?uri=http://id.erfgoed.net/foo/1", status=404)
        assert res.status == "404 Not Found"

    def test_handle_no_uri(self, app):
        res = app.get("/handle?url=http://id.erfgoed.net/foo/1", status=400)
        assert res.status == "400 Bad Request"

    def test_uris(self, app):
        res = app.get("/uris?uri=http://localhost/foobar/18")
        assert res.status == "200 OK"
        assert "application/json" in res.headers["Content-Type"]
        data = json.loads(res.body.decode("utf-8"))
        assert data["uri"] == "http://localhost/foobar/18"
        assert data["location"] == "http://localhost:5555/foobar/18"

    def test_uris_with_params(self, app):
        res = app.get(
            "/uris?uri=http://localhost/foobar/18"
            "?utm_source%3Dbeslissingsmail%26utm_medium%3Demail"
        )
        assert res.status == "200 OK"
        assert "application/json" in res.headers["Content-Type"]
        data = json.loads(res.body.decode("utf-8"))
        assert data["uri"] == (
            "http://localhost/foobar/18" "?utm_source=beslissingsmail&utm_medium=email"
        )
        assert data["location"] == (
            "http://localhost:5555/foobar/18"
            "?utm_source=beslissingsmail&utm_medium=email"
        )

    def test_uris_no_match(self, app):
        res = app.get("/uris?uri=http://id.erfgoed.net/foo/1")
        assert res.status == "200 OK"
        assert "application/json" in res.headers["Content-Type"]
        data = json.loads(res.body.decode("utf-8"))
        assert data["uri"] == "http://id.erfgoed.net/foo/1"
        assert data["location"] is None
        assert not data["success"]

    def test_uris_no_uri(self, app):
        res = app.get("/uris?url=http://localhost/foobar/18", status=400)
        assert res.status == "400 Bad Request"

    def test_uris_two_parameters(self, app):
        res = app.get("/uris?uri=urn:x-barbar:area:51")
        assert res.status == "200 OK"
        assert "application/json" in res.headers["Content-Type"]
        data = json.loads(res.body.decode("utf-8"))
        assert data["uri"] == "urn:x-barbar:area:51"
        assert data["location"] == "http://localhost:2222/area/51"

    def test_uris_caching(self, app):
        res = app.get("/uris?uri=http://localhost/foobar/18")
        assert "Cache-Control" in res.headers
        assert "ETag" in res.headers
        etag = res.headers["ETag"]
        res2 = app.get(
            "/uris?uri=http://localhost/foobar/18", headers={"If-None-Match": etag}
        )
        assert res2.status == "304 Not Modified"
