# 1. Document Control
- Title: Supplier Rebate Claim Validation — Master Test Plan (MVP1)
- Version: 1.0
- Application: Supplier Rebate Claim Validation (MVP1)
- Prepared by: TBD – confirm with Supplier Programs QA Lead
- Reviewed by: TBD – confirm with Supplier Programs, Architecture, Finance
- Audience: Supplier Programs Finance (Business Owner), Architects, QA Team, Program Admin, Finance Managers, AI Governance Council
- Purpose: Define the test approach, scope, coverage and exit criteria to validate MVP1 functionality, non‑functional requirements and integrations for the Supplier Rebate Claim Validation solution as described in the BRD (Business Requirement Specification – Supplier Rebate Claim Validation v1.0, 17 Feb 2026) and the Solution Architecture (Non-production).

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation, Version 1.0, 17 Feb 2026 (BRD)
- Solution Architecture: Supplier Rebate Claim Validation - Solution Architecture (Non-production) (architecture diagram P06_Rebate_Validation_Architecture.png)
- Appendix: Rebate Claim Validation MVP1 Scope Overview (BRD)
- AI Governance Council approval records (TBD – confirm with AI Governance Council)

# 3. Test Objectives
- Validate all MVP1 functional requirements and user stories listed in the BRD.
- Demonstrate ≥95% accuracy of extracted tier terms on the golden agreements dataset (BRD acceptance).
- Demonstrate 100% calculation accuracy against analyst‑verified examples (BRD acceptance).
- Validate that only analyst‑confirmed terms are used in calculations.
- Validate security and access controls (Azure AD) and RBAC including approval rules (Finance Manager approval above USD 50,000 and analysts cannot approve own claims).
- Validate interfaces and end‑to‑end flows: upload → extraction → confirmation → calculation → claim worksheet export.
- Validate data quality and reconciliation of purchase data to GL totals and that Delta Lake purchase data assumptions (complete for last 24 months) are handled.
- Validate performance targets: single supplier-year calculation ≤ 2 minutes; month-end batch of 400 agreements ≤ 8 hours (exact BRD values).
- Validate availability target: 99% business hours (BRD value).
- Validate auditability: reproducible calculations with agreement version and data snapshot date.
- Validate AI governance controls required by AI Governance Council and controls against hallucination (test points defined; thresholds TBD – confirm with AI Governance Council).

Measurable targets (from BRD):
- Extraction accuracy on golden agreements: ≥95%
- Calculation accuracy: 100% against analyst-verified examples
- Single supplier-year calculation time: ≤ 2 minutes
- Month-end batch (400 agreements) total time: ≤ 8 hours
- Availability: 99% business hours

# 4. In Scope
- MVP1 features and modules (per BRD):
  - Upload of rebate agreements (PDF) and amendments (Agreement Service → Azure Blob Storage).
  - AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions using Azure Document Intelligence and Azure OpenAI (APIM → Azure Document Intelligence / Azure OpenAI).
  - Analyst confirmation step in UI; only confirmed terms persisted to Azure PostgreSQL and used in calculations (Agreement Service → Azure PostgreSQL).
  - Calculation Service retrieval of purchase data from Delta Lake (EUDM) via Databricks SQL (Calculation Service → Delta Lake EUDM/IAP (Databricks SQL) | HTTPS/443 OAuth 2.0) to compute eligible spend, tier reached and earned rebate with both retroactive and incremental logic as specified.
  - Claim worksheet with supporting purchase lines, export to Excel, and variance to accrual (Calculation Service → Azure PostgreSQL results; export functionality).
  - Month‑end batch processing via Azure Function (Batch Scheduler) to run calculations for 400 agreements (Azure Function -> Agreement Service).
- NFRs and quality attributes in scope:
  - Availability: 99% business hours
  - Security: Azure AD authentication and authorization; agreements and spend data restricted/confidential per BRD
  - Performance: single calculation ≤ 2 minutes; month-end batch ≤ 8 hours
  - Auditability: reproducible calculations with agreement version and data snapshot date
