"use strict";

const runButton = document.querySelector("#run-button");
const buttonLabel = document.querySelector("#button-label");
const errorBanner = document.querySelector("#error-banner");
const dashboard = document.querySelector(".app-shell");

function clearScenarioResults(message) {
  for (const card of document.querySelectorAll(".scenario-card")) {
    for (const name of [
      "attack",
      "attempted_tool_call",
      "authorization_outcome",
      "execution_status",
    ]) {
      const element = card.querySelector(`[data-field="${name}"]`);
      if (element) element.textContent = "—";
    }
    const output = card.querySelector('[data-field="output"]');
    output.textContent = "";
    output.hidden = true;

    const trace = card.querySelector('[data-field="event_trace"]');
    const placeholder = document.createElement("li");
    placeholder.className = "trace-empty";
    placeholder.textContent = message;
    trace.replaceChildren(placeholder);
    card.querySelector("[data-trace-count]").textContent = "0 EVENTS";

    card.querySelector('[data-field="authorization_outcome"]').classList.remove(
      "danger-text",
      "safe-text",
    );
    card.querySelector('[data-field="execution_status"]').classList.remove(
      "danger-text",
      "safe-text",
    );
  }
}

function renderScenario(card, scenario) {
  const fields = [
    "attack",
    "attempted_tool_call",
    "authorization_outcome",
    "execution_status",
  ];

  for (const name of fields) {
    const element = card.querySelector(`[data-field="${name}"]`);
    if (element) element.textContent = scenario[name] ?? "—";
  }

  const output = card.querySelector('[data-field="output"]');
  output.textContent = scenario.output || "";
  output.hidden = !scenario.output;

  const trace = card.querySelector('[data-field="event_trace"]');
  trace.replaceChildren();
  for (const event of scenario.event_trace || []) {
    const item = document.createElement("li");
    item.textContent = event;
    trace.append(item);
  }
  card.querySelector("[data-trace-count]").textContent =
    `${(scenario.event_trace || []).length} EVENTS`;

  const authorization = card.querySelector('[data-field="authorization_outcome"]');
  const execution = card.querySelector('[data-field="execution_status"]');
  const governed = card.classList.contains("governed-card");
  const ran = scenario.execution_status.startsWith("EXECUTED");
  authorization.classList.toggle("danger-text", !governed);
  authorization.classList.toggle("safe-text", governed);
  execution.classList.toggle("danger-text", !governed && ran);
  execution.classList.toggle("safe-text", governed && !ran);
}

async function runSimulation() {
  runButton.disabled = true;
  buttonLabel.textContent = "Running local simulation…";
  errorBanner.hidden = true;
  dashboard.classList.add("is-loading");
  clearScenarioResults("Running local simulation…");

  try {
    const response = await fetch("/api/simulate", {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) throw new Error(`Local simulation returned HTTP ${response.status}.`);
    const payload = await response.json();
    if (payload.simulation_only !== true || payload.armorIQ_enforcement !== false) {
      throw new Error("Unexpected response: simulation status could not be verified.");
    }
    if (!Array.isArray(payload.scenarios) || payload.scenarios.length !== 2) {
      throw new Error("Unexpected response: both local scenarios were not returned.");
    }
    const cards = document.querySelectorAll(".scenario-card");
    if (cards.length !== 2) {
      throw new Error("Unexpected dashboard state: both scenario panels are unavailable.");
    }
    payload.scenarios.forEach((scenario, index) => renderScenario(cards[index], scenario));
    buttonLabel.textContent = "Run Again";
  } catch (error) {
    clearScenarioResults("No result: this simulation run failed.");
    errorBanner.textContent = `Could not run the local simulation: ${error.message}`;
    errorBanner.hidden = false;
    buttonLabel.textContent = "Retry Simulation";
  } finally {
    dashboard.classList.remove("is-loading");
    runButton.disabled = false;
  }
}

runButton.addEventListener("click", runSimulation);
