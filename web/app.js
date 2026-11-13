"use strict";
const $ = (id) => document.getElementById(id);
const state = { tests: [], selected: null, sources: [], token: "", result: null, busy: false, thesis: null, experimentIds: [], thesisSources: [] };
const thesisChoices = [...document.querySelectorAll("[data-thesis]")];
const scenarioFields = { economics: [
  ["annual_volume_usd", "Annual volume · USD", 1000000000, 0, 1e15, "any"],
  ["net_revenue_bps", "Retained revenue · basis points", 5, 0, 10000, "any"],
  ["allocation", "Share allocated to purchases · 0–1", 0.5, 0, 1, 0.01],
  ["near_price_usd", "Purchase price · USD / NEAR", 2, 0.000001, 1e6, "any"],
  ["annual_issuance_near", "Annual issuance assumption · NEAR", 30000000, 0, 1e12, "any"],
  ["burn_share", "Purchased tokens burned · 0–1", 0, 0, 1, 0.01],
], staking_inference: [
  ["staked_near", "Stake · NEAR", 1000, 0, 1e9, "any"],
  ["near_price_usd", "Assumed price · USD / NEAR", 2, 0.000001, 1e6, "any"],
  ["net_apy_pct", "Net annual reward after commission · %", 6, 0, 100, 0.01],
  ["input_million", "Monthly input · million tokens", 25, 0, 1e6, "any"],
  ["output_million", "Monthly output · million tokens", 10, 0, 1e6, "any"],
  ["input_usd_per_million", "Input price · USD / million tokens", 0.2, 0, 1e6, "any"],
  ["output_usd_per_million", "Output price · USD / million tokens", 1, 0, 1e6, "any"],
] };
const scenarioForms = new Map();
function node(tag, text, className) { const element = document.createElement(tag); if (text !== undefined) element.textContent = text; if (className) element.className = className; return element; }
function show(id, visible) { $(id).classList.toggle("hidden", !visible); }
async function api(path, body) {
  const response = await fetch(path, body ? { method: "POST", headers: { "Content-Type": "application/json", "X-Lab-Token": state.token }, body: JSON.stringify(body) } : {});
  const data = await response.json(); if (!response.ok) throw new Error(data.error || "Request failed"); return data;
}
function toast(text) { $("toast").textContent = text; show("toast", true); setTimeout(() => show("toast", false), 2600); }
function format(value) { return typeof value === "number" ? new Intl.NumberFormat("en-US", { maximumFractionDigits: 4 }).format(value) : String(value); }
function updateCommand() {
  if (!state.selected) return;
  let command = `python runner.py ${state.selected.id} --mode ${$("run-mode").value || state.selected.mode}`;
  if (scenarioFields[state.selected.id]) command += ` --parameters '${JSON.stringify(parameters())}'`;
  $("cli-command").textContent = command;
}
function parameters() {
  return Object.fromEntries((scenarioFields[state.selected.id] || []).map(([key]) => [key, Number($("param-" + key).value)]));
}
function showScenarioFields(item) {
  const container = $("scenario-fields");
  if (!scenarioFields[item.id]) {
    container.replaceChildren();
    return;
  }
  if (!scenarioForms.has(item.id)) {
    const fields = scenarioFields[item.id].map(([key, label, value, min, max, step]) => {
      const wrapper = node("div", undefined, "field");
      const caption = node("label", label);
      caption.htmlFor = "param-" + key;
      const input = node("input");
      Object.assign(input, { id: caption.htmlFor, type: "number", value, min, max, step, required: true });
      input.addEventListener("input", updateCommand);
      wrapper.append(caption, input);
      return wrapper;
    });
    scenarioForms.set(item.id, fields);
  }
  container.replaceChildren(...scenarioForms.get(item.id));
}
function moveTo(id, behavior = "auto") {
  $(id).focus({ preventScroll: true });
  $(id).scrollIntoView({ block: "start", behavior });
}
function openTheses() {
  show("thesis-library", true);
  $("show-theses").setAttribute("aria-expanded", "true");
}
function selectThesis(button, scroll = true) {
  if (state.busy) return;
  state.thesis = button.dataset.thesis;
  state.selected = null;
  state.result = null;
  thesisChoices.forEach(choice => choice.setAttribute("aria-pressed", String(choice === button)));
  $("selected-thesis-title").textContent = button.querySelector("strong").textContent;
  const content = $("thesis-" + state.thesis).content.cloneNode(true);
  const links = content.querySelector(".thesis-links");
  const experimentLinks = [...links.querySelectorAll('a[href^="/lab?test="]')];
  state.experimentIds = experimentLinks.map(link => new URL(link.getAttribute("href"), location.href).searchParams.get("test"));
  experimentLinks.forEach(link => link.closest("li").remove());
  state.thesisSources = [...links.querySelectorAll("a")].map(link => [link.getAttribute("href"), link.textContent.trim().replace(/\s*↗$/, "")]);
  links.remove();
  $("thesis-description").replaceChildren(content);
  const next = $("thesis-next");
  const hasExperiments = state.experimentIds.length > 0;
  next.textContent = hasExperiments ? "Let’s experiment ↓" : "No experiment for this thesis";
  next.disabled = !hasExperiments;
  next.removeAttribute("aria-controls");
  next.removeAttribute("aria-expanded");
  if (hasExperiments) {
    next.setAttribute("aria-controls", "workspace");
    next.setAttribute("aria-expanded", "false");
  }
  show("reference-thesis-action", !hasExperiments);
  show("thesis-detail", true);
  show("workspace", false);
  show("experiment-panel", false);
  show("result-panel", false);
  if (hasExperiments) show("lab-sources", false);
  else renderSources();
  if (scroll) moveTo("selected-thesis-title");
}
async function openExperiments(preferred, scroll = true) {
  const next = $("thesis-next");
  const focusTarget = state.experimentIds.length === 1 ? "experiment-panel" : "workspace";
  if (next.getAttribute("aria-expanded") === "true") {
    if (scroll) moveTo(focusTarget, "instant");
    return;
  }
  const items = state.experimentIds.map(id => state.tests.find(item => item.id === id)).filter(Boolean);
  if (!items.length) return;
  const chooser = $("experiment-choice");
  const placeholder = node("option", "Select an experiment");
  placeholder.value = "";
  placeholder.disabled = true;
  chooser.replaceChildren(placeholder, ...items.map(item => {
    const option = node("option", item.title);
    option.value = item.id;
    return option;
  }));
  const item = items.find(option => option.id === preferred) || (items.length === 1 ? items[0] : null);
  chooser.value = item?.id || "";
  show("experiment-picker", items.length > 1);
  show("workspace", true);
  next.setAttribute("aria-expanded", "true");
  const selection = item ? select(item) : null;
  if (scroll) moveTo(focusTarget, "instant");
  await selection;
}
function setSource(index) {
  $("source-code").textContent = state.sources[index].code;
  [...$("source-tabs").children].forEach((el, i) => { el.classList.toggle("active", i === index); el.setAttribute("aria-selected", String(i === index)); });
  $("source-caption").textContent = state.sources[index].path;
}
async function select(item) {
  if (state.busy) return;
  state.selected = item; state.result = null; state.sources = [];
  show("experiment-panel", true);
  renderSources(item);
  $("experiment-title").textContent = item.title; $("experiment-question").textContent = item.question;
  $("result-panel").setAttribute("aria-label", "Experiment results");
  $("runtime").textContent = item.runtime + " · " + item.duration;
  document.querySelector(".lang-pill").textContent = item.language || "PYTHON";
  show("sandbox-note", item.mode === "sandbox");
  $("sandbox-note").textContent = item.mode === "sandbox" ? item.setup_message + (item.replay_available ? " Recorded sandbox is available." : " No recorded sandbox capture is bundled yet.") : "";
  $("source-code").textContent = "Loading source…"; $("source-tabs").replaceChildren();
  $("run-mode").replaceChildren();
  for (const [value, label] of item.mode === "scenario" ? [["scenario", item.kind === "Offline rehearsal" ? "Offline rehearsal" : "Illustrative scenario"]] : item.mode === "sandbox" ? [["sandbox", "Fresh local sandbox"], ["replay", "Recorded sandbox · recompute"]] : [["live", item.live_label || "Live observation"], ["replay", "Recorded data · recompute"]]) {
    const option = node("option", label); option.value = value;
    option.disabled = (value === "replay" && !item.replay_available) || (value === "sandbox" && !item.sandbox_available); $("run-mode").append(option);
  }
  if (item.replay_available) $("run-mode").value = "replay";
  showScenarioFields(item);
  show("scenario-controls", Boolean(scenarioFields[item.id])); show("result-panel", false); show("result-content", false); show("run-error", false);
  $("run-button").disabled = true; updateCommand();
  try {
    const data = await api(`/api/source?id=${encodeURIComponent(item.id)}`);
    if (state.selected !== item) return;
    state.sources = data.files;
    data.files.forEach((file, i) => { const tab = node("button", file.path.split("/").pop(), "source-tab"); tab.type = "button"; tab.setAttribute("role", "tab"); tab.addEventListener("click", () => setSource(i)); $("source-tabs").append(tab); });
    setSource(0); $("run-button").disabled = state.busy || !canRunSelected();
  } catch (error) { if (state.selected === item) $("source-code").textContent = error.message; }
}
function renderTable(rows) {
  $("result-table").replaceChildren(); if (!rows.length) return;
  const keys = [...new Set(rows.flatMap(Object.keys))]; const table = node("table"); const head = node("tr");
  keys.forEach((key) => { const th = node("th", key); th.scope = "col"; head.append(th); }); const thead = node("thead"); thead.append(head); table.append(thead);
  const body = node("tbody"); for (const row of rows) { const tr = node("tr"); keys.forEach((key) => { const td = node("td", row[key] === undefined ? "—" : format(row[key])); if (key === "Status") td.className = row[key] === "Quoted" ? "quote-ok" : "quote-other"; tr.append(td); }); body.append(tr); } table.append(body); $("result-table").append(table);
}
function renderChart(chart) {
  show("result-chart", Boolean(chart)); $("result-chart").replaceChildren(); if (!chart) return;
  $("result-chart").append(node("h4", "Modeled annual supply change · NEAR · all other assumptions held constant"));
  const maximum = Math.max(1, ...chart.map((row) => Math.abs(row.value)));
  for (const row of chart) { const container = node("div", undefined, "chart-row"); const bar = node("progress"); bar.max = maximum; bar.value = Math.abs(row.value); bar.setAttribute("aria-label", `${row.label}: ${format(row.value)} NEAR`); container.append(node("span", row.label), bar, node("span", format(row.value) + " NEAR")); $("result-chart").append(container); }
}
function renderResult(output) {
  const result = output.result; state.result = output; $("result-title").textContent = result.headline;
  $("result-summary").textContent = result.summary; $("result-badges").replaceChildren();
  const badges = state.selected.mode === "sandbox" ? [output.mode === "replay" ? "RECORDED SANDBOX" : "FRESH LOCAL SANDBOX", "COMPUTED NOW", "TEST BALANCES ONLY"] : output.mode === "scenario" ? ["ILLUSTRATIVE SCENARIO", "EXECUTED NOW"] : [output.mode === "live" ? "LIVE DATA" : "RECORDED DATA", "COMPUTED NOW", state.selected.kind.toUpperCase()];
  if (["mpc_signature", "treasury_flows"].includes(output.experiment_id)) badges[0] = "ARCHIVED MAINNET";
  if (output.experiment_id === "intents_history") badges[0] = "HISTORICAL SERIES";
  if (["quotes", "quotes_repeat"].includes(output.experiment_id)) badges.push("PREVIEWS ONLY · NO SWAP EXECUTED");
  if (output.experiment_id === "payment_rehearsal") badges.splice(0, 1, "OFFLINE REHEARSAL", "RECORDED DRY QUOTE");
  badges.forEach((text) => $("result-badges").append(node("span", text, "badge" + (output.mode === "scenario" ? " scenario" : ""))));
  $("metrics").replaceChildren(); for (const metric of result.metrics) { const div = node("div", undefined, "metric"); div.append(node("span", metric.label, "metric-label"), node("span", format(metric.value), "metric-value"), node("span", metric.unit || "", "metric-unit")); $("metrics").append(div); }
  $("supports").textContent = result.supports;
  const sharedContext = {
    liquidity: " This quote evidence tests route availability at the sampled times. The proposed feedback loop between liquidity and distribution requires adoption and solver data.",
    adaptability: " This result shows key revocation and continued owner access, two account controls relevant when responsibilities change.",
  };
  $("supports").textContent += sharedContext[state.thesis] || "";
   $("investment-link").textContent = result.investment_link; $("limits").textContent = result.limits;
  renderTable(result.rows || []); renderChart(result.chart);
  const rowsDetail = $("result-table").closest("details");
  const primaryTables = {
    quotes: "Quote matrix · every planned cell",
    quotes_repeat: "Two quote rounds · matching routes and amounts",
    access: "Permission checks · expected and observed",
    global_contracts: "Deployment cost and storage · every measured step",
    mpc_signature: "Signature checks · original and changed digest",
    staking_inference: "Monthly budget · sensitivity to NEAR price",
    intents_history: "Two matched 30-day periods",
    treasury_flows: "Finalized native NEAR transfers",
    ai_attestation: "TDX report checks",
    payment_rehearsal: "Local payment policy · expected and observed",
  };
  const tableTitle = primaryTables[output.experiment_id];
  if (tableTitle) $("primary-table").append(rowsDetail);
  else $("result-content").insertBefore(rowsDetail, $("provenance").closest("details"));
  rowsDetail.open = Boolean(tableTitle);
  rowsDetail.querySelector("summary").textContent = tableTitle || "Inspect calculated rows";
  $("provenance").textContent = `Execution: ${output.executed_at}\nData captured: ${output.captured_at || "Not applicable — scenario assumptions"}\nElapsed: ${output.duration_ms} ms\nAnalysis source SHA-256: ${output.source_sha256}\nCapture source SHA-256: ${output.captured_source_sha256 || "Not applicable"}\nEvidence SHA-256: ${output.evidence_sha256}${result.block_height ? "\nBlock: " + result.block_height + "\nBlock hash: " + result.block_hash : ""}`;
  if (output.experiment_id === "mpc_signature") {
    $("provenance").textContent += `
Transaction: ${result.transaction_hash}
Sign receipt: ${result.sign_receipt_id}
Callback receipt: ${result.callback_receipt_id}
Calling account: ${result.calling_account}
Derivation path: ${result.derivation_path}
Derived public key (compressed hex): ${result.derived_public_key}`;
  }
  if (result.quote_recorded_at) $("provenance").textContent += `\nDry quote recorded: ${result.quote_recorded_at}`;
  $("raw-output").textContent = JSON.stringify(output.evidence, null, 2);
  show("another-experiment-action", state.experimentIds.length > 1);
  show("result-content", true);
}
function renderSources(item) {
  const references = new Map(state.thesisSources);
  for (const url of item?.sources || []) {
    if (references.has(url)) continue;
    const { hostname, pathname } = new URL(url);
    const domain = hostname.replace(/^www\./, "");
    const page = pathname.split("/").filter(Boolean).at(-1);
    references.set(url, page ? `${domain} · ${page.replaceAll("-", " ")}` : domain);
  }
  for (const [id, label] of Object.entries(item?.related || {})) {
    references.set("/lab?test=" + encodeURIComponent(id), label);
  }
  const list = $("source-links");
  list.replaceChildren();
  for (const [url, label] of references) {
    const link = node("a", label + " ↗");
    link.href = url;
    link.title = url;
    if (url.startsWith("https://")) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    }
    const row = node("li");
    row.append(link);
    list.append(row);
  }
  show("lab-sources", references.size > 0);
}
function canRunSelected() {
  return state.selected && (state.selected.mode !== "sandbox" || ($("run-mode").value === "replay" ? state.selected.replay_available : state.selected.sandbox_available));
}
function setRunControls() {
  thesisChoices.forEach(button => { button.disabled = state.busy; });
  $("thesis-next").disabled = state.busy || !state.experimentIds.length;
  $("experiment-choice").disabled = state.busy;
  $("run-mode").disabled = state.busy;
  $("run-button").disabled = state.busy || !state.sources.length || !canRunSelected();
}
async function runSelected() {
  if (state.busy || !canRunSelected()) return;
  if (state.selected.mode === "scenario") { for (const input of $("scenario-fields").querySelectorAll("input")) { if (!input.reportValidity()) return; } }
  state.busy = true; state.result = null; setRunControls();
  show("result-panel", true); show("result-content", false); show("run-error", false); show("running-state", true);
  $("running-title").textContent = state.selected.id === "payment_rehearsal" ? "Reviewing the sample payment and recorded quote…" : $("run-mode").value === "replay" ? "Recomputing from recorded evidence…" : $("run-mode").value === "scenario" ? "Computing your assumptions…" : $("run-mode").value === "sandbox" ? "Starting a fresh local Sandbox and running the experiment…" : ["quotes", "quotes_repeat"].includes(state.selected.id) ? "Requesting six dry previews; all outcomes will be kept…" : "Requesting public evidence and running analysis…";
  try { const output = await api("/api/run", { id: state.selected.id, mode: $("run-mode").value, parameters: state.selected.mode === "scenario" ? parameters() : {} }); renderResult(output); }
  catch (error) { $("run-error").textContent = error.message + (state.selected.mode === "scenario" ? "" : " Nothing has been replaced with a cached success. Select recorded data explicitly to retry."); show("run-error", true); }
  finally { state.busy = false; setRunControls(); show("running-state", false); moveTo("result-panel", "instant"); }
}
async function boot() {
  $("show-theses").addEventListener("click", () => { openTheses(); moveTo("theses-title"); });
  thesisChoices.forEach(button => button.addEventListener("click", () => selectThesis(button)));
  $("thesis-next").addEventListener("click", () => {
    if (state.tests.length) openExperiments();
  });
  $("experiment-choice").addEventListener("change", event => {
    const item = state.tests.find(test => test.id === event.target.value);
    if (!item) return;
    select(item);
    moveTo("workspace", "instant");
    $("experiment-choice").focus({ preventScroll: true });
  });
  $("another-experiment").addEventListener("click", () => {
    moveTo("workspace", "instant");
    $("experiment-choice").focus({ preventScroll: true });
  });
  document.querySelectorAll("[data-back-to-theses]").forEach(button => {
    button.addEventListener("click", () => moveTo("theses-title"));
  });
  $("run-mode").addEventListener("change", () => { updateCommand(); setRunControls(); });
  $("run-button").addEventListener("click", runSelected);
  $("copy-code").addEventListener("click", async () => { try { await navigator.clipboard.writeText($("source-code").textContent); toast("Code copied"); } catch { toast("Select the source text to copy it in this browser."); } });
  $("download-result").addEventListener("click", () => { if (!state.result) return; const url = URL.createObjectURL(new Blob([JSON.stringify(state.result, null, 2)], { type: "application/json" })); const a = node("a"); a.href = url; a.download = `near-evidence-${state.result.experiment_id}-${state.result.mode}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); });
  const requested = new URLSearchParams(location.search).get("test");
  const initial = requested && thesisChoices.find(button =>
    $("thesis-" + button.dataset.thesis).content.querySelector('a[href="/lab?test=' + CSS.escape(requested) + '"]'));
  if (initial) {
    openTheses();
    selectThesis(initial, false);
  }
  try {
    const data = await api("/api/catalog");
    state.tests = data.tests;
    state.token = data.csrf_token;
    if (initial && state.thesis === initial.dataset.thesis) await openExperiments(requested, false);
  } catch (error) {
    $("load-error").textContent = "Could not load experiments: " + error.message;
    show("load-error", true);
  }
}
boot();
