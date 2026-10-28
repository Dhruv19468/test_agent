# Master Test Plan – Quote Assistant
Version: 1.0
Application: Quote Assistant
Prepared by: QA Lead, Quality Engineering
Reviewed by: Test Manager
Test phase: MVP1
Audience: Business Stakeholders, Product Owners, Architects, Development Team and QA Team
Purpose. This plan defines the quality approach for validating Quote Assistant MVP1, from RFQ intake through line extraction, catalog matching, draft quote review and export. Salesforce CPQ creation, pricing and learning from corrections are MVP2 and are not release blockers for MVP1.

## References
Quote Assistant BRD. Quote Assistant architecture diagram.

# Test Objectives
Verify extraction of customer part number, description, manufacturer, quantity and unit of measure from RFQ emails, PDF, DOCX and XLSX. Confirm product matching returns the correct catalog item as top-1 for at least 80% of lines and up to three alternatives. Validate the 70% confidence threshold, highlighting and manual review behaviour. Verify the model only proposes items that exist in the catalog index (no hallucinated items). Validate role-based access, data confidentiality, performance and Responsible AI controls.

# Scope of Testing
In scope (functional): mailbox intake; manual paste and upload; attachment parsing; line extraction with Azure OpenAI; catalog search and matching; confidence threshold; draft quote edit/add/remove; Excel export; synonym administration; nightly catalog index refresh; Azure AD SSO; RBAC; error handling.
In scope (non-functional): performance (50-line RFQ in 30 s, search under 2 s per line), security and privacy, Responsible AI, accessibility, observability, reliability and browser compatibility.

### Out of scope
- Automatic sending of quotes and order creation.
- Freight calculation and pricing engine changes.
- Salesforce CPQ integration, pricing retrieval and learning from corrections (MVP2).

# Assumptions and Dependencies
- RFQs vary from structured tables to free text and may contain customer-specific terms.
- Matching accuracy depends on catalog description quality and synonyms.
- Graph API mailbox, PIM export, Azure OpenAI and AI Search must be available or mocked.
- Inside Sales will provide a labelled RFQ test set with the correct item for each line.
- Azure OpenAI quota is sufficient for performance testing.

# Test Strategy

## Test levels
- Unit testing: developer-owned tests for attachment parsers, prompt builders, response validators, matching ranker and APIs. Target minimum coverage: 85%.
- Component testing: RFQ processing service, matching service, catalog loader function and synonym administration.
- API and contract testing: positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning.
- Integration testing: UI–backend, Graph API mailbox–processing service, backend–APIM–Azure OpenAI, backend–APIM–AI Search, Event Grid–catalog loader function, function–AI Search, backend–Cosmos DB and backend–Azure AD.
- System testing: end-to-end scenarios across RFQ intake, extraction, matching, review, edit and export.
- User acceptance testing: Inside Sales Representatives and Sales Managers validate matching quality, usability and turnaround time on real-like RFQs.

## Techniques
Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Functional Test Coverage
- RFQ intake: Email body only, PDF, DOCX, XLSX, multiple attachments, image-only PDF, password-protected file, empty RFQ, very long email thread. Verify forwarded emails are attributed to the correct representative and unsupported formats show a clear error.
- Line extraction – Extract customer part number, description, manufacturer, quantity and unit of measure for tables and free-text lines. Cover quantities in words ('two hundred'), mixed units (FT vs EA), missing quantity, duplicate lines and non-product text (signatures, disclaimers).
- Catalog matching – Verify top-1 match and up to three alternatives with confidence scores for exact item numbers, manufacturer part numbers, synonyms and free text. Lines below 70% confidence are highlighted; lines with no result show 'No match found' instead of an invented item. Verify that every proposed item exists in the current catalog index and discontinued items are not proposed.
- Draft quote: Edit quantity, choose an alternative, remove and add lines, approve the draft and export to Excel with correct columns. Verify representatives see only their own RFQs and Sales Managers see their team's RFQs.
- Administration and catalog refresh – Add, edit and delete synonyms and verify the effect on matching without redeployment. Change confidence threshold and verify highlighting; verify nightly index refresh, partial file and failed refresh handling.

# Roles & Permissions
| Role | Permitted actions | Restricted actions |
|---|---|---|
| Inside Sales Rep | Submit RFQs, review and edit matches, approve and export own drafts | Other reps' RFQs, synonyms and thresholds |
| Sales Manager | View team RFQs, drafts and match quality reports | Editing reps' drafts, administration |
| Catalog Admin | Synonyms, confidence threshold, index refresh schedule | Viewing customer RFQ content |
Verify data isolation between representatives, manager team scope, direct-URL/API access to other users' RFQs, session expiry and role changes.

