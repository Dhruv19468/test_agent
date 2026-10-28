# 1. Document Control
- Title: QA Master Test Plan  
- Version: 1.0  
- Application: Email Purchase Order Entry Automation  
- Prepared by: QA Lead, Quality Engineering  
- Reviewed by: Test Manager, Product Owner, Architecture Lead  
- Audience: Customer Service Operations, CS Admins, CS Supervisors, CSRs, Architects, Development Team, QA Team  
- Purpose: Define the quality approach, scope, entry/exit criteria and measurable test activities required to validate Email Purchase Order Entry MVP1 from PO intake through extraction, item matching, SAP validation and draft sales order creation for CSR review.

# 2. References
- Business Requirements Document (BRD) – Email Purchase Order Entry Automation, Version 1.0, 02 Mar 2026 (Customer Service Operations)
- Solution architecture diagram: P07_Email_Order_Entry_Architecture.png (architecture summary provided)

# 3. Test Objectives
- Verify PO intake from branch mailboxes via Microsoft Graph is received and triggers processing end-to-end.
- Verify duplicate PO detection by customer PO number (100% detection in test set).
- Validate extraction of customer PO number, sold-to, ship-to, requested delivery date and lines (customer part, description, quantity, UoM, price) using Azure Document Intelligence and Azure OpenAI with per-field confidence displayed.
- Validate customer identification by sender domain and PO content.
- Validate item matching via customer cross-reference table and fallback to catalog search (Azure AI Search).
- Validate SAP validation via APIM: customer active, material valid, pricing check with price variance >5% flagged.
- Verify creation of draft sales order in SAP (draft only) within 5 minutes for 95% of POs.
- Verify CSR review queue, ability to correct lines, and that no automatic release occurs in MVP1 (human review required for every order).
- Validate RBAC: CSRs see only branch queues; CS Admins can upload cross-reference files and configure confidence thresholds; CS Supervisors see SLA flags.
- Verify non-functional targets: Availability 99.5% 24x5; Peak handling 300 emails/hour; Observability – end-to-end trace per email to SAP draft order number.
- Provide measurable acceptance evidence against BRD acceptance criteria: ≥95% header accuracy and ≥90% line accuracy (pilot customers), draft within 5 minutes for 95% of POs, duplicate detection 100% in test set, and no releases without CSR action.

# 4. In Scope
Functional (MVP1):
- T01: Intake from branch order mailboxes via Microsoft Graph (Event Grid trigger -> Service Bus -> Order Extraction Service)
- T02: Duplicate PO detection by customer PO number
- T03: Extraction of header and lines (Azure Document Intelligence + Azure OpenAI)
- T04: Customer identification by sender domain and PO content
- T05: Item matching via customer cross-reference table then Azure AI Search catalog fallback
- T06: SAP validation via APIM (customer active, material valid, pricing check; flag price variance >5%)
- T07: Creation of draft sales orders in SAP (draft only)
- T08: CSR review queue with correction capability (release action present but manual)
- T09: Display of confidence per field in Web UI
- T10: Highlight lines with missing customer cross-reference
- T11: SLA flag for orders older than 30 minutes in queue (visible to CS Supervisor)
- T12: CS Admin capability to upload customer cross-reference file and manage confidence thresholds
Non-functional:
- T29: Availability 99.5% 24x5
- T31/T32: Performance – draft order created within 5 minutes for 95% of POs; peak 300 emails/hour
- T33: Observability – end-to-end trace per email
- Security: Azure AD (Entra ID) authentication and branch-based queue access
- Data stores: Azure Blob Storage for emails; Azure Cosmos DB for drafts

# 5. Out of Scope
List of explicit MVP2 items and other exclusions from BRD:
- T13: Straight-through release for trusted customers (MVP2)
- T14: Order acknowledgement emails (MVP2)
- T15: EDI fallback detection (MVP2)
- T16: Analytics (MVP2)
- T71: No straight-through release in MVP1
- T72: No acknowledgements in MVP1
- T73: No EDI handling in MVP1
- T74: No analytics in MVP1
- Additional BRD exclusions: EDI orders, credit checks changes, quotations, returns

