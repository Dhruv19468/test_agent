# Test Plan — Supplier Rebate Claim Validation

Version: 1.0  
Prepared by: QA Lead  
Date: 2026-02-XX

## 1. Document Purpose
This test plan describes the testing strategy, scope, resources, schedule, and detailed test approaches for Supplier Rebate Claim Validation (MVP1, with MVP2 test considerations). It ensures the product meets functional, non-functional, security, regulatory and acceptance criteria defined in the Business Requirement Specification.

## 2. Objectives
- Verify automated extraction of rebate agreement terms (tiers, rates, eligible product lines, periods) from PDF agreements using Azure Document Intelligence and Azure OpenAI meets ≥95% extraction accuracy compared to golden dataset.
- Ensure analyst confirmation flow prevents unconfirmed terms from being used.
- Validate correct rebate calculations (retroactive and incremental) against Databricks Delta Lake purchase data; meet 100% calculation accuracy on analyst-verified examples.
- Validate claim worksheet generation (supporting purchase lines, export to Excel), variance-to-accrual, RBAC and approval workflows.
- Verify performance and scalability: single supplier-year calculation ≤ 2 minutes; month-end batch (400 agreements) ≤ 8 hours.
- Ensure auditability (reproducible calculations with agreement version and data snapshot date), security controls, and availability SLAs.

## 3. Scope

### In scope (MVP1)
- Upload of rebate agreement PDFs and amendments (Blob Storage).
- AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions (Azure Document Intelligence + Azure OpenAI).
- Analyst confirmation step; confirmed terms persisted to Azure PostgreSQL.
- Calculation service retrieving purchase data from Delta Lake (Databricks SQL) to compute eligible spend, tier reached, earned rebate (retroactive/incremental).
- Claim worksheet generation with supporting purchase lines, Excel export, variance to accrual.
- RBAC: Azure AD authentication; approval rules (Finance Manager for claims > USD 50,000); analysts cannot approve own claims.
- Auditability: record agreement version, confirmation user, data snapshot date.

### Out of scope (MVP1)
- Supplier portal submission, dispute tracking, accrual posting, amendment comparison (MVP2 scope).

## 4. Features to be Tested
- Agreement upload (file types, size limits, amendments)
- AI extraction: fields and page references, confidence scores
- Terms confirmation UI and persistence
- Calculation logic:
  - Retroactive vs incremental
  - Tier boundary behaviors (exact thresholds)
  - Eligible vs excluded product lines
  - Product line mapping application
  - Spend reconciliation to GL totals
- Claim worksheet and Excel export contents/format
- Variance to accrual calculation/reporting
- RBAC and approval workflows (including segregation of duties)
- Integration:
  - Delta Lake (Databricks SQL)
  - Azure Blob Storage
  - Azure PostgreSQL
  - APIM to Azure Document Intelligence and OpenAI
  - Azure AD auth flows
- Performance and scale: single-run and batch
- Auditability and reproducibility (snapshot date behavior)
- Error handling and resiliency (AI failures, missing data, corrupted PDFs)
- Logging, monitoring and alerts (Datadog, Azure Monitor)
- Data protection/security controls: access restrictions, encryption at rest/in transit

## 5. Features Not to be Tested
- Supplier portal submission, dispute workflow, accrual postings (MVP2)
- Production-only infrastructure failover (except as part of non-functional load/availability testing in pre-prod)
- Payment collection flows

## 6. Test Types & Approach

### 6.1 Functional Testing
- Unit testing (development responsibility; QA will review unit test coverage reports)
- Component testing of Agreement Service and Calculation Service
- API testing for service endpoints (Agreement upload, term confirm, run calculation, fetch results)
- UI testing for upload, term review/confirmation, calculation run, worksheet review/export, approvals

Approach: manual test cases executed in test environments; automation for repeatable API and calculation checks.

