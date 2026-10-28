# Supplier Rebate Claim Validation — Test Plan (MVP1)

Version: 1.0  
Date: 2026-02-17 (aligned to BRS)  
Prepared by: QA Lead — Supplier Rebate Claim Validation

---

## 1. Purpose

This test plan defines the testing approach, scope, resources, schedule, test cases, entry/exit criteria and acceptance criteria for MVP1 of the Supplier Rebate Claim Validation project. MVP1 covers: agreement PDF upload, AI extraction of terms (tiers/rates/periods/product lines/exclusions), analyst confirmation, calculation against purchase data in Delta Lake (Databricks SQL), claim worksheet generation and exports, and variance to accrual reporting.

---

## 2. Objectives

- Verify automated extraction produces correct tier terms (≥95% accuracy on golden dataset).
- Verify calculations reproduce analyst-verified examples (100% accuracy).
- Verify analyst confirmation gating prevents unconfirmed terms from being used.
- Verify performance targets: single supplier-year calc ≤ 2 minutes; month-end batch (400 agreements) ≤ 8 hours.
- Verify security, auditability, RBAC and data quality requirements.

---

## 3. Scope

In scope (MVP1):
- PDF agreement upload (including amendments)
- Extraction via Azure Document Intelligence & Azure OpenAI:
  - Supplier, period, tiers (threshold + rate), retroactive vs incremental, eligible product lines, exclusions, page references
- Analyst confirmation workflow
- Calculation service (Databricks SQL against Delta Lake) producing:
  - Eligible spend, tier reached, earned rebate (retroactive vs incremental)
- Claim worksheet with supporting purchase lines, Excel export, variance to accrual
- Auditability: agreement version and data snapshot date captured

Out of scope (MVP1):
- Supplier portal submission
- Dispute tracking
- Accrual posting
- Amendment comparison (beyond upload)

---

## 4. Quality / Acceptance Criteria (from BRS)

- Extraction accuracy: ≥95% of tier terms on golden agreements.
- Calculation accuracy: 100% against analyst-verified examples.
- Performance: single supplier-year calc ≤ 2 minutes; month-end batch (400) ≤ 8 hours.
- Availability target: 99% business hours.
- Auditability: every calculation reproducible with agreement version + data snapshot date.
- RBAC: Approvals > USD 50,000 require Finance Manager; analysts cannot approve their own claims.

---

## 5. Test Strategy

Approach:
- Risk-based testing with focus on AI extraction accuracy, calculation correctness, data reconciliation, RBAC, auditability and performance.
- Layered testing: unit/component tests (dev), integration (services + Databricks + AI), system tests (end-to-end), performance/load, security, regression, and UAT with Supplier Programs SMEs.
- Use a golden dataset of agreements and analyst-verified calculations for acceptance testing.
- Automation where feasible: API tests, calculation verification, regression suites, smoke tests, and parts of performance testing.
- Manual testing for AI ambiguity handling, analyst UX flows, edge-case documents, and exploratory tests.

Test types:
- Unit / Component (developer/QA)
- API / Integration
- AI/ML validation (precision/recall/confidence thresholding)
- Functional system (end-to-end)
- Data quality / reconciliation
- Performance / Load / Scalability
- Security / RBAC / Penetration basics
- Accessibility / Usability (analyst workflows)
- Regression
- UAT (Supplier Programs analysts + Finance Manager)

Pass/fail gates:
- Critical defects: none open at release.
- Major defects: ≤1 judged acceptable with documented mitigation (rare).
- Acceptance criteria thresholds (AI/calculations/performance) must be met.

---

## 6. Test Items (Components)

- Web UI (upload, term review, run calc, worksheet view, export)
- Agreement Service (uploads, store to Blob, persisted terms to PostgreSQL)
- Calculation Service (runs Databricks SQL; reads Delta Lake; writes results)
- Batch Scheduler (Azure Function) — month-end runs
- Azure Document Intelligence & Azure OpenAI – extraction pipeline via APIM
- Azure Blob Storage — agreements
- Azure PostgreSQL — confirmed terms and results
- Databricks SQL / Delta Lake — purchase data
- Azure AD integration / RBAC
- Monitoring/Logging/Telemetry (Datadog, Azure Monitor)

---

## 7. Test Environment & Setup

