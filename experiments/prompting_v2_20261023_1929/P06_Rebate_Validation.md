# 1. Document Control
- Title: Master Test Plan – Supplier Rebate Claim Validation (MVP1)
- Version: 1.0
- Application: Supplier Rebate Claim Validation
- Prepared by: QA Lead (Supplier Rebate Program) — TBD – confirm with Supplier Programs
- Reviewed by: Rebate Programs Finance, Architecture, Program Admin, AI Governance Council, Finance (BIR) — individual reviewers TBD – confirm with owners
- Audience: Business Owners (Supplier Programs Finance), Architects, QA Team, Program Admin, Finance Manager, AI Governance Council
- Purpose statement: Define the test approach, scope, coverage, entry/exit criteria and acceptance verification required to validate MVP1 of Supplier Rebate Claim Validation as described in the BRD (Version 1.0, 17 Feb 2026) and the Solution Architecture (Non-production).

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation, Version 1.0, 17 Feb 2026 (BRD)
- Supplier Rebate Claim Validation - Solution Architecture (Non-production) (architecture diagram: P06_Rebate_Validation_Architecture.png)
- Appendix: Rebate Claim Validation MVP1 Scope Overview (BRD)
- AI Governance Council approvals and compliance notes referenced in BRD
- (Any additional supporting documents) TBD – confirm with <owner>

# 3. Test Objectives
- Verify every MVP1 functional requirement and user story from the BRD is implemented and behaves per specification.
- Verify business rules and thresholds:
  - Finance Manager approval enforced for claims above USD 50,000.
  - Analyst cannot approve own claims (segregation of duties).
- Verify NFR targets exactly as stated:
  - Availability: 99% business hours.
  - Performance: single supplier-year calculation ≤ 2 minutes; month-end batch of 400 agreements ≤ 8 hours.
  - Auditability: every calculation reproducible with agreement version and data snapshot date.
- Verify AI/extraction quality and controls:
  - Extraction accuracy ≥ 95% on golden agreements (acceptance criterion).
  - Calculation accuracy = 100% against analyst-verified examples (acceptance criterion).
  - Analyst confirmation required and enforced before calculations use terms.
- Verify integrations, data flows, data ownership, classification and refresh frequencies as documented.
- Provide test evidence for acceptance criteria listed in BRD and readiness for AI Governance Council review.

# 4. In Scope
- All MVP1 functional features and quality attributes listed in the BRD:
  - Upload of agreement PDFs and amendments.
  - AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions using Azure Document Intelligence and Azure OpenAI.
  - Analyst confirmation step; only confirmed terms used in calculations.
  - Calculation using purchase data from Delta Lake (EUDM) via Databricks SQL: eligible spend, tier reached, earned rebate (retroactive applies rate to full spend; incremental applies rate per tier band).
  - Claim worksheet with supporting purchase lines, export to Excel, and variance to accrual.
  - RBAC and approval workflow: Azure AD authentication; Finance Manager approval above USD 50,000; analysts cannot approve own claims.
  - Auditability requirements: reproducible calculations with agreement version and data snapshot date.
  - Data sources and owners as listed: Rebate agreements (Upload, Ad-hoc, owner Supplier Programs, Restricted), Purchase data (Delta Lake (EUDM), Daily, owner Finance Data, Confidential), Product line mapping (Configuration, Monthly, owner Program Admin, Internal), Calculations (Tool output, Per run, owner Supplier Programs, Confidential).
  - Integrations and connections described in architecture (see section 8 and section 11).
  - Quality checks: Agreement term completeness, tier thresholds ascending, purchase data reconciliation to GL totals.
  - NFRs: Availability 99% business hours; Performance targets above.
  - AI governance and SOX relevance items called out (AI Governance Council approval; C2P).
- Test levels: unit/integration (component), service/API, system, regression, user acceptance (business sign-off).
- Test types: functional, integration, security, data quality, AI/extraction accuracy, performance/load, reliability/recovery, audit/logging, compatibility (browsers supported by Web UI), export to Excel verification.

