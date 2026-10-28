# 1. Document Control
- Title: Email Purchase Order Entry Automation – MVP1 Master Test Plan  
- Version: 1.0 (test plan)  
- Application: Email Purchase Order Entry Automation (MVP1)  
- Prepared by: QA Lead – TBD – confirm with Customer Service Operations  
- Reviewed by: TBD – confirm with Customer Service Operations / Architecture Team / CS Admin  
- Audience: Business Owner (Customer Service Operations), Architects, QA Team, CS Admin, CS Supervisor, CSRs, SAP Integration Team, AI Governance Council  
- Purpose statement: Define scope, strategy, coverage and acceptance-based test approach to validate MVP1 as defined in the BRD and the Solution Architecture. This plan uses only facts from the BRD (Email Purchase Order Entry Automation v1.0, 02 Mar 2026) and the Solution Architecture (Non-production).

# 2. References
- BRD: Email Purchase Order Entry Automation, Version 1.0, Date: 02 Mar 2026 (contains objectives, scope, requirements, NFRs, data sources, acceptance criteria, risks)  
- Architecture: Email Purchase Order Entry Automation - Solution Architecture (Non-production) (connections list, services, data stores, environment notes)  
- P07_Email_Order_Entry_Architecture.png (referenced in BRD) – TBD – confirm with Architecture owner for file access

# 3. Test Objectives
- Prove MVP1 functional requirements are implemented per BRD:
  - PO intake from branch order mailboxes via Microsoft Graph
  - Extraction of header and lines using Azure Document Intelligence and Azure OpenAI
  - Customer and ship-to identification, item matching via customer cross-reference then catalog
  - SAP validation via APIM and creation of a draft sales order (not released)
  - CSR review queue with corrections and release action disabled for MVP1
- Validate acceptance criteria:
  - ≥95% header field accuracy and ≥90% line accuracy on pilot customers
  - Draft order created within 5 minutes of email receipt for 95% of POs
  - No orders released without CSR action in MVP1
  - Duplicate POs detected 100% in test set
- Validate non-functional targets from BRD:
  - Availability: 99.5% 24x5
  - Performance: Peak 300 emails per hour; draft within 5 minutes for 95% of POs
  - Observability: end-to-end trace per email to SAP draft order number
- Validate security, RBAC and segregation of duties as specified (Azure AD, branch-based queue access)
- Validate AI and data quality controls, confidence presentation, and human-in-the-loop behavior for MVP1

# 4. In Scope
(only MVP1 items from BRD)
- PO intake from branch order mailboxes via Microsoft Graph (Branch mailboxes -> Azure Event Grid -> Service Bus -> Order Extraction Service)
- Duplicate PO detection by customer PO number
- Extraction (header and lines) from email body and PDF/Excel attachments using Azure Document Intelligence and Azure OpenAI
  - Fields: customer PO number, sold-to, ship-to, requested delivery date
  - Line fields: customer part, description, quantity, UoM, price
- Customer identification by sender domain and PO content
- Item matching via customer cross-reference table, then catalog search (Azure AI Search)
- SAP validation via APIM (customer active, material valid, price variance >5% flagged)
- Creation of a draft sales order in SAP (draft, not released)
- CSR review queue (Web UI (Review Queue)) with:
  - Display of header/lines and per-field confidence
  - Highlight lines missing customer part cross-reference
  - CSR corrections saved back to draft orders in Cosmos DB
  - CSR release action disabled for MVP1 (no straight-through release)
- Observability: end-to-end trace linking email to SAP draft order number
- Data stores and flows: Blob Storage for emails, Cosmos DB for order drafts, Event Grid and Service Bus orchestration
- Roles: CSR, CS Supervisor, CS Admin (as defined in BRD)

# 5. Out of Scope
(Explicit BRD exclusions and MVP2 items)
- MVP2 features (deferred to Out of Scope for MVP1):
  - Straight-through release for trusted customers
  - Order acknowledgement emails
  - EDI detection and handling
  - Analytics
- EDI orders (explicitly out of scope)
- Credit check changes, quotations, returns
- Any automatic order release (No straight-through release in MVP1)