Environments:
- Dev: unit/component tests (CI)
- QA/Integration: non-production subscription as per architecture (APIM wired to test AI endpoints or mocks, Databricks test cluster, Azure Postgres, Blob)
- Performance/Staging: scaled resources to simulate production monthly batch (Databricks cluster size representative)
- UAT: environment with realistic data slices and golden dataset

Required provisioning:
- Azure AD test tenant accounts for Analyst, Finance Manager, Program Admin
- Databricks workspace and SQL warehouse with a copy/masked subset of Delta Lake purchase data (last 24 months)
- APIM connection to Azure Document Intelligence & Azure OpenAI (or test mode/mocks)
- Blob storage with test PDFs (golden agreements + edge-case PDFs)
- Postgres test DB with schema and seeded configurations (product line mappings, supplier mappings)
- Key Vault with test secrets
- Monitoring and logging enabled

Test data:
- Golden agreements (set of ~100 agreements representative of complexity)
- Analyst-verified calculation examples (10–20 per key pattern)
- Delta Lake purchase datasets: complete, partial, returns/credit notes, multiple product lines, missing days
- Product line mapping configuration variants
- Edge-case PDFs: scanned images, two-column layouts, tables, footnotes, amended contracts, multi-language if applicable

Data masking:
- Use masked PII where necessary; ensure compliance for confidential data.

Dependencies:
- Data platform team access
- AI services whitelisted for non-prod
- Supplier Programs SMEs for golden dataset and UAT validation

---

## 8. Roles & Responsibilities

- QA Lead: Plan execution, reporting, traceability
- QA Engineers: Create/execute test cases, automation, defect reporting
- Developers: Unit tests, fix defects
- Data Engineers: Provide Delta Lake test data and Databricks access
- AI Engineers/Architects: Provide AI endpoints, extraction tuning, golden dataset
- Product Owner / Supplier Programs SME: Provide golden dataset, validate UAT acceptance, sign-off
- Finance Representative: Approve UAT scenarios for approval workflow (>$50k)
- Security Team: Conduct security reviews/pen tests as scheduled
- Release Manager: Coordinate deployment to QA/UAT/Staging

---

## 9. Test Tools & Automation

- Test management: Azure DevOps / Jira (test cases, defects, reporting)
- API testing: Postman / Newman / REST-assured
- UI automation: Playwright or Selenium (select Playwright preferred)
- Backend/SQL verification: pytest with Databricks JDBC/ODBC connectors or Databricks notebooks + assertion frameworks
- Performance/load: Locust or JMeter
- AI validation tooling: custom Python scripts to compare extracted fields to golden annotations; compute precision/recall/F1
- CI/CD: GitHub Actions (existing infra), integrate nightly regression runs
- Monitoring: Datadog, Azure Monitor for logs and metrics
- Reporting: Automated test run reports uploaded to pipeline; daily test status dashboards

---

## 10. Traceability Matrix (summary)

Map of major FRs to test areas (sample):

- FR: PDF upload -> Tests: Upload success, malformed PDF, scan image, large file size
- FR: Extraction of tiers/rates/periods/product lines -> Tests: Extraction accuracy (golden), page refs, ambiguous wording, missing fields
- FR: Analyst confirmation -> Tests: UI presents extracted terms, confirm/reject flows, edits persisted, unconfirmed terms not used
- FR: Calculation (retroactive vs incremental) -> Tests: Correct math for retroactive, incremental, boundary thresholds, returns/credits, currency
- FR: Databricks SQL / Delta Lake integration -> Tests: Query correctness, performance, retry handling, data snapshot
- FR: Worksheet export to Excel -> Tests: Excel formatting, supporting lines, variance to accrual, snapshot metadata
- FR: RBAC/Approval (>$50k) -> Tests: Finance approval flow, analysts cannot approve own claims, audit trail
- FR: Auditability -> Tests: calculation reproducibility by agreement version & data snapshot date
- Non-functional: Performance -> Tests: single calc time, batch run time
- Security -> Tests: Azure AD auth flows, storage access, encryption, privileged access

(Full traceability matrix to be maintained in test management tool.)

---

## 11. Test Scenarios & Representative Test Cases

Below are grouped representative test cases. Each test case will be authored in the test management tool with steps, expected results, data, preconditions and post-conditions.

Naming convention: T-<Group>-<NN>

### A. Agreement Upload & Storage

T-UP-01: Upload valid PDF agreement
- Preconditions: User logged in as Rebate Analyst
- Steps: Upload a valid agreement PDF
- Expected: File stored in Blob; metadata created; preview available