# 6. Assumptions and Dependencies
Assumptions (from BRD / TEST BASIS):
- T75: Customers send one PO per email in most cases.
- T76: Cross-reference files exist for top 200 customers.
- T77: System integration details (APIM, Event Grid, Service Bus) to be validated with backend architects.
Dependencies:
- T78: SAP integration team for APIM access and validation test data.
- T79: Mailbox access approval for branch mailboxes (Graph API).
- T80: CS branches participation for UAT.
- Test data must be masked for customer confidential data; AI Governance Council approval required (T66).
Constraints:
- If any integration is unavailable in non-production, approved mocks must be used (T77). Mocks and test harness approaches: TBD – confirm with Customer Service Operations and Architecture Lead.

# 7. Test Strategy
Levels of testing:
- Unit testing: developer responsibility for extraction mappers, cross-reference loader, matching logic and API clients.
- Component testing: Order Extraction Service, Order Creation Service, Web UI Review Queue, APIM connectors to Azure Document Intelligence, Azure OpenAI and Azure AI Search.
- Contract/API testing: APIM -> SAP, APIM -> Azure Document Intelligence, APIM -> Azure OpenAI, APIM -> Azure AI Search, Graph API mailbox ingestion, Event Grid -> Service Bus contracts (schemas, authentication, error codes, idempotency).
- Integration testing: end-to-end between Branch Mailboxes (Graph API) -> Azure Event Grid -> Azure Service Bus -> Order Extraction Service -> Order Creation Service -> Azure Cosmos DB -> SAP (via APIM).
- System testing: full scenarios including duplicates, cross-reference missing, SAP validation failures and SLA flagging.
- Performance and scalability testing: peak 300 emails/hour and draft within 5 minutes for 95% of POs.
- UAT: CSR and CS Supervisor validation on pilot branches and pilot customers.
Test techniques:
- Requirements-based test design, equivalence partitioning, boundary-value analysis, negative testing, exploratory testing, pairwise for combinations of sender domain and cross-reference state, data-driven tests for confidence thresholds.
Test automation:
- Regression automation for API contracts and extraction validation (tooling: TBD – confirm with QA Manager).
Test data management:
- Golden labelled dataset for pilot customers (see T26) and test sets for duplicates (T27). Data masking required.

# 8. Functional Test Coverage
Covering each MVP1 functional requirement and user story (mapped to TEST BASIS):

- Intake from branch mailboxes (T01, T49):
  - Verify Event Grid receives new-mail events from Branch Mailboxes (Graph API).
  - Verify Event Grid -> Service Bus event publish and ordering.
  - Verify Order Extraction Service consumes Service Bus messages and stores email copy to Azure Blob Storage (T52, T53).
  - Failure modes: mailbox unavailable, malformed email, oversized attachments; expected behavior: retry, dead-letter to review queue and CS Admin notification (TBD – confirm with owner for notification behaviour).

- Duplicate PO detection (T02, T19, T27):
  - Test case: identical customer PO number received twice within dataset → second message flagged as duplicate; expected: duplicate detection 100% on test set.
  - Edge cases: same PO number from different customers (should not be flagged), different formatting of PO number (leading/trailing spaces, case) normalized and compared.

- Extraction of header and lines (T03, T63):
  - Verify extraction of customer PO number, sold-to, ship-to, requested delivery date, and every line field (customer part, description, quantity, UoM, price).
  - Source technologies: Azure Document Intelligence + Azure OpenAI via APIM (T45, T46).
  - Validate multi-attachment emails (body text + PDF + Excel), scanned PDFs, Excel attachments parsing, multi-page PO tables, decimal precision, negative or zero quantities (quality rule: line quantity must be > 0 - T21).
  - Verify per-field source page/attachment reference and confidence value displayed in UI (T09, T63).

- Customer identification (T04):
  - Verify identification via sender domain and PO content: positive match, ambiguous match (multiple possible customers) flagged for CSR, unknown domain fallback.
  - Test cases: sender domain present in cross-reference; sender domain absent but customer ID present in PO body.

- Item matching (T05):
  - Verify matching via uploaded customer cross-reference table (T12, T59) first, then Azure AI Search catalog fallback (T47).
  - Test: customer part with cross-reference → matched to material; missing cross-reference → fallback catalog search returns exact/closest hits; no match → highlighted in UI (T10).

