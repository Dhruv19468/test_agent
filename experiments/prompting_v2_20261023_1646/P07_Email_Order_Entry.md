# 1. Document Control
- Title: Email Purchase Order Entry Automation — MVP1 Master Test Plan
- Version: 1.0
- Application: Email Purchase Order Entry Automation (MVP1)
- Prepared by: QA Lead (Master Test Plan)
- Reviewed by: TBD – confirm with Business Owner / Architecture Owner
- Audience: Customer Service Operations (Business Owner), Architects, QA Team, CS Admin, CS Supervisors, AI Governance Council
- Purpose: Define the test approach, scope, coverage and acceptance verification for MVP1 (PO email ingestion, extraction, matching, SAP validation and draft sales order creation with CSR review) based only on the BRD v1.0 and the provided architecture description.

# 2. References
- BRD – Email Purchase Order Entry Automation, Version 1.0, Date: 02 Mar 2026
- Solution Architecture: "Email Purchase Order Entry Automation - Solution Architecture (Non-production)" (connections and component listing)
- P07_Email_Order_Entry_Architecture.png (referenced in BRD)
- AI Governance Council approvals referenced in BRD

# 3. Test Objectives
- Prove MVP1 meets functional requirements: PO intake from branch mailboxes, extraction of headers and lines, customer & ship-to identification, item matching (cross-reference then catalog), SAP validation, duplicate detection, and draft sales order creation into CSR review queue.
- Validate quality targets and acceptance criteria from BRD:
  - ≥95% header field accuracy and ≥90% line accuracy on pilot customers.
  - Draft created within 5 minutes for 95% of POs.
  - Duplicate PO detection 100% in test set.
  - No orders released without CSR action in MVP1.
- Validate non-functional targets from BRD:
  - Availability: 99.5% 24x5.
  - Performance: handle peak 300 emails per hour; draft within 5 minutes for 95% of POs.
  - Observability: end-to-end trace exists per email to SAP draft order number.
- Validate security, RBAC and segregation of duties: Azure AD-based access, branch-based queue access, CSR-only release in MVP1.
- Validate AI and data quality controls: field-level confidence displayed, CS Admin-managed confidence thresholds, price variance >5% flagged, mandatory data quality checks (mandatory headers, line quantity > 0, UoM valid in SAP).
- Demonstrate integrations work end-to-end according to the architecture connections list.

# 4. In Scope
(All items are MVP1 unless otherwise noted)
- PO intake:
  - Monitor branch order mailboxes via Microsoft Graph (Graph API) and Event Grid eventing.
  - Duplicate PO detection by customer PO number.
- Extraction:
  - Extract customer PO number, sold-to, ship-to, requested delivery date and lines (customer part, description, quantity, UoM, price) using Azure Document Intelligence and Azure OpenAI.
  - Store email copy in Azure Blob Storage.
- Matching & identification:
  - Customer identification by sender domain and PO content.
  - Item matching via customer cross-reference table (CS Admin upload) then Azure AI Search catalog fallback.
- SAP validation and draft order creation:
  - Validate customer active, material valid, and price checks via SAP S/4HANA APIs accessed through APIM.
  - Flag price variance >5%.
  - Create draft sales order (not released) in SAP; create draft in Azure Cosmos DB for CSR review queue.
- CSR review queue:
  - Web UI (Review Queue) shows draft orders with header, lines and field-level confidence for CSR review and correction.
  - CSR must perform review for every order (no straight-through release in MVP1).
- Observability:
  - End-to-end trace per email to SAP draft order number is available.
- Data quality checks:
  - Mandatory header fields present; line quantity > 0; UoM valid in SAP.
- RBAC:
  - Branch-based queue access enforced; Azure AD authentication.
- Integration points listed in architecture (see Section 8 and Section 15).
- Non-production architecture footprint as provided (Order Extraction Service, Order Creation Service, APIM, AI services, Service Bus, Event Grid, Blob Storage, Cosmos DB, Web UI).

# 5. Out of Scope
- All explicit MVP2 items and BRD exclusions:
  - MVP2 items:
    - Straight-through release for trusted customers.
    - Order acknowledgement emails.
    - EDI fallback detection.
    - Analytics.
  - BRD explicit exclusions:
    - EDI orders.
    - Credit checks changes.
    - Quotations.
    - Returns.
