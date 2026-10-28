# 1. Document Control
- Title: QA Test Plan  
- Version: 1.0  
- Application: Email Purchase Order Entry Automation  
- Prepared by: QA Lead, Quality Engineering (Customer Service Operations program)  
- Reviewed by: Test Manager, Architects, Product Owner, Customer Service Operations stakeholders  
- Audience: Customer Service Operations, Architects, Development, QA, CS branches, CS Admins  
- Purpose: Define the quality approach and acceptance criteria to validate Email Purchase Order Entry Automation MVP1: mailbox intake, extraction from email body and PDF/Excel attachments, customer/ship-to identification, item matching (cross-reference + catalog), SAP validation, draft sales order creation, CSR review queue and duplicate PO detection. MVP2 capabilities are documented as Out of Scope and will not block MVP1 acceptance unless Product approves otherwise.

# 2. References
- Email Purchase Order Entry Automation BRD (Version 1.0, 02 Mar 2026)  
- Email Purchase Order Entry Architecture diagram (P07_Email_Order_Entry_Architecture.png)

# 3. Test Objectives
- Verify extraction of required fields from email body and attachments: customer PO number, sold-to, ship-to, requested delivery date, lines (customer part, description, quantity, UoM, price) and per-field confidence values.  
- Verify correct customer identification by sender domain and PO content.  
- Verify item matching: customer cross-reference lookup then Azure AI Search catalog fallback.  
- Verify SAP validation via APIM: customer active, material valid, price variance >5% flagged.  
- Verify creation of a draft sales order (not released) in SAP / Cosmos DB and CSR review queue. Confirm every order requires CSR review in MVP1 (no straight-through release).  
- Verify duplicate PO detection by customer PO number (100% detection in test set).  
- Validate NFRs: 99.5% 24x5 availability target, draft order created within 5 minutes of email receipt for 95% of POs, peak throughput 300 emails per hour.  
- Validate end-to-end traceability per email to SAP draft order number.  
- Validate AI/extraction quality targets: ≥95% header field accuracy and ≥90% line accuracy on pilot customers (these are acceptance criteria).  
- Validate role-based branch-scoped access and admin capabilities (cross-reference upload, confidence thresholds).

# 4. In Scope
- All MVP1 functional requirements from the BRD:
  - PO intake from branch order mailboxes via Microsoft Graph (Graph API -> Event Grid flow).  
  - Extraction from email body and PDF/Excel attachments using Azure Document Intelligence and Azure OpenAI.  
  - Customer identification by sender domain and PO content.  
  - Item matching via customer cross-reference table and Azure AI Search catalog fallback.  
  - SAP validation via APIM: customer active, material valid checks, and price variance >5% flagged.  
  - Creation of a draft sales order (not released) and persistence in Cosmos DB; CSR review queue in Web UI.  
  - Duplicate PO detection by customer PO number.  
  - Per-field confidence reporting and CS Admin ability to upload cross-reference files and manage confidence thresholds (admin UI flows).  
- Integrations and protocols shown in architecture (see Section 8 & 15).  
- Non-functional attributes for MVP1: availability 99.5% 24x5, performance (95% drafts within 5 minutes), peak 300 emails/hour, end-to-end observability, confidentiality of customer data, branch-based RBAC.  
- Test types: unit, component, API/contract, integration, system, performance, reliability, security, accessibility, UAT with CS branches and CS Admin.

# 5. Out of Scope
- All explicit MVP2 items (deferred):  
  - Straight-through release for trusted customers (MVP2)  
  - Order acknowledgement emails (MVP2)  
  - EDI detection and handling (MVP2)  
  - Analytics (MVP2)  
- Other explicitly stated out-of-scope items in BRD: EDI orders, credit checks changes, quotations, returns.

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Customers send one PO per email in most cases.
  - Cross-reference files exist for top 200 customers and CS Admin will provide pilot datasets.
  - Branch mailboxes and Graph API access will be available for non-production or approved mocks.
