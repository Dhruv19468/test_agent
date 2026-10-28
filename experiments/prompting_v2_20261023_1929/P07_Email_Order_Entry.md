# 1. Document Control
- Title: Master Test Plan — Email Purchase Order Entry Automation (MVP1)
- Version: 1.0
- Application: Email Purchase Order Entry Automation (MVP1)
- Prepared by: Senior QA Lead (prepared/reviewed by QA team)
- Reviewed by: Business Owner (Customer Service Operations), Architects, QA Team (TBD – confirm with Business Owner list for signature)
- Audience: Customer Service Operations, CS Admin, CS Supervisor, CSR representatives, Integration/SAP team, Architects, AI Governance Council
- Purpose: Define the test approach, scope, coverage and exit criteria needed to validate MVP1 meets the BRD and architecture requirements for converting PO emails to SAP draft orders for CSR review.

# 2. References
- BRD: "Business Requirements Document (BRD) – Email Purchase Order Entry Automation", Version 1.0, Date 02 Mar 2026.
- Architecture: "Email Purchase Order Entry Automation - Solution Architecture (Non-production)" (architecture text provided, including connection lines and environment notes).
- Appendix materials referenced in BRD: "Email Order Entry MVP1 Scope Overview", "P07_Email_Order_Entry_Architecture.png" (diagram referenced in BRD) — (TBD – confirm with Architecture owner for file locations).

# 3. Test Objectives
- Prove the system converts PO emails into SAP draft sales orders per MVP1 scope, preserving CSR review for every order.
- Demonstrate measurable achievement of business objectives and acceptance criteria from the BRD:
  - Create SAP draft orders within 5 minutes of email receipt for 95% of POs.
  - Achieve ≥95% header field accuracy and ≥90% line accuracy on pilot customers.
  - Detect duplicate POs by customer PO number 100% in test set.
  - Ensure no orders are released without CSR action in MVP1.
  - Validate price variance rule: price variance >5% is flagged.
- Verify NFR targets: Availability 99.5% 24x5, peak handling 300 emails per hour, end-to-end traceability per email to SAP draft order number.
- Verify role-based access, segregation of duties and branch-based queue access.
- Validate integrations and data flows per architecture (protocol/auth and purpose).
- Validate AI extraction, confidence scoring, fallback logic and controls against hallucination; verify CS Admin upload and confidence threshold behavior.
- Verify quality checks: mandatory header fields present; line quantity > 0; UoM valid in SAP.

# 4. In Scope
All items below are in scope for MVP1 only (per BRD):

- PO intake from branch order mailboxes via Microsoft Graph (branch mailboxes -> Event Grid -> Service Bus -> Order Extraction Service path).
- Duplicate PO detection by customer PO number.
- Extraction of:
  - Customer PO number
  - Sold-to
  - Ship-to
  - Requested delivery date
  - Lines: customer part, description, quantity, UoM, price
  Using Azure Document Intelligence and Azure OpenAI (as the BRD specifies).
- Customer identification by sender domain and PO content.
- Item matching via:
  - Customer cross-reference table (CS Admin upload, monthly)
  - Catalog search (Azure AI Search fallback)
- SAP validation via APIM:
  - Customer active
  - Material valid
  - Price variance >5% flagged
- Creation of a draft sales order in SAP (not released).
- CSR review queue (Web UI) with:
  - Per-field confidence displayed
  - Highlighting lines where customer part number has no cross-reference
  - CSR correction capability and release action (release action exists but release must not be used to auto-release in MVP1; CSRs will perform manual release in SAP)
- Observability requirement: end-to-end trace per email to SAP draft order number.
- Data stores: Blob Storage for emails, Cosmos DB for order drafts.
- Flow and integration paths listed in the architecture connections (validated end-to-end).

# 5. Out of Scope
Explicitly excluded items (BRD MVP2 items and BRD "Exclusions"):
- Straight-through release for trusted customers (MVP2) — out of scope.
- Order acknowledgement emails (MVP2) — out of scope.
- EDI detection and handling (MVP2 and BRD Exclusions) — out of scope.
- Analytics (MVP2) — out of scope.
- Changes to credit checks, quotations, returns — out of scope.
- Any automatic release of orders without CSR action (BRD: No orders released without CSR action in MVP1).

