"""Offline-safe helpers for reporting a supplied policy decision."""

_MISSING = object()


def policy_decision_result(decision) -> str:
    """Return ``allowed`` or ``denied`` for a decision with a boolean field."""
    allowed = getattr(decision, "allowed", _MISSING)
    if allowed is True:
        return "allowed"
    if allowed is False:
        return "denied"
    raise ValueError("decision must have a boolean 'allowed' field")


def format_policy_decision(decision) -> str:
    """Format the fields the integration currently reports for a decision."""
    result = policy_decision_result(decision)
    return (
        f"Allowed: {result == 'allowed'}\n"
        f"Action: {decision.action}\n"
        f"Reason: {decision.reason}"
    )
