# Test Plan — Supplier Rebate Claim Validation (MVP1)
Version: 1.0  
Prepared by: QA Lead  
Date: 2026-02-20 (baseline for MVP1)

## Table of Contents
- Purpose
- Scope
  - In scope (MVP1)
  - Out of scope
- Objectives and Acceptance Criteria (QA)
- Test Approach / Strategy
  - Test levels
  - Test types
  - AI-specific testing strategy
  - Data and reconciliation testing strategy
  - Test automation strategy
- Test Items (What will be tested)
- Features / Requirements Mapped to Test Types
- Test Exclusions
- Entry / Exit Criteria
- Test Environment, Tools & Test Data
- Roles & Responsibilities
- Test Deliverables & Reporting
- Traceability & Coverage
- Test Cases (high-level and selected detailed cases)
- Non-functional Testing (performance, security, availability, auditability)
- Integration & Interface Testing
- Regression Testing
- Defect Management
- Risks, Assumptions & Mitigations
- Test Schedule / Milestones
- Sign-off

---

## Purpose
Provide a complete, actionable QA/Test Plan for MVP1 (agreement upload, AI extraction, analyst confirmation, calculation using Delta Lake purchase data via Databricks SQL, claim worksheet export) that ensures functional correctness, AI extraction quality, security, performance, auditability and readiness for deployment.

---

## Scope

### In scope (MVP1)
- Agreement PDF upload and amendments
- Extraction of: supplier, period, tiers (thresholds, rates), retroactive vs incremental flag, eligible product lines and exclusions, page references using Azure Document Intelligence and Azure OpenAI
- Analyst confirmation workflow for extracted terms
- Calculation service retrieving purchase data from Delta Lake (Databricks SQL) to compute eligible spend, tier reached and earned rebate (both retroactive and incremental rules)
- Claim worksheet with supporting purchase lines, Excel export, and variance to accrual
- RBAC: Azure AD login, analyst vs finance manager vs program admin roles; approval controls (Finance Manager approves claims > USD 50,000)
- Auditability: reproducible calculations tied to agreement version and data snapshot date
- Performance expectations per Quality Attributes

### Out of scope
- MVP2 features: Supplier portal submission, dispute tracking, accrual posting, amendment comparison
- Customer (sell-side) rebates, price protection claims, supplier payment collection

---

## Objectives and Acceptance Criteria (QA)
- AI extraction: ≥95% accuracy of extracted tier terms on golden agreements (per Business requirement).
- Calculation accuracy: 100% match against analyst-verified examples for representative cases.
- Performance: Single supplier-year calculation ≤ 2 minutes; month-end batch of 400 agreements ≤ 8 hours.
- Availability: 99% during business hours.
- Security: Azure AD enforced; data access restricted by role; analyst cannot approve own claim; Finance Manager approves claims > USD 50,000.
- Auditability: Every calculation reproducible with agreement version and data snapshot date; traceable logs for AI extraction, confirmations, calculation inputs/outputs.
- Usability: Analyst confirmation UI usable within user acceptance tests (time-to-complete metric: typical agreement confirmation < 10 minutes).
- Data reconciliation: Purchase totals reconcile to GL totals within defined tolerance (to be agreed; default: 0.5% or absolute threshold).

---

## Test Approach / Strategy

High-level approach: combination of developer/unit testing, automated integration tests, system-level automated and manual tests, AI validation using a golden dataset, and structured manual exploratory testing by domain SMEs.

### Test levels
- Unit testing (developer responsibility)
- Integration testing (services, Databricks SQL, Blob, PostgreSQL, APIM, AI services)
- System / End-to-End (E2E) testing (full flow: upload → extract → confirm → calculate → worksheet/export)
- Regression testing (automated suites)
- User Acceptance Testing (UAT) with Rebate Analysts and Finance Managers (SMEs)
- Performance & Load testing (single calc & batch)
- Security & RBAC testing (auth, authorization)
- Auditability and reproducibility testing

### Test types
- Functional testing (happy paths, edge cases, negative cases)
- AI model validation (precision/recall, extraction accuracy, confidence score handling)
- Data validation & reconciliation
- Integration & API testing (APIM, Databricks SQL, Blob, Azure Postgres, Azure DI/OpenAI)
- Performance & Load testing
- Security & access control testing (Azure AD, secrets via Key Vault)
- Failure and resilience testing (timeouts, retries, partial data)
- Usability testing for analyst confirmation flows and worksheets
- Regression testing

