- Test Plan : Cost Sheet Automation
- Version: 1.0
- Application: Cost Sheet Automation
- Prepared by: Sangram Mohanty
- Reviewed By : Pradeep Baskaran
- Test phase: MVP1
Audience: Business Stakeholders, Product Owners, Architects, Development Team and QA Team
Purpose. This plan defines the quality approach for validating the Cost Sheet Automation MVP1, from supplier PDF intake through extraction, validation, worksheet generation, pricing comparison, approval and audit logging. Items explicitly marked MVP2 are retained as forward-looking coverage and are not release blockers for MVP1 unless approved by Product.

# References
- Cost Sheet Automation BRD
- Cost Sheet Automation Figma designs

# AI Driven Extraction and Historical Pricing Validation
- Verify accurate extraction of Anixter parts, Trim, Functions, Finishes, Options, descriptions, categories, prices and metadata from supplier PDF price books.
- Confirm correct pricing-data mapping, calculations and standardized pricing worksheet generation.
- Validate retrieval of current pricing from enterprise data sources and accurate current-versus-updated comparisons.
- Validate threshold rules, exception handling, approval workflow, role-based access and security controls.
- Verify data integrity, audit trails, operational logging, accessibility, performance, availability and compliance expectations.
- Demonstrate support for multiple supplier formats with minimal manual intervention and a controlled process for unknown formats.
- Scope
- In scope for MVP1
Functional: supplier PDF upload; file validation; PDF parsing and extraction; pricing-data mapping; validation rules; updated pricing worksheet generation; worksheet review and approval; Azure AD authentication; RBAC; error handling; current-price retrieval and comparison where enabled by the MVP1 design; audit and operational logging.
Non-functional: security, accessibility, performance, data quality, logging/observability, browser compatibility, reliability and recovery validation.

# Out of scope
- Mainframe pricing-logic changes.
- CORE system changes.
- Non-pricing processes; refer to the BRD.
- Supplier discount-rule automation is a forward-looking MVP2 capability unless explicitly enabled for MVP1.

# Quality Risks, Assumptions and Dependencies
- Supplier PDFs may be text-based, scanned, password-protected, multi-column or formatted differently between releases.
- AI-assisted extraction accuracy depends on representative labelled samples and agreed ground truth.
- Current pricing, storage, CMT(AI), Azure AD and downstream APIs must be available or replaced with approved mocks.
- Business owners will provide threshold values, approval rules, supported file limits, SLAs, supplier templates and masked production-like data.
- Test environments must isolate supplier-sensitive data, use least-privilege accounts and retain test evidence.
- Current implementation and assumptions.
- Supplier Name.
- Testing Strategy
- Test levels
1.   Unit testing: developer-owned tests for PDF parsers, business rules, validation engine and APIs. Target minimum coverage: 85%, with critical calculation and security paths covered.
2.   Component testing: PDF extraction service, worksheet generator, authentication module and audit-logging module.
3.   API and contract testing: positive and negative API behaviour, request/response schemas, authentication, error codes, idempotency and version compatibility.
4.   Integration testing: UI–backend, backend–database, backend–Azure AD, backend–CMT(AI), backend–storage and downstream pricing integrations.
5.   System testing: end-to-end business scenarios across upload, extraction, validation, comparison, worksheet generation, approval and audit.
6.   User acceptance testing: Pricing Analysts and Pricing Admins validate business workflow, pricing accuracy, usability and exception handling.

# Test techniques
Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise supplier/browser coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Functional Test Coverage

## Upload and file security
- Valid PDF; large PDF; multi-page PDF; empty file; corrupted PDF; password-protected PDF(Need to check with business); duplicate upload; unsupported format; virus-infected or malicious file; concurrent uploads.
- Validate file size/type limits, filename handling, checksum or duplicate(Need to Confirm from Business regarding the file structure) detection, upload progress, cancellation, retry, safe storage, clear user errors and no partial records after failure.

## PDF extraction and mapping
- Extract parts, prices, Trim, Functions, Finishes, Options, descriptions, categories, units, currencies, effective dates and supplier metadata.
- Validate missing prices, invalid symbols, OCR quality, special characters, decimal precision, currency formats, multi-column layouts, repeated headers/footers, tables spanning pages and duplicate records.
- Verify source-to-target field mapping, confidence scores or review flags where available, traceability to source page/row and preservation of leading zeroes and identifiers.

## Supplier formats
Cover Supplier Type A, Supplier Type B, Supplier Type C, a new supplier template and an unknown format. Verify correct template selection, graceful rejection or manual-review routing for unknown layouts, and that a new template does not regress existing suppliers.

## Worksheet generation and export
- Validate required columns, column order, formatting, formulas, rounding, currency, effective dates, completeness, duplicate handling, special characters, row counts and source traceability.
- Verify Excel export, file naming, download permissions, re-openability, formula/value consistency and protection against overwriting an approved worksheet.

## Pricing retrieval, comparison and validation
- Test existing part found, part not found, multiple matches, invalid mapping, timeout, database failure and retry behaviour.
- For current price $100 and updated price $110, verify a 10% increase. For current price $100 and updated price $90, verify a 10% decrease.
- Cover zero, null, negative, equal and duplicate prices; very large values; rounding boundaries; currency mismatch; and division-by-zero handling.
- Validate increases/decreases beyond threshold, boundary values, exception overrides, admin-modified thresholds, versioning and approval of overridden exceptions.

