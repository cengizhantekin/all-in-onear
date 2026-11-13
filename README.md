# All in oNEar — Evidence Lab

**Why NEAR?** A local, source-visible exploration of an integrated-stack investment thesis.

All in oNEar tests parts of an integrated-stack investment thesis through public observations, local Sandbox experiments and explicit scenarios. **Why NEAR?** introduces the thesis. **Labs** shows the source, result and evidence for each experiment.

## Start here

1. From the project directory, run `python3 server.py` on macOS, Linux or WSL, or `py -3 server.py` on Windows. Use Python 3.11 or newer. Open [Why NEAR?](http://127.0.0.1:8765/).
2. Open **Meet Hubble** → **Show All Theses** → **One payment, four capabilities** → **Let’s experiment**. Under **Choose an experiment**, select **Rehearse a cross-chain payment**, then click **Run experiment**. The offline rehearsal checks a sample request against a recorded Intents dry quote. Expect **4/4** policy decisions to match. It stops at human review.
3. Use the experiment picker to inspect the TDX report, account permissions and Chain Signatures evidence behind the workflow. **Download evidence** saves each run’s inputs, results and provenance as JSON.

| Mode | Experiments | Requirements |
|---|---|---|
| Recorded replay | Protocol, MPC configuration, asset catalog, dry quotes, access keys, global contracts, signature verification, repeat quotes, historical Intents activity, treasury flows, AI attestation | Python and the bundled records |
| Scenario | Token economics, Staking for Inference, payment rehearsal | Python and the bundled payment quote |
| Fresh Sandbox | Access keys, global contracts | Supported Linux/WSL or macOS ARM64, Node.js, Sandbox binary and sufficient file descriptors |
| Optional verification | Intel DCAP quote chain | Compatible `dcap-qvl` build and recorded collateral |

The bundle runs **all 14 experiments** offline with Python alone using saved evidence and local scenarios. AI attestation replay checks the saved report’s fields and measurements with Python. Its Intel quote-chain check runs when the optional verifier is installed.

## Quick start — Windows

Install **Python 3.11 or newer** from [python.org](https://www.python.org/downloads/windows/), including the Python launcher. VS Code is optional. The base app and bundled replays require only Python. Start fresh Sandbox runs from a supported Linux/WSL or macOS ARM64 shell.

Extract or clone the project into a regular folder. In PowerShell, from the project folder:

```powershell
py -3 --version
py -3 server.py
```

Open **http://127.0.0.1:8765** in your browser. Alternatively, double-click `start.bat` from a regular Windows folder. If the project is under `~/near-evidence-lab` in WSL, start it with `python3 server.py` from the Ubuntu terminal. Keep the terminal open while using the app; press Ctrl+C to stop it. If the launcher is unavailable but Python is on PATH, use `python server.py`.

**First check:** open **Labs** from the header, choose **Show All Theses**, then select **A foundation that scales** and **Let’s experiment**. Choose **Recorded data · recompute**, then click **Run experiment**. You should see the saved block height, calculated shard counts and provenance. Switch to live mode to request a new observation; values may differ.

## macOS / Linux / evaluator container

```sh
python3 --version
python3 -m unittest discover -s tests -v
python3 runner.py network --mode replay
python3 server.py
```

The base app uses the Python standard library. The Intel quote-chain verification has an optional dependency described below. The tests do not contact external services or require credentials. Guide endpoint checks use an ephemeral loopback HTTP server. Windows-specific execution is documented but was not tested on a Windows machine in this build.

For a container that needs to expose the UI outside loopback:

```sh
python3 server.py --host 0.0.0.0 --port 8765
```

This development server is intended for local use, not as hardened public hosting. The default bind is loopback. A sandbox that forbids listening sockets can use the CLI instead. Browser screenshots are not necessary to reproduce the analysis.

## Run all included observations offline

```sh
python3 runner.py payment_rehearsal --mode scenario
python3 runner.py network --mode replay
python3 runner.py mpc --mode replay
python3 runner.py assets --mode replay
python3 runner.py quotes --mode replay
python3 runner.py economics --mode scenario
python3 runner.py access --mode replay
python3 runner.py global_contracts --mode replay
python3 runner.py mpc_signature --mode replay
python3 runner.py staking_inference --mode scenario
python3 runner.py quotes_repeat --mode replay
python3 runner.py intents_history --mode replay
python3 runner.py treasury_flows --mode replay
python3 runner.py ai_attestation --mode replay
```

On Windows substitute `py -3` for `python3`. CLI output is structured JSON containing raw evidence, hashes, mode, capture time, execution time and calculated results.

## Refresh public observations

```sh
python3 runner.py network --mode live --record
python3 runner.py mpc --mode live --record
python3 runner.py assets --mode live --record
python3 runner.py quotes --mode live --record
```

`--record` explicitly replaces that experiment's recording. Ordinary UI runs do not change the committed recordings. No transaction is sent and no wallet is connected. Public endpoint access and rate limits can change. If a live request fails, the UI reports failure; it never silently substitutes a recorded success. Recorded mode must be selected explicitly.

The RPC endpoint is `https://free.rpc.fastnear.com`; the catalog endpoint is `https://1click.chaindefuser.com/v0/tokens`. The quote module has a separate fixed `POST https://1click.chaindefuser.com/v0/quote` transport that rejects requests unless `dry` is the boolean `true`. They are fixed in `experiments/common.py`. Individual observation scripts explain their inputs and calculations. Do not scan or contact MPC participant URLs: this app only reads the public contract state.

## Local access-key sandbox

The fresh access-key experiment runs against a local NEAR Sandbox node. It creates fresh keys and accounts in **NEAR Sandbox 2.14.0**, compiles the included minimal WAT contract, and submits signed transactions directly to loopback JSON-RPC. The SDK only signs/serializes: the intended denials must come from the node. No public wallet, API key, mainnet or testnet account is loaded.

The bundled WSL capture matched all eight permission checks. Replay in the app or run `python3 runner.py access --mode replay`. See [the recorded findings](docs/SANDBOX_FINDINGS_TR.md).

Fresh execution needs Linux/WSL or macOS ARM64, a hard open-file limit >=65535 and Node.js >=22.22.2. See [Windows setup and experiment instructions](docs/SANDBOX_SETUP_TR.md). On a supported environment, from the project root:

```sh
npm --prefix sandbox ci --ignore-scripts --no-audit --no-fund
node sandbox/check.mjs
python3 runner.py access --mode sandbox --record
```

The collector caches the pinned official binary using Python's standard HTTP client before starting the Node.js wrapper. First run downloads about 36 MB. npm dependencies use the sandbox-specific lockfile; they do not change the base Python app's requirements. Ordinary UI sandbox runs do not overwrite a recording; `--record` does so explicitly. After a successful capture, Python-only replay becomes available with `python3 runner.py access --mode replay`.

Allowance is a gas budget, not a blanket asset-spending cap on the target contract. Public view calls do not require an access key. The harness uses only ephemeral local balances, and normal completion removes the temporary node state. Raw public RPC replies and signed local test transactions are captured; private keys are not exported.

## Direct-model AI attestation

Open **Inspect a confidential AI report** (experiment 13). The bundled
GLM 5.3 Flash report came from a public direct-model endpoint with a fresh
client nonce. Replay checks the nonce, signer and declared TLS fingerprint
inside the quote, the configuration hash, the RTMR3 event log, and the debug
flag. A one-bit nonce change is the rejection control.

```sh
python3 runner.py ai_attestation --mode replay
```

The optional Intel verifier checks the quote chain against the bundled
collateral at the recorded capture time. It returned `UpToDate` in the
original verification. To repeat that check independently in Ubuntu:

```sh
python3 -m pip install --only-binary=:all: --target .attestation-deps dcap-qvl==0.7.1
PYTHONPATH="$PWD/.attestation-deps" python3 runner.py ai_attestation --mode replay
```

Use that same `PYTHONPATH` when starting `server.py` to show the Intel
verification in the browser. Without the dependency the app shows that
the signature chain has not been checked in the current run. The report
and collateral remain in the downloaded evidence. The live report request
uses the experimental direct endpoint and needs no API key. See the
[verification guide](https://docs.near.ai/cloud/verification/direct/model-attestation).
This experiment covers one report. A separate inference, GPU verdict and
same-connection peer certificate binding require their own checks.

## Onchain flows to the Intents buyback wallet

Open **Trace NEAR into the buyback wallet** (experiment 12). Three selected
Intents transactions were discovered through [NearBlocks](https://nearblocks.io/)
and verified using NEAR archival RPC replies. The verifier matches the Intents
withdrawal event to the wNEAR unwrap, follows the callback dependency and
checks the successful native NEAR transfer to the labeled wallet. The unwrap
return includes the one yoctoNEAR attached to the call. The final wallet credit
matches the withdrawal amount without that extra yoctoNEAR.

```sh
python3 runner.py treasury_flows --mode replay
python3 runner.py treasury_flows --mode live --record
```

The sample covers three finalized wallet inflows. A market purchase, prior
funding source, later disposition or protocol-wide burn needs separate records.
The [NEAR revenue dashboard](https://revenue.near.org/) supplies the wallet label.

## Historical Intents activity and wallet revenue

Open **Track Intents usage and wallet revenue** (experiment 11). It compares
13 September–12 October and 13 October–11 November 2026, inclusive UTC.
Every date must appear in the volume, gross fee and wallet revenue series.

```sh
python3 runner.py intents_history --mode replay
python3 runner.py intents_history --mode live --record
```

Replay uses the three bundled DefiLlama API responses. Live mode refetches
the same historical windows and can reflect upstream revisions. The
[volume adapter](https://github.com/DefiLlama/dimension-adapters/blob/master/dexs/near-intents/index.ts)
aggregates NEAR's daily Intents volume dataset. The
[fees adapter](https://github.com/DefiLlama/dimension-adapters/blob/master/fees/near-intents/index.ts)
sums gross swap fees and estimates wallet revenue from NEAR/wNEAR inflows
to three labeled wallets. Its filters exclude transfers between those wallets.
Both USD ratios divide the period total by swap volume and multiply by 10,000.
Revenue sweeps can lag swap activity, so the ratios are period comparisons.
Buyback execution, burns, and profit require separate evidence.

## Staking for Inference scenario

Open **From staking rewards to AI usage** (experiment 09). Enter a stake, an
assumed NEAR price and a net annual reward rate after validator commission.
Estimate the bill from monthly input and output token volumes and their
respective rates per million tokens.

```sh
python3 runner.py staking_inference --mode scenario
```

The average monthly credit estimate is stake × price × net annual reward rate
÷ 12. The token bill is the sum of input and output volume multiplied by their
respective rates. The calculator shows uncovered usage and the stake needed
to cover the assumed bill. Its three price rows use 0.5×, 1× and 1.5× the
assumed NEAR price with the other inputs held constant.

The defaults are illustrative. NEAR AI describes how rewards fund eligible
inference credits in its [Staking for Inference overview](https://docs.near.ai/cloud/staking-for-inference/overview).
The product's [calculator](https://docs.near.ai/cloud/staking-for-inference/calculator)
and [model rates](https://near.ai/pricing) are available for reference.

## Chain Signatures verification

Open **Verify a real Chain Signature** (experiment 08). Recorded mode is selected
when the bundled evidence is available. Run it with Python alone:

```sh
python3 runner.py mpc_signature --mode replay
```

The recording contains a finalized mainnet transaction from 10 November 2026
and the signer root public key read at the sign receipt's block. The verifier
follows the sign receipt to its successful callback and checks its domain,
digest and derivation tweak. It derives the public key from the calling
contract, path and historical root key. The recorded signature verifies for
the original digest and fails when a bit in the first byte is flipped. An
independent noble-curves check agreed with the derived key and both outcomes
during development. The app's replay has no Node.js dependency.

Use `python3 runner.py mpc_signature --mode live --record` to refetch the same
historical evidence from archival RPC. The module reads public data and
performs verification locally. This check covers the recorded ECDSA digest.
The underlying Bitcoin payload and settlement are outside the experiment.

## Global contracts comparison

Open **Deploy once, reuse across accounts** (experiment 07). It uses the same
Sandbox and npm dependencies as the access-key experiment. The harness compares
three regular deployments with one hash-based publication and three attachments
of the same WASM. Account state starts equivalent within each pair. Both paths
exercise the contract, and a state write checks that other accounts remain
independent.

```sh
node sandbox/global-contracts.mjs --check
python3 runner.py global_contracts --mode sandbox --record
python3 runner.py global_contracts --mode replay
```

The offline check compiles the WASM and checks the three transaction encodings.
The sandbox run waits for finalized outcomes, including refunds, before
measuring balances. The table reports gas, the change in spendable account
balance, and the storage reserve calculated from the protocol rate. The
publication charge is included in the publisher's balance change. The storage
reserve remains in the account balance. Account storage figures exclude
protocol-wide copies of shared code.

The bundled capture in `data/recordings/global_contracts.json` can be replayed with Python alone. A fresh run requires a Sandbox host with sufficient file descriptors and uses local test balances.

## Repeat the dry quote matrix

Open **Compare two dry quote rounds** (experiment 10). Replay compares the
same three routes at 25 and 250 USDC in two captures. The first round on
10 November 2026 had six usable previews. All six attempts in the second
round on 12 November timed out from the capture environment. The rows retain
those outcomes. A difference is calculated when a cell has usable quotes in
both rounds. These two observations do not estimate service uptime.

```sh
python3 runner.py quotes_repeat --mode replay
python3 runner.py quotes_repeat --mode live --record
```

Live mode pairs the existing `quotes.json` baseline with six fresh requests
under the same dry policy. With `--record`, the comparison is saved to
`data/recordings/quotes_repeat.json`. Each round retains its timestamp,
capture-source digest and evidence checksum. The live run can take up to
roughly 90 seconds if requests time out.

## Dry quote matrix

Open **From listings to route previews** (experiment 05). Its default is **Recorded data · recompute**, which requires no network or credentials. Select **Live preview · 6 requests** to collect a new snapshot. One run requests the catalog, then makes one preview attempt for each route/amount cell; it usually takes about 20–95 seconds. No wallet or transaction signing is involved.

The fixed routes are **NEAR → Base, Base → Solana and Solana → Ethereum**, using pinned USDC asset IDs at **25 and 250 USDC**. The script checks chain, symbol and six-decimal metadata before quoting. Inputs are token units, not an assumption that USDC equals exactly one USD. Public example addresses satisfy preview validation; they are not user wallets and must never be funded.

The included snapshot returned matching previews for **6 of 6 cells**. Request/response bodies, per-request start/end timestamps, HTTP statuses and observed response times are retained. HTTP failures, timeouts, malformed responses and missing pinned assets stay visible in the six-cell denominator. The runner does not silently replace live failure with a recording. A failed catalog request fails the run because the pinned assets could not be checked.

API response milliseconds are measured at this client; transfer seconds are the service's **unverified estimate**, not measured settlement. Minimum output reflects the request's 100-bps tolerance. Output differences must not be treated as isolated fees or price impact. Quote signatures are retained but not cryptographically verified. This small, selected snapshot is not a reliability or complete-stack superiority test. See [the experiment findings](docs/QUOTES_FINDINGS_TR.md).

## Economic assumptions

Six editable parameters: annual volume, retained revenue basis points, purchase allocation share, token purchase price, annual issuance assumption and burn share. **None of the defaults claim to be current NEAR measurements.**

The model calculates retained revenue → purchase allocation → tokens purchased → tokens burned. Net modeled supply change is issuance minus burns, with other supply events excluded. Purchased tokens retained in a treasury are not burned. At zero burn share, purchases do not reduce total supply in this model. The chart changes volume while holding all other assumptions constant; bar lengths show absolute magnitude and labels retain the sign.

## Hubble in Labs

Hubble walks readers through the thesis, its sources and the experiment controls. Select **Show All Theses**, choose a thesis, then select **Let’s experiment** to open its evidence tools. Source-based topics open their references. Hubble uses scripted navigation and authored explanations. No model or API key is needed.

## Source visibility and evidence integrity

The source tabs show the selected experiment plus its shared HTTP helpers, runner and registry. Each run records the current source digest and evidence digest. Replay also includes the source digest from capture time; a changed analyzer remains visible rather than being presented as the original version. A failed checksum rejects the record.

Checksums are tamper checks relative to the saved record, **not provider attestations or an independently trusted timestamp**. RPC data here is trusted from the queried public provider; this app does not verify a NEAR light-client proof. The two Sandbox experiments sign local test transactions using ephemeral keys. Public-data experiments and the payment rehearsal perform read-only analysis or dry quote requests. The server runs named Python functions from a fixed registry, not arbitrary shell or model output. Secrets remain server-side and are never included in result downloads.

After editing Python experiment/runner source, restart the server. A source-digest guard rejects execution when files changed since process startup, so displayed files are not silently paired with already-imported older code.

## Layout

| Path | Role |
|---|---|
| `server.py` | Local HTTP service and fixed API routes |
| `catalog.py` | Claims, sources and allowlisted experiments |
| `runner.py` | CLI, capture, replay and evidence hashes |
| `experiments/` | Inspectable collectors and deterministic analyzers |
| `agent.py` | Optional NEAR AI chat transport and result narration |
| `guide.py` | Local topic routing and constrained model recommendations |
| `web/` | Buildless HTML/CSS/JavaScript interface |
| `data/recordings/` | Public observations, dry quotes and local Sandbox evidence for offline replay |
| `data/fixtures/` | Fixed quote input for the payment rehearsal |
| `docs/PLAN.md` | Next milestones and research gates |
| `tests/` | Offline behavior and integrity checks |

## Research status

The evidence covers specific capabilities, historical activity and selected wallet flows. The investment thesis depends on repeated usage and how that activity contributes to NEAR. Integration effort, completed settlement in the rehearsal and comparative performance against another stack remain unmeasured.

Public source URLs appear next to each experiment and in `docs/RESEARCH_PREPARATION_TR.md`. Third-party API data remains subject to its source's terms; the MIT license below applies to our code, not to ownership of the provider data or third-party documentation. Snapshot scope is limited to public technical metadata.

## License

Original project code: MIT. Source documentation is linked, not republished in full. The Sandbox recordings use ephemeral accounts and test balances. The project contains no private keys.