T-UP-02: Upload amendment PDF and link to base agreement
- Expected: Amendment linked; versioning created; page refs preserved

T-UP-03: Upload scanned image PDF (OCR)
- Expected: Document Intelligence returns OCR; extraction pipeline handles scanned text

T-UP-04: Upload extremely large PDF (> allowed size)
- Expected: Error message with allowed size; file rejected

T-UP-05: Corrupted/invalid PDF
- Expected: Graceful error and logging

### B. AI Extraction (Azure Document Intelligence + OpenAI)

T-AI-01: Extract tiers, rates and thresholds from golden agreement
- Data: Known golden agreement
- Expected: All tiers, thresholds, rates and page references match golden annotations; accuracy measured

T-AI-02: Identify retroactive vs incremental
- Expected: Correct flag set; page ref returned

T-AI-03: Extract eligible product lines and exclusions
- Expected: All eligible lines and exclusions matched; mappings suggested

T-AI-04: Extraction confidence < threshold -> flag for manual review
- Input: Agreement with ambiguous language
- Expected: Extract results flagged as low confidence; Analyst must confirm

T-AI-05: Multi-column / table-based tiers
- Expected: Correct extraction with correct thresholds and page references

T-AI-06: Missing explicit tier (implicit wording)
- Expected: Extraction either reasonable inference with low confidence OR flagged for analyst

Metrics to capture:
- Precision/Recall/F1 for fields (supplier, period, tier thresholds, rates, retro/inc, product lines)
- Overall accuracy across golden set (target ≥95%)

### C. Analyst Confirmation & Editing

T-CONF-01: Analyst sees extracted terms with page refs
- Expected: UI shows terms and corresponding page locations and confidence scores

T-CONF-02: Analyst edits a tier threshold and saves
- Expected: Edited terms persisted; version created; extraction metadata retained

T-CONF-03: Unconfirmed terms cannot be used to run calculation
- Steps: Extract but do not confirm, attempt calculation
- Expected: System prompts to confirm terms before calculation

T-CONF-04: Audit trail of who confirmed and when
- Expected: PostgreSQL record shows user, timestamp, version id

### D. Calculation Logic

T-CALC-01: Retroactive calculation scenario
- Data: Single supplier-year with spend X between thresholds for retroactive rule
- Expected: Earned rebate = rate at reached tier * total eligible spend (full spend), matches analyst-verified math

T-CALC-02: Incremental calculation scenario (banded)
- Data: Multiple tiers
- Expected: Each tier band calculated separately, sum equals expected; matches analyst example

T-CALC-03: Boundary threshold (exactly at threshold)
- Expected: Correct tier assignment per definition (documented rule); test both inclusive/exclusive interpretations

T-CALC-04: Returns/negative adjustments in purchase data
- Expected: Calculation handles credits per rules (if defined); flagged if ambiguous

T-CALC-05: Eligible product line mapping applied
- Expected: Only purchases mapped to eligible product lines included; exclusions removed

T-CALC-06: Multiple purchase lines across days and currencies
- Expected: Currency handling (if relevant) and date-range filtering work; conversion applied if required (confirm rule), otherwise flagged

T-CALC-07: Missing purchase data / gaps
- Expected: Reconciliation UI shows missing data and variance to GL; calculation completes with warnings

T-CALC-08: Reproducibility: rerun calculation with same data snapshot & agreement version -> same result
- Expected: Identical outputs and audit records

T-CALC-09: Calculation accuracy against golden analyst examples (multiple)
- Expected: Exact numeric match for all golden examples (100% pass)

### E. Claim Worksheet & Export

T-WKS-01: Generate claim worksheet
- Expected: Claim worksheet shows eligible spend lines, tier reached, earned rebate, data snapshot id, agreement version

T-WKS-02: Excel export format and contents
- Expected: Export opens in Excel; columns present; supporting lines included; correct totals and formatting

T-WKS-03: Variance to accrual report
- Expected: System calculates variance vs accrual and displays correctly

T-WKS-04: Large worksheet export (many lines)
- Expected: Export within acceptable time; memory usage stable

### F. RBAC & Approvals

T-RBAC-01: Analyst role permissions
- Expected: Upload, confirm, run calculations, but cannot approve claims > $50k

T-RBAC-02: Finance Manager approval required > $50k
- Steps: Create claim > $50k
- Expected: Approval workflow routes to Finance Manager; only Finance Manager can approve