# 5. Out of Scope
- All MVP2 features and explicit exclusions listed in BRD:
  - Supplier portal submission (MVP2).
  - Dispute tracking (MVP2).
  - Accrual posting to finance (MVP2).
  - Amendment comparison (MVP2).
- Out of scope (explicit BRD exclusions):
  - Customer rebates (sell-side).
  - Price protection claims.
  - Supplier payment collection.

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Delta Lake purchase data is complete for the last 24 months.
  - Agreements are mostly digital PDFs.
  - Analyst confirmation step will be used to mitigate complex agreement language.
- Dependencies (from BRD and Architecture):
  - Data platform team for Databricks access (Databricks SQL / Delta Lake EUDM/IAP).
  - Supplier Programs SMEs for golden dataset used for extraction accuracy testing.
  - Azure AD (Entra ID) for identity and RBAC.
  - APIM, Azure Document Intelligence and Azure OpenAI availability in Azure AI Landing Zone.
  - Azure Blob Storage and Azure PostgreSQL for agreements and confirmed terms/calculation results.
  - Supporting services: Datadog, GitHub Actions, Key Vault, Azure Monitor for observability and secrets.
- Test constraints:
  - Solution labeled as Non-production; production-only behaviors not in scope.
  - Test data provisioning from Delta Lake and golden agreements depends on owners; timing dependent.
- Items requiring confirmation:
  - Test environment names and subscription access for Non-production Subscription, Shared Services Subscription, Azure AI Landing Zone — TBD – confirm with Architecture owner
  - Test account provisioning and APIM keys / Managed Identity access for Azure Document Intelligence and Azure OpenAI — TBD – confirm with Cloud/AI owner

# 7. Test Strategy
- Approach:
  - Validate requirements through layered testing: component/unit tests (development), integration tests (services + AI + Databricks), system tests (end-to-end within Non-production), performance/load tests, security and compliance tests, and UAT with Rebate Analysts and Finance Manager.
  - Use the golden dataset maintained by Supplier Programs SMEs for AI extraction accuracy validation.
  - All AI-extracted terms require explicit Analyst confirmation step; automate test cases to assert that unconfirmed terms are not used for calculation.
- Test levels:
  - Component/unit testing (dev-owned) — verify Agreement Service, Calculation Service logic (including retroactive vs incremental calculations).
  - Integration testing — Agreement Service ↔ Blob Storage; Agreement Service ↔ Azure PostgreSQL; Calculation Service ↔ Azure PostgreSQL; Calculation Service ↔ Delta Lake (Databricks SQL); APIM ↔ Azure Document Intelligence; APIM ↔ Azure OpenAI.
  - System testing — end-to-end upload → extraction → confirmation → calculation → worksheet → export → approval workflow.
  - Performance/load testing — validate stated performance targets.
  - Security and compliance testing — RBAC, Azure AD auth, data classification enforcement, AI governance controls.
  - UAT — Rebate Analysts and Finance Manager validation against business scenarios and acceptance criteria.
- Test types and techniques:
  - Functional: positive/negative, boundary and edge cases (tier thresholds, ascending thresholds, missing tiers).
  - Data-driven: use representative purchase data scenarios (zero spend, spend exactly on thresholds, multi-tier crossing, retroactive vs incremental).
  - AI/extraction testing: precision/recall style checks on extracted fields with page references; human-in-the-loop confirmation flows.
  - Integration: contract tests for REST endpoints and Databricks SQL queries (validate query results match expected eligible spend).
  - Security: authentication, authorization, data access control, secrets handling.
  - Performance: timing measurements and batch throughput validation for the month-end batch of 400 agreements.
  - Reliability: simulate transient failures for Databricks/AI services and verify retry/recovery and audit trails.
- Test tools and environment orchestration:
  - Test tool selection and test environment provisioning: TBD – confirm with <owner>
  - Defect tracking and test management tool: TBD – confirm with <owner>

