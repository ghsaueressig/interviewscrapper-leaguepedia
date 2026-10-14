"""Run from backend/: python -m unittest discover -s tests -v"""
import unittest
from unittest.mock import patch, MagicMock

from security import UnsafeURLError, validate_url, resolve_public_ip, safe_get


class URLSecurityTests(unittest.TestCase):
    def test_approved_sources(self):
        for host in ("maisesports.com.br", "www.sheepesports.com", "pichauarena.com.br", "itatiaia.com.br"):
            self.assertEqual(validate_url(f"https://{host}/article"), f"https://{host}/article")

    def test_rejected_urls(self):
        invalid = (
            "http://127.0.0.1/", "http://169.254.169.254/", "http://localhost/",
            "https://maisesports.com.br.evil.example/", "https://evil.example/",
            "https://user:pass@maisesports.com.br/", "file:///etc/passwd",
            "https://maisesports.com.br:8080/", "https://other.maisesports.com.br/",
            "https://maisesports.com.br/\nX-Test: bad", "https://maisesports.com.br:bad/",
        )
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(UnsafeURLError):
                validate_url(url)

    @patch("security.socket.getaddrinfo")
    def test_dns_private_or_mixed_is_rejected(self, lookup):
        lookup.return_value = [(2, 1, 6, "", ("8.8.8.8", 443)),
                               (2, 1, 6, "", ("127.0.0.1", 443))]
        with self.assertRaises(UnsafeURLError):
            resolve_public_ip("maisesports.com.br", 443)

    @patch("security.socket.getaddrinfo")
    def test_dns_public_ip(self, lookup):
        lookup.return_value = [(2, 1, 6, "", ("8.8.8.8", 443))]
        self.assertEqual(resolve_public_ip("maisesports.com.br", 443), "8.8.8.8")

    @patch("security.requests.Session.get")
    def test_redirect_to_unapproved_host_is_blocked(self, get):
        response = MagicMock()
        response.status_code = 302
        response.headers = {"Location": "http://127.0.0.1/private"}
        get.return_value = response
        with self.assertRaises(UnsafeURLError):
            safe_get("https://maisesports.com.br/article")
        self.assertEqual(get.call_count, 1)

    @patch("security.requests.Session.get")
    def test_response_size_limit(self, get):
        response = MagicMock()
        response.status_code = 200
        response.iter_content.return_value = iter([b"123456789"])
        get.return_value = response
        with self.assertRaises(UnsafeURLError):
            safe_get("https://maisesports.com.br/article", max_bytes=4)



if __name__ == "__main__":
    unittest.main()
