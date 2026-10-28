# Master Test Plan – Email Order Entry
| Field | Value |
|---|---|
| Version | 0.9 |
| Application | Email Order Entry |
| Prepared by | QA Lead, Quality Engineering |
| Reviewed by | Test Manager |
| Test phase | MVP1 |
| Audience | Business Stakeholders, Product Owners, Architects, Development Team and QA Team |
Purpose: This plan defines the quality approach for validating Email Order Entry MVP1: mailbox intake, extraction, customer and item matching, SAP validation, draft order creation and CSR review. Straight-through release, acknowledgements, EDI detection and analytics are MVP2.

## References
- Email Order Entry BRD
- Email Order Entry architecture diagram

# Quality Objectives
Verify extraction of PO header and lines from email bodies, PDFs and Excel attachments. Validate customer identification and item matching via cross-reference and catalog search. Validate SAP validation rules and draft order creation without release. Verify duplicate PO detection. Validate 5-minute SLA, branch-based access and observability.

# Test Scope
In scope (functional): Graph mailbox intake; Event Grid/Service Bus processing; extraction; customer identification; item matching; SAP validation; draft order creation; review queue; cross-reference upload; Azure AD; RBAC.
In scope (non-functional): performance (95% within 5 minutes, 300 emails per hour), security, accessibility, observability, reliability.

### Out of scope
EDI orders, credit check changes, quotations and returns. Straight-through release, acknowledgements, EDI detection and analytics (MVP2).

# Test Assumptions
- PO formats vary widely by customer.
- SAP sandbox with test customers and materials available.
- Cross-reference files for pilot customers provided.

# Approach

## Levels of testing
- Unit testing: developer-owned tests for field mappers, duplicate detector, matching logic, SAP payload builder and APIs. Target minimum coverage: 85%.
- Component testing: extraction service, order creation service and review queue.
- API and contract testing: positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning.
- Integration testing: Graph mailbox–Event Grid–Service Bus, extraction–APIM–Document Intelligence/Azure OpenAI/AI Search, order creation–SAP, services–Cosmos DB/Blob and Azure AD.
- System testing: end-to-end scenarios across email receipt, extraction, matching, SAP validation, draft creation and CSR release.
- User acceptance testing: CSRs and CS Supervisors validate drafts, corrections and queue management.

## Test techniques
Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Roles & Permissions
- CSR: Permitted actions: Review, correct and release drafts for own branches; Restricted actions: Other branches, admin
- CS Supervisor – Permitted actions: Monitor and reassign queue; Restricted actions: Admin configuration
- CS Admin: Permitted actions: Mailbox routing, cross-reference upload, thresholds; Restricted actions: Releasing orders
Verify branch isolation, release only by CSRs, and admin restrictions.

# Test Coverage – Functional

## Intake and duplicates
- Single PO, multiple attachments, non-PO email, duplicate customer PO number, mailbox outage.

## Extraction
- Header (PO number, sold-to, ship-to, date) and lines (part, description, quantity, UoM, price) from body, PDF and Excel; multi-page POs.

## Customer and item matching
- Sender domain match, unknown sender, cross-reference hit, miss with catalog fallback, ambiguous item highlighted.

## SAP validation and draft
- Inactive customer, invalid material, price variance 5% (no flag) vs 5.01% (flag), draft created not released, SAP timeout retry.

## Review queue
- Branch queues, 30-minute ageing flag, correction and release, reassignment by supervisor.

# Security & Compliance Testing
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Spoofed sender domains must not be auto-identified as trusted customers.
- Prompt-injection text in emails must not alter processing.
- Dependency scanning, SAST/DAST and penetration testing before release.

# AI and Data Quality Validation
Use a labelled PO set from pilot customers. Targets ≥95% header and ≥90% line accuracy.
Field-level accuracy by format (body, PDF, Excel). Matching accuracy with and without cross-reference. Version tracking per email.

# Non-Functional Requirements Testing

## Performance and scalability
- 95% of drafts within 5 minutes; 300 emails per hour peak; queue backlog recovery.

## Reliability and recovery
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility & Browser Compatibility
Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow. Current enterprise-supported versions of Edge, Chrome and Firefox.

# Logging, Monitoring & Audit
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture email identifier, customer, PO number, extraction version, matches, SAP draft number, CSR corrections and release. Confirm timestamps, access controls, retention and exportability.

# Test Data and Environment Strategy
- Valid: Pilot customer POs with expected drafts
- Invalid: Non-PO emails, corrupt attachments
- Boundary: 5%/5.01% price variance, 29/30-minute ageing
- Security – Spoofed domains, injection text
- Production-like: Weekly email volume
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Entry and Exit Criteria

## Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data available.
- SAP sandbox data and pilot cross-references loaded.
- Build deployed with unit-test evidence and known limitations documented.

## Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects.
- Accuracy targets met.
- 100% duplicate detection.
- No release without CSR action.
- SLA met.
- All UAT scenarios approved and business sign-off completed.

# Defect Management
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong customer or material on order | Order drafted for wrong ship-to |
| High | Drafts not created | SAP integration failure |
| Medium | Workaround | Excel PO needs manual lines |
| Low | Cosmetic | Queue sort order |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risks and Mitigations
| Risk | Mitigation |
|---|---|
| Format variety | Golden set and review |
| Spoofing | Security tests |
| SAP limits | Load tests and retry |
| Missing cross-references | Fallback tests |

# Test Deliverables
Master Test Plan and Test Strategy. Requirements Traceability Matrix (RTM). Test scenarios, cases, scripts and automation report. Versioned test data and golden dataset. Defect report, daily status report and test execution report. Performance, security, accessibility and reliability test reports. UAT evidence and sign-off. Test closure report with residual risks and lessons learned.

# Traceability and Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, field accuracy, draft SLA compliance, correction rate, SAP error rate, accessibility and security findings and UAT completion.

# Sample E2E Flow
- PO email arrives in branch mailbox.
- Event triggers processing.
- Header and lines extracted.
- Customer and items matched.
- SAP validation and draft creation.
- CSR reviews and releases.
- Verify trace and audit.
Release decision: MVP1 should not be released until the exit criteria are met or deviations are accepted by Customer Service Operations and Product.