# 8. Functional Test Coverage
For each BRD MVP1 functional requirement and user story, list what will be verified.

- Upload of agreement PDFs and amendments (MVP1)
  - Verify PDFs and amendment files can be uploaded via Web UI.
  - Verify storage of uploaded agreements in Azure Blob Storage (Agreement Service -> Azure Blob Storage).
  - Verify metadata captured (uploader, upload timestamp, version).
  - Verify security: upload only by authenticated Azure AD users; uploaded blobs access restricted as per security classification.
- AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions using Azure Document Intelligence and Azure OpenAI (MVP1)
  - Verify APIM -> Azure Document Intelligence call is made with correct layout parameters.
  - Verify APIM -> Azure OpenAI calls for term extraction are invoked per architecture.
  - Verify extracted fields include supplier, period dates, tier definitions (thresholds and rates), retroactive vs incremental flag, eligible product lines, exclusions, and page references.
  - Verify extraction includes page references as required by user story.
  - Verify extraction failures logged and surfaced to analyst for manual correction.
  - Validate extraction accuracy against golden agreements dataset; measure and report extraction accuracy (target ≥ 95%).
- Analyst confirmation step; only confirmed terms used (MVP1)
  - Verify UI shows extracted terms with page references.
  - Verify Analyst can edit/correct extracted terms.
  - Verify unconfirmed terms cannot be used by Calculation Service (Agreement Service -> Azure PostgreSQL holds confirmed terms).
  - Verify audit record created for confirmation event (user, timestamp, agreement version).
- Calculation using purchase data from Delta Lake (EUDM) via Databricks SQL (MVP1)
  - Verify Calculation Service calls Delta Lake (Calculation Service -> Delta Lake EUDM/IAP (Databricks SQL) | HTTPS/443 OAuth 2.0) to retrieve purchase lines.
  - Verify eligible spend calculations according to product line mapping and eligible/exclusion rules.
  - Verify tier logic:
    - Retroactive: apply rate to full eligible spend for the tier reached.
    - Incremental: apply rate per tier band.
  - Verify tier thresholds require ascending thresholds (validate BRD quality check).
  - Verify calculation correctness against analyst-verified examples (target 100% calculation accuracy).
  - Verify purchase data reconciliation to GL totals quality check executed and discrepancies reported.
- Claim worksheet with supporting purchase lines, export to Excel, and variance to accrual (MVP1)
  - Verify worksheet contains supplier, period, confirmed terms (with agreement version), purchase line support, tier reached, earned rebate, and variance to accrual.
  - Verify export to Excel functions and exported file includes required fields and formatting.
  - Verify worksheet stores calculation results in Azure PostgreSQL (Calculation Service -> Azure PostgreSQL).
- User Stories (explicit checks)
  - Rebate Analyst uploads an agreement and sees extracted tiers with page references — verify as above.
  - Analyst must confirm extracted terms before use — verify confirmation step blocks calculations.
  - Rebate Analyst runs a calculation for a period and sees purchases, tier reached and earned rebate — verify UI and worksheet data match calculated results.
  - Finance Manager approves claims above USD 50,000 — verify that claims with earned rebate > USD 50,000 route to Finance Manager for approval and cannot be approved by analysts (including self-approval prevention).
- Integration contract tests (per architecture connections)
  - Rebate Analysts -> App Gateway | HTTPS/443 AD/SSO — verify SSO sign-in and session handling.
  - Finance Managers -> App Gateway | HTTPS/443 AD/SSO — verify Finance Manager role mapping.
  - Azure AD (Entra ID) -> App Gateway | HTTPS/443 AD/SSO / OAuth 2.0 — verify token-based auth flows.
  - Web UI -> Agreement Service | REST — validate API contracts and error handling.
  - Web UI -> Calculation Service | run calculation — validate request/response, input validation.
  - Azure Function (Batch Scheduler) -> Agreement Service | month-end batch — verify month-end batch trigger behavior (note: scheduling and batch control details TBD – confirm with <owner>).
  - Agreement Service -> Azure Blob Storage | agreements — verify blob operations and access controls.
  - Agreement Service -> Azure PostgreSQL | confirmed terms — verify DB writes and readback.
  - Calculation Service -> Azure PostgreSQL | results — verify DB writes and readback.
  - Calculation Service -> Delta Lake EUDM/IAP (Databricks SQL) | HTTPS/443 OAuth 2.0 — verify query execution and expected result schema.
  - Agreement Service -> APIM | HTTPS/443 Managed Identity — verify managed identity auth.
  - APIM -> Azure Document Intelligence | layout — verify API calls and responses.
  - APIM -> Azure OpenAI | term extraction — verify API calls and responses.
