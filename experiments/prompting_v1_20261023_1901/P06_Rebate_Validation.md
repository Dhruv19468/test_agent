# Test Plan — Supplier Rebate Claim Validation (MVP1)

Version: 1.0  
Prepared by: QA Lead  
Date: 2026-02-20 (aligned to BRS v1.0 17 Feb 2026)

Contents
1. Introduction & Objectives
2. Scope (In / Out)
3. Test Approach & Strategy
4. Test Items / Features to be Tested
5. Test Types & Coverage
6. Test Environment, Data & Tools
7. Roles & Responsibilities
8. Test Schedule & Milestones
9. Entry / Exit Criteria
10. Acceptance Criteria Mapping
11. Test Cases (representative list)
12. Test Data & Golden Dataset
13. Automation Strategy & Regression
14. Performance, Scalability & Load Testing
15. Security, Privacy & Compliance Testing
16. Integration & End-to-end Test Strategy
17. Non-functional Tests (availability, auditability)
18. Defect Management & Reporting
19. Risk, Assumptions & Mitigations
20. Test Deliverables
21. Traceability Matrix (summary)
22. Approval

---

# 1. Introduction & Objectives
Purpose: Define QA approach and detailed test planning for MVP1 of Supplier Rebate Claim Validation: upload of rebate agreement PDFs, AI extraction of terms, analyst confirmation, calculation of rebates using Delta Lake purchase data and Databricks SQL, and claim worksheet generation.

Primary QA Objectives:
- Validate functional correctness of extraction, confirmation, calculation and worksheet generation.
- Achieve acceptance criteria: ≥95% accuracy on extracted tier terms (golden dataset) and 100% calculation accuracy against verified examples.
- Validate performance targets: single supplier-year calculation <= 2 minutes; month-end batch of 400 agreements <= 8 hours (MVP1 scope target).
- Validate security, auditability, RBAC and data reconciliation requirements.

# 2. Scope
In scope (MVP1):
- Upload of agreement PDFs/amendments
- Azure Document Intelligence & Azure OpenAI-based extraction of: supplier, period, tiers (thresholds, rates), retroactive vs incremental flag, eligible product lines & exclusions, page references
- Analyst review/confirmation of extracted terms (confirmed terms used by calculation)
- Calculation using Delta Lake (Databricks SQL): eligible spend, tier reached, earned rebate (retroactive vs incremental), supporting purchase lines
- Claim worksheet export to Excel and variance to accrual
- Auditability: agreement version and data snapshot usage logged

Out of scope:
- Supplier portal submission, dispute tracking, accrual posting, amendment comparison (MVP2)

# 3. Test Approach & Strategy
- Layered testing: Unit (service-level by dev), Component, Integration, System, UAT.
- Hybrid test approaches:
  - Automated API and calculation tests (Databricks SQL queries validation).
  - Automated UI tests for primary analyst workflows (upload, confirm, run calc, export).
  - Manual exploratory tests for complex PDFs and edge-case language.
  - AI testing: two tracks
    - Deterministic validation against golden dataset (for acceptance).
    - Live-model smoke and robustness tests using representative PDF corpus and adversarial variants.
  - Performance tests for single-run and bulk batch scenarios using synthetic and production-like data.
  - Security testing: RBAC, data access, injection, OWASP top 10 web testing.
  - Audit and reproducibility testing: reproduce calculation from stored agreement version and snapshot date.
- Use test doubles (stubs/mocks) for Azure Document Intelligence and OpenAI during most functional tests to guarantee deterministic behavior; run a dedicated set of tests against live AI services to measure extraction accuracy.

Risk-driven priorities:
- Prioritize tests validating calculation correctness and analyst-confirmation gating (critical for business correctness).
- Emphasize AI extraction accuracy and fallbacks when uncertain (page reference tagging).

# 4. Test Items / Features to be Tested
- Authentication & Authorization (Azure AD integration, RBAC: Rebate Analyst, Finance Manager, Program Admin)
- File upload (single PDF, multiple pages, amendments)
- AI extraction pipeline: Document Intelligence -> OpenAI term parsing -> stored extracted terms with page references and confidence scores
- Terms review UI: edit, confirm, reject, versioning and audit log
- Databricks SQL integration (Delta Lake): data retrieval by product line mapping, date ranges, supplier mapping
- Calculation Service: retroactive vs incremental calculation logic, tier logic, rounding, currency handling, period boundaries
- Claim worksheet generation & Excel export: line-level supporting purchases, totals, tier reached, earned rebate, variance to accrual
- Batch processing (month-end): scheduler invocation, processing 400 agreements
- Logging and audit trails (agreement version, snapshot date, extraction confidence, calculation parameters)
- Error & exception handling: missing mapping, ambiguous extraction, connectivity failures
- Performance, availability, security, and backup/retry behaviors

