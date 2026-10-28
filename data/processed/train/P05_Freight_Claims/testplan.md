# QA Test Plan – Freight Claims Automation
1.1 · Freight Claims Automation · QA Lead, Quality Engineering
Purpose: This plan defines the quality approach for validating Freight Claims Automation MVP1: shipment lookup, evidence upload, AI damage description, claim value and deadline calculation, approval, packet generation and carrier email. Carrier APIs, status tracking, recovery reporting and finance posting are MVP2.

## References
- Freight Claims Automation BRD
- Freight Claims Automation architecture diagram

# Objectives
- Verify shipment lookup by PRO/BOL and pre-fill from TMS and ERP.
- Validate evidence rules per claim type and upload limits.
- Verify claim value calculation and deadline/late-claim warnings are 100% correct.
- Validate AI damage description quality and editability.
- Validate approval above USD 5,000, packet generation, carrier email and branch-scoped access.

# Scope
In scope (functional): shipment lookup; claim form; evidence upload; AI damage description; claim value calculation; deadline rules; approval; packet PDF; carrier email; claims register; carrier administration; Azure AD; RBAC.
In scope (non-functional): performance (lookup 3 s, description 20 s, packet 10 s), tablet usability, security, accessibility, observability and reliability.

### Out of scope
- Customer portal, litigation and insurance claims.
- Carrier API submission, status tracking, recovery reporting and finance posting (MVP2).

# Quality Risks, Assumptions and Dependencies
- Photos may be blurry, dark or unrelated.
- TMS and ERP APIs available in non-production or mocked.
- Carrier deadline rules provided by Transportation.

# Test Approach
| Test level | Description |
|---|---|
| Unit testing | developer-owned tests for claim value calculator, deadline rules, evidence validator and APIs. Target minimum coverage: 85%. |
| Component testing | claims service, packet service, email function and AI description component. |
| API and contract testing | positive and negative behaviour, schemas, authentication, error codes, idempotency and versioning. |
| Integration testing | UI–claims service, claims service–APIM–TMS/ERP/Azure OpenAI, claims–Blob/PostgreSQL, Service Bus–packet service, Function–SendGrid and Azure AD. |
| System testing | end-to-end scenarios across lookup, evidence, description, calculation, approval, packet and email. |
| User acceptance testing | Branch Users and Claims Specialists validate the claim flow on tablets and desktops. |
Techniques: Use requirements-based testing, equivalence partitioning, boundary-value analysis, pairwise coverage, negative testing, exploratory testing, risk-based prioritisation, regression testing and data-driven automation.

# Functional Testing
- Shipment lookup: Valid PRO, valid BOL, unknown number, multiple matches, TMS timeout with manual entry fallback.
- Evidence upload: Up to 10 photos JPG/PNG ≤10 MB; 11th photo blocked; HEIC rejected; PDFs for documents; mandatory evidence per claim type.
- AI damage description: Description reflects visible damage, is editable, and states 'unable to determine' for unclear photos rather than inventing damage.
- Claim value and deadlines: 3 damaged units × USD 45.20 = USD 135.60 plus freight where applicable; rounding to 2 decimals. Concealed damage on day 5 → no warning; day 6 → warning; carrier 9-month deadline enforced.
- Approval, packet and email: Claims above USD 5,000 require Claims Specialist approval; USD 5,000.00 exactly does not. Packet PDF contains form, photos and documents; email sent to correct carrier address; status updates in register.

# Access Control Testing
- Branch User – Permitted actions: Create and submit own branch claims; Restricted actions: Other branches, approvals, admin
- Claims Specialist – Permitted actions: Approve above USD 5,000, follow up, close; Restricted actions: Carrier configuration
- Logistics Admin: Permitted actions: Carriers, deadlines, templates; Restricted actions: Approving claims
Verify branch isolation, approval enforcement, direct-URL access and session expiry on shared tablets.

# AI and Data Quality Validation
Use a labelled photo set with expected damage descriptions. Target: users rate ≥85% of descriptions acceptable; 0% invented damage on 'no damage' photos.
Human rating of description quality. Negative tests with unrelated photos. Model and prompt version tracked per claim.

