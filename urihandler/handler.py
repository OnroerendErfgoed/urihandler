import copy
import logging
import re

from pyramid.httpexceptions import HTTPNotAcceptable
from webob.acceptparse import AcceptNoHeader
from zope.interface import Interface

log = logging.getLogger(__name__)


class IUriHandler(Interface):
    pass


class UriHandler:
    """
    Central handler that deals with redirecting uri's.
    """

    def __init__(self, uris=[]):
        self.uris = uris

    def handle(self, uri, request):
        uris = copy.deepcopy(self.uris)
        for u in uris:
            if "mount" not in u or u["mount"]:
                if u["match"].startswith("^"):
                    u["match"] = u["match"].replace("^", "^" + request.host_url)
                else:
                    u["match"] = request.host_url + "/.*" + u["match"]
            log.debug(f"Matching {uri} to {u['match']}.")
            m = re.match(u["match"], uri)
            if m:
                redirect = u["redirect"]
                if isinstance(redirect, dict):
                    if isinstance(request.accept, AcceptNoHeader):
                        redirect = redirect.get("default")
                        if not redirect:
                            raise HTTPNotAcceptable()
                    else:
                        for mime, redirect in redirect.items():
                            if mime in request.accept:
                                break
                        else:
                            # No matching mime was found.
                            raise HTTPNotAcceptable()
                redirect = redirect.format(**m.groupdict())
                log.debug(f"Match found. Redirecting to {redirect}.")
                return redirect
        return None


def _build_uri_handler(registry, handlerconfig):
    """
    :param pyramid.registry.Registry registry: Pyramid registry
    :param dict handlerconfig: UriHandler config in dict form.
    :rtype: :class:`uriregistry.registry.UriHandler`
    """
    uri_handler = registry.queryUtility(IUriHandler)
    if uri_handler is not None:
        return uri_handler

    uri_handler = UriHandler(
        handlerconfig["uris"],
    )

    registry.registerUtility(uri_handler, IUriHandler)
    return registry.queryUtility(IUriHandler)


def get_uri_handler(registry):
    """
    Get the :class:`urihandler.handler.UriHandler` attached to this pyramid
    application.

    :rtype: :class:`urihandler.handler.UriHandler`
    """
    # Argument might be a config or request
    regis = getattr(registry, "registry", None)
    if regis is None:
        regis = registry
    return regis.queryUtility(IUriHandler)
