"""Offline tests for the local web adapter; no server or network is used."""

import unittest
from pathlib import Path

from gauntlet_web import build_simulation_payload

WEB_ROOT = Path(__file__).with_name("web")


class GauntletWebAdapterOfflineTests(unittest.TestCase):
    def test_payload_contains_both_labeled_simulations(self):
        payload = build_simulation_payload()

        self.assertIs(payload["simulation_only"], True)
        self.assertIs(payload["armorIQ_enforcement"], False)
        self.assertEqual(len(payload["scenarios"]), 2)
        unguarded, governed = payload["scenarios"]
        self.assertIn("SIMULATION ONLY", unguarded["name"])
        self.assertIn("SIMULATION ONLY", governed["name"])
        self.assertIn("publish_report", governed["attempted_tool_call"])

    def test_governed_payload_reports_unavailable_tool_not_policy_denial(self):
        governed = build_simulation_payload()["scenarios"][1]

        self.assertIn("SIMULATED BLOCK", governed["authorization_outcome"])
        self.assertIn("unavailable", governed["authorization_outcome"])
        self.assertEqual(governed["execution_status"], "NOT EXECUTED")
        self.assertIsNone(governed["output"])
        self.assertTrue(any("publish_report is not registered" in event for event in governed["event_trace"]))

    def test_permission_strip_has_dark_theme_styles(self):
        styles = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")

        for selector in (
            ".permission-strip{",
            ".permission-lock{",
            ".permission-separator{",
            ".blocked-tool{",
        ):
            self.assertIn(selector, styles)
        self.assertIn("background:", styles[styles.index(".permission-strip{"):])
        self.assertIn("border:", styles[styles.index(".blocked-tool{"):])

    def test_dashboard_labels_capability_unavailability_as_simulation(self):
        page = (WEB_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn('class="scenario-number">SCENARIO 01</span><span class="scenario-mode">SIMULATED', page)
        self.assertIn('class="scenario-number">SCENARIO 02</span><span class="scenario-mode">SIMULATED', page)
        self.assertIn("SIMULATED TOOL AVAILABILITY", page)
        self.assertIn('<div class="tool-list"><span class="tool-badge tool-available"><code>research</code>', page)
        self.assertIn("publish_report</code><span>unavailable - not registered</span>", page)
        self.assertIn("<h4 class=\"trace-title\">EVENT TRACE</h4>", page)
        self.assertIn('href="/styles.css?v=3"', page)
        self.assertIn('<span class="field-label-text">ATTACK INSTRUCTION</span>', page)
        self.assertIn("Simulation, not enforcement.", page)
        self.assertNotIn("Publishing is denied", page)

    def test_dashboard_styles_wrap_scenario_tools_and_traces_at_narrow_widths(self):
        styles = (WEB_ROOT / "styles.css").read_text(encoding="utf-8")

        self.assertIn(".card-topline{height:auto;", styles)
        self.assertIn(".card-topline{display:grid;grid-template-columns:minmax(0,1fr) auto;", styles)
        self.assertIn(".scenario-index{min-width:0;display:flex;", styles)
        self.assertIn(".permission-strip{display:grid;grid-template-columns:auto auto minmax(0,1fr);", styles)
        self.assertIn(".tool-list{grid-column:1/-1;", styles)
        self.assertIn(".tool-badge{min-width:0;display:inline-flex;", styles)
        self.assertIn(".event-list li{min-width:0;", styles)
        self.assertIn(".trace-heading{display:grid;grid-template-columns:minmax(0,1fr) auto;", styles)
        self.assertIn("@media(max-width:760px){.card-topline{", styles)
        self.assertIn("@media(max-width:430px){.card-topline{", styles)

    def test_frontend_clears_old_results_before_running_and_after_failure(self):
        script = (WEB_ROOT / "app.js").read_text(encoding="utf-8")
        run_start = script.index("async function runSimulation()")
        fetch_start = script.index('fetch("/api/simulate"', run_start)
        loading_clear = script.index('clearScenarioResults("Running local simulation…")', run_start)
        catch_start = script.index("} catch (error) {", fetch_start)
        failure_clear = script.index('clearScenarioResults("No result: this simulation run failed.")', catch_start)

        self.assertLess(loading_clear, fetch_start)
        self.assertLess(catch_start, failure_clear)
        self.assertIn('dashboard.classList.add("is-loading")', script)
        self.assertIn('dashboard.classList.remove("is-loading")', script)


if __name__ == "__main__":
    unittest.main()
