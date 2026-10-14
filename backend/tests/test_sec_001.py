import importlib
import os
import socket
import ssl
import subprocess
import sys
import tempfile
import threading
import types
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import requests

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from security import (
    UnsafeURLError,
    resolve_public_ip,
    safe_get,
    validate_url,
    validate_youtube_url,
)


def make_test_certificate(directory, common_name):
    cert_path = Path(directory) / "cert.pem"
    key_path = Path(directory) / "key.pem"
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", str(key_path), "-out", str(cert_path),
            "-days", "1", "-nodes", "-subj", f"/CN={common_name}",
        ],
        check=True,
        capture_output=True,
    )
    return cert_path, key_path


class ProtocolAndUrlTests(unittest.TestCase):
    def test_http_and_https_approved_publishers_are_accepted(self):
        for host in ("maisesports.com.br", "www.sheepesports.com", "pichauarena.com.br", "itatiaia.com.br"):
            self.assertTrue(validate_url(f"https://{host}/article").startswith("https://"))
            self.assertTrue(validate_url(f"http://{host}/article").startswith("http://"))

    def test_credentials_ports_and_lookalike_domains(self):
        rejected = (
            "https://user:pass@maisesports.com.br/a",
            "https://maisesports.com.br:8080/a",
            "https://maisesports.com.br.evil.example/a",
            "https://evil.example/a",
            "https://user:pass@youtube.com/watch?v=abc",
            "https://youtube.com.evil.example/watch?v=abc",
            "https://youtu.be:8080/abc",
        )
        for url in rejected:
            with self.subTest(url=url), self.assertRaises(UnsafeURLError):
                if "youtube" in url or "youtu.be" in url:
                    validate_youtube_url(url)
                else:
                    validate_url(url)

    def test_http_to_https_same_publisher_redirect_is_allowed(self):
        from urllib.parse import urljoin
        current = validate_url("http://maisesports.com.br/article")
        self.assertEqual(
            validate_url(urljoin(current, "https://maisesports.com.br/article")),
            "https://maisesports.com.br/article",
        )

    def test_redirect_to_forbidden_host_is_blocked(self):
        from urllib.parse import urljoin
        current = validate_url("https://maisesports.com.br/article")
        with self.assertRaises(UnsafeURLError):
            validate_url(urljoin(current, "http://127.0.0.1/private"))
        with self.assertRaises(UnsafeURLError):
            validate_url(urljoin(current, "https://evil.example/phish"))


class PinAndTlsTests(unittest.TestCase):
    def test_connection_uses_first_public_ip_not_rebound_address(self):
        answers = [
            [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))],
            [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))],
        ]

        def fake_getaddrinfo(hostname, port, *args, **kwargs):
            return answers.pop(0)

        seen = []

        def fake_create(address, *args, **kwargs):
            seen.append(address)
            raise OSError("stopped before network")

        with patch("security.socket.getaddrinfo", fake_getaddrinfo), \
             patch("security.urllib3_connection.create_connection", fake_create):
            with self.assertRaises((UnsafeURLError, requests.exceptions.RequestException, OSError)):
                safe_get("https://maisesports.com.br/article")

        self.assertEqual(seen, [("8.8.8.8", 443)])
        self.assertTrue(answers, "second DNS answer was not consumed by the client")

    def test_private_dns_answer_never_connects(self):
        def fake_getaddrinfo(hostname, port, *args, **kwargs):
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 443))]

        def fail_create(*args, **kwargs):
            raise AssertionError("connection attempted")

        with patch("security.socket.getaddrinfo", fake_getaddrinfo), \
             patch("security.urllib3_connection.create_connection", fail_create):
            with self.assertRaises(UnsafeURLError):
                safe_get("https://maisesports.com.br/article")

    def test_dns_failure_is_rejected(self):
        with patch("security.socket.getaddrinfo", side_effect=socket.gaierror("no dns")):
            with self.assertRaises(UnsafeURLError):
                resolve_public_ip("maisesports.com.br", 443)

    def test_environment_proxy_is_not_used(self):
        created = []
        real = requests.Session.__init__

        def wrapped(self, *args, **kwargs):
            real(self, *args, **kwargs)
            created.append(self)

        with patch.dict(os.environ, {"HTTPS_PROXY": "http://127.0.0.1:9", "HTTP_PROXY": "http://127.0.0.1:9"}), \
             patch("requests.Session.__init__", wrapped), \
             patch("security.socket.getaddrinfo", side_effect=socket.gaierror("stop")):
            with self.assertRaises(UnsafeURLError):
                safe_get("https://maisesports.com.br/article")

        self.assertTrue(created)
        self.assertFalse(created[-1].trust_env)

    def test_tls_uses_pinned_ip_and_rejects_wrong_certificate(self):
        seen_sni = []

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok")

            def log_message(self, *_):
                return

        with tempfile.TemporaryDirectory() as directory:
            cert_path, key_path = make_test_certificate(directory, "evil.example")
            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_path, key_path)

            def record_sni(sock, name, tls_context):
                seen_sni.append(name)
                return None

            context.sni_callback = record_sni
            server.socket = context.wrap_socket(server.socket, server_side=True)
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                pinned_url = f"https://maisesports.com.br:{port}/article"
                with patch("security.resolve_public_ip", return_value="127.0.0.1"), \
                     patch("security.validate_url", return_value=pinned_url):
                    with self.assertRaises(requests.exceptions.SSLError):
                        safe_get(pinned_url)
            finally:
                server.shutdown()
                server.server_close()

        self.assertEqual(seen_sni, ["maisesports.com.br"])


