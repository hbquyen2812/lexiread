"""Check the curated study catalog without archiving lesson content.

Default: validate the local catalog, without network access.
--crawl: check at most 60 catalog URLs, respecting robots.txt and redirects.
--self-test: run offline policy checks. No arbitrary URL or output-path option.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "study_sources.json"
REPORT = ROOT / "data" / "public_sources" / "foundation_crawl.json"
AGENT = "LexiReadStudySourcesBot"
USER_AGENT = AGENT + "/1.0 (metadata-only; manual catalog check)"
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
KINDS = {"grammar", "vocabulary", "dictionary", "ielts", "toeic"}
MAX_ITEMS = 60
MAX_REDIRECTS = 4
MAX_HTML_BYTES = 256 * 1024
MAX_ROBOTS_BYTES = 256 * 1024
MAX_PDF_BYTES = 1024
SOCKET_TIMEOUT = 10
READ_DEADLINE = 20
RUN_DEADLINE = 480
MIN_DELAY = 1.5
MAX_DELAY = 10

# Exact official hosts and relevant public paths. No wildcard subdomains.
ALLOWED = {
    "learnenglish.britishcouncil.org": ("/free-resources/",),
    "takeielts.britishcouncil.org": ("/prepare/",),
    "www.cambridgeenglish.org": ("/learning-english/activities-for-learners/",),
    "dictionary.cambridge.org": ("/dictionary/", "/grammar/", "/us/grammar/"),
    "www.oxfordlearnersdictionaries.com": (
        "/wordlists/", "/definition/english/", "/external/pdf/wordlists/",
    ),
    "downloads.bbc.co.uk": ("/learningenglish/",),
    "learningenglish.voanews.com": ("/p/",),
    "ielts.org": ("/take-a-test/preparation-resources/sample-test-questions/",),
    "www.ielts.org": ("/take-a-test/preparation-resources/sample-test-questions/",),
    "www.ets.org": ("/toeic/test-takers/", "/content/dam/ets-org/pdfs/toeic/", "/pdfs/toeic/"),
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class PolicyError(ValueError):
    pass


def safe_url(url: str, *, robots: bool = False) -> str:
    if not isinstance(url, str) or len(url) > 2048:
        raise PolicyError("URL must be a string of at most 2048 characters")
    if any(ord(c) < 33 or ord(c) == 127 for c in url) or "\\" in url:
        raise PolicyError("Whitespace, control characters and backslashes are forbidden")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as exc:
        raise PolicyError("Malformed URL") from exc
    if parts.scheme != "https" or parts.hostname not in ALLOWED:
        raise PolicyError("Only exact allowlisted HTTPS hosts are permitted")
    if parts.username or parts.password or port not in (None, 443):
        raise PolicyError("Credentials and nonstandard ports are forbidden")
    if parts.query or parts.fragment:
        raise PolicyError("Catalog probes do not accept query strings or fragments")
    decoded = parts.path
    for _ in range(3):
        decoded = unquote(decoded)
    if decoded != unquote(decoded):
        raise PolicyError("Excessive URL encoding is forbidden")
    if any(ord(c) < 32 for c in decoded) or "\\" in decoded:
        raise PolicyError("Encoded controls and backslashes are forbidden")
    if any(segment in (".", "..") for segment in decoded.split("/")):
        raise PolicyError("Path traversal is forbidden")
    if robots:
        if decoded != "/robots.txt":
            raise PolicyError("Robots redirects must remain robots.txt on an allowed host")
    elif not any(decoded.startswith(prefix) for prefix in ALLOWED[parts.hostname]):
        raise PolicyError("Path is outside the allowlisted learning-resource paths")
    return url


def validate_catalog(data: dict) -> list[dict]:
    if data.get("version") != 1:
        raise ValueError("Catalog version must be 1")
    date.fromisoformat(data["checked_at"])
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        raise ValueError(f"Catalog must contain between 1 and {MAX_ITEMS} items")
    seen_ids, seen_urls = set(), set()
    required = {"id", "title", "provider", "url", "levels", "kind", "description_vi"}
    for item in items:
        if not isinstance(item, dict) or set(item) != required:
            raise ValueError("Each source must have exactly the documented metadata fields")
        identifier = item["id"]
        if not isinstance(identifier, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
            raise ValueError("Source IDs must be lowercase slug strings")
        safe_url(item["url"])
        if identifier in seen_ids or item["url"] in seen_urls:
            raise ValueError("Source IDs and URLs must be unique")
        seen_ids.add(identifier)
        seen_urls.add(item["url"])
        if item["kind"] not in KINDS:
            raise ValueError(f"Unknown resource kind: {identifier}")
        levels = item["levels"]
        if not isinstance(levels, list) or not levels or any(v not in LEVELS for v in levels):
            raise ValueError(f"Invalid CEFR levels: {identifier}")
        if levels != [level for level in LEVELS if level in levels]:
            raise ValueError(f"Levels must be unique and ordered A1 through C2: {identifier}")
        for field in ("title", "provider", "description_vi"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError(f"Missing {field}: {identifier}")
        if len(item["description_vi"]) > 500:
            raise ValueError(f"Description must be brief metadata: {identifier}")
    return items


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.finished = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title" and not self.finished:
            self.in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title" and self.in_title:
            self.in_title = False
            self.finished = True

    def handle_data(self, data):
        if self.in_title:
            self.parts.append(data[:500])


class Client:
    def __init__(self):
        self.opener = build_opener(NoRedirect())
        self.robots = {}
        self.last_request = {}
        self.started = time.monotonic()

    def wait_for_host(self, host: str, delay: float = MIN_DELAY):
        if time.monotonic() - self.started >= RUN_DEADLINE:
            raise PolicyError("Overall crawl deadline reached")
        remaining = delay - (time.monotonic() - self.last_request.get(host, 0))
        if remaining > 0:
            time.sleep(remaining)
        self.last_request[host] = time.monotonic()

    def wire(self, url: str, robots: bool) -> tuple[dict, bytes]:
        """One bounded request, with redirects disabled and no retry on errors."""
        request = Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/plain" if robots else "text/html,application/pdf;q=0.9",
            "Accept-Encoding": "identity",
        })
        try:
            response = self.opener.open(request, timeout=SOCKET_TIMEOUT)
        except HTTPError as exc:
            result = {
                "http_status": exc.code,
                "content_type": exc.headers.get_content_type(),
                "location": exc.headers.get("Location"),
                "detail": f"HTTP {exc.code}; no retry or error-body download",
            }
            exc.close()
            return result, b""
        except (URLError, TimeoutError, OSError) as exc:
            return {"http_status": None, "detail": f"Network request failed: {type(exc).__name__}"}, b""
        with response:
            mime = response.headers.get_content_type()
            result = {
                "http_status": response.status,
                "content_type": mime,
                "content_encoding": response.headers.get("Content-Encoding", "identity"),
                "charset": response.headers.get_content_charset() or "utf-8",
            }
            if result["content_encoding"].lower() not in ("identity", ""):
                result["detail"] = "Unexpected compression; content not decoded or verified"
                return result, b""
            if not robots and mime not in ("text/html", "application/xhtml+xml", "application/pdf"):
                result["detail"] = "Unexpected MIME type; content not downloaded"
                return result, b""
            cap = MAX_ROBOTS_BYTES if robots else MAX_PDF_BYTES if mime == "application/pdf" else MAX_HTML_BYTES
            deadline = time.monotonic() + READ_DEADLINE
            chunks, count = [], 0
            try:
                while count <= cap:
                    if time.monotonic() > deadline:
                        result["detail"] = "Body read deadline reached; content not verified"
                        return result, b""
                    chunk = response.read(min(8192, cap + 1 - count))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    count += len(chunk)
            except (TimeoutError, OSError) as exc:
                result["detail"] = f"Body read failed: {type(exc).__name__}"
                return result, b""
            body = b"".join(chunks)
            result["bytes_read"] = len(body)
            result["body_truncated"] = len(body) > cap
            return result, body[:cap]

    def fetch(self, url: str, *, robots: bool = False) -> tuple[dict, bytes]:
        original, visited, redirects = url, set(), []
        try:
            for hop in range(MAX_REDIRECTS + 1):
                safe_url(url, robots=robots)
                if url in visited:
                    raise PolicyError("Redirect loop")
                visited.add(url)
                host = urlsplit(url).hostname
                delay = MIN_DELAY
                if not robots:
                    policy = self.robot_policy(host)
                    delay = policy["delay_seconds"]
                    if policy["status"] != "ready":
                        return {"status": "blocked_robots_unavailable", "final_url": url,
                                "detail": policy["detail"], "redirects": redirects}, b""
                    if not policy["parser"].can_fetch(AGENT, url):
                        return {"status": "blocked_robots", "final_url": url,
                                "detail": "robots.txt disallows this bot or resource path",
                                "redirects": redirects}, b""
                self.wait_for_host(host, delay)
                result, body = self.wire(url, robots)
                result["final_url"] = url
                result["redirects"] = list(redirects)
                status = result.get("http_status")
                if status in (301, 302, 303, 307, 308):
                    location = result.pop("location", None)
                    if not location:
                        raise PolicyError("Redirect has no Location header")
                    if hop == MAX_REDIRECTS:
                        raise PolicyError("Redirect limit reached")
                    destination = urljoin(url, location)
                    redirects.append({"from": url, "to": destination, "http_status": status})
                    safe_url(destination, robots=robots)
                    url = destination
                    continue
                result.pop("location", None)
                result["status"] = "fetched" if status is not None and 200 <= status < 300 else "http_error" if status else "network_error"
                return result, body
        except PolicyError as exc:
            return {"status": "policy_blocked", "final_url": url, "detail": str(exc),
                    "redirects": redirects, "requested_url": original}, b""
        raise AssertionError("Redirect loop must return or raise")

    def robot_policy(self, host: str) -> dict:
        if host in self.robots:
            return self.robots[host]
        url = f"https://{host}/robots.txt"
        result, body = self.fetch(url, robots=True)
        policy = {"host": host, "url": url, "status": "unavailable",
                  "delay_seconds": MIN_DELAY, "check": result,
                  "detail": "robots.txt could not be checked; fail closed"}
        parser = RobotFileParser(url)
        if result.get("http_status") in (404, 410):
            parser.parse(["User-agent: *", "Allow: /"])
            policy.update(status="ready", detail="robots.txt not found; no published restrictions")
        elif (result.get("status") == "fetched" and body and not result.get("body_truncated")
              and result.get("content_type") in ("text/plain", "text/html")):
            decoded = body.decode("utf-8-sig", errors="replace")
            if "<html" not in decoded.lower() and "<!doctype" not in decoded.lower():
                parser.parse(decoded.splitlines())
                policy.update(status="ready", detail="robots.txt parsed")
        elif result.get("status") == "fetched" and result.get("bytes_read") == 0:
            parser.parse(["User-agent: *", "Allow: /"])
            policy.update(status="ready", detail="Empty robots.txt; no published restrictions")
        if policy["status"] == "ready":
            delay = parser.crawl_delay(AGENT) or parser.crawl_delay("*") or MIN_DELAY
            rate = parser.request_rate(AGENT) or parser.request_rate("*")
            if rate and rate.requests:
                delay = max(delay, rate.seconds / rate.requests)
            policy["delay_seconds"] = max(MIN_DELAY, delay)
            if delay > MAX_DELAY:
                policy.update(status="unavailable", detail="Publisher request interval exceeds this short-run crawler's limit; skipped")
        policy["parser"] = parser
        self.robots[host] = policy
        return policy

    def probe(self, item: dict) -> dict:
        result, body = self.fetch(item["url"])
        record = {"id": item["id"], "url": item["url"], "checked_at": now(), **result}
        if result["status"] != "fetched":
            return record
        mime = result.get("content_type")
        if mime == "application/pdf" and body.startswith(b"%PDF-"):
            record.update(status="ok", verification="HTTP success, PDF MIME and file signature; header probe only")
        elif mime in ("text/html", "application/xhtml+xml") and body:
            parser = TitleParser()
            try:
                parser.feed(body.decode(result.get("charset", "utf-8"), errors="replace"))
            except (LookupError, ValueError):
                record.update(status="unverified_content", detail="HTML could not be decoded")
                return record
            title = " ".join("".join(parser.parts).split())[:300]
            denied = any(phrase in title.lower() for phrase in (
                "access denied", "just a moment", "attention required", "robot check", "page not found",
            ))
            if title and parser.finished and not denied:
                record.update(status="ok", title=title,
                              verification="HTTP success, HTML MIME and completed page title; interactions not tested")
            else:
                record.update(status="unverified_content", title=title,
                              detail="No complete title, or page appears to be an error/challenge")
        else:
            record.update(status="unverified_content", detail=result.get("detail", "MIME or file signature did not match a readable resource"))
        record.pop("charset", None)
        return record


def self_test():
    """Offline tests exercise safety behavior without contacting any publisher."""
    import copy
    import unittest
    from unittest.mock import patch

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    class PolicyTests(unittest.TestCase):
        def test_catalog_and_coverage(self):
            items = validate_catalog(catalog)
            self.assertGreaterEqual(len(items), 30)
            self.assertEqual({item["kind"] for item in items}, KINDS)
            self.assertEqual({v for item in items for v in item["levels"]}, set(LEVELS))

        def test_unsafe_urls(self):
            for url in (
                "http://www.ets.org/toeic/test-takers/prepare.html",
                "https://www.ets.org.evil.example/toeic/test-takers/prepare.html",
                "https://me:secret@www.ets.org/toeic/test-takers/prepare.html",
                "https://127.0.0.1/toeic/test-takers/prepare.html",
                "https://www.ets.org:444/toeic/test-takers/prepare.html",
                "https://www.ets.org/toeic/test-takers/%252e%252e/private",
                "https://www.ets.org/toeic/test-takers/%0asecret",
                "https://www.ets.org/admin/",
                "https://www.ets.org/toeic/test-takers/prepare.html?url=http://localhost",
            ):
                with self.subTest(url=url), self.assertRaises(PolicyError):
                    safe_url(url)

        def test_duplicate_and_bad_level_rejected(self):
            altered = copy.deepcopy(catalog)
            altered["items"].append(altered["items"][0])
            with self.assertRaises(ValueError):
                validate_catalog(altered)
            altered = copy.deepcopy(catalog)
            altered["items"][0]["levels"] = ["C3"]
            with self.assertRaises(ValueError):
                validate_catalog(altered)

        def test_robots_denial_never_fetches_resource(self):
            client = Client()
            with patch.object(client, "wait_for_host"), patch.object(client, "wire", return_value=(
                {"http_status": 200, "content_type": "text/plain", "bytes_read": 30}, b"User-agent: *\nDisallow: /\n"
            )) as wire:
                result = client.probe(catalog["items"][0])
            self.assertEqual(result["status"], "blocked_robots")
            self.assertEqual(wire.call_count, 1)
            self.assertTrue(wire.call_args.args[0].endswith("/robots.txt"))

        def test_robots_403_fails_closed_without_retry(self):
            client = Client()
            with patch.object(client, "wait_for_host"), patch.object(client, "wire", return_value=(
                {"http_status": 403}, b""
            )) as wire:
                result = client.probe(catalog["items"][0])
            self.assertEqual(result["status"], "blocked_robots_unavailable")
            self.assertEqual(wire.call_count, 1)

        def test_redirect_cannot_escape_allowlist(self):
            client = Client()
            with patch.object(client, "wait_for_host"), patch.object(client, "wire", side_effect=[
                ({"http_status": 404}, b""),
                ({"http_status": 302, "location": "http://127.0.0.1/private"}, b""),
            ]) as wire:
                result = client.probe(catalog["items"][0])
            self.assertEqual(result["status"], "policy_blocked")
            self.assertEqual(wire.call_count, 2)

        def test_redirect_target_is_checked_against_robots(self):
            client = Client()
            with patch.object(client, "wait_for_host"), patch.object(client, "wire", side_effect=[
                ({"http_status": 200, "content_type": "text/plain"},
                 b"User-agent: *\nDisallow: /free-resources/private\n"),
                ({"http_status": 302, "location": "/free-resources/private"}, b""),
            ]) as wire:
                result = client.probe(catalog["items"][0])
            self.assertEqual(result["status"], "blocked_robots")
            self.assertEqual(wire.call_count, 2)

        def test_binary_robots_response_fails_closed(self):
            client = Client()
            with patch.object(client, "wait_for_host"), patch.object(client, "wire", return_value=(
                {"http_status": 200, "content_type": "application/pdf"}, b"%PDF-1.7"
            )) as wire:
                result = client.probe(catalog["items"][0])
            self.assertEqual(result["status"], "blocked_robots_unavailable")
            self.assertEqual(wire.call_count, 1)

        def test_pdf_mime_without_signature_not_verified(self):
            client = Client()
            with patch.object(client, "fetch", return_value=(
                {"status": "fetched", "http_status": 200, "content_type": "application/pdf"}, b"<html>Denied</html>"
            )):
                result = client.probe(catalog["items"][-1])
            self.assertEqual(result["status"], "unverified_content")

    outcome = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PolicyTests))
    if not outcome.wasSuccessful():
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--crawl", action="store_true", help="Check catalog sources and replace the fixed metadata report")
    mode.add_argument("--validate", action="store_true", help="Validate catalog only (the default)")
    mode.add_argument("--self-test", action="store_true", help="Run offline validation and crawler policy tests")
    parser.add_argument("--limit", type=int, default=MAX_ITEMS, help="Maximum catalog entries to check (1–60)")
    args = parser.parse_args()
    if not 1 <= args.limit <= MAX_ITEMS:
        parser.error("--limit must be between 1 and 60")
    if args.self_test:
        self_test()
        return
    raw = CATALOG.read_bytes()
    data = json.loads(raw.decode("utf-8"))
    items = validate_catalog(data)
    counts = dict(sorted(Counter(item["kind"] for item in items).items()))
    if not args.crawl:
        print(json.dumps({"valid": True, "items": len(items), "kinds": counts, "levels": list(LEVELS)}, ensure_ascii=False))
        return
    started_at = now()
    client = Client()
    records = []
    for item in items[:args.limit]:
        result = client.probe(item)
        records.append(result)
        print(f"{item['id']}: {result['status']}", flush=True)
    statuses = dict(sorted(Counter(record["status"] for record in records).items()))
    report = {
        "version": 1,
        "catalog_checked_at": data["checked_at"],
        "catalog_sha256": hashlib.sha256(raw).hexdigest(),
        "started_at": started_at,
        "completed_at": now(),
        "user_agent": USER_AGENT,
        "policy": {
            "metadata_only": True, "stored_response_bodies": False,
            "allowed_hosts": sorted(ALLOWED), "max_items": MAX_ITEMS,
            "requested_limit": args.limit, "catalog_items": len(items),
            "max_redirects": MAX_REDIRECTS, "max_html_bytes": MAX_HTML_BYTES,
            "max_pdf_bytes": MAX_PDF_BYTES, "max_robots_bytes": MAX_ROBOTS_BYTES,
            "socket_timeout_seconds": SOCKET_TIMEOUT, "body_deadline_seconds": READ_DEADLINE,
            "crawl_deadline_seconds": RUN_DEADLINE, "minimum_delay_seconds": MIN_DELAY,
            "robots_failure_policy": "fail_closed_except_404_or_410",
            "retries": 0,
        },
        "summary": {"checked": len(records), "not_checked": len(items) - len(records), "statuses": statuses},
        "robots": [{key: value for key, value in policy.items() if key != "parser"}
                   for policy in client.robots.values()],
        "items": records,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    temporary = REPORT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(REPORT)
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