- Dependencies:
  - SAP integration team for APIM access to sales order and pricing APIs.
  - Mailbox access approval for branch mailboxes (Graph API).
  - CS branches and CS Admin availability for UAT, providing pilot customers and cross-reference files.
  - Azure Document Intelligence, Azure OpenAI and Azure AI Search access in non-production.
  - End-to-end observability and tracing support from platform/ops teams.
- Test constraints:
  - Test data must not include unmasked sensitive customer data; use masked or synthetic data unless explicitly approved by Security/IA.  
- Items TBD – confirm with owner:
  - Test tooling (test case management, automation frameworks) – TBD – confirm with QA Manager.  
  - Exact non-production environment names and subscriptions/provisioning schedule – TBD – confirm with Platform Architect.  
  - Detailed supported browser list for CSR Web UI – TBD – confirm with CS Admin.

# 7. Test Strategy
- Levels:
  - Unit tests: developer-owned; verify extraction mappers, match logic, duplicate detection functions, SAP API client adapters. Evidence required for handover to QA. (Coverage target TBD – confirm with QA Manager.)  
  - Component tests: Order Extraction Service, Order Creation Service, Web UI (Review Queue), APIM adapters, AI calls.  
  - API/contract tests: APIM <-> SAP, APIM <-> Azure Document Intelligence/OpenAI/Search, Graph API integration; verify schemas, auth, error codes, idempotency.  
  - Integration tests: Event Grid -> Service Bus -> Order Extraction Service -> Order Creation Service -> Cosmos DB -> SAP via APIM; Web UI integration with Cosmos DB and branch-scoped queues.  
  - System tests: end-to-end scenarios: email arrival to draft order in CSR queue with traceability.  
  - Performance tests: throughput and latency (see Section 12).  
  - Security, reliability, accessibility and compliance testing.  
  - UAT: CSRs and CS Supervisors from pilot branches to validate workflows and acceptance criteria.
- Techniques:
  - Requirements-based test cases mapped to BRD user stories, equivalence partitioning, boundary-value analysis (e.g., price variance at 5% boundary), negative testing, data-driven tests with golden dataset, exploratory testing, regression suites, and risk-based prioritisation.
- Automation:
  - Automate API/contract tests, end-to-end happy-path regression and performance harnesses where feasible. Tooling – TBD – confirm with QA Manager.

# 8. Functional Test Coverage
For each MVP1 requirement and sample user story, the tests will verify the following.

- PO intake (Branch mailboxes via Graph API):
  - New mail event handled via Event Grid; event enqueued to Service Bus.  
  - Multi-attachment emails: PDF and Excel attachments handled; body-only orders handled.  
  - Duplicate detection by customer PO number: identical customer PO number within configured window flagged as duplicate and routed to duplicate resolution workflow. Test positive and negative cases (same PO number different customer = not duplicate).  
  - Mailbox unavailable, Graph API auth failure, malformed email event: verify retries, error logs and alerts.

- Extraction (Azure Document Intelligence + Azure OpenAI):
  - Extract header fields: customer PO number, sold-to, ship-to, requested delivery date. Each field must include a per-field confidence value and source (body vs attachment).  
  - Extract line-level fields: customer part, description, quantity, UoM, price. Multi-page line tables, lines split across pages, Excel attachments, scanned PDFs and special characters to be tested.  
  - Validate zero/negative quantities rejected; line quantities must be > 0 (BRD quality check).  
  - Field-level confidence reporting: verify confidence thresholds (admin-configurable) cause highlights/flags in CSR UI when below threshold.

- Customer identification:
  - Identify customer via sender domain and PO content; test matching sender domain to known customer and fallback to PO content parsing. False-positive and false-negative scenarios to be tested.

- Item matching:
  - Customer cross-reference lookup: existing mapping yields direct material match. Test missing cross-reference and fallback to Azure AI Search catalog lookup.  
  - Highlight lines where customer part number has no cross-reference for CSR review (user story).  
  - Verify CS Admin upload of cross-reference file (format, validation, versioning) and its effect on subsequent matching.

