# Test Plan — Supplier Rebate Claim Validation (MVP1)

Version: 1.0  
Author: Senior QA Lead  
Date: 2026-02-17 (aligned with BRS dates)  
Project Owner: Supplier Programs Finance

Contents
1. Purpose & Objectives  
2. Scope (In / Out)  
3. Test Strategy & Approach  
4. Test Items / Features to Test  
5. Test Types and Focus Areas  
6. Test Environment, Tools & Data Requirements  
7. Test Schedule & Milestones  
8. Entry / Exit Criteria  
9. Test Coverage & Traceability to Requirements / Acceptance Criteria  
10. Test Case Templates and Sample Key Test Cases  
11. Non-Functional Testing (Performance, Security, Availability, Auditability)  
12. AI / Document Extraction Testing Approach  
13. Integration & Interface Test Plans (Dependencies)  
14. Defect Management, Severity, and Reporting  
15. Roles & Responsibilities  
16. Risks, Assumptions & Mitigations  
17. Test Deliverables & Sign-off

---

1. Purpose & Objectives
- Provide a complete QA plan to verify MVP1 functionality: PDF upload, AI extraction of terms, analyst confirmation, calculations against Delta Lake purchase data, claim worksheet generation, and exports.
- Ensure the solution meets quality attributes: extraction accuracy (≥95%), calculation accuracy (100% against verified examples), performance (1 supplier-year within 2 minutes; month-end 400 agreements within 8 hours), availability (99% business hours), auditability and security (Azure AD, data restrictions).
- Provide test coverage for functional, integration, system, regression, performance, security, accessibility and AI-specific tests.

2. Scope
In scope (MVP1)
- Upload of rebate agreement PDFs and amendments
- AI extraction of: supplier, period, tiers (thresholds and rates), retroactive vs incremental indicator, eligible product lines and exclusions, page references
- Analyst confirmation UI & workflow (confirmed terms persisted)
- Calculation service pulling purchase data from Delta Lake via Databricks SQL
- Calculation rules: retroactive vs incremental, tier determination, eligible spend
- Claim worksheet generation with supporting purchase lines, Excel export, and variance to accrual
- RBAC for analyst/finance/program admin and approval gating (> USD 50,000) enforcement
- Audit/logging: store agreement version, data snapshot date, reproducible calculation metadata

Out of scope (MVP1)
- Supplier portal submission, dispute tracking, accrual posting, amendment comparison (MVP2)

3. Test Strategy & Approach
- Risk-based testing prioritizing extraction accuracy, calculation correctness, and security.
- Layered approach: Unit/Component tests (dev teams), Integration tests (services + infra), System tests (end-to-end), Performance & Load tests (batch), UAT (business users: Rebate Analysts + Finance Managers), Regression automation for CI.
- For AI components: a mixture of golden dataset evaluation, negative/ambiguous PDF tests, and human-in-the-loop acceptance tests.
- Test early and often; use test doubles (mocks) for some external dependencies in integration tests and run a subset against real services in pre-production for final verification.
- Automate API, UI happy-path and regression cases. Automate data-driven calculation validation where feasible (PyTest + DB assertions).
- Maintain reproducible test data snapshots and environment configuration for auditability.

4. Test Items / Features to Test
- UI: upload flow, progress, extracted term display with page refs, confirmation flow, calculation run trigger, results page, export to Excel, error messages
- Agreement Service: file ingest, metadata extraction, storage to Blob, persistence of confirmed terms to PostgreSQL
- AI Integration: calls to APIM -> Document Intelligence & Azure OpenAI, response handling, fallback & retry logic, page reference mapping
- Calculation Service: Databricks SQL queries, mapping to product lines, tier logic (retroactive, incremental), eligible spend filters, variance to accrual calculation
- Batch Scheduler (Azure Function): month-end batch orchestration
- Data Stores: Blob (agreements), Azure PostgreSQL (terms & results), Delta Lake (purchase data)
- Security: Azure AD authentication, role-based access, prevention of self-approval, secrets via Key Vault
- Observability: logging, metrics, Datadog/Azure Monitor alerts, audit trail of runs
- Export & Reporting: Excel file contents and formatting, supporting purchase lines included
- Error handling & retries (AI service failures, Databricks timeouts)

