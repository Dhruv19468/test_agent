# Test Plan — Email Purchase Order Entry Automation (MVP1)
Version: 1.0  
Date: 2026-03-XX  
Author: QA Lead

Table of contents
- Introduction & Purpose
- Objectives
- Scope (In scope / Out of scope)
- Test Items
- Test Strategy & Approach
- Test Types and Coverage
- Test Cases / Scenarios (key cases & samples)
- Test Data Requirements
- Test Environment, Tools & Mocks
- Test Schedule & Milestones
- Roles & Responsibilities
- Entry / Exit Criteria
- Acceptance Criteria & Traceability
- Defect Management and Reporting
- Test Automation Strategy
- Non-Functional (Performance, Security, Observability) Testing Details
- UAT & Pilot Plan
- Risks, Assumptions & Mitigations
- Deliverables & Sign-off

---

## 1. Introduction & Purpose
This test plan defines the QA approach, scope, environments, test types, data, schedule and acceptance criteria for MVP1 of the Email Purchase Order Entry Automation project. MVP1 ingests PO emails (body + attachments), extracts header/lines via Azure Document Intelligence / Azure OpenAI, matches items, validates via SAP APIs and creates draft sales orders for CSR review (no auto-release).

## 2. Objectives
- Validate functional correctness of email intake, extraction, matching, SAP validation and draft order creation.
- Validate RBAC (branch-based queue access) and security (Azure AD).
- Validate non-functional requirements: draft order creation latency (≤5 minutes for 95% of POs), peak throughput (300 emails/hour), availability (design verification for 99.5% 24x5).
- Verify acceptance criteria from BRD (header ≥95% accuracy, line ≥90% accuracy on pilot; duplicate detection 100% for test set; no automatic release).

## 3. Scope
In scope (MVP1):
- Mailbox ingestion via Microsoft Graph and Event Grid.
- Extraction of header fields and lines from email body + PDF/Excel attachments using Azure Document Intelligence and Azure OpenAI.
- Customer identification (sender domain + PO content).
- Item matching via customer cross-reference and fallback to catalog (Azure AI Search).
- SAP validation through APIM: customer active, material valid, price variance flagging (>5%).
- Draft sales order creation in SAP (draft only).
- CSR review queue (Web UI) with field confidence display and correction capability.
- Duplicate PO detection by customer PO number.
- Observability: end-to-end traceability for test cases.

Out of scope:
- EDI orders, straight-through release (MVP2), acknowledgements, returns/credits, analytics (MVP2).

## 4. Test Items
- Order Extraction Service (parses emails, calls AI services)
- Order Creation Service (validation, SAP APIM interactions)
- Web UI (CSR Review Queue)
- Azure integrations: Document Intelligence, OpenAI, AI Search
- Message/Eventing: Event Grid, Service Bus
- Data stores: Blob Storage (email copies), Cosmos DB (drafts)
- Identity: Azure AD (RBAC)
- Integration connectors: Microsoft Graph (mailboxes), SAP S/4HANA (APIM)
- Supporting: Logging/Tracing (Datadog / Azure Monitor)

## 5. Test Strategy & Approach
- Testing phases:
  - Smoke / Sanity tests on each deployment
  - Component / Unit tests (dev-owned but QA to verify coverage & results)
  - Integration tests using test doubles for external systems where necessary
  - System / E2E tests using staging instances of Graph API, SAP test system, and Azure AI test keys
  - Performance & Load tests (throughput & SLA)
  - Security & Access control tests
  - Regression tests on every release
  - UAT with CSRs and CS Supervisor on pilot branches
- Shift-left: collaborate with devs to define contract tests for APIM/SAP and message contracts on Service Bus.
- Risk-based testing: prioritize flows that impact customer orders, duplicate detection, SAP validations and visibility to CSRs.

## 6. Test Types and Coverage
- Functional
  - Happy path single PO (email body + PDF attachment)
  - Multiple attachments, Excel, mixed formats
  - Missing/partial headers
  - Multi-line POs, UoM variations, price present/absent
  - Cross-reference match and fallback to catalog
  - Duplicate PO detection
  - SAP validation flags (customer inactive, material invalid, price variance >5%)
  - Draft creation correctness and saved confidence metadata
  - CSR corrections persisted and applied
