# 1. Document Control
- Title: QA Test Plan
- Version: 1.0
- Application: Email Purchase Order Entry Automation
- Prepared by: TBD – confirm with QA Lead
- Reviewed by: TBD – confirm with Test Manager
- Audience: Business stakeholders, architects and QA team
- Purpose: Define the quality approach, scope, strategy, tests and exit criteria to validate Email Purchase Order Entry Automation MVP1 from PO intake (branch mailboxes) through extraction, item matching, SAP validation and draft sales order creation and CSR review.

# 2. References
- Email Purchase Order Entry Automation BRD, Version 1.0, 02 Mar 2026
- Email Purchase Order Entry Architecture diagram (P07_Email_Order_Entry_Architecture.png)

# 3. Test Objectives
- Verify accurate extraction of the following fields from email body and PDF/Excel attachments: customer PO number, sold-to, ship-to, requested delivery date, and lines (customer part, description, quantity, UoM, price). Measure field-level accuracy against acceptance targets.
- Verify item matching logic: customer cross-reference lookup first, fallback to catalog (Azure AI Search), and correct flagging when no cross-reference exists.
- Verify customer identification by sender domain and PO content.
- Validate SAP S/4HANA checks via APIM: customer active, material valid, and price variance logic (price variance >5% must be flagged).
- Verify creation of a draft sales order in SAP (draft only, not released) and that CSR review is required for every order in MVP1.
- Verify duplicate PO detection by customer PO number (100% detection in test set).
- Validate non-functional targets from BRD:
  - Draft order created within 5 minutes of email receipt for 95% of POs.
  - System supports peak 300 emails per hour.
  - Availability 99.5% 24x5.
- Verify RBAC and branch-based queue access so CSRs see only their branch queue.
- Verify observability: end-to-end trace from email to SAP draft order number and required logging metrics (emails processed, draft accuracy, CSR correction rate, time to draft).

# 4. In Scope
- All MVP1 functional features:
  - PO intake from branch order mailboxes via Microsoft Graph and Event Grid -> Service Bus processing flow.
  - Extraction from email body and attachments (PDF and Excel) using Azure Document Intelligence and Azure OpenAI mapping.
  - Customer identification by sender domain and content.
  - Item matching via customer cross-reference table (CS Admin uploads) and Azure AI Search catalog lookup fallback.
  - SAP validation via APIM: customer active, material valid, price variance >5% flagged.
  - Draft sales order creation in SAP (draft only, not released) via Order Creation Service.
  - CSR review queue (Web UI) with branch-based visibility and correction/release action (CSR must perform release in MVP1).
  - Duplicate PO detection by customer PO number.
- Integrations listed in architecture:
  - Azure AD / App Gateway / APIM / Azure Document Intelligence / Azure OpenAI / Azure AI Search / Branch Mailboxes (Graph API) / Azure Event Grid / Azure Service Bus / Azure Blob Storage / Azure Cosmos DB / SAP S/4HANA.
- Non-functional scope:
  - Performance: 95% of drafts within 5 minutes; peak 300 emails/hour.
  - Availability: 99.5% 24x5.
  - Observability: end-to-end trace per email to SAP draft order number.
  - Security: Azure AD authentication and branch-based queue access; confidentiality of PO emails.
- Test types: unit, component, API/contract, integration, system, performance, reliability, security, accessibility/compatibility, AI/data quality validation, UAT with CSR and CS Supervisor participation.

# 5. Out of Scope
- MVP2 capabilities (deferred to Out of Scope):
  - Straight-through release for trusted customers (MVP2).
  - Order acknowledgement emails (MVP2).
  - EDI detection/fallback (MVP2).
  - Analytics (MVP2).
- Other out of scope (per BRD):
  - Changes to credit checks, quotations, returns.
- Any automatic order release functionality (explicitly no orders released without CSR action in MVP1).

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Customers send one PO per email in most cases.
  - Cross-reference files exist for top 200 customers.
  - CS branches will participate in UAT.
- Dependencies (from BRD / architecture):
  - SAP integration team to provide access to S/4HANA sales order and pricing APIs via APIM.
  - Mailbox access approval for branch mailboxes (Graph API).
  - APIM integration to Azure Document Intelligence, Azure OpenAI and Azure AI Search per architecture.
  - CS Admin to provide cross-reference uploads and to configure confidence thresholds.
  - Non-production environments with SAP test data and mailbox test accounts.
