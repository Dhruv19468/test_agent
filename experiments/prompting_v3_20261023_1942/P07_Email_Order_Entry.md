# 1. Document Control
- Title: QA Test Plan  
- Version: 1.0  
- Application: Email Purchase Order Entry Automation  
- Prepared by: QA Lead, Quality Engineering (TBD – confirm with QA Lead)  
- Reviewed by: Test Manager (TBD – confirm with Test Manager)  
- Audience: Customer Service Operations, Product Owners, Architects, Development Team, QA Team, CS branches, SAP integration team  
- Purpose: Define the quality and test approach to validate Email Purchase Order Entry Automation MVP1 from PO email intake through extraction, customer/item matching, SAP validation and draft sales order creation and CSR review queue. MVP2 functionality (straight-through release, acknowledgements, EDI handling, analytics) is explicitly out of scope for MVP1 unless formally approved.

# 2. References
- Business Requirements Document (BRD) – Email Purchase Order Entry Automation, Version 1.0, Date 02 Mar 2026  
- Solution Architecture diagram: P07_Email_Order_Entry_Architecture.png (architecture summary provided)

# 3. Test Objectives
- Verify extraction of customer PO number, sold-to, ship-to, requested delivery date and lines (customer part, description, quantity, UoM, price) from email body and PDF/Excel attachments.
- Verify customer identification (sender domain and PO content) and branch assignment.
- Verify item matching via customer cross-reference table, with fallback to catalog search (Azure AI Search).
- Verify SAP validation via APIM: customer active, material valid, price variance >5% flagged.
- Verify creation of a draft sales order (not released) and delivery to CSR review queue.
- Verify duplicate PO detection by customer PO number (100% detection in test set).
- Validate measurable NFR targets:
  - Draft order created within 5 minutes of email receipt for 95% of POs.
  - System supports peak 300 emails per hour.
  - Availability 99.5% 24x5.
- Verify RBAC and branch-based queue access (CSRs see only their branch queues).
- Validate AI governance and data quality targets from BRD: ≥95% header accuracy and ≥90% line accuracy on pilot customers (acceptance criteria).
- Confirm "No orders released without CSR action" for MVP1.

# 4. In Scope
- MVP1 functional scope (from BRD):
  - PO intake from branch order mailboxes via Microsoft Graph (branch mailboxes -> Event Grid -> Service Bus -> Order Extraction Service).
  - Extraction from email body and PDF/Excel attachments using Azure Document Intelligence and Azure OpenAI.
  - Customer identification by sender domain and PO content.
  - Item matching via customer cross-reference (uploaded by CS Admin) and Azure AI Search catalog fallback.
  - SAP validation via APIM (customer active, material valid, price variance >5% flagged).
  - Creation of draft sales orders (not released) in SAP and storage of drafts in Azure Cosmos DB.
  - CSR review queue (Web UI) with corrections and explicit release action reserved for CSRs.
  - Duplicate PO detection by customer PO number.
- Non-functional coverage in scope:
  - Availability: 99.5% 24x5.
  - Performance: draft within 5 minutes for 95% of POs; peak 300 emails/hour capacity.
  - Observability: end-to-end trace from email to SAP draft order number.
  - Security: Azure AD authentication; branch-based queue access; handling of confidential customer data.
  - Logging: capture emails processed, draft accuracy, CSR correction rate, time to draft (note: detailed logging specification is TBD – confirm with Monitoring Owner).

# 5. Out of Scope
- MVP2 items and explicit exclusions:
  - Straight-through release / automatic order release for trusted customers (MVP2).
  - Order acknowledgement emails (MVP2).
  - EDI detection and EDI fallback (MVP2).
  - Analytics (MVP2).
- Other BRD exclusions:
  - EDI orders, credit checks changes, quotations, returns.

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Customers send one PO per email in most cases.
  - Cross-reference files exist for top 200 customers and are uploaded monthly by CS Admin.
  - CS branches and CS Admin will participate in UAT and supply masked, production-like PO samples for pilot customers.
- Dependencies (from BRD / architecture):
  - SAP integration team to provide SAP S/4HANA sales order and pricing APIs via APIM.
  - Mailbox access approval for branch mailboxes (Graph API).
  - Azure Document Intelligence, Azure OpenAI and Azure AI Search availability in non-production via APIM.
  - Cosmos DB and Blob Storage for drafts and email copies respectively.
  - Event Grid and Service Bus for orchestration.