- Any automatic release to SAP without CSR action (must be enforced as out of scope for MVP1).
- Any enhancements beyond MVP1 (deferred to MVP2 or later).

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Customers send one PO per email in most cases.
  - Cross-reference files exist for top 200 customers.
- Test assumptions:
  - Test mailboxes and mailbox access via Graph API will be provided.
  - SAP validation APIs via APIM will be available in non-production.
  - CS branches and pilot customer data will be available for UAT.
- Dependencies (from BRD and architecture):
  - SAP integration team (SAP S/4HANA APIs).
  - Mailbox access approval (branch mailboxes).
  - CS branches for UAT.
  - Azure AD (Entra ID) and App Gateway for authentication and entry.
  - Order Extraction Service and Order Creation Service deployments in non-production.
  - Access to Azure Document Intelligence, Azure OpenAI and Azure AI Search test endpoints.
  - Service Bus and Event Grid connectivity.
- Items requiring confirmation (TBD):
  - Test defect tracking tool and triage owner — TBD – confirm with QA Manager.
  - Test automation framework and CI/CD pipeline integration — TBD – confirm with DevOps Owner.
  - Non-production test environment names, subscriptions and network access lists — TBD – confirm with Architecture Owner.

# 7. Test Strategy
- Levels:
  - Component/unit testing: developers validate services (Order Extraction Service, Order Creation Service) against mocks.
  - Integration testing: verify connections between components and external systems per architecture (Graph API -> Event Grid -> Service Bus -> Extraction -> APIM -> AI services -> Blob/Cosmos DB -> SAP).
  - System testing: end-to-end tests across full workflow for MVP1 features.
  - Performance and load testing: validate throughput and timing NFRs.
  - Security and RBAC testing: validate Azure AD authentication, branch-based access and segregation.
  - UAT with CSRs and CS Supervisors on pilot branches/customers to validate acceptance criteria.
- Test types and techniques:
  - Functional test cases (positive, negative, edge cases).
  - Data-driven tests for extraction and matching (varied PO layouts).
  - Exploratory testing for unusual PO layouts (risk listed in BRD).
  - Regression testing for every build.
  - Synthetic and replayed real-email scenarios (using sanitized PO emails).
  - Mocking & stubbing for SAP master data where SAP non-production constraints exist; full SAP integration tests where permitted.
  - AI validation tests: automated measurement of header and line accuracy and confidence mapping.
  - Security tests: authentication, authorization, RBAC, data confidentiality.
  - Observability tests: verify traces and logs per email to SAP draft order number.
- Test automation:
  - Automate API and regression tests where feasible; exact tools TBD – confirm with QA/DevOps Owner.
- Acceptance tests:
  - Pilot UAT verification for the acceptance criteria specified in BRD.

# 8. Functional Test Coverage
For each functional requirement and user story from BRD, list what will be verified.

- PO intake from branch order mailboxes via Microsoft Graph (Graph API)
  - Verify Event Grid receives new mail events from Branch Mailboxes.
  - Verify Azure Event Grid forwards event to Azure Service Bus.
  - Verify Order Extraction Service dequeues messages from Service Bus.
  - Verify email copy saved to Azure Blob Storage.
  - Verify duplicate detection by customer PO number (detect 100% in test set including exact duplicates and duplicates with minor formatting differences).

- Extraction of customer PO number, sold-to, ship-to, requested delivery date and lines using Azure Document Intelligence and Azure OpenAI
  - Verify extracted header fields: customer PO number, sold-to, ship-to, requested delivery date.
  - Verify extracted line fields: customer part, description, quantity, UoM, price.
  - Verify field-level confidence value returned for each field.
  - Verify storage of extracted data and confidence in Cosmos DB draft record.
  - Verify accuracy targets: header field accuracy ≥95% and line accuracy ≥90% on pilot customers.

- Customer identification by sender domain and PO content
  - Verify identification by sender domain mapping to customer.
  - Verify fallback identification via PO content when sender domain not definitive.

- Item matching via customer cross-reference table, then catalog search (Azure AI Search)
  - Verify match via uploaded cross-reference file (CS Admin upload).
  - Verify fallback to Azure AI Search catalog when cross-reference miss.
  - Verify unmatched lines flagged/highlighted in Web UI.
  - Verify CS Admin ability (in test) to upload cross-reference and impact on matching.