- SAP validation & pricing variance (T06, T18):
  - Verify APIM call to SAP checks: customer active, material valid, price check.
  - Pricing rule: price variance >5% flagged. Test numerical boundaries: exactly 5.00% → not flagged? BRD states price variance >5% flagged; therefore 5.00% should not be flagged; 5.01% must be flagged.
  - Verify UoM valid in SAP (T22) and line quantity > 0 (T21).
  - Verify response handling for SAP timeouts, errors and retries (T83 mitigation).

- Draft sales order creation (T07, T25, T36):
  - Verify Order Creation Service posts draft order via APIM to SAP and that SAP returns a draft order number recorded in Azure Cosmos DB (T56).
  - Performance: draft order created within 5 minutes of email receipt for 95% of POs (T31, T36). Test measured from Event Grid timestamp to SAP draft order creation timestamp.
  - Verify no automatic order release occurs in MVP1 (T17, T71, T87).

- CSR review queue and corrections (T08, T37, T38):
  - Verify Web UI shows draft orders in CSR's branch queue (RBAC T23) with per-field confidence and edit capability.
  - Verify corrected lines are persisted and revalidated against SAP prior to CSR releasing the order in SAP.
  - Verify release action exists but UAT confirms manual release only (T87).

- Confidence thresholds and admin actions (T12, T64):
  - CS Admin can upload cross-reference file and set confidence thresholds; tests include malformed upload, duplicate keys, large file, and successful upload applied to matching logic.
  - Verify thresholds affect highlighting/flags displayed to CSRs.

- SLA and Supervisor view (T11, T39):
  - Verify orders older than 30 minutes are flagged in the queue and visible to CS Supervisor; test with simulated timestamps and queue monitoring.

- Logging, tracing and observability (T33):
  - Verify correlation IDs exist end-to-end (Event Grid -> Service Bus -> Extraction -> APIM -> SAP) and SAP draft order number is present in trace.
  - Metrics: emails processed, draft accuracy, CSR correction rate, time to draft (logging spec TBD – confirm with Monitoring Owner).

# 9. Roles, Permissions and Workflow Testing
Validate role behaviour per BRD / TEST BASIS:
- CSR (T38, T23):
  - Permissions: view branch queue only, review draft orders, correct lines, initiate release to SAP (manual), cannot upload cross-reference or configure thresholds.
  - Tests: verify CSRs cannot see other branches’ queues; verify UI actions allowed; verify attempt to access admin endpoints is rejected.
- CS Supervisor (T39):
  - Permissions: monitor queue and SLAs, reassign orders, view flagged orders older than 30 minutes.
  - Tests: reassign action works; SLA flag visibility; cannot upload cross-reference.
- CS Admin (T40, T24):
  - Permissions: upload customer cross-reference files, manage mailbox routing and confidence thresholds.
  - Tests: upload success/failure paths; upload audit logging; verify Admin cannot release orders (segregation of duties).
- RBAC tests:
  - Authentication: Azure AD (Entra ID) via App Gateway (T41–T44) including token validation and expiry.
  - Verify branch-based access mapping to queues (T23).
  - Verify session timeout and inactive account handling (TBD – confirm session timeout with Security Owner).

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization:
  - Verify Azure AD (Entra ID) SSO via App Gateway, OAuth2.0 flows and role assignment (T43).
  - Verify CSRs restricted to branch queues; Admin and Supervisor roles constrained.
- Data protection:
  - Verify email and draft storage in Azure Blob Storage and Azure Cosmos DB are encrypted at rest and in transit (APIM -> Blob Storage via Managed Identity, T48).
  - Verify customer confidential data is masked in UIs and logs where required (T58, T61), per AI Governance Council.
- Threat & vulnerability checks:
  - Test malicious attachments, file upload exploits, injection in extracted fields and overflow conditions.
  - Verify rate limiting and abuse protection (TBD – confirm with Security Owner).
- Compliance & approvals:
  - Verify AI Governance Council approval tracking for AI components (T66).
  - Verify logging for Admin upload actions and configuration changes.

# 11. AI and Data Quality Validation
- Golden dataset and accuracy targets:
  - T26/T84/T85: Validate extraction accuracy using pilot customer labelled dataset: ≥95% header field accuracy and ≥90% line accuracy. Measure separate metrics for numeric vs text fields and capture precision/recall.
