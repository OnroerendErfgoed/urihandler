import logging
import os

from urihandler import _load_configuration
from urihandler import _parse_settings


class TestGeneral:
    def test_parse_settings(self):
        settings = {
            "urihandler.config": os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "test.yaml"
            )
        }
        args = _parse_settings(settings)
        assert "config" in args
        assert args["config"] == os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "test.yaml"
        )

    def test_load_configuration(self):
        cfg = _load_configuration(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "test.yaml")
        )
        assert "uris" in cfg

    def test_load_configuration_bad_file(self, caplog):
        with caplog.at_level(logging.WARN):
            _load_configuration(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "fail.yaml")
            )
        assert len(caplog.records) == 1
        assert caplog.records[0].message == (
            "^/no_default_present/(?P<id>\\d+)$: Having no default mimetype when "
            "declaring multiple mime redirect rules will result in a 406 when no "
            "accept header is present."
        )
