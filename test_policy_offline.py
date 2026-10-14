"""Offline/mock-only decision formatting tests; no SDK client or network."""

import unittest
from unittest.mock import Mock

from policy_decision import format_policy_decision, policy_decision_result


class OfflineMockPolicyDecisionTests(unittest.TestCase):
    def test_allowed_decision_is_reported(self):
        decision = Mock(allowed=True, action="allow", reason="Policy permits tool")

        self.assertEqual(policy_decision_result(decision), "allowed")
        self.assertEqual(
            format_policy_decision(decision),
            "Allowed: True\nAction: allow\nReason: Policy permits tool",
        )

    def test_denied_decision_is_reported(self):
        decision = Mock(allowed=False, action="deny", reason="Tool is not approved")

        self.assertEqual(policy_decision_result(decision), "denied")
        rendered = format_policy_decision(decision)
        self.assertNotIn("Allowed: True", rendered)
        self.assertEqual(
            rendered,
            "Allowed: False\nAction: deny\nReason: Tool is not approved",
        )

    def test_missing_decision_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "boolean 'allowed' field"):
            policy_decision_result(None)

    def test_invalid_allowed_value_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "boolean 'allowed' field"):
            policy_decision_result(Mock(allowed="false"))


if __name__ == "__main__":
    unittest.main()