- Confidence per field (T63) and thresholds (T64):
  - Verify confidence values returned by Azure Document Intelligence / Azure OpenAI are displayed per-field.
  - Verify CS Admin can configure thresholds; confirm threshold effects (highlighting, routing) align with configuration.
- Responsible AI / hallucination controls:
  - Verify Azure OpenAI mapping does not alter numeric fields (prices, quantities, UoM) or material codes.
  - Verify model and prompt version recorded per invoice for audit.
  - Reprocessing: verify re-run with new model produces new extraction version and is auditable (T11 traces).
- Test cases:
  - False positive/negative analysis: track when extracted field is wrong but high confidence; route to CSR and log.
  - Edge cases: ambiguous part descriptions, OCR errors in scanned PDFs, multiple currencies (if present).

# 12. Performance Testing
Measure against NFRs (T29, T31, T32):
- Targets:
  - Draft order creation within 5 minutes for 95% of POs (T31/T36).
  - System able to handle peak 300 emails per hour (T32).
  - Availability 99.5% 24x5 (T29).
- Tests:
  - Throughput tests: ramp to 300 emails/hour sustained and measure end-to-end latency, Service Bus depth and APIM/SAP concurrency effects.
  - Latency distribution: measure median, 95th and 99th percentile time from Event Grid message to SAP draft order creation.
  - Load tests with different mixes: many small orders, large multi-page attachments, Excel attachments.
  - Concurrency: multiple CSR users accessing Review Queue (TBD – confirm targeted concurrent user counts with Product Owner).
- Monitoring:
  - Track queue depth, processing time per component, error rates, API rate-limit responses from SAP.

# 13. Reliability and Recovery Testing
- Resilience tests:
  - Service restarts during processing; ensure idempotency and no duplicate draft orders.
  - Event Grid / Service Bus interruptions and reconnection with message replay/poison-message handling.
  - APIM -> SAP timeouts and retries; verify queueing/back-off behaviour (T83).
- Recovery tests:
  - Simulate Azure Blob Storage unavailability and verify fallback behaviour.
  - Data reconciliation after recovery: ensure drafts reflect final extracted/corrected data and no data loss.
- Disaster scenarios:
  - Simulate long SAP outage and verify system queues and that no releases occur automatically.
- Observability:
  - Alerts and runbooks (TBD – confirm with Operations Owner).

# 14. Accessibility and Compatibility Testing
- BRD does not define explicit accessibility targets. Confirm requirements: TBD – confirm with Customer Service Operations.
- Web UI compatibility: confirm enterprise-supported browsers and versions (TBD – confirm with Customer Service Operations). Minimal tests: UI rendering and basic functionality on modern Edge/Chrome as available in test environments (confirmation required).

# 15. Logging, Monitoring and Audit Testing
- Verify structured logs, correlation IDs, and per-email trace to SAP draft order number (T33).
- Audit records must capture: event timestamp, sender, customer resolved, cross-reference version, confidence per field, matching decisions, SAP draft order number, user corrections and Admin uploads.
- Verify Cosmos DB contains draft order records (T56) and is queryable by invoice/message ID.
- Confirm retention and exportability of logs (TBD – confirm retention policy with Security/Compliance Owner).
- Verify monitoring: metrics for emails processed, draft accuracy, CSR correction rate, time to draft.

# 16. Test Environments and Test Data
Environments:
- Non-production Subscription environment mirroring architecture (Order Extraction Service, Order Creation Service, APIM, Azure Document Intelligence, Azure OpenAI, Azure AI Search, Azure Event Grid, Azure Service Bus, Azure Blob Storage, Azure Cosmos DB, App Gateway, Azure AD) per architecture notes.
- Isolated dev, QA/integration, performance and UAT environments.
- Where enterprise integrations unavailable, use approved mocks for Branch Mailboxes (Graph API) and SAP (APIM) – TBD – confirm with SAP integration team.
Test data:
- Golden labelled dataset for pilot customers (T26), including body-text orders, PDF orders, Excel attachments, multi-page POs and scanned PDFs.
- Duplicate PO test set (T27).
- Edge and negative cases: missing mandatory headers (T20), zero/negative quantities (T21), invalid UoM (T22), price variance exactly 5% and >5% (T18).
- Masking: no unmasked customer confidential data allowed; masked or synthetic invoices must be used.
- Record dataset, model and prompt versions used for each test run.

