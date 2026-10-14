"""Offline/mock-only tests for local dispatch; no ArmorIQ SDK or network."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from gauntlet_demo import (
    _simulated_publish_noop,
    dispatch_registered_tool,
    dispatch_tool,
    run_prompt_injection_scenarios,
)


class GauntletDispatcherOfflineTests(unittest.TestCase):
    def test_allowed_decision_calls_echo_exactly_once(self):
        echo = Mock(return_value="hello")
        decision = SimpleNamespace(allowed=True, reason="simulated allow")

        result = dispatch_tool("gauntlet__echo", "hello", decision, echo_tool=echo)

        self.assertEqual(result.status, "executed")
        self.assertTrue(result.executed)
        self.assertEqual(result.output, "hello")
        echo.assert_called_once_with(message="hello")

    def test_denied_decision_never_calls_echo(self):
        echo = Mock(return_value="hello")
        decision = SimpleNamespace(allowed=False, reason="simulated deny")

        result = dispatch_tool("gauntlet__echo", "hello", decision, echo_tool=echo)

        self.assertEqual(result.status, "denied")
        self.assertFalse(result.executed)
        self.assertIsNone(result.output)
        echo.assert_not_called()

    def test_missing_decision_never_calls_echo(self):
        echo = Mock(return_value="hello")

        result = dispatch_tool("gauntlet__echo", "hello", None, echo_tool=echo)

        self.assertEqual(result.status, "blocked")
        self.assertIn("Missing or invalid", result.reason)
        echo.assert_not_called()

    def test_argument_binding_error_is_reported_before_tool_invocation(self):
        invocations = []

        def tool(message):
            invocations.append(message)
            return message

        result = dispatch_registered_tool(
            "tool",
            {"unexpected": "value"},
            SimpleNamespace(allowed=True),
            {"tool": tool},
        )

        self.assertEqual(result.status, "invalid_input")
        self.assertFalse(result.executed)
        self.assertEqual(invocations, [])

    def test_uninspectable_tool_is_not_invoked(self):
        invocations = []

        class ToolWithoutInspectableSignature:
            __signature__ = object()

            def __call__(self, **arguments):
                invocations.append(arguments)
                return "unexpected"

        result = dispatch_registered_tool(
            "tool",
            {"value": "dummy"},
            SimpleNamespace(allowed=True),
            {"tool": ToolWithoutInspectableSignature()},
        )

        self.assertEqual(result.status, "not_invoked")
        self.assertFalse(result.executed)
        self.assertIn("was not invoked", result.reason)
        self.assertEqual(invocations, [])

    def test_type_error_inside_invoked_tool_is_an_execution_error(self):
        invocations = []

        def tool(message):
            invocations.append(message)
            raise TypeError("failure raised inside tool")

        result = dispatch_tool(
            "gauntlet__echo",
            "hello",
            SimpleNamespace(allowed=True),
            echo_tool=tool,
        )

        self.assertEqual(result.status, "execution_error")
        self.assertTrue(result.executed)
        self.assertIsNone(result.output)
        self.assertIn("TypeError: failure raised inside tool", result.reason)
        self.assertEqual(invocations, ["hello"])

    def test_malformed_decision_never_calls_echo(self):
        echo = Mock(return_value="hello")
        decision = SimpleNamespace(allowed="true")

        result = dispatch_tool("gauntlet__echo", "hello", decision, echo_tool=echo)

        self.assertEqual(result.status, "blocked")
        self.assertIn("boolean 'allowed' field", result.reason)
        echo.assert_not_called()

    def test_invalid_tool_name_is_rejected(self):
        echo = Mock(return_value="hello")
        decision = SimpleNamespace(allowed=True)

        result = dispatch_tool("shell", "hello", decision, echo_tool=echo)

        self.assertEqual(result.status, "rejected")
        self.assertIn("Unknown tool", result.reason)
        echo.assert_not_called()

    def test_denied_registered_tool_never_executes(self):
        publisher = Mock(return_value="published")
        decision = SimpleNamespace(
            allowed=False,
            reason="SIMULATED DENY; tool is outside the allowlist",
        )

        result = dispatch_registered_tool(
            "publish_report",
            {"content": "dummy"},
            decision,
            {"publish_report": publisher},
        )

        self.assertEqual(result.status, "denied")
        self.assertFalse(result.executed)
        publisher.assert_not_called()

    def test_unregistered_tool_is_unavailable_before_any_callable_runs(self):
        research = Mock(return_value="harmless finding")
        decision = SimpleNamespace(allowed=True)

        result = dispatch_registered_tool(
            "publish_report",
            {"content": "dummy"},
            decision,
            {"research": research},
        )

        self.assertEqual(result.status, "rejected")
        self.assertFalse(result.executed)
        self.assertIn("unavailable to this agent", result.reason)
        research.assert_not_called()

    def test_governed_scenario_has_research_only_and_never_publishes(self):
        research = Mock(return_value="harmless finding")

        with patch(
            "gauntlet_demo._simulated_publish_noop",
            wraps=_simulated_publish_noop,
        ) as publisher:
            unguarded, governed = run_prompt_injection_scenarios(
                governed_research_tool=research,
            )

        self.assertIn("SIMULATION ONLY", governed.name)
        self.assertEqual(governed.authorization_outcome.split()[0], "SIMULATED")
        self.assertIn("BLOCK", governed.authorization_outcome)
        self.assertIn("unavailable", governed.authorization_outcome)
        self.assertEqual(governed.execution_status, "NOT EXECUTED")
        self.assertIsNone(governed.output)
        self.assertIn("publish_report is not registered", " ".join(governed.event_trace))
        self.assertIn("unavailable to this agent", " ".join(governed.event_trace))
        research.assert_called_once()
        # The only publisher call belongs to the unguarded local no-op scenario.
        publisher.assert_called_once_with(
            content="Dummy research finding: the echo tool returns its input unchanged."
        )
        self.assertIn("EXECUTED locally", " ".join(governed.event_trace))

        # The unguarded path is an isolated simulation with a no-op publisher.
        self.assertIn("SIMULATION ONLY", unguarded.name)


if __name__ == "__main__":
    unittest.main()