# 5. Test Types & Coverage
- Functional Testing: All functional requirements (100% coverage of MVP1 functional requirements).
- Integration Testing: Interfaces to Azure Blob Storage, Azure PostgreSQL, Databricks SQL (Delta Lake), APIM, Azure Document Intelligence & Azure OpenAI (stubs and live).
- System Testing: End-to-end flows including UI and batch scheduler.
- Regression Testing: Full regression for release candidate.
- Acceptance Testing / UAT: Business user (Rebate Analysts / Finance Manager) validation of workflows and claim worksheet content.
- Performance & Load Testing: single supplier-year response, 400-agreement batch.
- Security Testing: Authentication, authorization, data access, secrets handling (Key Vault), vulnerabilities.
- AI Model Validation: Accuracy & confidence thresholds versus golden dataset.
- Data Quality & Reconciliation Testing: reconciliation to GL totals and EUDM snapshots.
- Failover & Resilience Testing: service outages, retries, partial failures.
- Accessibility & Usability: basic checks for analyst UI (optional but recommended).
- Auditability Testing: reproduction of runs from stored agreement version and data snapshot.

# 6. Test Environment, Data & Tools
Environments:
- Dev: unit tests and developer integration
- QA/Test: feature-complete environment with stubs/mocks for external systems
- Pre-Prod / Staging: production-like connectivity to Databricks SQL (read-only), Azure Blob, PostgreSQL; limited live AI calls for extraction validation
- Production: not used for testing except runbooks and smoke after deployment

Infrastructure / Dependencies:
- Azure AD (test tenant or dev tenant)
- App Gateway, Web UI, Agreement Service, Calculation Service deployed into non-prod subscription
- Blob Storage for agreements (test containers)
- Azure PostgreSQL test DB
- Databricks SQL read access to a test copy of Delta Lake EUDM (snapshot)
- APIM fronting AI services
- Azure Document Intelligence & Azure OpenAI (stubs in QA; live in Staging)
- Supporting: Key Vault, Datadog, GitHub Actions, Azure Monitor

Test Tools:
- Test management: Azure DevOps Test Plans / TestRail / Jira
- API testing: Postman, RestAssured, pytest + requests
- UI automation: Playwright or Selenium WebDriver (prefer Playwright)
- DB/SQL tests: Databricks SQL connector, pytest
- Load/Perf: JMeter / k6 / Azure Load Testing
- Security: Burp Suite, Snyk scans, static scans already in pipeline
- Data creation / ETL test utilities: Python scripts, Databricks notebooks
- CI: GitHub Actions integration for automated test runs
- Logging & monitoring: Datadog + Azure Monitor

# 7. Roles & Responsibilities
- QA Lead (owner): test planning, coordination, reporting
- QA Engineers: write and execute test cases, automation scripts, regression pack
- Automation Engineer: maintain automation framework and pipeline
- Performance Engineer: design and run load tests, analyze
- Security Engineer: run security and penetration tests
- Dev Engineers: fix defects, provide unit tests, support environment setup
- Program SMEs (Supplier Programs): provide golden dataset and sign-off for UAT
- Finance SME: validate accrual variance logic and approval thresholds
- DevOps: manage environments, access to Databricks and Azure services

# 8. Test Schedule & Milestones (MVP1 — Mar–Jun 2026)
- Test Planning & Setup: Week 1–2
- Environment Provisioning & Data Load: Week 2–4
- Test Case Development & Automation Scripting: Week 3–6
- Component & Integration Testing: Week 6–9
- System Testing & AI Golden Dataset Validation: Week 9–12
- Performance & Batch Testing: Week 11–13
- UAT with Business Users: Week 13–14
- Regression & Hardening: Week 14–15
- Release Candidate & Sign-off: Week 15–16

(Adjust dates to project cadence; exact timeline to be finalized with project manager.)

# 9. Entry / Exit Criteria
Entry criteria for System Test:
- Development unit tests passed and merged
- Builds deployed to QA environment
- Test environment configuration complete (DB, Blob, Databricks test snapshot)
- Golden dataset & representative PDF corpus available

Exit criteria for System Test:
- All critical & high defects resolved or mitigated
- ≥95% of planned system tests executed; pass rate >= 95% critical scenarios, >= 85% overall
- Performance goals met for baseline tests (single supplier-year <= 2min)
- AI extraction accuracy on golden dataset meets >=95% (staging run)
- Regression pack executed for release candidate with no critical failures