- Data sources in scope (from BRD):
  - Rebate agreements — Source: Upload; Frequency: Ad-hoc; Owner: Supplier Programs; Security: Restricted
  - Purchase data — Source: Delta Lake (EUDM); Frequency: Daily; Owner: Finance Data; Security: Confidential
  - Product line mapping — Source: Configuration; Frequency: Monthly; Owner: Program Admin; Security: Internal
  - Calculations (tool output) — Source: Tool output; Frequency: Per run; Owner: Supplier Programs; Security: Confidential

# 5. Out of Scope
- All MVP2 items (deferred):
  - Supplier portal submission
  - Dispute tracking
  - Accrual posting to finance
  - Amendment comparison
- Other explicit exclusions from BRD:
  - Customer rebates (sell-side)
  - Price protection claims
  - Supplier payment collection

# 6. Assumptions and Dependencies
- Test assumptions (from BRD and architecture):
  - Delta Lake purchase data is complete for the last 24 months.
  - Agreements are mostly digital PDFs.
  - Non-production environment(s) will mirror the architecture boundaries described (Non-production Subscription, Azure AI Landing Zone, Shared Services Subscription).
- Dependencies:
  - Data platform team for Databricks/Databricks SQL access and Delta Lake snapshots (Dependency owner: Data platform team).
  - Supplier Programs SMEs for golden dataset and analyst‑verified calculation examples (Dependency owner: Supplier Programs).
  - AI Governance Council for controls and approval of AI usage.
  - Architecture/Platform team for Azure AD, App Gateway, APIM and connectivity.
- Items requiring clarification / confirmation:
  - Confidence score thresholds for extraction and any auto‑accept rules: TBD – confirm with Supplier Programs / AI Governance Council
  - Specific environment names, service endpoints and credentials for non-production: TBD – confirm with Architecture/Platform owner
  - Test execution schedule and test tools for performance/load/automation/defect tracking: TBD – confirm with QA Lead and Program Admin
  - The story note "to be validated with the backend architects": validation required as dependency before finalizing some integration tests.

# 7. Test Strategy
- Approach:
  - Risk‑based test planning focusing on AI extraction accuracy, calculation correctness, RBAC/approval workflow, data reconciliation and performance.
  - Progressive testing: component/unit where available, integration, system, performance and UAT.
  - Use golden datasets (agreements + analyst-verified calculation examples) for extraction and calculation acceptance.
  - Human‑in‑the‑loop verification for all AI extracted terms (analyst confirmation step to be exercised in tests).
- Test levels:
  - Unit / Component testing (development responsibility; verify Agreement Service, Calculation Service functions)
  - Integration testing (APIs: Web UI ↔ Agreement Service ↔ Blob Storage ↔ APIM ↔ Azure AI; Calculation Service ↔ Delta Lake; Azure AD SSO flows)
  - System testing (end‑to‑end flows in Non‑production)
  - Performance/Load testing (single calculation and month‑end batch)
  - Security testing (authentication, authorization, data access controls)
  - Data quality testing (reconciliation to GL totals, mapping correctness)
  - AI/Responsible AI testing (extraction accuracy, hallucination controls, human confirmation paths)
  - User Acceptance Testing (UAT) with Rebate Analysts and Finance Managers
- Test techniques:
  - Black‑box functional test cases driven from user stories and functional requirements
  - Data‑driven testing with representative purchase datasets and golden agreements
  - Boundary and negative testing for tier thresholds and rate application (e.g., threshold exactly at USD amounts)
  - Regression test suite to be built and run for each release
  - Automated checks where feasible (automation tool: TBD – confirm with QA Lead)
  - Exploratory testing for complex agreement language scenarios
- Tools and infrastructure:
  - Test tools and automation frameworks: TBD – confirm with QA Lead
  - Defect tracking tool: TBD – confirm with QA Lead