# 6. Assumptions and Dependencies
- Test assumptions (from BRD):
  - Customers send one PO per email in most cases
  - Cross-reference files exist for top 200 customers
- Dependencies (from BRD and Architecture):
  - SAP integration team availability and APIM connectivity
  - Mailbox access approval for branch mailboxes (Graph API)
  - CS branches for UAT / pilot
  - Order Extraction Service, Order Creation Service, Web UI (Review Queue), APIM, Azure Document Intelligence, Azure OpenAI, Azure AI Search, Event Grid, Service Bus, Blob Storage, Cosmos DB must be reachable from non-production subscription per architecture
  - Azure AD (Entra ID), App Gateway and network boundaries as described
- Items requiring confirmation (TBD – confirm with owner):
  - Test environment names, URLs, credentials and subscription details – TBD – confirm with Architecture owner
  - Exact confidence thresholds managed by CS Admin (no numeric thresholds provided in BRD) – TBD – confirm with CS Admin
  - Logging/monitoring implementation details (BRD marked TBD – pending SME review) – TBD – confirm with Observability owner
  - Retry counts, SLA windows for messaging components (Event Grid / Service Bus) – TBD – confirm with Integration owner

# 7. Test Strategy
- Approach:
  - Risk-based testing focused on business-critical flows and NFR targets from BRD
  - Validate both functional correctness and AI-extraction quality with human-in-the-loop verification
  - Incremental test levels: component/unit verification (owner teams), integration tests, system tests, performance/load tests, security tests, UAT with pilot CS branches
- Test levels:
  - Component/Unit: Order Extraction Service parsing logic, duplication detection unit tests (owner responsibility)
  - Integration: APIM -> Azure Document Intelligence/OpenAI/Search, Service Bus -> Order Extraction Service, Order Creation Service -> SAP via APIM, Blob Storage and Cosmos DB operations
  - System: End-to-end flows from new mail to draft order in SAP and CSR Review Queue
  - Performance/Load: Validate peak 300 emails/hour and draft within 5 minutes for 95% of POs
  - UAT/Pilot: Pilot customers (top customers with cross-reference files) with CS branches
- Test types:
  - Functional, Integration, Regression, Performance/Load, Resilience/Recovery, Security (authentication/authorization), Observability, Accessibility, AI quality / Responsible AI validation
- Techniques:
  - Sample PO emails in multiple formats: plain text, HTML body, PDF attachments, Excel attachments (as BRD states)
  - Synthetic negative tests: malformed POs, missing header fields, quantities <= 0, invalid UoM values
  - AI quality evaluation: labeled ground-truth test set (pilot customers) to measure header and line accuracy
  - Duplicate detection test set (100% detection expected)
  - SAP validation scenarios: valid/invalid customer, valid/invalid material, price variance >5% and <=5%
  - Security tests: Azure AD SSO flows, RBAC, branch-based queue access
  - Observability tests: validate end-to-end tracing present for each processed email

# 8. Functional Test Coverage
For each MVP1 requirement and sample user story from BRD, what will be verified:

- PO intake from branch mailboxes via Microsoft Graph
  - Verify Event Grid receives new mail events from Branch Mailboxes (Graph API)
  - Verify Event Grid -> Service Bus event delivery
  - Verify Service Bus enqueues and Order Extraction Service consumes messages
  - Verify email MIME and attachments copied to Azure Blob Storage (copy present)

- Duplicate PO detection by customer PO number
  - Verify duplicate detection logic finds same customer PO number across new messages
  - Verify duplicate handling behavior per BRD (detect 100% in test set)
  - Verify duplicates flagged in Review Queue and not created as duplicate drafts in SAP

- Extraction of fields using Azure Document Intelligence and Azure OpenAI
  - Verify extraction of customer PO number, sold-to, ship-to, requested delivery date
  - Verify extraction of line-level fields: customer part, description, quantity, UoM, price
  - Verify support for extraction from email body, PDFs and Excel attachments
  - Verify per-field confidence returned and stored/displayed

- Customer identification by sender domain and PO content
  - Verify matching by sender domain when present
  - Verify fallback to PO content parsing if sender domain ambiguous
  - Verify correct sold-to/ship-to identified or appropriate flagging when ambiguous

