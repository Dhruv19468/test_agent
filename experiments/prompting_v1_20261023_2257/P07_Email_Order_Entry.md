# Test Plan — Email Purchase Order Entry Automation (MVP1 / MVP2)

Version: 1.0  
Author: QA Lead  
Date: 2026-03-XX

## Table of Contents
1. Objectives
2. Scope
3. Assumptions & Constraints
4. Acceptance Criteria (from BRD)
5. Test Strategy and Approach
6. Test Types / Areas
7. Test Coverage & Traceability Matrix
8. Test Environment & Data
9. Test Deliverables
10. Test Schedule & Milestones
11. Test Entry and Exit Criteria
12. Roles & Responsibilities
13. Test Tools
14. Test Case Examples (representative)
15. Performance, Scalability & Availability Testing Plan
16. Security & Compliance Testing Plan
17. Observability, Logging & Monitoring Tests
18. Defect Management & Severity
19. Reporting & Metrics
20. Risks, Mitigations & Contingencies
21. Sign-off

---

## 1. Objectives
- Validate the solution meets BRD functional and non-functional requirements for MVP1 and planned MVP2 features.
- Ensure draft orders are created correctly, reliably, and within performance targets.
- Validate AI extraction, matching, SAP validation and CSR review queue behavior.
- Verify security, privacy, availability and observability requirements.
- Provide clear, measurable evidence for acceptance criteria.

---

## 2. Scope

In scope (MVP1):
- Mailbox monitoring (Microsoft Graph) for branch order mailboxes.
- PO extraction from email body and PDF/Excel attachments using Azure Document Intelligence and Azure OpenAI.
- Customer and ship-to identification.
- Line extraction: customer part, description, quantity, UoM, price, requested date.
- Item matching (customer cross-reference then catalog via Azure AI Search).
- SAP validation via APIM (customer active, material exists, price variance check).
- Creation of draft sales order in SAP (draft only — no release).
- CSR review queue (Web UI) with field-level confidence indicators and edit capability.
- Duplicate PO detection by customer PO number.
- RBAC: branch-based queue access.
- Observability: end-to-end trace per email to draft order (APIM traceability).
- Data persistence (Blob Storage for emails, Cosmos DB for drafts).

Out of scope:
- EDI intake, straight-through release (MVP2 for trusted customers), acknowledgements (MVP2), credit checks changes, returns.

MVP2 (to be tested later):
- Straight-through release for trusted customers.
- Acknowledgement emails.
- EDI detection & fallback.
- Analytics.

---

## 3. Assumptions & Constraints
- Test mailboxes and mailbox access will be provided for QA.
- SAP integration endpoints and test system available (non-prod SAP) with representative master data.
- Cross-reference files available for test customers; ability to upload variations via CS Admin UI.
- AI services (Document Intelligence, OpenAI, AI Search) are available in non-production with costs and rate limits accounted for.
- Processing SLA: 95% of POs create draft within 5 minutes.
- Peak load to simulate: 300 emails/hour.
- One PO per email is the normal case but multiple PO-per-email must be tested as an edge scenario.

---

## 4. Acceptance Criteria (from BRD)
- ≥95% header field accuracy and ≥90% line accuracy on pilot customers.
- Draft created within 5 minutes for 95% of POs.
- No orders released without CSR action in MVP1.
- Duplicate POs detected 100% in test set.

QA will validate these acceptance criteria with objective measurements.

---

## 5. Test Strategy and Approach

High-level approach:
- Combine manual exploratory testing, scripted functional tests, automated API and UI test suites, and performance/security testing.
- Early focus on integration tests (Graph -> Event Grid -> Service Bus -> Extraction -> AI -> Order Creation -> APIM -> SAP) because multiple systems must connect correctly.
- Use test doubles/mocks for systems where non-prod endpoints aren’t available (e.g., stub SAP responses) but ensure end-to-end tests against real SAP test instance prior to UAT.
- Build datasets for typical customers and edge cases; control and track AI model prompts and document processing configuration.
- Measure accuracy metrics for extraction and matching against labeled ground truth.

