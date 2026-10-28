# Test Plan — Email Purchase Order Entry Automation (MVP1)
Version: 1.0  
Date: 2026-03-xx  
Prepared by: QA Lead

Table of contents
1. Overview and Objectives  
2. Scope (In / Out)  
3. Test Strategy and Approach  
4. Test Types and Coverage  
5. Test Environment(s) & Tools  
6. Test Data & Test Mailboxes  
7. Test Deliverables & Artifacts  
8. Roles & Responsibilities  
9. Entry / Exit Criteria and Acceptance Criteria Mapping  
10. Test Schedule / Milestones  
11. Test Cases (structure, representative cases, and suites)  
12. Automation Strategy  
13. Performance & Load Test Plan  
14. Security, Privacy & Compliance Test Plan  
15. Observability / Logging / Traceability Tests  
16. Defect Management & Reporting  
17. Risks, Assumptions & Mitigations  
18. Sign-off

---

1. Overview and Objectives
- Purpose: Validate that the Email Purchase Order Entry Automation (MVP1) ingests branch PO emails and attachments, extracts header and line data, identifies customer and ship-to, matches items using customer cross-reference/catalog, validates via SAP, creates draft sales orders in SAP for CSR review, and meets functional and non-functional requirements in the BRD.
- Primary test objectives:
  - Functional correctness: header/line extraction, matching, SAP validation, draft creation, queue behavior.
  - Data accuracy: meet acceptance thresholds (≥95% header accuracy, ≥90% line accuracy on pilot customers).
  - Performance: 95% of drafts created within 5 minutes; handle peak 300 emails/hour.
  - Security & compliance: Azure AD auth, branch-based RBAC, data confidentiality.
  - Resilience/observability: end-to-end traceability, retries on transient failures.
  - Prevent release of orders in MVP1 (no straight-through release).

2. Scope
- In-scope (MVP1):
  - Mailbox monitoring via Microsoft Graph, ingest of email body and attachments (PDF, Excel, common image formats).
  - Duplicate PO detection by customer PO number.
  - Extraction (Azure Document Intelligence + Azure OpenAI) of customer PO number, sold-to, ship-to, requested delivery date, lines: customer part, description, qty, UoM, price.
  - Customer identification (sender domain + PO content).
  - Item matching via customer cross-reference file; fallback to catalog via Azure AI Search.
  - SAP validation through APIM: customer active, material valid, price variance flagging (>5%), and creation of draft sales order (not released).
  - CSR review queue web UI with ability to correct, save, and release manually.
  - Observability: end-to-end trace per email to SAP draft number, logging of confidence per field.
  - RBAC: Branch-based queue access.
- Out of scope:
  - EDI orders, straight-through release (MVP2), acknowledgements (MVP2), analytics (MVP2), credit-check changes, returns.

3. Test Strategy and Approach
- Combination of manual and automated testing across unit, integration, system, end-to-end, performance, security and UAT.
- Risk-based prioritization: prioritize extraction accuracy, duplicate detection, SAP validation, draft creation SLA, and RBAC.
- Test in multiple environments: Dev (unit + component), Integration (connected to sandbox services), System (end-to-end against SAP sandbox and simulated mailboxes), Pre-production (near-prod configuration), Pilot/UAT with selected branches.
- Use synthetic and sanitized real sample emails representing typical and edge-case PO formats.
- Regression suite to run on every build; smoke tests for daily sanity.
- Traceability: map test cases to BRD requirements and acceptance criteria.

4. Test Types and Coverage
- Unit Tests (Dev): extraction models, service logic, duplicate detection.
- Component/Integration Tests:
  - Graph API -> Event Grid -> Service Bus -> Order Extraction Service.
  - APIM integrations to Azure Document Intelligence, Azure OpenAI, Azure AI Search.
  - Order Creation Service -> Cosmos DB -> SAP S/4HANA via APIM.
- System / End-to-End Tests:
  - Full flow from email arrival to draft in SAP and queue in Web UI.
  - CSR actions in UI (correct, save, release).
- Functional Tests:
  - Header and line extraction, item matching, confidence scoring, duplicate detection logic.
- Data Quality Tests:
  - Mandatory field presence, UoM validation, qty > 0, price checks and variance flags.
- Performance / Load & Stress Tests:
  - Throughput target 300 emails/hr, SLA 95% drafts created within 5 minutes under normal and peak load.