- Item matching via customer cross-reference table, then catalog search (Azure AI Search)
  - Verify cross-reference lookup for customer part -> material
  - Verify fallback search against catalog (Azure AI Search) when no cross-reference found
  - Verify lines where no customer part cross-reference exists are highlighted in UI

- SAP validation via APIM and creation of draft sales order
  - Verify APIM call to SAP S/4HANA to validate:
    - customer active
    - material valid
    - pricing check: price variance >5% flagged
  - Verify Order Creation Service creates draft sales order in SAP (draft, not released)
  - Verify draft order record created in Cosmos DB with header, lines, confidence metadata

- CSR review queue (Web UI (Review Queue))
  - Verify CSR can view draft orders for their branch only (RBAC / branch-based queue access)
  - Verify per-field confidence visible to CSR
  - Verify CSR can edit header and line fields and save corrections back to draft (Cosmos DB)
  - Verify release action is present but disabled in MVP1 (no automatic release)
  - Verify CS Supervisor view includes flagging of orders older than 30 minutes
  - Verify CS Admin can upload a customer cross-reference file (upload flow, data persisted and used for matching)

- Observability / traceability
  - Verify an end-to-end trace exists linking incoming email to SAP draft order number for each processed email

# 9. Roles, Permissions and Workflow Testing
- Roles to test (as defined in BRD):
  - CSR
    - Verify CSR can view draft orders only for their branch (RBAC)
    - Verify CSR cannot view other branches’ queues
    - Verify CSR can correct fields, save corrections and that changes persist to Cosmos DB/draft order
    - Verify CSR cannot release orders in MVP1 (release must not result in SAP order release)
  - CS Supervisor
    - Verify supervisor can view queue across branches per assigned permissions (confirm exact scope with owner) – TBD – confirm with CS Supervisor
    - Verify orders older than 30 minutes are flagged for CS Supervisor
    - Verify reassign orders functionality (if present) – TBD – confirm with CS Admin whether reassign is in MVP1 UI
  - CS Admin
    - Verify CS Admin can upload and update customer cross-reference files (frequency: Monthly as per BRD)
    - Verify CS Admin can maintain confidence thresholds (UI and effect) – numeric thresholds TBD – confirm with CS Admin
- Segregation of duties
  - Verify that CS Admin cannot release orders (separation)
  - Verify only CSR can perform corrections and (when enabled in later MVP) release
  - Verify audit trail captures user who edited / saved corrections

# 10. Security, Privacy and Compliance Testing
- Authentication and Authorization
  - Verify Azure AD (Entra ID) SSO for CSR and Admin Users via App Gateway (HTTPS/443 AD/SSO)
  - Verify role-based access policies enforced per BRD (branch-based queue access)
- Data protection
  - Verify PO emails and attachments stored in Azure Blob Storage with appropriate access controls (Managed Identity)
  - Verify Cosmos DB access restricted and draft orders marked Confidential
  - Verify secrets stored in Key Vault used by services (confirm Key Vault usage per architecture)
- Compliance / Responsible AI
  - Verify AI Governance Council approval recorded and that AI services usage aligns with governance controls noted in BRD
  - Verify customer data classification Confidential is respected in storage, logs and UI
- Penetration / vulnerability testing
  - Test surface: App Gateway, APIM endpoints, Web UI – schedule TBD – confirm with Security owner
- Items requiring confirmation (TBD – confirm with owner):
  - Specific security test cases, scanning tools and schedule – TBD – confirm with Security owner

# 11. AI and Data Quality Validation
- Ground-truth accuracy targets (from BRD acceptance criteria):
  - Header field accuracy ≥95% on pilot customers
  - Line accuracy ≥90% on pilot customers
- Test approach:
  - Build labeled ground-truth dataset for pilot customers (sample emails with gold-standard extracted fields)
  - Measure extraction accuracy per field and overall line-level accuracy against ground truth
  - Track draft accuracy, CSR correction rate, and field-level confidence correlation
- Confidence thresholds and behavior:
  - Verify per-field confidence is returned by extraction pipeline and visible in UI
  - Verify low-confidence fields are highlighted and require CSR attention
  - Confirm numeric thresholds are configurable by CS Admin (threshold values TBD – confirm with CS Admin)