- Test environment/other constraints:
  - Test data must be treated as Confidential (customer data). Masking or synthetic data required where production data cannot be used.
  - If any required integration is not available, approved mocks must be provided.
- Items requiring confirmation:
  - Test environment names, access and schedule: TBD – confirm with Test Manager
  - Tools for automation, performance and security testing: TBD – confirm with QA Lead

# 7. Test Strategy
- Test levels:
  - Unit testing: developer-owned, covering extraction mappers, mapping logic and matching algorithm.
  - Component testing: Order Extraction Service, Order Creation Service, Web UI Review Queue, connectors to Azure Document Intelligence/OpenAI/Search.
  - API and contract testing: APIM endpoints, authentication, error codes, idempotency, schema validation.
  - Integration testing: Graph API -> Event Grid -> Service Bus -> Extraction -> Blob/DB -> Order Creation -> SAP via APIM.
  - System testing: end-to-end scenarios from email ingestion to SAP draft order creation and CSR review.
  - Performance/load testing: throughput and latency targets in NFR.
  - Reliability/resilience testing: retries, idempotency and recovery.
  - Security testing: auth, RBAC, data protection and injection tests.
  - UAT: CSR and CS Supervisor validation and acceptance testing.
- Test techniques:
  - Requirements-based traceable test cases.
  - Equivalence partitioning and boundary-value analysis (notably price variance threshold at 5%, time-to-draft at 5 minutes, duplicate detection).
  - Pairwise and combinatorial testing for fields/attachments (PDF vs Excel, scanned vs native).
  - Negative and exploratory testing.
  - Data-driven automation for extraction/regression tests.
  - Risk-based prioritisation: highest priority on extraction accuracy, SAP validation, duplicate detection and no-automatic-release control.

# 8. Functional Test Coverage
The following functional areas will be validated with specific test checks and example cases derived from BRD rules.

H2: PO Intake (mailbox)
- Validate mailbox event flow: Branch Mailboxes (Graph API) -> Azure Event Grid (new mail) -> Azure Service Bus -> Order Extraction Service.
- Test cases:
  - New PO email (native body) -> event -> processing.
  - Email with PDF attachment containing PO.
  - Email with Excel attachment containing PO lines.
  - Scanned PDF vs machine-readable PDF.
  - Multiple attachments (one valid PO + one unrelated attachment).
  - Email with no PO content (should be routed to manual review or rejected).
  - Duplicate email with same customer PO number (duplicate detection should identify and handle per rules).
  - Mailbox unavailable / Graph API error -> retry behavior and alerting.
  - Multiple POs in single email (edge case): system behavior must be documented and CSR-visible; BRD assumption is one PO per email in most cases.
- Acceptance checks:
  - Event is enqueued to Service Bus and a copy of email stored in Blob Storage.

H2: Extraction
- Fields to extract and verify: customer PO number, sold-to, ship-to, requested delivery date, lines with customer part, description, quantity, UoM, price.
- Test cases:
  - Correct extraction of fields from body, PDF and Excel.
  - Multi-page attachments with line tables spanning pages.
  - Scanned images with OCR (Document Intelligence).
  - Decimal precision and rounding.
  - Missing mandatory fields (invoice number equivalent: customer PO number) -> rejection or CSR manual entry.
  - Negative or zero quantities -> flagged (quality check: line quantity > 0).
  - Invalid UoM not in SAP master data -> flagged.
  - Field-level confidence reported for each extracted field.
- Acceptance checks:
  - Header mandatory fields present for valid POs.
  - Line-level reconciliation where applicable.

H2: Customer Identification
- Methods to validate: sender domain and PO content.
- Test cases:
  - Sender domain mapping to customer.
  - Sender domain absent or generic -> identification from PO content.
  - Conflicting identification results -> produce a confidence score and route to CSR for verification.

H2: Item Matching
- Flow: customer cross-reference lookup (CS Admin upload) -> Azure AI Search catalog fallback.
- Test cases:
  - Customer part maps to exact material via cross-reference.
  - No cross-reference -> catalog lookup returns one match and match confidence acceptable.
  - No matches -> line flagged for CSR with highlight (user story: CSR sees missing cross-reference highlighted).
  - Multiple catalog matches -> present options and confidence.
  - Cross-reference upload processing (CS Admin upload monthly) and effect on subsequent matching (reprocess test).