- Security Tests:
  - Azure AD authentication, RBAC checks, secrets handling (Key Vault), data encryption at rest/in transit, penetration test.
- Resilience / Chaos:
  - API failures, SAP API throttling (queueing/retry), Service Bus delivery retries, message duplication scenarios.
- Observability / Monitoring Tests:
  - Trace ID propagation, logging completeness for metrics: time-to-draft, draft accuracy, correction rate.
- Usability / Accessibility:
  - CSR review UI flows, error messages, keyboard navigation, role-specific access.
- UAT (Pilot):
  - Pilot with selected branches to validate accuracy metrics, CSR feedback loop and workflows.

5. Test Environment(s) & Tools
- Environments:
  - Dev: component tests, mocked external dependencies.
  - Integration: connected to Azure AI sandbox endpoints, mocked/sandbox SAP.
  - System/Pre-Prod: full-connected sandbox (APIM to Microsoft AI services and SAP sandbox), realistic data volumes.
  - UAT: pre-prod or dedicated pilot environment using selected branch mailboxes.
- Infrastructure components to be present:
  - Azure Event Grid, Service Bus, Blob Storage, Cosmos DB, APIM, AKS-hosted services (Order Extraction, Order Creation, Web UI), Azure Document Intelligence, Azure OpenAI, Azure AI Search, Key Vault.
  - SAP S/4HANA sandbox with master data support for test customers/materials.
  - Test mailboxes (Graph API) per branch for functional and load tests.
- Tools:
  - Test management: Azure DevOps Test Plans or Jira Xray.
  - Automation: Playwright/Selenium for UI, pytest/JUnit for service tests.
  - API testing: Postman / Newman.
  - Load testing: k6 or JMeter.
  - Security testing: Burp Suite, Azure Security Center tools, static analysis tools.
  - Logs/Monitoring: Datadog, Azure Monitor, Application Insights.
  - CI/CD: GitHub Actions.
  - Data generation: custom scripts to generate emails and attachments.
  - Diff/accuracy analysis: custom scripts to compare extracted vs expected; compute accuracy metrics.

6. Test Data & Test Mailboxes
- Test mailboxes: one mailbox per test branch (at least 5 branches for UAT/pilot), plus admin mailbox. Mailboxes must be provisioned and accessible via Graph API credentials in test environment.
- Test data sets:
  - Baseline set: 200 representative POs from pilot customers (sanitized); used to validate accuracy acceptance.
  - Variants: different email layouts: structured form-like POs, plain text, varied PDF templates, Excel attachments, scanned images/OCR with noise, multi-page POs, images embedded.
  - Edge cases: multi-PO-per-email, missing header fields, negative qty, zero qty, invalid UoM, unusually formatted dates, multiple currencies, inconsistent delimiters, line breaks inside descriptions.
  - Item matching cases: known cross-reference mapping, cross-ref missing, multiple candidate matches, catalog-only match required, price variance scenarios (>5% lower/higher).
  - SAP master data conditions: active customer, inactive/blocked customer, valid/invalid material, pricing that triggers variance flags.
  - Duplicate detection: same customer PO number in different emails, same PO number from different branches.
  - Confidence threshold scenarios: fields with low/high confidence.
- Data privacy: real customer data must be sanitized or consented; store test data in secure environment.

7. Test Deliverables & Artifacts
- Test Plan (this document)
- Traceability Matrix: mapping BRD requirements to test cases
- Test Cases / Test Suites (functional, integration, E2E, performance, security)
- Test Data sets and generation scripts
- Test execution reports (daily/weekly), metrics dashboards
- Defect logs and resolution reports
- UAT sign-off forms and pilot feedback report
- Release readiness report

8. Roles & Responsibilities
- QA Lead (owner): test planning, coordination, reporting, sign-off.
- QA Engineers: write/execute test cases, automation development, defect verification.
- Developers: unit tests, fix defects, support integration tests.
- DevOps/Platform: provide environments, CI/CD, service accounts, Key Vault.
- Integration/SAP team: provide SAP sandbox APIs, test master data scenarios.
- CS Admin / Business SME: supply cross-ref files, evaluate ML output, UAT sign-off.
- CS Pilot Branch CSRs: participate in UAT and feedback.
- Security Team: perform security assessments and penetration testing.