Testing levels:
- Unit tests: developers (not in QA scope but will validate).
- Component tests: individual microservices (Order Extraction Service, Order Creation Service).
- Integration tests: AI services, Message Bus, APIM, SAP.
- System tests: end-to-end workflows.
- Performance, stress & scalability tests.
- Security, access control and compliance tests.
- UAT with CS branches and pilot customers.
- Regression tests for subsequent releases (MVP2).

Pass/fail criteria:
- Functional tests: pass for all high/medium priority test cases except documented and accepted deviations.
- NFR tests: meet stated SLAs (performance, availability, security) per acceptance thresholds.

---

## 6. Test Types / Areas

1. Functional Testing
   - Mailbox ingestion & duplicate detection
   - Attachment handling (PDF, XLSX, CSV), body parsing
   - Field extraction (header and line fields)
   - Item matching logic (cross-reference first, fallback catalog search)
   - SAP validation responses handling (customer/material active/inactive, price variance)
   - Draft order creation in SAP (draft saved, not released)
   - CSR review UI (display draft, edit, confidence indicators, branch queue restrictions)
   - CS Admin actions (upload cross-reference)
   - Error handling and retries

2. Integration Testing
   - Graph API → Event Grid → Service Bus flow
   - Service bus message ordering / dead-letter behavior
   - APIM calls to AI services and SAP
   - Blob storage persistence & retrieval
   - Cosmos DB storage schema and queries for UI

3. End-to-End (System) Testing
   - Full flow from email arrival to draft order visible in CSR queue and SAP
   - Traceability of end-to-end trace ID

4. Performance, Load & Scalability Testing
   - Throughput: steady 300 emails/hour and burst scenarios
   - Latency: 95% drafts within 5 minutes
   - Resilience under AI service rate limits and SAP API throttling
   - Resource utilization and queue back-pressure behavior

5. Reliability & Availability Testing
   - Failover / retries for transient failures (Graph, AI service, SAP)
   - Service Bus dead-letter handling and recovery
   - Availability against 99.5% 24x5 requirement

6. Security & Compliance Testing
   - Authentication/authorization (Azure AD RBAC)
   - Branch-based access control in UI and API
   - Data encryption at rest and in transit
   - Sensitive data handling & logging (no PII in logs unless encrypted / redacted)
   - Secrets in Key Vault access verification
   - Penetration testing / OWASP checks on Web UI and APIs
   - AI governance checks (data retention, model usage policy)

7. Observability & Monitoring Testing
   - End-to-end trace per email
   - Logging across components (correlation IDs)
   - Metrics (processing time, error rates) emitted to Datadog/Azure Monitor
   - Alerts on SLA breaches

8. Usability / Accessibility Testing
   - CSR UI usability for reviewing and correcting drafts
   - Accessibility basic checks (keyboard navigation, screen reader basics) for CSR UI

9. Data Validation / Data Quality Tests
   - Mandatory header fields present
   - Line quantity > 0
   - UoM valid per SAP master data
   - Confidence thresholds and highlighting behavior

10. Regression Testing
   - Full regression on release candidate of MVP1 and for each subsequent MVP2 iteration

---

## 7. Test Coverage & Traceability Matrix (high-level)

Below is a mapping of key BRD requirements to test areas / representative test cases. A full traceability matrix (RTM) will be maintained in the test management tool (Azure DevOps / Jira).

- Requirement: Mailbox intake via Microsoft Graph -> Tests: mailbox ingestion, event grid triggers, service bus queue processing
- Requirement: Duplicate PO detection -> Tests: duplicate detection with same customer PO in same branch mailbox and across branches
- Requirement: Extraction of header and line fields -> Tests: extraction accuracy for body, PDF and Excel attachments, various layouts
- Requirement: Customer identification by sender domain & content -> Tests: identify customer via domain, via sold-to in PO body, ambiguous cases
- Requirement: Item matching via cross-reference then catalog -> Tests: match by cross-ref, fallback catalog search, no-match flagged
- Requirement: SAP validation via APIM -> Tests: customer inactive, material invalid, price variance >5% flagged
- Requirement: Draft sales order creation (not released) -> Tests: draft present in SAP and Cosmos DB, not released
- Requirement: CSR review queue with edits and branch-level RBAC -> Tests: CSR UI list, edit/save operations, branch scoping
- Requirement: Draft within 5 minutes (95%) -> Tests: time to draft distribution under normal and peak loads
- Requirement: Observability - end-to-end trace -> Tests: trace IDs across components, log correlation
- Requirement: Security - Azure AD and branch-based access -> Tests: role enforcement & session tests