- SAP validation via APIM (customer active, material valid, price variance >5% flagged) and creation of a draft sales order (not released)
  - Verify APIM call to SAP returns customer active status.
  - Verify material validation via SAP APIs.
  - Verify price variance calculation and flagging when variance >5%.
  - Verify draft sales order creation in SAP (draft status) and corresponding draft record in Cosmos DB.
  - Verify "not released" status persisted and no automatic release executed in MVP1.

- CSR review queue with corrections and release action
  - Verify Web UI displays draft with header, lines, and field-level confidence.
  - Verify lines without cross-reference highlighted.
  - Verify CSRs can correct fields and save changes.
  - Verify CSRs can release the order in SAP (CSR release action triggers SAP release) — ensure tests confirm only CSR-initiated releases occur.
  - Verify CS Supervisors can monitor queue and reassign orders.
  - Verify CSR view restricted to their branches only (RBAC).

- Duplicate PO detection
  - Verify duplicate detection logic for customer PO number, including different formatting and attachments.
  - Verify duplicate detection rate meets 100% on test set.

- Observability
  - Verify an end-to-end trace (correlation ID) exists from incoming email to Cosmos DB draft and SAP draft order number for each processed email.

- Data quality checks
  - Verify mandatory header fields enforcement.
  - Verify line quantity > 0 validation.
  - Verify UoM validity check against SAP master data.

- Logging and metrics
  - Verify logging of emails processed, draft accuracy metrics, CSR correction rate, and time to draft (per BRD logging items; note TBD for pending SME review).

# 9. Roles, Permissions and Workflow Testing
- Roles to test (from BRD / architecture):
  - CSR
  - CS Supervisor
  - CS Admin
- Identity / access control:
  - Azure AD (Entra ID) authentication for CSR and Admin users via App Gateway.
  - Verify CSRs see queues for their branches only (branch-based queue access).
  - Verify CS Admin functions: mailbox routing maintenance, customer cross-reference uploads, confidence threshold configuration.
  - Verify CS Supervisor functions: monitor queue, reassign orders, view SLA flags (orders older than 30 minutes flagged).
- Segregation of duties:
  - Verify that in MVP1 no automatic straight-through release is available.
  - Verify only CSR role can perform release action; Admin and Supervisor cannot release unless they have CSR privilege (test specific role privileges as provisioned).
- Workflow tests:
  - Verify full process flow: mail arrival -> extraction -> matching -> SAP validation -> draft in queue -> CSR review/correction -> CSR release -> SAP order release (release step executed only on CSR action).
  - Verify orders older than 30 minutes are flagged in the queue view (user story).

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization:
  - Verify Azure AD SSO integration via App Gateway.
  - Verify RBAC restricts branch queues per CSR.
- Data confidentiality:
  - Verify emails and draft orders stored as Confidential (as per BRD).
  - Verify access to email copies in Blob Storage is limited to authorized roles and services.
- Secrets and keys:
  - Verify Key Vault usage for service credentials where configured in architecture (confirm with Architecture Owner).
- AI Governance & privacy:
  - Verify compliance with AI Governance Council approvals (presence of approval artifacts required for deployment).
- Compliance tests:
  - Verify that customer data identified as Confidential is treated per compliance policies (TBD – confirm with Security/Compliance Owner).
- Penetration or vulnerability testing:
  - Schedule / scope TBD – confirm with Security Owner.

# 11. AI and Data Quality Validation
- Services used:
  - Azure Document Intelligence
  - Azure OpenAI
  - Azure AI Search
- Validation points:
  - Field-level accuracy measurement: compute header field accuracy and line accuracy across pilot customers; target ≥95% header, ≥90% line.
  - Confidence thresholds:
    - Verify CS Admin can configure per-field confidence thresholds (administration function).
    - Verify behavior when confidence < threshold: route to CSR review and highlight field (no auto-correction).
  - Human-in-the-loop controls:
    - Verify every order routes to CSR review in MVP1 regardless of confidence.
    - Verify confidence per field shown in Web UI (user story).
  - Controls against hallucination:
    - Verify mapping and validation steps against SAP master data and cross-reference/catalog before any material codes are suggested.
    - Verify that any AI-suggested field that cannot be validated against SAP master data or cross-reference is flagged and requires CSR confirmation.
    - Verify that Azure OpenAI outputs are used only as mapping aids and that final persisted values are validated (e.g., material validity via SAP).
  - Price variance rule:
    - Verify price variance calculation and that variance >5% is flagged.
  - Test datasets:
    - Use representative PO layouts including known variations and unusual formats to exercise Document Intelligence and OpenAI mapping.
  - Measurement & reporting:
    - Log extraction confidence and accuracy metrics; compute draft accuracy and CSR correction rate.