- Hallucination and provenance controls:
  - Verify Azure OpenAI outputs include traceability to source text (source spans or confidence metadata) where provided by service (or alternative provenance data) – validate that every populated field can be traced to a source element
  - Verify that generated values without supporting source evidence are flagged and sent for human review
  - Verify process for CS Admin / AI Governance Council to tune models or thresholds (process artifact) – confirm with AI Governance Council
- Duplicate detection:
  - Validate duplicate PO detection works 100% on curated test set
- Data quality business rules:
  - Validate mandatory header fields enforcement
  - Validate line quantity > 0 enforcement
  - Validate UoM valid in SAP enforcement (per BRD)
- Metrics to capture during testing:
  - Header field accuracy, line accuracy, per-field confidence distributions, correction rates, false-positive/false-negative for duplicate detection, number of hallucination incidents and handling

# 12. Performance Testing
- Targets from BRD:
  - Draft order created within 5 minutes of email receipt for 95% of POs
  - Peak 300 emails per hour
- Tests to run:
  - Baseline test: process representative workload of POs at normal rate and measure average time to draft
  - Load test: sustained 300 emails/hour for representative duration – validate 95% within 5 minutes
  - Burst tests: higher-than-peak bursts to validate queueing behavior and Service Bus throttling (exact burst values TBD – confirm with Integration owner)
  - SAP validation latency tests (measure APIM -> SAP round-trip and effect on end-to-end time)
  - End-to-end SLA measurement and monitoring integration (Datadog / Azure Monitor per architecture) – confirm metrics available
- Test data and orchestration:
  - Use synthetic emails representative of formats (PDF / Excel / body)
  - Include mix of successful, validation-failed, and low-confidence items
- Test schedule and durations: specific test windows TBD – confirm with Performance owner and SAP integration team

# 13. Reliability and Recovery Testing
- Availability target: 99.5% 24x5 (from BRD)
- Tests:
  - Component failure simulations: Order Extraction Service instance failures, APIM transient failures, Service Bus message consumer restarts
  - Message retry and dead-letter handling: verify Service Bus retries, dead-lettering and reprocessing (retry counts and backoff TBD – confirm with Integration owner)
  - SAP API error handling: simulate SAP validation failures and ensure proper flagging and retry logic
  - Blob Storage and Cosmos DB connectivity loss simulations and recovery
  - Verify queueing and retry mitigations for SAP API limits (BRD mitigation = Queueing and retry)
- Recovery acceptance:
  - System recovers to processing state without manual data loss and preserves traceability
  - Relevant alerts fired to monitoring channels (Datadog / Azure Monitor per architecture) – validate alerting is configured (details TBD – confirm with Observability owner)

# 14. Accessibility and Compatibility Testing
- Web UI (Review Queue) compatibility:
  - Browser compatibility matrix TBD – confirm with CS UI owner (browsers and versions)
  - Verify UI works on supported browsers and standard CSR workstations
- Accessibility:
  - Accessibility testing scope TBD – confirm with Accessibility owner whether WCAG requirements apply for MVP1

# 15. Logging, Monitoring and Audit Testing
- Verify logging and monitoring for:
  - Emails processed
  - Draft accuracy metrics
  - CSR correction rate
  - Time to draft (end-to-end)
  - End-to-end trace linking email -> Cosmos DB draft -> SAP draft order number
- Verify audit trail:
  - Record of who viewed/edited/saved corrections and timestamps
  - Record of duplicate detection decisions
- Observability components per architecture: Datadog, Azure Monitor (confirm metric names and dashboards) – details TBD – confirm with Observability owner
- Verify alerts for:
  - Processing backlog growth
  - Failed message retries / dead-letter queue messages
  - SAP API rate-limit errors
  - System component outages impacting 99.5% 24x5 target

# 16. Test Environments and Test Data
- Environments (per architecture):
  - Non-production Subscription environment containing Azure AI Landing Zone, Shared AKS Non-prod, Data Stores, Integration & Eventing (as in architecture) – environment access details TBD – confirm with Architecture owner
  - Shared Services Subscription (contains Azure AD and App Gateway) – test identities required
  - SAP non-production systems accessed via APIM – SAP test endpoint details TBD – confirm with SAP integration team