5. Test Types and Focus Areas
Functional
- Extraction correctness (fields, rates, thresholds, page refs)
- Analyst confirmation persistence and prevention of unconfirmed terms use
- Calculation correctness (unit tests + system tests)
- RBAC & approval workflow (> USD 50k) and self-approval prevention
- UI validation (forms, input validation, file size limits, supported PDF types)

Integration
- Agreement Service <-> Blob Storage
- Agreement Service <-> PostgreSQL
- APIM -> Document Intelligence & OpenAI
- Calculation Service <-> Databricks SQL (Delta Lake)
- Batch Scheduler orchestration

System / E2E
- Full flow: upload PDF -> extraction -> confirmation -> calculation -> worksheet export
- Reproducible calculation using agreement version & data snapshot

Performance & Scalability
- Single supplier-year calculation ≤ 2 minutes
- Month-end batch of 400 agreements ≤ 8 hours
- Concurrent users: concurrent uploads and calculations during business hours without degradation
- Stress test Databricks queries and PostgreSQL writes

Security & Compliance
- Azure AD SSO, role enforcement, data access restrictions
- Data encryption in transit and at rest, Key Vault usage
- SOX-relevant controls coverage (audit trail, segregation of duties)

AI / ML
- Extraction accuracy ≥95% on golden agreements
- Handling ambiguous/complex language
- Robustness to different PDF layouts, scanned images, amendments

Reliability & Observability
- Retry behaviors and alerting on failures
- Audit log completeness (who ran what, snapshot used)

Usability / UAT
- Business user acceptance: Rebate Analysts and Finance Managers validate workflows, debugability, and clarity

Regression
- Automated suite for core functionality and calculation rules

6. Test Environment, Tools & Data Requirements
Environments
- Dev (unit/component)
- Integration (mocks for some external services)
- Pre-Production / Staging (full connectivity to non-prod Azure Document Intelligence, Azure OpenAI sandbox, Databricks non-prod EUDM dataset)
- Production (post-deployment verification under runbook)

Tools
- Test management: Azure DevOps (Test Plans) or equivalent (Jira + Xray)
- API test / automation: Postman, REST-assured, PyTest (requests), or similar
- UI automation: Playwright or Selenium
- Load test: k6 or JMeter
- DB validation & automation: PySpark/Databricks notebooks + pytest-db or custom scripts
- Security scanners: OWASP ZAP, static scanning via GitHub Actions, secrets scanning
- Monitoring: Datadog, Azure Monitor for alerts/metrics
- CI/CD: GitHub Actions for test runs
- Artifact storage and golden dataset: Secure Blob container

Test Data
- Golden agreements dataset (annotated) covering common, edge and complex clauses (≥ sample size needed to validate 95% criterion)
- Negative / malformed PDFs (images, scanned, rotated pages)
- Purchase datasets in Delta Lake: monthly, multiple suppliers, with reconciliation to GL totals
- Product line mapping datasets including product exclusions
- Accrual snapshot values for variance comparisons
- Test user accounts for roles (Analyst, Finance Manager, Program Admin) in Azure AD test tenant
- Mock responses for Document Intelligence & OpenAI for unit/integration tests; real calls in pre-prod

Data Privacy & Security for Test Data
- Use anonymized or synthetic purchase data where production data is not permitted.
- Restrict golden dataset & test data to test tenant with appropriate access controls.

7. Test Schedule & Milestones (High-level for MVP1)
Assuming MVP1 delivery Mar–Jun 2026 (per BRS). Example QA timeline (adjust per project plan):
- Test Plan sign-off: Week 0
- Test environment provisioning: Weeks 1–2
- Test data & golden dataset preparation: Weeks 2–4
- Component & Integration test cycles: Weeks 4–8
- System test (E2E): Weeks 9–11
- Performance & Load testing (single-run & month-end batch): Weeks 11–13
- Security & Compliance testing (including AI Governance checklist): Weeks 12–14
- UAT with Rebate Analysts & Finance Managers: Weeks 14–15
- Regression & stabilization: Weeks 15–16
- Release candidate verification & sign-off: Week 16

8. Entry / Exit Criteria
Entry Criteria (for major test phases)
- Test environment deployed and validated.
- Golden dataset and test purchase data loaded.
- API endpoints reachable; necessary accounts provisioned.
- Dev unit tests passing and build available from CI.
- Test cases written and reviewed.

