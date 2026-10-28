- Test Plan
- Vendor Compliance Screening
0.9 · Vendor Compliance Screening · QA Lead, Quality Engineering
This plan defines the quality approach for validating Vendor Compliance Screening MVP1: package upload, classification, extraction, cross-checks, sanctions screening, risk rating, decisions and evidence packs. Continuous monitoring, Ariba integration, self-service and reminders are MVP2.

# Test Objectives
- Verify document classification and field extraction accuracy.
- Validate cross-checks for name, tax ID, address, bank holder and insurance.
- Validate sanctions screening for supplier and owners and match handling.
- Verify risk rating rules are 100% correct.
- Validate approvals, evidence packs, 7-year retention, masking and security.

# In Scope / Out of Scope
In scope (functional): upload; classification; extraction; cross-checks; insurance expiry and coverage; screening API; risk rating; decisions; Compliance Manager approvals and clearance; evidence pack; Azure AD; RBAC.
In scope (non-functional): performance (10 documents in 2 minutes, screening in 10 s), security and privacy, retention, accessibility, observability, reliability.

### Out of scope
Performance management, contract negotiation and ERP payment setup. Continuous monitoring, Ariba, self-service and reminders (MVP2).

# Test Assumptions
- Documents may be scanned or photographed.
- Screening sandbox returns configurable match results.
- Compliance provides golden data.

# Testing Strategy
| Test level | Description |
|---|---|
| Unit testing | developer-owned tests for cross-check rules, risk rating engine, masking and APIs. Target minimum coverage: 85%. |
| Component testing | document service, screening service and evidence service. |
| API and contract testing | positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning. |
| Integration testing | UI–services, document service–Blob/APIM–Document Intelligence, Service Bus–screening service, screening–APIM–screening API, services–PostgreSQL and Azure AD. |
| System testing | end-to-end scenarios across upload, classification, extraction, cross-checks, screening, rating, decision and evidence. |
| User acceptance testing | Supplier Risk Analysts and Compliance Managers validate checks, screening and approvals. |
Techniques: Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Roles & Permissions
- Supplier Risk Analyst: Permitted actions: Upload, review, decide Low/Medium risk; Restricted actions: Approving High risk, clearing matches, settings
- Compliance Manager: Permitted actions: Approve High risk, clear Potential Matches; Restricted actions: Settings
- Risk Admin: Permitted actions: Document types, rules, screening settings; Restricted actions: Decisions
Verify approval and clearance restrictions, masking per role and evidence access control.

# Features to be Tested

## Upload and classification
- PDF/JPG/PNG ≤15 MB; 16 MB rejected; each document type classified; unknown document routed to manual review.

## Extraction and cross-checks
- Legal name, tax ID, address, bank holder compared to form; tax ID format by country; insurance USD 2M exactly passes, USD 1.99M fails; expired insurance flagged.

## Sanctions screening
- Supplier and each owner screened; No Match, Potential Match, Confirmed Match; API timeout blocks decision until screened.

## Risk rating
- Confirmed Match → High; expired insurance → High; tax ID mismatch → High; Potential Match → Medium; all clear → Low.

## Decisions and evidence
- High risk requires Compliance Manager; every Potential Match cleared with reason; evidence pack contains documents, checks, screening results and decision.

# Document AI and Data Quality Validation
Use golden onboarding packages. Targets ≥95% classification and ≥93% field extraction accuracy.
Confusion matrix by document type. Field accuracy for tax IDs and bank holder names. Version tracking per supplier.

# Non-Functional Requirements Testing

## Performance
- 10-document package within 2 minutes; screening within 10 seconds; 10 and 25 concurrent analysts.

## Resilience
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility & Browser Compatibility
- Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow.
- Current enterprise-supported versions of Edge, Chrome and Firefox.

## Security
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Verify bank and tax data masked except last 4 digits.
- Verify screening API key stored in Key Vault and never logged.
- Verify 7-year retention policy and deletion protection on evidence storage.
- Dependency scanning, SAST/DAST and penetration testing before release.

# Observability and Audit Testing
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, supplier, documents, extracted values (masked), screening request and result, risk rating, decision, approver and clearance reasons. Confirm timestamps, access controls, retention and exportability.

# Test Environment & Data
| Data category | Examples |
|---|---|
| Valid | Golden packages with expected checks and ratings |
| Invalid | Unreadable, oversized and unknown documents |
| Boundary | Insurance USD 2M/1.99M, expiry today/yesterday, 15/16 MB |
| Security | Restricted roles, key exposure tests |
| Production-like | Masked packages at monthly volume |
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Entry / Exit Criteria

## Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data available.
- Screening sandbox configured with test match scenarios; golden packages approved.
- Build deployed with unit-test evidence and known limitations documented.

## Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects.
- Classification and extraction targets met.
- Risk rating 100% correct.
- 100% of suppliers screened before decision.
- Retention and masking verified.
- All UAT scenarios approved and business sign-off completed.

# Defect Severity & Process
- Critical: Definition: Sanctioned supplier rated Low or decision without screening; Example: Confirmed Match not shown
- High: Definition: Flow blocked; Example: Screening API integration fails
- Medium – Definition: Workaround; Example: Manual classification needed
- Low: Definition: Cosmetic; Example: Evidence PDF layout
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Test Risks
- False negatives in screening – Scenario tests with sandbox
- Document quality: Manual review route
- Data exposure: Masking and key tests
- API outage: Block-until-screened tests

# Test Deliverables
Master Test Plan and Test Strategy. Requirements Traceability Matrix (RTM). Test scenarios, cases, scripts and automation report. Versioned test data and golden dataset. Defect report, daily status report and test execution report. Performance, security, accessibility and reliability test reports. UAT evidence and sign-off. Test closure report with residual risks and lessons learned.

# Traceability
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, classification and extraction accuracy, screening coverage, rating accuracy, review time, accessibility and security findings and UAT completion.

# Sample E2E Flow
- Analyst signs in with MFA.
- Uploads onboarding package.
- Documents classified and extracted.
- Cross-checks shown.
- Screening performed.
- Risk rating calculated.
- Compliance Manager approves High risk.
- Evidence pack generated and retained.

# Sign-off
| Role | Name | Signature / Date |
|---|---|---|
| QA Lead |  |  |
| Product Owner |  |  |
| Business Owner |  |  |
Release decision: MVP1 should not be released until the exit criteria are met or deviations are accepted by Supplier Risk and Product.