# 8. Functional Test Coverage
For each MVP1 functional requirement and user story from the BRD, the plan below states what will be verified.

- Upload of agreement PDFs and amendments (Agreement Service → Blob Storage)
  - Verify UI allows upload of PDF agreements and amendments.
  - Verify files are stored in Azure Blob Storage and metadata recorded.
  - Verify non‑PDF or corrupted files are rejected with clear error messages.
  - Verify security: only authenticated users (Azure AD) can upload.

- AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions (APIM → Azure Document Intelligence / Azure OpenAI)
  - Verify extraction returns: supplier, period(s), tiers (threshold amounts and rates), retroactive vs incremental flag, eligible product lines, exclusions, and page references.
  - Verify extraction metadata (page references) match source PDF pages.
  - Verify extracted tier thresholds are ascending (per BRD quality checks).
  - Validate extraction accuracy vs golden agreements: achieve ≥95% accuracy on tier terms.
  - Validate responses for complex wording and ensure extraction outputs structured fields.
  - Validate that extracted results include confidence values from AI services where available (if not available, note and confirm with Architecture).

- Analyst confirmation step; only confirmed terms used
  - Verify UI presents extracted terms to Rebate Analyst with page references.
  - Verify Analyst can accept, edit and reject extracted fields.
  - Verify edited/confirmed terms are persisted to Azure PostgreSQL.
  - Verify calculations use only confirmed/edited terms from PostgreSQL.
  - Verify audit trail records who confirmed/edited and which agreement version was used.

- Calculation using purchase data from Delta Lake via Databricks SQL
  - Verify Calculation Service queries Delta Lake (Databricks SQL) using HTTPS/443 OAuth 2.0 and retrieves daily purchase data.
  - Verify product line mapping is applied (monthly configuration by Program Admin).
  - Verify eligible spend calculation per agreement (filters on eligible product lines and exclusions).
  - Verify tier logic:
    - Retroactive: rate applies to full spend when tier reached.
    - Incremental: rate applies to spend within each tier band.
  - Verify tier reached and earned rebate amounts computed correctly for representative cases including:
    - Spend below first tier
    - Spend exactly on threshold values (boundary)
    - Spend across multiple tiers
    - Retroactive vs incremental behavior
  - Validate calculation results against analyst‑verified examples (100% accuracy requirement).
  - Verify variance to accrual calculation and reporting.

- Claim worksheet and exports
  - Verify claim worksheet contains: agreement identifier, confirmed terms, period, supporting purchase lines, tier reached, earned amount, variance to accrual, agreement version, data snapshot date.
  - Verify export to Excel functionality and format.
  - Verify worksheet stores results in Azure PostgreSQL with per‑run metadata.

- Month‑end batch processing (Azure Function → Agreement Service)
  - Verify Azure Function can trigger month‑end batch via Agreement Service for multiple agreements.
  - Verify batch processes 400 agreements end‑to‑end and produces results for each.
  - Validate batch behavior for partial failures and retries (see reliability tests).

- Auditability and reproducibility
  - Verify each calculation run records agreement version and data snapshot date.
  - Verify a run can be reproduced using the recorded agreement version and data snapshot.

# 9. Roles, Permissions and Workflow Testing
- Roles to test (per BRD):
  - Rebate Analyst
  - Finance Manager
  - Program Admin