# 6. Assumptions and Dependencies
Assumptions (from BRD):
- Customers send one PO per email in most cases.
- Cross-reference files exist for top 200 customers.
- CS branches will participate in UAT (BRD: dependencies list includes CS branches for UAT).
Dependencies (test execution depends on the following teams/resources):
- SAP integration team to provide test sandbox endpoints and APIM contracts.
- Mailbox access approval for branch mailboxes (Graph API) for test mailboxes.
- CS Admin to provide cross-reference upload capability and sample files (frequency: Monthly).
- Availability of the non-production subscription architecture (APIM, Document Intelligence, OpenAI, AI Search, Event Grid, Service Bus, Blob Storage, Cosmos DB).
- AI Governance Council approval for AI models and usage (as required by BRD).
- Observability/monitoring services available as per architecture (Datadog, Azure Monitor) — where monitoring configuration is required (TBD – confirm with Architecture owner).
Test constraints:
- Test environment is the Non-production Subscription as described in architecture (non-prod labelled). If additional environments required (e.g., dedicated UAT or performance test environment), specify: TBD – confirm with <owner>.

# 7. Test Strategy
Approach:
- Risk-based testing focusing on MVP1 functional requirements, high-risk integrations (Graph API, APIM to SAP), AI extraction accuracy and NFR targets.
- Validate both positive and negative cases, edge cases and failure/retry scenarios.
Test levels:
- Unit testing (by devs) — verify service logic and handlers (coverage is a dev responsibility; QA will review unit test reports) — test harness TBD – confirm with Dev Lead.
- Integration testing — validate message flows: Graph API -> Event Grid -> Service Bus -> Order Extraction Service -> Blob Storage/Cosmos DB -> Order Creation Service -> APIM -> SAP.
- System testing — end-to-end tests from email receipt to draft order creation and CSR queue behaviour.
- Regression testing — in each build.
- User Acceptance Testing (UAT) — with CS branches (BRD dependency).
Test types:
- Functional tests (requirements & user stories).
- Integration tests (per architecture connections).
- Data validation tests (mandatory header, line quantity >0, UoM validation).
- AI accuracy tests (header and line accuracy, per-field confidence thresholds, duplicate detection).
- Security tests (Azure AD auth, RBAC, branch-based queue access).
- Performance/load tests (peak 300 emails/hour; 95% within 5 minutes).
- Reliability/failure/recovery tests (APIM/SAP API limits, queuing, retry).
- Observability tests (end-to-end traceability).
- Accessibility/compatibility tests for Web UI (TBD – confirm supported browsers and devices with UX owner).
Techniques:
- Test case design using requirement-based, boundary value, equivalence class, error guessing for layout variability.
- Use of synthetic test emails and attachments representing common and unusual PO layouts (TBD – sample dataset and generation rules to be confirmed with Business Owner and CS Admin).
Test tooling:
- Test management, automation, and defect tools: TBD – confirm with <owner>. (Do not invent tools.)

# 8. Functional Test Coverage
For every MVP1 functional requirement and sample user story in BRD, tests will verify the items below.

- PO intake via Microsoft Graph
  - Verify Event Grid receives new mail events from Branch Mailboxes (Graph API -> Event Grid).
  - Verify Event Grid -> Service Bus event forwarding.
  - Verify Order Extraction Service consumes messages from Service Bus.
  - Verify email copy stored to Azure Blob Storage.
  - Verify duplicate PO detection by customer PO number (100% detection in provided test set).
  - Tests:
    - New mail positive path (single PO per email).
    - Duplicate email (same customer PO number) flagged and not duplicated in draft orders.
    - Multi-attachment emails (PDF/Excel) processed; attachment handling errors flagged.

- Extraction of header and lines (Azure Document Intelligence + Azure OpenAI)
  - Verify extraction of customer PO number, sold-to, ship-to, requested delivery date.
  - Verify extraction of lines: customer part, description, quantity, UoM, price.
  - Verify field-level confidence is returned and persisted with draft orders.
  - Verify mandatory header fields presence validation.
  - Verify line quantity > 0 enforcement.
  - Verify UoM validation against SAP master data.
  - Tests:
    - Clean, well-structured PO layouts.
    - Unusual PO layouts (BRD risk) — ensure CSR review and confidence flags.
    - Partial extractions (missing fields) — ensure draft flagged and CSR notified.
    - Field-level confidence thresholds exercised (see AI tests).

- Customer identification
  - Verify identification by sender domain and PO content.
  - Negative tests where sender domain ambiguous: ensure fallback paths and CSR-visible flags.