- Quality checks
  - Agreement term completeness: verify extraction and confirmation fail if required fields missing; generate reviewer queue.
  - Tier thresholds ascending: create negative test cases where thresholds are non-ascending and verify system flags them.
  - Purchase data reconciliation to GL totals: verify reconciliation reports identify gaps.

# 9. Roles, Permissions and Workflow Testing
- Roles to be tested (BRD user roles):
  - Rebate Analyst
    - Verify ability to upload agreements, view and edit extracted terms, confirm terms, run calculations, view claim worksheets, export to Excel.
    - Verify cannot approve claims (explicit segregation of duties).
  - Finance Manager
    - Verify ability to review and approve claims above USD 50,000.
    - Verify access to variance to accrual and ability to view worksheets and supporting purchase lines.
  - Program Admin
    - Verify ability to maintain supplier mappings, product line mappings and calculation settings (test scope: config changes effect on calculations).
- Authentication & Authorization:
  - Verify Azure AD (Entra ID) SSO authentication for all users (Rebate Analysts, Finance Managers).
  - Verify role mapping and permissions enforced per RBAC: access to upload, view, confirm, run calculations, approve (Finance Manager), maintain configuration (Program Admin).
  - Verify segregation of duties: Analyst cannot approve their own submissions or any approvals reserved for Finance Manager.
  - Verify approval thresholds: claims ≤ USD 50,000 can be approved by Program-defined approvers (if defined) — if unclear, verify default behavior and escalate: TBD – confirm with <owner>.
- Workflow testing:
  - End-to-end approval workflow for claims below and above USD 50,000.
  - Negative cases: attempt to bypass confirmation and run calculation; attempt to approve as unauthorized user; verify system blocks and logs these events.

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization
  - Verify Azure AD integration (Entra ID), OAuth flows and token validation per architecture.
  - Validate least privilege access for data stores: Blob Storage, Azure PostgreSQL, Delta Lake.
- Data protection
  - Verify agreements and spend data access is restricted as per BRD classification (Restricted / Confidential / Internal).
  - Verify secrets usage via Key Vault for API keys and service principals; validate access controls.
- Compliance & Governance
  - Verify logging and audit trails capture agreement version, confirmation events, calculation runs, data snapshot date, and approver identities for SOX relevance as assessed via C2P.
  - Verify AI governance controls are in place (human-in-the-loop Analyst confirmation, AI Governance Council approvals recorded).
- Penetration and vulnerability testing:
  - Scope and scheduling: TBD – confirm with Security owner.
- Data retention and masking:
  - Verify masking or restricted access where required for confidential purchase data in test environments; test data handling rules TBD – confirm with Data Owner.

# 11. AI and Data Quality Validation
- AI/Extraction accuracy targets and tests:
  - Acceptance criterion: ≥95% accuracy of extracted tier terms on golden agreements.
  - Test activities:
    - Use golden agreements dataset (owner: Supplier Programs SMEs) to measure extraction precision and recall for fields: supplier, period, tiers (threshold and rate), retroactive/incremental flag, eligible product lines, exclusions, page references.
    - Record page reference correctness for each extracted field.
    - Track per-field accuracy and overall extraction accuracy.
    - Create error taxonomy (missing field, wrong threshold value, wrong rate, incorrect retroactive flag, incorrect eligibility).
  - Failure handling:
    - Verify any extraction below threshold surfaces the document for mandatory Analyst confirmation and correction.
    - Verify corrected terms are stored with versioning in Azure PostgreSQL.