- Acceptance:
  - The acceptance criteria from BRD (header/line accuracy) must be met on pilot customers.

# 12. Performance Testing
- Targets to validate (from BRD):
  - Draft order created within 5 minutes of email receipt for 95% of POs.
  - Peak 300 emails per hour.
- Tests to execute:
  - Throughput/load tests simulating up to peak 300 emails/hour and bursts to validate processing queueing and end-to-end latency.
  - End-to-end timing tests measuring envelope time from email receipt (Event Grid event) to draft creation in Cosmos DB and SAP draft order creation.
  - SLA test: validate 95% of samples have draft creation <= 5 minutes.
  - Scalability tests for Service Bus, Order Extraction Service, and Order Creation Service under load.
  - Backpressure and degradation tests: simulate SAP API slowness/limits and observe queueing/retry behavior and SLA impact.
- Test data for performance:
  - Use representative mix of simple and complex POs, multi-line orders and attachments (PDF/Excel) to reflect real-world variability (BRD: 6,000 PO emails per week across 40 branches).
- Observability:
  - Validate metrics collection of processing times per stage and ability to correlate to end-to-end traces.

# 13. Reliability and Recovery Testing
- Availability target:
  - Verify system components support 99.5% 24x5 availability.
- Tests:
  - Component failure and recovery tests (service restart, simulated Azure Document Intelligence outage, APIM/SAP unavailable).
  - Retry and queueing behavior: ensure Event Grid/Service Bus retains messages and Order Extraction Service retries per architecture behavior (confirm retry policies with Architecture Owner).
  - Data integrity after failover: ensure no duplicate draft creation and duplicate detection remains effective.
  - Recovery tests:
    - Simulate transient SAP API failures and ensure orders are retried and do not get released automatically.
- Observability:
  - Verify alerts and dashboards (TBD – confirm with Monitoring Owner) for service outages and processing backlogs.

# 14. Accessibility and Compatibility Testing
- Accessibility:
  - Web UI (Review Queue) should be tested for standard accessibility behavior. Specific accessibility requirements are not specified in BRD — tests to be defined in UAT with accessibility stakeholders (TBD – confirm with Accessibility Owner).
- Compatibility:
  - Verify Web UI functions with supported browsers and devices used by CSRs and Admins — supported browser list TBD – confirm with UI Owner.
- Note: No explicit accessibility or compatibility targets are provided in BRD.

# 15. Logging, Monitoring and Audit Testing
- Verify logging for:
  - Emails processed, draft accuracy, CSR correction rate, time to draft (BRD logging items).
  - End-to-end correlation ID per email to SAP draft order number.
- Verify monitoring:
  - Metrics for processing time per stage, queue depth (Service Bus), Event Grid event rates, error rates, AI extraction confidence distributions.
  - Alerts for orders older than 30 minutes (user story), queue backlog thresholds (TBD), and service outages.
- Audit:
  - Verify audit trail for CSR corrections and release actions (who, what, when).
  - Verify storage of draft orders in Cosmos DB includes confidence and provenance metadata.
- Tools and dashboards:
  - Architecture lists Datadog and Azure Monitor as supporting services — confirm which will be used for MVP1 monitoring dashboards and alerts — TBD – confirm with Monitoring Owner.
- Note: "Logging and Monitoring" in BRD has items pending SME review — any gaps to be validated during design.

# 16. Test Environments and Test Data
- Environments (from architecture / BRD):
  - Non-production Subscription containing Azure AI Landing Zone, Shared AKS Non-prod, Data Stores, Integration & Eventing (as described).
  - Shared Services Subscription containing Azure AD and App Gateway.
  - On-Premise CSR/Admin user contexts for UI access.
- Environment details required (TBD):
  - Exact non-production environment names and access details — TBD – confirm with Architecture Owner.
  - SAP non-prod endpoints and test credentials — TBD – confirm with SAP Integration Owner.
  - Test mailbox accounts and mailbox access approvals — TBD – confirm with Customer Service Owner.
- Test data management:
  - Use sanitized real PO emails where possible to reflect real layouts (sanitization required for confidential data).
  - Provide cross-reference files representative of top 200 customers.
  - Provide SAP master data test snapshots (customers, materials, prices) or mock endpoints.