- Item matching
  - Verify matching via customer cross-reference table first (CS Admin uploads).
  - Verify fallback to catalog search via Azure AI Search (APIM -> Azure AI Search connection).
  - Verify lines where no customer part cross-reference exist are highlighted to CSR.
  - Tests:
    - Cross-reference match success.
    - Cross-reference missing -> catalog search success.
    - No match -> flagged for CSR.

- SAP validation via APIM
  - Verify APIM calls to SAP for:
    - Customer active check
    - Material validity
    - Price comparison and flagging where variance >5%
  - Verify draft creation in SAP (Order Creation Service -> SAP S/4HANA via APIM).
  - Verify draft orders are not released (no automatic release).
  - Tests:
    - Valid master data: draft created successfully.
    - Invalid customer/material: appropriate error/queue flagging.
    - Price variance >5%: flagged in draft and visible to CSR.

- CSR review queue and Web UI
  - Verify draft orders appear in Web UI queue (Order Creation Service -> Cosmos DB -> Web UI).
  - Verify CSRs see per-field confidence and can correct fields.
  - Verify lines with missing cross-reference are highlighted.
  - Verify CS Supervisors see orders older than 30 minutes flagged (user story).
  - Verify CS Admin can upload a customer cross-reference file (upload action and effect).
  - Verify branch-based queue access (CSR sees only their branch queue).
  - Tests:
    - CSR correction flows and subsequent draft update.
    - Reassign orders (CS Supervisor capability).
    - CS Admin upload: new cross-reference applies to subsequent processing (or re-match behavior to be confirmed: TBD – confirm with CS Admin).

- Observability & logs
  - Verify end-to-end trace per email to SAP draft order number.
  - Verify logging for: emails processed, draft accuracy metrics, CSR correction rate, time to draft (BRD logging items). Note: Monitoring specifics pending SME review (BRD: TBD – pending SME review).

# 9. Roles, Permissions and Workflow Testing
Roles defined in BRD:
- CSR
- CS Supervisor
- CS Admin

RBAC and workflows to test (based on BRD and architecture):
- Authentication: Azure AD (Entra ID) SSO for CSR Users and Admin Users via App Gateway (CSR Users -> App Gateway | HTTPS/443 AD/SSO; Admin Users similar).
- Verify branch-based queue access:
  - CSR can only view and act on draft orders for their branch (RBAC enforcement).
- Verify CS Supervisor capabilities:
  - Monitor queue and SLAs.
  - Reassign orders.
  - Verify orders older than 30 minutes are flagged and visible to Supervisor (user story).
- Verify CS Admin capabilities:
  - Upload customer cross-reference files (monthly frequency).
  - Maintain mailbox routing and confidence thresholds (BRD lists CS Admin responsibilities).
  - Tests:
    - Upload valid and invalid cross-reference files.
    - Verify permission checks: only CS Admin role can upload.
- Segregation of duties:
  - Ensure CS Admin cannot impersonate CSR to release orders.
  - Ensure no user can release an order automatically in MVP1; release action remains an explicit CSR action in SAP (test that the application does not auto-release).

Authentication/authorization integration tests:
- Azure AD -> App Gateway -> APIM paths: validate SSO/OAuth flows (where applicable).
- Verify that only authenticated users can access the Web UI and that their role restricts UI actions.

# 10. Security, Privacy and Compliance Testing
- Authentication and Authorization
  - Test Azure AD SSO for CSR and Admin users.
  - Validate token expiry and error handling.
  - Verify branch-based access restrictions and RBAC enforcement.

- Data protection and confidentiality
  - Verify PO emails and attachments stored in Blob Storage with appropriate access controls (as per architecture).
  - Verify Cosmos DB draft orders access controls.
  - Validate that customer data is handled as "Confidential" per BRD and access logs are generated.

- Secrets and service identities
  - Validate managed identity or Key Vault usage where applicable (architecture includes Key Vault). Exact secrets configuration: TBD – confirm with Security owner.

- AI Governance & Responsible AI
  - Validate AI Governance Council approval is captured for model usage (BRD states approval required).
  - Tests for controls against hallucination: ensure AI outputs are bounded to extraction tasks, confidence values are persisted, and unknown mappings are flagged (see AI tests).
- Compliance
  - Ensure audit trail for who reviewed/changed a draft order (CSR actions) is recorded.
  - Verify retention and deletion policies for emails and drafts (TBD – confirm retention policy with Compliance owner).

