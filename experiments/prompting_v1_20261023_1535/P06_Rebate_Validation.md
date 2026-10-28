# Test Plan — Supplier Rebate Claim Validation (MVP1)

Version: 1.0  
Author: QA Lead — Supplier Rebate Claim Validation  
Date: 2026-02-XX

This test plan covers functional, integration, system, performance, security and data quality validation for MVP1 (agreement upload & extraction, analyst confirmation, calculation from Delta Lake via Databricks SQL, claim worksheet generation and exports). It assumes the Solution Architecture and Business Requirement Specification provided.

---

## 1. Objectives of Testing
- Verify the system correctly extracts rebate agreement terms (supplier, period, tiers with thresholds & rates, retroactive vs incremental flag, eligible product lines and exclusions) with page references using Azure Document Intelligence + Azure OpenAI.
- Ensure only analyst-confirmed terms are used in calculations.
- Validate calculations of eligible spend, tier reached and earned rebate (retroactive and incremental) against authoritative examples (100% calculation accuracy required).
- Validate claim worksheet generation with supporting purchase lines, Excel export and variance to accrual.
- Validate data integration with Delta Lake via Databricks SQL (data completeness and reconciliation to GL totals).
- Validate availability, performance and auditability non-functional requirements (per-spec performance SLOs, reproducibility).
- Validate security and RBAC (Azure AD), including approval rules (Finance approval > USD 50,000) and segregation of duties (analysts cannot self-approve).

---

## 2. In-Scope / Out-of-Scope

In scope (MVP1)
- Upload of rebate agreements (PDF) and amendments.
- AI extraction of terms and page references.
- Analyst confirmation workflow.
- Calculation service reading Delta Lake purchase data via Databricks SQL; supporting retroactive/incremental rules.
- Claim worksheet generation, line-level support, Excel export, variance to accrual.
- Auditability: capture of agreement version and data snapshot date per run.
- RBAC rules for Rebate Analyst, Finance Manager, Program Admin.

Out of scope (MVP1)
- Supplier portal submission, dispute tracking, accrual posting, amendment comparison (MVP2 items).
- Customer rebates, price protection claims, supplier payment collection.

---

## 3. Test Approach and Strategy

General strategy
- Use risk-based testing prioritizing: extraction accuracy, calculation correctness, data integrity, and RBAC.
- Combine manual exploratory testing for complex agreement language and AI behaviors with automated regression tests for APIs, calculations and UI workflows.
- Maintain a golden dataset for extraction accuracy and calculation validation (provided by Supplier Programs SMEs).
- Automate API and backend tests early; UI automation for critical user flows (upload, confirm, run calc, export).
- Continuous testing in CI/CD (GitHub Actions) for each build. Nightly runs of extraction/calc regression on a representative dataset.

Types of testing
- Functional testing (unit, component, end-to-end).
- Integration testing (Agreement Service <> Blob/Postgres <> APIM <> Azure Document Intelligence/OpenAI; Calculation Service <> Delta Lake).
- System testing (full workflow: upload → confirm → calculate → worksheet/export).
- Regression testing (automated).
- Performance and load testing (single supplier-year and month-end batch).
- Security & access control testing (authentication, authorization, data access, audit logs).
- Data quality and reconciliation testing (Delta Lake vs GL and expected results).
- AI-specific testing (extraction accuracy, false positives/negatives, page reference correctness).
- Usability / UAT with Rebate Analysts and Finance Managers using sample agreements.
- Disaster recovery / backup verification for critical persistence (agreements, confirmed terms, calculation results).

Success criteria (high-level)
- Extraction accuracy ≥95% on golden agreements.
- 100% calculation accuracy against analyst-verified examples.
- Calculation performance: single supplier-year ≤2 minutes; month-end 400 agreements ≤8 hours.
- Reproducibility established: calculations reproducible with agreement version and data snapshot date.
- RBAC and approval rules enforced; analysts cannot self-approve.
- Availability target validated in production readiness tests.

---

## 4. Test Items (to be tested)

Functional components
- Web UI (Upload, Terms Review/Confirmation, Run Calculation, Worksheet Viewer, Export).
- Agreement Service (ingest, save to Blob, create Extract job).
- APIM integrations to Azure Document Intelligence and Azure OpenAI.
- AI extraction pipeline: raw extraction, post-processing, page reference assignment.
- Confirmation workflow and persistence to Azure PostgreSQL.
- Calculation Service (Databricks SQL queries to Delta Lake, tier logic, retroactive/incremental application, variance to accrual).
- Claim worksheet generator and Excel export.
- Batch Scheduler (Azure Function) for month-end batch (smoke/functional).
- Audit logs and metadata storage (agreement version, data snapshot date, extraction model id).
- RBAC & approval workflow via Azure AD.