### 6.2 Integration Testing
- Validate interactions across services: Web UI ↔ Agreement Service ↔ Blob Storage/Postgres; Calculation Service ↔ Databricks SQL ↔ PostgreSQL; APIM ↔ Azure Document Intelligence/OpenAI.
- Data flow validation end-to-end for example agreements: upload → extract → confirm → calculate → worksheet.

Approach: automated API integration tests and scheduled integration scenarios.

### 6.3 System Testing
- Full end-to-end scenarios with realistic data snapshots (golden purchase data) and product line mappings.

### 6.4 Regression Testing
- Regression suite to be run on every release; includes extraction/pass/fail scenarios and calculation verification.

Approach: automated and nightly runs in test/staging.

### 6.5 Performance & Load Testing
- Single supplier-year calculation: measure and verify ≤ 2 minutes.
- Month-end batch: run 400 agreements in a single job and verify completion ≤ 8 hours.
- Concurrent users: simulate expected analyst/finance manager load (e.g., 50 concurrent UI users) to ensure 99% business-hours availability target.

Tooling: JMeter or k6 for API/Service load tests; Databricks job profiling for SQL execution times.

### 6.6 Security & Access Control Testing
- Azure AD authentication/authorization (SSO/OAuth flows)
- RBAC enforcement: Test that Finance Managers can approve > USD 50k, analysts cannot approve own claims, Program Admins manage mappings.
- Data protection: verify encryption-at-rest/in-transit, least-privilege access to Blob/Postgres/Databricks.
- Vulnerability scanning and pen-testing in pre-prod; SAST/DAST scans integrated with CI.

### 6.7 AI/Model Validation Testing
- Extraction accuracy against golden dataset (≥95%).
- Confidence thresholds and fallback/error states for low-confidence extractions.
- Page reference correctness.
- Ambiguity handling and multi-version agreements.
- Tests for retro vs incremental misclassification.

Approach: measure precision/recall per field; record false positives/negatives for retraining and model governance.

### 6.8 Auditability & Reproducibility Testing
- Re-run calculations with same data snapshot date and confirmed terms; results must match previous run.
- Amendments and versioning: validate that changing agreement version produces new reproducible result and historical result preserved.

### 6.9 Usability & Accessibility
- Basic UI usability checks for analyst workflows.
- WCAG 2.1 AA basic checks for critical pages.

### 6.10 Compliance & SOX Controls Testing
- Ensure approvals and segregation of duties controls satisfy SOX/C2P checklist.
- Logs and audit trails exist and are tamper-evident.

## 7. Test Environment
- Environments: Dev, Test (integrated), Staging/Pre-prod (production-like), Production (post-release validation).
- Services and dependencies mirrored in Test/Staging: Azure AD test tenant, Blob Storage, Azure PostgreSQL test instance, Databricks SQL workspace (with test Delta Lake snapshots), APIM test instance, Azure Document Intelligence + OpenAI sandbox resources.
- Monitoring: Datadog and Azure Monitor integration present in Staging.

Environment setup responsibilities: Platform/Infra teams (Databricks and Azure). QA to validate environment readiness checklist before test execution.

## 8. Test Data Requirements & Management
- Golden agreements dataset: 100+ annotated PDF agreements (covering simple, complex, retroactive, incremental, tier edge cases, exclusions, amendments) maintained by Supplier Programs SMEs.
- Purchase data snapshots: Delta Lake snapshots for last 24 months; a golden snapshot for deterministic calculation tests.
- Product line mapping configurations (correct and deliberately incorrect mappings for negative tests).
- Test user accounts: Rebate Analyst, Finance Manager, Program Admin with Azure AD test accounts.
- Sensitive data: Use masked/anonymized data where production data is not available/allowed per security policy.

Data management: QA will request data snapshots from Data Platform Team. Maintain dataset versions, and store test data in secure test storage.