UAT entry:
- System Test exit criteria met
- Business users scheduled and available

UAT exit / Release sign-off:
- Business sign-off for acceptance criteria
- Known lower-severity defects logged with mitigations
- Security & compliance sign-offs (AI Governance Council when required)

# 10. Acceptance Criteria Mapping
- Acceptance: ≥95% extraction accuracy of tier terms on golden agreements -> AI Model Validation tests (golden dataset).
- Acceptance: 100% calculation accuracy against analyst-verified examples -> Calculation regression suite comparing outputs to oracle.
- Auditability: Every calculation reproducible with agreement version and data snapshot date -> Auditability tests reproduce runs and compare outputs byte-for-byte.
- RBAC: Finance Manager approval enforced for claims > USD 50,000; Analysts cannot approve own claims -> RBAC test cases.
- Performance: single supplier-year <= 2 minutes; month-end batch of 400 agreements <= 8 hours -> Performance test runs.

# 11. Representative Test Cases (IDs, brief)
Note: These are representative — full test case catalog will expand per requirement.

Functional / Happy Path
- TC-F-001: Upload a well-formed agreement PDF -> extraction produces supplier, period, tiers, product lines, page references -> items displayed in UI with confidence scores.
- TC-F-002: Analyst edits an extracted tier (threshold and rate) and confirms -> confirmed terms persisted in PostgreSQL with versioning and audit trail.
- TC-F-003: Run calculation for a confirmed agreement for single period -> calculation service queries Delta Lake and returns eligible spend, tier reached, earned rebate (retroactive) -> worksheet generated with supporting lines and exportable to Excel.
- TC-F-004: Incremental tier calculation -> verify per-tier incremental calculation, rounding and totals match analyst oracle.
- TC-F-005: Claim worksheet includes variance to accrual and link to purchase lines.

Negative & Edge Cases
- TC-N-001: Upload ambiguous/complex PDF (merged amendments, two-tier tables) -> system flags low confidence on certain terms and requires analyst confirmation (cannot auto-confirm).
- TC-N-002: Missing product line mapping for one supplier line -> calculation logs mapping error, shows unmapped spend and prompts admin; calculation proceeds only for mapped spend.
- TC-N-003: Delta Lake connectivity interruption during calculation -> calculation fails gracefully with retry; partial results not persisted; error reported to analyst.

AI / Extraction Tests
- TC-AI-001: Golden dataset extraction run -> per-agreement extraction accuracy >=95% for tiers and rates; page references correct
- TC-AI-002: Confidence threshold behavior -> documents with confidence < threshold are shown as unconfirmed and cannot be used for calculation without analyst confirmation

Integration & Data
- TC-I-001: Databricks SQL query returns expected set of purchase lines by product line mapping for sample supplier-year; totals reconcile to GL snapshot within tolerance.
- TC-I-002: Agreement file saved to Blob Storage and version reference stored in PostgreSQL; deletion attempts protected by RBAC

RBAC & Approval Flow
- TC-R-001: Analyst attempts to approve a claim > USD 50,000 -> UI blocks action; approval required by Finance Manager.
- TC-R-002: Finance Manager approves claim; log entry created; status changes to Approved.

Batch & Performance
- TC-P-001: Single supplier-year calculation completes within 2 minutes (typical dataset).
- TC-P-002: Month-end batch of 400 agreements completes within 8 hours in staging with simulated production data snapshot.
- TC-P-003: Concurrency test: several analysts running calculations concurrently (10–20) without performance degradation beyond SLAs.

Auditability & Repro
- TC-AUD-001: Reproduce a calculation run by selecting agreement version and snapshot date -> results identical to original exported worksheet (byte-for-byte or value-equal).

Security & Compliance
- TC-S-001: Access attempts with unauthorized user fail (Azure AD integration, role enforcement).
- TC-S-002: Secrets are not exposed in logs; Key Vault access is used.

Error Handling
- TC-E-001: If OpenAI or Document Intelligence returns 5xx, system shows meaningful error to analyst and falls back to manual upload confirmation workflow.

Regression
- TC-RG-001: Full regression pack covering critical flows executed for release candidate.

(Each TC will be captured in the test management tool with preconditions, detailed steps, test data, expected results, and pass/fail criteria.)

# 12. Test Data & Golden Dataset
Test Data Types:
- Golden agreements: at least 100 annotated PDFs covering common and edge-case contract language (simple tier, multiple tier tables, retroactive vs incremental, amendments, exclusions). Provided by Supplier Programs SMEs.
- Representative PDF corpus: 400+ agreements for batch performance tests (synthetic/obfuscated to protect PII and supplier confidentiality).
- Delta Lake snapshots: test copy of purchase data for the past 24 months containing PO lines, product line mappings, GL totals for reconciliation.
- Product line mapping configurations (including unmapped edge cases).
- Accrual values for variance calculation (seeded in PostgreSQL or CSV).