class EndpointTests(unittest.TestCase):
    added_modules = {}

    @classmethod
    def setUpClass(cls):
        cls.added_modules = {}

        def ensure(name, **attrs):
            if name in sys.modules:
                return
            try:
                importlib.import_module(name)
                return
            except ModuleNotFoundError:
                module = types.ModuleType(name)
                for key, value in attrs.items():
                    setattr(module, key, value)
                sys.modules[name] = module
                cls.added_modules[name] = module

        ensure("data")
        ensure("services")
        ensure("data.players", PLAYER_DATA={})
        ensure("data.teams", TEAM_MAP={})
        ensure("services.leaguepedia",
               resolve_player=lambda *a, **k: None,
               get_cached_player=lambda *a, **k: None,
               cache_player=lambda *a, **k: None,
               get_current_player=lambda *a, **k: None,
               search_player=lambda *a, **k: None,
               fuzzy_match_player=lambda *a, **k: None,
               fuzzy_match_players=lambda *a, **k: [],
               extract_fuzzy_player_candidates=lambda *a, **k: [])
        ensure("data.content",
               STOPWORDS=set(),
               INTERVIEW_TITLE_MARKERS=[],
               ARTICLE_TITLE_MARKERS=[],
               TRANSLATOR_PATTERNS=[],
               YOUTUBE_INTERVIEW_PATTERNS=[],
               YOUTUBE_ARTICLE_PATTERNS=[])
        ensure("data.tournaments",
               TOURNAMENT_CALENDAR={},
               TOURNAMENT_PATTERNS={},
               TOURNAMENT_NAMES={})
        ensure("data.authors", AUTHOR_MAPPINGS=[])
        ensure("data.config", MAX_URLS_PER_REQUEST=10)
        ensure("youtube_metadata", get_youtube_metadata=lambda url: {"title": "ok", "published_at": None})
        import app as app_module
        cls.app = app_module
        cls.client = app_module.app.test_client()

    @classmethod
    def tearDownClass(cls):
        for name in cls.added_modules:
            sys.modules.pop(name, None)

    def test_invalid_json_shapes_are_400(self):
        cases = [
            ("/api/scrape", None, "application/json"),
            ("/api/scrape", "[", "application/json"),
            ("/api/scrape", "[1,2]", "application/json"),
            ("/api/youtube-metadata", "[]", "application/json"),
            ("/api/youtube-metadata", "null", "application/json"),
        ]
        for path, body, content_type in cases:
            with self.subTest(path=path, body=body):
                response = self.client.post(path, data=body, content_type=content_type)
                self.assertEqual(response.status_code, 400)
                self.assertNotIn(b"Traceback", response.data)

    def test_invalid_url_items_do_not_500(self):
        response = self.client.post("/api/scrape", json={"urls": [None, 12, "ftp://maisesports.com.br/a", "https://evil.example/a"]})
        self.assertIn(response.status_code, (200, 400))
        self.assertNotIn(b"Traceback", response.data)
        if response.status_code == 200:
            for item in response.get_json()["results"]:
                self.assertIn("error", item)
                self.assertNotIn("Traceback", item["error"])

    def test_internal_exception_is_not_exposed(self):
        with patch.object(self.app, "safe_get", side_effect=RuntimeError("secret-token-xyz")):
            result = self.app.scrape_article("https://maisesports.com.br/article")
        self.assertEqual(result["error"], "Erro ao processar a página.")
        self.assertNotIn("secret-token", result["error"])

    def test_youtube_metadata_rejects_non_youtube(self):
        response = self.client.post("/api/youtube-metadata", json={"url": "https://evil.example/watch"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["error"], "URL do YouTube inválida.")


if __name__ == "__main__":
    unittest.main()


FAKE_YOUTUBE_KEY = "FAKE_YT_KEY_DO_NOT_LOG_12345"


class YouTubeKeyLeakTests(unittest.TestCase):
    def _capture_logs(self, logger_name):
        import logging
        from io import StringIO
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        logger = logging.getLogger(logger_name)
        previous = logger.level
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return stream, handler, logger, previous

    def _release_logs(self, stream, handler, logger, previous):
        logger.removeHandler(handler)
        logger.setLevel(previous)
        return stream.getvalue()

    def test_connection_failure_does_not_leak_key(self):
        import youtube_metadata
        leaked = (
            "HTTPSConnectionPool(host='www.googleapis.com', port=443): "
            f"Max retries exceeded with url: /youtube/v3/videos?key={FAKE_YOUTUBE_KEY}"
        )
        stream, handler, logger, previous = self._capture_logs("youtube_metadata")
        try:
            with patch.dict(os.environ, {"YOUTUBE_API_KEY": FAKE_YOUTUBE_KEY}), \
                 patch.object(youtube_metadata, "YOUTUBE_API_KEY", FAKE_YOUTUBE_KEY), \
                 patch("youtube_metadata.requests.Session.get",
                       side_effect=requests.ConnectionError(leaked)):
                with self.assertRaises(requests.RequestException) as caught:
                    youtube_metadata.get_youtube_metadata(
                        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                    )
        finally:
            logged = self._release_logs(stream, handler, logger, previous)

        import traceback
        formatted = "".join(traceback.format_exception(
            type(caught.exception), caught.exception, caught.exception.__traceback__
        ))
        self.assertNotIn(FAKE_YOUTUBE_KEY, str(caught.exception))
        self.assertNotIn(FAKE_YOUTUBE_KEY, repr(caught.exception))
        self.assertNotIn(FAKE_YOUTUBE_KEY, formatted)
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertNotIn(FAKE_YOUTUBE_KEY, logged)

    def test_timeout_does_not_leak_key(self):
        import youtube_metadata
        leaked = f"Read timed out. (read timeout=15) url=https://www.googleapis.com/youtube/v3/videos?id=dQw4w9WgXcQ&key={FAKE_YOUTUBE_KEY}"
        with patch.dict(os.environ, {"YOUTUBE_API_KEY": FAKE_YOUTUBE_KEY}), \
             patch.object(youtube_metadata, "YOUTUBE_API_KEY", FAKE_YOUTUBE_KEY), \
             patch("youtube_metadata.requests.Session.get",
                   side_effect=requests.Timeout(leaked)):
            with self.assertRaises(requests.RequestException) as caught:
                youtube_metadata.get_youtube_metadata(
                    "https://youtu.be/dQw4w9WgXcQ"
                )
        import traceback
        formatted = "".join(traceback.format_exception(
            type(caught.exception), caught.exception, caught.exception.__traceback__
        ))
        self.assertNotIn(FAKE_YOUTUBE_KEY, str(caught.exception))
        self.assertNotIn(FAKE_YOUTUBE_KEY, formatted)
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)

    def test_scrape_youtube_log_and_response_hide_key(self):
        import app as app_module
        leaked = RuntimeError(
            f"request failed for https://www.googleapis.com/youtube/v3/videos?key={FAKE_YOUTUBE_KEY}"
        )
        stream, handler, logger, previous = self._capture_logs("app")
        try:
            with patch.object(app_module, "get_youtube_metadata", side_effect=leaked):
                result = app_module.scrape_youtube(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                )
        finally:
            logged = self._release_logs(stream, handler, logger, previous)

        self.assertEqual(result["error"], "Erro ao processar vídeo do YouTube.")
        self.assertNotIn(FAKE_YOUTUBE_KEY, result["error"])
        self.assertNotIn(FAKE_YOUTUBE_KEY, logged)
        self.assertIn("RuntimeError", logged)
        self.assertNotIn("Traceback", logged)

    def test_metadata_endpoint_hides_key_on_timeout(self):
        import app as app_module
        leaked = requests.Timeout(
            f"timeout key={FAKE_YOUTUBE_KEY}"
        )
        client = app_module.app.test_client()
        stream, handler, logger, previous = self._capture_logs("app")
        try:
            with patch.object(app_module, "get_youtube_metadata", side_effect=leaked):
                response = client.post(
                    "/api/youtube-metadata",
                    json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                )
        finally:
            logged = self._release_logs(stream, handler, logger, previous)

        self.assertEqual(response.status_code, 500)
        body = response.get_data(as_text=True)
        self.assertNotIn(FAKE_YOUTUBE_KEY, body)
        self.assertEqual(
            response.get_json()["error"],
            "Erro ao consultar metadados do YouTube.",
        )
        self.assertNotIn(FAKE_YOUTUBE_KEY, logged)