## 9. Test Tools & Automation Strategy
- Test management: Jira (or Azure DevOps Boards) for test cases, execution, and defects.
- API testing: Postman + Newman or REST-assured; automated as part of CI.
- UI automation: Playwright or Selenium (prefer Playwright for speed and reliability).
- Unit/Component automation: PyTest/Unittest (per service language).
- Calculation verification: automated scripts (Python) to run calculation service via API and compare outputs with expected results.
- Performance testing: k6 or JMeter.
- CI/CD: GitHub Actions integrated with test automation; run smoke/regression in pipeline.
- Security scanning: Snyk/Veracode for SAST; OWASP ZAP for DAST.
- Reporting & monitoring: Datadog dashboards for performance and errors.

Automation scope:
- High priority: API contracts, calculation correctness scenarios, AI extraction regression tests (field-level comparisons), RBAC workflows, critical UI flows (upload → confirm → calculate → export).
- Medium: full UI regression suite.
- Low: exhaustive UI style checks.

## 10. Traceability
A Requirements Traceability Matrix (RTM) will map each FR/Acceptance Criteria to test cases. Key mappings:
- Extraction accuracy (Acceptance) → AI extraction field tests + golden dataset evaluation.
- Calculation accuracy → calculation unit and end-to-end tests with golden data.
- RBAC/Approval rules → role-based integration tests + negative tests.
- Performance SLAs → performance tests for single-run and batch.

RTM will be maintained in Jira/Confluence.

## 11. Test Cases & Test Scenarios (Representative / High-level)
Note: Detailed test cases will be stored in test management tool. Below are representative scenarios.

### 11.1 Agreement Upload & Extraction
- TC-A1: Upload valid PDF agreement → Verify API accepts, stores in Blob, returns extraction job id.
- TC-A2: Upload corrupted/unsupported file → Verify error returned and file rejected.
- TC-A3: Extraction success for standard agreement → Verify fields (supplier, period, tiers, retro vs incremental, eligible product lines, exclusions) extracted with page refs and confidence scores.
- TC-A4: Complex language agreement → Verify fallback behavior (low confidence flag) and analyst prompt to confirm.
- TC-A5: Amendment upload → Verify mapping to original agreement and versioning.

### 11.2 Terms Confirmation
- TC-B1: Analyst views extracted terms and page refs → Accept terms → Confirmed terms persisted to PostgreSQL with user and timestamp.
- TC-B2: Analyst rejects/change terms → Verify updated terms flow and log.
- TC-B3: Unconfirmed terms cannot be used to run calculations → Verify calculation API returns error/blocked.

### 11.3 Calculation Logic
- TC-C1: Incremental tiers correct calculation → Use golden sample, verify per-tier band calculations and total rebate.
- TC-C2: Retroactive tiers correct calculation → Verify full-spend rate application at threshold attainment.
- TC-C3: Exact-threshold boundary test → Spend equals tier threshold → verify proper tier and rate applied.
- TC-C4: Exclusions and eligible product line mapping → Verify excluded SKUs omitted from eligible spend.
- TC-C5: Missing product line mapping → Verify exception handling and admin notification.
- TC-C6: Variance-to-accrual computation → Verify difference calculation against accrual snapshot.

### 11.4 Worksheet & Export
- TC-D1: Claim worksheet contains supporting purchase lines (line-level details), tier reached and earned rebate.
- TC-D2: Excel export integrity: file download, format, columns, sums equals displayed results.
- TC-D3: Large worksheet export performance & memory handling.

### 11.5 Approval & RBAC
- TC-E1: Analyst runs and prepares worksheet → cannot self-approve if approval required.
- TC-E2: Finance Manager approves claim > USD 50,000 → Verify approval persisted, audit log includes approver and timestamp.
- TC-E3: Program Admin user permissions to modify product mapping and cannot approve claims (unless configured).

