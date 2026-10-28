# Email Purchase Order Entry Automation — Test Plan (MVP1)

Version: 1.0  
Author: QA Lead  
Date: 2026-03-xx

Purpose: This document defines the QA strategy, scope, test design, environments, acceptance criteria and schedule for validating the Email Purchase Order Entry Automation (MVP1) described in the BRD and architecture docs. It covers functional, integration, non-functional, security, acceptance and regression testing needed to verify the solution meets business and technical requirements.

---

## Table of Contents
1. Objectives
2. Scope (in / out)
3. Test approach and strategy
4. Test types & Coverage
5. Requirements traceability (high level)
6. Key test scenarios and sample test cases
7. Non-functional tests (performance, availability, security, observability)
8. Test data and test artifacts
9. Test environments & tools
10. Roles & responsibilities
11. Test schedule, phases, entry/exit criteria
12. Defect management, reporting & metrics
13. Risks, assumptions & mitigations
14. Test automation strategy
15. UAT / Pilot plan and acceptance criteria
16. Sign-off criteria

---

## 1. Objectives
- Verify that PO emails are processed end-to-end into draft sales orders in SAP (not released).
- Validate data extraction (headers & lines) and confidence scoring.
- Validate customer and item matching logic (cross-reference first, catalog fallback).
- Validate SAP validations and draft order creation via APIM.
- Validate duplicate PO detection.
- Demonstrate performance (draft order within 5 minutes for 95% of POs) and stability at expected peak load (300 emails/hour).
- Validate RBAC, security, observability, and logging.
- Ensure CSR review queue behavior meets BRD requirements.

---

## 2. Scope

In scope (MVP1):
- Mailbox intake via Microsoft Graph.
- Document extraction from email body, PDF and Excel attachments using Azure Document Intelligence and Azure OpenAI.
- Customer identification (sender domain + PO content).
- Item matching (customer cross-reference, then Azure AI Search catalog).
- SAP validation (customer active, material valid, pricing variance flagged) and creating draft sales orders via APIM.
- Draft order storage in Cosmos DB and CSR review Web UI (per-branch access).
- Duplicate PO detection by customer PO number.
- Logging, confidence scoring and traceability (end-to-end trace).

Out of scope (for MVP1):
- Straight-through release (MVP2 feature).
- Acknowledgement emails (MVP2).
- EDI detection/handling (MVP2).
- Analytics (MVP2).
- Credit checks, returns, quotations.

---

## 3. Test approach & strategy

Overall approach:
- Use a layered test approach: unit & component tests (dev responsibility), integration tests (service boundaries), end-to-end (E2E) scenario tests, non-functional tests and pilot UAT with representative branch users.
- Emphasize realistic test inputs: real-world PO formats from pilot branches, scanned images and Excel attachments, and edge cases (missing/ambiguous fields).
- Combine automated tests (API, extraction pipeline, regression suites) with manual exploratory tests (UI review flows, ambiguous OCR outcomes).
- Use sandbox SAP environment and dedicated test mailboxes. Mimic production architecture (Event Grid, Service Bus, Service endpoints) in non-prod.

Test levels:
- Component/unit (dev)
- Integration (APIM -> Azure AI services, Service Bus, Blob, Cosmos, SAP sandbox)
- End-to-end (mailbox -> draft order -> CSR UI)
- System/Regression
- Performance & Load
- Security & Penetration
- UAT / Pilot with CSRs

Quality gates:
- Smoke tests on deployment
- Regression pack for each sprint
- Formal pre-UAT sign-off

---

## 4. Test types & coverage

Functional tests:
- Mail ingestion (Graph / Event Grid trigger)
- Duplicate detection
- Document extraction (header & lines)
- Confidence scoring per field
- Customer identification
- Item matching (cross-ref and catalog fallback)
- SAP validation rules (customer active, material valid, price variance flag)
- Draft sales order creation (not released)
- CSR Review UI (view, edit, save, requeue)
- Branch-based RBAC for queues
- Error handling, retries and dead-lettering