# 17. Entry, Suspension and Exit Criteria
Entry criteria:
- BRD approved and requirements baselined.
- Non-production environment provisioned with required integrations or approved mocks (APIM, Event Grid, Service Bus, Azure Document Intelligence, Azure OpenAI, Azure AI Search).
- Mailbox test accounts available and seeded with test messages.
- Golden dataset and duplicate test sets available and loaded.
- Build deployed with unit-test evidence and component tests passed.
Suspension criteria:
- Critical integration (Graph API, Service Bus, APIM to SAP) unavailable for more than agreed window (TBD – confirm with Architecture Lead).
- Security blocking findings (Critical) discovered.
Exit criteria (must be met for release decision):
- T84/T85: Extraction accuracy targets met on pilot dataset: ≥95% header, ≥90% line items.
- T86/T31/T36: Draft created within 5 minutes for 95% of POs in performance test runs.
- T87: No orders released automatically in MVP1; CSR review enforced.
- T27/T88: Duplicate PO detection validated 100% on test set.
- No open Critical defects and no open High-severity security defects.
- At least 95% of planned test cases passed with all critical-path cases passed.
- Observability and end-to-end traceability validated.
- Business sign-off from Customer Service Operations and UAT approval from CSRs and CS Supervisors.

# 18. Defect Management
- Severity definitions (aligned to business impact):
  - Critical: incorrect draft creation (wrong customer/material leading to shipment error), data corruption, security breach.
  - High: core workflow blocked (no drafts created), duplicate detection failing in production test set, RBAC breach allowing cross-branch access.
  - Medium: feature works with workaround (UI shows wrong confidence formatting), intermittent mismatch on catalog fallback.
  - Low: cosmetic/UI alignment, minor telemetry naming.
- Defect handling:
  - Track defects in project defect tracker (tooling: TBD – confirm with QA Manager).
  - Triage daily for Severity Critical/High; owner assigned to dev for fix; retest after fix.
  - Every defect record must include steps to reproduce, expected/actual, environment, data set, evidence (logs/screenshots), and root cause once available.

# 19. Risks and Mitigations
- Risk T81: Unusual PO layouts → Mitigation: labelled golden dataset, CSR review with confidence flags, iterative model tuning.
- Risk T82: Missing cross-references → Mitigation: Azure AI Search catalog fallback and highlight missing lines in UI for CSR correction.
- Risk T83: SAP API limits → Mitigation: queueing, retry/back-off and collaboration with SAP integration team to define limits.
- Data privacy risk: customer data exposure → Mitigation: masking in test data, role-based access and AI Governance Council approval.
- Dependency risk: mailbox access delays → Mitigation: use mocks for mailbox ingestion during integration testing.

# 20. Test Deliverables and Reporting
Deliverables:
- Test plan (this document)
- Test cases mapped to TEST BASIS (T01–T91) with pass/fail criteria
- Automated test scripts (API/contract) – tooling: TBD – confirm with QA Manager
- Golden labelled dataset and duplicate test sets
- Test run reports: functional, integration, performance and security test results
- UAT sign-off package: test evidence, defects list, acceptance checklist
Reporting:
- Weekly test status: planned/executed/passed/failed/blocked, defect ageing, extraction accuracy metrics, draft latency metrics, duplicate detection KPIs, and UAT progress.
- Escalation: Critical defects escalated to Business Owner (Customer Service Operations) immediately.

# 21. Traceability and Metrics
- Traceability approach: every BRD requirement and TEST BASIS item mapped to one or more test cases. Maintain a traceability matrix linking requirements → test cases → test results.
- Metrics / KPIs to report:
  - Extraction accuracy: header and line accuracy (precision/recall)
  - Draft latency: median, P95, P99 and % within 5 minutes
  - Throughput: emails processed per hour, max sustainable throughput
  - Duplicate detection rate (should be 100% on test set)
  - CSR correction rate and time in queue
  - Availability and error rates for integrations
  - Security findings and remediation status
