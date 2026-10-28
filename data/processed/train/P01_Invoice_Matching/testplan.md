- QA Test Plan
- Invoice Matching Automation
Version: 1.0
Application: Invoice Matching Automation
Prepared by: QA Lead, Quality Engineering
Reviewed by: Test Manager
Test phase: MVP1
Audience: Business Stakeholders, Product Owners, Architects, Development Team and QA Team
Purpose. This plan defines the quality approach for validating Invoice Matching Automation MVP1, from invoice intake through extraction, SAP PO/GR retrieval, three-way matching, exception listing and review. Items marked MVP2 (SAP posting, exception workflow, duplicate detection, supplier notifications) are forward-looking and are not release blockers for MVP1 unless approved by Product.

## References
- Invoice Matching Automation BRD
- Invoice Matching Automation architecture diagram

# Invoice Extraction and Three-Way Match Validation
- Verify accurate extraction of invoice number, supplier, dates, PO number, currency, tax, totals and line items from supplier PDFs.
- Confirm correct retrieval of PO and GR data from SAP through APIM and accurate three-way matching.
- Validate price (±2% default) and quantity (0 units default) tolerance rules and exception flagging.
- Validate role-based access, approval limits (USD 25,000) and security controls.
- Verify data integrity, traceability, logging, performance, availability and SOX-relevant controls.

# Scope
In scope (functional): mailbox ingestion via Graph API; manual upload; file validation; invoice extraction; PO/GR retrieval from SAP; three-way matching; tolerance rules; match result worksheet; exception list; Azure AD authentication; RBAC; error handling; operational logging.
In scope (non-functional): security, accessibility, performance (10-page invoice in 60 s, 500 invoices per hour), data quality, observability, browser compatibility, reliability and recovery.

### Out of scope
- Payment execution and SAP payment run changes.
- Non-PO invoices and travel and expense claims.
- SAP posting, exception workflow, duplicate detection and supplier notifications are MVP2 capabilities.

# Assumptions, Constraints & Dependencies
- Invoices may be text-based, scanned, multi-page or contain multiple currencies.
- Extraction accuracy depends on labelled sample invoices per pilot supplier.
- SAP PO/GR APIs, Graph API mailbox, Azure AD and storage must be available or replaced with approved mocks.
- AP Operations will provide tolerance values, approval limits and masked production-like invoices.
- Test environments must not contain unmasked bank or tax identifiers.

# Testing Strategy

## Levels of testing
- Unit testing: developer-owned tests for extraction mappers, tolerance calculator, matching engine and APIs. Target minimum coverage: 85%.
- Component testing: mailbox ingestion function, extraction service (Document Intelligence), line normalisation (Azure OpenAI), matching service and notification service.
- API and contract testing: positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning.
- Integration testing: UI–backend, Graph API mailbox–Azure Function, Function–Blob Storage, Service Bus–ingestion service, backend–APIM–Document Intelligence, backend–SAP S/4HANA, backend–PostgreSQL and backend–Azure AD.
- System testing: end-to-end scenarios across intake, extraction, PO/GR retrieval, matching, exception listing, review and approval.
- User acceptance testing: AP Analysts and AP Supervisors validate match results, exception handling, approval limits and usability.

## Test techniques
Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Features to be Tested

## Invoice intake
- Mailbox polling: new invoice, multiple attachments, non-PDF attachment, oversized attachment, duplicate email, mailbox unavailable.
- Manual upload: valid PDF, scanned PDF, corrupted file, empty file, password-protected file, unsupported format; clear errors and no partial records after failure.

## Invoice extraction
- Extract invoice number, supplier, invoice date, PO number, currency, tax, total and every line item.
- Validate multi-page invoices, line tables spanning pages, credit notes with negative totals, multiple tax rates, special characters and decimal precision.
- Verify source page reference for every field and reconciliation of line totals to invoice total.

## PO and GR retrieval
- Test PO found, PO not found, PO closed, partial GR, no GR yet, multiple GRs, SAP timeout and retry.
- Verify supplier on invoice matches supplier on PO; mismatch raised as exception.

## Three-way matching and tolerances
- For PO unit price USD 100.00 and invoice USD 102.00, verify within ±2% tolerance (matched); USD 102.01 must be flagged.
- Quantity invoiced greater than quantity received must be flagged with 0-unit default tolerance.
- Cover zero, null and negative values, rounding boundaries, currency mismatch and admin-modified tolerances per supplier category.

## Match worksheet and exception list
- Validate matched, partially matched and unmatched statuses, variance amounts, exception reasons, filters and export to Excel.
- Verify approval above USD 25,000 requires AP Supervisor and mandatory comment.