Golden Dataset Requirements:
- Each golden PDF must be accompanied by ground-truth extraction (supplier, period, tiers with thresholds & rates, retro vs incremental flag, eligible product lines, page references).
- Ground-truth stored in a canonical format (JSON) for automated comparison.

Data Handling:
- Use obfuscated or synthetic real-like data where required for privacy.
- Ensure test environment access controls mimic production RBAC.

# 13. Automation Strategy & Regression
Automation Goals:
- Automate API-level tests for Agreement Service, Calculation Service, DB checks.
- Automate calculation verification by running calculation and comparing to an oracle dataset (100% deterministic tests).
- Automate UI smoke tests for upload -> confirm -> run calc -> export.
- Continuous execution of regression pack in CI pipeline on each release.

Coverage Targets:
- Automate ~70–80% of functional tests (critical flows) by release.
- Maintain manual exploratory tests for AI ambiguous extractions.

Test Automation Framework:
- Use Playwright for UI automation (fast, parallel), pytest for API and SQL validation, and GitHub Actions for CI orchestration.
- Store test artifacts (screenshots, logs, exported worksheets) in CI artifact storage and Datadog for monitoring.

Regression Pack:
- Core calculation correctness cases
- RBAC & approval flows
- Extraction golden dataset checks (staged)
- Key integration endpoints health checks

# 14. Performance, Scalability & Load Testing
Performance Objectives:
- Single supplier-year calculation <= 2 minutes (median and P95 targets)
- Month-end batch of 400 agreements <= 8 hours
- System availability 99% during business hours

Perf Test Plan:
- Baseline single-run performance with typical dataset (size based on supplier spend and purchase lines).
- Scale tests: increase line count, product lines, and number of concurrent runs.
- Batch run performance: simulate scheduler running 400 agreements sequentially / in parallel as per architecture; measure throughput and resource consumption.
- Test Databricks SQL response time and pagination for large result sets.
- Stress tests to characterize breaking points and graceful degradation.
- Observe CPU, memory, DB connections, Databricks warehouse concurrency limits.

Acceptance Thresholds:
- Single-run P95 < 2 minutes
- Batch 400-run wall-clock < 8 hours (with logs of per-agreement times)
- No data loss or truncation during batch

# 15. Security, Privacy & Compliance Testing
Security Tests:
- Azure AD authentication / SSO test coverage
- RBAC enforcement: roles and approval gating
- OWASP top 10 web application tests (SQLi, XSS, CSRF, auth flaws)
- Secrets management verification (Key Vault usage; no secrets in logs)
- API rate-limiting tests and abuse scenarios
- Penetration testing (staging) coordinated with security team

AI-Specific Governance Tests:
- Ensure extraction logs include model version, confidence, and request/response metadata per AI Governance Council requirements.
- Validate sensitive data handling: no leakage of PII in prompts or logs.

SOX / Compliance:
- Validate audit trails for agreement upload, confirmation, calculation run, approvals (who, when, what changed)
- Ensure separation of duties (analysts cannot approve their own claims) implemented and tested

# 16. Integration & End-to-end Test Strategy
- Use integration tests that exercise: Web UI -> Agreement Service -> APIM -> Document Intelligence/OpenAI (stubs/live) -> PostgreSQL -> Calculation Service -> Databricks SQL -> Delta Lake -> results back to Web UI -> Excel export.
- Stubbing strategy:
  - QA: stub AI services with deterministic responses for agreed test cases.
  - Staging: run subset of tests with live AI services for accuracy measurement.
- Databricks integration: use read-only test snapshots; verify SQL queries return expected data and are resilient to schema changes.
- Monitoring of end-to-end latency and error rates.

# 17. Non-functional Tests (Availability, Auditability)
Availability:
- Simulate component failure (e.g., Blob Storage throttling, Databricks interruptions) and verify graceful degradation and retry behavior.
Auditability:
- Run tests to reproduce calculations from stored agreement version and data snapshot date; verify same outputs.
- Check audit logs for correct metadata: user ID, timestamp, agreement version ID, data snapshot timestamp, model version and confidence.