- Test constraints:
  - Test environments must not contain unmasked customer-sensitive data (customer data confidential per BRD).
  - Any missing integration endpoints, production-like cross-reference files, or mailbox access must be replaced with approved mocks (TBD – confirm with Integration Owner).

# 7. Test Strategy
- Approach:
  - Requirement-driven test design with risk-based prioritisation targeting BRD acceptance criteria and NFRs.
  - Combine automated API/contract tests and data-driven extraction validation with manual exploratory and UAT by CSRs.
- Test levels:
  - Unit tests (developer-owned) for extraction mappers, customer identification, item match logic and APIs (target test coverage: TBD – confirm with Development Lead).
  - Component tests for Order Extraction Service, Order Creation Service, Web UI, APIM integrations and AI calls.
  - API and contract tests for APIM -> Azure AI services and APIM -> SAP; include schema validation, authentication, error codes and retry behaviour.
  - Integration tests: Graph API mailbox -> Event Grid -> Service Bus -> Order Extraction Service -> Order Creation Service -> Cosmos DB -> SAP via APIM.
  - System tests: end-to-end PO email -> draft creation -> CSR review queue scenarios.
  - UAT: CSRs and CS Supervisors using representative branch queues and pilot customer data.
  - Regression testing: extraction, matching and SAP validation scenarios after model/prompt or mapping changes.
- Test types and techniques:
  - Positive and negative testing, boundary-value analysis, equivalence partitioning, pairwise for combinations of attachment types, file formats (PDF/Excel), currencies and UoM.
  - Exploratory testing focused on unusual PO layouts and multi-attachment emails.
  - Data-driven tests using golden datasets for pilot customers.
  - Security and privacy testing (pen tests and SAST/DAST) prior to release (TBD – confirm schedule with Security Owner).

# 8. Functional Test Coverage
For every MVP1 functional requirement and user story below we list what will be verified.

H2: PO Intake (mailboxes)
- Verify Event Grid receives new mail events from Branch Mailboxes (Graph API) for:
  - Single PO email, multiple attachments, combined body + attachment POs.
  - Non-PO emails (noise) are ignored or routed correctly.
  - Duplicate email deliveries and re-delivery scenarios.
  - Mailbox unavailable / Graph API errors -> retry and monitoring alerts.
- Verify system persists email copy to Azure Blob Storage per architecture line: APIM -> Azure Blob Storage | HTTPS/443 Managed Identity.

H2: Manual / alternative intake (if applicable)
- If manual upload UI exists in MVP1 (confirm with Product Owner): tests for upload of PDF and Excel attachments; invalid/corrupt files produce clear errors and do not create partial drafts (TBD – confirm with Product Owner).

H2: Extraction (Azure Document Intelligence + Azure OpenAI)
- Verify extraction of header fields: customer PO number, sold-to, ship-to, requested delivery date.
- Verify extraction of line fields: customer part, description, quantity, UoM, price.
- Verify multi-page attachments and tables spanning pages; Excel attachment parsing.
- Verify extraction of negative/zero quantities are flagged as invalid per data quality rule (line quantity > 0).
- Verify UoM validity check against SAP master data (UoM valid in SAP).
- Verify source reference for fields (email body vs attachment and page/cell reference) is captured (TBD – confirm field names with Data Owner).
- Verify confidence score is reported per field (CS Admin can upload/maintain thresholds). Numerical thresholds for pass/fail are TBD – confirm with CS Admin.

H2: Customer Identification
- Verify identification by sender domain and PO content:
  - Emails from known sender domain map to customer.
  - Conflicting signals (sender domain differs from PO header) produce a flagged exception for CSR review.
- Verify branch assignment based on mailbox (CSRs see only their branch queue).

H2: Item Matching
- Verify match attempt via customer cross-reference table:
  - Exact match of customer part -> mapped material code.
  - If cross-reference missing, fallback to Azure AI Search catalog lookup.
- Verify correct handling when no match found: line highlighted for CSR with suggested catalog hits.
- Verify CS Admin upload of cross-reference file (monthly) is accepted and used in matching (upload validation tests).

H2: SAP Validation and Business Rules
- Verify SAP master data checks via APIM:
  - Customer active check.
  - Material validity check.
  - UoM valid check.