- Acceptance checks:
  - Lines with missing cross-reference are highlighted in CSR UI.
  - Matching source recorded in draft (cross-reference vs catalog).

H2: SAP Validation and Price Variance
- SAP checks via APIM: customer active, material valid, price check and price variance rule.
- Business rule: price variance >5% must be flagged.
- Example numeric checks:
  - If SAP price = 100.00 and PO price = 105.00 → difference = 5.00 → 5% → boundary case: 5% = threshold; BRD says >5% flagged, so 5.00 (exactly 5%) must NOT be flagged; 105.01 (5.01%) must be flagged. Tests must include exact 5.00 and 5.01% scenarios.
  - If SAP price = 100.00 and PO price = 106.00 → 6% -> must be flagged.
- Other SAP validation test cases:
  - Customer inactive -> flag and route to CSR.
  - Material invalid -> flag and route to CSR.
  - Pricing API timeout or error -> retry and escalate per runbook.
- Acceptance checks:
  - Price variance logic behaves as above.
  - Validation outcomes recorded in draft and visible to CSR.

H2: Draft Sales Order Creation
- Verify Order Creation Service writes draft order to SAP (draft, not released) and to Cosmos DB as drafts per architecture.
- Test cases:
  - Successful draft creation with SAP draft sales order number returned and trace recorded.
  - Failed draft creation due to SAP error -> no partial release; draft in Cosmos DB with pending state, alert for retry or manual intervention.
  - Ensure no automatic release occurs in MVP1.
- Acceptance checks:
  - Draft order exists in SAP and in Cosmos DB; end-to-end trace from email to SAP draft order number is present.

H2: CSR Review Queue (Web UI)
- Branch-based queue access: CSRs see only their branch queue.
- Test cases:
  - CSR can view extracted fields, confidence per field, matching source and SAP validation flags.
  - CSR can correct header or line fields and save updates; corrected draft reflects changes and resubmits to SAP draft creation if required.
  - Lines with missing cross-reference are visually highlighted.
  - CS Supervisor sees orders older than 30 minutes flagged (user story).
  - CSR release action: in MVP1 CSR must perform release in SAP; test that release remains manual and cannot be bypassed by system.
- Acceptance checks:
  - Branch-based segregation enforced.
  - SLA flagging (30 minutes) visible to Supervisor.

H2: Duplicate PO Detection
- Rule: duplicate detection by customer PO number (BRD).
- Test cases:
  - Two emails (same or different branches) with identical customer PO number -> duplicate detection must identify duplicates.
  - Reprocessing scenarios where same message reprocessed -> idempotency (no duplicate drafts).
  - Duplicate detection coverage: run a curated test set to verify 100% detection (per acceptance criteria).
- Acceptance checks:
  - Duplicate POs are not created as multiple drafts; detection rate 100% in the test set.

H2: Observability and Metrics
- Verify logging of: email ID, timestamp, extracted fields with confidence, cross-reference used, SAP validation outcome, draft order ID, processing time.
- Metrics to capture: emails processed, draft accuracy, CSR correction rate, time to draft.

# 9. Roles, Permissions and Workflow Testing
- Roles defined in BRD: CSR, CS Supervisor, CS Admin.
- Tests:
  - CSR:
    - Permitted: view and correct drafts, release orders in SAP (CSR must release), view branch queues only.
    - Restricted: cannot change cross-reference files or system-wide confidence thresholds.
  - CS Supervisor:
    - Permitted: monitor queue and SLAs, reassign orders, see flagged orders older than 30 minutes.
    - Restricted: cannot upload cross-reference files (unless also CS Admin).
  - CS Admin:
    - Permitted: maintain mailbox routing, upload customer cross-reference files, set confidence thresholds.
    - Restricted: should not be able to perform CSR release actions in MVP1 if segregation of duties is required (confirm policy with business).
- Verify:
  - RBAC enforced at UI and API layers via Azure AD / App Gateway per architecture (OAuth 2.0).
  - Branch-based queue access enforced (CSRs only see their branch).
  - Privilege escalation attempts blocked and logged.
  - Session expiry, token validation and logout behavior (TBD – confirm required session timeout with Security owner).

# 10. Security, Privacy and Compliance Testing
- Authentication and Authorization:
  - Verify Azure AD authentication and role assignment for CSR, CS Supervisor and CS Admin.
  - Verify App Gateway / APIM integration for auth (HTTPS/443 AD/SSO and OAuth 2.0 where shown in architecture).