# 18. Defect Management & Reporting
- Issue tracker: Jira (or Azure DevOps Boards). Defect fields include severity, priority, environment, steps to reproduce, logs and attachments.
- Severity Levels:
  - Sev1 (Critical): Calculation incorrect for multiple agreements, data loss, security critical.
  - Sev2 (High): Major functionality broken, e.g., extraction consistently wrong for many agreements, batch cannot complete.
  - Sev3 (Medium): Partial functionality or UI issues affecting productivity.
  - Sev4 (Low): Cosmetic or minor issues.
- Triage cadence: Daily for Sev1/2, every 48 hours for Sev3.
- Reporting: Weekly QA status report with test coverage, defect trends, open critical defects, and readiness.

# 19. Risks, Assumptions & Mitigations
Risks:
- AI extraction fails to meet 95% accuracy -> mitigation: mandatory analyst confirmation and human review workflows, add more training examples and parse rules.
- Delta Lake data gaps -> mitigation: reconciliation checks, fallback to recent snapshot or manual data entry, log unmapped spend.
- Databricks concurrency limits impacting batch performance -> mitigation: schedule batches, optimize SQL, coordinate with Data Platform team.
- Dependencies unavailable during test windows -> mitigation: mock services and parallelize test cases independent of missing components.

Assumptions:
- Delta Lake purchase data is complete for last 24 months (as per BRS).
- Agreements primarily digital PDFs; golden dataset will be provided by Supplier Programs SMEs.
- Databricks SQL access will be provided to QA environment.

# 20. Test Deliverables
- Test Plan (this document)
- Test Cases & Execution Records (TestRail / Azure DevOps)
- Automation Scripts & CI pipelines
- Test Data & Golden Dataset (secure location)
- Test Execution Reports (daily/weekly)
- Defect Reports and Triage Notes
- Performance Test Report (including resource usage)
- Security Assessment Report & remediation logs
- UAT Sign-off Document and Acceptance evidence
- Release Test Summary and Go/No-go recommendation

# 21. Traceability Matrix (summary)
Map each main requirement to test type(s) and representative test cases:

- Upload agreement PDFs -> Functional/UI TC-F-001, Integration TC-I-001
- AI extraction of tiers & page refs -> AI TC-AI-001, TC-F-001
- Analyst confirmation gating -> TC-F-002, RBAC TC-R-001
- Delta Lake calculation logic retroactive/incremental -> TC-F-003, TC-F-004, Calculation regression suite
- Export worksheet & variance to accrual -> TC-F-005
- Auditability & reproducible runs -> TC-AUD-001
- Performance targets -> TC-P-001, TC-P-002
- Security & RBAC -> TC-S-001, TC-R-001

(Full traceability matrix maintained in test management tool.)

# 22. Approval
Signatures / Approvals required:
- QA Lead
- Product Owner / Business Owner (Supplier Programs Finance)
- Finance Manager representative
- Program Admin or Product Ops
- Security / Compliance lead (AI Governance Council representative)

---

Appendix A — Sample Detailed Test Case (example)

TC-F-003 (Detailed)
- Title: Single-period calculation (retroactive) for confirmed agreement
- Preconditions:
  - Agreement PDF uploaded and terms confirmed (retroactive flag = true)
  - Delta Lake snapshot loaded for supplier with purchase lines for the period
  - Product line mappings exist for supplier lines
- Steps:
  1. As Rebate Analyst, select supplier and period and click "Run Calculation"
  2. Service fetches confirmed terms and issues Databricks SQL to retrieve eligible purchase lines
  3. Calculation Service applies retroactive rate to total eligible spend and produces earned rebate value
  4. UI displays tier reached, eligible spend, earned rebate and supporting purchase lines
  5. Export worksheet to Excel and validate content
- Expected Results:
  - Calculation completes within SLA (single-run <= 2 min)
  - Earned rebate equals oracle amount (exact match)
  - Excel contains all supporting purchase lines and variance to accrual
  - Run metadata saved (agreement version, snapshot date)

Appendix B — AI Testing Notes
- Use two-mode testing:
  - Deterministic mode: stub AI responses to match ground truth for functional automation.
  - Live mode: run extraction across golden dataset and compute per-field precision/recall; log confidence distribution and page reference accuracy.
- Establish an acceptance test that computes per-agreement pass/fail: tiers & rates correctly extracted AND page references correct. Success threshold: >= 95%.

Appendix C — Communication & Escalation
- Daily stand-ups during test execution window
- Immediate escalation for Sev1 to project steering with 4-hour SLA for on-call response
- Weekly QA status to stakeholders

---

If you want, I will:
- Export this plan into Azure DevOps Test Plans or TestRail format and populate initial test cases, or
- Produce the full, detailed test case catalog (all functional, negative, integration, AI-edge, and regression cases) ready for import.

Which would you prefer next?