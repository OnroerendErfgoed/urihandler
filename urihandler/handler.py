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

    def __init__(self, uris=None):
        self.uris = uris or []

    def handle(self, uri, request):
        params = ""
        if "?" in uri:
            uri, params = uri.split("?", 1)
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
                    redirect = self._get_redirect_based_on_accept_header(
                        request.accept, redirect
                    )
                if params:
                    redirect = f"{redirect.format(**m.groupdict())}?{params}"
                else:
                    redirect = redirect.format(**m.groupdict())
                log.debug(f"Match found. Redirecting to {redirect}.")
                return redirect
        return None

    def _get_redirect_based_on_accept_header(self, accept_header, redirect_rule):
        """
        Return the redirect rule based on accept header.

        At its core it simply looks for a matching mime between accept header
        and the configured mime type redirects. But exceptions apply.

        If there is no accept header specified or if no matching mime is found,
        the default will be returned. If default is not set, HTTP 406 gets raised.
        """
        default = redirect_rule.get("default")
        if isinstance(accept_header, AcceptNoHeader):
            if not default:
                raise HTTPNotAcceptable()
            return default

        for mime, redirect in redirect_rule.items():
            if mime in accept_header:
                return redirect

        if not default:
            raise HTTPNotAcceptable()

        return default


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