- Tests to perform:
  - Authentication via Azure AD (Entra ID) for each persona (Rebate Analysts, Finance Managers) — verify SSO via App Gateway.
  - RBAC tests:
    - Rebate Analysts: can upload agreements, view/confirm/edit extracted terms, run calculations and prepare claim worksheets.
    - Finance Manager: can review and approve claims above USD 50,000.
    - Program Admin: can maintain supplier mappings, product line mappings and calculation settings.
  - Segregation of duties:
    - Verify Analysts cannot approve their own claims.
    - Verify Finance Manager approval is required for claims above USD 50,000; test boundary cases at USD 50,000 exactly and just above.
  - Workflow tests:
    - End‑to‑end: upload → extraction → confirm → run calculation → generate worksheet → approval (if applicable).
    - Role switching scenarios: Analyst attempts to approve own claim (must be blocked).
    - Audit trail: record of actions and approvals captured in Azure PostgreSQL with user IDs.

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization:
  - Test Azure AD (Entra ID) SSO for all user types (Rebate Analysts, Finance Managers).
  - Test token lifetime, session behavior and unauthorized access attempts.
- Data protection and confidentiality:
  - Verify access control over agreements (Restricted), purchase data (Confidential), product line mapping (Internal) and calculations (Confidential).
  - Verify least privilege: only Program Admin can modify mappings; only Supplier Programs and Finance roles can view calculation outputs per BRD.
- Data at rest and in transit:
  - Verify uploads go to Azure Blob Storage over HTTPS/443; verify database connections are secured.
  - Verify Calculation Service → Delta Lake uses HTTPS/443 OAuth 2.0 as specified.
- Compliance & governance:
  - Confirm AI Governance Council approval exists and tests conform to any required controls (TBD – confirm with AI Governance Council).
  - Verify SOX relevance assessment (C2P) compliance requirements are met where applicable (TBD – confirm with Finance / C2P).
- Penetration and vulnerability testing:
  - Scope and scheduling: TBD – confirm with Security team.
  - Verify secrets (Key Vault) usage for service credentials (TBD – confirm with Platform/Architecture).

# 11. AI and Data Quality Validation
- Extraction accuracy:
  - Use golden agreements dataset from Supplier Programs SMEs to measure extraction accuracy for tier terms.
  - Acceptance target: ≥95% accuracy on extracted tier terms (BRD).
  - Define measurement method: compare structured extracted fields to golden truth; produce precision/recall metrics (detailed metric definitions: TBD – confirm with QA Lead).
- Confidence thresholds and auto‑accept rules:
  - Confidence score thresholds for accepting or flagging extracted fields: TBD – confirm with Supplier Programs / AI Governance Council.
  - Tests:
    - Verify that low‑confidence fields are flagged for mandatory analyst review.
    - Verify that even high‑confidence fields still require analyst confirmation (per BRD “must confirm”).
- Hallucination and Responsible AI controls:
  - Verify system does not invent terms not present in the PDF; sample tests for hallucination behaviors.
  - Verify page references are provided and correspond to source pages to mitigate hallucination.
  - Verify APIM and AI services integration paths per architecture; record request/response logs for AI service interactions.
  - Confirm AI Governance Council controls and reporting requirements are met (TBD – confirm).
- Data quality checks:
  - Verify agreement term completeness and tier thresholds ascending.
  - Verify purchase data reconciliation to GL totals.
  - Verify product line mapping monthly refresh applied correctly, and unmapped items are reported.
- Human‑in‑the‑loop validation:
  - Verify analyst confirmation UI enforces confirmation before calculation.
  - Verify edited terms persist with user audit metadata.
- Golden dataset and training/test split:
  - Golden dataset sourcing: Supplier Programs SMEs (External Dependencies).
  - Validate that test dataset covers complex agreement language scenarios (TBD – confirm coverage with Supplier Programs SMEs).

# 12. Performance Testing
- Targets (from BRD):
  - Single supplier-year calculation: ≤ 2 minutes
  - Month-end batch: 400 agreements within ≤ 8 hours
