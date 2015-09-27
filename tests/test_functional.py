# -*- coding: utf-8 -*-
import os

import pytest

from webtest import TestApp

@pytest.fixture()
def app():
    settings = {
        'urihandler.config': os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test.yaml')
    }
    from urihandler import main
    return TestApp(main({}, **settings))

class TestFunctional:

    def test_redirect(self, app):
        res = app.get('/foobar/18', status=303)
        assert res.status == '303 See Other'

    def test_redirect_no_match(self, app):
        res = app.get('/test', status=404)
        assert res.status == '404 Not Found'

    def test_handle(self, app):
        res = app.get('/handle?uri=http://localhost/foobar/18', status=303)
        assert res.status == '303 See Other'

    def test_handle_no_match(self, app):
        res = app.get('/handle?uri=http://id.erfgoed.net/foo/1', status=404)
        assert res.status == '404 Not Found'

    def test_handle_no_uri(self, app):
        res = app.get('/handle?url=http://id.erfgoed.net/foo/1', status=400)
        assert res.status == '400 Bad Request'