- SAP validation via APIM:
  - Customer active check: active vs inactive customers handled per API response. Inactive customer flagged for CSR.  
  - Material valid check: material existence validated; unmatched materials flagged.  
  - Price variance: where extracted price differs from SAP price by >5% must be flagged. Exactly 5% difference: boundary test (BRD specifies >5% flagged — ensure > and = handled correctly).  
  - UoM validity: UoM must be valid in SAP; invalid UoM flagged.

- Draft sales order creation and CSR review queue:
  - Draft created in Cosmos DB and visible in Web UI Review Queue for the CSR assigned to branch. The draft must include header, lines, confidence per field, match results and SAP validation flags.  
  - Ensure no order is released to SAP (no straight-through release) in MVP1. Attempts to release via UI must be blocked or not present. Verify controls.  
  - CS Supervisor scenarios: orders older than 30 minutes are flagged in supervisor view (user story). Test ageing and flagging.

- Duplicate PO detection:
  - Test detection for duplicate customer PO numbers (same customer), ensure duplicates are flagged and prevented from creating secondary draft orders. Validate detection logic under race conditions and delayed mail arrival.

- User stories:
  - CSR: see draft order, confidence per field, correct highlighting for missing cross-reference lines.  
  - CS Supervisor: see orders older than 30 minutes flagged.  
  - CS Admin: upload cross-reference file and change confidence thresholds; verify changes are audited (change history) and take effect.

# 9. Roles, Permissions and Workflow Testing
- Roles (from BRD):
  - CSR: Review draft orders, correct lines, release orders in SAP (CSR performs release in MVP1 after manual review). Verify CSRs can only see queues for their branches (branch-based RBAC).  
  - CS Supervisor: Monitor queue and SLAs, reassign orders (verify supervisor permissions for viewing across their scope).  
  - CS Admin: Maintain mailbox routing, upload cross-reference files, manage confidence thresholds. Verify admin cannot bypass CSR review to auto-release (segregation of duties). BRD requires CSR review for every order in MVP1; test to ensure Admin/Dev accounts cannot programmatically auto-release drafts in production-like flows without explicit product approval.  
- Tests:
  - Verify Azure AD authentication and role assignment for CSR, CS Supervisor and CS Admin accounts via App Gateway (see architecture connections).  
  - Verify least privilege: UI/API calls blocked for unauthorized roles; direct-URL/API access protection.  
  - Verify session timeout, account disablement, role changes effect. (Specific session timeout values – TBD – confirm with Security/CS Admin.)

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization:
  - Azure AD sign-on, branch-based queue access enforcement and token validation via App Gateway and APIM. Test token expiry and refresh flows.  
- Data protection:
  - Customer data classified as Confidential per BRD. Verify storage controls for Blob Storage and Cosmos DB configurations (at-rest encryption presumed). Confirm masking/sanitisation policy for test data (tests must use masked or synthetic customer data unless approved).  
- Input validation and attachment scanning:
  - Test malicious attachments (scripted Excel, macro, malformed PDFs) and validate ingestion rejection or safe handling.  
- API security:
  - Verify APIM enforces authentication and expected quotas. Test error-handling with no leaked sensitive data.  
- Compliance:
  - Validate that AI Governance Council approval is recorded and that AI services are used under approved governance (evidence required).  
- Penetration & scanning:
  - SAST/DAST/Dependency scanning and a penetration test before MVP1 release – scheduling and scope TBD – confirm with Security Owner.

# 11. AI and Data Quality Validation
- Targets (BRD acceptance criteria):
  - ≥95% header field accuracy on pilot customers.  
  - ≥90% line accuracy on pilot customers.  