- Integration
  - Graph API -> Event Grid -> Service Bus -> Extraction Service flow
  - APIM -> SAP validation/draft creation
  - AI services invocation and error handling
  - Blob & Cosmos DB persistence
- System / E2E
  - Full flow from inbound mail to draft appearing in CSR queue and trace linking to SAP draft number
- Performance & Load
  - Throughput: 300 emails/hour sustained (baseline), peak bursts, concurrency
  - Latency: draft created within 5 minutes for 95% of POs
  - Stress tests beyond expected peaks and validate queueing/retries
- Reliability / Resilience
  - Retry logic for transient APIM failures, message redelivery
  - Handling of long-running AI extraction
- Security
  - Azure AD SSO validation, RBAC (branch scoping)
  - Secrets management (Key Vault)
  - Data-in-transit (HTTPS), data-at-rest (Blob/Cosmos encryption)
  - PII handling and masking in logs
  - Pen test of web UI and APIs (OWASP Top 10)
- Observability / Monitoring
  - End-to-end traceability exists for each processed mail
  - Metric collection: processing time, extraction confidence distribution, CSR correction rate, errors
- AI-specific
  - Validate confidence scoring semantics and thresholds
  - Adversarial/edge-case documents (unusual layouts)
  - Drift test cases (unexpected vocabulary)
- Accessibility & Usability
  - Web UI basic accessibility (keyboard navigation, screen reader labels) for CSR usability tests

## 7. Test Cases & Scenarios (Key / Representative)
Each test case will be assigned an ID; below are representative ones. All test cases will reference BRD requirement IDs in the traceability matrix.

Functional / E2E

- TC-FUNC-001 — Happy path: Single PO email with PDF attachment
  - Steps: Send PO email to branch mailbox with header fields and 2 lines in PDF; monitor pipeline.
  - Expected: Draft created in Cosmos within 5 minutes; header fields extracted (≥95% accuracy), both lines matched to materials via customer cross-ref; confidence values present; draft visible in CSR queue for branch; no release flag set.

- TC-FUNC-002 — Excel attachment with multiple lines and mixed UoM
  - Expected: All lines extracted, UoM normalized to SAP UoM; unmatched UoM flagged.

- TC-FUNC-003 — Unknown customer part numbers
  - Steps: Lines use customer part numbers not in cross-ref and found by catalog.
  - Expected: Fallback to catalog returns materials; where no catalog match, line flagged with low confidence and highlighted in UI.

- TC-FUNC-004 — Price variance >5%
  - Steps: Price present in PO that differs from SAP price by >5%
  - Expected: Line flagged as price variance; draft created and flagged for CSR review; no automatic release.

- TC-FUNC-005 — Duplicate PO detection
  - Steps: Send two emails with same customer PO number within short window
  - Expected: Second email is detected as duplicate; system prevents duplicate draft creation; flag/alert and link to existing draft.

- TC-FUNC-006 — Missing mandatory header (sold-to or ship-to)
  - Expected: Draft either fails mandatory validation and is held for manual processing; system surfaces missing fields with low confidence; CSR UI shows TODO.

- TC-FUNC-007 — CSR correction flow
  - Steps: CSR edits line quantity and material and saves
  - Expected: Changes persist to Cosmos DB; audit trail recorded; correction metrics updated.

Integration / Error scenarios

- TC-INT-001 — SAP API returns 5xx transient error during validation
  - Expected: Retry per backoff policy; on continued failure, message put to retry queue and alert generated.

- TC-INT-002 — AI service degraded / times out
  - Expected: Extraction service times out gracefully, places email into exception queue with reason; partial extraction persisted where possible.

Performance / Load

- TC-PERF-001 — Sustained throughput 300 emails/hour
  - Steps: Simulate 300 inbound emails evenly across hour
  - Expected: System processes ≥95% within 5 minutes; queue length remains stable; no message loss.