- Verify price variance rule:
  - Business rule: price variance >5% flagged.
  - Test cases:
    - SAP price 100.00, submitted price 105.00 → NOT flagged (exactly 5% is allowed).
    - SAP price 100.00, submitted price 105.01 → flagged as price variance >5%.
    - Negative/zero prices flagged as invalid.
  - Currency mismatch scenarios flagged as exception.
- Verify duplicate PO detection by customer PO number:
  - Same customer PO number submitted twice → second instance flagged as duplicate.
  - Duplicate detection must be 100% in the provided test duplicate set (acceptance criterion).

H2: Draft Sales Order Creation
- Verify draft sales order creation via Order Creation Service -> SAP S/4HANA via APIM (validate API call and response handling).
- Verify drafts persist to Azure Cosmos DB per architecture (Order Creation Service -> Azure Cosmos DB | drafts).
- Verify E2E traceability: email ID -> draft order identifier returned from SAP.
- Verify that drafts are NOT automatically released in MVP1 (No automatic release; acceptance criterion: No orders released without CSR action).

H2: CSR Review Queue & UI
- Verify Web UI shows draft orders per branch (branch-based access).
- Verify fields and field-level confidence shown to CSR.
- Verify CSR can correct header and line fields and submit corrected draft for release only by CSR action.
- Verify CS Supervisor views: monitoring, reassign orders, and seeing orders older than 30 minutes flagged (user story).
- Verify actions and validations on release action are disabled until CSR explicit action.

H2: Duplicate and Error Handling
- Verify duplicate detection prevents creation of duplicate drafts or flags duplicates for CSR review (as per requirement).
- Verify idempotency: reprocessing same Event Grid event does not create duplicate drafts.

H2: Edge cases and negative scenarios
- Excel attachments with multiple sheets, password-protected files, corrupted attachments -> clear error and no partial drafts (if password-protected handling is out of scope, system should surface appropriate error).
- Multiple POs in single email (contradiction to assumption) -> test system behaviour and flag for CSR (TBD – confirm desired behaviour with Business Owner).

# 9. Roles, Permissions and Workflow Testing
- Roles to test (from BRD): CSR, CS Supervisor, CS Admin.
- Verify RBAC and segregation:
  - CSR: permitted to review draft orders, correct lines, release orders in SAP (CSR release action). Restricted from CS Admin functions.
  - CS Supervisor: permitted to monitor queue and SLAs, reassign orders. Verify view-only or elevated rights per design (TBD – confirm exact Supervisor permissions with Product Owner).
  - CS Admin: permitted to maintain mailbox routing, upload customer cross-reference, and configure confidence thresholds. Restricted from performing CSR release (segregation of duties).
- Verify branch-based access: CSRs can only view and act on orders for their assigned branch.
- Verify session timeout, Azure AD authentication, and SSO behaviour (App Gateway -> APIM -> AD/SSO).
- Verify that no user other than CSR can release orders in MVP1 (enforced both in UI and API layers).

# 10. Security, Privacy and Compliance Testing
- Authentication/Authorization:
  - Azure AD sign-on and role assignment; verify SSO flows: CSR Users -> App Gateway | HTTPS/443 AD/SSO.
  - Verify branch-based queue scoping enforces least privilege.
- Data protection:
  - Confirm customer data confidentiality handling: encrypted at rest (Cosmos DB, Blob Storage) and in transit (HTTPS/443). Detailed encryption controls TBD – confirm with Security Owner.
  - Verify that logs and exports do not expose sensitive customer data (masking where required).
- Threat testing:
  - Malicious attachment tests (malformed PDFs, macros in Excel), injection strings in extracted fields.
  - Rate limiting and DoS protection for Graph API / APIM endpoints (TBD – confirm threshold values with Architecture Owner).
- Compliance:
  - Verify AI Governance Council approvals are recorded for model/prompt versions used in extraction and mapping.
  - Verify auditability for changes to cross-reference uploads and confidence thresholds (CS Admin actions logged).
- Penetration tests and SAST/DAST to be scheduled before release (TBD – confirm with Security Owner).

# 11. AI and Data Quality Validation
- Golden datasets:
  - Use labelled golden dataset from pilot customers to measure extraction accuracy.
  - Acceptance targets (BRD): ≥95% header field accuracy and ≥90% line accuracy on pilot customers.