# 11. AI and Data Quality Validation
AI components (from BRD and architecture):
- Azure Document Intelligence (APIM -> Azure Document Intelligence | extract)
- Azure OpenAI (APIM -> Azure OpenAI | map fields)
- Azure AI Search (APIM -> Azure AI Search | item search)

Validation objectives:
- Extraction accuracy targets:
  - Header field accuracy ≥95% (acceptance criteria).
  - Line accuracy ≥90% (acceptance criteria).
  - Tests will be executed on pilot customers per BRD acceptance criteria.
- Confidence thresholds and CS Admin controls:
  - Verify per-field confidence values are displayed to CSR.
  - Verify CS Admin can upload/maintain confidence thresholds (BRD role).
  - Behavior when confidence below threshold: ensure field is flagged and CSR review required.
- Hallucination and incorrect mapping controls:
  - Ensure Azure OpenAI output is validated against SAP master data and cross-reference/catalog results.
  - Verify that mappings which cannot be confirmed by cross-reference/catalog/SAP are flagged and not auto-applied.
  - Validate that any AI-suggested material ID is confirmed against SAP material validity before draft creation (APIM SAP validation).
- Duplicate detection:
  - Validate duplicate PO logic by customer PO number with test set (100% detection requirement in test set).
- Test datasets and measurement:
  - Use a representative pilot dataset of emails (TBD – confirm dataset and pilot customer list with Business Owner).
  - Measure and report header and line accuracy, precision/recall where applicable.
- Re-train/re-config triggers:
  - Validate how corrections by CSRs feed back to model/data (TBD – confirm with ML owner if corrections stored for future model improvement).

# 12. Performance Testing
NFR and performance targets (BRD exact values must be met):
- Draft order created within 5 minutes of email receipt for 95% of POs.
- Peak capacity: 300 emails per hour.
- Availability: 99.5% 24x5.

Performance test plan:
- Load tests to simulate sustained 300 emails/hour and spike tests above peak to observe throttling and queueing behavior (exact spike levels and tooling: TBD – confirm with Performance owner).
- End-to-end timing measurements:
  - Measure time from Event Grid new mail to draft order creation in SAP for each test email.
  - Validate 95% within 5 minutes target.
- SAP API limit and queueing behavior:
  - Test APIM/SAP failure modes and backlog handling via Service Bus retries and queueing (BRD mentions SAP API limits mitigation).
- Availability validation:
  - Verify application components meet 99.5% 24x5 in non-prod monitoring (test SLAs and simulate failures to verify failover where applicable). Specific monitoring thresholds and checks: TBD – confirm with Operations owner.
- Test data volumes:
  - Use realistic email sizes and attachment types (PDF, Excel). Dataset creation: TBD – confirm with CS Admin/Business Owner.

# 13. Reliability and Recovery Testing
- Retry and queue handling:
  - Validate Service Bus retry logic from Order Extraction Service and Order Creation Service.
  - Simulate temporary SAP/APIM outage and verify messages are retried/queued without data loss.
- Error handling:
  - Verify failed extraction, failed matching, or failed SAP validation produce clear flags in the CSR queue and do not create invalid drafts.
- Observability for failures:
  - Ensure end-to-end trace can be used to troubleshoot failed orders to the specific failing component.
- Disaster recovery:
  - Non-prod environment DR behaviour: TBD – confirm with Infrastructure/Architecture owner for recovery SLAs and test hooks.

# 14. Accessibility and Compatibility Testing
- Web UI compatibility:
  - Supported browsers/devices are not specified in BRD — testing of Web UI compatibility: TBD – confirm supported browsers/devices with UX/Front-end owner.
- Accessibility:
  - No accessibility requirements specified in BRD — validate basic keyboard navigation and screen reader behaviour if required: TBD – confirm with Accessibility owner.

# 15. Logging, Monitoring and Audit Testing
BRD logging items: emails processed, draft accuracy, CSR correction rate, time to draft (with "TBD – pending SME review").

Tests:
- Verify logging exists for:
  - New mail received and Event Grid event ID.
  - Service Bus message ID and processing status.
  - Extraction results with field-level confidence.
  - Cross-reference and catalog match results.
  - SAP validation responses and draft order number (end-to-end trace).
  - CSR corrections and user ID who performed changes.
  - Time-to-draft metric per email.
- Verify monitoring/alerts:
  - Alerts for processing backlogs, failures, and orders >30 minutes in queue (Supervisor user story).
  - Integrations with Datadog/Azure Monitor are configured (architecture lists these supporting services) — verification of configurations: TBD – confirm with Monitoring owner.