- Data protection:
  - Ensure customer PO emails and PII are handled as Confidential (BRD). Confirm masking rules where required and ensure logs do not contain unmasked sensitive fields.
  - Validate encryption in transit (HTTPS/443) and encryption at rest for Blob Storage and Cosmos DB (verify configuration or confirm with infra owner).
- Injection and malware:
  - Test malicious attachments (macro-enabled Excel, embedded scripts) and malicious text payloads. Ensure attachments are stored safely and not executed.
- API security:
  - Rate limiting, input validation, and safe error messages.
- AI governance:
  - Verify AI Governance Council approvals are in place (BRD lists approvals). Confirm governance artifacts available: TBD – confirm with AI Governance Council contact.
- Penetration and vulnerability scanning:
  - Schedule SAST/DAST and penetration testing before release: TBD – confirm with Security owner.

# 11. AI and Data Quality Validation
- Accuracy targets (BRD Acceptance Criteria):
  - ≥95% header field accuracy on pilot customers.
  - ≥90% line accuracy on pilot customers.
- Confidence and thresholds:
  - CS Admin configurable confidence thresholds (BRD). Tests must validate that threshold changes affect routing/flagging.
  - Verify field-level confidence returned for each extracted field.
- Responsible AI checks (examples consistent with BRD):
  - Ensure Azure OpenAI mapping does not alter numeric quantities, UoM or prices (no hallucinated numeric changes).
  - Verify fallback behavior when cross-reference missing (catalog search) and that the source of match is recorded.
  - Maintain golden labelled dataset for pilot customers to measure precision/recall.
- Test cases:
  - Golden dataset runs to compute header and line accuracy percentages.
  - Measure false positives/false negatives for item mapping and price variance detection.
  - Test that confidence threshold configuration (changed by CS Admin) changes routing as expected.
- Metrics and reporting:
  - Report header/line accuracy per pilot customer, per attachment type (PDF, Excel, scanned), and per confidence bucket.

# 12. Performance Testing
- Targets from BRD:
  - Draft order created within 5 minutes of email receipt for 95% of POs.
  - Peak 300 emails per hour.
  - Availability 99.5% 24x5.
- Performance tests:
  - Throughput test: sustained 300 emails/hour for representative mix (PDF, Excel, scanned) and measure success rate.
  - Latency test: measure time from Event Grid new mail trigger to SAP draft order creation; validate 95th percentile <= 5 minutes.
  - Spike tests: short bursts above 300/hour to observe degradation and recovery.
  - Concurrency tests: multiple CSRs accessing UI concurrently (TBD – confirm concurrency target with Product).
  - Resource and queue saturation tests: Service Bus queue depth monitoring and behavior under backpressure.
- Acceptance:
  - 95% of test POs processed within 5 minutes.
  - System handles 300 emails/hour without loss and appropriate degradation at higher loads.

# 13. Reliability and Recovery Testing
- Tests:
  - Service Bus consumer restart during processing: ensure idempotency and no duplicate drafts.
  - APIM -> SAP transient failures: retry logic, exponential backoff and alerting.
  - Blob Storage outage simulation: ensure processing halts safely and recovery creates consistent state.
  - Event Grid delivery retries and duplicate event handling.
  - Reprocessing of failed messages and ensure duplicate detection still prevents duplicate drafts.
- Acceptance:
  - No duplicate drafts created during recovery scenarios.
  - Failures produce actionable alerts and account for retries per runbook (TBD – confirm runbook with Ops owner).

# 14. Accessibility and Compatibility Testing
- BRD does not mandate accessibility targets; Web UI will be tested for basic enterprise compatibility:
  - Verify UI functions in enterprise-supported browsers (TBD – confirm which browsers/versions with Browser Support owner).
  - Verify keyboard navigation and readable fonts/contrast for primary functions (CSR queue, record view and edit).
- Confirm any formal accessibility standard requirements: TBD – confirm with Accessibility owner.

# 15. Logging, Monitoring and Audit Testing
- Verify end-to-end traceability (BRD): each email maps to a SAP draft order number and trace is visible.
- Logs/metrics to validate:
  - Email ID/message-id, processing timestamps, extracted fields and confidence, matching source, SAP validation results, draft order ID, processing time, error codes.
  - Operational metrics: emails processed, draft accuracy, CSR correction rate, time-to-draft.
