- QA Test Plan
- RMA Assistant
1.0 · RMA Assistant · QA Lead, Quality Engineering
This plan defines the quality approach for validating RMA Assistant MVP1: request intake, SAP invoice lookup, policy retrieval (RAG), eligibility recommendation with citations, restocking fee, approvals, RMA creation and customer notification. Supplier claims, customer portal, labels and analytics are MVP2.

# Quality Objectives
Verify request intake and SAP invoice lookup. Validate policy retrieval uses only active policy versions and every recommendation cites a valid clause. Verify eligibility rules (30-day window, warranty periods, non-returnable categories) and restocking fee logic. Validate approvals for exceptions and returns above USD 10,000. Validate RMA creation in SAP only after approval, notification email, security and Responsible AI controls.

# Scope
In scope (functional): web form and mailbox intake; SAP invoice lookup; policy ingestion and versioning; retrieval; recommendation with citations; eligibility and fee rules; approvals; RMA creation; email notification; Azure AD; RBAC.
In scope (non-functional): performance (recommendation 15 s, RMA 10 s), Responsible AI, security, accessibility, observability, reliability.

### Out of scope
Refunds, inventory disposition and credit memos. Supplier claims, customer portal, shipping labels and analytics (MVP2).

# Test Assumptions
- Policies vary by supplier and change over time.
- Golden decisions from coordinators available.
- SAP RMA API and SendGrid available or mocked.

# Test Strategy
| Test level | Description |
|---|---|
| Unit testing | developer-owned tests for eligibility rules, fee calculator, citation validator and APIs. Target minimum coverage: 85%. |
| Component testing | returns service, policy ingestion and indexing, recommendation component and notification service. |
| API and contract testing | positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning. |
| Integration testing | UI–returns service, Graph mailbox–returns service, returns–APIM–SAP/AI Search/Azure OpenAI, policy ingestion–Document Intelligence/AI Search/Blob, Service Bus–notification–SendGrid and Azure AD. |
| System testing | end-to-end scenarios across intake, invoice lookup, policy retrieval, recommendation, approval, RMA and notification. |
| User acceptance testing | Returns Coordinators and Managers validate recommendations, citations and approvals. |
Techniques: Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Role-Based Access and Workflow
- Returns Coordinator: Permitted actions: Review, approve within policy, create RMA; Restricted actions: Exceptions, returns above USD 10,000, policy admin
- Returns Manager: Permitted actions: Approve exceptions and high-value returns; Restricted actions: Policy administration
- Policy Admin: Permitted actions: Upload, version and retire policies; fee rules; Restricted actions: Approving returns
Verify approval thresholds, exception approvals, policy admin restrictions and audit of overrides.

# Features to be Tested
| Area | Coverage |
|---|---|
| Request intake and invoice lookup | Form and email requests, missing invoice number, invoice not found, partial quantity return, photos attached. |
| Policy ingestion and retrieval | Upload new version, retire old version; retired policy must never be cited; supplier and category filters applied. |
| Recommendation and citations | Every recommendation includes document, clause and effective date; citation text exists in the active policy; no recommendation when no policy found. |
| Eligibility and fees | Non-defective return on day 30 eligible, day 31 not eligible; custom cut cable not returnable; defective within warranty → fee waived; non-defective → 15% fee. |
| Approval, RMA and notification | Exception requires Returns Manager with reason; USD 10,000.01 requires manager; RMA created only after approval; email sent with RMA number. |

# AI, Retrieval and Responsible AI Validation
Use golden decisions from coordinators with expected citations. Targets ≥90% decision agreement and 100% valid citations from active policies.
- Retrieval recall@5 for the correct policy clause.
- Citation validity checks against source text.
- Consistency across repeated runs; version tracking for model, prompt and index.

# Non-Functional Requirements Testing

## Performance
- Recommendation within 15 seconds; RMA creation within 10 seconds; 25 and 50 concurrent users.

## Resilience
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility and compatibility
Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow. Current enterprise-supported versions of Edge, Chrome and Firefox.

## Security
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Prompt-injection text in customer requests must not change recommendations.
- Verify customer data not stored in prompts or logs.
- Dependency scanning, SAST/DAST and penetration testing before release.

# Audit and Observability
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, request identifier, invoice, policy document and version cited, recommendation, decision, approver, RMA number. Confirm timestamps, access controls, retention and exportability.

# Test Data Management
- Valid: Requests with golden decisions and citations
- Invalid: Missing invoice, unknown supplier
- Boundary: Day 30/31, USD 10,000.00/10,000.01
- Security – Injection text, restricted roles
- Production-like: Monthly volume with 300 policies indexed
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Entry and Exit Criteria
| Entry criteria | Exit criteria |
|---|---|
| BRD approved and requirements baselined; acceptance criteria and thresholds agreed. | At least 95% of planned test cases passed, with all critical-path cases passed. |
| Environment, integrations, monitoring and access provisioned; test data available. | No open Critical defects and no open High-severity security defects. |
| Policy index loaded with active and retired versions; golden decisions approved. | ≥90% decision agreement. |
| Build deployed with unit-test evidence and known limitations documented. | 100% valid citations; no retired policy cited. |
|  | Fee logic 100% correct. |
|  | No RMA without approval. |
|  | All UAT scenarios approved and business sign-off completed. |

# Defect Tracking
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong eligibility executed or retired policy cited | RMA created for non-returnable item |
| High | Flow blocked | SAP RMA creation fails |
| Medium | Workaround | Manual invoice search needed |
| Low | Cosmetic | Citation formatting |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risk Register
| Risk | Mitigation |
|---|---|
| Outdated policies | Versioning tests |
| Hallucinated terms | Citation validation |
| Ambiguous policies | Human approval and golden set |
| SAP dependency | Mocks and retries |

# Test Deliverables
Master Test Plan and Test Strategy. Requirements Traceability Matrix (RTM). Test scenarios, cases, scripts and automation report. Versioned test data and golden dataset. Defect report, daily status report and test execution report. Performance, security, accessibility and reliability test reports. UAT evidence and sign-off. Test closure report with residual risks and lessons learned.

# Test Metrics
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, decision agreement, citation validity, retrieval recall, handling time, accessibility and security findings and UAT completion.

# Schedule
MVP1: Apr–Jul 2026. MVP2: 2027. Test execution and UAT aligned to MVP1 milestones above.

# Representative End-to-End Scenario
- Customer submits a return request.
- Coordinator signs in.
- Invoice retrieved from SAP.
- Policy clauses retrieved and recommendation shown with citation.
- Fee calculated.
- Coordinator approves; RMA created in SAP.
- Customer receives email.
- Verify audit trail.

# Document Approval
| Role | Name | Signature / Date |
|---|---|---|
| QA Lead |  |  |
| Product Owner |  |  |
| Business Owner |  |  |
Go/No-Go: MVP1 should not be released until the exit criteria are met or deviations are accepted by Returns & Warranty Operations and Product.