### AI-specific testing strategy
- Golden dataset: curated set of agreements (≥200 documents recommended, with at least 50 complex/edge-case PDFs) labeled by SMEs for ground truth. Use this to measure extraction accuracy (tiers, thresholds, rates, page refs, retro/incremental, product line eligibility/exclusions).
- Confidence threshold tests: verify system handles low-confidence extractions (flags for manual confirmation).
- Error injection: create PDF variants (scanned images, atypical formatting, amendments, inline redlines) to validate robustness.
- Ground-truth-driven unit tests for extraction pipeline; per-field metrics tracked across releases.
- Human-in-loop confirmation: test that until confirmation, terms are not used in calculations.

### Data & reconciliation testing strategy
- Use known snapshot datasets of Delta Lake purchase data with reconciled GL totals.
- Test data should include: complete spend, missing lines, product line mapping mismatches, excluded SKUs, retrospective transactions (back-dated), and multi-currency (if applicable).
- Reconciliation tests to compare calculated eligible spend to GL totals for sample suppliers and periods.

### Automation strategy
- Automate integration tests (APIs, DB) via CI (GitHub Actions).
- Automate end-to-end happy path and regression tests where possible (Selenium/Playwright for UI; Postman/RestAssured for APIs).
- Automate AI extraction validation by running pipeline on golden dataset and measuring field-level accuracy.
- Performance tests automated using JMeter/k6 targeting calculation service and batch scheduler.
- Manual testing for exploratory, UI usability, and SME validations.

---

## Test Items (system components to be tested)
- Web UI (upload, review/confirm, run calculation, view worksheet, exports)
- Agreement Service (upload, store to Blob, call APIM → Azure DI/OpenAI, store confirmed terms in PostgreSQL)
- Calculation Service (Databricks SQL connector, calculation engine, stored results to PostgreSQL)
- Batch Scheduler (Azure Function) — month-end batch review (non-production)
- APIM integrations to Azure Document Intelligence & Azure OpenAI
- Data stores: Blob Storage (agreement files), Azure PostgreSQL (terms, results), Delta Lake (EUDM) via Databricks SQL
- Authentication/Authorization via Azure AD
- Monitoring & logging (Datadog, Azure Monitor), secrets (Key Vault)
- Excel export and supporting purchase lines in worksheet
- Audit logging and reproducibility features (agreement version, snapshot date)

---

## Features / Requirements Mapped to Test Types (high-level matrix)
- Upload PDFs → Functional, Integration, Negative (invalid files), Security (RBAC), Performance (large PDFs)
- Extract tiers/rates/page refs → AI validation (golden dataset), Functional (correct mapping), UI (display page refs)
- Confirm terms → Functional, Usability, RBAC (analyst cannot bypass)
- Use confirmed terms in calculations → Integration, System, Auditability
- Calculation (retroactive vs incremental) → Functional (calculation correctness), Data validation (edge cases), Performance
- Eligible product lines & exclusions → Functional, Data mapping, Integration (product line mapping)
- Claim worksheet & Excel export → Functional, Usability, Data completeness
- Variance to accrual → Functional, Data reconciliation
- Reproducible calculation with agreement version & snapshot → Auditability tests, Data integrity
- RBAC & approvals (Finance Manager > $50k) → Security, Functional (approval workflow), Negative tests (analyst approve own)
- API integrations → Integration and contract testing with APIM, Databricks, AI services

---

## Test Exclusions
- Supplier portal submission, dispute tracking, accrual posting, amendment comparison (MVP2)
- End-to-end financial posting into general ledger (out of scope for MVP1)

---

## Entry / Exit Criteria

### Entry criteria (to begin system/E2E testing)
- All unit and component tests pass.
- Development feature-complete for MVP1 features and deployed to test environment.
- Test environment ready and connected to test instances of Blob, PostgreSQL, Databricks SQL (or mocks/stubs if live not available), APIM, and AI services (or reliable sandbox/mocks).
- Golden dataset for AI extraction prepared and SME-verified.
- Test data snapshots available for Delta Lake representing at least 24 months.
- Test accounts and RBAC roles created in Azure AD test tenant.
- Monitoring & logging configured.

### Exit criteria (for release candidate)
- All critical and high defects resolved and verified; medium defects evaluated by product owner and mitigated or deferred with plan.
- Acceptance criteria met:
  - AI extraction accuracy ≥95% on golden dataset
  - Calculation accuracy validated against 100% of analyst-verified examples
  - Performance targets met (single calc ≤2 minutes; batch ≤8 hours for 400)
  - Auditability checks passed (reproducibility verified)
