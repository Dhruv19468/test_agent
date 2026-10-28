# Test Plan — Email Purchase Order Entry Automation (MVP1)

Version: 1.0  
Date: 2026-03-02 (aligned to BRD)  
Prepared by: QA Lead

Purpose: provide a complete test plan to verify that the Email Purchase Order Entry Automation (MVP1) meets functional, non-functional, security and acceptance requirements specified in the BRD and architecture documents.

Contents
- Overview & Objectives
- Scope (In / Out)
- Test Strategy & Approach
- Test Types / Areas to Cover
- Test Items / Features to Test
- Acceptance Criteria Mapping
- Test Environments & Test Data
- Test Design: Test Cases & Scenarios (high-level + sample detailed cases)
- Non-functional Tests: Performance, Scalability, Reliability, Observability, Security
- AI & Data Validation Testing Strategy
- Automation Strategy
- Entry / Exit Criteria
- Test Schedule & Milestones
- Roles & Responsibilities
- Defect Management & Reporting
- Risks, Assumptions & Mitigations
- Deliverables

---

# 1. Overview & Objectives
Objectives (from BRD)
- Reduce order entry time by 60% (measured in pilot)
- Reduce order entry errors by 50%
- Create SAP draft orders within 5 minutes of email receipt for 95% of POs
- Keep CSR review for every order in MVP1 (no automatic release)

QA Objectives
- Validate functional correctness of extraction, matching, validation and draft creation.
- Validate security, RBAC and data privacy requirements.
- Validate non-functional requirements: availability, performance (throughput and latency), observability.
- Validate AI model behavior (extraction/mapping) and ensure accuracy metrics meet acceptance criteria.
- Provide measurable evidence against BRD acceptance criteria.

---

# 2. Scope

In scope (MVP1)
- Mailbox ingestion from branch order mailboxes via Microsoft Graph (Event Grid -> Service Bus).
- Extraction of PO header and lines from email body and attachments (PDF/Excel) using Azure Document Intelligence and Azure OpenAI.
- Customer & ship-to identification.
- Item matching via customer cross-reference table then Azure AI Search (catalog) fallback.
- SAP validation via APIM (customer active, material valid, price variance checks).
- Creation of draft sales order in SAP (draft only, not released).
- CSR review queue (web UI) with confidence scores and edit/correct/reject actions.
- Duplicate PO detection by customer PO number.
- Logging & end-to-end traceability per email to SAP draft order number.

Out of scope (MVP1)
- Straight-through automatic release (MVP2).
- Acknowledgement emails (MVP2).
- EDI orders, returns, credit checks, quotations.

---

# 3. Test Strategy & Approach

Overall approach
- Use a risk-based test approach prioritizing: (1) ingestion/extraction accuracy, (2) SAP validation/draft creation, (3) duplicate detection, (4) RBAC/security, (5) performance & availability.
- Combine automated API and integration tests with manual exploratory testing and CSR UAT.
- Validate AI outputs against ground-truth labeled data sets. Measure accuracy and confidence mapping.
- Use synthetic and redacted production-like email samples for realistic coverage; include edge / failure cases.
- End-to-end (E2E) tests will exercise the whole pipeline: mailbox event -> extraction -> matching -> SAP validation -> draft creation -> CSR queue.
- Use contract tests for APIM -> SAP and APIM -> AI service interfaces.
- Regression pack will be maintained and run on each CI/CD deployment.

Test levels
- Unit tests: developers (not in QA plan details but assumed).
- Integration tests: service-to-service (Event Grid, Service Bus, APIM, AI services, Blob, Cosmos DB).
- System / E2E tests: full pipeline.
- Performance & load tests: throughput and latency.
- Security & compliance tests: AD authentication, RBAC, data encryption and access control.
- UAT: CSR users (branch pilots).
- Regression & Release verification (smoke).

Test data approach
- Synthetic emails (varied templates): clean structured POs, scanned images (OCR), multi-page PDFs, Excel attachments with multiple formats, emails with multiple POs (edge), missing fields.
- Customer master and cross-reference test data in SAP and Cosmos DB.
- Catalog/index of items for AI Search fallback.
- Known “trusted” customers flagged for MVP2 tests (for regression planning).
- Duplicate PO test set with repeated customer PO numbers.

Traceability
- Map test cases to BRD acceptance criteria and user stories. Maintain a traceability matrix.

---