- Data classification:
  - PO emails: Confidential, source Branch mailboxes, Frequency: Continuous, Owner: Customer Service.
  - Customer cross-reference: Internal, Source: CS Admin upload, Frequency: Monthly, Owner: Customer Service.
  - SAP master data: Confidential, Source: SAP, Frequency: On demand, Owner: Master Data.
  - Draft orders: Confidential, Source: Tool output, Frequency: Per email, Owner: Customer Service.
  - (These are as specified in BRD Data & Storage section.)
- Test data provisioning owner confirmations:
  - Confirm test data provisioning responsibilities — TBD – confirm with Customer Service and Master Data Owners.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:
  - Test environments provisioned and accessible (non-production subscription and shared services) — TBD – confirm with Architecture Owner.
  - Required integrations reachable or appropriate mocks/stubs available (Graph API, SAP via APIM, Azure AI services).
  - Test data and mailboxes available.
  - Smoke tests for basic connectivity passed.
- Suspension criteria:
  - Critical/unresolved defects blocking end-to-end flow (severity criteria defined in Section 18).
  - Major environment or integration outage preventing testing (e.g., no mailbox access, SAP API down).
- Exit criteria:
  - All critical and high priority defects resolved or mitigated with approval from Business Owner.
  - Acceptance criteria met:
    - ≥95% header field accuracy and ≥90% line accuracy on pilot customers.
    - Draft within 5 minutes for 95% of POs (performance tests).
    - Duplicate PO detection 100% in test set.
    - No orders released without CSR action in MVP1.
  - Security and compliance checks passed and AI Governance Council sign-off artifacts available.
  - UAT sign-off by Customer Service Operations (pilot branches).

# 18. Defect Management
- Defect severity (examples aligned to acceptance criteria and business impact):
  - Critical (P0): End-to-end processing completely fails; duplicates not detected leading to duplicate drafts; orders released without CSR action; inability to connect to SAP for draft creation when required for tests.
  - High (P1): Extraction accuracy below acceptance thresholds on pilot customers; price variance not flagged; RBAC breach allowing cross-branch access.
  - Medium (P2): UI display issues, incorrect confidence displayed, intermittent API errors causing retries.
  - Low (P3): Cosmetic UI issues, telemetry label missing, minor log format issues.
- Tracking tool: TBD – confirm with QA Manager.
- Triage process:
  - Daily defect triage during system and UAT phases with QA Lead, Dev Lead, Architecture Owner and Business Owner representatives.
  - Critical defects escalate to stakeholders immediately.
- Resolution and verification:
  - Defects fixed in development, unit tested, deployed to test environment, and regression tested before closure.

# 19. Risks and Mitigations
(From BRD and test perspective)
- Unusual PO layouts
  - Mitigation: Include exploratory testing and diverse PO layout test set; keep CSR review and confidence flags.
- Missing cross-references
  - Mitigation: Validate catalog search fallback via Azure AI Search; mark lines as unmatched and require CSR action.
- SAP API limits
  - Mitigation: Queueing and retry approach, performance tests to measure effect.
- Mailbox access approvals delayed
  - Mitigation: Use test mailboxes and/or mocked Graph API events until approvals are complete.
- AI hallucination / incorrect mappings
  - Mitigation: Enforce validation against SAP master data and cross-references; human-in-the-loop for every order; AI Governance Council oversight.
- Test data availability and confidentiality
  - Mitigation: Use sanitized real data and define data handling processes; confirm with Security/Compliance Owner.
- Environment readiness delays
  - Mitigation: Early confirmation of environment provisioning (TBD – confirm with Architecture Owner).

# 20. Test Deliverables and Reporting
- Deliverables:
  - Test plan (this document).
  - Test cases and test scripts (functional, integration, performance).
  - Test data sets (sanitized PO emails, cross-reference files, SAP test data).
  - Test execution logs and defect reports.
  - Performance and load test reports (showing 5-minute and 300 emails/hour results).
  - AI accuracy and confidence reports (header/line accuracy, confidence distributions).
  - UAT sign-off report and acceptance checklist (covering BRD acceptance criteria).
  - Monitoring and observability verification report (end-to-end traceability).
- Reporting cadence:
  - Daily test status during system test and UAT phases.
  - Weekly summary to Business Owner and Architects.
  - Final test summary with acceptance criteria results and outstanding risks.
- Report recipients:
  - Customer Service Operations (Business Owner), QA Team, Architecture Owner, SAP Integration Team, AI Governance Council (as needed).