Exit Criteria (system test -> UAT, and release)
- All critical (P1) defects resolved or have approved exceptions.
- No severity 1 defects open.
- Test coverage: 100% of prioritized functional tests executed; AI extraction metrics measured and ≥95% on golden dataset.
- Performance targets met: single supplier run ≤ 2 minutes; month-end batch ≤ 8 hours (or documented mitigation).
- Security scan results acceptable, no critical vulnerabilities.
- Auditability: runs reproducible with agreement version and snapshot; audit logs validated.
- UAT sign-off by Rebate Programs Finance and Program Admins.

9. Test Coverage & Traceability
- Maintain Requirements Traceability Matrix (RTM): map each BRS functional requirement, user story, and acceptance criterion to at least one test case.
- Key acceptance criteria mapping:
  - ≥95% extraction accuracy -> AI extraction test suite + golden dataset evaluation
  - 100% calculation accuracy (against analyst-verified examples) -> set of data-driven calculation test cases comparing system output to master calculations (analyst verified)
  - Reproducibility with snapshot date -> tests that re-run stored calculation metadata and verify identical results
  - Performance targets -> performance test plans and results

10. Test Case Templates and Sample Key Test Cases
Test case template (to be used in Test Management tool):
- ID
- Title
- Requirement(s) mapped
- Preconditions
- Test data
- Steps
- Expected result
- Actual result
- Status (Pass/Fail)
- Defect ID(s)
- Notes

Sample test cases (representative; full suite to be created in test tool):

TC-UI-001 Upload valid agreement PDF
- Req: Upload of rebate agreements
- Preconditions: Analyst logged in
- Steps: Navigate to Upload -> select valid PDF -> submit
- Expected: File accepted, progress shown, stored in Blob, acknowledgement with file metadata

TC-AI-EXT-001 Extract simple tier terms (happy path)
- Req: Extraction of tiers, rates, period
- Preconditions: Golden PDF with known terms
- Steps: Upload golden PDF -> trigger extraction
- Expected: Extracted supplier, period, tier thresholds and rates match golden annotation; page refs correct; extraction confidence values recorded

TC-AI-EXT-NEG-001 Extract ambiguous language fallback / analyst verification
- Req: Analysts must confirm terms
- Steps: Upload ambiguous clause PDF
- Expected: System flags low confidence; requires manual confirmation; cannot proceed to calculation until confirmed

TC-CALC-001 Calculation — retroactive tier
- Req: Calculation using purchase data; retroactive vs incremental
- Preconditions: Confirmed terms indicate retroactive; test purchase dataset
- Steps: Run calculation for period
- Expected: Rate applied to full eligible spend when threshold is reached; rebate amount matches analyst-calculated expected value

TC-CALC-002 Calculation — incremental tier
- Req: Incremental tier application
- Steps: Run calculation where spend crosses multiple tiers
- Expected: Each tier band computed separately and summed; matches oracle calculation

TC-EXCEL-001 Claim worksheet content & export
- Req: Claim worksheet with supporting purchase lines and variance to accrual
- Steps: After calculation, open worksheet -> export Excel
- Expected: All supporting lines included, totals match UI, Excel format consistent, variance to accrual computed correctly

TC-RBAC-001 Approval gating
- Req: Finance approval for > USD 50k; analysts cannot approve own claims
- Steps: Create claim > 50k as Analyst -> attempt to approve; Login as Finance Manager -> approve
- Expected: Analyst blocked; Finance Manager can approve; audit entry created

TC-PERF-001 Single supplier-year calculation time
- Req: Performance: ≤ 2 minutes
- Steps: Run calculation for supplier-year dataset of expected size
- Expected: Completion time ≤ 2 minutes

TC-BATCH-001 Month-end batch throughput
- Req: Month-end batch of 400 agreements within 8 hours
- Steps: Trigger batch with 400 agreements and representative purchase data
- Expected: Batch completes within 8 hours, no major errors, per-agreement time distribution acceptable

TC-AUDIT-001 Reproducible calculation using snapshot
- Req: Auditability: calculations reproducible with agreement version and data snapshot date
- Steps: Run calculation -> note metadata -> rerun with same snapshot -> compare outputs
- Expected: Outputs identical; logs show agreement version and snapshot used