T-RBAC-03: Analyst cannot approve own claims
- Expected: Approval action constrained; attempt to approve own claim blocked with message

T-RBAC-04: Logs for approval actions
- Expected: Audit record with user, timestamp, action

### G. Integration & Data

T-INT-01: Calculation Service connects to Databricks SQL warehouse with OAuth
- Expected: Successful queries; retries on transient errors

T-INT-02: Agreement Service persists confirmed terms to PostgreSQL
- Expected: Data integrity; constraints enforced (tier thresholds ascending)

T-INT-03: Blob access controls
- Expected: Only permitted roles can read agreements; SAS tokens behavior tested

T-INT-04: Data reconciliation to GL totals
- Expected: Reconciliation reports show totals and discrepancies; data completeness checks pass for test set

### H. Performance & Scalability

T-PERF-01: Single supplier-year calculation latency
- Load: baseline config
- Expected: ≤ 2 minutes per supplier-year (measure median/95th percentile)

T-PERF-02: Month-end batch run
- Load: 400 agreements run in scheduled batch
- Expected: Complete within 8 hours; resource utilization tracked

T-PERF-03: Concurrent calculator runs (N concurrent analysts)
- Expected: System scales appropriately; queuing/throughput policies enforced

T-PERF-04: Excel export under large data volume
- Expected: Export completes under threshold time

Tools: Locust/JMeter; Databricks job metrics; Azure Monitor.

### I. Security & Compliance

T-SEC-01: Azure AD authentication & SSO
- Expected: Login flows, token expiration, refresh handled

T-SEC-02: RBAC enforcement tests (least privilege)
- Expected: Role-based actions restricted

T-SEC-03: Data-at-rest and in-transit encryption verification
- Expected: Storage/DB encrypted; TLS enforced

T-SEC-04: Logging of access to confidential data and role-based audit trail
- Expected: Audit logs captured and available in monitoring

T-SEC-05: SOX-relevant controls review (C2P)
- Expected: Controls documented; test evidence supplied

T-SEC-06: Basic pentest/scan (dependency scanning)
- Expected: Critical vulnerabilities resolved / mitigated before production

### J. Error Handling & Resilience

T-ERR-01: AI service outage simulated
- Expected: Graceful degradation: queued extraction requests; admin alerts; analyst can upload but extraction pending

T-ERR-02: Delta Lake connectivity loss during calculation
- Expected: Retry logic invoked; clear error to user; partial results not persisted

T-ERR-03: Calculation error mid-run
- Expected: Transactional behavior: no partial claim committed; errors logged and surfaced

---

## 12. AI/ML Validation Approach

- Golden dataset: curated set of agreements with hand-labeled fields (supplier, periods, tier thresholds, rates, retro/inc flag, product lines, page refs).
- Evaluate per-field metrics: precision, recall, F1, and overall extraction accuracy.
- Acceptance: ≥95% correctness on tiers/rates/threshold extraction across golden dataset.
- Confidence thresholds: define thresholds below which UI forces analyst review; test threshold behavior.
- Drift monitoring: tests for model regression after model updates; include nightly/weekly validation run on golden set in CI.
- Error taxonomy: classify AI extraction errors (missed tier, wrong threshold, wrong rate, wrong page ref, wrong retro/inc classification) to prioritize fixes.

---

## 13. Test Data Management

- Maintain separated datasets:
  - Golden agreements (annotated)
  - Standard test agreements (edge cases)
  - Delta Lake test data (complete, partial, returns)
- Version control test datasets; tag by date snapshot
- Mask/transform any real sensitive data per security policy
- Provide sample product line mapping matrices for Program Admin tests

---

## 14. Automation Strategy

- Automate smoke tests in CI for every deployment: authentication, upload, simple extraction flow (with mocks), minimal calculation
- Automate API integration tests for Agreement Service, Calculation Service, APIM interactions
- Automate calculation correctness tests by running Databricks SQL and asserting expected totals for golden examples
- Daily/ nightly AI validation job against golden dataset (compute accuracy metrics)
- Automate regression suites for critical paths
- Manual tests remain for exploratory AI behavior, ambiguous PDFs, UAT sign-off

---

## 15. Defect Management & Severity

Severity definitions:
- Critical (P0): Data loss, incorrect calculations affecting financial claims, security breach, inability to run calculations at month-end
- Major (P1): Key function broken (e.g., upload or extraction) but workaround exists
- Minor (P2): UI glitches, cosmetic issues, low-impact failures
- Trivial (P3): Documentation, minor layout issues