Integration tests:
- Event Grid -> Service Bus -> Extraction Service flow
- APIM connectivity to Azure Document Intelligence, Azure OpenAI, Azure AI Search
- Order Creation Service -> Cosmos DB and APIM->SAP sandbox
- Blob Storage persistence (email copies) and retrieval
- End-to-end traceability logging

Non-functional tests:
- Performance (throughput, latency: 5-minute SLA, peak 300 emails/hr)
- Stress & soak tests
- Availability (99.5% 24x5 target)
- Resilience (service restarts, transient SAP API failures)
- Scalability (Service Bus and processing scaling)

Security & compliance:
- Azure AD authentication and RBAC verification
- Data-in-transit & at-rest encryption checks (Key Vault usage)
- Data masking where required for logs
- Penetration tests of public endpoints (App Gateway, APIM)

Usability / Accessibility:
- CSR Web UI usability, error feedback, visibility of confidence flags

Observability & monitoring:
- End-to-end trace per email to SAP draft order number
- Metrics: time-to-draft, extraction accuracy, CSR correction rate

Regression:
- Full regression suite covering critical functional flows before each release.

---

## 5. Requirements traceability (high level)
For each BRD requirement, tests will be designed to validate it. Examples:
- Mailbox intake via Microsoft Graph: validate detection of new mail, Event Grid event creation, Service Bus enqueuing.
- Duplicate PO detection: test with same customer PO number repeated, ensure second message flagged/blocked.
- Extraction of header & lines: verify extracted values and confidence per field across formats (text PDF, image PDF, Excel).
- Customer identification: verify domain-based mapping and content-based fallback.
- Item matching: cases where cross-ref exists; cases where no cross-ref and catalog search returns candidate; cases of no match.
- SAP validation and draft creation: positive and negative flows (invalid customer, invalid material, price variance >5% flagged).
- CSR review queue: CSR sees draft, can edit, save and confirm not released.
- Non-functional: draft in <5 minutes for 95% in test dataset; peak load processing; RBAC branch isolation.

A detailed Requirements Traceability Matrix (RTM) will map each BRD item to test cases and will be maintained in the test repository.

---

## 6. Key test scenarios & sample test cases

Note: test cases will be captured in the test management tool (Jira Xray/Zephyr/TestRail). Below are representative scenarios and sample cases.

6.1 Mail intake & routing
- TC-F-001: New email in branch mailbox triggers Event Grid event and places message on Service Bus. Verify event metadata includes mailbox, timestamp, message-id.
- TC-F-002: Email with multiple attachments (PDF + Excel) is copied to Blob Storage and referenced by extraction service.
- TC-F-003: Email lacking body but with PO in attachment is processed successfully.

6.2 Duplicate PO detection
- TC-F-010: Two emails for same sold-to and same customer PO number within retention window -> second flagged as duplicate and not re-created as draft. Verify duplicate flag and notification in UI/logs.
- Negative: Slightly different PO numbers -> should not be considered duplicate.

6.3 Document extraction
- TC-F-020: Text-based PDF with standard PO layout -> header and lines extracted with confidence >= threshold.
- TC-F-021: Scanned image PDF requiring OCR -> extracted values and confidence scores; verify corrections possible in UI.
- TC-F-022: Excel PO file with multiple sheets -> extraction uses first meaningful sheet; lines parsed.
- TC-F-023: Malformed attachment with missing quantities -> extraction marks missing fields with low confidence and highlights in UI.

6.4 Customer identification
- TC-F-030: Sender domain maps to known customer -> correct sold-to identified.
- TC-F-031: No domain mapping but sold-to appears in PO body -> identification via content fallback.
- TC-F-032: Ambiguous match -> system flags for CSR manual selection.

6.5 Item matching
- TC-F-040: Customer part number present in cross-reference -> material matched, confidence high.
- TC-F-041: No cross-ref -> Azure AI Search returns multiple candidates -> top candidate selected with confidence; CSR sees highlight.
- TC-F-042: No match found in catalog -> line flagged for CSR action.
- TC-F-043: UoM present but not valid in SAP -> validation error flagged.