Non-functional aspects
- Performance and load: calculation times and month-end batch.
- Security: Azure AD auth, data access restrictions, secrets in Key Vault.
- Monitoring and alerting (Datadog, Azure Monitor).

---

## 5. Requirements Traceability (summary)

Map examples (test coverage must ensure each requirement is tested):
- BRS: Extract tiers, rates, eligible product lines, periods -> AI extraction tests + page refs.
- BRS: Analyst confirmation -> tests for confirmed vs unconfirmed use in calculations.
- BRS: Calculation using Delta Lake -> calculation functional tests and reconciliation.
- BRS: Retroactive vs incremental -> test both calculation modes with banded spend.
- BRS: Claim worksheet + Excel export -> verify content, line-level support and variance to accrual.
- BRS: Approval > USD 50k -> RBAC and approval workflow tests.
- BRS: Availability 99% business hours -> production readiness + resilience tests.
- Acceptance Criteria: ≥95% extraction accuracy and 100% calculation accuracy -> dedicated test suites.

A full traceability matrix will be maintained in the QA repository linking each test case to specific FR IDs, user stories and acceptance criteria.

---

## 6. Test Environment Requirements

Environments
- Dev: Unit and component tests; developers.
- CI (Build): automated unit and integration tests.
- QA (Integration): full integration tests with test instances of APIM, Document Intelligence (test keys), OpenAI (sandbox / low-cost model or mocked responses), Databricks test warehouse pointing to a copy of Delta Lake test dataset.
- Staging (Pre-prod): production-like infra (APIM, Key Vault, Blob, PostgreSQL, Databricks), real tokens for Azure services where possible; subset of production-like data (masked).
- Production: out-of-scope for QA but acceptance testing and smoke tests will be run post-deploy.

Environment setup needs
- Azure subscriptions and tenants as per architecture (non-prod).
- Test Azure AD tenants with test users for Rebate Analyst, Finance Manager, Program Admin.
- Key Vault with test secrets.
- Test Blob containers for agreement PDFs.
- PostgreSQL test DB for confirmed terms and results.
- Databricks SQL warehouse with a snapshot of Delta Lake test data (last 24 months coverage).
- Datadog and Azure Monitor hooks for monitoring tests.

Data considerations
- Golden agreement set (authoritative expected extraction) — includes:
  - Simple agreements (straightforward tiers)
  - Complex language (retroactive, incremental, exceptions)
  - Amendments and combined documents
  - Misformatted PDFs (scanned images, tables)
- Purchase data: realistic PO line items mapped to product lines.
- Product line mapping test configs (valid and invalid mappings)
- Masked/made-up PII; confidentiality maintained.

---

## 7. Test Data Requirements & Management

Test data sources
- Golden agreements repository (SME-verified).
- Purchase data snapshots from Delta Lake (test copies) for last 24 months for representative suppliers.
- Product line mapping sets (canonical + edge-case entries).
- Accrual data examples for variance calculations.

Data scenarios
- Supplier with single tier (simple).
- Supplier with multiple tiers (incremental).
- Supplier with retroactive tiers.
- Agreements with exclusions and product-line level eligibility.
- Agreements with amendments changing tiers mid-period.
- Missing or incomplete agreement fields (to verify analyst confirmation required).
- Databricks dataset gaps (to trigger reconciliation alerts).
- Large-volume purchase history (stress case for performance).

Data refresh & snapshotting
- Each test run that validates reproducibility must record a data snapshot id/time and use that snapshot. Snapshot mechanism to be provided by Data platform (Databricks snapshot or query with snapshot_date parameter). Tests must assert the snapshot metadata is captured in calculation results.

Data privacy
- Use masked/anonymized data in non-prod. Production data only used in staging with approved controls.

---

## 8. Test Scenarios and Representative Test Cases

Below are grouped key test scenarios. A full test case suite (with preconditions, steps, expected results) will be maintained in the test management tool.