- UAT signed off by Supplier Programs SMEs and Finance representative for MVP1 scope.
- Regression suite executed and passing on release candidate.
- Security scan and basic penetration tests passed (no critical issues).
- Release notes and known issues documented.

---

## Test Environment, Tools & Test Data

### Environments
- Dev (unit tests, developer)
- Test / Integration (connected to test/sandbox versions of services)
- Performance (isolated environment for load tests)
- UAT (representative environment with SMEs)
- Non-production architecture mirrors production networking and auth boundaries (per architecture diagram)

### Tools
- Test management: Azure DevOps Test Plans or equivalent (Jira + Xray)
- Automation: Playwright/Selenium (UI), Postman / Newman / RestAssured (API), PyTest/JUnit (integration)
- CI: GitHub Actions
- Load: k6 or JMeter
- AI validation tooling: custom scripts (Python) to evaluate extraction outputs vs golden labels (compute precision/recall/field accuracy)
- Monitoring: Datadog, Azure Monitor
- Secrets: Key Vault
- Databricks test workspace / SQL endpoints (or mocked SQL)
- Database migration / test data provisioning: scripts with checkpoints to restore snapshots
- Excel validation: automated verification scripts using openpyxl / Apache POI

### Test Data
- Golden agreement set (≥200 PDFs) with labels for:
  - tiers (threshold, rate), retro vs incremental, period, eligible product lines/exclusions, page references
  - edge-cases: ambiguous language, scanned PDFs, amendments, redlines, multiple tiers, varying currencies
- Purchase datasets:
  - Small: single supplier-year with simple tier crossing
  - Medium: supplier with multiple product lines, exclusions
  - Complex: supplier with retroactive adjustments, backdated POs, missing mapping items
  - Month-end batch: 400 supplier datasets for batch run
- Product line mapping configurations, including intentional mismatches
- Accrual benchmark data (for variance comparison)
- Test users for roles: Rebate Analyst, Finance Manager, Program Admin (Azure AD test tenant)

---

## Roles & Responsibilities
- QA Lead (you): test plan, coordinate tests, track coverage, reporting, sign-off readiness
- QA Engineers: design & execute tests, automate suites, performance testing
- Developers: unit tests, fix defects, provide test hooks, stub/mocks if required
- Data Platform/Databricks team: provide test SQL endpoints and snapshots, assist with performance tests
- Supplier Programs SMEs / Rebate Analysts: validate AI outputs (golden dataset), UAT
- Finance Manager SME: approve UAT scenarios involving approvals > $50k
- Security team: run security scans/penetration tests
- DevOps: environment provisioning, CI/CD pipelines
- Product Owner: accept UAT results and sign-off

---

## Test Deliverables & Reporting
- Test Plan (this document)
- Test Cases & Test Suites (functional, integration, regression, AI validation)
- Test Data Inventory & Golden Dataset
- Test Execution Reports (daily during cycles)
- Defect Reports (tracked in Jira/Azure DevOps)
- Performance Test Reports (latency, throughput, resource usage)
- AI Extraction Validation Report (field-level accuracy, confidence distributions)
- Security Test Report
- UAT Sign-off document
- Final Test Summary & Release Recommendation

---

## Traceability & Coverage
- Each functional requirement, user story and acceptance criterion will be traced to at least one test case. Traceability matrix will be maintained (Requirement ID → Test Case IDs → Test Results).
- AI extraction acceptance criteria mapped to golden dataset tests.
- Calculation accuracy acceptance criteria mapped to deterministic test cases with SME-verified expected outputs.

---

## Test Cases (high-level list and selected detailed cases)
Note: Full detailed test cases will be maintained in the test management tool.

High-priority test cases (representative):

1. TC-FUNC-001: Upload valid agreement PDF (happy path)
   - Steps: Login as Rebate Analyst → Upload PDF → Verify stored in Blob → UI shows file and metadata
   - Expected: Upload success, file accessible, initial processing triggered

2. TC-FUNC-002: AI extraction happy path (simple agreement)
   - Steps: Upload golden agreement → Wait for extraction → Verify extracted supplier, period, tiers, rates, page refs
   - Expected: Fields correctly populated; confidence scores shown; no missing mandatory fields

3. TC-AI-003: AI extraction accuracy (golden dataset)
   - Steps: Run extraction across golden dataset → Compare fields to ground truth
   - Expected: Field-level accuracy ≥95% for tiers; overall acceptance criteria met