9. Entry / Exit Criteria and Acceptance Criteria Mapping
- Entry criteria for system testing:
  - All services deployed in test environment.
  - Mailboxes available and Graph API access configured.
  - SAP sandbox accessible with required test master data.
  - Extraction and mapping models deployed; baseline cross-reference files uploaded.
  - Smoke tests pass.
- Exit criteria from system testing:
  - All critical and high defects fixed or have accepted workarounds.
  - Pass rate: ≥95% of critical functional tests; automation regression pass rate ≥90%.
  - Performance tests meet SLA for draft creation (95% within 5 minutes) under normal load.
  - Security, logging, and RBAC tests passed.
- Acceptance Criteria mapping (from BRD):
  - ≥95% header field accuracy — validated via baseline set tests and accuracy reports.
  - ≥90% line accuracy — validated via baseline set tests.
  - Draft within 5 minutes for 95% of POs — validated via timed throughput tests and logs.
  - No orders released without CSR action in MVP1 — validated via end-to-end and access control tests.
  - Duplicate POs detected 100% in test set — validated with duplicate detection test set.

10. Test Schedule / Milestones (high-level)
- Week 1–2: Test env provisioning, test data creation, test case writing (functional + integration).
- Week 3–6: Component & integration testing (AI services, API integrations).
- Week 7–9: System and E2E testing, functional regression.
- Week 10: Performance/load testing and resilience testing.
- Week 11: Security & penetration testing.
- Week 12–13: UAT pilot with selected branches, final fixes.
- Week 14: Release readiness and sign-off.
(Adjust dates to align with project timeline Apr–Jul 2026.)

11. Test Cases — Structure and Representative Examples
- Test case template:
  - ID, Title, Requirement(s) mapped, Priority (P0/P1/P2), Preconditions, Test data, Steps, Expected result, Actual result, Pass/Fail, Comments.
- Representative Functional / E2E test cases (sample set; full suite to be maintained in test management tool):

F-001: Email Intake — New Email Triggers Processing
- Req: Mailbox monitoring via Graph; Event Grid->Service Bus flow.
- Preconditions: Test mailbox received new email; Event Grid configured.
- Steps: Send test email to branch mailbox; observe event in Event Grid and message in Service Bus; confirm Order Extraction Service receives event.
- Expected: Extraction service receives email within configured latency; email persisted in Blob Storage.

F-002: Duplicate Detection by Customer PO Number
- Req: Duplicate PO detection by customer PO number.
- Preconditions: Send two emails with identical customer PO#.
- Steps: Send first email → process → draft created. Send second email with same PO#.
- Expected: Second email flagged as duplicate; no second draft created; alert/flag recorded in logs and UI.

F-003: Extraction Accuracy — Header Fields
- Req: Extract customer PO#, sold-to, ship-to, requested date.
- Preconditions: Provide sample email/attachment with known header values.
- Steps: Process email, retrieve extracted header data and confidence values from Cosmos DB / Web UI.
- Expected: Extracted values match expected; each header field confidence ≥ threshold; overall header accuracy logged. Run across 200 baseline POs to compute accuracy metric.

F-004: Line Extraction — Multi-line PDF and Excel
- Req: line extraction (customer part, description, qty, UoM, price).
- Steps: Process numerous templates including PDFs and Excel attachments.
- Expected: Lines extracted correctly with UoM validated; qty >0; per-line confidence values captured.

F-005: Item Matching — Cross-reference and Catalog Fallback
- Req: Use customer cross-ref table then catalog search.
- Steps: Send POs where first some items exist in cross-ref, some only in catalog, some unknown.
- Expected: Items mapped via cross-ref where present; catalog used when cross-ref missing; unmatched items highlighted to CSR.

F-006: Price Variance Flagging in SAP Validation
- Req: Price variance >5% flagged.
- Preconditions: SAP master data set price X; PO line price set to X*1.06.
- Steps: Process email and run SAP validation.
- Expected: Line flagged for price variance >5%; draft created with flag and CSR notification.

F-007: Draft Creation and CSR Queue
- Req: Draft created in SAP (not released); CSR web UI shows draft with editable fields and confidence per field.
- Steps: Complete end-to-end; open CSR UI as branch CSR.
- Expected: Draft present in queue, matches extracted data; CSR can edit lines, save changes, and must explicitly release in SAP (release action) — ensure no automatic release occurs.

