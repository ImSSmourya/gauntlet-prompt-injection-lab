# Gauntlet

## Project overview

Gauntlet is a local prompt-injection demonstration. It compares an unguarded simulated agent with an agent whose local tool registry contains only its permitted research tool. A localhost dashboard presents each scenario, attempted tool call, simulated authorization or tool-availability result, execution status, and event trace.

This is a hackathon prototype. Its dashboard and local scenarios do not demonstrate verified ArmorIQ policy enforcement or production security.

## Problem and motivation

Prompt injection can steer an agent toward tools outside the user's intended task. Gauntlet illustrates why an agent's available capabilities matter: a simulated publishing instruction can reach a publisher in an unguarded setup, while a tool absent from a least-privilege registry is unavailable to that agent.

## How Gauntlet works

The Python simulation uses local dispatch logic and harmless dummy data. The browser dashboard requests the two scenario results from a small Python HTTP server bound to `127.0.0.1`. The unguarded scenario's publisher is a local no-op stub: it returns a simulated message and does not publish, send data, or call an external service. The dashboard makes no ArmorIQ or other external requests.

## Two simulated scenarios

- **Unguarded agent:** follows the dummy injected instruction. Its local registry includes `publish_report`, which reaches a harmless no-op publisher stub. The trace labels the decision and execution as simulated.
- **Least-privilege agent:** its registry contains `research` only. A `publish_report` attempt is unavailable because that tool is not registered; no publishing function is called in this scenario.

These are local demonstrations of capability boundaries, not real policy decisions.

## Architecture and project structure

- `gauntlet_demo.py` - local tool dispatcher, simulated prompt-injection scenarios, and command-line demonstrations.
- `gauntlet_echo.py` - independent local echo function.
- `policy_decision.py` - helper for interpreting and formatting a supplied decision object; it does not contact ArmorIQ.
- `gauntlet_web.py` - standard-library localhost server and JSON adapter for the existing simulation.
- `web/index.html`, `web/styles.css`, `web/app.js` - dashboard markup, styling, and browser behavior.
- `run_policy_live.py` - separate ArmorIQ SDK example; it can contact the configured service when run.
- `armoriq.yaml` - local ArmorIQ configuration; intentionally excluded from the public submission.
- `.env` - local-only environment file; intentionally excluded from the public submission and ignored by Git patterns in this project.
- `requirements.txt` - pins `armoriq-sdk==0.6.10` for the separate SDK example.
- `test_*_offline.py` - standard-library offline tests. The live runner is named `run_policy_live.py`, so unittest discovery does not import it.

## Installation and setup

Gauntlet requires Python 3. The local dashboard, demonstrations, and offline tests use only the Python standard library; no package installation is needed for those workflows. From a clean Windows checkout, create a virtual environment:

```powershell
py -3 -m venv .venv
```

The separate ArmorIQ SDK example requires the pinned SDK dependency. Install it only when preparing that example:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The SDK example also requires a valid, authorized ArmorIQ configuration. `armoriq.yaml` and `.env` are local files intentionally excluded from the public repository. Supply them through your approved private setup; do not commit credentials or populated configuration to the submission. Connectivity and authorization remain unverified; see [ArmorIQ integration status and limitations](#armoriq-integration-status-and-limitations).

## Launching the dashboard

Start the local server:

```powershell
.\.venv\Scripts\python.exe gauntlet_web.py
```

Open `http://127.0.0.1:8000` in a browser and select **Run Attack Simulation**. Stop the server with `Ctrl+C`. The server accepts an optional `--port` argument; for example:

```powershell
.\.venv\Scripts\python.exe gauntlet_web.py --port 8010
```

## Running the demonstrations

Run the two prompt-injection scenarios:

```powershell
.\.venv\Scripts\python.exe gauntlet_demo.py --prompt-injection
```

Run the local echo demonstration with an explicitly simulated allow decision:

```powershell
.\.venv\Scripts\python.exe gauntlet_demo.py "hello" --decision allow
```

Run it with a simulated deny decision:

```powershell
.\.venv\Scripts\python.exe gauntlet_demo.py "hello" --decision deny
```

The CLI labels these as simulated decisions. None of these local commands invokes ArmorIQ.

## Running the offline tests

Run unittest discovery from the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

The discovered tests cover local dispatch, simulated decision formatting, and the dashboard adapter and markup. They use the standard library and do not initialize a live ArmorIQ client or make network requests.

## ArmorIQ integration status and limitations

`run_policy_live.py` is separate from the local dashboard and offline tests. It loads the ArmorIQ configuration and performs an SDK session/check flow; running it may contact the configured service. Its endpoint connectivity and the saved credential's authorization for the intended environment remain unverified. The live runner has not demonstrated a successful policy decision.

The current SDK path does not pass through or enforce `require_csrg: true`. The local tools are not registered with ArmorIQ, and dashboard decisions are generated by Gauntlet's local simulation logic. Do not interpret simulated outcomes or offline tests as verified ArmorIQ policy enforcement. The project does not claim production-grade security.

## Future improvements

- Confirm the correct ArmorIQ environment, backend/proxy configuration, and credential authorization with official support before attempting a live evaluation.
- Verify a real policy decision and the intended tool-registration/delegation flow before describing the project as ArmorIQ-integrated.
- Add a safe public configuration template and submission checklist without committing local identities, credentials, or secrets.
- Improve the demo with judge-friendly narration and repeatable, clearly labeled attack cases while preserving the offline/local boundary.
