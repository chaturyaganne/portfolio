# Relay - grounded service triage

A self-initiated Applied AI FDE portfolio project by Chaturya Ganne. The public website is a working local retrieval and rule-based planning demo on fictional tickets and knowledge. It is not a ServiceNow product or a production deployment.

Public project: https://chaturyaganne.github.io/portfolio/relay/
Personal portfolio: https://chaturyaganne.github.io/portfolio/

## Try it in 90 seconds

1. Load **VPN connection** and run the workflow. Inspect the proposed owner, cited checks, knowledge cards, and trace.
2. Open a source and compare it with the proposed work note. Review the sample proposal to prepare a ServiceNow-shaped dry-run payload.
3. Edit the request. The previous result and approval are invalidated.
4. Try **Security escalation**, **Missing knowledge**, **Permission boundary**, and **Untrusted instructions**.
5. Run the evaluation suite. Its numbers are calculated from the included fixtures, not prefilled performance claims.

The public browser experience never calls a model or sends ticket data to a backend. It processes fictional input in memory. Exports are files downloaded to the user's device. There is no tracking, persistent ticket storage, or real ServiceNow write.

## Run the full local project

Requires Node 22 or later.

```bash
npm run build
npm start
```

Open the printed loopback URL, normally http://127.0.0.1:4178. The default API mode uses the same deterministic core as the public site. The production dependency count is zero.

### API contract

`GET /api/health` reports whether an optional model was configured and explicitly reports `writesEnabled: false`.

`POST /api/plan` accepts:

```json
{
  "title": "VPN tunnel error 809 after laptop update",
  "details": "Internet works but the VPN shows error 809 after a laptop update.",
  "role": "support",
  "mode": "local-extractive"
}
```

Response fields include `decision`, `owner`, `sources`, `steps`, `draft`, `trace`, `metrics`, and a non-cryptographic change-detection digest. Request size and field lengths are bounded. There are no API routes for external ticket writes.

### Optional real local-model path

Install and run Ollama separately and make a model available through its standard local service. This repository does not install a model or claim that a model inference was exercised here.

PowerShell example, using the name of a model you have already installed:

```powershell
$env:OLLAMA_MODEL = 'YOUR_INSTALLED_MODEL'
npm start
```

The UI exposes the optional model checkbox only when the local server reports a configured model. It requests `mode: "ollama"` from the Node API, which calls Ollama's `/api/chat` with a JSON schema. `OLLAMA_BASE_URL` can select another **loopback** Ollama address. Remote destinations are rejected by this prototype adapter.

The model receives permitted retrieved evidence and untrusted ticket text. Its output is restricted to a summary and source IDs; the adapter rejects malformed fields and citations outside the retrieved set. The model cannot change the route, approval state, or payload. A citation allowlist does not prove factual consistency. A human still needs to inspect the summary. On a model failure, the UI reports the failure; the user can explicitly rerun without model mode.

## What is implemented

- Active-status and sample-role filtering **before** retrieval.
- BM25-style lexical scoring with term frequency, document frequency and length normalization. Two matching non-stopword terms and a minimum lexical score are required. Scores are not confidence probabilities.
- Extractive checks and work notes sourced from the leading permitted article.
- Rule-based security escalation, explicit abstention, and narrow instruction-override blocking.
- Reviewer confirmation and change detection before a dry-run payload export.
- Shared core in the browser and Node API, with an optional local-model adapter.
- Six repeatable synthetic fixtures and automated unit, API, and UI behavior checks.
- A trace with actual local retrieval/policy elapsed time. No fabricated latency or business-impact numbers.

## What is simulated or incomplete

- **Roles:** client-switchable examples, not authentication. The entire fictional corpus is public. Deployments must enforce permissions on a trusted server; the local API also accepts a caller-supplied demo role and is not an authorization service.
- **Approvals:** a self-declared reviewer label in browser memory, not an authenticated approval or durable audit event. The digest only detects accidental proposal changes; it is not a signature or tamper-resistant control.
- **ServiceNow:** a correctly shaped sample `PATCH /api/now/table/incident/{sys_id}` with a placeholder sys_id and `work_notes` only. No ServiceNow instance, credentials, record lookup, assignment-group resolution, authentication, or network write is implemented.
- **Policy:** transparent example rules, not a general prompt-injection defense or safety guarantee.
- **Knowledge:** seven synthetic articles. No document ingestion, embedding model, vector database, persistent index, or real customer corpus.
- **Evaluation:** six synthetic regression fixtures, not a retrieval benchmark, customer study, or model-quality certification. Real model inference and browser visual/assistive-technology QA must be verified separately.

## Customer discovery and next iteration

The assumed customer is a service-desk team that needs to route incidents with useful evidence. This is a hypothesis, not an interview finding. For a real pilot, observe several handoffs, label routing/evidence expectations with subject-matter experts, and define a baseline review workflow.

Measure review effort, routing errors, citation support, abstention quality, and operator overrides using an agreed evaluation set. Establish baseline and acceptance thresholds before implementation changes. Add server-side identity and document authorization, tenant boundaries, durable auditing, secret management, safe integration retries, and load testing before connecting real systems. Add semantic retrieval only when a larger corpus and evaluation show a benefit.

## Tests

```bash
npm install
npm test
```

`jsdom` is a development dependency only, for DOM behavior tests. The native dialog is mocked in these tests; they do not certify browser layout or accessibility. Model-adapter tests use a mock service, not a live LLM.

## File map

`data.json` fictional corpus, scenarios and fixtures; `core.js` retrieval, policy, approvals and evaluation; `app.js` browser interaction; `server.cjs` local HTTP API and model adapter; `site.css` responsive interface; `tests.cjs` regression checks; `build.cjs` static packaging.

## Role context and technical references

Matt's supplied hiring post describes a builder-heavy Applied AI & ML FDE team working on GenAI customer scenarios alongside AI research. This project responds to that scope; it does not claim to reproduce his team's architecture.

- [ServiceNow public Applied AI FDE role](https://careers.servicenow.com/jobs/744000154154044/forward-deployed-solution-engineer-applied-ai-fde/): end-to-end builds, APIs, orchestration, UI, reusable patterns and production delivery. This public listing is senior; it is not assumed to be the precise opening from Matt's post.
- [Ollama structured output documentation](https://ollama.com/blog/structured-outputs): schema-based output on the local chat endpoint.
- [ServiceNow Table API](https://www.servicenow.com/docs/r/xanadu/api-reference/rest-apis/c_TableAPI.html): the basis for the dry-run endpoint shape.

AI assistance supported implementation and documentation. Review and understand the retrieval, policy, API, and evaluation code before presenting the project in a technical conversation.
