"""Offline tests for the local web adapter; no network is used."""

import unittest
from pathlib import Path
from unittest.mock import Mock

from gauntlet_demo import (
    build_governed_tool_registry,
    dispatch_registered_tool,
    permission_profile_tools,
)
from gauntlet_web import build_simulation_payload

WEB_ROOT = Path(__file__).with_name("web")


class GauntletWebAdapterOfflineTests(unittest.TestCase):
    def test_payload_contains_simulated_profile_and_two_scenarios(self):
        payload = build_simulation_payload("read_only")
        self.assertIs(payload["simulation_only"], True)
        self.assertIs(payload["armorIQ_enforcement"], False)
        self.assertEqual(payload["profile"], "read_only")
        self.assertEqual(len(payload["scenarios"]), 2)
        self.assertIn("publish_report", payload["scenarios"][1]["attempted_tool_call"])

    def test_profiles_have_distinct_tool_grants(self):
        self.assertEqual(permission_profile_tools("read_only"), {"research"})
        self.assertEqual(permission_profile_tools("limited_access"), {"research", "gauntlet__echo"})
        self.assertIn("publish_report", permission_profile_tools("admin_simulation"))

    def test_advertised_profile_capabilities_match_dispatch_allowlists(self):
        advertised = build_simulation_payload()["profiles"]
        for profile, capabilities in advertised.items():
            self.assertEqual(set(capabilities), permission_profile_tools(profile))

    def test_echo_is_registered_and_invocable_only_for_permitted_profiles(self):
        registry = build_governed_tool_registry(lambda query: "dummy research")
        self.assertIn("gauntlet__echo", registry)
        echo = Mock(return_value="echoed")
        registry["gauntlet__echo"] = echo
        allowed = object()
        # Admin and limited access both advertise and permit the registered echo tool.
        for profile in ("limited_access", "admin_simulation"):
            result = dispatch_registered_tool(
                "gauntlet__echo", {"message": "hello"},
                type("Decision", (), {"allowed": True})(), registry,
                permission_profile=profile,
            )
            self.assertEqual(result.status, "executed")
        self.assertEqual(echo.call_count, 2)
        denied = dispatch_registered_tool(
            "gauntlet__echo", {"message": "hello"}, allowed, registry,
            permission_profile="read_only",
        )
        self.assertEqual(denied.status, "permission_denied")
        self.assertEqual(echo.call_args_list, [
            unittest.mock.call(message="hello"),
            unittest.mock.call(message="hello"),
        ])

    def test_backend_dispatcher_denies_tool_before_call_for_limited_profile(self):
        publisher = Mock(return_value="published")
        result = dispatch_registered_tool(
            "publish_report", {"content": "dummy"}, object(), {"publish_report": publisher},
            permission_profile="limited_access",
        )
        self.assertEqual(result.status, "permission_denied")
        self.assertFalse(result.executed)
        publisher.assert_not_called()

    def test_admin_profile_runs_only_the_local_publisher_stub(self):
        scenario = build_simulation_payload("admin_simulation")["scenarios"][1]
        self.assertTrue(scenario["execution_status"].startswith("EXECUTED locally"))
        self.assertIn("SIMULATED ONLY", scenario["output"])

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            build_simulation_payload("superuser")
        with self.assertRaises(ValueError):
            permission_profile_tools([])

    def test_dashboard_uses_palette_and_accessible_collapsible_traces(self):
        page = (WEB_ROOT / "index.html").read_text(encoding="utf-8")
        styles = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")
        script = (WEB_ROOT / "app.js").read_text(encoding="utf-8")
        for profile in ("Read-only", "Limited Access", "Admin Simulation"):
            self.assertIn(profile, page)
        for color in ("#CCC9A1", "#F0FFCE", "#A53F2B", "#4C230A", "#280004"):
            self.assertIn(color, styles)
        self.assertIn('<details class="trace-details">', page)
        self.assertIn('aria-live="polite"', page)
        self.assertIn('method: "POST"', script)
        self.assertIn("permission_profile", (Path(__file__).with_name("gauntlet_demo.py")).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