11. Non-Functional Testing
Performance & Load
- Test cases: single-run perf, concurrency (N concurrent calculation runs), month-end batch 400 agreements.
- Targets: single supplier-year ≤ 2 minutes; batch ≤ 8 hours.
- Tools: k6/JMeter for API/HTTP loads; Databricks performance testing via scheduled notebooks.
- Metrics captured: response time distribution, CPU/memory of Calculation Service, Databricks query times, DB connection pool metrics, retries.

Security Tests
- Authentication & Authorization: validate Azure AD SSO, role-based access enforcement, permission boundary tests (analyst cannot access other suppliers unless mapped).
- Authorization negative tests: attempt to approve own claim; enforce Finance Manager gating.
- Data access: confirm data access restrictions to Blob & PostgreSQL using test roles.
- Vulnerability scanning: static code analysis, OWASP ZAP for UI.
- Secrets: validate Key Vault usage and rotation policies.
- Logging & audit: validate tamper-resistant audit logs are created and accessible for SOX.

Availability & Resilience
- Simulate AI service outage / degraded latency: verify retries, timeouts, user notifications, ability to queue extraction for later, and prevent using unconfirmed extractions.
- Validate idempotency of batch runs and safe re-runs.

Observability
- Validate metric collection for extraction accuracy, calculation durations, queue depths, errors.
- Ensure alerts configured for failures and performance breaches.

12. AI / Document Extraction Testing Approach
Goal: Ensure extraction accuracy ≥95% on golden agreements and robustness to PDF variations.

Golden Dataset
- Curate and annotate a representative set of agreements (≥ sample size to provide statistical confidence — discuss with business; e.g., 200 agreements covering supplier diversity, languages, scanned & born-digital PDFs, amendments).
- Each golden agreement annotated with expected fields: supplier, effective period, tiers (threshold & rate), retroactive flag, eligible product lines & exclusions, page references.

Evaluation Metrics
- Field-level accuracy (precision, recall, F1) for structured fields.
- Page reference correctness rate.
- Overall agreement-level accuracy: whether all required fields correctly extracted.

Test Types
- Unit / integration test with mocked AI responses for parsing pipeline logic.
- Golden dataset automated evaluation in pre-prod with real AI service; compute metrics and compare to acceptance threshold (≥95%).
- Negative/edge-case tests: complex language, inconsistent formatting, scanned images, handwritten annotations, multi-amendment documents.
- Confidence thresholding tests: ensure low-confidence extractions surface to analyst confirmation.
- Drift monitoring: plan for periodic re-evaluation and metric tracking over time.

Human-in-the-Loop Validation
- Confirm that the system forces analyst confirmation before calculation when confidence low or always per requirement.
- UAT to validate annotation display (page refs, highlights) and edit/save behavior.

AI Governance & Compliance
- Ensure that AI Governance checklist items are included in test plan (explainability: page refs & confidence scores, model provenance).
- Document acceptance of model usage by AI Governance Council.

13. Integration & Interface Test Plans
APIM & AI Services
- Validate APIM call correctness, managed identity authentication, latency handling, and error mapping.
- Test for rate-limiting behavior and graceful degradation.

Databricks / Delta Lake
- Validate Databricks SQL queries returning expected aggregates.
- Test credential management (OAuth) and network access.
- Validate reconciliation checks to GL totals.

Azure Blob & PostgreSQL
- Verify file write and read, metadata persistence, and access control.
- Verify database backups & transactional integrity for confirmed terms and results.

Batch Scheduler
- Validate Azure Function scheduling, idempotency (prevent duplicate runs), retry behavior on partial failures.

14. Defect Management & Reporting
- Tool: Azure DevOps (or Jira) issue tracking.
- Severity levels:
  - Critical (P1): system incorrect rebate calculations, data corruption, security breach, inability to perform calculation runs, breach of performance SLA causing business loss.
  - High (P2): extraction accuracy below acceptance threshold for golden dataset, major UI/workflow blockages, major integration failures.
  - Medium (P3): non-blocking UI defects, edge-case extraction errors, minor performance degradation.
  - Low (P4): cosmetic issues, minor logging omissions.