### 11.6 Integration
- TC-F1: Calculation Service successfully queries Databricks SQL and handles transient SQL failures (retry/backoff).
- TC-F2: APIM calls to Azure Document Intelligence and OpenAI return expected layout and extracted fields.

### 11.7 Performance & Scalability
- TC-G1: Single supplier-year run under 2 minutes using golden dataset.
- TC-G2: Month-end batch: execute 400 calculations and finish under 8 hours; measure resource utilization.
- TC-G3: Concurrent users: 50 analysts running operations; verify UI responsiveness and system stability.

### 11.8 Auditability & Reproducibility
- TC-H1: Re-run calculation with same snapshot date and confirmed terms → identical outputs and same calculation metadata.
- TC-H2: Change in agreement version → new results persist, old results remain unchanged and retrievable.

### 11.9 AI Failures & Error Handling
- TC-I1: Low-confidence extraction → system flags and disallows automatic use until analyst confirms.
- TC-I2: False extraction mapping test cases → log false positives for model governance.

### 11.10 Security Tests
- TC-J1: Unauthorized user attempts upload, view or approve → access denied.
- TC-J2: Verify transport encryption (HTTPS), storage encryption, and Key Vault integration for secrets.
- TC-J3: SAST/DAST vulnerabilities are addressed or have accepted mitigations.

## 12. Acceptance Criteria & Exit Criteria

### Acceptance Criteria (from BRS)
- AI extraction accuracy ≥ 95% on golden agreements (measured field-by-field).
- 100% calculation accuracy against analyst-verified examples (golden calculation tests).
- Reproducible calculations with agreement version and data snapshot date.
- Single supplier-year calculation ≤ 2 minutes; month-end batch ≤ 8 hours.
- RBAC and approval workflow implemented: approvals > USD 50,000 by Finance Manager; analysts cannot approve their own claims.
- Exportable claim worksheet with required details.
- Audit logs available for actions: upload, extract, confirm, run calculation, approval.

### Exit Criteria (to move from Test to Staging/Pre-prod)
- All critical and high severity defects resolved or mitigated with approved waivers.
- All acceptance criteria met.
- Regression suite (smoke and core) passes in Test environment.
- Performance tests pass SLAs or have documented mitigation/plan.
- Security scan results reviewed and critical vulnerabilities remediated.
- Test sign-off by QA Lead, Product Owner (Supplier Programs), and relevant SMEs.

## 13. Entry Criteria (to begin testing)
- Test environment provisioned and stable.
- Required services reachable (Azure AD test tenant, Blob, Postgres, Databricks test workspace, APIM, AI services).
- Golden dataset and purchase data snapshots ingested into test environments.
- Build deployed to Test environment and smoke tested.
- Test resources (personnel, tools, access) available.

## 14. Defect Management
- Tool: Jira (or Azure DevOps) for defect lifecycle.
- Severity/Priority definitions aligned with org standards.
- Triage cadence: daily during critical phases; twice-weekly in steady state.
- SLA for defect response:
  - Critical (P0): 24 hours
  - High (P1): 3 business days
  - Medium (P2): 10 business days
  - Low (P3): next sprint/planned
- Retest and closure process defined; all defects must be reproducible with test steps and logs.

## 15. Roles & Responsibilities
- QA Lead (this plan owner): test strategy, scheduling, RTM, final test sign-off.
- QA Engineers: test case development, execution, automation, defect logging.
- Developers: unit tests, fix defects, provide support for test harness.
- Data Platform Team: provide Databricks access, purchase data snapshots.
- Supplier Programs SMEs: supply golden agreement dataset, validate AI extraction and calculation results.
- Security Team: run SAST/DAST, pen-test, verify compliance.
- Product Owner / Business Owner: acceptance of functional results and sign-off.
- Platform/Infra: environment provisioning and monitoring.