- Tests:
  - Validate correlation IDs passed across components (Event Grid -> Service Bus -> Extraction -> Order Creation -> Cosmos DB -> SAP).
  - Verify dashboards/alerts for processing failures, API errors and SLA violations (30 minute queue flagging).
  - Ensure logs do not contain unmasked confidential customer data in searchable logs.
- Retention and export: confirm retention periods and exportability with Compliance owner: TBD – confirm with <owner>.

# 16. Test Environments and Test Data
- Environments required (to be provisioned / confirmed):
  - Dev, QA/integration, Performance, UAT and Pre-prod with connectivity to SAP non-production via APIM and test branch mailboxes. Specific environment names and access: TBD – confirm with Infrastructure owner.
- Test data:
  - Golden labelled dataset for pilot customers (masked or synthetic) used for accuracy measurement.
  - Valid POs: native body, PDF, Excel, scanned PDFs, multi-page tables.
  - Invalid POs: missing customer PO number, invalid UoM, zero/negative quantity, corrupt attachments.
  - Boundary cases: price variance exactly 5.00% (must NOT be flagged), price variance 5.01% (must be flagged), duplicate detection cases, draft creation latency edge cases (just under and just over 5 minutes).
  - Cross-reference files: current monthly upload and older versions for reprocessing tests.
- Data handling:
  - All test data marked Confidential; masking or synthetic data must be used when production cannot be used.
  - Version test data and record model/prompt/configuration used for each run.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:
  - BRD baselined and acceptance criteria agreed.
  - Test environments provisioned with access to branch mailbox test accounts, APIM endpoints to Azure Document Intelligence, Azure OpenAI, Azure AI Search and SAP non-production APIs or approved mocks.
  - Cross-reference files for pilot customers available.
  - Golden labelled dataset available for accuracy measurement.
  - Build deployed to QA environment with unit test evidence and component test results.
- Suspension criteria:
  - Critical production-impacting dependencies unavailable (SAP non-prod/APIM, Graph API) for > agreed window (TBD – confirm with Test Manager).
  - Severe security findings blocking further testing.
- Exit criteria (must all be met unless formally approved otherwise):
  - ≥95% header field accuracy on golden dataset for pilot customers.
  - ≥90% line accuracy on golden dataset for pilot customers.
  - Draft order created within 5 minutes for ≥95% of POs in performance tests.
  - Duplicate PO detection = 100% on curated duplicate test set.
  - No orders released automatically in MVP1 (verified).
  - All Critical defects closed and no open High-severity security defects.
  - UAT sign-off from Customer Service Operations (CSR and CS Supervisor): TBD – confirm sign-off owners.

# 18. Defect Management
- Severity definitions (aligned with business impact):
  - Critical: Incorrect draft creation that leads to wrong shipped goods or data corruption; automatic release of order in MVP1; security breach exposing customer data.
  - High: Core workflow broken (inability to create drafts), duplicate drafts created, SAP validation failures producing incorrect accept decisions.
  - Medium: Function works with workaround (e.g., one attachment type requires manual correction).
  - Low: Cosmetic or UI issues.
- Defect lifecycle:
  - Log defects in agreed defect tracking tool: TBD – confirm with QA Lead.
  - Defect triage cadence: daily for Critical/High, twice weekly for Medium/Low (TBD – confirm).
  - Each defect must include steps to reproduce, environment, build, evidence, severity and owner.
- Escalation:
  - Critical defects escalated to Product and Architecture owners immediately.

# 19. Risks and Mitigations
- Risk: Unusual PO layouts causing extraction failures.
  - Mitigation: Golden dataset per pilot customer, conservative confidence thresholds and CSR review for all orders.
- Risk: Missing cross-references for many customers.
  - Mitigation: Catalog search fallback (Azure AI Search) and highlight missing cross-reference to CSR; prioritize cross-reference upload for top customers.
- Risk: SAP API limits or unavailability.
  - Mitigation: Queueing (Service Bus), retry logic, and approved mocks for testing if SAP non-prod is unavailable.
- Risk: Mailbox access delays or approvals.
  - Mitigation: Escalate mailbox approvals early; provision test mailboxes if production access unavailable.
- Risk: Sensitive customer data exposure in logs.
  - Mitigation: Masking rules, limit log retention of PII and review by Security/Compliance.

