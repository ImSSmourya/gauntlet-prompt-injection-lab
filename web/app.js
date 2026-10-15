"use strict";

const runButton = document.querySelector("#run-button");
const buttonLabel = document.querySelector("#button-label");
const profileSelect = document.querySelector("#profile-select");
const errorBanner = document.querySelector("#error-banner");
const dashboard = document.querySelector(".app-shell");
const profileNames = {
  read_only: "Read-only",
  limited_access: "Limited Access",
  admin_simulation: "Admin Simulation",
};
const descriptions = {
  read_only: "Research only. Publishing is unavailable.",
  limited_access: "Research and local echo. Publishing is unavailable.",
  admin_simulation: "All simulated tools, including a local no-op publisher.",
};

profileSelect.addEventListener("change", () => {
  document.querySelector("#profile-description").textContent = descriptions[profileSelect.value];
  document.querySelector("#summary-profile").textContent = profileNames[profileSelect.value];
  document.querySelector("#summary-result").textContent = "Ready to run";
});

function renderTrace(field, countName, events) {
  const list = document.querySelector(`[data-field="${field}"]`);
  list.replaceChildren();
  for (const event of events || []) {
    const item = document.createElement("li");
    item.textContent = event;
    list.append(item);
  }
  document.querySelector(`[data-trace-count="${countName}"]`).textContent = `${(events || []).length} events`;
}

function render(payload) {
  const [unguarded, governed] = payload.scenarios;
  document.querySelector('[data-field="unguarded-auth"]').textContent = unguarded.authorization_outcome;
  document.querySelector('[data-field="unguarded-status"]').textContent = unguarded.execution_status;
  document.querySelector('[data-field="governed-auth"]').textContent = governed.authorization_outcome;
  document.querySelector('[data-field="governed-status"]').textContent = governed.execution_status;
  document.querySelector('[data-field="profile-status"]').textContent = profileNames[payload.profile].toUpperCase();
  for (const [field, data] of [["unguarded-output", unguarded], ["governed-output", governed]]) {
    const output = document.querySelector(`[data-field="${field}"]`);
    output.textContent = data.output || "";
    output.hidden = !data.output;
  }
  renderTrace("unguarded-trace", "unguarded", unguarded.event_trace);
  renderTrace("governed-trace", "governed", governed.event_trace);
  document.querySelector("#summary-profile").textContent = profileNames[payload.profile];
  document.querySelector("#summary-result").textContent = governed.execution_status.startsWith("EXECUTED") ? "Publisher stub executed locally" : "Publish blocked by profile";
}

async function runSimulation() {
  runButton.disabled = true;
  buttonLabel.textContent = "Running…";
  errorBanner.hidden = true;
  dashboard.classList.add("is-loading");
  document.querySelector("#summary-profile").textContent = profileNames[profileSelect.value];
  document.querySelector("#summary-result").textContent = "Running simulation…";
  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      cache: "no-store",
      body: JSON.stringify({ profile: profileSelect.value }),
    });
    if (!response.ok) throw new Error(`Local simulation returned HTTP ${response.status}.`);
    const payload = await response.json();
    if (payload.simulation_only !== true || payload.armorIQ_enforcement !== false || payload.profile !== profileSelect.value || !Array.isArray(payload.scenarios) || payload.scenarios.length !== 2) {
      throw new Error("Unexpected response: simulation status or profile could not be verified.");
    }
    render(payload);
    buttonLabel.textContent = "Run Again";
  } catch (error) {
    document.querySelector("#summary-result").textContent = "Simulation failed";
    errorBanner.textContent = `Could not run the local simulation: ${error.message}`;
    errorBanner.hidden = false;
    buttonLabel.textContent = "Retry Simulation";
  } finally {
    dashboard.classList.remove("is-loading");
    runButton.disabled = false;
  }
}

runButton.addEventListener("click", runSimulation);