- Tests and measurements:
  - Build a labelled golden dataset using pilot customers (CS Admin/Customer Service to provide masked representative POs). Compute precision/recall and overall accuracy separately for header fields and line items.  
  - Per-field confidence: verify confidence values are produced for every field and thresholds configurable by CS Admin. Test behavior when confidence below threshold: UI highlights and CSR required review.  
  - Azure Document Intelligence extraction and Azure OpenAI mapping: validate that numeric fields (quantity, price) are not altered by mapping; validate description normalization does not change item codes or numeric values.  
  - Validate fallback matching (cross-reference -> catalog search) for missing cross-reference entries. Measure matching recall for the pilot dataset.  
  - Track extraction/processing failures and reprocessing behaviour for updated models or mapping rules (reprocessing process and results must be reproducible) – reprocessing process steps TBD – confirm with CS Admin.  
- Responsible AI / hallucination controls:
  - Verify mapping outputs do not invent material numbers or prices; flag any non-evidence-based values for CSR review. Specific guardrails and mitigation steps (retraining, prompt management) – TBD – confirm with AI Governance Council and CS Admin.

# 12. Performance Testing
- NFR targets to validate (from BRD):
  - Draft order created within 5 minutes of email receipt for 95% of POs.  
  - System handles peak 300 emails per hour.  
  - Availability 99.5% 24x5 (operational measurement and monitoring to demonstrate).  
- Tests:
  - Throughput tests simulating burst and sustained arrival patterns up to and above 300 emails/hour; measure average and P95/P99 processing time from email arrival to draft creation.  
  - Latency tests for individual large/complex emails (multi-page PDFs, large Excel attachments) to measure time to draft.  
  - Concurrent user tests for CSR Web UI under load (TBD – confirm number of concurrent CSR users with CS Ops).  
  - Service Bus and Event Grid throughput/queue depth tests and impact on draft latency.  
- Performance instrumentation and baselining: capture processing time per stage, queue latencies, APIM response times, AI service latencies.

# 13. Reliability and Recovery Testing
- Scenarios:
  - Event Grid delivery retries and Service Bus message redelivery after Order Extraction Service outage; verify idempotency and duplicate suppression.  
  - Blob Storage or Cosmos DB transient failures: test retry logic and eventual consistency; verify no data loss for drafts and that drafts reconcile after recovery.  
  - SAP API (via APIM) timeouts or throttling: verify queued retry, error flagging to CSR with clear reason (e.g., SAP unavailable).  
  - Mailbox unavailability or Graph API auth failure: verify retry/backoff and alerting.  
- Verify recovery runbooks and alerts are generated (runbooks and alerting procedures – TBD – confirm with Platform/Operations).

# 14. Accessibility and Compatibility Testing
- Accessibility:
  - CSR Web UI: keyboard navigation, screen-reader labels, focus order, error identification and colour contrast per enterprise accessibility policy (specific standards and benchmarks – TBD – confirm with Accessibility Owner).  
- Browser/device compatibility:
  - Supported browsers and versions are TBD – confirm with CS Admin / Enterprise Desktop Standards. Test matrix to be defined after confirmation.

# 15. Logging, Monitoring and Audit Testing
- Logging & tracing requirements from BRD:
  - End-to-end trace per email to SAP draft order number. Verify correlation IDs pass through Event Grid -> Service Bus -> Order Extraction Service -> Order Creation Service -> APIM -> Cosmos DB and SAP.  
  - Log events: email receipt, extraction result (fields + confidences), matching decisions, SAP validation responses, draft creation (Cosmos DB id), duplicate detection events, cross-reference uploads, and CSR corrections.  
  - Monitoring: draft accuracy metrics, CSR correction rates, time-to-draft, emails processed per hour. (The BRD notes logging/monitoring text: "Emails processed, draft accuracy, CSR correction rate, time to draft (TBD – pending SME review)". Test definitions for dashboards and alert thresholds – TBD – confirm with CS Operations.)  
- Audit:
  - Verify audit trail for CS Admin uploads/changes (cross-reference file uploads and confidence threshold changes) including who, when, and what changed.  
  - Verify retention requirements for logs and audit records – TBD – confirm with Compliance.