## 16. Test Schedule & Milestones (MVP1: Mar–Jun 2026)
- Test planning & environment setup: Mar weeks 1–2
- Golden dataset assembly & data snapshot: Mar weeks 2–4
- Component/unit testing by devs: Mar–Apr
- Integration testing: Apr
- System & AI validation testing: Apr–May
- Performance & load testing: May
- Security & compliance testing: May
- Regression & UAT with business (Rebate Analysts & Finance Managers): May–Jun
- Final acceptance testing & sign-off: End of Jun

Detailed test calendar to be maintained in Jira/Confluence and updated weekly.

## 17. Risk & Mitigation
- Risk: Complex agreement language causes low extraction accuracy.
  - Mitigation: Mandatory analyst confirmation; maintain golden dataset to retrain/refine prompts; implement low-confidence workflow.
- Risk: Delta Lake gaps or inconsistent purchase data.
  - Mitigation: Reconciliation checks, fallbacks, and documented exceptions; require data platform to provide completeness reports.
- Risk: Misinterpretation of retroactive vs incremental.
  - Mitigation: Explicit extraction field with tests covering both patterns and edge cases; SME review for ambiguous cases.
- Risk: Performance degradation at month-end.
  - Mitigation: Load tests, capacity planning, parallelization of calculation jobs, resource autoscaling.
- Risk: Security or compliance blockers (SOX).
  - Mitigation: Early involvement of Security/Compliance teams; audit trail verification and segregation of duties tests.

## 18. Reporting & Metrics
- Daily test execution reports during active test cycles.
- Weekly quality dashboards covering:
  - Test case execution status
  - Defect counts by severity and status
  - Pass/fail rate for AI extraction (field-level)
  - Calculation accuracy % (golden tests)
  - Performance test results (latency and throughput)
- Final Test Summary Report and Go/No-Go recommendation.

## 19. Test Deliverables
- Test Plan (this document)
- Test Cases and Scripts (stored in test management tool)
- Test Data Inventory and Snapshots
- Automation Test Suites (repository links)
- Test Execution Reports and Dashboards
- Defect Logs
- Performance & Security Test Reports
- Final Test Summary & Sign-off document

## 20. Automation & Regression Strategy
- Automate API-level test cases for extraction, confirmation, calculation and result retrieval as first priority.
- Automate calculation verification using expected output CSVs from golden dataset.
- Schedule nightly regression runs in CI; full regression before each release.
- Maintain CI gating for critical tests (smoke + core calculation tests) in GitHub Actions.

## 21. AI-specific Governance & Testing
- Governance: ensure AI use is approved per AI Governance Council; maintain model prompt/version and extraction model versioning in logs.
- Field-level accuracy metrics collected per run; threshold alerts for drop in accuracy.
- Retraining/Prompt-tuning tickets created from logged extraction errors.
- Save extraction outputs and model responses for audit and retraining (subject to data retention and security policies).

## 22. Compliance & SOX Considerations
- Test and demonstrate segregation of duties (analyst cannot approve own claims) and maintain audit trails.
- Validate logging and retention meet SOX and internal policies.
- Ensure change control and CI/CD deployment approvals captured per C2P and WAB processes.

## 23. Post-release & Production Validation
- Production smoke tests (sanity): agree on a small set of non-production sensitive agreements to run first calculation after deployment.
- Monitor production metrics for first 72 business hours: error rates, calculation times, AI extraction confidence dips.
- Rollback plan documented with infra and dev teams.

## 24. Approval & Sign-off
Sign-off required from:
- QA Lead
- Product Owner (Supplier Programs)
- Finance Manager (to confirm acceptance of approval flow)
- Data Platform Lead (Databricks/Delta)
- Security/Compliance Lead
- AI Governance representative

Sign-off will be recorded in Confluence/Jira with formal acceptance of Exit Criteria.

---

Appendices:
- Appendix A — Sample RTM template (in test repository)
- Appendix B — Golden dataset inventory (SME-maintained)
- Appendix C — Known limitations and waivers (if any)

End of Test Plan.