# 4. Test Types / Areas to Cover

1. Mailbox Ingestion
   - Event Grid trigger from Graph API, new mail detection, Service Bus enqueue.
   - Blob Storage snapshot of email and attachments.

2. Extraction (AI)
   - Azure Document Intelligence extraction for PDF/Scanned.
   - Azure OpenAI mapping of fields to canonical model.
   - Handling of Excel attachment parsing.

3. Data Matching & Enrichment
   - Customer identification via sender domain and content.
   - Ship-to resolution.
   - Item matching: customer cross-reference first, catalog fallback via Azure AI Search.
   - Confidence score computation per field/line.

4. Duplicate Detection
   - Customer PO number deduplication logic and thresholding.

5. SAP Validation & Draft Creation (APIM)
   - Customer active check, material validity, pricing validation, price variance >5% flagging.
   - Creating draft (not released) sales order in SAP and returning draft order number.

6. CSR Review Web UI
   - Display: header, lines, confidence per field, flags for missing cross-ref.
   - Actions: edit, save, reject, send to SAP release (MVP1: only CSR can release manually in SAP; release action should not automatically release).

7. Observability & Logging
   - End-to-end trace: correlation IDs, audit logs from mail arrival to SAP draft number.
   - Metrics: time-to-draft, extraction confidence distribution, correction rate.

8. Non-Functional
   - Performance: process 300 emails/hour peak; 95% within 5 minutes.
   - Availability: 99.5% 24x5.
   - Security: Azure AD, RBAC (branch-based queue access), secrets handling (Key Vault).
   - Resilience: queueing/backpressure, retry/backoff handling for SAP API limits.

9. Compliance & Privacy
   - Ensure PII is handled per policy; encrypted at rest/in transit; access logs.

10. AI Governance / Model Safety
    - Evaluation of hallucinations, incorrect mappings, low-confidence handling and CSR fallback.

---

# 5. Test Items / Features to Test (List)

- Mailbox monitoring via Graph -> Event Grid integration.
- Event Grid -> Service Bus event delivery & retry.
- Order Extraction Service:
  - Blob save of raw email and attachments.
  - Document Intelligence OCR and structured extraction.
  - Excel parsing logic.
  - OpenAI mapping of extracted blocks to canonical fields.
  - Confidence scoring algorithm.
- Customer identification service (domain + content heuristics).
- Cross-reference lookup service (file upload mapping).
- Catalog search (Azure AI Search) fallback.
- Duplicate detection logic (customer PO number dedupe).
- SAP validation via APIM (customer/material/price checks).
- Draft order creation in SAP (create draft + return ID).
- Cosmos DB storage of draft order with audit info and confidence.
- Web UI (Review Queue): filter by branch, edit/save, view confidence, flags, trace links to SAP draft.
- RBAC/Authorization (Azure AD).
- Logging, telemetry (Datadog / Azure Monitor), correlation IDs.
- Retry and error handling for SAP rate limits and AI service outages.
- Data archival / retention to Blob.
- Observability: end-to-end traceable logs and metrics.

---

# 6. Acceptance Criteria & Testables (Mapping to BRD)

Acceptance Criteria (BRD) and test approach:

- ≥95% header field accuracy and ≥90% line accuracy on pilot customers
  - Test: run extraction against labeled dataset (pilot customers), compute accuracy metrics per header field and per line (material + qty + UoM + price). Report pass if ≥95% header and ≥90% line.

- Draft created within 5 minutes for 95% of POs
  - Test: time-to-draft measurement on representative load (including peak), measure 95th percentile <= 5 minutes.

- No orders released without CSR action in MVP1
  - Test: simulate processing for various customers including ones flagged as “trusted”; verify draft in SAP not released; attempt to auto-release should be blocked.

- Duplicate POs detected 100% in test set
  - Test: feed test set of duplicate emails and verify duplicate detection flags and no duplicate drafts created.

- Misc functional requirements (extraction/validation/flags)
  - Test each via E2E cases and negative cases.

---

# 7. Test Environments & Tools

Environments
- Dev: unit and initial integration testing (developer-managed).
- Integration/Test: Event Grid, Service Bus, APIM (pointing to mock SAP), AI services (staging), Blob & Cosmos DB test instances, Web UI.
- Pre-Prod (staging): full integration with SAP test system (S/4HANA sandbox), real Graph mailbox test accounts, full telemetry enabled.
- Production (not for tests except smoke after deployment) — tests should run only in controlled environments with sanitized data.