---

## 8. Test Environment & Data

Environments:
- Dev: developer local / feature branches (unit/component tests)
- Integration: shared integration non-prod (APIM, AI services, Event Grid, Service Bus, Blob, Cosmos; SAP sandbox or mocked)
- QA/System Test: fully integrated non-prod environment with test mailboxes, SAP test system
- Performance Test Lab: environment with representative scale and observability
- UAT: business user environment (CS branches) with real-like mailboxes and test SAP

Environment setup checklist:
- Azure AD test tenant and test user accounts for CSR, CS Supervisor, CS Admin with correct roles
- Test mailboxes for each branch; Graph API credentials and delegated permissions
- Event Grid, Service Bus namespaces configured
- APIM configured for AI services and SAP endpoints (with staging keys)
- Keys and secrets in Key Vault and accessible by services
- Cosmos DB & Blob Storage with test containers
- Datadog/Azure Monitor configured for metrics and logs
- Test SAP S/4HANA endpoint accessible (or API stubs with realistic behavior)
- Web UI deployed in non-prod with HTTPS via App Gateway (AD SSO test)
- CI/CD (GitHub Actions) pipeline for deploying test builds

Test Data:
- Labeled set of POs (golden set) containing:
  - 1000+ representative POs for accuracy measurement (pilot customers with cross-refs)
  - Variety of formats: structured PO PDFs, scanned images, Excel attachments, plain email bodies
  - Edge cases: multiple POs in one email, missing fields, ambiguous addresses, multiple currencies, various UoMs
  - Negative cases: invalid UoM, zero or negative quantity, price mismatch >5%, inactive customer
  - Duplicate PO samples across branches and same branch
- Cross-reference files for top customers and variations
- SAP master data test set with materials, price lists, customers (active/inactive)
- Test user accounts: CSR_A_Branch1, CSR_B_Branch2, CSAdmin, CS Supervisor

Data privacy:
- Use synthetic or anonymized PII in test data. If real customer data used, require approvals and secure handling.

---

## 9. Test Deliverables
- Test Plan (this document)
- Test cases & scripts (manual & automated) in test management tool
- Test data sets and labeled extraction ground truth
- Automation framework and automated test suites (API, UI)
- Load and performance test scripts & results
- Security test report and penetration test findings
- Defect logs with traceability to requirements
- Test summary reports, metrics dashboards
- UAT sign-off document

---

## 10. Test Schedule & Milestones (High-level)

Assuming MVP1 timeline Apr–Jul 2026; QA schedule roughly:
- Week 1–2: Test planning, environment provisioning
- Week 3–6: Test case development and test data creation; component / integration smoke tests
- Week 7–10: Functional & Integration testing (iterative sprints)
- Week 11–12: Performance & Load testing (peak & burst)
- Week 13: Security & compliance testing
- Week 14: UAT with CS pilot branches
- Week 15: Regression & stabilization
- Week 16: Release candidate sign-off

Detailed schedule will be tracked in project plan and adjusted per development cadence.

---

## 11. Test Entry and Exit Criteria

Entry Criteria (for full system test):
- Environments provisioned and stable
- Integration endpoints (Graph, Event Grid, Service Bus, APIM) available
- SAP test instance accessible or realistic stubs available
- Test data and test mailboxes in place
- Build deployed to QA environment and smoke tests passed
- Test cases reviewed and approved

Exit Criteria (system / UAT):
- All high priority defects resolved and closed
- Medium priority defects resolved or have accepted workaround with documented risk
- Acceptance criteria metrics met (header accuracy >=95%, line accuracy >=90% on pilot, draft within 5 minutes for 95%)
- Performance tests show acceptable SLA adherence or mitigations in place
- Security & compliance tests completed and critical findings remediated
- UAT sign-off from CS business owner

---

## 12. Roles & Responsibilities

