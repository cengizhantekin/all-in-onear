# Validation — 0.5.0

## Access-key harness status — runtime not verified

- 40 Python unit checks passed; access-key cases use explicitly synthetic parser fixtures, never installed in data/recordings.
- The real WAT source compiled and passed WebAssembly validation. The signed denied-method transaction was encoded/decoded offline; no SDK permission lookup prevented its construction.
- The official 2.14.0 binary downloaded successfully but refused to start, including its version command: required NOFILE 65535, environment hard/soft limits 16384. No permission case actually ran on a node.
- No access.json capture is bundled. Fresh execution and replay remain unavailable until prerequisites or a real capture exist. Existing five modules are retained.
- Windows user confirmed WSL/Ubuntu is not installed. Setup is the next user-side dependency.

## Previously verified v0.4 checks

- Runtime: Python 3.12.14, standard library only; no pip packages.
- 32 unittest checks passed, including all four recorded observations, economic assumptions, guide routing/validation, HTTP session controls and new dry quote boundaries.
- A real six-cell live quote matrix was captured on 2026-11-10, 13:21:01–13:21:56 UTC. Six matching dry preview structures returned HTTP 201. Capture source digest still matches the delivered experiment/common/runner/catalog source.
- Every planned cell is retained. Offline synthetic fixtures check HTTP errors, transport timeouts, invalid/mismatched quotes, wrong dry flags, deposit metadata, missing assets and changed decimals. These injected failures are tests, not failures asserted in the six-cell live snapshot.
- Preview transport rejects dry=false, integer 1 and missing dry values before HTTP; redirects are not followed. Generic fetch_json does not allow the quote endpoint.
- Browser UI: direct quote selection, replay, six-row result matrix and quotes → economics → quotes transitions checked. Existing scenario chart and result table behavior remain intact.
- JavaScript syntax: node --check web/app.js passed.

## Scope and limits

- Browser QA used recorded quotes. The live matrix was run through the same Python collector from the CLI; a second live browser matrix was not requested.
- The user has confirmed the earlier Windows app and four original modules worked. This new quote module has not yet been exercised on the user's Windows machine; mobile viewport behavior was not directly checked.
- No real API key: live NEAR AI calls, model compatibility/cost and TEE verification remain untested. Model transport/response checks use mocked responses.
- No MPC signature, sandbox access-key test, executed swap, settlement measurement or independently verified quote signature is included.
- GitHub publication and hackathon submission have not occurred.

See QUOTES_FINDINGS_TR.md for the fixed protocol, full six-row findings, setup probes and inference limits.