- Extraction validation:
  - Measure precision/recall for header and line fields separately; record per-field accuracy and per-document accuracy.
  - Track confidence scores returned by Azure Document Intelligence / Azure OpenAI and correlate with actual accuracy to validate CS Admin thresholds (threshold numeric values are TBD – confirm with CS Admin).
- Responsible AI checks:
  - Verify Azure OpenAI mapping does not alter numeric fields (quantities, prices, UoM, material codes).
  - Record model/prompt and APIM route versions per processed email for traceability.
  - Reprocess sample set after model/prompt changes and compare outputs; track regression.
- Error handling:
  - For low-confidence fields (per CS Admin thresholds) ensure flagged for CSR review.
  - Verify fallback logic to Azure AI Search when cross-reference missing.
- Change control:
  - Reprocessing and model update policy and test coverage for model changes are TBD – confirm with AI Governance Council.

# 12. Performance Testing
- Targets (from BRD / NFR):
  - Draft order created within 5 minutes of email receipt for 95% of POs.
  - Peak load target: 300 emails per hour.
  - Availability: 99.5% 24x5.
- Performance tests:
  - Single-message latency: measure time from Graph API event to draft order creation (end-to-end) using representative pilot emails (text-based, scanned PDFs, Excel).
  - Load tests:
    - Sustained load: 300 emails/hour sustained for 2 hours (measure queue depths, Service Bus throughput, processing time percentiles).
    - Spike tests: bursts up to TBD – confirm acceptable burst (TBD – confirm with Architecture Owner).
  - Concurrency tests: multiple concurrent CSR users accessing review queue (TBD number of concurrent CSRs – confirm with Customer Service Ops).
- Success criteria:
  - 95th percentile end-to-end <= 5 minutes for 95% of processed POs.
  - System maintains correct behaviour and does not drop events at specified peak.
- Monitoring:
  - Instrumentation to measure processing time, Service Bus queue length, APIM latency, SAP API response times.

# 13. Reliability and Recovery Testing
- Scenarios:
  - Event Grid / Service Bus outages and retries – verify idempotency and no duplicate drafts.
  - Partial failure: Order created in Cosmos DB but SAP call failed – verify reconciliation and retry logic.
  - Mailbox unavailability (Graph API errors) – verify alerts, retries and fallback behaviour.
  - Component restarts (Order Extraction Service, Order Creation Service) during processing – verify safe retries and eventual consistency.
- Recovery verification:
  - After simulated outage, process backlog of events and validate no loss or duplication.
  - Verify monitoring alerts trigger and runbooks for manual intervention (runbooks TBD – confirm with Ops Owner).

# 14. Accessibility and Compatibility Testing
- Accessibility:
  - Web UI (Review Queue) must support enterprise accessibility basics: keyboard navigation, focus order, screen-reader labels and sufficient colour contrast (detailed WCAG conformance level TBD – confirm with Accessibility Owner).
- Browser compatibility:
  - Test Web UI on enterprise-supported browsers (Edge, Chrome, Firefox). Exact supported versions TBD – confirm with Frontend Owner.

# 15. Logging, Monitoring and Audit Testing
- Verify E2E traceability per BRD: each email maps to Cosmos DB draft and SAP draft order number.
- Logging requirements to verify:
  - Capture: email identifier, customer PO number, branch mailbox, extraction model version, per-field confidence, matching decisions, SAP validation results, draft order id, user corrections, and release action (if any).
  - Ensure logs respect confidentiality (no sensitive customer data in cleartext).
  - Verify retention settings and access controls for logs (TBD – confirm retention period with Compliance Owner).
- Monitoring:
  - Dashboards for processing rate, draft latencies, queue depth, error rates and AI extraction accuracy metrics (detailed metrics TBD – confirm with Monitoring Owner).
- Audit:
  - CS Admin uploads and configuration changes must be auditable.
  - AI model/prompt version logged per processed email (for governance).

# 16. Test Environments and Test Data
- Environments:
  - Development, Integration/QA, Performance and UAT environments (labels and subscriptions TBD – confirm with Environment Owner).
  - Non-production must contain APIM access to Azure AI services and SAP test endpoints or approved mocks.
