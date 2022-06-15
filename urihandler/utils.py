import base64
import hashlib

from pyramid.renderers import render
from pyramid.util import bytes_
from pyramid.util import text_


def create_version_hash(uri_dict, request):
    """
    Turn a response into a version hash.

    :param dict uri_dict:
    :param pyramid.request.Request request:
    :rtype: str
    """
    json = render(renderer_name="json", value=uri_dict, request=request)
    hash = text_(
        base64.b64encode(hashlib.md5(bytes_(json, encoding="UTF-8")).digest()),
        encoding="UTF-8",
    )
    return hash.strip("=")