- Test data management:
  - Create synthetic/obfuscated PO emails (PDF, Excel, text) matching sample layouts and edge cases
  - Pilot customer data sets (top customers with cross-reference files); use masked/anonymized production data where required and permitted (data classification: Confidential)
  - Cross-reference files: monthly upload cadence; include current top-200 cross-reference dataset for matching tests
  - SAP master data: test customers, materials, and pricing test data – coordinate with Master Data owner
- Data security:
  - All test artifacts containing customer-like data must be classified and handled as Confidential
- Test data owners to confirm provisioning: Master Data, Customer Service, CS Admin – coordination required

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:
  - Test environment provisioned and accessible (Non-production subscription, APIM, Event Grid, Service Bus, Blob Storage, Cosmos DB, Azure Document Intelligence, Azure OpenAI, Azure AI Search) – confirmation required
  - Test data (synthetic emails, cross-reference files, SAP test master data) available
  - Deployment of Order Extraction Service, Order Creation Service, Web UI to test environment
- Suspension criteria:
  - Critical defects preventing end-to-end processing or blocking testing of core flows
  - Infrastructure outages preventing access to core integrations (Graph API mail events, APIM to SAP)
- Exit criteria:
  - All critical and high-severity defects resolved or mitigated per agreed risk acceptance
  - Acceptance criteria from BRD met:
    - Header field accuracy ≥95% and line accuracy ≥90% on pilot customers
    - Draft order created within 5 minutes for 95% of POs (verified under test load)
    - No orders released without CSR action in MVP1
    - Duplicate POs detected 100% in test set
  - All planned test cases executed with pass rates meeting release gates (detailed pass thresholds to be confirmed) – TBD – confirm with Business Owner

# 18. Defect Management
- Defect lifecycle:
  - Logged, triaged, assigned, fixed, retested, closed
- Severity definitions (align to business impact):
  - Critical: End-to-end processing broken; POs not reaching draft; data corruption; security breach
  - High: Major functionality impaired (duplicate detection fails at scale; SAP validation incorrect)
  - Medium: Non-critical functional issues impacting UX or requiring workaround
  - Low: Cosmetic or minor issues
- Defect tracking tool: TBD – confirm with QA Lead / Tooling owner
- Triage cadence: daily triage during execution; escalate Critical defects immediately to Architecture and Business Owner

# 19. Risks and Mitigations
(From BRD; do not invent new ones beyond BRD statements)
- Risk: Unusual PO layouts  
  - Mitigation: CSR review and confidence flags (BRD)
- Risk: Missing cross-references  
  - Mitigation: Catalog search fallback (Azure AI Search) (BRD)
- Risk: SAP API limits  
  - Mitigation: Queueing and retry (BRD)
- Test-specific risks (from dependencies):
  - Mailbox access not approved in time -> testing cannot validate end-to-end intake  
    - Mitigation: Escalate mailbox access approval with Customer Service and Architecture teams; use simulated mail events if required
  - SAP test API not available -> cannot validate SAP draft creation  
    - Mitigation: Coordinate with SAP integration team early; prepare mocked SAP responses for early integration tests

# 20. Test Deliverables and Reporting
- Deliverables:
  - This Master Test Plan (current document)
  - Detailed test cases and test scripts for functional, integration, AI-quality, performance, recovery and security tests
  - Test data sets (synthetic emails, cross-reference files, SAP test data) with classification and handling instructions
  - Test execution records and defect logs
  - Performance and AI accuracy reports (including header/line accuracy metrics)
  - Test summary report and recommendation for MVP1 readiness against acceptance criteria
- Reporting cadence:
  - Daily test execution status during system test phase (format and recipients TBD – confirm with Business Owner)
  - Weekly quality dashboard during test window (KPIs per Section 21)

# 21. Traceability and Metrics
- Traceability:
  - Every BRD functional requirement and user story will be traced to one or more test cases. Traceability matrix to be created and maintained (artifact: Requirement-to-Test Traceability Matrix) – deliverable