Tools
- Test management: Azure DevOps Test Plans or equivalent (TestRail).
- API test / automation: Postman / Newman, REST-assured.
- UI automation: Playwright or Selenium.
- Load testing: k6 or JMeter.
- AI evaluation: custom Python scripts to compare extracted outputs vs ground truth; metrics dashboard.
- Logging/Monitoring: Datadog, Azure Monitor, Application Insights.
- CI/CD: GitHub Actions (integration with test runs).
- Secrets: Key Vault (verify via integration).

Data requirements
- Labeled dataset of PO emails (min N=2000 samples for accuracy measurement across top customers). Include ground truth labels for header & lines.
- SAP test master data: customers, materials, prices, price variance cases.
- Cross-reference files for top customers.
- Catalog index sample.

Security
- Test accounts in Azure AD per CSR role and per branch.
- Ensure all test data is non-production or sanitized.

---

# 8. Test Design: Sample Test Cases & Scenarios

Below are representative high-value test cases. Each will be implemented as detailed test cases in the test repository.

Test Case IDs use prefix TC.

Functional / E2E tests

TC-F001 — Mailbox ingestion: simple email with inline PO
- Precondition: Test mailbox configured; service listening.
- Steps: Send sample email with header + 2 lines in body.
- Expected: Event received; email saved to Blob; extraction outputs header and lines; draft created in SAP; Cosmos DB draft record exists; Web UI shows new draft with correct confidence.

TC-F002 — PDF attachment (structured) extraction
- Steps: Send email with PDF attachment containing PO table.
- Expected: Document Intelligence extracts header and lines; mapping to canonical fields; draft created.

TC-F003 — Scanned PDF (image) extraction
- Steps: Send scanned image PDF PO (OCR path).
- Expected: OCR extracts text; Document Intelligence identifies fields with lower confidence; draft created and confidence scores present; CSR UI flags any low-confidence fields.

TC-F004 — Excel attachment parsing (multiple sheets/format variants)
- Steps: Send .xlsx with PO data in different layouts (rows first, columns first).
- Expected: Parser reads rows, maps lines correctly; multiple formats handled.

TC-F005 — Customer identification via sender domain
- Steps: Email from known domain (customer A).
- Expected: Customer resolved to customer A.

TC-F006 — Customer identification via PO content when domain ambiguous
- Steps: Email from generic domain with customer PO fields referencing customer id.
- Expected: Customer resolved via content heuristics.

TC-F007 — Cross-reference match present
- Steps: Line with customer part number that maps to material via cross-reference.
- Expected: Material matched from cross-ref; confidence high; Web UI shows matched material.

TC-F008 — Cross-reference missing -> Catalog fallback
- Steps: Line with customer part not in cross-ref.
- Expected: Catalog search returns candidate matches; chosen match stored with lower confidence and UI shows "no cross-ref" highlight.

TC-F009 — Price variance >5% flagged
- Steps: Line with price deviating >5% from SAP price.
- Expected: Validation flags the line for CSR attention and price variance flag present in draft.

TC-F010 — Customer inactive in SAP -> validation error
- Steps: Customer marked inactive in SAP.
- Expected: SAP validation fails; draft not created; order put into error queue for manual handling; event/notification logged.

TC-F011 — Duplicate PO detection
- Steps: Send same customer PO number twice (within dedupe window).
- Expected: Second email flagged as duplicate; no second draft created; duplicate handling logged.

TC-F012 — End-to-end traceability
- Steps: Process a PO.
- Expected: Correlation ID available linking email -> extraction steps -> APIM call -> SAP draft order number; logs show trace.

TC-F013 — CSR web UI branch-based RBAC
- Steps: CSR from branch A logs in; attempts to view branch B queue.
- Expected: Access denied; CSR only sees branch A queue.

TC-F014 — Draft not released automatically
- Steps: Process PO from a normal and a trusted customer (if trusted flagged in data).
- Expected: Drafts created and not released. Even for trusted customers, no auto-release occurs in MVP1.

TC-F015 — Multiple POs in single email (edge case)
- Steps: Email contains 2 POs.
- Expected: System either processes first PO and flags ambiguous or extracts both when supported (documented behavior); ensure no silent loss. This test verifies documented behavior.

