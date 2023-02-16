import logging
import os

import yaml
from pyramid.config import Configurator

from .handler import _build_uri_handler
from .handler import get_uri_handler

log = logging.getLogger(__name__)


def _parse_settings(settings):
    """
    Parse the relevant settings for this application.

    :param dict settings:
    """

    log.debug(settings)

    prefix = "urihandler"

    defaults = {
        "config": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "sample.yaml")
        )
    }

    urihand_settings = defaults.copy()

    for short_key_name in ("config",):
        key_name = f"{prefix}.{short_key_name}"
        if key_name in settings:
            urihand_settings[short_key_name] = settings.get(
                key_name, defaults.get(short_key_name, None)
            )

    for short_key in urihand_settings:
        long_key = f"{prefix}.{short_key}"
        settings[long_key] = urihand_settings[short_key]

    return urihand_settings


def _load_configuration(path):
    """
    Load the configuration for the UriHandler.

    :param str path: Path to the config file in YAML format.
    :returns: A :class:`dict` with the config options.
    """
    log.debug("Loading uriregistry config from %s." % path)
    with open(path) as f:
        content = yaml.safe_load(f.read())

    # Perform some validation so we can warn/fail early.
    for redirect_rule in content["uris"]:
        if "default" not in redirect_rule:
            if isinstance(redirect_rule["redirect"], dict):
                log.warning(
                    f"{redirect_rule['match']}: Having no default mimetype when "
                    f"declaring multiple mime redirect rules will result in a 406 "
                    f"when no accept header is present."
                )
            continue
    log.debug(content)
    return content


def main(global_config, **settings):
    """This function returns a Pyramid WSGI application."""
    config = Configurator(settings=settings)

    urihand_settings = _parse_settings(config.registry.settings)
    handlerconfig = _load_configuration(urihand_settings["config"])

    _build_uri_handler(config.registry, handlerconfig)

    config.add_directive("get_uri_handler", get_uri_handler)
    config.add_request_method(get_uri_handler, "uri_handler", reify=True)

    config.add_route("handle", "/handle")
    config.add_route("uris", "/uris")
    config.add_route("redirect", "/{uri:.*}")

    config.scan()
    return config.make_wsgi_app()
