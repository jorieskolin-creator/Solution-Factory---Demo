# CSCF Demo — Solution Assurance Engine

A scripted, AI-free demonstration of the Continuous Solution Creation Flow. The factory has three production lines. Only Line 1 accepts the prepared Solution Assurance Engine New Build Brief. Lines 2 and 3 always reject selected material.

## Use the demonstration

1. Select **Download Demo Input Document**. Keep its contents unchanged; renaming the file is allowed.
2. Add that DOCX with **New Build** on Line 1, then select **Start Build**.
3. Follow eight stages and 21 tasks over 150 seconds. Pause or inspect reached stages whenever needed. Switching away from the tab automatically pauses the build; resuming is explicit.
4. At the release gate, review or download the fixed Document of Approval. **Approve & Deploy** and **Save & Continue Later** both display **DEMO ENDED**. They do not deploy, save, grant approval or contact an external service.
5. Restart to repeat the scenario.

Uploads are read in browser memory and checked using SHA-256 through the Web Crypto API. They are never sent to the server, retained in browser storage or passed to an AI service. Filenames and extensions do not establish acceptance. An edited or re-saved document must be rejected. The SHA-256 comparison requires HTTPS or localhost.

## Documents and scenario

- `public/documents/SAE-CSCF-New-Build-Brief-v1.0.docx`: the single accepted input, **CSCF-SAE-NB-001**, version **1.0**.
- `public/documents/SAE-Document-of-Approval-v1.0.pdf`: the fixed, seven-page approval package, marked **Approval pending** with **PASS — SIMULATED** records.
- `src/scenario.json`: the shared purpose, ten requirements, measurable acceptance criteria, deliverables, verification scenarios and workflow descriptions.
- `src/asset-manifest.json`: finalized document fingerprints and identity.
- `scripts/create-documents.py`: deliberate authoring workflow. Creates the DOCX first, fingerprints it, then prepares its matching PDF and manifest. Regenerating changes the accepted bytes: distribute the new pair and rebuild together. This is never run during a demonstration or production build.

The future SAE specification includes bounded, governed AI capabilities. This demo simulates those activities with prepared descriptions and evidence. Its results do not establish assurance, compliance or operating effectiveness for an actual SAE implementation. Runtime elapsed times appear only in the application; the PDF contains fixed scenario records.

The original reference documents in this repository are preserved. Synced ChatGPT project sources were used as read-only references and are not packaged as editable application source.

## Run locally

Use Node.js 22.18 or later and the pinned pnpm version in `package.json`.

```sh
corepack enable
pnpm install --frozen-lockfile
pnpm run verify:assets
pnpm test
pnpm run build
pnpm start
```

Open `http://localhost:3000`. For development use `pnpm dev`.

The small Express production server serves the Vite build and exposes `GET /health`. It listens on Railway's `PORT` and `0.0.0.0`. It has no upload, AI, approval or deployment endpoints, databases or secrets.

## Railway deployment

Deploy this repository's `codex/cscf-demo` branch into project **CSCF Demo**, one service **cscf-demo**. `railway.toml` defines the asset verification, tests, build, start and health check. Railway supplies the port. Connect a generated Railway HTTPS domain to the service. No environment secrets are required.

## Verification

Automated tests cover accepted and renamed input bytes; changed, unrelated, empty, oversized and unreadable inputs; guaranteed Line 2/3 rejection; stage order and timing; pause, hidden-tab and delayed-frame behavior; terminal state/timer protection; requirement references and fixed report integrity. Each task remains readable for seven seconds, with ten seconds for the final assembly. Delayed frames cannot skip whole tasks.

The finalized six-page DOCX and seven-page PDF were rendered and visually reviewed. Text extraction verified that every acceptance criterion is present in both documents and that the PDF repeats the accepted input fingerprint. Browser checks cover intake, rejection/retry, stage inspection, pause/resume, ending actions, keyboard operation and responsive layouts.