# NFR Testing

## Performance and scalability
Lookup within 3 seconds; description within 20 seconds for 10 photos; packet within 10 seconds. 25 and 50 concurrent users.

## Reliability and recovery
- Service restart during processing, network interruption, dependency failure, retry/idempotency and recovery from partial failure.
- Backup/restore, data reconciliation after recovery, alerting and runbooks.

## Accessibility & Browser Compatibility
- Screen reader labels, keyboard-only navigation, focus order, colour contrast, error identification and zoom/reflow.
- Current enterprise-supported versions of Edge, Chrome and Firefox.
- Validate responsive layout on supported tablets and touch interaction.

## Security
- Azure AD login, MFA, session timeout, token expiration, logout and JWT validation.
- RBAC at UI and API layers; rate limiting; input validation; safe error messages; CSRF and XSS protection.
- Test image files with embedded scripts and EXIF data stripping.
- Verify unit cost is not exposed in carrier emails beyond the claim total.
- Dependency scanning, SAST/DAST and penetration testing before release.

# Audit and Observability
Verify structured logs, metrics, traces, correlation IDs, dashboards and alerts. Audit records must capture user, branch, claim identifier, PRO/BOL, claim value, approval, packet and email events, model version. Confirm timestamps, access controls, retention and exportability.

# Test Data and Environment Strategy
- Valid: Shipments with damaged and short deliveries, labelled photos
- Invalid: Unknown PRO, HEIC files, oversized photos
- Boundary – Day 5/6 concealed damage, USD 5,000.00/5,000.01, 10/11 photos
- Security: Malicious images, restricted roles
- Production-like – Monthly claim volume with masked costs
Isolated development, QA/integration, performance and UAT environments; versioned test data and expected results; record build, configuration, dataset and model version for every execution.

# Suspension, Entry and Exit Criteria

## Entry criteria
- BRD approved and requirements baselined; acceptance criteria and thresholds agreed.
- Environment, integrations, monitoring and access provisioned; test data available.
- TMS/ERP test data or mocks available; carrier rules configured.
- Build deployed with unit-test evidence and known limitations documented.

## Exit criteria
- At least 95% of planned test cases passed, with all critical-path cases passed.
- No open Critical defects and no open High-severity security defects.
- Claim value and deadline rules 100% correct.
- ≥85% description acceptance in UAT.
- Performance targets met.
- All UAT scenarios approved and business sign-off completed.

# Defect Tracking
| Severity | Definition | Example |
|---|---|---|
| Critical | Wrong claim value or wrong carrier | Packet sent to wrong carrier |
| High | Claim cannot be submitted | Upload fails for all photos |
| Medium | Workaround | Lookup needs manual entry for one carrier |
| Low | Cosmetic | Tablet button spacing |
Each defect includes steps, expected/actual results, evidence, severity, environment, build, owner and retest result.

# Risk Register
| Risk | Mitigation |
|---|---|
| Poor photos | Negative tests and editable description |
| API gaps | Fallback tests |
| Rule errors | Boundary tests |
| Data exposure | Email content tests |

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
Map every BRD requirement to test cases and evidence. Report weekly planned/executed/passed/failed/blocked cases, coverage by requirement and risk, defect severity and ageing, evidence completeness, calculation accuracy, description acceptance, packet success rate, accessibility and security findings and UAT completion.

# Schedule
- MVP1: Apr–Jun 2026
- MVP2: Q4 2026
- Test execution and UAT aligned to MVP1 milestones above.

# Representative End-to-End Scenario
- Sign in as Branch User on a tablet.
- Look up a shipment by PRO.
- Upload photos and documents.
- Review the AI description.
- Verify claim value and deadline.
- Route to Claims Specialist for approval above USD 5,000.
- Generate the packet and email the carrier.
- Verify register and audit trail.

# Sign-off
| Role | Name | Signature / Date |
|---|---|---|
| QA Lead |  |  |
| Product Owner |  |  |
| Business Owner |  |  |
Go/No-Go: MVP1 should not be released until the exit criteria are met or deviations are accepted by Logistics and Product.