# 21. Traceability and Metrics
- Traceability:
  - Each BRD functional requirement, user story and acceptance criterion will be mapped to test cases. (Detailed traceability matrix to be produced: TBD – confirm with QA Manager).
- Key metrics / KPIs to report:
  - Header field accuracy (aggregate and per-field).
  - Line-level accuracy.
  - Processing time distribution and percentage of drafts created within 5 minutes.
  - Number of emails processed, success rate, failure rate.
  - Duplicate detection rate (target 100% on test set).
  - CSR correction rate (number and percentage of drafts modified by CSR).
  - Orders older than 30 minutes count and time-in-queue metrics.
  - Security/RBAC violations (should be zero).
  - Availability (measured uptime) vs target 99.5% 24x5.
- Metric collection owner: TBD – confirm with Monitoring/Operations Owner.

# 22. Test Schedule
- High-level timeline from BRD:
  - MVP1: Apr–Jul 2026.
- Test phases (high-level; exact dates TBD – confirm with QA Manager and Project Manager):
  - Test planning and environment setup — start by Apr 2026 (align with MVP1 timeline).
  - Component & integration tests — Apr–May 2026.
  - System testing including AI accuracy measurement — May–Jun 2026.
  - Performance & reliability testing (300 emails/hour, 5-minute SLA) — Jun 2026.
  - UAT with CS branches / pilot customers — Jun–Jul 2026.
  - Final acceptance and sign-off — by end of Jul 2026 (subject to schedule alignment).
- Exact test schedule and milestones: TBD – confirm with Project Manager.

# 23. End-to-End Scenario
Representative E2E scenario to validate core flow and acceptance criteria:
1. Branch mailbox receives a PO email with PDF attachment (single PO per email assumption).
2. Graph API triggers Event Grid new mail event.
3. Event Grid forwards event to Azure Service Bus.
4. Order Extraction Service dequeues event and saves email copy to Azure Blob Storage.
5. Order Extraction Service invokes APIM which calls Azure Document Intelligence (extract) and Azure OpenAI (map fields).
6. Extracted header and line data returned with per-field confidence; data stored in Cosmos DB draft record with provenance.
7. Customer identified by sender domain; item matching attempted via uploaded customer cross-reference; unmatched lines fall back to Azure AI Search catalog.
8. APIM calls SAP S/4HANA APIs to validate customer active, material validity and price; price variance >5% flagged.
9. Order Creation Service creates a draft sales order in SAP (draft status) and writes draft metadata to Cosmos DB.
10. Web UI (Review Queue) displays draft for CSR assigned to that branch; fields show confidence values and highlight lines with no cross-reference.
11. CSR reviews and corrects if necessary; CSR saves and executes release action — resulting in SAP order release (release step must be CSR-initiated).
12. End-to-end traceable correlation ID links the incoming email to SAP draft/order number and is available in logs.
13. Metrics captured: processing time (should be <=5 minutes for 95% of POs), extraction accuracy, duplicate detection (if duplicate PO number present, appropriate duplicate flow triggered).

# 24. Approvals
- Required sign-offs for test completion and release (as per BRD approvals):
  - AI Governance Council
  - Finance (BIR)
  - AI intake
  - Global Intake
  - C2P
  - WAB
  - Customer Service Operations (Business Owner) — UAT acceptance
  - Architecture Owner — integration verification
- QA sign-off: QA Lead (Master Test Plan owner) after acceptance criteria met and defects triaged/resolved.

--- 
Notes / Outstanding items requiring confirmation (TBD):
- Test environment access and exact environment names — TBD – confirm with Architecture Owner.
- Test mailbox account provisioning and mailbox access approvals — TBD – confirm with Customer Service Owner.
- SAP non-production endpoints and mock/stub policy — TBD – confirm with SAP Integration Team.
- Defect tracking tool and CI/CD test automation integration — TBD – confirm with QA Manager / DevOps Owner.
- Monitoring and dashboard tool selection (Datadog vs Azure Monitor config) and alert thresholds — TBD – confirm with Monitoring Owner.
- Accessibility requirements and supported browsers/devices — TBD – confirm with UI Owner.

This test plan covers all MVP1 functional requirements, user stories, business rules, thresholds, NFR targets, roles and permissions, integrations, data sources, AI quality controls, assumptions, dependencies, risks, acceptance criteria and the MVP1 timeline as required by the BRD and the architecture description.