# Role-Based Access and Workflow
- AP Analyst: Permitted actions: Upload invoices, review match results, resolve exceptions, approve within limit; Restricted actions: Approve above USD 25,000, tolerance configuration, user management
- AP Supervisor – Permitted actions: Approve above limit, override exceptions with comment, monitor SLAs; Restricted actions: Configuration of tolerance rules and mailbox
- AP Admin: Permitted actions: Tolerance rules, approval limits, supplier mapping, mailbox and user roles; Restricted actions: Approving invoices (segregation of duties)
Verify least privilege, segregation of duties (Admin cannot approve), privilege escalation, direct-URL/API access, inactive users, session expiry and override approvals with mandatory comments.

# Security & Compliance Testing
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Verify masking of bank and tax identifiers in UI, exports and logs.
- Test malicious attachments in the mailbox, file-upload exploits, injection strings in invoice text and oversized payloads.
- Verify encryption at rest and in transit, Key Vault secret handling and Managed Identity access between services.
- Dependency scanning, SAST/DAST and penetration testing before release.

# AI and Data Quality Validation
Use a labelled golden dataset of invoices from all pilot suppliers, including scanned and multi-page invoices. Target accuracy is ≥95% for header fields and ≥90% for line items, measured separately for numeric and text fields.
- Analyse false positives and false negatives in line extraction and review-routing thresholds.
- Validate Azure OpenAI line normalisation does not change quantities, prices or item codes.
- Track model and prompt version per invoice; verify reprocessing after a model change.

# Non-Functional Requirements Testing

## Performance and scalability
- Extraction and matching of a 10-page invoice within 60 seconds.
- Batch of 500 invoices processed within 1 hour; queue depth and Service Bus throughput monitored.
- Test 10, 50 and 100 concurrent users on the match worksheet.

## Reliability and recovery
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility & Browser Compatibility
- Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow.
- Current enterprise-supported versions of Edge, Chrome and Firefox.

# Audit and Observability
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, role, invoice identifier, supplier, PO number, extraction and model version, match outcome, tolerance applied, overrides, approvals and configuration changes. Confirm timestamps, access controls, retention and exportability.

# Test Data Management
- Valid: Pilot supplier invoices with expected golden outputs and matching SAP PO/GR records
- Invalid – Corrupt, password-protected, empty and non-PDF attachments
- Boundary: Price variance exactly at ±2%, quantity over receipt by 1 unit, approval exactly USD 25,000
- Security: Malicious attachments, injection strings, expired tokens and restricted-role accounts
- Production-like – Masked invoices and SAP data at representative monthly volume
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Entry / Exit Criteria

## Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data available.
- SAP non-production PO/GR data seeded for pilot suppliers; AP mailbox test account available.
- Build deployed with unit-test evidence and known limitations documented.

## Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects.
- Extraction targets met for the golden dataset (≥95% header, ≥90% lines).
- 100% of variances above tolerance flagged as exceptions.
- Performance results meet 60-second and 500-per-hour targets.
- All UAT scenarios approved and business sign-off completed.

# Defect Tracking
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong match decision, data corruption or security breach | Invoice outside tolerance marked as matched |
| High | Core workflow blocked or control failure | Approval above USD 25,000 possible without Supervisor |
| Medium | Function works with workaround | One supplier layout needs manual field correction |
| Low | Cosmetic issue | Variance column misaligned in export |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risk Register
| Risk | Mitigation |
|---|---|
| Variable invoice layouts | Golden dataset per supplier, custom extraction models, human review |
| SAP API unavailability | Mocks, contract tests, retries and timeouts |
| Tolerance misconfiguration | Boundary tests and admin change audit |
| Sensitive data exposure | Masking tests, least privilege and log scanning |
| Scope creep into MVP2 | MVP release control and formal change approval |

# Recommended MVP1 Traceability and Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, extraction precision/recall, touchless match rate, exception rate, processing SLA compliance, API error rate, accessibility and security findings and UAT completion.

# Representative End-to-End Scenario
- Authenticate through Azure AD and verify the AP Analyst role.
- Receive an invoice in the AP mailbox and confirm ingestion into Blob Storage and the Service Bus queue.
- Extract header and line data with source references.
- Retrieve PO and GR data from SAP.
- Run three-way matching with tolerance rules.
- Review the match worksheet and exception list.
- Approve within limit, or route above USD 25,000 to AP Supervisor.
- Verify audit records, telemetry and reconciliation of totals.
Release decision: MVP1 should not be released until the exit criteria are met or each deviation has documented impact, mitigation, owner and formal AP Operations/Product acceptance.