# 20. Test Deliverables and Reporting
- Deliverables:
  - Test plan (this document).
  - Traceable test cases mapped to BRD requirements.
  - Automation scripts and test data sets (location and access: TBD – confirm with QA Lead).
  - Performance test reports (latency and throughput).
  - Security test reports (SAST/DAST/PenTest): TBD – confirm schedule.
  - Defect reports and triage notes.
  - UAT test evidence and sign-off documentation.
  - Test summary report and exit criteria evidence.
- Reporting:
  - Weekly status: planned vs executed cases, pass/fail/blocked counts, open defects by severity, extraction accuracy metrics, time-to-draft SLA compliance, duplicate detection rate.
  - Ad-hoc alerts for Critical defects.

# 21. Traceability and Metrics
- Traceability:
  - Map every BRD requirement and user story (MVP1) to one or more test cases and acceptance test results.
- Metrics/KPIs to report:
  - Test coverage by requirement (%).
  - Test execution progress and pass rate.
  - Defect density and ageing by severity.
  - Extraction accuracy: header and line accuracy (%) per pilot customer and overall.
  - Draft creation latency: median and 95th percentile; % within 5 minutes.
  - Duplicate detection rate (%) on test set.
  - CSR correction rate (%) and top correction types.
  - Availability and error rates for integrations (APIM, Graph API, SAP).

# 22. Test Schedule
- High-level plan from BRD:
  - MVP1: Apr–Jul 2026 (BRD high-level build window).
- Detailed test phase dates and milestones: TBD – confirm with Test Manager and Product (proposed sequencing: component & integration tests during Apr–May, system & performance tests in Jun, UAT and acceptance in Jul).
- Milestones to schedule:
  - Test environment readiness.
  - Golden dataset availability.
  - Component integration complete.
  - Performance test window.
  - UAT start and completion.
  - Exit criteria validation and release decision.

# 23. End-to-End Scenario
Representative E2E scenario to validate core flow and business rules:
1. New email arrives in Branch Mailbox (Graph API). Event Grid emits new mail event to Service Bus.
2. Order Extraction Service consumes event, stores an email copy to Blob Storage and invokes Azure Document Intelligence via APIM to extract header and line fields.
3. Azure OpenAI mapping standardises fields (via APIM) and Azure AI Search used for catalog fallback if cross-reference absent.
4. System identifies customer by sender domain; cross-reference lookup maps customer part to SAP material.
5. Order Creation Service calls SAP S/4HANA via APIM to validate customer active, material valid and pricing.
   - Numeric example: SAP price = 100.00, extracted PO price = 105.00 → difference = 5.00 (5.00%) → per BRD rule (>5% flagged) this exact 5.00% must NOT be flagged; test also where PO price = 105.01 (5.01%) MUST be flagged.
6. Draft sales order is created in SAP (draft state) and a draft record is written to Azure Cosmos DB. End-to-end trace ID maps email to SAP draft order number.
7. Draft appears in CSR Web UI review queue for the branch (CSR sees only their branch queue). Line with missing cross-reference is highlighted.
8. CSR corrects a line quantity and saves; correction persists and draft updated. CSR performs manual release in SAP (MVP1 requires CSR action).
9. Verify logs capture extraction confidences, matching source, SAP validation outcome and draft order ID. Verify time from email receipt to draft creation is <5 minutes for this sample (and measured across a representative workload per performance tests).
10. Duplicate detection test: submit duplicate email with same customer PO number; system must mark as duplicate and prevent duplicate draft creation.

# 24. Approvals
- Business and governance approvals listed in BRD to be obtained before release:
  - AI Governance Council
  - Finance (BIR)
  - AI intake
  - Global Intake
  - C2P
  - WAB
- QA/Test sign-off: TBD – confirm with Product and QA Lead

---

Notes / Actions requiring confirmation
- Prepared by / Reviewed by names: TBD – confirm with QA Lead / Test Manager
- Test environment names, access and schedule: TBD – confirm with Infrastructure owner
- Test and defect tracking tools, automation frameworks and performance/security test tools: TBD – confirm with QA Lead
- Runbooks, exact retry/backoff policies and session timeout values: TBD – confirm with Architecture / Ops owners
- Any formal accessibility standard obligations and supported browser versions: TBD – confirm with Product/Accessibility owner