6.6 SAP validation & draft order creation
- TC-F-050: Valid customer, valid materials, price within 5% -> draft created in SAP sandbox and draft number stored in Cosmos DB; trace logged.
- TC-F-051: Price variance >5% -> draft created but line flagged, CSR alerted.
- TC-F-052: Inactive customer -> draft NOT created; error status stored; CSR notified.
- TC-F-053: SAP API timeout/failure -> retries and eventual dead-lettering observed; transient errors retried per policy.

6.7 CSR Review UI
- TC-F-060: CSR sees draft for their branch only; can edit header and lines; saving updates Cosmos DB and SAP draft if re-sent.
- TC-F-061: Confidence indicators displayed per field; CSR can filter by low-confidence lines.
- TC-F-062: Orders older than 30 minutes flagged for supervisor (simulate time).

6.8 Observability & logs
- TC-F-070: End-to-end trace for an email includes mailbox message id, extraction request id, Service Bus message id, APIM call id and SAP draft number.
- TC-F-071: Metrics for time-to-draft captured and exposed to Datadog/Azure Monitor.

6.9 Edge & negative cases
- TC-F-080: Email contains multiple POs (contrary to assumption) -> system behavior documented: create one draft per PO if supported or escalate to CSR. Validate chosen approach.
- TC-F-081: Extremely large attachments -> system handles or rejects gracefully per limit.
- TC-F-082: Corrupted attachment -> processing error, audit log, and CSR notification.

6.10 Security & RBAC
- TC-S-001: User without branch privileges cannot view other branches’ orders.
- TC-S-002: Authentication failure to Azure AD blocked.
- TC-S-003: Secrets access via Key Vault limited to managed identity.

---

## 7. Non-functional tests

7.1 Performance & Load
- Goal: 95% drafts created within 5 minutes of email receipt.
- Tests:
  - Baseline throughput test: steady 300 emails/hr across multiple branches.
  - Spike test: sudden burst to 600 emails/hr and observe behavior, queuing and throttle.
  - Endurance/soak test: sustained 300/hr for 24 hours.
  - Measure per-email time distribution (P50, P90, P95, P99).

7.2 Scalability & Resilience
- Scale worker replicas, Service Bus partitions and ensure throughput scales.
- Inject SAP API transient errors and validate retry logic and dead-letter.

7.3 Availability
- Simulate component failure (Order Extraction pod restart; Document Intelligence latency) and validate system remains within SLA and recovers.

7.4 Security testing
- Pen test of public endpoints (App Gateway/APIM).
- Authorization tests for RBAC.
- Validate encryption (TLS), Key Vault policies and log masking.

7.5 Observability
- Validate traceable IDs surface in logs and Datadog.
- Verify alerts for failure rates, high queue depth, >30 min in queue, SLA breaches.

---

## 8. Test data & artifacts

Test data types:
- Sample PO emails collected from pilot branches (sanitized/pseudonymized).
- Synthetic emails created to exercise edge cases (missing fields, multiple POs).
- Attachments:
  - Text-based PDFs (common layouts).
  - Scanned PDFs (images with varying quality).
  - Excel templates (single and multi-sheet).
  - Malformed files.
- Customer cross-reference files (valid, incomplete, conflicting).
- Catalog index in Azure AI Search (seeded copy of catalog).
- SAP sandbox master data variations (active/inactive customers, materials, price differences).

Data management:
- Use separate non-prod mailboxes and test tenants.
- Sanitize any PII/customer confidential data; where production data is used, follow governance approval.
- Seed Cosmos DB and Blob Storage with required baseline items for regression tests.
- Versioned cross-reference uploads for repeatable tests.

Artifacts to maintain:
- Test cases in test management tool.
- RTM mapping test cases to BRD requirements.
- Test data definitions and generation scripts (for automation).
- Test run reports and performance logs.
- Defect log in Jira (with severity/priority and trace links).

---

## 9. Test environments & tools

Environments:
- Dev: unit/component tests (not for integration work).
- Integration/non-prod: mirrors architecture (Event Grid, Service Bus, AKS, APIM, Document Intelligence sandbox, Azure OpenAI test keys, Azure AI Search test index, Blob Storage, Cosmos DB, SAP sandbox).
- UAT/Pilot: environment connected to pilot branch mailboxes and CSR testers. Use separate SAP test tenant.
- Tools should be configured for deterministic behavior (fixed test data seeds).