4. TC-FUNC-004: Low-confidence extraction flagged for manual confirmation
   - Steps: Upload intentionally ambiguous agreement → Extraction yields low confidence → UI shows caution and requires confirmation
   - Expected: System requires analyst confirmation; cannot proceed to calculation until confirmed

5. TC-FUNC-005: Analyst confirmation enforces terms usage
   - Steps: Extract terms but do not confirm → Attempt run calculation
   - Expected: Calculation blocked with message that terms are not yet confirmed

6. TC-FUNC-006: Calculation - retroactive tier example
   - Data: Supplier with retroactive rule: 2% from $1M, 3% from $2M; spend $1.5M
   - Steps: Confirm terms, run calculation
   - Expected: Earned rebate = full spend × applicable rate (apply definition: retroactive applies highest rate to full spend?) — (Exact business rule: retroactive applies rate to full spend; test asserts expected per SME-calculated formula). Verify supporting purchase lines included and tier reached displayed correctly.

7. TC-FUNC-007: Calculation - incremental tier example
   - Data: Incremental tiers defined; spend crossing multiple bands
   - Steps: Confirm terms, run calculation
   - Expected: Earned rebate equals sum of each band × respective rate; verify per-line supporting detail

8. TC-FUNC-008: Eligible product line filtering
   - Data: Purchase dataset includes eligible and non-eligible SKUs
   - Steps: Run calculation
   - Expected: Only eligible product lines included; exclusions removed; supporting lines indicate exclusion reason

9. TC-FUNC-009: Variance to accrual calculation
   - Steps: Run calculation where accrual exists → Verify variance computed correctly and shown on worksheet
   - Expected: Variance equals (calculated rebate - accrual), signed and displayed correctly

10. TC-FUNC-010: Excel export content & format
    - Steps: Generate claim worksheet → Export to Excel → Validate file contains expected rows, columns, totals and formatting
    - Expected: Excel file downloadable, correct content, supporting purchase lines included

11. TC-Security-001: RBAC - approval > $50,000 must be Finance Manager
    - Steps: Create claim > $50k → Attempt approve as Rebate Analyst → Attempt approve as Finance Manager
    - Expected: Analyst cannot approve (UI/403); Finance Manager can approve

12. TC-Security-002: Analyst cannot approve own claim
    - Steps: Analyst uploads agreement, runs calc → Attempt to approve claim as same analyst even if Role elevated
    - Expected: Denied; process enforces separation of duties

13. TC-Perf-001: Single supplier-year calculation time <= 2 minutes
    - Steps: Run calculation for a representative supplier-year with expected dataset
    - Expected: Elapsed time under 120 seconds; resource metrics collected

14. TC-Perf-002: Month-end batch 400 supplier run <= 8 hours
    - Steps: Trigger batch scheduler in performance environment with 400 supplier datasets
    - Expected: Completed within 8 hours; monitor failures and resource usage

15. TC-Audit-001: Reproducible calculation
    - Steps: Run calculation with agreement version V1 and data snapshot date D1 → Save results. Re-run using same agreement version and snapshot → Compare outputs and logs
    - Expected: Identical results; timestamped audit trail present

16. TC-Integration-001: Databricks SQL connectivity & query correctness
    - Steps: Calculation service calls Databricks SQL with expected query → Verify results returned & used
    - Expected: Secure connection via OAuth, correct results; timeouts and retry logic tested

17. TC-Failure-001: Partial data on Delta Lake (missing days)
    - Steps: Provide dataset with missing purchase rows → Run calculation
    - Expected: System logs data gaps, flags reconciliation warning, does not silently produce incorrect totals

Detailed templates for each of the above will include preconditions, data, exact steps, expected results, pass/fail criteria and evidence artifacts (screenshots, logs, exported files).

---

## Non-functional Testing

### Performance & Load
- Single calculation: ≤ 2 minutes. Validate with 95th percentile and median.
- Batch calculation (400 agreements): ≤ 8 hours. Validate resource consumption, scaling behavior, and recovery from transient failures.
- Stress tests: push concurrent calculation runs (N users) to measure system behavior and determine breaking point.

### Security & Access Control
- Azure AD authentication verification for all entry points.
- Authorization checks for each endpoint and UI action.
- Secrets management (Key Vault) verified: no secrets in logs.
- Data-at-rest (Blob and PostgreSQL) and data-in-transit verification (HTTPS/TLS).
- Penetration testing for high/critical issues (scoped for MVP1 common endpoints).
- SOX/C2P considerations: logging, segregation of duties tests.