- QA Lead (author): Test planning, coordination, reporting
- QA Engineers: test case development, execution, automation, defect triage
- Developers: fix defects, provide unit/component tests
- Integration Engineers: provide access and run integration fixes
- SAP Integration Team: provide SAP test endpoints & support
- CS Business Owner & CS Reps: UAT, feedback, acceptance
- Security Team: run penetration testing and review
- DevOps: environment provisioning, CI/CD pipeline
- AI Governance / Data Owners: review AI data use and approvals

---

## 13. Test Tools

- Test Management: Azure DevOps Test Plans or Jira + Xray
- Source & CI: GitHub Actions
- API Test Automation: Postman / Newman, RestAssured, or PyTest requests
- UI Test Automation: Playwright or Selenium WebDriver
- Performance Test: k6, JMeter, or Gatling
- Security Testing: OWASP ZAP, Burp Suite (where permitted)
- Observability: Datadog, Azure Monitor, Application Insights
- Logging/Correlation: centralized logs with correlation IDs
- Data Storage: Azure Blob for artifacts, Cosmos DB queries for verification
- Defect Tracking: Azure DevOps or Jira

---

## 14. Test Case Examples (Representative)

Note: Full test case suite will be maintained in the test management tool. Below are representative critical tests.

Test Case TC-FUNC-001: Mailbox Ingestion — Simple Email
- Purpose: Verify a plain-text email with a single PO in the body is ingested and draft created.
- Steps:
  1. Send test email with customer PO number, sold-to, ship-to, requested date and two lines to branch mailbox A.
  2. Observe Event Grid event and Service Bus processing.
  3. Verify email stored in Blob.
  4. Verify extraction output persisted in Cosmos DB.
  5. Verify draft order created in SAP as draft and visible in CSR queue for Branch A.
- Expected:
  - Draft in Cosmos DB contains header fields with confidence values.
  - Draft in SAP created (draft flag) and not released.
  - CSR in Branch A can view and edit; CSR in Branch B cannot.

Test Case TC-FUNC-002: PDF Attachment Extraction — Scanned PO
- Purpose: Validate extraction from multi-page PDF (structured).
- Steps:
  1. Send PDF attachment containing PO with 5 lines to mailbox.
  2. Check Document Intelligence extraction results and field mapping.
  3. Verify accuracy vs ground-truth.
- Expected:
  - Header and line fields extracted with confidence indicators; line accuracy >=90% for pilot set.

Test Case TC-FUNC-003: Excel Attachment Extraction — Multiple Sheets
- Purpose: Validate Excel (XLSX) attachments, multiple sheets, only first sheet used unless otherwise specified.
- Steps:
  1. Upload XLSX containing PO lines on sheet1; sheet2 contains other data.
  2. System extracts lines from correct sheet.
- Expected:
  - Correct line extraction; wrong-sheet ignored (or flagged per design).

Test Case TC-FUNC-004: Duplicate PO Detection
- Purpose: Detect duplicate by customer PO number.
- Steps:
  1. Send Email A with PO# X to Branch 1.
  2. Send Email B with same PO# X to Branch 1 within short window.
  3. Repeat to Branch 2 (if requirement covers cross-branch duplicate detection).
- Expected:
  - Second email identified as duplicate; flagged in UI; no second draft created (or dedupe behavior per spec).

Test Case TC-FUNC-005: Item Matching — Cross-Reference Present
- Purpose: Verify match via customer cross-reference.
- Steps:
  1. Ensure cross-ref contains mapping customerPart123 -> material 456.
  2. Send PO line with customerPart123.
  3. Verify material 456 assigned in draft and confidence high.
- Expected:
  - Material matched from cross-ref and SAP validation OK.

Test Case TC-FUNC-006: Item Matching — Cross-Reference Missing, Catalog Fallback
- Purpose: Validate fallback to catalog search.
- Steps:
  1. No cross-ref for customerPart999.
  2. Catalog contains material Z that matches description.
  3. Verify system uses AI search and suggests match with lower confidence.
- Expected:
  - Catalog match present; line highlighted for CSR with confidence < threshold.

Test Case TC-FUNC-007: SAP Validation — Price Variance >5%
- Purpose: Flag lines where price deviates greater than 5%.
- Steps:
  1. SAP price for material is $100; PO price is $120 (20% variance).
  2. Send PO.
  3. Verify line flagged in draft and in CSR UI.