- Audit trail:
  - Verify immutable audit entries for create/update actions on drafts and CSR releases (even though releases must be manual in SAP).

# 16. Test Environments and Test Data
Test environments:
- Primary test environment: Non-production Subscription as described in architecture (APIM, Azure Document Intelligence, Azure OpenAI, Azure AI Search, Event Grid, Service Bus, Blob Storage, Cosmos DB, Shared AKS Non-prod).
- Shared services: Azure AD and App Gateway in Shared Services Subscription (per architecture).
- SAP test endpoints: TBD – confirm with SAP integration team for sandbox endpoints and credentials.
- Environment readiness and access: TBD – confirm with Infrastructure and Security owners.

Test data:
- PO email samples (PDF and Excel) representing:
  - Typical POs (clean structured)
  - Unusual layouts (risk in BRD)
  - Missing header fields
  - Multiple attachments
  - Duplicate PO numbers
- Cross-reference files:
  - Representative files for top 200 customers (BRD states these exist). CS Admin to provide.
- SAP master data:
  - Test customers, materials and price data for validation tests (TBD – confirm with SAP integration team).
- Data classification:
  - All test data treated as Confidential per BRD.
- Test data preparation and ownership:
  - Create synthetic test emails where necessary; dataset specification and generation: TBD – confirm with Business Owner and CS Admin.

# 17. Entry, Suspension and Exit Criteria
Entry criteria (for system test / UAT):
- Development build deployed to Non-production Subscription with integrations reachable.
- Mailbox access for test branch mailboxes configured (Graph API).
- APIM endpoints to AI services and SAP stub/sandbox available.
- CS Admin cross-reference upload functionality available.
- Test data set prepared and accessible.
- Test environment sign-off by Architecture/Infra owner: TBD – confirm with owner.

Suspension criteria:
- Critical/blocker defects preventing end-to-end processing of emails to draft orders.
- Unavailable dependent systems (Graph API, Service Bus, APIM to SAP) for > agreed time window (TBD – confirm acceptable downtime with stakeholders).
- Security incidents impacting test data or environment.

Exit criteria:
- All critical and high defects resolved or accepted by Business Owner.
- Acceptance criteria met as per BRD:
  - ≥95% header field accuracy and ≥90% line accuracy on pilot customers.
  - Draft within 5 minutes for 95% of POs.
  - No orders released without CSR action in MVP1.
  - Duplicate POs detected 100% in test set.
- Successful UAT sign-off by Business Owner/CS stakeholders.
- Test reports and metrics published.

# 18. Defect Management
- Defect severity definitions: (align to enterprise standard where available — if not available, TBD – confirm with QA/PM owner).
- Defect tracking tool: TBD – confirm with <owner>.
- Triage process:
  - Daily triage for P1/P2 defects during test windows; P3/P4 weekly.
  - Owners for fix and retest to be assigned: Development, Integration/SAP, AI/ML, CS Admin as applicable.
- Defect SLA targets: TBD – confirm with Program Manager.

# 19. Risks and Mitigations
Risks (from BRD and architecture) and mitigations:

- Unusual PO layouts (BRD risk)
  - Mitigation: CSR review and confidence flags; include diverse layouts in test dataset.

- Missing cross-references (BRD risk)
  - Mitigation: Catalog search fallback via Azure AI Search; highlight to CSR.

- SAP API limits (BRD risk)
  - Mitigation: Queueing via Service Bus and retry policies; test API throttling and queue behavior.

- AI hallucination / incorrect mappings
  - Mitigation: Validate AI outputs against cross-reference/catalog and SAP; flag low confidence; AI Governance Council oversight.

- Mailbox access approval delays (Dependency)
  - Mitigation: Early coordination with mailbox owners; use dedicated test mailboxes if needed.

- Observability gaps (BRD: logging pending SME)
  - Mitigation: Confirm logging/monitoring requirements early (TBD – confirm with SME) and include test hooks.

- Test environment readiness delays
  - Mitigation: Validate environment availability early; escalate blockers.

# 20. Test Deliverables and Reporting
Deliverables:
- Test plan (this document).
- Test cases and traceability matrix (requirement-to-test mapping) — created in test management tool (TBD – confirm tool).
- Test data sets (PO emails, cross-reference files, SAP master data stubs).
- Test execution reports (daily/weekly).
- Defect logs and triage minutes.
- Performance test reports and timing metrics (95% within 5 minutes measurement).
- AI accuracy reports (header ≥95%, line ≥90% for pilot customers).
- UAT sign-off document.