# Role-Based Access and Workflow
Role   Permitted actions   Restricted actions
Pricing Analyst   Upload files, review extracted pricing, resolve exceptions, approve worksheets where authorised   Supplier configuration, validation-rule administration and user management
Pricing Admin   Supplier configuration, validation rules, user management and controlled overrides   Actions outside assigned environment or tenant
Verify least privilege, privilege escalation, direct-URL/API access, role switching, inactive users, session expiry, separation of duties, approval transitions, rejected/reworked worksheets and concurrent edits.

# Security, Privacy and Compliance
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC enforcement at UI and API layers; rate limiting; security headers; input validation; safe error messages; CSRF and XSS protection.
- Test SQL injection, path traversal, file-upload exploits, malware handling, oversized payloads and archive/decompression risks.
- Verify encryption at rest and in transit, secret handling, retention/deletion, access logging, masked test data and no sensitive pricing data in logs or exported error messages.
- Perform dependency scanning, SAST/DAST and penetration testing before release; track remediation and approved exceptions.

# AI and Data Quality Validation
Use a labelled golden dataset covering all supported suppliers, document types and difficult layouts. Target extraction accuracy is at least 90%, with separate measures for numeric fields, text fields, tables, multi-page documents, precision, recall and field-level completeness.
- Analyse false positives and false negatives, confidence thresholds, human-review routing and reproducibility.
- Run drift tests for supplier-format changes and new PDF layouts; define model/version traceability, rollback and reprocessing behaviour.
- Validate completeness, accuracy, consistency, uniqueness, referential integrity, currency/unit consistency and reconciliation to source totals.
- Non-Functional Testing
- Performance and scalability
- Test 1 MB, 10 MB and 50 MB PDFs, representative page counts and worksheet sizes.
- Test 10, 50 and 100 concurrent users, queue behaviour, API latency, throughput, resource utilisation and rate limits.
- Max file in Queue ?
- Validate worksheet generation and end-to-end processing against a business-approved SLA error rates.
- Test multiple suppliers, bulk upload, high transaction volume and large worksheet generation.

# Reliability and recovery
- 24-hour continuous processing, repeated uploads, service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Verify backup/restore, data reconciliation after recovery, alerting, runbooks and recovery objectives where defined.

# Accessibility and compatibility
- Screen reader labels, keyboard-only navigation, focus order, visible focus, colour contrast, error identification, zoom/reflow and accessible downloads.
- Validate current enterprise-supported versions of Edge, Chrome and Firefox at agreed desktop resolutions.

# Observability and Audit Testing (Ask)
Verify structured logs, metrics, traces, correlation IDs, dashboards and actionable alerts. Audit records must capture user, role, supplier, uploaded file identifier, processing time, extraction/model version, validation errors, approval actions, overrides and configuration changes. Confirm timestamps, immutability/access controls, retention and exportability.

# Test Data and Environment Strategy
Data category   Examples
Valid   Known Supplier A/B/C PDFs and expected golden outputs
Invalid   Corrupt, password-protected, unsupported, empty and incomplete files
Boundary   Maximum file/page sizes, large prices, long descriptions, zero/null/negative values
Security   Malicious uploads, injection strings, expired tokens and restricted-role accounts
Production-like   supplier pricing, representative volumes and realistic mappings
Maintain isolated development, QA/integration, performance and UAT environments. Version test data and expected results; reset state between runs; record build, configuration, browser, dataset and model version for every execution.
- Entry and Exit Criteria
- Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data and supplier templates available.
- Build deployed with unit-test evidence, API documentation and known limitations documented.

# Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects; residual risk formally accepted.
- AI extraction target met for the approved golden dataset, or exception approved by Product and Business.
- Performance, accessibility, audit and recovery results meet agreed thresholds.
- All UAT scenarios approved and business sign-off completed.

# Defect Management
Severity   Definition   Typical example
Critical   Pricing calculation wrong, data corruption, security breach or unrecoverable workflow failure   Approved worksheet contains materially incorrect prices
High   Core workflow blocked or major security/control failure   Users cannot upload or approve any valid worksheet
Medium   Function works with a reasonable workaround   One supplier format requires manual retry
Low   Cosmetic or low-impact usability issue   Minor alignment or wording defect
Each defect should include reproducible steps, expected/actual results, evidence, severity, environment, build, data identifiers, owner, root cause and retest result. Trend defect leakage, reopen rate, cycle time and escaped defects.

# Risks and Mitigations
Risk   Mitigation
Supplier PDF format changes   Template-based validation, contract tests, drift monitoring and rapid template rollback
OCR or AI inaccuracies   Golden dataset, confidence thresholds, human review and reconciliation checks
Poor source data quality   Validation, quarantine, exception workflow and source-owner feedback
Security exposure   Secure upload, least privilege, scanning, SAST/DAST and penetration testing
Integration failures   Mocks, contract tests, retries, timeouts, monitoring and recovery tests
Scope creep   MVP release control, prioritised backlog and formal change approval

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
Map every BRD requirement to one or more test cases and evidence items. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, extraction precision/recall, processing SLA compliance, API error rate, accessibility findings, security findings and UAT completion.

# Representative End-to-End Scenario
1.   Authenticate through Azure AD and verify the user's role.
2.   Upload a supported supplier PDF and validate file-security controls.
3.   Extract and map pricing data, retaining confidence and source traceability.
4.   Validate completeness, duplicates, thresholds and exceptions.
5.   Retrieve current pricing, compare increases/decreases and handle unmatched parts.
6.   Generate, review and export the updated pricing worksheet.
7.   Approve or reject the worksheet according to role permissions.
8.   Verify audit records, operational telemetry, notifications and final data reconciliation.
Release decision: MVP1 should not be released until the exit criteria are met or each deviation has documented impact, mitigation, owner and formal Business/Product acceptance.