- Expected:
  - Price variance flagged, CSR must review.

Test Case TC-FUNC-008: Branch RBAC
- Purpose: Ensure CSRs only see their branch queue.
- Steps:
  1. CSR_A (Branch A) and CSR_B (Branch B) login.
  2. Place POs to Branch A mailbox.
  3. Verify CSR_A sees new drafts; CSR_B does not.
- Expected:
  - Branch scoping enforced.

Test Case TC-FUNC-009: Error Handling — SAP Down
- Purpose: Validate retry/backoff and queueing behavior when SAP API is unavailable.
- Steps:
  1. Simulate SAP APIM returns 503.
  2. Send PO.
  3. Observe retry attempts, message stays in queue or used dead-letter per design.
- Expected:
  - Processing retries per policy; order reprocessed when SAP restored; clear error visible in UI for CSR or admin.

Test Case TC-PERF-001: Throughput — 300 emails/hour
- Purpose: Verify system handles peak load.
- Steps:
  1. Inject 300 emails evenly across an hour and several burst scenarios (500 in an hour).
  2. Monitor time to draft, CPU/RAM, latency to SAP.
- Expected:
  - 95% drafts within 5 minutes under 300/hr; SLA violations captured and analyzed.

Test Case TC-NFR-SEC-001: Azure AD Authentication
- Purpose: Verify access control and session behaviors.
- Steps:
  1. Attempt access to UI/APIs with valid/invalid tokens; verify RBAC.
- Expected:
  - Auth succeeds with valid tokens; unauthorized returns 401/403.

Additional tests:
- Multiple PO per email (edge)
- Non-English or special characters in attachments
- Large attachments (>10MB) and timeouts
- Partial extraction with low confidence vs high confidence thresholds
- CS Admin upload of cross-ref file changes effectivity timely

---

## 15. Performance, Scalability & Availability Testing Plan

Goals:
- Verify draft creation within 5 minutes for 95% of POs under normal and peak loads.
- Validate system resilience under spikes and component throttling (AI, SAP).
- Confirm 99.5% availability 24x5 on non-prod SLA test window as far as feasible.

Test Scenarios:
- Baseline: 100 emails/hour steady-state for 1 hour.
- Peak: 300 emails/hour sustained for 2 hours.
- Burst: 600 emails/hour for 15 minutes, then back to baseline.
- Long-duration: 24-hour soak at moderate load to verify memory leaks or queue build-up.
- Degraded AI service scenario: throttle Document Intelligence and OpenAI rates and observe fallback behaviors and processing backlog.
- SAP throttling simulation: simulate APIM returning 429 and 503 errors; validate retry/backoff and dead-letter handling.

Metrics to collect:
- Time from email receipt to draft creation (P95, P99)
- Processing queue lengths and latency per component
- CPU/memory of AKS pods / service instances
- API success/failure rate and error breakdown
- SLA breach counts and reasons

Acceptance:
- P95 <= 5 minutes for 95% of POs under normal/peak (300/hr).
- System continues processing (no data loss) under degraded conditions; backlog processed after recovery.

---

## 16. Security & Compliance Testing Plan

Areas:
- Authentication & Authorization: Azure AD validation, RBAC (CSR branch scoping).
- Data protection: encryption in transit (HTTPS) and at rest (Blob, Cosmos DB).
- Secrets: Key Vault access patterns and rotation.
- Data minimization: logs do not include full PII or are masked as required.
- Penetration Testing: OWASP Top 10 tests on Web UI, injections, XSS, CSRF, broken auth.
- API security: rate limiting, proper use of tokens, scopes in APIM.
- AI Governance & Privacy: ensure Azure OpenAI usage follows council approvals, data retention policies are respected.

Tests:
- Role-based access tests for all personas.
- Attempt to access other branch drafts via API bypass.
- Inspect logs to ensure no PII leaks.
- Validate certificate and TLS ciphers compliance.
- Run automated OWASP ZAP scans and remediate critical/high issues.

Compliance reporting:
- Provide artifacts demonstrating security reviews and remediation actions for AI Governance Council.

---

## 17. Observability, Logging & Monitoring Tests