A. Agreement Ingest & AI Extraction
- TC-A1: Upload well-structured PDF; verify Document Intelligence + OpenAI are called and returned terms contain supplier, period, tier thresholds/rates, retroactive/incremental flag, eligible product lines + page refs. Expected: fields match golden dataset ≥95 accuracy.
- TC-A2: Upload scanned image PDF (OCR); verify extraction still correctly identifies tiers and page refs.
- TC-A3: Upload complex language agreement (nested clauses); verify extractor returns candidate terms and highlights page refs; record missing/ambiguous fields for analyst review.
- TC-A4: Upload amendment PDF; verify extraction recognizes amended tier and maps to base agreement, generates versioning metadata.
- TC-A5: Upload corrupted or unreadable PDF; verify system flags extraction failure and records error for analyst.

B. Analyst Confirmation Workflow
- TC-B1: Rebate Analyst views extracted terms with page references and accepts unchanged terms; confirm terms persisted to PostgreSQL with version id and extracted_by metadata.
- TC-B2: Analyst edits terms (correct threshold/rate); verify edit audit log (who/when) and persisted confirmed terms used for calculations.
- TC-B3: Ensure unconfirmed terms cannot be used in calculation; attempt to run calculation with unconfirmed terms -> expected: system blocks and requires confirmation.
- TC-B4: Permissions: Program Admin can maintain product line mapping; Analyst cannot change product mapping unless role allows.

C. Calculation Engine - Functional
- TC-C1: Single-tier retroactive calculation: supplier spend crosses threshold; verify earned rebate calculated by applying rate to full eligible spend.
- TC-C2: Multi-tier incremental: ensure tier banding applied correctly (earnings per band); use known examples to assert 100% match.
- TC-C3: Tier threshold ascending validation: thresholds must be ascending; system validates on confirmation and flags if not.
- TC-C4: Eligible product lines and exclusions honored: exclude lines flagged in agreement; calculation excludes excluded spend.
- TC-C5: Reconciles to accrual: compute variance to provided accrual numbers and show correct variance.
- TC-C6: Use confirmed terms for calculation; changes after calculation produce new version and a reproducible calculation record.

D. Calculation Engine - Data Integration
- TC-D1: Calculation service executes Databricks SQL using provided credentials; returns expected spend lines and aggregates.
- TC-D2: Snapshot reproducibility: run calculation with snapshot date X and re-run with same snapshot -> identical results.
- TC-D3: Databricks data gap detection: when expected days missing, system logs reconciliation failure and marks calculation with data-quality flag.

E. Claim Worksheet & Exports
- TC-E1: Worksheet shows supporting purchase lines, tier reached, earned rebate, variance to accrual.
- TC-E2: Excel export correct format, all columns present, preserves numeric precision and date stamps.
- TC-E3: Large worksheet export (>100k lines) performance and memory handling.

F. RBAC, Approval Workflow & Auditability
- TC-F1: Analyst runs calculation and prepares worksheet under USD 50k; Finance approval not required; record reviewer if applicable.
- TC-F2: Claim > USD 50k: Finance Manager must approve prior to submission (MVP2 later). For MVP1 ensure approval flag and email/notification stub exists; if Finance Manager attempts to approve, verify proper logging.
- TC-F3: Analyst cannot approve own claims — attempt to approve as same user returns error.
- TC-F4: Audit trail exists for each calculation: agreement version, confirmed terms id, snapshot date, who ran calculation, who confirmed and time stamps.

G. Performance & Scalability
- TC-G1: Single supplier-year calculation completes ≤2 minutes (measure median and 95th percentile).
- TC-G2: Month-end batch of 400 agreements completes within ≤8 hours (run batch simulation or scaled performance test).
- TC-G3: Stress: concurrent calculations by multiple analysts (e.g., 10 concurrent) — system maintains acceptable latency and resource limits.

H. Security & Compliance
- TC-H1: Authentication via Azure AD SSO; non-authenticated user blocked.
- TC-H2: Authorization checks; users cannot access agreements they don't own unless Program Admin.
- TC-H3: Sensitive data encryption in transit & at rest (Blob, PostgreSQL); verify TLS usage and storage encryption enabled.
- TC-H4: Secrets management: Key Vault usage and rotation workflows.
- TC-H5: Penetration tests on public endpoints and API; static code scans integrated in CI.

I. Monitoring, Logging & Alerts
- TC-I1: Calculation service errors generate alerts in Datadog/Azure Monitor.
- TC-I2: Missing data reconciliation triggers specific log entries and status shown in UI.