TC-F016 — Missing mandatory header field
- Steps: Email missing required header (e.g., sold-to).
- Expected: Draft creation fails or flags incomplete requiring CSR intervention; extraction confidence zero for missing field.

TC-F017 — Negative/zero quantity
- Steps: Line quantity = 0 or negative.
- Expected: Validation fails/flagged per business rule; draft marked as error and queued for CSR.

TC-F018 — UoM invalid / not in SAP
- Steps: UoM not valid per SAP master data.
- Expected: Flagged and queued for CSR.

TC-F019 — High volume throughput / queueing
- Steps: Simulate 300 emails/hour sustained and a peak spike (400 in hour).
- Expected: 95% of drafts within 5 minutes under 300/hr; graceful degradation under spike with queued processing and no data loss; retry policy for SAP API.

TC-F020 — APIM / SAP rate-limit behavior
- Steps: Force SAP to respond with 429 or transient errors.
- Expected: Retry/backoff is invoked; order not lost; logs show retries.

Security & Compliance tests

TC-S001 — Azure AD authentication
- Steps: Attempt login as valid CSR user.
- Expected: SSO / token accepted.

TC-S002 — RBAC enforcement on Web UI & APIs
- Steps: Attempt branch access as unauthorized user; attempt elevated API calls.
- Expected: Forbidden responses.

TC-S003 — Secret & Key Vault usage
- Steps: Verify service cannot retrieve secrets without proper managed identity.
- Expected: Unauthorized access attempts fail; managed identity access succeeds.

TC-S004 — Data encryption at rest and in transit
- Steps: Validate Blob & Cosmos storage encryption configuration; check TLS enforcement.
- Expected: Encryption enabled; TLS enforced.

TC-S005 — Logging PII control
- Steps: Verify logs do not expose full PII fields (if policy requires redaction).
- Expected: Sensitive data masked per policy.

AI / Model-specific:

TC-AI001 — Extraction accuracy measurement (batch)
- Steps: Run the labeled dataset; compute per-field precision/recall and aggregate header/line accuracy.
- Expected: ≥95% header, ≥90% line for pilot customers.

TC-AI002 — Confidence threshold behavior
- Steps: Force low-confidence extraction (noisy scanned image).
- Expected: Low confidence scores cause field to be flagged for CSR; system does not auto-correct with high-confidence wrong mapping.

TC-AI003 — Hallucination detection
- Steps: Provide input designed to induce hallucination (ambiguous content).
- Expected: Model output validated against heuristics; high hallucination probability triggers fallback and flag.

Observability tests

TC-O001 — Metric emission
- Steps: Process POs and verify metrics for processed count, time-to-draft, error rates appear in Datadog/Azure Monitor.
- Expected: Metrics produced and visible with proper tags (branch, correlation id).

UAT / Acceptance tests

TC-UAT001 — CSR end-to-end acceptance
- Steps: CSR users from pilot branches run realistic day-of-work scenarios: review drafts, correct lines, save.
- Expected: CSR finds UI usable; corrections save to draft and persisted; acceptance sign-off.

Regression & Smoke

TSMOKE-001 — Deploy smoke: basic E2E check
- Steps: Trigger one sample PO processing post-deploy.
- Expected: All critical flows succeed.

---

# 9. Non-functional Testing (detailed)

Performance & Load
- Targets:
  - Throughput: 300 emails/hour sustained (5 emails/minute average ~ bursty).
  - Latency: 95th percentile time-to-draft <= 5 minutes.
  - Peak handling: graceful up to 400 emails/hour with queueing and bounded SLA violations.
- Tests:
  - Baseline: single PO end-to-end time.
  - Load: ramp to 300/hour; measure time-to-draft distribution.
  - Spike: sudden burst of 200 emails in 10 minutes.
  - Soak: sustained 24-hour run at 300/hour to detect memory leaks, resource exhaustion.
- Tools: k6/JMeter.

Scalability & Resilience
- Tests of Service Bus backlog handling, auto-scaling of Order Extraction Service replicas, retry/backoff on APIM/SAP 429s.
- Failover tests: simulate Azure Document Intelligence outage to validate fallback behaviour and error queueing.

Availability
- Test scenarios for component downtime and recovery; verify SLA measurement via monitoring.

Observability
- Validate logs for correlation IDs per email and log levels; ensure traceable path to SAP draft number.
- Validate dashboards and alerts: failed extraction rates, time-to-draft SLA breaches, queue depth.