- Tests to execute:
  - Single calculation performance:
    - Measure end‑to‑end time: from calculation initiation to worksheet available.
    - Test with representative purchase data volumes for a supplier-year (use actual Delta Lake snapshot or representative subset).
  - Batch performance:
    - Run month‑end batch via Azure Function for 400 agreements and measure total elapsed time and resource utilization.
    - Validate concurrency, throttling and rate limits when calling Databricks SQL and AI services.
  - Scalability and stress:
    - Evaluate behavior when Delta Lake returns large result sets; verify Calculation Service memory/CPU behavior (tooling and resource quotas: TBD – confirm with Platform).
  - Performance monitoring:
    - Ensure Datadog / Azure Monitor metrics are collected for these runs (TBD – confirm with Platform support).
- Test data and environment:
  - Use Non‑production subscription environment as per architecture.
  - Use production‑representative data snapshots where available (TBD – confirm with Data platform team).

# 13. Reliability and Recovery Testing
- Availability target: 99% business hours (BRD).
- Tests:
  - Simulate intermittent failures for AI services (Document Intelligence / OpenAI) and verify retry and fallback behavior.
  - Simulate Databricks/Delta Lake transient errors and validate Calculation Service retry/backoff handling.
  - Simulate Agreement Service or PostgreSQL unavailability: verify batch scheduling handles partial failures, logs errors and resumes/retries.
  - Verify that partial batch failures do not corrupt persisted confirmed terms or previously successful calculation outputs.
  - Recovery tests:
    - Verify reproducibility of calculation using agreement version and data snapshot after service restart.
    - Verify recovery from failed batch: Azure Function restart and reprocessing logic.
- Monitoring and alerting:
  - Validate alerts are triggered on failures (Datadog / Azure Monitor integration: TBD – confirm with Platform).

# 14. Accessibility and Compatibility Testing
- Accessibility:
  - Verify basic accessibility considerations for Rebate Analysts and Finance Managers in Web UI (TBD – confirm accessibility standards to apply with Program Admin).
- Compatibility:
  - Verify Web UI functions over supported browsers/devices (specific browsers not provided in BRD) — browser matrix: TBD – confirm with Program Admin.

# 15. Logging, Monitoring and Audit Testing
- Logging and audit trails:
  - Verify every major action is logged: upload, extraction request/response, analyst confirmation edits, calculation runs, exports, approvals.
  - Verify logs contain user identity (Azure AD), timestamps, agreement version, data snapshot date and run identifiers.
  - Verify storage of audit trail in Azure PostgreSQL and/or log store per architecture (TBD – confirm persistent audit store with Architecture).
- Monitoring:
  - Verify key metrics are emitted: extraction errors, extraction accuracy (on test runs), calculation times, batch completion status, API error rates.
  - Verify alerting thresholds for failures and performance degradations (thresholds: TBD – confirm with Platform/Operations).
- Retention:
  - Log retention policy: TBD – confirm with Compliance / Architecture.

# 16. Test Environments and Test Data
- Test environments (per architecture):
  - Non-production Subscription environment containing Web UI, Agreement Service, Calculation Service, Azure Function (Batch Scheduler), Azure Blob Storage, Azure PostgreSQL and APIM.
  - Azure AI Landing Zone with APIM, Azure Document Intelligence and Azure OpenAI (non-production instances).
  - Shared Services Subscription (Azure AD, App Gateway).
  - Supporting services boundaries for Datadog, GitHub Actions, Key Vault, Azure Monitor.
- Environment readiness:
  - Confirm endpoints, service principals and OAuth 2.0 credentials for Databricks SQL: TBD – confirm with Data platform team.
  - Confirm AI service keys and APIM configuration: TBD – confirm with Architecture/AI team.
- Test data sets:
  - Golden agreements dataset from Supplier Programs SMEs for extraction accuracy testing.
  - Analyst‑verified calculation examples for verifying 100% calculation accuracy.
  - Delta Lake purchase data snapshots covering last 24 months (assumption from BRD) or representative subsets for performance tests (availability to be confirmed by Data platform team).
  - Product line mapping configuration (monthly snapshot).
  - Test data masking/anonymization requirements for confidential data: TBD – confirm with Data Owner (Finance Data).