- Controls against hallucination and incorrect AI outputs:
  - Verify human-in-the-loop Analyst confirmation enforced before terms used.
  - Verify system captures AI confidence values if provided; if confidence capture not available, note: TBD – confirm with AI owner.
  - Verify logging of AI responses and prompts (APIM logs) for traceability and potential audit.
  - Verify AI Governance Council approvals recorded and requirements applied.
- Data quality for purchase data and mappings:
  - Validate Delta Lake purchase data completeness for last 24 months (assumption).
  - Validate product line mapping refresh frequency (monthly) and owner (Program Admin) usage in calculations.
  - Perform reconciliation tests: aggregated eligible spend vs GL totals; report mismatches.
- Golden dataset dependency:
  - Golden dataset availability and maintenance by Supplier Programs SMEs — dependency; schedule and ownership verification required.

# 12. Performance Testing
- Targets (exact values from BRD):
  - Single supplier-year calculation: within 2 minutes.
  - Month-end batch: 400 agreements within 8 hours.
  - Availability: 99% business hours.
- Performance tests to run:
  - Measure time for single supplier-year calculation including extraction confirmation step bypassed and included.
  - Run month-end batch simulation of 400 agreements (batch scheduler Azure Function -> Agreement Service) and measure end-to-end batch completion time including Databricks queries.
  - Measure system behavior under concurrent calculations (TBD – confirm number of concurrent users with owner) — default concurrency assumptions: TBD – confirm with <owner>.
  - Verify Calculation Service query times for typical Databricks SQL queries and aggregate time including network/hops.
  - Validate export-to-Excel performance for large worksheets (size TBD – confirm with <owner>).
- Test data and environment:
  - Use representative purchase data volumes from Delta Lake for realistic load (data volumes TBD – confirm with Finance Data owner).
- Performance monitoring:
  - Use supporting services shown in architecture: Datadog and Azure Monitor for measurement (configuration TBD – confirm with Supporting Services owner).
- Non-functional acceptance:
  - Report and obtain sign-off if targets are met (or if mitigations documented).

# 13. Reliability and Recovery Testing
- Availability and resilience tests:
  - Verify system meets 99% business hours availability target in Non-production test window (design test to simulate uptime metrics; production SLA compliance for final acceptance).
  - Simulate transient failures for:
    - Delta Lake (Databricks SQL) connectivity failures and validate retry logic and error reporting.
    - Azure Document Intelligence / Azure OpenAI failures and validate fallback, retries, and error surfacing to Analyst.
    - Azure PostgreSQL or Blob Storage transient errors and validate transaction handling and idempotency.
  - Verify batch scheduler (Azure Function) recovers and resumes month-end batch processing after transient failure.
- Recovery tests:
  - Verify calculation reproducibility: given agreement version and data snapshot date, rerun calculation to reproduce identical results.
  - Verify data snapshot mechanisms for purchase data are recorded and used for reproducibility (snapshot date captured in calculation results).
  - Verify manual and automatic retry behavior documented and tested.
- Observability:
  - Verify Datadog and Azure Monitor alerting on service failures, extraction errors, and batch failures (alert thresholds TBD – confirm with Monitoring owner).

# 14. Accessibility and Compatibility Testing
- Accessibility:
  - Verify Web UI basic accessibility checks for Rebate Analysts and Finance Managers (keyboard navigation, readable labels). Detailed accessibility standard (e.g., WCAG) compliance: TBD – confirm with Accessibility owner.
- Compatibility:
  - Verify Web UI works in supported browsers and versions — supported browser list: TBD – confirm with Program Admin.
  - Verify Web UI behaves for On-Premise clients via App Gateway per architecture.

