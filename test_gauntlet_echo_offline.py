"""Offline unit tests for the local echo function; no SDK or network access."""

import unittest

from gauntlet_echo import gauntlet__echo


class GauntletEchoOfflineTests(unittest.TestCase):
    def test_returns_normal_message_unchanged(self):
        self.assertEqual(gauntlet__echo("hello, Gauntlet"), "hello, Gauntlet")

    def test_returns_empty_message(self):
        self.assertEqual(gauntlet__echo(""), "")

    def test_rejects_non_string_message(self):
        with self.assertRaisesRegex(TypeError, "message must be a string"):
            gauntlet__echo(123)


if __name__ == "__main__":
    unittest.main()