- Test data management:
  - Maintain versioned snapshots of agreements, purchase data and mappings used for reproducibility.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:
  - Test environment deployed and accessible per architecture (Non‑production).
  - Azure AD test accounts for Rebate Analyst, Finance Manager and Program Admin available.
  - Golden agreements dataset and analyst‑verified calculation examples supplied by Supplier Programs SMEs.
  - Connectivity to Delta Lake (Databricks SQL) test endpoint and sample snapshots available.
  - APIM configured to reach Azure Document Intelligence and Azure OpenAI test instances.
- Suspension criteria:
  - Critical defects that block functional flows (e.g., inability to upload agreements, AI extraction API unavailable, calculation service unable to query Delta Lake) that cannot be mitigated in a timely manner.
  - Security breach or unresolved authorization issues preventing secure testing.
- Exit criteria:
  - Functional: All MVP1 functional test cases passed OR defects outstanding are only of low severity with approved risk acceptance.
  - AI extraction: Measured extraction accuracy ≥95% on golden dataset.
  - Calculation: 100% accuracy against analyst‑verified examples.
  - Performance: Single calculation and month‑end batch meet BRD targets or documented and accepted deviations.
  - Security: All critical/high security findings resolved or formally accepted by Security/Compliance.
  - Auditability: Reproducibility verified for sample runs.
  - UAT: Rebate Analysts and Finance Managers signed off on acceptance tests (TBD – confirm sign-off process).

# 18. Defect Management
- Defect severity definitions (QA standard):
  - Critical (P1): System unusable for primary flows (e.g., uploads fail, calculations incorrect for many records, data loss).
  - High (P2): Major functionality broken or incorrect (e.g., extraction missing key fields, approval enforcement fails).
  - Medium (P3): Functional issues with workarounds (e.g., UI formatting, export layout issues).
  - Low (P4): Cosmetic or minor issues.
- Defect tracking and triage:
  - Defect tracking tool: TBD – confirm with QA Lead.
  - Daily triage for P1/P2 defects with Architecture, Development and Business Owners until resolved.
  - SLAs for defect response/resolution to be agreed: TBD – confirm with QA Lead/Stakeholders.

# 19. Risks and Mitigations
- Risk: Complex agreement language leads to extraction errors.
  - Mitigation: Mandatory analyst confirmation; include complex cases in golden dataset; increase QA on extraction.
- Risk: Data lake gaps or incomplete purchase data.
  - Mitigation: Reconciliation checks to GL totals; escalate to Data platform team; document gaps and apply agreed handling.
- Risk: Retroactive vs incremental misread by AI.
  - Mitigation: Explicit field in extraction for retroactive vs incremental; dedicated test cases (per BRD risk register).
- Risk: AI service availability or unexpected outputs (hallucination).
  - Mitigation: Human confirmation required; logging of AI responses; AI Governance Council controls (confirm).
- Risk: RBAC misconfiguration allowing analysts to approve own claims.
  - Mitigation: Test segregation of duties; enforce checks in application logic and database-level constraints; audit logs.
- Risk: Performance target not met for month‑end batch.
  - Mitigation: Performance tuning, resource scaling, run pre‑production performance rehearsals.

# 20. Test Deliverables and Reporting
- Planned deliverables:
  - Test Plan (this document)
  - Test Cases and Test Scripts (functional, integration, AI QA, performance)
  - Test Data Catalog and snapshots used
  - Test Execution Logs and Results (test run reports)
  - Defect Reports and Triage Minutes
  - Performance Test Reports (single run and batch)
  - AI Extraction Accuracy Report against golden dataset
  - Test Summary and Sign‑off Report
- Reporting cadence:
  - Test execution status reports: TBD – confirm frequency with QA Lead and Business Owner
  - Immediate reporting for critical defects to stakeholders.

# 21. Traceability and Metrics
- Traceability:
  - A Requirement‑to‑Test matrix will be produced mapping each BRD MVP1 functional requirement and user story to test cases. (Actual matrix: TBD – confirm with QA Lead)