J. Negative & Edge Cases
- TC-J1: Agreement with contradictory tier statements — extractor returns candidate conflicts; analyst must resolve; system should not auto-use ambiguous terms.
- TC-J2: Product line mapping missing for supplier line — calculation logs unmapped lines and excludes or flags per config.
- TC-J3: Very large threshold values / zero rates / negative spend — validate system handles and reports invalid configs.

---

## 9. Automation Strategy & Tools

Automate
- Unit tests (calculation logic, API handlers).
- API/integration tests for Agreement Service, Calculation Service (Postman/Newman or REST Assured).
- Backend regression tests validating calculation outputs against golden examples (Python test harness).
- UI smoke and critical path flows (upload → confirm → calculate → export) via Playwright or Cypress.
- Performance tests with k6 or JMeter for calculation service and batch.
- CI: GitHub Actions triggers for unit/integration; nightly regression and extraction accuracy runs.
- Test data provisioning scripts for Databricks snapshots.

Tools recommended
- Test management: Azure DevOps Test Plans or Zephyr/JIRA.
- API testing: Postman / REST Assured.
- UI automation: Playwright / Cypress.
- Performance: k6 / Apache JMeter.
- Security scans: OWASP ZAP, Snyk for dependencies.
- Monitoring verification: Datadog APIs.
- Test data and golden dataset stored in secure Git or Blob with access control.

Automation targets (MVP1)
- Smoke tests (100%) automated.
- Core calculation regression tests: automated (cover top 20 canonical cases).
- UI regression suite: ~60% automated initially, expand iteratively.

---

## 10. Test Schedule & Milestones (aligned to Mar–Jun 2026 MVP1)

High-level schedule (example)
- Feb — Test planning & environment setup, golden dataset creation.
- Mar — Integration tests for upload/extraction; automation of extraction accuracy checks.
- Apr — Calculation engine functional tests; integrate Databricks snapshots; automate calculation regression.
- May — System tests, security testing, performance tuning (single supplier & batch).
- Early Jun — UAT with Rebate Analysts & Finance Managers; fix defects.
- Mid Jun — Final acceptance testing & sign-off; deployment to production as scheduled.

Milestones
- Environments ready: Week 1 Mar
- Golden dataset validated: Week 2 Mar
- Extraction accuracy >=95% on golden set: Week 4 Mar
- Calculation accuracy 100% on golden examples: Week 4 Apr
- Performance SLOs met (single calc & batch): End May
- UAT completion and acceptance: Mid Jun

Detailed test calendar and entry/exit criteria will be maintained in the project schedule.

---

## 11. Entry and Exit Criteria

Entry criteria for QA
- Development feature complete for target scope (feature branch merged into QA).
- Environments provisioned (QA/Staging).
- Golden dataset available and validated by SMEs.
- API contracts available; Databricks access provided with test snapshots.
- Test cases for feature area created and reviewed.

Exit criteria for QA (per release)
- All critical and high defects closed or mitigated with acceptance.
- No open critical Severity 1 defects.
- Regression pass rate >= 95% for automated suite and >= 90% for manual suites (subject to agreement).
- Extraction accuracy >=95% on golden set.
- Calculation accuracy 100% for canonical examples.
- Performance targets (single calc & batch) validated in staging.
- Security scan and pen test completed with all critical findings remediated or accepted by security owner.
- UAT sign-off by Rebate Analysts and Finance Manager stakeholders.

---

## 12. Defect Management and Severity Levels

Defect life-cycle
- Log defects in JIRA (or agreed tool) with reproducible steps, environment, logs and attachments (agreements, outputs).
- Triage daily by QA/Dev/BA; severity assigned per impact.

Severity definitions
- Severity 1 (Critical): Calculation incorrect for production example, data corruption, security breach, system unavailable — immediate fix/rollback.
- Severity 2 (High): Extraction failures causing unacceptable manual work, performance breaches preventing batch completion, RBAC high-impact lapses.
- Severity 3 (Medium): UI bugs affecting workflow but with workaround, minor calculation edge-case.
- Severity 4 (Low): Cosmetic, documentation, enhancements.

Escalation and SLA
- S1: Response within 2 hours, resolution or workaround within 24 hours (during sprint).
- S2: Response within 8 hours, fix in next patch/sprint.

---

## 13. Roles & Responsibilities