# 16. Test Environments and Test Data
- Environments:
  - Non-production subscription per architecture (contains Azure AI Landing Zone, Shared AKS Non-prod, Data Stores, Integration & Eventing). Provisioning and exact environment names – TBD – confirm with Platform Architect.  
  - Separate environments for development, QA/integration, performance and UAT. Test data sets versioned with model/mapping versions.  
- Test data:
  - Golden dataset of pilot customers (masked) covering typical and edge PO layouts, multi-page PDFs, Excel attachments, scanned images, special characters, multiple currencies and boundary cases. CS Admin and CS branches to supply pilot datasets.  
  - Invalid/corrupt: password-protected attachments, malformed Excel files, missing PO numbers, zero/negative quantities.  
  - Boundary data: price exactly at 5% variance (to validate >5% logic), orders older than 30 minutes (for supervisor flags), duplicate PO numbers.  
  - Security test data: malicious payload examples (macro-enabled Excel, script-laden attachments) in isolated environment.  
- Test data management:
  - All test data with customer-identifiable information must be masked unless explicit approval is obtained from Security/Compliance.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:
  - BRD approved and requirements baselined.  
  - Non-production environments provisioned and accessible (TBD – confirm with Platform).  
  - Graph API mailbox test accounts available.  
  - SAP non-production APIs via APIM accessible or approved mocks for validation.  
  - Golden dataset for pilot customers seeded in test environments.  
  - Build deployed to test environment with unit test evidence and component test results.
- Suspension criteria:
  - Blocking defects in ingestion, extraction or SAP validation that prevent end-to-end testing.  
  - Major security findings preventing further testing (High or Critical severity).  
- Exit criteria (must all be met or documented exceptions approved by Product/Customer Service Operations):
  - Functional: all critical and high-priority test cases passed; all BRD MVP1 functional requirements verified.  
  - AI accuracy: ≥95% header field accuracy and ≥90% line accuracy on pilot customers (BRD acceptance criteria).  
  - Performance: 95% of drafts created within 5 minutes and system can handle peak 300 emails/hour in performance test.  
  - Duplicate detection: 100% detection in the provided test set.  
  - Workflow control: no orders released without CSR action in MVP1 (demonstrable enforcement).  
  - No open Critical defects and no open High-severity security defects.  
  - Observability: end-to-end traceability demonstrated.  
  - UAT: business sign-off from CS pilot users for acceptance scenarios.

# 18. Defect Management
- Severity definitions:
  - Critical: core flow fails or produces incorrect business outcomes (e.g., draft created with incorrect customer leading to wrong shipments; orders released without CSR action).  
  - High: essential functionality broken with no acceptable workaround (e.g., extraction pipeline fails for majority of pilot layouts).  
  - Medium: functionality impacted with workaround (e.g., one cross-reference file format mismatch).  
  - Low: cosmetic or non-blocking issues.
- Defect process:
  - Tracking tool – TBD – confirm with QA Manager.  
  - Triage cadence: daily for Critical/High defects during system/UAT, weekly for lower severities. Assign owner, environment, steps-to-reproduce, expected vs actual and required attachments (logs, correlation IDs). Retest and closure criteria defined per defect.

# 19. Risks and Mitigations
- Risk: Unusual PO layouts cause extraction failures.  
  - Mitigation: Golden dataset covering variability, human-in-the-loop CSR review, iterative tuning of Document Intelligence and mapping.
- Risk: Missing cross-references for many customers.  
  - Mitigation: Catalog fallback via Azure AI Search, CS Admin upload process and prioritized onboarding of top customers.
- Risk: SAP API limits or outages.  
  - Mitigation: Queueing, retry/backoff and clear CSR flags when SAP validation cannot be completed.
- Risk: Mailbox access delays or Graph API changes.  
  - Mitigation: Use test mailbox accounts, implement robust error handling and retries; confirm Graph API access early.
- Risk: Sensitive customer data exposure in test environments.  
  - Mitigation: Masking/synthetic data policy; require approval for any production-like data.
