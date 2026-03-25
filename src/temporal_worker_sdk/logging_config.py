"""Structured logging: JSON option, Temporal context fields, no payloads at INFO."""

from __future__ import annotations

import contextvars
import hashlib
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Mapping

from temporal_worker_sdk.config import WorkerConfig

# Log lines: avoid echoing credentials if TEMPORAL_ADDRESS ever uses URI userinfo.
_LOG_TARGET_MAX_LEN = 128

_LOG_CONTEXT: contextvars.ContextVar[dict[str, str]] = contextvars.ContextVar(
    "temporal_worker_sdk_log_ctx",
    default={},
)


def log_context_set(**fields: str) -> contextvars.Token[dict[str, str]]:
    cur = dict(_LOG_CONTEXT.get())
    cur.update({k: v for k, v in fields.items() if v})
    return _LOG_CONTEXT.set(cur)


def log_context_reset(token: contextvars.Token[dict[str, str]]) -> None:
    _LOG_CONTEXT.reset(token)


def safe_temporal_target_for_log(address: str) -> str:
    """
    Return a monitoring-safe form of the gRPC target (host:port or URL).

    Strips ``user:pass@`` if present and truncates very long values so logs stay parseable
    without leaking credentials.
    """
    s = address.strip()
    if not s:
        return "(empty)"
    if "@" in s:
        s = s.rsplit("@", 1)[-1]
    for prefix in ("grpc://", "http://", "https://"):
        low = s[: len(prefix)].lower()
        if low == prefix:
            s = s[len(prefix) :]
            break
    if len(s) > _LOG_TARGET_MAX_LEN:
        digest = hashlib.sha256(s.encode("utf-8", errors="replace")).hexdigest()[:8]
        return f"{s[:_LOG_TARGET_MAX_LEN]}…(len={len(s)},id8={digest})"
    return s


def _payload_preview(value: object, *, max_len: int = 64) -> str:
    text = repr(value)
    if len(text) <= max_len:
        return text
    digest = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:12]
    return f"{text[:max_len]}…(len={len(text)},sha256_12={digest})"


class TemporalContextFilter(logging.Filter):
    """Attach worker identity and optional per-task context to every log record."""

    def __init__(self, cfg: WorkerConfig) -> None:
        super().__init__()
        self._cfg = cfg

    def filter(self, record: logging.LogRecord) -> bool:
        record.worker_task_queue = self._cfg.task_queue
        record.worker_namespace = self._cfg.temporal_namespace
        if self._cfg.worker_role:
            record.worker_role = self._cfg.worker_role
        if self._cfg.temporal_identity:
            record.worker_identity = self._cfg.temporal_identity
        for key, val in _LOG_CONTEXT.get().items():
            setattr(record, key, val)
        return True


class JsonLogFormatter(logging.Formatter):
    """One JSON object per line; includes dynamic attributes set by TemporalContextFilter."""

    _RESERVED = frozenset(
        {
            "name",
            "msg",
            "args",
            "created",
            "filename",
            "funcName",
            "levelname",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "message",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "thread",
            "threadName",
            "exc_info",
            "exc_text",
            "stack_info",
            "taskName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        payload: dict[str, Any] = {
            "ts": ts,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, val in record.__dict__.items():
            if key in self._RESERVED or key.startswith("_"):
                continue
            if isinstance(val, str | int | float | bool) or val is None:
                payload[key] = val
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, separators=(",", ":"))


def configure_worker_logging(cfg: WorkerConfig) -> None:
    """
    Configure root logging for the worker process.

    INFO default: workflow/activity *payloads* are not included (see README).
    DEBUG with TEMPORAL_WORKER_LOG_PAYLOADS_DEBUG may log truncated previews.
    """
    level = logging.DEBUG if cfg.log_payloads_debug else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    if cfg.log_json:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(levelname)s %(name)s "
                "[queue=%(worker_task_queue)s ns=%(worker_namespace)s] %(message)s"
            )
        )
    handler.addFilter(TemporalContextFilter(cfg))
    root.addHandler(handler)


def describe_payload_logging_policy(cfg: WorkerConfig) -> Mapping[str, str]:
    """Short strings for docs / debug help."""
    return {
        "info": "Workflow and activity *arguments* are omitted at INFO (types/names/ids only).",
        "debug_payloads": (
            "When TEMPORAL_WORKER_LOG_PAYLOADS_DEBUG is truthy, DEBUG logs may include "
            f"truncated repr (max 64 chars) plus length and sha256 prefix: {_payload_preview('example')!r}."
        ),
    }