- QA Lead (author): test plan, strategy, test case design, coordinate QA activities, report test health.
- QA Engineers: create/execute test cases, automation, performance tests, regression pack.
- Developers: unit tests, fix defects, support integration environment.
- Data Platform (Databricks): provide test snapshots, Databricks SQL access.
- AI SME / ML Engineer: support extraction model validation, provide model metadata.
- Supplier Programs SMEs: provide golden agreements, validate extraction and calculations, participate in UAT.
- Program Admin: setup product line mappings and test configs.
- Security Team: run pen tests and approve security posture.
- Release Manager: schedule deployments and coordinate acceptance.

---

## 14. Risks, Assumptions & Mitigations

Risks & mitigations
- Risk: AI extraction underperforms on complex agreements -> Mitigation: mandatory analyst confirmation, improve golden dataset, iterative model tuning and fallback rules.
- Risk: Databricks access delays -> Mitigation: early coordination with Data platform; use mocked datasets for early tests.
- Risk: Insufficient test coverage of edge-case contract language -> Mitigation: recruit SMEs, add real-life complex agreements to golden set.
- Risk: Performance degradation at month-end -> Mitigation: capacity testing, query optimization, batching strategies, resource autoscaling.
- Risk: RBAC misconfiguration allowing self-approval -> Mitigation: rigorous role tests and automated authorization checks in CI.
- Risk: Use of production PII in non-prod -> Mitigation: mandatory data masking & governance; only masked data in non-prod.

Assumptions
- Delta Lake data completeness for last 24 months.
- Agreements mostly digital PDFs (some scanned).
- Data platform can provide snapshots and Databricks SQL access for test envs.

---

## 15. Metrics & Reporting

Metrics to be reported weekly during QA
- Test execution summary: total tests, passed, failed, blocked.
- Defect metrics: open defects by severity, age, throughput.
- Automation coverage: number automated vs manual.
- Extraction accuracy: % fields correct on golden set (overall and per-field).
- Calculation accuracy: % matching golden calculation examples.
- Performance metrics: average/95th percentile calculation time; batch completion time.
- Traceability coverage: % requirements mapped to test cases.
- UAT progress and sign-offs.

Reporting cadence
- Daily stand-ups for QA during sprint.
- Weekly QA status to project stakeholders.
- Pre-release report with exit criteria confirmation.

---

## 16. Acceptance Tests (Summary aligned to BRS acceptance criteria)

Must-pass acceptance tests before MVP1 sign-off:
- AT-1: Extraction accuracy ≥95% on golden agreements (sample set agreed with Supplier Programs).
- AT-2: Calculation accuracy 100% vs SME-validated examples for retroactive and incremental scenarios.
- AT-3: Reproducibility: given agreement version and snapshot date, calculation re-run produces identical results.
- AT-4: Performance: single supplier-year calculation median and 95th percentile ≤2 minutes on staging infra; month-end batch 400 completes ≤8 hours.
- AT-5: RBAC & approval enforcement: Finance approval enforced for claims > USD 50,000 and analysts cannot approve their own claims.
- AT-6: Excel export validated for formatting and line-level support.
- AT-7: Audit logs present for upload, extraction, confirmation, calculations and exports.

---

## 17. Post-Release Validation (Production Smoke)

Post-deploy smoke checks (run within 24 hours)
- Upload a sample agreement and confirm extraction returns expected fields.
- Run a calculation for a low-risk supplier and validate time and result sanity.
- Verify audit entries recorded and RBAC enforced.
- Validate monitoring/alerts integrated (Datadog dashboards).
- Perform sanity DB checks for persisted confirmed terms and calculation results.

---

## 18. Appendix / Deliverables

QA deliverables
- Test plan (this document).
- Test case repository (detailed manual and automated test cases).
- Golden dataset and calculation examples with expected outputs.
- Automation scripts and CI configuration.
- Performance test reports and tuning recommendations.
- Security test and pen test reports.
- Final QA sign-off checklist.

Contacts
- QA Lead: [Name, contact]
- Product Owner / Business Owner: Supplier Programs Finance
- Data Platform Lead: [Name]
- AI/ML Lead: [Name]
- Security Lead: [Name]

---

If you want, I will:
- Create the detailed test case matrix (one file per functional area) mapped to FR IDs and acceptance criteria.
- Draft sample automation test scripts (API and calculation regression) and CI job definitions.
- Schedule a review workshop with SMEs to finalize the golden dataset and acceptance cases. Which would you prefer next?