- TC-PERF-002 — Burst of 500 emails in 30 minutes
  - Expected: System queues and processes with graceful degradation; no data loss; SLA may not be met for all but no system crash.

Security & RBAC

- TC-SEC-001 — Branch-based access control
  - Steps: CSR from branch A logs in and queries queue
  - Expected: CSR sees only branch A drafts; attempt to access branch B draft returns 403.

- TC-SEC-002 — Azure AD SSO and token expiry
  - Expected: SSO works; expired tokens cause redirect to login; service tokens rotated per Key Vault settings.

Observability

- TC-OBS-001 — Trace continuity
  - Steps: Process a test mail and retrieve trace ID
  - Expected: Trace links event grid id -> service bus -> extraction -> APIM call -> SAP draft number; trace visible in Datadog/Azure Monitor.

AI-specific

- TC-AI-001 — Confidence scoring thresholds
  - Steps: Create inputs that generate high/medium/low confidence per field
  - Expected: Confidence values correctly assigned and UI highlights low-confidence fields.

- TC-AI-002 — Unusual layout robustness
  - Steps: Send POs with non-standard layout or inline scanned images
  - Expected: Extraction returns partial data, flags low confidence; no incorrect high-confidence extractions.

Acceptance & Criteria Verification

- TC-ACC-001 — Acceptance Accuracy on Pilot Data
  - Steps: Run batch of pilot POs (sample set)
  - Expected: Achieve ≥95% header accuracy and ≥90% line accuracy.

- TC-ACC-002 — Draft within 5 minutes for 95% of POs
  - Steps: Execute representative set and measure times
  - Expected: 95% within SLA.

A full test case catalog will be maintained in the test management tool (e.g., Azure DevOps Test Plans) with steps, data, expected results, prerequisites, and links to logs/traces.

## 8. Test Data Requirements
- Test mailboxes per branch (staging mailboxes) and service accounts for Graph API.
- Sample PO emails:
  - Variety of layouts (standard, non-standard, scanned image, inline text).
  - Attachments: searchable PDFs, scanned PDFs (OCR), Excel PO templates.
  - POs with/without prices, different UoMs, multiple lines, currencies.
- Customer cross-reference files: valid, partial, and missing entries.
- Catalog index for AI Search (sample/partial).
- SAP test master data: customers (active/inactive), materials (valid/invalid), pricing entries (varied) in SAP test environment via APIM.
- Duplicate PO test set.
- Synthetic PII masked but realistic customer/sold-to/ship-to datasets. Use synthetic test data; production data may be cloned after masking and approvals.
- Test accounts to simulate AI model responses (mocked for deterministic tests).

Data privacy: All real customer data must be masked. Obtain approvals for any production-data use.

## 9. Test Environment, Tools & Mocks
Environments:
- Dev: unit/component tests
- QA/Staging (Non-production Azure subscription) — full integrated environment described in architecture doc (APIM, Event Grid, Service Bus, AKS, Blob, Cosmos DB)
- SAP Test/Mock instance reachable via APIM (stubs available if SAP staging is unavailable)
- AI Service test keys and sandbox models; ability to route AI calls to deterministic mock service for repeatable tests.

Tools:
- Test management: Azure DevOps Test Plans (or equivalent)
- CI/CD: GitHub Actions
- Automation: Playwright or Selenium for Web UI; API tests via Postman/Newman or REST-assured; load tests with k6/JMeter
- Monitoring: Datadog, Azure Monitor logs, Application Insights
- Secrets: Azure Key Vault
- Mocks/Stubs: Local/remote mock for SAP APIM, Graph API (if mailbox access is regulated), and AI services (to simulate errors and stable outputs)

Mocking strategy:
- Create deterministic AI response mocks for unit/integration tests.
- For full E2E, use sandbox AI endpoints if available, otherwise record-and-replay responses.
- SAP should have a test system; if unavailable, use APIM stub that simulates typical SAP responses including errors and rate limit responses.