# 15. Logging, Monitoring and Audit Testing
- Logging and audit requirements (from BRD):
  - Capture agreement version, confirmation events (user, timestamp), calculation runs, data snapshot date, AI extraction inputs/outputs, and approval events.
  - Verify logs and audit trails persist to configured monitoring/log store (Datadog/Azure Monitor) and are queryable for audits.
- Tests:
  - Run calculation and verify audit record contains: agreement ID, agreement version, confirmed terms, data snapshot date, purchase data range used, calculation inputs and outputs, and user who triggered run.
  - Verify AI extraction logs record the document ID, page references returned, and any confidence metadata (if available).
  - Verify approval event logs capture approver identity and timestamp.
  - Verify retention policy and access controls for logs: TBD – confirm with Compliance owner.
- Alerting:
  - Validate alerts for extraction failures, reconciliation mismatches, batch failures. Alert definitions and thresholds: TBD – confirm with Monitoring owner.

# 16. Test Environments and Test Data
- Environments (per architecture):
  - Non-production Subscription (Shared AKS Non-prod with Web UI, Agreement Service, Calculation Service; Integration & Eventing with Azure Function (Batch Scheduler); Data Stores).
  - Shared Services Subscription (Azure AD (Entra ID), App Gateway).
  - Azure AI Landing Zone (APIM, Azure Document Intelligence, Azure OpenAI).
  - Supporting Services boundary (Datadog, GitHub Actions, Key Vault, Azure Monitor).
  - Exact environment names, subscriptions and access: TBD – confirm with Architecture owner.
- Test data:
  - Agreements:
    - Golden agreements dataset (Supplier Programs SMEs) for extraction accuracy tests.
    - Variety of PDF contract types: simple tiers, multi-tier, retroactive, incremental, with exclusions.
  - Purchase data:
    - Delta Lake (EUDM) data extracts for last 24 months (assumption). Representative scenarios: zero spend, exactly-on-threshold, tier-crossing, high volume.
  - Product line mapping:
    - Representative mappings covering eligible and excluded product lines; contributor: Program Admin.
  - Calculations:
    - Analyst-verified examples (for 100% calculation accuracy) — maintain test cases with expected results.
- Test data management:
  - Mask confidential fields where necessary for privacy in test environments.
  - Golden dataset owner and refresh cadence: Supplier Programs SMEs — coordinate and confirm availability.
  - Provisioning and refresh of Delta Lake test extracts: TBD – confirm with Data platform team.

# 17. Entry, Suspension and Exit Criteria
- Entry Criteria for system testing:
  - All MVP1 components deployed to Non-production environment and accessible.
  - Test environments provisioned and configured (including Azure AD, APIM, Azure AI services).
  - Golden dataset available and test purchase data loaded.
  - Development unit tests and component-level tests complete and passed.
  - Test plan and test cases reviewed and signed off by QA Lead and Business Owner.
- Suspension Criteria:
  - Critical defects blocking core functionality (upload, extraction, confirmation, calculation, export) not resolved.
  - Data access to Delta Lake or AI services unavailable for greater than agreed outage window — escalation per dependency owners.
- Exit Criteria for MVP1 test phase:
  - All MVP1 functional test cases executed with pass rate acceptable to QA and Business Owner.
  - AI extraction accuracy validated ≥ 95% on golden dataset.
  - Calculation accuracy validated = 100% against analyst-verified examples.
  - Performance targets for single supplier-year and month-end batch met or documented mitigations accepted.
  - Security and compliance checks completed, and critical/high findings remediated or mitigated with acceptance by Security/Compliance owners.
  - UAT sign-off by Supplier Programs Finance (Rebate Analysts) and Finance Manager.
  - Test summary report and artifact handover delivered to stakeholders.
- Resumption Criteria:
  - For suspended test cycles, resume when blocking issues are resolved and validated in a pre-check regression.