F-008: RBAC — Branch-Based Access
- Req: Branch-based queue access.
- Steps: Login as CSR from branch A and branch B.
- Expected: CSR from A sees only branch A drafts; cannot view or modify other branches' drafts.

F-009: SLA — Draft Created Within 5 Minutes (functional + timing)
- Req: Draft created within 5 minutes for 95% of POs.
- Steps: Send a set of 500 emails at steady arrival and measure time from mail arrival to SAP draft creation (log timestamps).
- Expected: ≥95% drafts created within 5 minutes.

F-010: SAP API Throttling and Retry
- Req: Queueing and retry on SAP limits.
- Steps: Simulate SAP HTTP 429 responses for a period; observe service retry/backoff and eventual draft creation.
- Expected: Messages retried per policy; no loss of POs; appropriate logging/alerts triggered if delayed beyond thresholds.

F-011: Observability — End-to-End Trace
- Req: End-to-end trace per email.
- Steps: Process email; fetch trace ID in Web UI; correlate logs across Event Grid, Service Bus, extraction, AI services, APIM and SAP.
- Expected: Single trace ID present across systems; logs show steps and latencies.

F-012: Low Confidence Fields and CSR Correction Tracking
- Req: Show confidence per field; CSR corrections tracked.
- Steps: Provide POs with intentionally ambiguous fields; CSR modifies values in UI and saves.
- Expected: Low-confidence fields flagged; corrections persisted to Cosmos DB and show in correction history; system records correction rate.