Tools:
- Test management: Jira + Xray / Zephyr / TestRail
- Defect tracking: Jira
- API testing: Postman / Newman, REST-assured
- Automation & CI: GitHub Actions (aligned to architecture)
- UI automation: Playwright or Selenium
- Load testing: k6, JMeter, or Azure Load Testing
- Monitoring: Datadog & Azure Monitor
- Secrets management: Key Vault
- Source control: GitHub
- Data generation: Python/PowerShell scripts
- Document AI validation: custom comparators & golden datasets

Network/security:
- Ensure network access to external AI services, SAP sandbox via APIM endpoints, and necessary firewall rules.

---

## 10. Roles & responsibilities

- QA Lead (owner of test plan): finalize test plan, manage test execution, report quality metrics, acceptance sign-off.
- Test Engineers: design & execute test cases, automate suites, create test data, run performance and security tests.
- Developers: unit tests, fix defects, support integration testing, implement test hooks.
- Integration / SAP Team: provide sandbox endpoints, support SAP test scenarios, validate draft orders in SAP.
- CSRs (business testers): UAT and pilot participants; validate real workloads and acceptance criteria.
- CS Supervisor & CS Admin: participate in acceptance scenarios (queue monitoring, reassign).
- DevOps: maintain test environments, CI/CD pipelines, load test infrastructure.
- Security Team: perform pen test and signoff.

---

## 11. Test schedule, phases, entry & exit criteria

Phases (MVP1):
- Test planning & environment setup (2–3 weeks)
- Development & component tests (ongoing)
- Integration testing (2–3 sprints)
- System E2E testing (2 sprints)
- Performance, scalability & security testing (1 sprint)
- UAT / Pilot (2–3 weeks with pilot branches)
- Release readiness & sign-off

Sample entry criteria for E2E:
- Integration endpoints available (APIM, AI services, SAP sandbox).
- Test data and mailboxes seeded.
- >=80% of planned functional tests automated and passing in previous stages.
- No P0/P1 open defects blocking core flows.

Sample exit criteria for release to UAT:
- All P0 defects resolved.
- >=95% of smoke tests pass.
- Performance tests meet P95 SLA (<=5 minutes) on test dataset.
- Security scan findings triaged with risk accepted or remediated.

Release to production (MVP1) readiness:
- Acceptance criteria (BRD) met in pilot: header accuracy >=95%, line accuracy >=90%, draft within 5 minutes for 95% POs, no auto-release.
- All critical defects closed and medium defects accepted with mitigation.
- Runbook and rollback plan validated.

---

## 12. Defect management & reporting

- Tool: Jira (defect issue type) with priority levels:
  - P0 (Showstopper): system unusable for core flows (e.g., no drafts created).
  - P1 (Critical): major feature broken or data integrity issue (duplicate detection failing).
  - P2 (High): key functionality degraded (confidence flags missing).
  - P3 (Medium): non-critical functionality or UI issues.
  - P4 (Low): cosmetic or minor items.

- Defect lifecycle: Open -> Triaged -> In Progress -> Fixed -> Verified -> Closed.
- Triage frequency: daily during active test cycles.
- Weekly QA status report: test progress, pass/fail rates, defect trends, performance metrics, risks.
- Test metrics:
  - Test coverage (% of planned cases executed)
  - Pass rate
  - Defect density and trend
  - Mean time to detect & resolve critical defects
  - Performance SLA attainment (P95 time-to-draft)
  - Extraction accuracy (header / line accuracy) vs. BRD targets

---

## 13. Risks, assumptions & mitigations

Risks:
- Unusual PO layouts cause extraction failures.
  - Mitigation: CSR review with confidence flags, iterative Document Intelligence model tuning, sample-driven training.
- Missing/incomplete cross-reference files for customers.
  - Mitigation: Catalog fallback and clear UI flags for CSR; CS Admin upload process.
- SAP API limits / throttling.
  - Mitigation: Queueing, exponential backoff and retries; coordinate with SAP team for rate limits.
