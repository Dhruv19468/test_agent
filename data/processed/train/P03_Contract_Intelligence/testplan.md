- Test Strategy & Plan
- Contract Intelligence
Version: 1.0
Application: Contract Intelligence
Prepared by: QA Lead, Quality Engineering
Reviewed by: Test Manager
Test phase: MVP1
Audience: Business Stakeholders, Product Owners, Architects, Development Team and QA Team
Purpose: This plan defines the quality approach for validating Contract Intelligence MVP1, from contract upload through storage, processing, extraction, RAG scoring and the Contract Overview page. Draft analysis, renewal alerts, CRM integration and bulk upload are MVP2 and not release blockers.

# Contract Extraction and RAG Scoring Validation
- Verify upload validations and storage of original contracts in blob storage.
- Verify extraction of metadata and clauses with page references.
- Validate RAG scoring of all seven P3 Levers against documented thresholds and the Legal golden dataset.
- Validate Contract Overview search, filters, Summary and P3 Lever Status.
- Validate persona-based access, especially Customer restrictions, and audit logging.

# Scope of Testing
In scope (functional): upload and validation; blob storage; processing statuses; OCR; metadata and clause extraction; RAG scoring; Contract Overview; contract details; Standard Clause Library change and recalculation; failure notification; Azure AD; persona RBAC.
In scope (non-functional): performance (50 pages in 15 minutes, overview in 3 seconds for 5,000 contracts), security, accessibility, observability, reliability and browser compatibility.

### Out of scope
- Editing clauses or overriding RAG scores.
- E-signature and authoring.
- Draft analysis, renewal alerts, CRM integration and bulk upload (MVP2).

# Quality Risks, Assumptions and Dependencies
- Contracts may be scanned, long or use non-standard clause wording.
- Golden dataset of contracts with Legal-approved lever colours is required.
- Document Intelligence, Azure OpenAI, Service Bus and SendGrid must be available or mocked.
- SBU/customer mappings seeded before testing.

# Approach
| Test level | Description |
|---|---|
| Unit testing | developer-owned tests for upload validators, lever scoring rules, overview aggregation and APIs. Target minimum coverage: 85%. |
| Component testing | file service, processing service, extraction (Document Intelligence + Azure OpenAI), notification function and overview aggregation. |
| API and contract testing | positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning. |
| Integration testing | UI–file service, file service–Blob Storage, Service Bus–processing service, processing–APIM–Document Intelligence/Azure OpenAI, processing–PostgreSQL, Function–SendGrid and Azure AD. |
| System testing | end-to-end scenarios across upload, processing, extraction, scoring, overview and details. |
| User acceptance testing | Legal users validate extraction and scoring; account managers validate the overview and restrictions. |
Techniques: Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Test Coverage – Functional
- Upload and validation: Mandatory fields, PDF/DOCX only, 25 MB limit, password-protected file rejection, unique contract name per customer, Effective Date not after Expiration Date. Customer list filtered by SBU; confirmation message and Processing status after upload.
- Processing and failure handling – Statuses Uploaded → Processing → Completed/Failed; unreadable scan fails with readable reason and email to uploader; resubmission succeeds. Processing logs in Datadog with contract reference.
- Extraction: Parties, effective/expiration dates, renewal type, governing law, notice period; mismatch with user-entered values highlighted. Clauses with page references; clicking a reference opens the document at the page.
- RAG scoring: Payment Terms 45 days → Green, 46 and 60 → Amber, 61 → Red, missing → Red 'Clause not found'. All seven levers scored; threshold change by Admin triggers recalculation with previous result in history.
- Contract Overview: Search by customer, account number, contract name (min 3 characters), 'No contracts found' message. Active/Expired view, Expiring-in 30/60/90/180 days, Summary counts, P3 Lever Status counts, expand/collapse.