- Traceability table (all TEST BASIS IDs mapped to plan sections):

| Test basis ID | Item (short) | Plan section |
|---|---:|---|
| T01 | Intake from branch mailboxes via Microsoft Graph | 4 In Scope; 7 Test Strategy; 8 Functional Test Coverage (Intake) |
| T02 | Duplicate PO detection by customer PO number | 4 In Scope; 8 Functional Test Coverage (Duplicate detection) |
| T03 | Extraction of header & lines (DocInt + OpenAI) | 4 In Scope; 8 Functional Test Coverage (Extraction); 11 AI and Data Quality |
| T04 | Customer identification by sender domain & content | 8 Functional Test Coverage (Customer identification) |
| T05 | Item matching via cross-reference then catalog | 8 Functional Test Coverage (Item matching); 11 AI and Data Quality |
| T06 | SAP validation via APIM + price variance >5% flagged | 8 Functional Test Coverage (SAP validation) |
| T07 | Creation of draft sales order in SAP | 8 Functional Test Coverage (Draft creation); 12 Performance |
| T08 | CSR review queue with corrections and release action | 8 Functional Test Coverage (CSR queue); 9 Roles & Permissions |
| T09 | Present confidence per field in Web UI | 8 Functional Test Coverage (Confidence display); 11 AI and Data Quality |
| T10 | Highlight lines missing cross-reference | 8 Functional Test Coverage (Missing cross-reference) |
| T11 | Flag orders older than 30 minutes in queue | 8 Functional Test Coverage (SLA flag); 9 Roles & Permissions |
| T12 | CS Admin can upload cross-reference file | 8 Functional Test Coverage (Admin upload); 9 Roles & Permissions |
| T13 | Straight-through release for trusted customers (MVP2) | 5 Out of Scope |
| T14 | Order acknowledgement emails (MVP2) | 5 Out of Scope |
| T15 | EDI fallback detection (MVP2) | 5 Out of Scope |
| T16 | Analytics (MVP2) | 5 Out of Scope |
| T17 | Keep CSR review for every order in MVP1 | 3 Test Objectives; 8 Functional Test Coverage; 17 Exit Criteria |
| T18 | Price variance >5% flagged during SAP validation | 8 Functional Test Coverage (Pricing rule) |
| T19 | Duplicate POs must be detected | 8 Functional Test Coverage (Duplicate detection) |
| T20 | Mandatory header fields required | 8 Functional Test Coverage (Quality checks) |
| T21 | Line quantity must be > 0 | 8 Functional Test Coverage (Quality checks) |
| T22 | UoM must be valid in SAP | 8 Functional Test Coverage (Quality checks) |
| T23 | RBAC: CSRs see branch queues only | 9 Roles, Permissions and Workflow Testing |
| T24 | CS Admin maintains mailbox routing & cross-reference | 9 Roles, Permissions and Workflow Testing; 8 Functional Test Coverage |
| T25 | Worked example: PO email -> draft in 5 minutes | 8 Functional Test Coverage; 12 Performance; 21 Traceability |
| T26 | Worked example: pilot dataset accuracy targets | 11 AI and Data Quality; 17 Exit Criteria |
| T27 | Worked example: duplicate PO test set detection 100% | 8 Functional Test Coverage (Duplicate detection); 17 Exit Criteria |
| T28 | Worked example: order older than 30 minutes flagged | 8 Functional Test Coverage (SLA flag) |
| T29 | NFR: Availability 99.5% 24x5 | 3 Test Objectives; 12 Performance; 13 Reliability |
| T30 | Security: Azure AD auth & branch-based queue access | 10 Security, Privacy and Compliance Testing; 9 Roles |
| T31 | Performance: Draft within 5 min for 95% of POs | 3 Test Objectives; 12 Performance; 17 Exit Criteria |
| T32 | Peak handling: 300 emails per hour | 12 Performance |
| T33 | Observability: End-to-end trace per email | 3 Test Objectives; 15 Logging & Monitoring |
| T34 | KPI: Reduce order entry time by 60% | 3 Test Objectives; 21 Traceability (KPI monitoring) |
| T35 | KPI: Reduce order entry errors by 50% | 3 Test Objectives; 11 AI and Data Quality |
| T36 | KPI: Create SAP draft orders within 5 minutes | 3 Test Objectives; 12 Performance |
| T37 | KPI: Keep CSR review for every order in MVP1 | 3 Test Objectives; 5 Out of Scope |
| T38 | Role: CSR responsibilities | 9 Roles, Permissions and Workflow Testing |
| T39 | Role: CS Supervisor responsibilities | 9 Roles, Permissions and Workflow Testing |
| T40 | Role: CS Admin responsibilities | 9 Roles, Permissions and Workflow Testing |
| T41 | Integration: CSR Users -> App Gateway | 7 Test Strategy; 9 Roles |
| T42 | Integration: Admin Users -> App Gateway | 7 Test Strategy; 9 Roles |
| T43 | Integration: Azure AD -> App Gateway OAuth2.0 | 10 Security |
| T44 | Integration: App Gateway -> APIM | 7 Test Strategy; 8 Integration testing |
| T45 | APIM -> Azure Document Intelligence | 7 Test Strategy; 8 Functional Test Coverage |
| T46 | APIM -> Azure OpenAI | 7 Test Strategy; 11 AI and Data Quality |
| T47 | APIM -> Azure AI Search | 7 Test Strategy; 8 Item matching |
| T48 | APIM -> Azure Blob Storage | 7 Test Strategy; 16 Test Environments |
| T49 | Branch Mailboxes -> Event Grid | 7 Test Strategy; 8 Intake tests |
| T50 | Event Grid -> Service Bus | 7 Test Strategy; 8 Intake tests |
| T51 | Service Bus -> Order Extraction Service | 7 Test Strategy; 8 Intake tests |
| T52 | Extraction Service -> Blob Storage | 8 Functional Test Coverage (Intake) |
| T53 | Extraction Service -> Web UI (email copy) | 8 Functional Test Coverage (Intake) |
| T54 | Extraction Service -> Order Creation Service | 8 Functional Test Coverage |
| T55 | Web UI -> Cosmos DB | 8 Functional Test Coverage; 15 Logging |
| T56 | Order Creation Service -> Cosmos DB drafts | 8 Functional Test Coverage; 15 Logging |
| T57 | Order Creation Service -> SAP via APIM | 8 Functional Test Coverage (Draft creation) |
| T58 | Data: PO emails – Source, Frequency, Owner, Security | 16 Test Environments and Test Data; 10 Security |
| T59 | Data: Customer cross-reference – Source, Frequency, Owner | 16 Test Environments and Test Data |
| T60 | Data: SAP master data – Source, Frequency, Owner | 16 Test Environments and Test Data |
| T61 | Data: Draft orders – Source and Owner | 15 Logging; 16 Test Environments |
| T62 | Data stores: Blob & Cosmos DB | 7 Test Strategy; 16 Test Environments |
| T63 | AI quality: Provide confidence per field | 11 AI and Data Quality; 8 Functional Test Coverage |
| T64 | CS Admin can configure confidence thresholds | 8 Functional Test Coverage; 9 Roles |
| T65 | Keep CSR review for every order in MVP1 | 3 Test Objectives; 5 Out of Scope |
| T66 | AI Governance Council approval required | 10 Security; 6 Assumptions & Dependencies |
| T67 | Out of scope: EDI orders | 5 Out of Scope |
| T68 | Out of scope: Credit checks changes | 5 Out of Scope |
| T69 | Out of scope: Quotations | 5 Out of Scope |
| T70 | Out of scope: Returns | 5 Out of Scope |
| T71 | No straight-through release in MVP1 | 5 Out of Scope; 17 Exit Criteria |
| T72 | No acknowledgements in MVP1 | 5 Out of Scope |
| T73 | No EDI handling in MVP1 | 5 Out of Scope |
| T74 | No analytics in MVP1 | 5 Out of Scope |
| T75 | Assumption: one PO per email | 6 Assumptions |
| T76 | Assumption: cross-reference files exist for top 200 customers | 6 Assumptions |
| T77 | Note: integration details to be validated with backend architects | 6 Assumptions & Dependencies |
| T78 | Dependency: SAP integration team | 6 Assumptions & Dependencies |
| T79 | Dependency: Mailbox access approval | 6 Assumptions & Dependencies |
| T80 | Dependency: CS branches for UAT | 6 Assumptions & Dependencies |
| T81 | Risk: Unusual PO layouts | 19 Risks and Mitigations |
| T82 | Risk: Missing cross-references | 19 Risks and Mitigations |
| T83 | Risk: SAP API limits | 19 Risks and Mitigations |
| T84 | Acceptance: ≥95% header accuracy on pilot | 17 Exit Criteria; 11 AI and Data Quality |
| T85 | Acceptance: ≥90% line accuracy on pilot | 17 Exit Criteria; 11 AI and Data Quality |
| T86 | Acceptance: Draft within 5 minutes for 95% of POs | 17 Exit Criteria; 12 Performance |
| T87 | Acceptance: No orders released without CSR action in MVP1 | 17 Exit Criteria; 5 Out of Scope |
| T88 | Acceptance: Duplicate POs detected 100% in test set | 17 Exit Criteria; 8 Functional Test Coverage |
| T89 | Timeline: MVP1 Apr–Jul 2026 | 22 Test Schedule |
| T90 | Timeline: MVP2 Q4 2026 | 5 Out of Scope |
| T91 | High-Level Plan: MVP1 then MVP2 | 22 Test Schedule; 5 Out of Scope |