- Key Metrics / KPIs (from BRD and acceptance criteria):
  - Header field accuracy (target ≥95% on pilot customers)
  - Line accuracy (target ≥90% on pilot customers)
  - Draft creation latency: % of drafts within 5 minutes of email receipt (target 95%)
  - Peak throughput validated: emails/hour (target peak handle 300 emails/hour)
  - Duplicate detection accuracy (target 100% on test set)
  - Availability (target 99.5% 24x5)
  - CSR correction rate and time to correction
  - Number of hallucination incidents and resolution rate
  - Observability: percent of processed emails with end-to-end trace to SAP draft order
- Reporting artifacts:
  - Daily execution logs, defect dashboards, AI accuracy reports, performance test reports

# 22. Test Schedule
- High-level schedule (as aligned to BRD MVP1 plan):
  - MVP1 timebox in BRD: Apr–Jul 2026
  - High-level phases (dates and detailed schedule TBD – confirm with QA Lead and Project Manager):
    - Test planning and environment prep – within MVP1 window (TBD – confirm with Architecture owner)
    - Component & integration tests – early in cycle
    - System & AI-quality tests (including ground-truth evaluation) – mid-cycle
    - Performance & resilience tests – mid/late cycle
    - UAT / Pilot with CS branches – late cycle
    - Test closure and acceptance reporting – by end of MVP1 window (TBD – confirm with Business Owner)
- Specific test dates, windows and staffing to be confirmed – TBD – confirm with Project Manager

# 23. End-to-End Scenario
Representative E2E test scenario (to be implemented as system test and UAT):
- Pre-conditions:
  - Branch mailbox configured and Event Grid subscription active
  - Test customer cross-reference file uploaded for pilot customer
  - SAP test master data present (customer, material, pricing)
- Steps:
  1. Send a test PO email (PDF attachment) from pilot customer sender domain to branch mailbox (simulate via Graph API trigger if mailbox access limited)
  2. Event Grid captures new mail event and pushes to Service Bus
  3. Order Extraction Service consumes message, stores a copy in Blob Storage, and invokes Azure Document Intelligence to extract header and line data; Azure OpenAI used to map fields
  4. Extraction returns per-field confidences; Order Extraction Service performs customer identification and cross-reference lookup; missing cross-reference triggers catalog search (Azure AI Search)
  5. Order Creation Service calls APIM to validate customer active, material valid, and checks pricing; price variance >5% would be flagged
  6. Draft sales order created in SAP (draft) and draft record persisted to Cosmos DB, with end-to-end trace id linking email -> Cosmos DB draft -> SAP draft id
  7. Web UI (Review Queue) displays draft to CSR for branch; per-field confidences shown; lines missing cross-reference highlighted
  8. CSR edits a line (e.g., corrects quantity), saves changes; change persists to draft in Cosmos DB
  9. Verify CSR release action is present but disabled (no release occurs)
 10. Verify logs, metrics and end-to-end trace exist for the run
- Expected results:
  - Draft created in SAP and record in Cosmos DB within 5 minutes (95% of runs)
  - Header and line extraction accuracy meets acceptance thresholds on pilot dataset
  - Duplicate detection logic not triggered for unique PO; duplicate test cases will trigger duplicate detection and flag appropriately

# 24. Approvals
- Acceptance and sign-off required from:
  - Business Owner: Customer Service Operations
  - AI Governance Council (BRD lists AI Governance Council approval)
  - SAP Integration owner (for SAP draft order acceptance)
  - QA Lead (test validation)
- Specific approvers and signature artifacts TBD – confirm with Business Owner and AI Governance Council

--- 

Notes / Action items (TBDs to be confirmed with owners)
- Test environment details, credentials and access: TBD – confirm with Architecture owner  
- Confidence threshold numeric values and configuration details: TBD – confirm with CS Admin  
- Logging/monitoring metric names and dashboards: TBD – confirm with Observability owner  
- Defect tracking and test management tools: TBD – confirm with QA Lead / Tooling owner  
- Browser compatibility and accessibility requirements: TBD – confirm with CS UI owner  
- SAP test endpoints and mock behavior (if required): TBD – confirm with SAP integration team

This plan maps all MVP1 functional requirements, NFRs, roles, integrations, data sources, AI quality controls, assumptions, dependencies, acceptance criteria and risks as specified in the BRD and Solution Architecture.