- Test data sets:
  - Golden dataset per pilot customer: masked, labelled emails (body + attachments) with expected extraction outputs.
  - Invalid dataset: malformed attachments, multiple PO per email, corrupt files, password-protected Excel (if supported), negative quantities.
  - Boundary dataset: price variance exactly 5.00% (e.g., SAP price 100.00 vs 105.00), price variance 5.01%, quantity zero or 1 unit over usual values.
  - Duplicate dataset: identical customer PO number repeated to verify duplicate detection.
- Data ownership and classification (from BRD Data Sources):
  - PO emails – Source: Branch mailboxes | Frequency: Continuous | Owner: Customer Service | Security: Confidential
  - Customer cross-reference – Source: CS Admin upload | Frequency: Monthly | Owner: Customer Service | Security: Internal
  - SAP master data – Source: SAP | Frequency: On demand | Owner: Master Data | Security: Confidential
  - Draft orders – Source: Tool output | Frequency: Per email | Owner: Customer Service | Security: Confidential
- Test data management:
  - All production-like data must be masked; unmasked data in test environments is not permitted.
  - Record model/prompt/APIM versions and dataset versions for each test run.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:
  - BRD approved and requirements baselined (BRD Version 1.0, Date 02 Mar 2026).
  - Test environments provisioned with Event Grid, Service Bus, APIM, Cosmos DB, Blob Storage and access to Azure AI services or approved mocks.
  - Branch mailbox test accounts available via Graph API or mocks.
  - Golden datasets for pilot customers available and labeled.
  - Development build deployed with unit-test evidence (TBD – confirm required unit test evidence with Development Lead).
- Suspension criteria:
  - Critical blocking defect in core ingestion or extraction preventing progress.
  - SAP test APIs unavailable for >24 hours without approved mock replacement.
  - Major security vulnerability discovered preventing testing to proceed.
- Exit criteria:
  - Functional: All critical-path test cases passed (intake, extraction, matching, SAP validation, draft creation, CSR review).
  - Quality thresholds (as per BRD acceptance criteria):
    - Header field accuracy ≥95% on golden dataset for pilot customers.
    - Line item accuracy ≥90% on golden dataset for pilot customers.
    - Draft creation within 5 minutes for 95% of POs (measured in performance tests).
    - Duplicate PO detection validated as 100% in duplicate test set.
    - Confirmation that no orders were automatically released in MVP1 (verified through audit logs and SAP draft status).
  - Non-functional:
    - Performance: 95th percentile and acceptance metrics met for draft creation and peak throughput.
    - Availability: monitoring indicates readiness to meet 99.5% 24x5 (operational readiness checks TBD).
  - Security: no open Critical security defects; scheduled pen test or mitigation plan accepted.
  - UAT: CSRs and CS Supervisor sign-off on representative UAT scenarios.
  - All remaining open defects are documented with mitigations and business acceptances.

# 18. Defect Management
- Severity levels (aligned to business impact):
  - Critical: Wrong matching/validation decision or data corruption leading to incorrect draft orders (e.g., price variance >5% flagged as OK, automatic release of order). Requires immediate remediation.
  - High: Core workflow blocked or critical control failure (e.g., drafts not created for valid POs, duplicate detection disabled).
  - Medium: Function works with a documented workaround (e.g., one attachment type needs manual pre-processing).
  - Low: Cosmetic or non-blocking UI/UX issues.
- Defect process:
  - Defects logged in tracking tool (TBD – confirm with QA Lead).
  - Each defect must include steps to reproduce, environment, build, expected/actual, evidence (logs/screenshots), severity and owner.
  - Weekly triage with Product, Dev and QA to prioritise fixes (schedule TBD – confirm with Stakeholders).

# 19. Risks and Mitigations
- Risk: Unusual PO layouts reduce extraction accuracy.  
  - Mitigation: Golden dataset representative of layout variants; fallbacks to CSR review and catalog search; tune Document Intelligence models.
- Risk: Missing or late mailbox access / Graph API permissions.  
  - Mitigation: Use approved mocks; escalate to Mailbox Owner; early validation of mailbox connectivity.
- Risk: SAP API rate limits or unavailability.  
  - Mitigation: Queueing via Service Bus, exponential backoff/retry, and contract tests with SAP integration team.
- Risk: Cross-reference files incomplete for many customers.  
  - Mitigation: Catalog search fallback; highlight unmatched lines to CSR; prioritise cross-reference onboarding for top customers.