# 18. Defect Management
- Defect reporting and triage:
  - Defect tracking tool: TBD – confirm with <owner>.
  - Defect severity levels:
    - Critical: system unusable for core workflows (upload, confirm, calculate, export) or data loss / incorrect rebates causing material financial risk.
    - High: major functionality broken or incorrect calculation scenarios impacting material subset.
    - Medium: non-critical functionality, UI issues, or missing non-essential features.
    - Low: cosmetic, documentation, or minor usability issues.
  - Triage cadence: daily for Critical/High, weekly for Medium/Low — confirm with QA Lead and Business Owner.
  - Owners for defect resolution: Development/Architecture owners per component; issues related to data or golden dataset escalated to Data platform team / Supplier Programs SMEs.
- Defect lifecycle:
  - New -> Confirmed -> In Progress -> Fixed -> Verified -> Closed (or Reopened) — defect workflow tool specifics: TBD – confirm with <owner>.

# 19. Risks and Mitigations
(From BRD Risk Register and additional test hazards)
- Risk: Complex agreement language causing extraction errors.
  - Mitigation: Mandatory Analyst confirmation; maintain golden dataset; focused test cases for complex clauses.
- Risk: Data lake gaps impacting calculations.
  - Mitigation: Reconciliation checks to GL totals; escalate to Data platform team; include negative test cases.
- Risk: Retroactive vs incremental misread by AI.
  - Mitigation: Explicit extracted field for retroactive/incremental; test cases for both models; mandatory analyst confirmation.
- Risk: Availability or throttling of Azure Document Intelligence / Azure OpenAI.
  - Mitigation: Test resilience and retry logic; log and surface failures to analysts; define fallback manual process for critical month-end (TBD – confirm with Program Admin).
- Risk: Golden dataset availability or quality.
  - Mitigation: Supplier Programs SMEs to maintain golden dataset; include dependency in schedule.
- Risk: Unclear backend behavior noted in BRD user story note ("to be validated with the backend architects").
  - Mitigation: Confirm backend contracts and APIs with Architecture owner before test execution; create integration test stubs if needed.

# 20. Test Deliverables and Reporting
- Deliverables:
  - Test Plan (this document).
  - Test cases and test scripts for functional, integration, AI/extraction accuracy, performance, security, reliability.
  - Test data sets (golden agreements, purchase extracts, mapping configs) — ownership records.
  - Test execution reports and traceability matrix.
  - Defect logs and triage summaries.
  - Performance test reports with metrics against targets.
  - AI extraction accuracy report against golden dataset.
  - UAT sign-off forms from Rebate Analysts and Finance Manager.
  - Final Test Summary and Recommendations.
- Reporting cadence:
  - Daily test status for active test runs (Critical/High defects).
  - Weekly summary to stakeholders (overall progress, open defects, risks).
  - Final report at test completion.
- Distribution:
  - QA Lead, Supplier Programs Finance, Architecture, Program Admin, Finance Manager, AI Governance Council, Data platform team.

# 21. Traceability and Metrics
- Traceability:
  - Map every BRD MVP1 functional requirement and user story to one or more test cases. (Test artifacts will include Requirement-to-Test mapping.)
  - Key requirements mapped explicitly:
    - Upload agreements -> test cases for upload, storage, access controls.
    - AI extraction fields -> per-field extraction test cases and golden dataset verification.
    - Analyst confirmation -> test cases for confirmation gating and audit logging.
    - Calculation logic (retroactive vs incremental) -> test cases with expected numeric results.
    - Claim worksheet export and variance to accrual -> worksheet content and export verification cases.
    - Approval workflow (USD 50,000 threshold) -> approval routing and RBAC tests.
- Metrics / KPIs to report:
  - Test coverage (% of BRD MVP1 requirements with test cases).
  - Test execution (planned vs executed).
  - Pass/fail rates by test type.
  - Number and severity of defects.
  - AI extraction accuracy (%) overall and per-field.
  - Calculation accuracy (%) against analyst-verified examples.
  - Performance metrics: average and percentile times for single calculation; total batch time for 400 agreements.
  - Availability measured during test window (% uptime).
  - Time to remediate Critical/High defects.

