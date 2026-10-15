"""Local-only web adapter for the existing simulated Gauntlet scenarios."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from gauntlet_demo import (
    PERMISSION_PROFILES,
    permission_profile_tools,
    run_prompt_injection_scenarios,
)


WEB_ROOT = Path(__file__).with_name("web")


def build_simulation_payload(profile: str = "read_only") -> dict[str, Any]:
    """Return JSON-ready data from the existing local simulation logic."""
    scenarios = run_prompt_injection_scenarios(permission_profile=profile)
    return {
        "simulation_only": True,
        "armorIQ_enforcement": False,
        "profile": profile,
        "profiles": {
            name: sorted(permission_profile_tools(name))
            for name in PERMISSION_PROFILES
        },
        "scenarios": [asdict(scenario) for scenario in scenarios],
    }


class GauntletHandler(SimpleHTTPRequestHandler):
    """Serve the static dashboard and one local simulation endpoint."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(WEB_ROOT), **kwargs)

    def do_GET(self) -> None:
        if urlsplit(self.path).path != "/api/simulate":
            super().do_GET()
            return

        body = json.dumps(build_simulation_payload()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/simulate":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            request = json.loads(self.rfile.read(length) or b"{}")
            if not isinstance(request, dict):
                raise ValueError("Request body must be a JSON object.")
            profile = request.get("profile", "read_only")
            if not isinstance(profile, str) or profile not in PERMISSION_PROFILES:
                self.send_error(400, "Unknown permission profile")
                return
            payload = build_simulation_payload(profile)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_error(400, str(exc))
            return
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve the local-only Gauntlet simulation dashboard."
    )
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), GauntletHandler)
    print(f"Gauntlet dashboard (simulation only): http://127.0.0.1:{args.port}")
    print("Press Ctrl+C to stop the local server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGauntlet dashboard stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
