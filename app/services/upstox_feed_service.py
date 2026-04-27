import asyncio
import json
from datetime import datetime, timezone
from threading import Event, Lock, Thread
from typing import Any, Dict, Optional

import requests
import websockets
from google.protobuf.json_format import MessageToDict

from app.core.config import UPSTOX_TOKEN_FILE
from app.proto.market_data_pb2 import FeedResponse
from app.services.upstox_auth_service import get_token_status, load_token
from app.state.market_state import LIVE_PRICES

_UPSTOX_AUTHORIZE_URL = "https://api.upstox.com/v3/feed/market-data-feed/authorize"
_NIFTY50_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"


class UpstoxFeedService:
    def __init__(self) -> None:
        self._lock = Lock()
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._state: Dict[str, Any] = {
            "running": False,
            "started_at": None,
            "stopped_at": None,
            "last_message_at": None,
            "last_update_at": None,
            "last_error": None,
            "last_warning": None,
            "instrument_key": _NIFTY50_INSTRUMENT_KEY,
            "token_file": str(UPSTOX_TOKEN_FILE or "upstox_token.json"),
        }

    def _status_with_live_price(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        base_snapshot = dict(snapshot)
        key = _NIFTY50_INSTRUMENT_KEY
        live = LIVE_PRICES.get(key)
        base_snapshot["live_price"] = {
            "instrument_key": key,
            "status": "live" if live else "waiting_for_data",
            "ltp": (live or {}).get("ltp"),
            "timestamp": (live or {}).get("timestamp"),
        }
        base_snapshot["token"] = get_token_status()
        return base_snapshot

    def status(self) -> Dict[str, Any]:
        with self._lock:
            snapshot = dict(self._state)
        return self._status_with_live_price(snapshot)

    def start(self) -> Dict[str, Any]:
        token_status = get_token_status()
        if not token_status.get("ready"):
            reason = token_status.get("reason", "token_not_ready")
            raise RuntimeError(
                f"Cannot start feed: token not ready ({reason}). "
                "Complete Upstox OAuth callback to create/refresh token."
            )

        with self._lock:
            if self._state["running"]:
                return self._status_with_live_price(dict(self._state))
            self._state["running"] = True
            self._state["started_at"] = datetime.now(timezone.utc).isoformat()
            self._state["stopped_at"] = None
            self._state["last_error"] = None
            self._state["last_warning"] = None

        self._stop_event.clear()
        self._thread = Thread(target=self._run_loop, daemon=True, name="upstox-feed")
        self._thread.start()
        return self.status()

    def stop(self) -> Dict[str, Any]:
        self._stop_event.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=5)
        self._thread = None

        with self._lock:
            self._state["running"] = False
            self._state["stopped_at"] = datetime.now(timezone.utc).isoformat()
        return self.status()

    def _set_error(self, message: str) -> None:
        with self._lock:
            self._state["last_error"] = message

    def _set_warning(self, message: str) -> None:
        with self._lock:
            self._state["last_warning"] = message

    def _mark_message(self) -> None:
        with self._lock:
            self._state["last_message_at"] = datetime.now(timezone.utc).isoformat()

    def _mark_update(self) -> None:
        with self._lock:
            self._state["last_update_at"] = datetime.now(timezone.utc).isoformat()

    def _load_access_token(self) -> str:
        token_status = get_token_status()
        if not token_status.get("ready"):
            reason = token_status.get("reason", "token_not_ready")
            raise RuntimeError(f"Token not ready: {reason}")

        token_data = load_token() or {}
        token = token_data.get("access_token")
        if not token:
            raise RuntimeError("Token data missing access_token")
        return str(token)

    def _authorize_feed_url(self, access_token: str) -> str:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Api-Version": "2.0",
        }
        response = requests.get(_UPSTOX_AUTHORIZE_URL, headers=headers, timeout=15)
        if response.status_code >= 400:
            raise RuntimeError(
                f"Upstox feed authorize failed: HTTP {response.status_code} - {response.text}"
            )

        payload = response.json()
        data = payload.get("data") if isinstance(payload, dict) else None
        ws_url = None
        if isinstance(data, dict):
            ws_url = data.get("authorized_redirect_uri") or data.get("authorizedRedirectUri")

        if not ws_url:
            raise RuntimeError(
                "Upstox feed authorize response did not contain authorized websocket URL."
            )
        return str(ws_url)

    def _run_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                asyncio.run(self._ws_worker())
            except Exception as exc:
                self._set_error(str(exc))

            if self._stop_event.is_set():
                break
            self._stop_event.wait(timeout=3)

        with self._lock:
            self._state["running"] = False
            if self._state.get("stopped_at") is None:
                self._state["stopped_at"] = datetime.now(timezone.utc).isoformat()

    async def _ws_worker(self) -> None:
        access_token = self._load_access_token()
        ws_url = self._authorize_feed_url(access_token)

        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20, max_size=None) as ws:
            subscribe_payload = {
                "guid": "nifty50-paper-feed",
                "method": "sub",
                "data": {
                    "mode": "ltpc",
                    "instrumentKeys": [_NIFTY50_INSTRUMENT_KEY],
                },
            }
            await ws.send(json.dumps(subscribe_payload).encode("utf-8"))

            async for message in ws:
                if self._stop_event.is_set():
                    break
                self._mark_message()
                self._handle_feed_message(message)

    def _handle_feed_message(self, message: Any) -> None:
        key = _NIFTY50_INSTRUMENT_KEY

        # Upstox market feed uses protobuf frames. If decoding fails, surface a clear error.
        parsed_dict: Optional[Dict[str, Any]] = None
        try:
            if isinstance(message, (bytes, bytearray)):
                parsed = FeedResponse()
                parsed.ParseFromString(bytes(message))
                parsed_dict = MessageToDict(parsed, preserving_proto_field_name=True)
            elif isinstance(message, str):
                parsed_dict = json.loads(message)
            else:
                self._set_warning(f"Unsupported feed payload type: {type(message)}")
                return
        except Exception as exc:
            self._set_error(f"Feed payload decode failed: {exc}")
            return

        feeds = (parsed_dict or {}).get("feeds")
        if not isinstance(feeds, dict):
            self._set_warning("Feed payload missing 'feeds' map; waiting for price updates.")
            return

        entry = feeds.get(key)
        if not isinstance(entry, dict):
            return

        ltp = self._extract_ltp(entry)
        if ltp is None:
            self._set_warning("Feed message received for NIFTY50 but LTP was not present.")
            return

        LIVE_PRICES[key] = {
            "ltp": float(ltp),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw": entry,
        }
        self._mark_update()

    @staticmethod
    def _extract_ltp(feed_entry: Dict[str, Any]) -> Optional[float]:
        candidates = []

        ltpc = feed_entry.get("ltpc")
        if isinstance(ltpc, dict):
            candidates.append(ltpc.get("ltp"))

        full_feed = feed_entry.get("fullFeed") or feed_entry.get("full_feed")
        if isinstance(full_feed, dict):
            index_ff = full_feed.get("indexFF") or full_feed.get("index_ff")
            if isinstance(index_ff, dict):
                index_ltpc = index_ff.get("ltpc")
                if isinstance(index_ltpc, dict):
                    candidates.append(index_ltpc.get("ltp"))

            market_ff = full_feed.get("marketFF") or full_feed.get("market_ff")
            if isinstance(market_ff, dict):
                market_ltpc = market_ff.get("ltpc")
                if isinstance(market_ltpc, dict):
                    candidates.append(market_ltpc.get("ltp"))

        for candidate in candidates:
            if candidate is None:
                continue
            try:
                return float(candidate)
            except (TypeError, ValueError):
                continue
        return None