## 10. Test Schedule & Milestones
High-level (align with BRD MVP1 Apr–Jul 2026):
- Test planning & env setup: Mar–Apr 2026
- Component & Integration testing (Dev/QA): Apr–May 2026
- System/E2E testing: May–Jun 2026
- Performance & Security testing: Jun 2026
- Pilot & UAT with selected branches: Jun–Jul 2026
- Regression & Final Acceptance: late Jul 2026
Specific dates to be added to project schedule once dev sprint plan locks.

## 11. Roles & Responsibilities
- QA Lead (Author): Test plan, strategy, lead test execution, report metrics
- QA Engineers: Create/execute tests, automation, performance tests
- Dev Engineers: Unit tests, contract tests, fix defects
- Integration Engineers: SAP, Graph API connectivity, test stubs
- CSRs / CS Supervisor (Pilot): UAT execution and feedback
- CS Admin: Provide cross-reference files and mailbox access
- Security Team: Pen testing & security review
- AI Governance Council: Approve test use of AI services and datasets

## 12. Entry / Exit Criteria
Entry criteria for QA/System tests:
- Dev build deployed to QA/staging
- Service Bus, Event Grid, APIM endpoints configured
- Test mailboxes and SAP test endpoints available
- Test data and samples loaded (cross-ref, catalog, SAP master data)
- Mocks available for AI services (if needed)

Exit criteria to move to UAT:
- All critical & high severity defects resolved
- Smoke tests passed
- Regression pack executed successfully
- Performance tests passed or documented mitigations accepted
- Acceptance metrics met on QA samples (pre-UAT)
- Security & data governance approvals obtained

Exit criteria for MVP1 release:
- Acceptance criteria in BRD met on pilot (≥95% header accuracy, ≥90% line)
- Draft within 5 minutes 95% for pilot
- No orders released automatically
- Duplicate detection validated on test set
- UAT sign-off from CS Owner and AI Governance Council

## 13. Acceptance Criteria & Traceability
Map key BRD requirements to test coverage:
- Mailbox intake via Graph: Integration tests of Event Grid -> Service Bus pipelines; TC-INT-xxx
- Extraction of header/lines: Functional tests TC-FUNC-001..003, AI tests TC-AI-001..002
- Customer identification: Functional tests verifying domain and content matching
- Item matching (cross-ref then catalog): TC-FUNC-003 and negative cases
- SAP validation (active, material, price variance >5%): TC-FUNC-004, TC-INT-001
- Draft creation and CSR review queue: TC-FUNC-001, TC-FUNC-007
- Duplicate detection 100%: TC-FUNC-005
- No release in MVP1: TC-FUNC-001 + additional checks
- Performance SLA (draft within 5 mins, 95%): TC-PERF-001
- Availability / observability: Monitoring & trace tests TC-OBS-001

Acceptance will be signed off when all mapped tests for acceptance criteria pass in pilot UAT.

## 14. Defect Management & Reporting
- Tool: Azure DevOps (or Jira) for defect logging/tracking.
- Severity levels:
  - P0/Critical: Data loss, incorrect draft leading to wrong shipped order if released, system down.
  - P1/High: Major functional failure (duplicate not detected, SAP validation incorrect).
  - P2/Medium: UI issues, incorrect confidence display, partial extraction.
  - P3/Low: Cosmetic, minor logging issues.
- SLA for resolution aligned with release schedule; critical defects block UAT sign-off.
- Daily defect status in test execution phase; weekly summary reports to stakeholders otherwise.

## 15. Test Automation Strategy
- Automate smoke tests (build validation), regression suite for functional core flows, API contract tests, and UI critical paths.
- Automate API tests for Order Extraction → Order Creation interactions using Postman/Newman or REST-assured.
- Automate load tests via k6 for performance scenarios.
- CI: run automated test suites in GitHub Actions on PR merge and nightly.
- Maintain test data seeds and deterministic AI mocks for automated runs.
- Manual testing for exploratory, AI edge cases, UX and UAT with CSRs.

Regression pack (examples):
- Smoke: ingest email -> draft appears
- Regression functional: extraction accuracy on canonical templates, duplicate detection, SAP validation paths, CSR save/correction
- Security/regression: RBAC checks