- Risk: Scope creep into MVP2 (straight-through release, acknowledgements).  
  - Mitigation: Formal change control; MVP1 acceptance gates require Product approval for any deviation.

# 20. Test Deliverables and Reporting
- Test deliverables:
  - Test plan (this document).  
  - Test cases mapped to BRD requirements (traceability matrix).  
  - Automated test suites (API/contract/regression) – tool TBD.  
  - Performance test scripts and results.  
  - AI accuracy reports (precision/recall, field-level accuracy) for pilot dataset.  
  - Test execution and defect reports.  
  - UAT evidence and business sign-off artifacts.  
- Reporting:
  - Weekly test status: planned/executed/passed/failed/blocked, defect ageing and severity, coverage by requirement, AI accuracy metrics, time-to-draft KPIs. Exact report templates and distribution – TBD – confirm with QA Manager and CS Operations.

# 21. Traceability and Metrics
- Traceability:
  - Every BRD requirement and user story will be mapped to one or more test cases; change-controlled traceability matrix maintained.  
- Metrics/KPIs to capture:
  - Test coverage by requirement, test case execution rate, defect counts by severity and age.  
  - AI metrics: header accuracy, line accuracy (separate measures), per-field confidence distributions.  
  - Operational metrics: emails processed per hour, draft creation time (average, P95, P99), duplicate detection rate, CSR correction rate.  
  - Availability: measured vs 99.5% 24x5 target.  
- Reporting cadence: weekly test progress; final test summary at exit.

# 22. Test Schedule
- High-level milestones from BRD:
  - MVP1 build: Apr–Jul 2026 (BRD).  
  - Detailed test schedule (component, integration, system, performance and UAT dates) – TBD – confirm with Project Manager and QA Manager.  
- Note: schedule will be updated once environment provisioning and build cadence are confirmed.

# 23. End-to-End Scenario
Representative E2E test(s) to demonstrate MVP1 acceptance:

Scenario A — Happy path (pilot customer)
1. Email with single PDF attachment arrives to branch mailbox.  
   - Verify Graph API -> Event Grid -> Azure Event Grid -> Azure Service Bus event flow.  
2. Order Extraction Service picks up message from Service Bus, stores email copy in Azure Blob Storage and sends extracted PO to Order Creation Service.  
   - Verify extraction fields present with confidences and source references.  
3. Item matching: customer cross-reference yields material codes. If cross-reference missing for a line, fallback to Azure AI Search catalog.  
4. Order Creation Service calls SAP via APIM to validate customer/material/pricing; price difference within 5% → no flag.  
5. Draft sales order created in Cosmos DB and visible to CSR in Web UI review queue for the branch. End-to-end traceability from email id to Cosmos DB draft id and SAP validation call is recorded.  
6. CSR reviews, corrects (if needed) and releases order into SAP (CSR action in MVP1). Verify release action is performed by CSR and only after explicit CSR action.  
7. Verify audit logs for extraction, matching decisions, SAP validation responses, draft creation, CSR user id and timestamp.

Scenario B — Price variance boundary
- Use a PO where extracted price differs by exactly 5% and by 5.01% from SAP price to verify BRD-specified behavior: >5% flagged, =5% not flagged.

Scenario C — Duplicate detection race
- Two emails with same customer PO number arrive concurrently; verify detection logic prevents duplicate drafts and records first/second event handling with proper flags.

Scenario D — Failure recovery
- Simulate SAP APIM timeout during validation; ensure order is queued for retry, CSR receives informative flag, and no duplicate drafts are created when SAP recovers.

# 24. Approvals
- Required approvers (from BRD approvals):
  - AI Governance Council  
  - Finance (BIR)  
  - AI intake  
  - Global Intake  
  - C2P  
  - WAB  
- QA sign-off: QA Lead and Test Manager (names / signatures – TBD – confirm with QA Manager).  
- Business sign-off: Customer Service Operations owner and CS Admin (UAT approval).