# 22. Test Schedule
- High-level timeline (from BRD):
  - MVP1: Mar–Jun 2026 — test phases to be executed within this window.
  - Detailed test phase dates, test execution windows, and cutover windows: TBD – confirm with QA Lead, Architecture owner and Program Admin.
- Key milestones:
  - Environment readiness and data provisioning: TBD – confirm with owners.
  - Component/integration testing start: TBD – confirm with Development owner.
  - System testing start: TBD – confirm with QA Lead.
  - Performance and reliability testing: TBD – confirm with QA Lead.
  - UAT and business sign-off: within Mar–Jun 2026 window — exact dates TBD – confirm with Supplier Programs Finance and Finance Manager.

# 23. End-to-End Scenario
Representative E2E scenario (will form a UAT script):

Scenario: Rebate Analyst processes a supplier agreement and produces an approvable claim worksheet
1. Rebate Analyst authenticates via Azure AD (Entra ID) through App Gateway (Rebate Analysts -> App Gateway | HTTPS/443 AD/SSO).
2. Analyst uploads a supplier agreement PDF via Web UI; Agreement Service stores file in Azure Blob Storage and records metadata.
3. Agreement Service (via APIM managed identity) invokes Azure Document Intelligence (APIM -> Azure Document Intelligence | layout) and Azure OpenAI (APIM -> Azure OpenAI | term extraction) to extract supplier, period, tier thresholds & rates, retroactive/incremental flag, eligible product lines and page references.
4. Web UI displays extracted terms with page references to Analyst.
5. Analyst reviews and confirms/edits terms; Agreement Service persists confirmed terms in Azure PostgreSQL.
6. Analyst triggers calculation for a specified period (Web UI -> Calculation Service | run calculation).
7. Calculation Service queries Delta Lake EUDM/IAP via Databricks SQL (Calculation Service -> Delta Lake EUDM/IAP (Databricks SQL) | HTTPS/443 OAuth 2.0) to retrieve purchase lines; applies product line mapping (from configuration) to determine eligible spend.
8. Calculation Service computes tier reached and earned rebate (respecting retroactive or incremental logic) and writes results to Azure PostgreSQL.
9. Claim worksheet is generated with supporting purchase lines; Analyst exports worksheet to Excel and reviews variance to accrual.
10. If earned rebate > USD 50,000, the worksheet is routed to Finance Manager for approval; Finance Manager authenticates and approves (Finance Manager -> App Gateway | HTTPS/443 AD/SSO).
11. Audit logs recorded in Datadog/Azure Monitor capture agreement version, confirmation event, calculation inputs/outputs, snapshot date, and approval event.
12. Validate reproducibility by rerunning calculation using agreement version and data snapshot date and asserting identical results.

# 24. Approvals
- Required approvers (per BRD):
  - AI Governance Council
  - Finance (BIR)
  - AI intake
  - Global Intake
  - C2P
  - WAB
  - Supplier Programs Finance (Business Owner)
  - Architecture owner
  - QA Lead
- Sign-off procedure:
  - Deliver test summary, AI extraction accuracy report, calculation accuracy evidence, performance report, security findings and remediation evidence.
  - Obtain formal sign-off signatures or recorded approvals from named approvers — logistics and approver contacts: TBD – confirm with Supplier Programs Finance.

--- 
Notes / Open items requiring confirmation (owners indicated):
- Test toolset selection (automation, performance, test management): TBD – confirm with QA Lead
- Test environment names, subscription access and provisioning schedule: TBD – confirm with Architecture owner
- Defect tracking tool and triage cadence owner: TBD – confirm with QA Lead
- Supported browsers and accessibility standards: TBD – confirm with Program Admin
- Alert thresholds and monitoring configuration: TBD – confirm with Monitoring owner
- Exact concurrency targets for performance tests beyond single calculation and month-end batch: TBD – confirm with Performance owner
- Any backend API contract clarifications referenced in BRD note "to be validated with the backend architects": TBD – confirm with Architecture owner

End of Master Test Plan (MVP1).