- Mailbox access delays or Graph API permissions issues.
  - Mitigation: Early mailbox access requests; test mailboxes created.
- Use of production data without approvals.
  - Mitigation: Data sanitization and AI governance sign-off.
- Performance issues at peak.
  - Mitigation: Performance tests, autoscaling policies, backlog handling.

Assumptions:
- One PO per email in most cases; multiple POs handled via defined behavior (test to confirm).
- Cross-reference files exist for top 200 customers (seeded for pilot).
- SAP sandbox provides representative behavior for validation.

---

## 14. Test automation strategy

Automation goals:
- Automate smoke, regression and API integration tests to accelerate CI/CD.
- Automate pipeline triggers to run tests on PRs and nightly full regression.

Scope:
- Unit tests (dev)
- API/integration automation: Postman / REST-assured / Playwright for APIs (APIM endpoints), including mocks for AI services where necessary.
- Document extraction validation automation: automated submission of sample documents and verification against golden dataset.
- UI automation: Playwright for CSR review UI critical flows (view/edit/save).
- Load tests: k6 or Azure Load Testing scripts to simulate mailbox event load.
- Data-driven tests: use CSV/JSON of sample PO emails and expected extraction outputs.

CI/CD:
- Use GitHub Actions to run automated tests on build and PRs. Nightly runs for full regression and nightly load tests for early detection.

Maintenance:
- Keep golden datasets and expected outputs in version control.
- Tag test datasets with schema and version to align with model updates.

---

## 15. UAT / Pilot and Acceptance testing

UAT objective:
- Validate the system meets BRD acceptance criteria with real users (CSRs) and representative data.

Pilot plan:
- Select pilot branches (representative set including highest volume & some edge-case customers).
- Duration: 2–3 weeks of real emails flowing to non-prod/UAT environment or a controlled pilot in production (per business decision).
- Participants: CSR testers, CS Supervisors, CS Admin.

UAT activities:
- End-to-end processing of real or synthetic PO emails.
- Record extraction accuracy metrics and CSR correction rates.
- Validate SLA: time-to-draft measurements.
- Validate no orders auto-released (MVP1).
- Conduct feedback sessions and collect improvement items.

Acceptance criteria (from BRD):
- Header field accuracy >=95% (pilot measured).
- Line accuracy >=90% (pilot measured).
- Draft created within 5 minutes for 95% of POs.
- Duplicate PO detection success 100% on test set.
- CSR review queue functioning and branch RBAC enforced.

Acceptance test evidence:
- Test run reports, sampled transcripts of drafts vs. source POs, Datadog/Azure Monitor time metrics, defect closure summaries, and business sign-off.

---

## 16. Sign-off criteria

QA sign-off will be provided when:
- All P0/P1 defects are resolved.
- Acceptance criteria metrics met in UAT/pilot.
- Performance tests show P95 <= 5 minutes and system can handle expected peak with acceptable margin.
- Security assessment completed and any critical issues remediated.
- Observability and runbooks in place for incident handling.
- Business owner and CS stakeholders provide formal acceptance.

After sign-off, proceed to deployment to production per release plan.

---

## Appendix

A. Example of planned test data categories
- Normal: well-structured PDF POs from top customers.
- OCR: scanned POs with various DPI and noise.
- Excel: PO templates exported from customers' ERPs.
- Corner: missing PO number, multiple PO numbers, unusual UoM.
- Negative: invalid customer, inactive material, price outliers.

B. Monitoring & metrics to track in release
- Emails processed per hour
- Mean & P95 time-to-draft
- Extraction accuracy (header & line)
- CSR correction rate
- Draft creation success rate (SAP)
- Duplicate PO detection rate
- Queue depths & error rates

C. Deliverables from QA
- Test plan (this document)
- RTM (mapping tests to BRD)
- Test cases & automation scripts
- Test execution and defect reports
- UAT reports and acceptance evidence
- Lessons learned & post-mortem

---

If you want, I will:
- Produce the detailed RTM mapping each BRD requirement to test case IDs.
- Generate a prioritized test case list (spread across sprint deliveries).
- Create sample automated Postman collections and k6 scripts for initial performance tests. Which would you like next?