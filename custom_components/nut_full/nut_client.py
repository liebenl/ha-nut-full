"""
Minimal NUT protocol client — no external dependencies.
Implements just enough of the NUT protocol to:
  - LIST UPS
  - LIST VAR <ups>
"""
from __future__ import annotations

import socket
import logging

_LOGGER = logging.getLogger(__name__)

NUT_ERR = "ERR"


class NutError(Exception):
    """Raised when the NUT server returns an error response."""


class NutClient:
    """Simple synchronous NUT protocol client."""

    def __init__(
        self,
        host: str,
        port: int = 3493,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self._sock: socket.socket | None = None
        self._buf = b""  # raw receive buffer

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open TCP connection and authenticate."""
        self._sock = socket.create_connection(
            (self.host, self.port), timeout=self.timeout
        )
        self._sock.settimeout(self.timeout)
        self._buf = b""

        try:
            # Authenticate — send both in one write to avoid round-trip delays
            if self.username and self.password:
                self._sock.sendall(
                    f"USERNAME {self.username}\nPASSWORD {self.password}\n".encode()
                )
                # Consume the two OK responses
                ok1 = self._readline()
                ok2 = self._readline()
                _LOGGER.debug("NUT auth responses: %r %r", ok1, ok2)
                if ok1.startswith(NUT_ERR):
                    raise NutError(f"USERNAME rejected: {ok1}")
                if ok2.startswith(NUT_ERR):
                    raise NutError(f"PASSWORD rejected: {ok2}")
            elif self.username:
                self._sock.sendall(f"USERNAME {self.username}\n".encode())
                ok = self._readline()
                if ok.startswith(NUT_ERR):
                    raise NutError(f"USERNAME rejected: {ok}")
            elif self.password:
                self._sock.sendall(f"PASSWORD {self.password}\n".encode())
                ok = self._readline()
                if ok.startswith(NUT_ERR):
                    raise NutError(f"PASSWORD rejected: {ok}")
        except Exception:
            # connect() raised after the socket was opened — close it so we
            # don't leak the fd (the context manager's __exit__ is never
            # reached if __enter__ raises).
            self.disconnect()
            raise

    def disconnect(self) -> None:
        """Close the connection gracefully."""
        try:
            if self._sock:
                self._sock.sendall(b"LOGOUT\n")
        except Exception:
            pass
        finally:
            if self._sock:
                self._sock.close()
            self._sock = None
            self._buf = b""

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------

    def list_ups(self) -> dict[str, str]:
        """Return dict of {ups_name: description}."""
        lines = self._list("LIST UPS")
        result = {}
        for line in lines:
            # UPS <name> "<description>"
            parts = line.split(" ", 2)
            if len(parts) >= 2:
                name = parts[1]
                desc = parts[2].strip('"') if len(parts) > 2 else ""
                result[name] = desc
        return result

    def list_vars(self, ups_name: str) -> dict[str, str]:
        """Return dict of {variable: value} for the given UPS."""
        lines = self._list(f"LIST VAR {ups_name}")
        result = {}
        for line in lines:
            # VAR <ups> <variable> "<value>"
            parts = line.split(" ", 3)
            if len(parts) >= 4:
                var = parts[2]
                value = parts[3].strip('"')
                result[var] = value
        return result

    # ------------------------------------------------------------------
    # Protocol primitives
    # ------------------------------------------------------------------

    def _readline(self) -> str:
        """Read one newline-terminated line from the socket."""
        if self._sock is None:
            raise NutError("Not connected")
        while b"\n" not in self._buf:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise NutError("Connection closed by server")
            self._buf += chunk
        idx = self._buf.index(b"\n")
        line = self._buf[:idx].decode("utf-8", errors="replace").rstrip("\r")
        self._buf = self._buf[idx + 1:]
        _LOGGER.debug("NUT << %s", line)
        return line

    def _list(self, cmd: str) -> list[str]:
        """Send a LIST command and collect lines until END <cmd>."""
        _LOGGER.debug("NUT >> %s", cmd)
        self._sock.sendall((cmd + "\n").encode("utf-8"))

        end_prefix = f"END {cmd}"
        lines: list[str] = []

        first = self._readline()
        if first.startswith(NUT_ERR):
            raise NutError(f"NUT error for '{cmd}': {first}")
        if not first.startswith("BEGIN"):
            raise NutError(f"Unexpected response to '{cmd}': {first!r}")

        while True:
            line = self._readline()
            if line.startswith(end_prefix):
                break
            if line.startswith(NUT_ERR):
                raise NutError(f"NUT error mid-list: {line}")
            lines.append(line)

        return lines

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "NutClient":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()