- Risk: AI model/prompt changes cause regressions.  
  - Mitigation: Record model/prompt version per email, re-run regression on golden dataset after any change, require AI Governance Council sign-off for model changes.

# 20. Test Deliverables and Reporting
- Planned deliverables:
  - Test plan (this document).
  - Test cases and test scripts mapped to BRD requirements (repository TBD – confirm with QA Lead).
  - Automated API/contract test suite.
  - Golden dataset and expected outputs.
  - Performance test reports (latency, throughput, percentiles).
  - Security test reports (SAST/DAST / pen test summary).
  - UAT sign-off artifacts from CSRs and CS Supervisors.
  - Defect reports and triage logs.
- Reporting cadence:
  - Weekly QA status report: planned/executed/passed/failed/blocked, key defects, extraction accuracy metrics, performance KPIs, UAT progress (reporting owner and distribution list TBD – confirm with QA Lead).

# 21. Traceability and Metrics
- Traceability:
  - Map every BRD requirement and user story to test cases and evidence. Requirements to be mapped in traceability matrix (tool and location TBD – confirm with QA Lead).
- Key metrics to capture:
  - Extraction accuracy: header and line item accuracy per pilot customer and overall.
  - Draft creation latency: median, 95th and 99th percentiles; percent <= 5 minutes.
  - Throughput: emails processed per hour, Service Bus queue lengths.
  - Duplicate detection success rate (percent detected in duplicate test set; acceptance 100%).
  - CSR correction rate and types of corrections (field-level).
  - Defect counts by severity and ageing.
  - Availability measured against 99.5% 24x5.
  - AI model/prompt versions and regression results.

# 22. Test Schedule
- High-level milestones (from BRD High-Level Plan):
  - MVP1 build: Apr–Jul 2026 (BRD).
  - Detailed test schedule, phase dates, and UAT windows: TBD – confirm with Program Manager and Customer Service Operations.
- Suggested sequencing (to be confirmed):
  - Component & API tests as services become available.
  - Integration tests once APIM, Event Grid, Service Bus, Cosmos DB and Blob Storage are ready.
  - Performance tests after stable integration environment is available.
  - UAT with CS branches following sign-off on exit criteria from system testing.

# 23. End-to-End Scenario
Representative E2E scenario to validate core flow:
- Step 1: A PO email arrives in a Branch Mailbox (Graph API -> Event Grid -> Service Bus).
- Step 2: Order Extraction Service persists email copy to Azure Blob Storage and extracts header and line fields using Azure Document Intelligence and Azure OpenAI (via APIM).
- Step 3: Customer identification performed using sender domain and PO content; branch determined by mailbox.
- Step 4: Item matching attempted using customer cross-reference; missing matches fallback to Azure AI Search catalog via APIM.
- Step 5: Order Creation Service validates customer, material and price with SAP S/4HANA via APIM. Price variance exactly 5% is allowed; >5% is flagged.
- Step 6: Draft sales order created in SAP (Order Creation Service -> SAP via APIM) and draft persisted to Azure Cosmos DB.
- Step 7: Draft appears in CSR Web UI review queue for the branch; CSR reviews, corrects a line (e.g., resolves a missing cross-reference), and explicitly releases the order in SAP (release action is performed by CSR only — verify that no other role can perform release).
- Step 8: Verify end-to-end traceability: email id -> draft id in Cosmos DB -> SAP draft order number recorded in logs; verify extraction model/prompt version logged.

# 24. Approvals
- Required business/oversight approvals per BRD:
  - AI Governance Council
  - Finance (BIR)
  - AI intake
  - Global Intake
  - C2P
  - WAB
- QA sign-off:
  - QA Lead (TBD – confirm)
  - Product Owner / Customer Service Operations sign-off on UAT (TBD – confirm)
  - Security Owner sign-off on final security testing (TBD – confirm)

---

Notes / Open items (TBD – actions required)
- Test tools and defect tracking tool: TBD – confirm with QA Lead.
- Exact numerical confidence thresholds for field-level routing and CS Admin configuration values: TBD – confirm with CS Admin.
- Monitoring dashboard definitions and metric owners: TBD – confirm with Monitoring Owner.
- Detailed schedule and UAT dates within MVP1 (Apr–Jul 2026): TBD – confirm with Program Manager.
- Environment names and subscriptions for test execution: TBD – confirm with Cloud/Environment Owner.