- Defect lifecycle: New -> Triaged -> In Progress -> Fixed -> Verified -> Closed
- Weekly QA status reports including: test execution progress, open defects by severity, performance metrics, extraction accuracy, risks & blockers.

15. Roles & Responsibilities
- QA Lead: test plan, RTM, coordination, test progress reporting
- QA Engineers: test design, automation, execution of integration/system tests
- Performance Engineer: performance, load & capacity tests
- Security Engineer: security & compliance testing
- Data Engineer: prepare test data snapshots, run Databricks notebooks for test validation
- Dev Team: fix defects, write unit tests, support test environments
- Business SMEs (Rebate Analysts, Finance Managers): UAT, golden dataset annotation, acceptance sign-off
- Program Admin: product line mappings test data and configuration validation

16. Risks, Assumptions & Mitigations
Risks
- Delta Lake data gaps -> Mitigation: reconciliation checks to GL, test fallback behavior
- Complex agreement language that AI mis-parses -> Mitigation: mandatory analyst confirmation, annotated golden dataset, negative tests
- Databricks throttling or query slowness at scale -> Mitigation: query optimization, pagination, schedule batch windows
- AI service changes / model drift -> Mitigation: governance, periodic re-evaluation, confidence thresholds and human review

Assumptions
- Test access to Databricks non-prod EUDM mirrors representative production data for last 24 months
- Agreements are mostly digital PDFs (not primarily handwritten scans)
- Azure AI services available in pre-prod sandbox for final verification
- Finance Manager approval workflow will be validated with backend architects (note from user stories)

17. Test Deliverables & Sign-off
Deliverables
- Test Plan (this document)
- RTM mapping requirements to tests
- Test cases and automated test suites
- Golden dataset & extraction evaluation report
- Performance test report (single-run and batch)
- Security test report & vulnerability findings
- UAT test results and sign-off forms
- Final QA summary report and Release recommendation

Sign-off
- QA Lead
- Dev Lead
- Business Owner (Supplier Programs Finance)
- Security / AI Governance Council representative (where applicable)

Appendices

A. Requirement-to-Test Mapping (example; to be implemented in test tool)
- Map each BRS functional requirement line to test cases (e.g., "Extraction of tiers" -> TC-AI-EXT-001, TC-AI-EXT-NEG-001, TC-AI-EXT-REG01)

B. Example Acceptance Test Criteria Checklist (for final verification)
- [ ] Golden dataset extraction accuracy ≥95% (field-level)
- [ ] Calculation outputs match analyst-verified examples (100% for test set)
- [ ] Reproducibility: re-run with snapshot yields identical results
- [ ] Single supplier calculation ≤ 2 minutes
- [ ] Month-end batch of 400 accounts complete ≤ 8 hours
- [ ] RBAC and approval rules enforced, with audit trail
- [ ] Security scan: no P1 vulnerabilities; remediation plan for P2
- [ ] UAT sign-off by Rebate Analysts and Finance Manager(s)

C. Example Automation Strategy
- API tests & calculation validation automated and executed in CI on every PR.
- UI smoke tests automated and run on feature merges.
- Nightly scheduled extraction-evaluation run using golden dataset against latest AI model snapshot (in pre-prod).
- Performance and batch tests scheduled periodically (pre-release and monthly).

D. Estimated QA Effort (high-level)
- Test planning & environment setup: 2–3 weeks
- Test data & golden dataset preparation: 3–6 weeks (parallel)
- Test case development & automation: 4–8 weeks
- System & regression test cycles: 3–4 weeks
- Performance/security testing: 2–3 weeks
- UAT & stabilization: 2 weeks
(Tailor to actual project staffing and calendar.)

Notes / Next Steps
- Create and populate RTM with full set of BRS functional requirements and user stories. Assign priorities.
- Finalize golden dataset size and obtain SME annotations asap.
- Provision pre-prod connectivity to Azure Document Intelligence, Azure OpenAI, Databricks non-prod and Datadog.
- Confirm backend architects for Finance Approval rule implementation details (RBAC / approval workflow).
- Begin test case authoring in chosen test management tool.

If you want, I will:
- produce the detailed traceability matrix (RTM) mapping every BRS requirement to test cases, or
- generate the complete automated test plan skeleton (folders/test scripts) for CI, or
- create the golden dataset sampling plan and annotation schema. Which should I do next?