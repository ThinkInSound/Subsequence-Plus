"""api_feeds.py — On-the-fly external API polling for Pomski.

Provides a `DataFeeds` object pre-wired into the REPL namespace as `feeds`.
Call it from the browser command box or any REPL client at any time.

Usage
-----
    # Start a feed
    feeds.add("btc", "https://api.coinbase.com/v2/prices/BTC-USD/spot",
              interval=10, extract=lambda r: float(r["data"]["amount"]))

    # Feed with custom headers
    feeds.add("gh", "https://api.github.com/repos/python/cpython",
              headers={"Accept": "application/vnd.github+json"},
              extract=lambda r: r["stargazers_count"])

    # POST request
    feeds.add("custom", "https://api.example.com/query",
              method="POST", body={"filter": "all"},
              extract=lambda r: r["value"])

    # Stop a feed
    feeds.stop("btc")

    # See all active feeds and current values
    feeds

Values land in composition.data["feed_<key>"] for use inside patterns:

    @composition.pattern(channel=0, length=4)
    def ch1(p):
        price = composition.data.get("feed_btc", 0)
        pitch = int(48 + min(price / 1000, 36))
        p.note(pitch, beat=0)
"""

import asyncio
import json
import typing
import urllib.error
import urllib.request


class DataFeeds:
    """Manages named HTTP polling tasks that write results into composition.data.

    Each feed is an asyncio Task that runs on composition's event loop.
    Results are stored at composition.data["feed_<key>"].

    Designed to be called from the REPL (runs in a worker thread), so all
    task scheduling uses asyncio.run_coroutine_threadsafe.
    """

    def __init__(self, composition: typing.Any) -> None:
        self._composition = composition
        self._tasks: typing.Dict[str, asyncio.Task] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add(
        self,
        key: str,
        url: str,
        interval: float = 30,
        extract: typing.Optional[typing.Callable[[typing.Any], typing.Any]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        method: str = "GET",
        body: typing.Optional[typing.Any] = None,
    ) -> str:
        """Start (or restart) a named polling feed.

        Args:
            key:      Short name. Value lands in composition.data["feed_<key>"].
            url:      HTTP endpoint to poll.
            interval: Seconds between fetches (default 30).
            extract:  Callable(parsed_json) -> value. Stores full JSON if omitted.
            headers:  Optional dict of request headers.
            method:   HTTP method string (default "GET").
            body:     Optional body — serialised to JSON for the request.

        Returns a status string.
        """
        loop = self._composition._main_loop
        if loop is None or not loop.is_running():
            return "[feeds] ERROR: composition event loop not running. Call feeds.add() after composition.play() has started."

        # Cancel any existing task for this key first.
        existing = self._tasks.pop(key, None)
        if existing is not None:
            loop.call_soon_threadsafe(existing.cancel)

        # Schedule the new polling task on the event loop from this thread.
        async def _schedule() -> None:
            task = asyncio.ensure_future(
                self._poll_loop(key, url, interval, extract, headers, method, body)
            )
            self._tasks[key] = task

        asyncio.run_coroutine_threadsafe(_schedule(), loop).result(timeout=2)
        return f"[feeds] '{key}' started — polling every {interval}s → composition.data['feed_{key}']"

    def stop(self, key: str) -> str:
        """Cancel and remove a running feed by key."""
        loop = self._composition._main_loop
        task = self._tasks.pop(key, None)
        if task is None:
            return f"[feeds] '{key}' not found. Active: {list(self._tasks)}"
        if loop is not None:
            loop.call_soon_threadsafe(task.cancel)
        return f"[feeds] '{key}' stopped."

    def stop_all(self) -> str:
        """Cancel every active feed."""
        keys = list(self._tasks.keys())
        for key in keys:
            self.stop(key)
        return f"[feeds] stopped {len(keys)} feed(s): {keys}"

    # ------------------------------------------------------------------
    # Repr — typing `feeds` in the REPL shows live values
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        if not self._tasks:
            return "DataFeeds — no active feeds.\n  feeds.add(key, url, interval, extract)"
        lines = ["DataFeeds:"]
        for key in self._tasks:
            val = self._composition.data.get(f"feed_{key}", "<pending first fetch>")
            lines.append(f"  '{key}': {val!r}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _poll_loop(
        self,
        key: str,
        url: str,
        interval: float,
        extract: typing.Optional[typing.Callable[[typing.Any], typing.Any]],
        headers: typing.Optional[typing.Dict[str, str]],
        method: str,
        body: typing.Optional[typing.Any],
    ) -> None:
        data_key = f"feed_{key}"
        while True:
            try:
                raw = await asyncio.to_thread(self._fetch, url, method, headers, body)
                self._composition.data[data_key] = extract(raw) if extract else raw
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._composition.data[data_key] = f"ERROR: {exc}"
            await asyncio.sleep(interval)

    @staticmethod
    def _fetch(
        url: str,
        method: str,
        headers: typing.Optional[typing.Dict[str, str]],
        body: typing.Optional[typing.Any],
    ) -> typing.Any:
        encoded_body: typing.Optional[bytes] = None
        req_headers: typing.Dict[str, str] = headers.copy() if headers else {}

        if body is not None:
            encoded_body = json.dumps(body).encode()
            req_headers.setdefault("Content-Type", "application/json")

        req = urllib.request.Request(
            url,
            data=encoded_body,
            headers=req_headers,
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code} {exc.reason}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"URL error: {exc.reason}") from exc