Reporting cadence:
- Daily status during system test and UAT (TBD – confirm stakeholders).
- Weekly executive summary (TBD – confirm recipients).

# 21. Traceability and Metrics
- Requirement-to-test traceability:
  - All BRD MVP1 functional requirements, user stories and acceptance criteria will be mapped to test cases. (Detailed matrix to be produced in test management tool — TBD – confirm tool).
- Key test metrics/KPIs to report:
  - Header field accuracy (%)
  - Line accuracy (%)
  - Time-to-draft distribution and % ≤5 minutes
  - Duplicate detection success rate (test set)
  - CSR correction rate and most-corrected fields
  - Number/severity of defects by test phase
  - Throughput (emails/hour processed)
  - Availability percentage observed in test windows (against 99.5% 24x5)
- Reporting: metrics included in test execution reports and UAT dashboard (tooling TBD).

# 22. Test Schedule
High-level timeline (from BRD):
- MVP1: Apr–Jul 2026 (BRD High-Level Plan).
Detailed test phase dates and milestones:
- Test phase dates, environment deployment windows, regression windows, UAT start/end and go/no-go reviews: TBD – confirm with Program Manager and Project Plan owners.
- Performance testing and pilot customer validation to be scheduled within MVP1 timeframe (Apr–Jul 2026) in coordination with CS branches and SAP integration team.

# 23. End-to-End Scenario
Representative E2E scenario to validate core flow (one or more will be used in test runs):

Scenario A — Standard PO email (happy path)
- Pre-conditions:
  - Test branch mailbox configured; SAP sandbox available with active customer and materials.
  - Cross-reference file uploaded for the customer.
- Steps:
  1. Send test email (single PO per email) with PDF attachment containing header and lines.
  2. Branch Mailbox (Graph API) triggers Event Grid event.
  3. Event Grid forwards event to Service Bus.
  4. Order Extraction Service consumes queue message, copies email to Blob Storage and submits extracted PO (via APIM) to Order Creation Service.
  5. Extraction uses Azure Document Intelligence and Azure OpenAI to extract fields and returns per-field confidence.
  6. Item matching: cross-reference lookup succeeds; if not, catalog search via Azure AI Search is invoked.
  7. APIM calls SAP validation (customer active, material valid, price check). Price variance <=5% so not flagged.
  8. Draft sales order created in SAP (Order Creation Service -> SAP via APIM) as draft (not released).
  9. Draft entry persisted in Cosmos DB and surfaced in Web UI for CSR review, with per-field confidence and match details.
  10. CSR reviews, makes no changes, records action; audit trail captured.
- Expected results:
  - Draft created in SAP within 5 minutes (95% target across tests).
  - Field accuracy meets header and line acceptance criteria for pilot customers.
  - End-to-end traceability exists linking email -> event ID -> Service Bus message -> draft order number.

Other E2E scenarios (to be executed):
- Duplicate PO detection scenario.
- Extraction failure / low-confidence scenario requiring CSR correction.
- Price variance >5% flagged scenario.
- SAP unavailable -> queued and retried scenario.
- Cross-reference missing -> catalog search fallback scenario.

# 24. Approvals
Required approvals prior to production promotion (MVP1):
- Business Owner: Customer Service Operations (acceptance and UAT sign-off).
- Architecture owner (non-prod environment sign-off).
- SAP Integration owner (validation of APIM contracts and sandbox).
- AI Governance Council (approval for AI model usage).
- QA Lead (test exit criteria met).
- Operations / Monitoring owner (observability and alerts sign-off).
Note: Approval names and sign-off process: TBD – confirm with Program Manager and Governance owners.

Appendix / Action Items (TBD confirmations)
- Confirm file locations for architecture diagram P07_Email_Order_Entry_Architecture.png with Architecture owner.
- Confirm test management and defect tracking tools with Program Manager.
- Confirm test data set and pilot customer list with Business Owner and CS Admin.
- Confirm monitoring/alert configuration and ownership with Monitoring owner.
- Confirm supported browsers/devices for Web UI compatibility with UX owner.
- Confirm retention policy and compliance requirements with Compliance owner.
- Confirm environment readiness dates and SAP sandbox endpoints with SAP integration team.

End of Master Test Plan — MVP1 (Email Purchase Order Entry Automation)