- Verify correlation IDs created at mailbox event level and propagated across components (Event Grid -> Service Bus -> Extraction Service -> Order Creation -> APIM -> SAP).
- Validate that end-to-end trace for each email maps to SAP draft order number.
- Validate metrics are emitted: emails processed, drafts created, processing time, extraction confidence distributions, CSR correction rate.
- Verify alerts: sustained queue depth threshold, SLA breaches, repeated failures to SAP, AI auth errors.
- Test instrumentation by intentionally inducing errors and verifying alerts and dashboards.

---

## 18. Defect Management & Severity

Severity levels:
- S0 / Critical: Data loss, orders released without CSR in MVP1, system down for all users. Target fix: immediate hotfix / rollback.
- S1 / High: Critical functionality broken for many users (e.g., extraction not producing headers for majority of POs), or major security vulnerability. Target fix: fix in next patch within SLA.
- S2 / Medium: Feature incorrect behavior for subset; performance degradation under specific conditions. Target fix per sprint.
- S3 / Low: Cosmetic/UI or infrequent edge case. Target fix in backlog.

Defect lifecycle:
- Report -> Triage (daily) -> Assign -> Fix -> QA verification -> Close
- Tool: Azure DevOps / Jira
- Each defect must include reproduction steps, logs/correlation ID, environment, screenshots, and sample email/test data.

SLAs for defect response:
- S0: 2 hours acknowledgement, 24 hours resolution (or rollback) if in production-like environments
- S1: 1 business day acknowledgement, resolution in prioritized sprint
- S2/S3: standard triage in sprint planning

---

## 19. Reporting & Metrics

Reports to produce:
- Daily/weekly test execution status (planned vs executed vs passed/failed)
- Defect summary and aging
- Accuracy Report: header and line accuracy vs ground-truth (pilot customers)
- Performance Report: P50/P95/P99 times, throughput, resource utilization
- Security Report: vulnerabilities found, severity, remediation status
- UAT feedback summary
- Final Test Summary and Recommendation for release

Key QA metrics:
- Header field accuracy (%) — target ≥95%
- Line accuracy (%) — target ≥90%
- Draft creation SLA P95 <= 5 minutes
- Duplicate detection accuracy (%) — target 100% on test set
- CSR correction rate vs automated extraction — measured and trended
- Regression pass rate

---

## 20. Risks, Mitigations & Contingencies

1. Risk: Mailbox access delays/Graph API permissions not provisioned
   - Mitigation: Request mailbox access early; prepare mocks; schedule integration once access confirmed.

2. Risk: SAP integration not available in non-prod or rate-limited
   - Mitigation: Build realistic stubs; run full end-to-end tests as soon as SAP test environment becomes available; define retry/backoff behavior.

3. Risk: AI service rate limits and variability in extraction accuracy
   - Mitigation: Include retry & circuit-breaker logic; maintain confidence flags; increase pilot data to calibrate models; configure fallback (catalog) behavior.

4. Risk: Unusual PO layouts causing extraction failures
   - Mitigation: Implement and test fallback UI workflows; ensure CSR highlights low confidence fields; include training and documentation for CSRs.

5. Risk: Performance issues at peak load
   - Mitigation: Autoscaling, queueing, back-pressure, and performance tuning identified during stress tests.

6. Risk: Sensitive data leak
   - Mitigation: Masking logs, limit data retention, Key Vault, security review, AI governance approvals.

Contingency:
- If major AI extraction underperforms, consider a phased rollout for selected pilot branches only.

---

## 21. Sign-off

Sign-off criteria:
- All critical/high defects closed.
- Acceptance criteria thresholds validated and met by test evidence.
- Business UAT acceptance obtained.
- Security review accepted and critical issues resolved.

Sign-off authorities:
- QA Lead
- Business Owner (Customer Service Operations)
- SAP Integration Lead
- Security Lead / AI Governance rep

---

Appendix: Next steps
- Finalize detailed test cases in test management tool.
- Begin environment provisioning and test data creation.
- Schedule integration smoke tests as soon as first non-prod build is deployed.

If you want, I can:
- Produce the full RTM exported as a table in Markdown mapping every BRD item to specific test cases,
- Generate the complete set of manual test cases (step-by-step) in Azure DevOps format,
- Prepare performance test scripts (k6) templates for the 300/hr scenarios. Which would you like next?