- Metrics / KPIs to collect:
  - Test coverage (% of requirements with test cases)
  - Test pass rate (per test run)
  - Number and severity of defects
  - Extraction accuracy (%) against golden dataset (target ≥95%)
  - Calculation accuracy (%) against analyst examples (target 100%)
  - Average and 95th percentile calculation time for single supplier-year (target ≤2 minutes)
  - Total time for month‑end batch of 400 agreements (target ≤8 hours)
  - Availability during business hours (target 99%)
  - Time to resolution for P1/P2 defects (targets: TBD – confirm with QA Lead)

# 22. Test Schedule
- High‑level milestones (from BRD timeline):
  - MVP1 development and testing window: Mar–Jun 2026 (BRD)
- Detailed test schedule: TBD – confirm with QA Lead and Program Manager
  - (To include: environment readiness, unit/component test completion, integration testing window, system testing, AI accuracy validation, performance testing, UAT and sign‑off.)

# 23. End-to-End Scenario
Representative E2E scenario to be executed in system testing and UAT:

- Scenario: Prepare and approve a claim for Supplier A for Year Y
  1. Rebate Analyst authenticates via Azure AD and uploads Supplier A agreement PDF (including amendment) via Web UI.
  2. Agreement Service stores PDF in Azure Blob Storage and invokes APIM -> Azure Document Intelligence and Azure OpenAI for extraction.
  3. System displays extracted terms (supplier, period, tiers with thresholds and rates, retroactive vs incremental flag, eligible product lines and page references) to Rebate Analyst.
  4. Rebate Analyst reviews, edits a tier threshold, and confirms terms. Confirmed terms persisted to Azure PostgreSQL with audit metadata.
  5. Rebate Analyst runs calculation for the period. Calculation Service queries Delta Lake (Databricks SQL) via HTTPS/443 OAuth 2.0, applies product line mapping and computes eligible spend, tier reached and earned rebate (retroactive/incremental logic exercised).
  6. Calculation results persisted to Azure PostgreSQL; claim worksheet generated with supporting purchase lines and variance to accrual.
  7. If earned rebate > USD 50,000, system flags for Finance Manager approval. Finance Manager authenticates and approves the claim (approval recorded).
  8. Export claim worksheet to Excel and verify file contents.
  9. Verify reproducibility by re-running calculation using recorded agreement version and data snapshot date and comparing outputs.
  10. Validate logs, audit trails and extraction accuracy for the run.
- Variants:
  - Batch mode: Azure Function triggers month‑end batch to process 400 agreements; validate throughput and partial failure handling.
  - Negative: AI extraction returns low confidence for a key tier field — verify system forces analyst edit/confirmation and logs low confidence.

# 24. Approvals
- Test Plan approval required from:
  - Supplier Programs Finance (Business Owner)
  - Architecture/Platform owner
  - QA Lead
  - AI Governance Council (for AI testing approach)
  - Finance Manager representative
- Approval records / signatures: TBD – confirm with Supplier Programs and Governance owners

--- 

Notes / Outstanding Items Requiring Confirmation
- Confidence score thresholds for AI extraction acceptance/auto‑flagging: TBD – confirm with Supplier Programs / AI Governance Council
- Test tools for automation, performance testing and defect tracking: TBD – confirm with QA Lead
- Environment endpoint details, credentials and non‑production service names: TBD – confirm with Architecture/Platform
- Golden dataset delivery schedule and coverage: TBD – confirm with Supplier Programs SMEs
- Specific monitoring/alert thresholds and log retention policies: TBD – confirm with Platform/Operations and Compliance

This test plan covers all MVP1 functional requirements, user stories, NFR targets, roles and permissions, integrations and data sources as specified in the BRD and Solution Architecture documents. Items explicitly listed as MVP2 or otherwise excluded in the BRD are documented in Out of Scope.