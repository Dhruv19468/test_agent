- MASTER TEST PLAN
- Rebate Claim Validation
Version: 0.9
Application: Rebate Claim Validation
Prepared by: QA Lead, Quality Engineering
Reviewed by: Test Manager
Test phase: MVP1
Audience: Business Stakeholders, Product Owners, Architects, Development Team and QA Team
Purpose: This plan defines the quality approach for validating Rebate Claim Validation MVP1: agreement upload, term extraction, analyst confirmation, calculation from Delta Lake purchase data, claim worksheet and accrual variance. Portal submission, disputes, accrual posting and amendment comparison are MVP2.

## References
Rebate Claim Validation BRD. Rebate Claim Validation architecture diagram.

# Test Objectives
Verify extraction of supplier, period, tiers, retroactive/incremental type, eligible product lines and exclusions. Validate that only analyst-confirmed terms are used. Verify calculation accuracy for retroactive and incremental tiers is 100% against verified examples. Validate Delta Lake data retrieval and reconciliation. Validate approval above USD 50,000, segregation of duties and reproducibility.

# In Scope / Out of Scope
In scope (functional): agreement upload; extraction; confirmation; Databricks SQL retrieval; calculation; worksheet export; accrual variance; month-end batch; Azure AD; RBAC.
In scope (non-functional): performance (supplier-year in 2 minutes, 400 agreements in 8 hours), auditability and reproducibility, security, accessibility, reliability.

### Out of scope
- Customer rebates, price protection and payment collection.
- Portal submission, disputes, accrual posting and amendment comparison (MVP2).

# Test Assumptions
- Agreements contain complex tier language and amendments.
- Databricks SQL warehouse available with test data snapshot.
- Analyst-verified calculation examples provided.

# Testing Strategy

## Test levels
- Unit testing: developer-owned tests for tier calculator (retroactive and incremental), eligibility filter, reconciliation and APIs. Target minimum coverage: 85%.
- Component testing: agreement service, extraction, calculation service and batch scheduler.
- API and contract testing: positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning.
- Integration testing: UI–services, agreement service–APIM–Document Intelligence/Azure OpenAI, calculation service–Databricks SQL (Delta Lake), services–PostgreSQL/Blob and Azure AD.
- System testing: end-to-end scenarios across upload, extraction, confirmation, calculation, worksheet and approval.
- User acceptance testing: Rebate Analysts and Finance Managers validate terms, calculations and worksheets.

## Test techniques
Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Test Coverage – Functional

## Agreement extraction
- Tiers, rates, thresholds, periods, eligible lines and exclusions with page references; amendments override base terms.

## Confirmation
- Unconfirmed terms cannot be used; edits recorded with user and time.

## Calculation
- Retroactive: spend USD 2.1M with tiers 2% ≥USD 1M and 3% ≥USD 2M → USD 63,000.
- Incremental: same spend → 2% of USD 1M + 3% of USD 0.1M = USD 23,000.
- Spend exactly at threshold, below first tier (0), excluded product lines, returns and credit notes.

## Data retrieval and reconciliation
- Databricks query by supplier, period and product lines; timeout and retry; totals reconcile to GL control totals.

## Worksheet and approval
- Supporting lines, tier reached, earned amount, variance to accrual, Excel export; above USD 50,000 requires Finance Manager; analysts cannot approve own claims.

# Roles & Permissions
| Role | Permitted actions | Restricted actions |
|---|---|---|
| Rebate Analyst | Upload, confirm terms, calculate, prepare worksheets | Approving own claims, settings |
| Finance Manager | Approve above USD 50,000, review variances | Editing terms |
| Program Admin | Mappings and settings | Approvals |
Verify segregation of duties, approval thresholds, data access restrictions and audit of term edits.

# Security, Privacy and Compliance
Azure AD login, MFA, session timeout, token expiration, logout and JWT validation. RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection. Verify Databricks access via OAuth with least-privilege service principal. Verify spend data not exposed in logs. Dependency scanning, SAST/DAST and penetration testing before release.

# AI and Data Quality Validation
Use golden agreements with SME-verified terms. Target ≥95% term extraction accuracy; calculations must be 100% correct.
- Field-level accuracy for thresholds, rates and tier type.
- Amendment precedence tests.
- Version tracking for model, agreement and data snapshot.

# NFR Testing

## Performance and scalability
- Supplier-year calculation within 2 minutes.
- 400-agreement month-end batch within 8 hours.

## Reliability and recovery
- Re-run of a calculation with the same snapshot produces identical results.
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility and compatibility
- Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow.
- Current enterprise-supported versions of Edge, Chrome and Firefox.

# Logging, Monitoring & Audit
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, agreement version, confirmed terms, data snapshot date, calculation result, approval and export. Confirm timestamps, access controls, retention and exportability.

# Environments and Test Data
- Valid: Golden agreements with verified terms and calculations
- Invalid: Unreadable agreements, missing tiers
- Boundary: Spend at thresholds, USD 50,000.00/50,000.01 approvals
- Security – Restricted accounts
- Production-like – Masked 24-month purchase snapshot
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Suspension, Entry and Exit Criteria
| Entry criteria | Exit criteria |
|---|---|
| BRD approved and requirements baselined; acceptance criteria and thresholds agreed. | At least 95% of planned test cases passed, with all critical-path cases passed. |
| Environment, integrations, monitoring and access provisioned; test data available. | No open Critical defects and no open High-severity security defects. |
| Databricks test snapshot and verified calculation examples available. | 100% calculation accuracy on verified examples. |
| Build deployed with unit-test evidence and known limitations documented. | ≥95% extraction accuracy. |
|  | Batch performance met. |
|  | All UAT scenarios approved and business sign-off completed. |

# Defect Severity & Process
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong rebate amount | Retroactive calculated as incremental |
| High | Calculation blocked | Databricks query fails |
| Medium | Workaround | Manual term correction |
| Low | Cosmetic | Export column width |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risk Register
- Agreement complexity: Confirmation step and golden set
- Data gaps – Reconciliation tests
- Calculation logic errors – Worked examples and boundary tests
- Access delays – Early Databricks provisioning

# Deliverables and Reporting
Master Test Plan and Test Strategy. Requirements Traceability Matrix (RTM). Test scenarios, cases, scripts and automation report. Versioned test data and golden dataset. Defect report, daily status report and test execution report. Performance, security, accessibility and reliability test reports. UAT evidence and sign-off. Test closure report with residual risks and lessons learned.

# Recommended MVP1 Traceability and Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, extraction accuracy, calculation accuracy, batch SLA compliance, reconciliation variances, accessibility and security findings and UAT completion.

# Timeline
- MVP1: Mar–Jun 2026
- MVP2: Q4 2026
- Test execution and UAT aligned to MVP1 milestones above.

# Key End-to-End Scenario
- Sign in as Rebate Analyst.
- Upload an agreement.
- Confirm extracted terms.
- Run a calculation from Delta Lake.
- Review worksheet and variance.
- Finance Manager approves.
- Verify audit and reproducibility.
Release recommendation: MVP1 should not be released until the exit criteria are met or deviations are accepted by Supplier Programs Finance and Product.