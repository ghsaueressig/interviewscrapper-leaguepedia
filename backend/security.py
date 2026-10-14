"""Network boundary for fetching user-submitted article URLs.

Only configured publishers may be fetched. Connections are made to a vetted
DNS result, rather than resolving the hostname again inside the HTTP client.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit, urlunsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3 import PoolManager
from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.util import connection as urllib3_connection

from data.publications import WRITTEN_PUBLICATIONS

MAX_REDIRECTS = 3
MAX_RESPONSE_BYTES = 3 * 1024 * 1024
DEFAULT_TIMEOUT = (5, 15)


class UnsafeURLError(ValueError):
    """The requested URL or its resolved destination is not allowed."""


def validate_url(url: str, allowed_domains=None) -> str:
    """Return a canonical URL only when it targets an approved publisher."""
    if not isinstance(url, str) or not url or len(url) > 2048:
        raise UnsafeURLError("URL inválida ou muito longa.")
    if any(ord(c) < 33 or ord(c) == 127 for c in url):
        raise UnsafeURLError("URL contém caracteres proibidos.")
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port  # May raise ValueError.
    except ValueError as exc:
        raise UnsafeURLError("URL malformada.") from exc
    if parsed.scheme not in ("https", "http") or not hostname:
        raise UnsafeURLError("Protocolo ou hostname inválido.")
    if parsed.username is not None or parsed.password is not None:
        raise UnsafeURLError("Credenciais na URL não são permitidas.")
    if port not in (None, 80, 443):
        raise UnsafeURLError("Porta não permitida.")
    if (parsed.scheme == "https" and port == 80) or (parsed.scheme == "http" and port == 443):
        raise UnsafeURLError("Combinação de porta e protocolo inválida.")
    hostname = hostname.lower().rstrip(".")
    allowed = allowed_domains if allowed_domains is not None else WRITTEN_PUBLICATIONS
    # Only apex and www: do not automatically trust arbitrary subdomains.
    if not any(hostname == domain or hostname == "www." + domain for domain in allowed):
        raise UnsafeURLError("Domínio não permitido para artigos.")
    if parsed.fragment:
        parsed = parsed._replace(fragment="")
    return urlunsplit(parsed)


def resolve_public_ip(hostname: str, port: int) -> str:
    """Reject the entire DNS answer if any address is non-public."""
    try:
        addresses = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeURLError("Não foi possível resolver o domínio.") from exc
    if not addresses:
        raise UnsafeURLError("Domínio sem endereço IP.")
    ips = []
    for entry in addresses:
        ip = ipaddress.ip_address(entry[4][0])
        if not ip.is_global:
            raise UnsafeURLError("Destino de rede não permitido.")
        ips.append(str(ip))
    return ips[0]


class _PinnedConnectionMixin:
    def _new_conn(self):
        ip = resolve_public_ip(self.host, self.port)
        try:
            return urllib3_connection.create_connection(
                (ip, self.port), self.timeout, source_address=self.source_address,
                socket_options=self.socket_options,
            )
        except OSError as exc:
            from urllib3.exceptions import NewConnectionError
            raise NewConnectionError(self, f"Connection failed: {exc}") from exc


class _PinnedHTTPConnection(_PinnedConnectionMixin, HTTPConnection):
    pass


class _PinnedHTTPSConnection(_PinnedConnectionMixin, HTTPSConnection):
    pass


class _PinnedHTTPPool(HTTPConnectionPool):
    ConnectionCls = _PinnedHTTPConnection


class _PinnedHTTPSPool(HTTPSConnectionPool):
    ConnectionCls = _PinnedHTTPSConnection


class _PinnedAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        self.poolmanager = PoolManager(num_pools=connections, maxsize=maxsize, block=block, **pool_kwargs)
        self.poolmanager.pool_classes_by_scheme = {"http": _PinnedHTTPPool, "https": _PinnedHTTPSPool}


def safe_get(url: str, *, headers=None, timeout=DEFAULT_TIMEOUT,
             max_redirects=MAX_REDIRECTS, max_bytes=MAX_RESPONSE_BYTES) -> requests.Response:
    """Fetch a permitted article with DNS-pinned connections and bounded body."""
    current = validate_url(url)
    with requests.Session() as session:
        session.trust_env = False  # Never route user URLs through environment proxies.
        adapter = _PinnedAdapter()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        for hop in range(max_redirects + 1):
            response = session.get(current, headers=headers, timeout=timeout,
                                   allow_redirects=False, stream=True)
            try:
                if response.status_code in (301, 302, 303, 307, 308):
                    if hop == max_redirects:
                        raise UnsafeURLError("Limite de redirecionamentos excedido.")
                    from urllib.parse import urljoin
                    location = response.headers.get("Location")
                    if not location:
                        raise UnsafeURLError("Redirecionamento sem destino.")
                    current = validate_url(urljoin(current, location))
                    continue
                response.raise_for_status()
                chunks = []
                size = 0
                for chunk in response.iter_content(chunk_size=16384):
                    size += len(chunk)
                    if size > max_bytes:
                        raise UnsafeURLError("Resposta excede o tamanho permitido.")
                    chunks.append(chunk)
                # Populate Requests' cached content so callers can use .text.
                response._content = b"".join(chunks)
                response._content_consumed = True
                return response
            finally:
                response.close()
    raise UnsafeURLError("Redirecionamento inválido.")