Security Tests
- Penetration testing of public endpoints (App Gateway & APIM).
- IAM tests: Azure AD roles, least privilege checks.
- Verify Key Vault secrets access policies.
- Verify data retention and deletion flows.

Compliance & Privacy
- PII handling tests, ensure no unnecessary exposure in logs or telemetry.

---

# 10. AI & Data Validation Strategy

Because AI is core, testing must be rigorous and repeatable.

- Ground-truth datasets:
  - Build labeled dataset of representative PO emails per BRD: top 200 customers + small customers, varied templates, scanned images, Excel variants.
  - Size target: at least 1,000 labeled emails for initial MVP accuracy measurement; larger (2k–5k) recommended for robust measurement.

- Metrics:
  - Header field accuracy per field (sold-to, ship-to, customer PO number, requested date) — measure precision/recall.
  - Line-level accuracy: correct material match, quantity, UoM, price.
  - Confidence calibration: measure correlation of confidence score to actual correctness.
  - False positive rate for item matching (catalog fallback) and hallucination detection.

- Acceptance thresholds:
  - Header fields: >=95% accuracy for pilot customers.
  - Line accuracy: >=90% for pilot customers.
  - Duplicate detection: 100% on test set.

- Testing method:
  - Automated batch evaluation: compare model outputs to ground truth and produce reports.
  - Guard rails: for low confidence or uncertain mapping, system must flag field and not auto-correct without CSR confirmation.
  - Retraining or prompt tuning: test changes in AI models in controlled evaluation prior to promoting.

- Non-determinism:
  - Record seeds/versions of OpenAI prompts and Document Intelligence models used to reproduce results in testing.

---

# 11. Automation Strategy

What to automate
- API-level tests: end-to-end APIs, APIM -> SAP mock contracts, AI service stubs.
- Regression pack: E2E smoke tests covering ingestion, extraction (sample), SAP draft creation (mocked), UI basic flows (smoke).
- Performance tests: automation for load scenarios (k6 scripts).
- Model evaluation: automated batch scoring scripts for labeled datasets.

What to keep manual
- Exploratory testing of new PO layouts and novel scanned documents.
- UAT with CSRs for usability and workflows.
- Security pentests (external vendor/manual specialized).

Execution
- CI/CD integration: automated suites run on every pull request or scheduled nightly (regression).
- Post-deployment smoke suite executed automatically in pre-prod and production gates.

Test data management
- Use sanitized or synthetic production-like data. Maintain versioned labeled datasets for AI evaluation.

---

# 12. Entry & Exit Criteria

Entry criteria for system/E2E testing
- All components deployed in test/pre-prod (Event Grid, Service Bus, Order Extraction, Order Creation Service, APIM mocks/SAP sandbox, Blob, Cosmos DB, Web UI).
- Test accounts (Azure AD) provisioned for CSR, Admin, Supervisor roles.
- Labeled dataset available for AI evaluation.
- Cross-reference and catalog test data present.
- Test plans and automation scripts available.

Exit criteria for system/E2E testing
- All critical and high severity defects fixed and verified.
- Acceptance criteria met for majority of BRD items or documented exceptions with business sign-off.
- Performance tests show 95th percentile time-to-draft <= 5 minutes in pre-prod under expected load (300/hr).
- Observability and tracing validated; dashboards and alerts configured.
- Regression suite passing (pre-agreed pass rate e.g., 95%).

UAT Entry/Exit
- Entry: System validated in pre-prod; stakeholders and pilot CS branches scheduled.
- Exit: CSR sign-off on UAT scenarios or documented list of known issues with business acceptance.

---

# 13. Test Schedule & Milestones (High-level aligned to BRD)

Assuming MVP1 delivery Apr–Jul 2026:
- Weeks 1–4: Test environment setup, test data creation, labeled dataset build.
- Weeks 5–8: Integration & component testing (Event Grid, Service Bus, extraction services, APIM with SAP sandbox).
- Weeks 9–12: System / E2E testing + functional regression; AI model evaluation on labeled dataset.
- Weeks 13–14: Performance & resilience testing; security checks.
- Weeks 15–16: UAT with pilot branches; fix cycle.
- Week 17: Final acceptance testing and sign-off; prepare for rollout.

Adjust schedule as per actual project timeline.

---

# 14. Roles & Responsibilities