## 16. Non-Functional Testing Details

Performance
- Test objectives:
  - Verify sustained throughput 300 emails/hour
  - Verify processing latency: 95% within 5 minutes
- Metrics collected: end-to-end processing time per email, queue depth, time in each service, APIM latency, AI call latencies
- Test design:
  - Steady-state test (300/hr)
  - Burst tests (500 in 30 min)
  - Soak test (24 hours at moderate volume)
- Accept criteria: 95% within 5 minutes for baseline test; no unhandled exceptions; backpressure works.

Availability & Resilience
- Verify retry/backoff on transient APIM/SAP failures
- Simulate service unavailability (AI / SAP) and validate fallback to exception queue and alerts
- Validate data persistence and reprocessing after outages

Security
- Tests:
  - Authentication: valid & invalid Azure AD tokens, expired tokens
  - Authorization: branch scoping checks
  - Input validation / OWASP Top 10 for web UI & APIM endpoints
  - Secrets & key rotation checks
  - Data masking & logs: ensure PII not logged in plaintext

Observability
- Confirm trace ID is generated and propagated across Event Grid, Service Bus, services and APIM calls, and linked to SAP draft number
- Verify dashboards for processing rate, latency, and error rates
- Ensure alerts defined for processing failure thresholds

AI Governance & Model Behavior
- Validate model behavior on corner cases and model hallucination risk mitigation
- Test confidence score thresholds and UI highlighting
- Ensure AI Governance Council approvals for model usage and test data

## 17. UAT & Pilot Plan
- Participants: Selected CSRs from 3 pilot branches + CS Supervisor + CS Admin
- Scope: End-to-end tests using real (masked) pilot customer data; CSR workflow for review & correction
- Duration: 2–3 weeks
- Acceptance: Use BRD acceptance criteria and KPI monitoring (draft accuracy, time to draft, CSR correction rate)
- Feedback loop: Triage of findings daily; adjustments to thresholds, UI tweaks or AI model prompts before broad rollout.

## 18. Risks, Assumptions & Mitigations
Risks
- AI extraction inconsistent on unusual PO layouts → Mitigation: thorough edge-case testing, highlight confidence, keep CSR review mandatory.
- SAP integration limits / rate limiting → Mitigation: implement queueing/retries and throttling; test APIM behavior under load.
- Mailbox access delays/permissions → Mitigation: early coordination with mailbox owners; create test mailboxes.
- Production data privacy concerns → Mitigation: mask production data; obtain approvals.

Assumptions
- Cross-reference files available for top customers as per BRD.
- SAP test environment or reliable APIM stubs available for test.
- Azure AI test/sandbox accounts available.

## 19. Reporting & Metrics
During test phases provide:
- Daily test execution & defect summary (during test sprints)
- Weekly QA status reports: progress vs schedule, outstanding high/critical defects
- Pilot KPIs: header & line accuracy, time to draft distribution, CSR correction rate, duplicate detection rate
- Final QA report: test coverage, defects, unresolved risks, acceptance results

Key metrics to capture automatically via monitoring:
- Emails processed per hour, per branch
- Processing time percentiles (p50/p90/p95)
- Extraction confidence distributions
- CSR correction rate & common correction types
- Duplicate detection success rate
- Number of failed drafts / exception queue items

## 20. Deliverables
- This Test Plan (document)
- Test cases suite (Azure DevOps)
- Automated test scripts & CI pipeline entries
- Performance test scripts & reports
- Security & Pen test report
- UAT results & sign-off
- Final QA Summary & Acceptance Evidence (logs, traces, metrics)

## 21. Sign-off
- QA Lead: [Name / signature / date]
- Business Owner (Customer Service Operations): [Name / signature / date]
- Dev Team Lead: [Name / signature / date]
- AI Governance Council rep: [Name / signature / date]

(Actual sign-off fields to be appended to final document.)

---

If you want, I will:
- produce the full enumerated test-case spreadsheet with step-by-step steps, expected results and test data, or
- create automation skeletons (Postman collections, k6 load scripts) for the key API flows. Which would you prefer next?