# AI, Matching Quality and Responsible AI Validation
Use a labelled RFQ golden set covering structured, free-text and customer-specific RFQs. Targets: ≥80% top-1 item accuracy and ≥95% correct quantity and unit of measure.
- Measure top-1 and top-3 accuracy, precision of the confidence threshold and rate of 'No match found'.
- Run consistency tests: the same RFQ processed three times must give the same matches.
- Track prompt version, model version and index version per RFQ; re-run the golden set after every change.

# Performance, Reliability & Accessibility

## Performance and scalability
- Draft quote for a 50-line RFQ within 30 seconds; catalog search under 2 seconds per line.
- Test 20, 50 and 100 concurrent representatives and Azure OpenAI rate limits (HTTP 429 handling).
- Nightly index refresh of the full catalog completes before 06:00.

## Resilience
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility & Browser Compatibility
Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow. Current enterprise-supported versions of Edge, Chrome and Firefox.

## Security
Azure AD login, MFA, session timeout, token expiration, logout and JWT validation. RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection. Prompt-injection tests embedded in RFQ text (e.g. 'ignore previous instructions') must not change system behaviour. Verify no customer names, emails or phone numbers appear in logs, prompts stored in telemetry or exports outside the user's scope. Verify Azure OpenAI content filtering is enabled and that customer data is not retained for model training. Dependency scanning, SAST/DAST and penetration testing before release.

# Observability and Audit Testing
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, role, RFQ identifier, prompt and model version, index version, match confidence, edits made, approval and export actions. Confirm timestamps, access controls, retention and exportability.

# Environments and Test Data
- Valid: Labelled RFQs (table, free text, mixed) with correct item per line
- Invalid – Empty RFQs, unsupported files, image-only PDFs, non-product emails
- Boundary – 50-line and 51-line RFQs, confidence exactly 70%, very long descriptions
- Security – Prompt-injection text, PII-heavy emails, restricted-role accounts
- Production-like: Synthetic RFQs at weekly volume with the full catalog index
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Entry / Exit Criteria
| Entry criteria | Exit criteria |
|---|---|
| BRD approved and requirements baselined; acceptance criteria and thresholds agreed. | At least 95% of planned test cases passed, with all critical-path cases passed. |
| Environment, integrations, monitoring and access provisioned; test data available. | No open Critical defects and no open High-severity security defects. |
| Catalog index loaded and validated; labelled RFQ golden set approved by Inside Sales. | ≥80% top-1 matching and ≥95% quantity/UoM accuracy on the golden set. |
| Build deployed with unit-test evidence and known limitations documented. | No hallucinated (non-catalog) items in any test run. |
|  | No PII found in logs during log scanning. |
|  | All UAT scenarios approved and business sign-off completed. |

# Defect Severity & Process
- Critical: Definition: Wrong item proposed with high confidence, data leak or security breach; Example: Item not in catalog proposed as top match
- High – Definition: Core flow blocked; Example: Attachments cannot be processed
- Medium: Definition: Workaround exists; Example: Alternative list missing for some lines
- Low: Definition: Cosmetic; Example: Confidence badge colour wrong
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risk Register
| Risk | Mitigation |
|---|---|
| Ambiguous descriptions | Confidence threshold, alternatives, synonym management |
| Hallucinated items | Validation that every item exists in the index; negative tests |
| Prompt injection | Input sanitisation tests and system-prompt hardening |
| Model or quota limits | Rate-limit tests, retries and queueing |
| Catalog refresh failure | Index health checks and alerting |

# Traceability and Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, top-1/top-3 matching accuracy, extraction accuracy, turnaround time, Azure OpenAI error and throttling rate, accessibility and security findings and UAT completion.

# Sample E2E Flow
- Sign in with Azure AD as an Inside Sales Rep.
- Forward an RFQ email with an XLSX attachment to the sales mailbox.
- Verify extracted lines with quantity and unit of measure.
- Verify top match, alternatives and confidence per line; low-confidence lines highlighted.
- Edit a quantity, choose an alternative and add a missing line.
- Approve and export the draft quote to Excel.
- Verify audit trail, telemetry and absence of PII in logs.
Release recommendation: MVP1 should not be released until the exit criteria are met or each deviation has documented impact, mitigation, owner and formal Sales Operations/Product acceptance.