### Availability & Resilience
- Failover tests for transient AI service downtime: system should surface errors and queue extractions for retry; analyst can re-run extraction.
- Blob/Postgres unavailability tests: graceful degradation and detailed error messages.

### Auditability & Reproducibility
- Log provenance: store agreement version, extraction output, confirmed terms, data snapshot date, SQL query, and calculation input dataset reference.
- Re-run tests to validate identical outputs for same inputs.

---

## Integration & Interface Testing
- APIM → Azure Document Intelligence & OpenAI: contract tests, response schema validation, error handling, throttling handling.
- Calculation Service → Databricks SQL: test secure OAuth flow, SQL correctness, pagination/limits.
- Agreement Service → Blob/Postgres: test storage/retrieval, versions, and transactionality on confirm.
- Web UI → Services: test end-to-end flows, session handling, timeouts.
- Monitoring integration: ensure events logged to Datadog/Azure Monitor.

---

## Regression Testing
- All functional flows (upload/extract/confirm/calc/export) will be included in automated regression suites.
- AI extraction regression: re-run golden dataset check when models or prompts are changed.
- Regression suite runs in CI for each release candidate.

---

## Defect Management
- Tool: Jira/Azure DevOps
- Severity definitions: Critical (blocker/production-impacting), High (major functionality broken), Medium (partial feature), Low (UI/typos)
- SLA: Critical defects fixed within 48 hours (configurable by PO); High fixed in next sprint; others triaged.
- Root cause analysis for critical/high defects; test case updates to prevent regressions.

---

## Risks, Assumptions & Mitigation

Risks:
- AI extraction falls below 95% accuracy on live agreements (complex language)
  - Mitigation: Expand golden dataset, refine prompts, fallback manual extraction UI, mandatory confirmation.
- Databricks access/performance limited
  - Mitigation: Work closely with data platform team; caching; query optimization; staged performance tests
- Test data fidelity (Delta Lake snapshots incomplete)
  - Mitigation: Use synthetic augmented datasets; reconciliation checks to flag gaps
- RBAC misconfiguration
  - Mitigation: Dedicated security tests; run principle of least privilege checks
- Long batch runtime on full dataset
  - Mitigation: Parallelization, job throttling, compute scaling in Databricks

Assumptions:
- Delta Lake purchase data complete for last 24 months (per BRD)
- Agreements are mostly digital PDFs (not handwritten)
- Test environment can access AI services (or reliable sandbox/mocks)

---

## Test Schedule / Milestones (MVP1 aligned with Mar–Jun 2026)
- Week 0–2: Test plan approval, environment preparation, golden dataset collection & labeling
- Week 3–6: Integration tests; API contract tests; initial AI validation (first pass)
- Week 7–10: System/E2E tests; functional test completion
- Week 11–12: Performance testing (single calc & batch); security scan
- Week 13: UAT with Rebate Analysts & Finance Manager SMEs
- Week 14: Regression & final validation; prepare release candidate
- Week 15: Sign-off & release to targeted non-production or pilot

(Adjust per actual sprint cadence and release dates; detailed schedule to be maintained in test tool.)

---

## Sign-off Criteria & Approval
- QA provides release recommendation when exit criteria are met.
- Sign-off required from:
  - Supplier Programs (Product Owner)
  - Finance representative (for approval workflows)
  - Security/Compliance (for data & AI governance)
  - QA Lead

---

## Appendix: Key Test Scenarios and Example Data Patterns

- Scenario A: Perfectly-structured digital PDF, single-tier retroactive → Expect extraction correct; calculation straightforward.
- Scenario B: Multi-tier incremental with multiple product lines and exclusions → Confirm incremental math and correct filtering.
- Scenario C: Scanned image PDF (OCR required) → Validate extraction confidence; ensure analyst sees page refs for verification.
- Scenario D: Amendment uploaded after initial agreement (MVP1 supports amendments upload) → Confirm extraction of changed terms and versioning for auditability.
- Scenario E: Data gap in Delta Lake for portion of period → System flags and outputs reconciliation warning; analyst notified.
- Scenario F: Edge-case language “2% from $1M on incremental basis” ambiguous phrasing → AI extraction produces low-confidence or ambiguous flag; analyst confirmation required.

---

If you want, I will:
- Produce the full set of detailed test cases in the test management format (preconditions, steps, expected results, data) for import into Azure DevOps or Jira.
- Prepare the golden dataset labeling template (CSV schema) and an automated AI evaluation script (Python) for field-level accuracy reports.
- Draft UAT scripts for Rebate Analysts / Finance Managers.

Which of the above would you like me to prepare next?