# 22. Test Schedule
- High-level plan aligned with BRD timelines:
  - MVP1: Apr–Jul 2026 (T89)
  - MVP2: Q4 2026 (T90) — out of scope for this plan
- Detailed test phase dates, sprint-by-sprint test windows, UAT dates and regression windows: TBD – confirm with QA Manager and Customer Service Operations. Test schedule to be published once development sprint plan and environment availability confirmed.

# 23. End-to-End Scenario
Representative E2E scenario (to be executed in system/integration/UAT environments):
1. Simulate PO email arrival in branch mailbox (Graph API) with body and PDF attachment.
2. Event Grid publishes new-mail event and Service Bus receives message (T49–T51).
3. Order Extraction Service consumes message, stores email copy in Azure Blob Storage (T52) and posts extraction to Order Creation Service (T54). Web UI receives email copy for CSR review (T53).
4. Extraction uses Azure Document Intelligence and Azure OpenAI (via APIM) to extract header and line fields and returns per-field confidence (T45–T46, T63).
5. System identifies customer by sender domain and PO content (T04), applies customer cross-reference match, and attempts catalog search via Azure AI Search if needed (T05, T47).
6. Order Creation Service calls SAP via APIM to validate customer active, material valid and pricing; pricing variance >5% flagged (T06, T18).
7. Draft sales order is created in SAP (draft only) and SAP draft order number is returned and stored in Azure Cosmos DB (T07, T56).
8. End-to-end trace is verified: Event Grid timestamp -> correlation IDs -> SAP draft order number (T33).
9. Draft appears in CSR branch queue with per-field confidence; CSR corrects any lines and manually releases order in SAP (release action is manual in MVP1) (T08, T17).
10. Verify duplicate detection: if an earlier identical customer PO number exists in system, new incoming message is flagged and surfaced to CSR/Admin (T02/T27).
11. Measure from email receipt to SAP draft creation: must be within 5 minutes for 95% of POs in acceptance/performance runs (T31/T36). Log all discrepancies.

# 24. Approvals
- Required sign-offs for MVP1 release:
  - Business Owner: Customer Service Operations (BRD owner)
  - Product Owner / CS Ops Lead
  - Architecture Lead
  - QA Lead (test evidence)
  - UAT sign-off from CSRs and CS Supervisors
  - AI Governance Council confirmation of AI components (T66)
- Formal approval artefacts: UAT sign-off document, extraction accuracy report on pilot dataset (T84/T85), performance run report demonstrating T31/T36, and defect closure evidence per exit criteria.

---  

Notes / Open items requiring confirmation:
- Monitoring and logging retention policies and runbooks: TBD – confirm with Operations Owner.
- Test automation tooling and defect tracking tool: TBD – confirm with QA Manager.
- Browser compatibility and accessibility targets for Web UI: TBD – confirm with Customer Service Operations.
- Exact session timeout and MFA details: TBD – confirm with Security Owner.