Edge / Negative cases:
- E-001: Missing mandatory header (no customer PO#) — flag to CSR, do not create draft (or create draft with missing mandatory field error per business rule).
- E-002: Line with qty=0 or negative — flagged as invalid; reject or queue for manual correction.
- E-003: Non-PO emails (spam, EDI) — ensure EDI detection not created by MVP1, non-POs ignored or moved to exception queue.

12. Automation Strategy
- Automate:
  - API-level smoke and regression tests (high coverage of extraction, matching, validation logic) using Postman/Newman and pytest.
  - UI regression tests for Web UI (Playwright).
  - Data-driven extraction accuracy tests comparing expected vs extracted values.
  - CI pipeline to run fast-suite on each PR; nightly full regression.
- Not automated initially:
  - Some AI model subjective decisions and complex UAT feedback (manual validation).
- Maintain automation artifacts in GitHub; integrate into GitHub Actions for scheduled runs and pre-deployment gating.

13. Performance & Load Test Plan
- Objectives:
  - Validate throughput of 300 emails/hour (peak) and processing latency SLA (95% within 5 minutes).
  - Validate behavior under burst loads (e.g., 600 emails/hour) and system degradation behavior.
- Scenarios:
  - Baseline load: 100 emails/hour steady for 1 hour.
  - Peak load: 300 emails/hour steady for 2 hours.
  - Spike: 600 emails/hour for 15 minutes to test scaling/backpressure.
  - Mixed complexity: combine simple structured POs and complex scanned images in load.
- Metrics to capture:
  - Time from email arrival to draft creation (mean, P95, P99).
  - Service bus queue length & processing time.
  - API latency for APIM calls to AI services and SAP.
  - Error rates, retries, dropped messages.
- Tools: k6 (recommended), JMeter for multi-protocol tests.
- Environment: Pre-prod environment with realistic sizing; monitoring via Datadog/Azure Monitor.
- Acceptance:
  - Under peak 300/hr: ≥95% drafts within 5 minutes.
  - Under spike: graceful degradation with retries, acceptable backlog growth and alerting.

14. Security, Privacy & Compliance Test Plan
- Authentication & Authorization:
  - Validate Azure AD sign-on flows for CSR and Admin roles.
  - Test RBAC: branch-based access enforcement, admin-only functions accessible by CS Admin role only.
- Data protection:
  - Validate encryption at rest (Blob, Cosmos DB) and in transit (HTTPS).
  - Confirm Key Vault is used for secrets and credentials—no hard-coded secrets in service images.
- Penetration testing:
  - External (app gateway/APIM) and internal service-level pentest (OWASP Top 10).
- Access logs & audit:
  - Verify audit trail for sensitive actions (cross-ref upload, corrections, release action).
- AI Governance:
  - Verify model usage complies with AI Governance Council approval artifacts.
  - Test for PII handling in AI services — ensure PII minimization and logging policies.
- Compliance:
  - Ensure test data sanitized; GDPR/CCPA considerations for real customer data.
- Tools: Burp Suite, static code analysis, Azure Security Center.

15. Observability / Logging / Traceability Tests
- Validate trace ID propagation end-to-end (Event Grid -> Service Bus -> extraction -> APIM -> SAP).
- Validate logs capture: timestamps, event types, confidence scores per field, errors/exceptions, retries.
- Validate metrics dashboard: emails processed per minute, time-to-draft distribution, correction rates, duplicates flagged, failures.
- Test alerting: SLA breach (e.g., drafts older than 30 minutes flagged), queue length thresholds trigger alerts to CS Supervisor.

16. Defect Management & Reporting
- Tool: Azure DevOps Boards or Jira.
- Severity levels:
  - P0 (Critical): Blocker to core flow (e.g., no drafts created, data corruption); immediate fix or rollback.
  - P1 (High): Major functional break, acceptance criteria not met (e.g., duplicate detection failure).
  - P2 (Medium): Non-critical functional or minor UI issues.
  - P3 (Low): Cosmetic, docs, enhancement.
- Triage cadence: Daily for P0/P1; every 2–3 days for P2/P3.
- Communication: Slack/Teams channel for real-time critical issues; weekly QA report to stakeholders.

17. Risks, Assumptions & Mitigations
- Risk: Unusual PO layouts reduce extraction accuracy.
  - Mitigation: Expand sample training set, improve templates, CSR corrections tracked to retrain models.
- Risk: SAP API rate limits cause delays.
  - Mitigation: Implement backoff/retry, queuing, batch processing, and alerting.
- Risk: Mailbox access delays/permissions.
  - Mitigation: Early request for mailbox access; test mailboxes prepared upfront.
- Risk: Insufficient cross-reference coverage.
  - Mitigation: Fallback to catalog search; flag missing cross-ref to CS Admin for upload.
- Assumptions:
  - Most customers send one PO per email; cross-ref files for top 200 customers exist.
  - SAP sandbox can simulate master data cases required.
- Contingency: If acceptance thresholds not met in UAT, extend pilot and refine extraction models and mapping rules.

18. Sign-off
- Acceptance sign-off required from:
  - QA Lead
  - Business Owner (Customer Service Operations)
  - CS Supervisor (Pilot branches)
  - Integration/SAP team
  - Security/Compliance owner
- Sign-off criteria: all P0/P1 defects resolved or mitigated, acceptance criteria met (accuracy & SLA), security sign-off complete, UAT successful.

Appendices
A. Traceability Matrix (sample mapping)
- BRD: Duplicate PO detection -> Tests: F-002, Regression suite.
- BRD: Extraction of header/lines -> Tests: F-003, F-004 and baseline accuracy runs.
- BRD: Item matching -> Tests: F-005.
- BRD: SAP validation and price variance flagging -> Tests: F-006.
- BRD: Draft creation within 5 min -> Tests: F-009 + performance suite.
- BRD: CSR review queue -> Tests: F-007, F-012.
- BRD: RBAC -> Tests: F-008.

B. Example Test Case (formal)
- ID: F-003-R1
- Title: Header extraction — requested delivery date variants
- Requirement: Extraction of requested delivery date (BRD section Extraction)
- Priority: P0
- Preconditions: Mailbox created; email with requested date in multiple formats (MM/DD/YYYY, DD-MMM-YYYY, textual).
- Test Data: Sample email with three POs each using different date formats.
- Steps:
  1. Send email to branch test mailbox.
  2. Wait for processing and check Cosmos DB or Web UI for extracted requested dates.
- Expected result: All requested dates extracted accurately and normalized; confidence score per date captured; field-level accuracy recorded.
- Pass: Extracted normalized dates match expected normalized format.

C. Reporting & Metrics
- Daily QA report: test runs, passed/failed, critical defects, environment issues.
- Weekly metrics: accuracy percent (header, lines), time-to-draft distribution, CSR correction rates, duplicates detected, test coverage.
- UAT Pilot report: acceptance metrics vs BRD targets and CSR qualitative feedback.

Final notes
- Maintain an evolving baseline corpus of PO samples to continuously test extraction accuracy and reduce false positives/negatives.
- Early engagement with CS Admin and SAP integration team is critical to provision test master data and cross-reference files.
- Continuous monitoring & retraining plan to be coordinated with AI Governance Council as MVP moves to production.

End of Test Plan.