- QA Lead (owner): produce and maintain test plan, coordinate testing, report status.
- Test Engineers: create and run test cases, automation scripting, performance tests.
- AI Evaluation Specialist / Data Scientist: curate labeled dataset, evaluate model outputs, run scoring.
- DevOps / Platform: provision test environment and monitoring, support CI/CD test runs.
- Integration / SAP team: provide SAP test sandbox, support APIM contract testing.
- CS Pilot Users (CSR / Supervisor / Admin): participate in UAT and acceptance testing.
- Security Team: run security & compliance tests.

---

# 15. Defect Management & Reporting

- Defect tool: Azure DevOps Boards / Jira (project standard).
- Severity definitions:
  - Sev 1 (Critical): production-breaking or data loss or security breach.
  - Sev 2 (High): major functionality broken preventing core flow (draft creation).
  - Sev 3 (Medium): partial loss or UI issues not blocking main flow.
  - Sev 4 (Low): cosmetic or minor issues.
- SLAs for fixes: negotiated with Dev/PO; critical issues immediate triage.
- Reporting: weekly QA status reports; daily during stabilization and UAT; metrics dashboard for defect counts, pass rates, test coverage.

---

# 16. Risks, Assumptions & Mitigations

Risks
- Mailbox access delays (Graph API permissions)
  - Mitigation: early permission request; test mailboxes seeded in advance.
- SAP API rate limits causing delays/loss
  - Mitigation: queueing, retry/backoff, mock testing and pre-prod validation with SAP team.
- AI extraction variability (non-deterministic)
  - Mitigation: labeled dataset, confidence thresholds, conservative fallback to CSR review.
- Insufficient labeled data to reach accuracy targets
  - Mitigation: iterate with pilot customers; increase labeled dataset size; active learning loop.
- Unusual PO layouts not covered
  - Mitigation: exploratory testing and escalation path; flagging & CSR fallback.
- Security or compliance blockers
  - Mitigation: early engagement with security and AI Governance; use of sanitized data for testing.

Assumptions
- Cross-reference files available for top customers.
- SAP sandbox accessible for integration testing.
- Test accounts and branch users will be available for UAT.

---

# 17. Deliverables

- Test Plan (this document).
- Test Cases repository (detailed cases linked to IDs above).
- Automation scripts for API, performance and model evaluation.
- Labeled dataset & AI evaluation reports.
- Test results reports and dashboards (functional, performance, security).
- Defect reports and resolution logs.
- UAT sign-off artifacts.

---

# 18. Appendix — Sample Detailed Test Case (example format)

TC-F009 — Price variance >5% flagged
- ID: TC-F009
- Purpose: Verify price variance check flags items >5% variance from SAP price.
- Preconditions:
  - SAP test data: material M-100 has base price 100.00.
  - Cross-reference present mapping to M-100.
- Steps:
  1. Send PO email with one line: Customer part mapping to M-100, quantity 10, price 108.00 (8% variance).
  2. Wait for processing; observe APIM validation call and draft creation flow.
  3. Open draft in Cosmos DB and Web UI.
- Expected:
  - SAP validation detects price variance >5% and sets a flag on the line.
  - Web UI shows price variance warning to CSR with details (SAP price, requested price, percent variance).
  - Draft created but requires CSR attention on that line.
  - Metric logged showing price variance event.
- Severity if fail: High
- Notes: If catalog fallback used (no cross-ref), expected behavior same if material identified.

---

# 19. Test Metrics & Reporting

Key metrics to report:
- Test execution coverage: Planned vs executed test cases.
- Pass/Fail rates by test type (functional, integration, performance).
- Defects: count by severity & status.
- AI metrics: header accuracy, line accuracy, precision/recall, confidence calibration.
- Performance: time-to-draft latency (median, p95), throughput achieved.
- Observability: alerts count, correlation ID coverage.
- UAT acceptance: sign-off status and feedback.

---

# 20. Closing Notes

- AI-specific tests and labeled datasets are critical to determine acceptance. Plan to run multiple iterations and maintain versioned test datasets and prompts/model versions.
- Collaborate early with SAP integration and mailbox owners to ensure test accounts and permissions are available.
- The plan should be updated as architecture/design details evolve or as MVP1 scope changes (e.g., additional fields, new attachments formats).

If you want, I can:
- Populate the detailed test case matrix into Azure DevOps format,
- Draft automation scripts / k6 load files for the performance tests,
- Help design the labeled dataset schema and sample labeling instructions for the extraction ground truth.