Defect lifecycle: Log in Jira/Azure DevOps -> Triage daily -> Assign -> Fix -> Verify -> Close

Acceptance to release: No unresolved P0; P1 defects require documented mitigation & PO approval.

---

## 16. Entry & Exit Criteria

Entry Criteria (to begin system testing):
- Dev unit/component tests passed
- QA environment provisioned with all integrations (or validated mocks)
- Golden dataset and Delta Lake test data loaded
- AI services accessible (or well-defined mocks)
- Test cases authored and reviewed

Exit Criteria (to consider MVP1 ready for UAT/Release):
- All critical and major defects closed or mitigated with PO sign-off
- AI extraction accuracy ≥95% on golden dataset
- Calculation accuracy 100% on analyst-verified examples
- Performance targets met in staging for single calc and batch run
- Security review completed with no blocking issues
- Auditability and RBAC tests passed
- UAT sign-off by Supplier Programs SME and Finance Manager for approval workflow

---

## 17. Test Schedule (high-level; to be refined)

Assuming MVP1 March–June 2026:
- Month 0 (provisioning): Environments & test data (2 weeks)
- Month 1–2: Component/integration testing, AI tuning with golden set (6 weeks)
- Month 3: System testing, calculation verification against golden examples (4 weeks)
- Month 4: Performance/stress testing & security review (3 weeks)
- Month 5: UAT with SMEs and sign-off (2 weeks)
- Buffer & defect remediation (remaining time until release)

Daily/weekly status reporting during test cycles; defects triaged in weekly triage.

---

## 18. Risks & Mitigations (QA-focused)

- Risk: AI extraction falls below 95% on production agreements
  - Mitigation: Mandatory analyst confirmation; iterative AI tuning; fallbacks to manual entry UI; hold release until thresholds met for golden set
- Risk: Delta Lake data incomplete for required periods
  - Mitigation: Data completeness checks; reconciliation to GL; error/warning for missing days
- Risk: Databricks query performance insufficient for batch
  - Mitigation: Performance tuning, cluster sizing, query optimization, paging/batching
- Risk: RBAC misconfiguration leading to unauthorized approvals
  - Mitigation: Security tests, least-privilege review, verify with AD test accounts
- Risk: Sensitive data in test environments
  - Mitigation: Masking, secure key vault, restricted access

---

## 19. Reporting & Metrics

Daily/weekly metrics:
- Test case execution status (pass/fail)
- Defect counts by severity and age
- AI extraction accuracy metrics (precision/recall/F1) against golden dataset
- Calculation accuracy (number passed vs total golden examples)
- Performance metrics: avg & 95th percentile calc time, batch runtime
- Coverage: FR mapped to executed tests
- Traceability: requirements coverage

Deliverables:
- Test plan (this document)
- Test cases (in test tool)
- Test execution reports
- Defect reports and triage logs
- AI validation reports
- Performance & capacity report
- UAT sign-off documentation

---

## 20. Compliance & Auditability Tests

- Verify each calculation record contains:
  - Agreement version id
  - Blob path and checksum of agreement PDF
  - Data snapshot id/date used for calculation
  - Analyst who confirmed terms and timestamp
  - System user who ran the calculation and timestamps
- Reproducibility test: Re-run calculation using stored agreement version and snapshot id; results must match exactly
- Evidence capture: store logs and query results for audit; provide reproducibility playbook for auditors

---

## 21. Post-Release Regression & Monitoring

- Nightly regression suite to run critical smoke tests
- Nightly AI golden dataset validation; alert on degradation
- Production monitoring & alerting thresholds: failed calculations, increased latencies, AI errors, authentication failures
- Post-release bugfix window (SLA) and hotfix pipeline

---

## 22. Appendix: Example Test Case Template

- Test ID:
- Title:
- Related Requirement(s):
- Preconditions:
- Test data:
- Steps:
- Expected result:
- Actual result:
- Status:
- Notes / Attachments (logs, screenshots, exported worksheets)

---

If you want, I will:
- Populate the test management system with all test cases and link to requirements.
- Produce the golden dataset specification and a sampling plan (how many agreements of each complexity).
- Produce automation scripts templates for API and calculation tests (example Postman collection + Databricks SQL assertions).
- Produce a detailed performance test plan with Databricks cluster sizing recommendations.

Which of the above would you like me to deliver next?