# Access Control Testing
| Role | Permitted actions | Restricted actions |
|---|---|---|
| Legal | Upload, view all contracts and analysis | Settings, user management |
| Admin | All Legal actions, mappings, Standard Clause Library, users | Editing RAG results |
| Customer | Read-only overview and contracts for assigned customers | Upload, Settings, unassigned customers |
Verify hidden menus per persona, direct-URL access denied for Upload and Settings, customer-level data isolation and logout/back-button behaviour.

# Security & Compliance Testing
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Verify uploaded files cannot be executed or accessed without authorisation (signed URLs only).
- Test malicious files, injection in contract names and oversized uploads.
- Verify no contract text in application logs.
- Dependency scanning, SAST/DAST and penetration testing before release.

# AI and Data Quality Validation
Use a Legal golden dataset of contracts with approved lever colours and metadata. Targets: ≥90% lever colour accuracy and ≥95% metadata accuracy.
- Measure per-lever accuracy and confusion between Amber and Red.
- Verify reasons and page references support each score.
- Re-run golden set after model, prompt or library changes.

# Non-Functional Testing

## Performance and scalability
- 50-page contract processed within 15 minutes.
- Contract Overview within 3 seconds for 5,000 contracts.
- 10, 25 and 50 concurrent users.

## Reliability and recovery
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility and compatibility
- Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow.
- Current enterprise-supported versions of Edge, Chrome and Firefox.

# Logging, Monitoring & Audit
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, persona, contract identifier, SBU, customer, action (upload, view, archive), model version and library version. Confirm timestamps, access controls, retention and exportability.

# Test Data and Environment Strategy
| Data category | Examples |
|---|---|
| Valid | Golden contracts with approved lever colours |
| Invalid | Password-protected, XLSX, >25 MB, unreadable scans |
| Boundary | Payment terms 45/46/60/61 days, names of 2/3/120/121 characters |
| Security | Restricted persona accounts, direct URLs |
| Production-like | 5,000 masked contracts across SBUs |
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Entry / Exit Criteria

## Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data available.
- Golden dataset approved by Legal; SBU/customer mappings seeded.
- Build deployed with unit-test evidence and known limitations documented.

## Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects.
- ≥90% lever accuracy and ≥95% metadata accuracy on golden set.
- Customer persona isolation verified.
- Performance targets met.
- All UAT scenarios approved and business sign-off completed.

# Defect Severity & Process
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong RAG colour shown as correct, data leak across customers | Customer user sees another customer's contract |
| High | Upload or processing blocked | All scanned contracts fail |
| Medium | Workaround exists | Filter needs page refresh |
| Low | Cosmetic | Badge colour shade |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risks and Mitigations
| Risk | Mitigation |
|---|---|
| Poor scan quality | OCR tests and failure flow |
| Scoring inaccuracy | Golden dataset and reason review |
| Access leakage | Persona isolation tests |
| Performance at scale | Volume tests with 5,000 contracts |

# Deliverables and Reporting
- Master Test Plan and Test Strategy
- Requirements Traceability Matrix (RTM)
- Test scenarios, cases, scripts and automation report
- Versioned test data and golden dataset
- Defect report, daily status report and test execution report
- Performance, security, accessibility and reliability test reports
- UAT evidence and sign-off
- Test closure report with residual risks and lessons learned

# Recommended MVP1 Traceability and Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, lever accuracy, extraction accuracy, processing SLA compliance, failure rate, accessibility and security findings and UAT completion.

# Schedule
- MVP1 build: Apr–Jun 2025
- UAT: Jul 2025
- MVP2: Q4 2025
- Test execution and UAT aligned to MVP1 milestones above.

# Sample E2E Flow
- Sign in as Legal.
- Upload a contract with attributes.
- Verify storage and processing.
- Verify metadata and clauses.
- Verify RAG scores.
- Verify Contract Overview as Customer persona.
- Verify audit log.

# Approvals
| Role | Name | Signature / Date |
|---|---|---|
| QA Lead |  |  |
| Product Owner |  |  |
| Business Owner |  |  |
Go/No-Go: MVP1 should not be released until the exit criteria are met or deviations are formally accepted by Legal Operations and Product.