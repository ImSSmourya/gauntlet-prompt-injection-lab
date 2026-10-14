from armoriq_sdk import ArmorIQClient, SessionOptions
from armoriq_sdk.config import load_armoriq_config
from policy_decision import format_policy_decision

config = load_armoriq_config("armoriq.yaml")
client = ArmorIQClient(
    user_id=config.identity.user_id,
    agent_id=config.identity.agent_id,
    proxy_endpoint=config.proxy.url,
    timeout=float(config.proxy.timeout),
    max_retries=int(config.proxy.max_retries),
    use_production=(config.environment == "production"),
)
# The current SDK path does not pass through or enforce config.intent.require_csrg.
session = client.start_session(SessionOptions(mode="sdk"))

tool_name = "gauntlet__echo"
tool_args = {"message": "hello"}

try:
    session.start_plan(
        [{"name": tool_name, "args": tool_args}],
        goal="Test that an unapproved tool is blocked"
    )

    decision = session.check(tool_name, tool_args)

    print(format_policy_decision(decision))
finally:
    session.close()
    client.close()
