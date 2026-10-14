# Gauntlet

Gauntlet is a small local demo of tool dispatch and a prompt-injection scenario. Its decisions are simulated. It does not demonstrate ArmorIQ policy enforcement.

## Files

- `gauntlet_echo.py` — local `gauntlet__echo` function.
- `gauntlet_demo.py` — local tool dispatcher and two-scenario prompt-injection demonstration.
- `gauntlet_web.py` and `web/` — standard-library localhost dashboard using the existing simulation logic.
- `policy_decision.py` — helper that interprets an explicit boolean `allowed` decision.
- `test_gauntlet_demo_offline.py`, `test_gauntlet_echo_offline.py`, `test_policy_offline.py`, `test_gauntlet_web_offline.py` — offline-only standard-library tests.
- `run_policy_live.py` — separate live ArmorIQ example; running it can contact the configured service.
- `armoriq.yaml` — existing ArmorIQ configuration.
- `requirements.txt` — dependency pin for the live SDK example.

## Launch the dashboard

Use the project's existing virtual environment on Windows:

```powershell
.\.venv\Scripts\python.exe gauntlet_web.py
```

Open `http://127.0.0.1:8000` and press **Run Attack Simulation**. The dashboard requests both results from the local Python process. The server binds only to `127.0.0.1`, and the dashboard makes no external requests. Stop the server with `Ctrl+C`. To use another local port:

```powershell
.\.venv\Scripts\python.exe gauntlet_web.py --port 8010
```

The endpoint invokes the existing `run_prompt_injection_scenarios()` simulation. No packages need to be installed.

## Demo and offline tests

```powershell
.\.venv\Scripts\python.exe gauntlet_demo.py --prompt-injection
.\.venv\Scripts\python.exe -m unittest -v
```

The unguarded simulation follows the injected publishing instruction using a local no-op publisher stub. The least-privilege simulation registers only `research`; a `publish_report` attempt is unavailable before any publisher can run. All data is dummy data; no actual publishing occurs. Every displayed decision is simulated.

The isolated echo dispatcher can also be demonstrated with simulated decisions:

```powershell
.\.venv\Scripts\python.exe gauntlet_demo.py "hello" --decision allow
.\.venv\Scripts\python.exe gauntlet_demo.py "hello" --decision deny
```

## ArmorIQ status and limitations

`run_policy_live.py` is kept separate from unittest discovery because it performs a live SDK flow. Backend connectivity and credential authorization for the intended environment remain unverified. Do not treat local simulated decisions, dashboard results, or offline tests as real ArmorIQ evaluation.

The local `gauntlet__echo`, `research`, and simulated publisher functions are not registered with ArmorIQ. The dashboard is a controlled local illustration, not a production agent or real publisher. The SDK configuration's `require_csrg: true` is not passed through or enforced by the current SDK path. Real policy enforcement, tool registration, endpoint configuration, and authorization need verification before this can serve as an ArmorIQ-integrated demo.
