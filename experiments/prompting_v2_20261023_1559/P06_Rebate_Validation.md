# 1. Document Control
- Title: Master Test Plan – Supplier Rebate Claim Validation (MVP1)
- Version: 1.0
- Application: Supplier Rebate Claim Validation
- Prepared by: QA Lead – TBD – confirm with QA Lead
- Reviewed by: Supplier Programs Finance, Finance Data, Program Admin, Architecture (TBD – confirm reviewers)
- Audience: Business Owners (Supplier Programs Finance), Architects, QA team, Program Admin, Finance Manager
- Purpose: Define the test scope, approach, criteria and deliverables to validate MVP1 of the Supplier Rebate Claim Validation solution against the Business Requirement Specification (BRD v1.0, 17 Feb 2026) and the Solution Architecture (Non-production).

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation, Version 1.0, 17 Feb 2026 (BRD)
- Supplier Rebate Claim Validation - Solution Architecture (Non-production) (architecture diagram P06_Rebate_Validation_Architecture.png)
- Appendix: Rebate Claim Validation MVP1 Scope Overview (within BRD)

# 3. Test Objectives
- Prove functional correctness of all MVP1 features described in the BRD:
  - Agreement PDF upload, extraction of terms, analyst confirmation, calculation from Delta Lake, claim worksheet generation and Excel export.
- Verify business rules, thresholds and approvals exactly as stated:
  - Finance Manager approval for claims above USD 50,000; analysts cannot approve their own claims.
- Validate AI extraction and data quality targets:
  - ≥95% accuracy of extracted tier terms on golden agreements (BRD acceptance criteria).
  - 100% calculation accuracy against analyst-verified examples (BRD acceptance criteria).
- Validate non-functional requirements (NFRs) exactly as stated:
  - Availability: 99% business hours.
  - Performance: single supplier-year calculation ≤ 2 minutes; month-end batch of 400 agreements ≤ 8 hours.
  - Auditability: reproducible calculation with agreement version and data snapshot date.
- Verify interfaces, integrations, security and role-based access controls per architecture.
- Confirm assumptions, dependencies and mitigations are exercised where feasible.

Measurable targets (from BRD):
- Extraction accuracy ≥95% on golden dataset.
- Calculation accuracy 100% vs analyst-verified examples.
- Availability 99% business hours.
- Single calculation ≤ 2 minutes.
- Month-end batch (400 agreements) ≤ 8 hours.
- Approval enforcement: Finance Manager for claims > USD 50,000.

# 4. In Scope
(Only MVP1 items. Each item below will have tests defined in sections 7–13.)
- Upload of agreement PDFs and amendments (Blob Storage ingestion).
- AI extraction of:
  - supplier
  - period
  - tiers (threshold, rate)
  - retroactive vs incremental indicator
  - eligible product lines and exclusions
  - page references for extracted terms
  - Extraction performed via Azure Document Intelligence and Azure OpenAI (per BRD).
- Analyst confirmation step: extracted terms must be confirmed before use.
- Calculation using purchase data from Delta Lake (EUDM) via Databricks SQL:
  - eligible spend
  - tier reached
  - earned rebate (retroactive applies rate to full spend; incremental applies rate per tier band)
- Claim worksheet:
  - supporting purchase lines
  - tier reached and earned amount
  - variance to accrual
  - export to Excel
- Data quality checks:
  - Agreement term completeness
  - Tier thresholds ascending
  - Purchase data reconciliation to GL totals
- RBAC and approval workflow:
  - Rebate Analyst, Finance Manager, Program Admin permissions
  - Finance Manager approval for claims above USD 50,000
  - Analysts cannot approve their own claims
- Integrations and connections listed in the Solution Architecture (see section 8 for mappings).
- Auditability: reproduction of calculation with agreement version and data snapshot date.

# 5. Out of Scope
(Explicit MVP2 items and exclusions from BRD)
- Supplier portal submission (MVP2)
- Dispute tracking (MVP2)
- Accrual posting to finance (MVP2)
- Amendment comparison (MVP2)
- Customer rebates (sell-side)
- Price protection claims
- Supplier payment collection

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Delta Lake purchase data is complete for the last 24 months.
  - Agreements are mostly digital PDFs.
- Dependencies:
  - Databricks SQL warehouse access and Delta Lake data from Data platform team.
  - Golden dataset of agreements from Supplier Programs SMEs for extraction accuracy testing.
  - Azure AD for authentication (identity and access).
  - Azure Document Intelligence and Azure OpenAI services available in Non-production.
  - Blob Storage and Azure PostgreSQL available for agreements and confirmed terms/results.
  - APIM connectivity to AI services and managed identity configuration.
- Test constraints:
  - Solution architecture labeled Non-production; test environment provisioning may be subject to tenant/network boundaries shown in architecture.
- Items requiring confirmation (TBD):
  - Test environments (names, subscriptions, network access) – TBD – confirm with Architecture Owner.
  - Test tools for automation, load and performance (e.g., performance tool) – TBD – confirm with QA Lead.
  - Exact business hours time window for availability calculations and monitoring – TBD – confirm with Business Owner.
  - Monitoring/alerting configuration and thresholds (Datadog/Azure Monitor) – TBD – confirm with Architecture Owner.

# 7. Test Strategy
- Approach:
  - Risk-based test selection prioritizing BRD acceptance criteria, AI extraction accuracy, calculation accuracy, security, and performance targets.
  - Use a mix of manual exploratory tests for complex language extraction and automated regression tests for calculation logic and RBAC.
- Test levels:
  - Component/unit testing: Agreement Service extraction handlers, Calculation Service business logic (performed by devs / pipeline validation – coordinate with Dev).
  - Integration testing: AI services, APIM, Blob Storage, Azure PostgreSQL, Databricks SQL (Delta Lake).
  - System testing: end-to-end flows (upload -> confirm -> calculate -> worksheet -> export).
  - Performance/load testing: single calculation and month-end batch scenarios.
  - User Acceptance Testing (UAT): Rebate Analysts and Finance Managers validating workflows and outputs.
- Test types:
  - Functional, Integration, Regression, Performance, Availability, Security/Penetration, Data quality, AI extraction validation, Auditability and Reproducibility testing.
- Techniques:
  - Golden dataset comparison for AI extraction accuracy.
  - Deterministic test vectors for calculation logic (analytic examples verified by SMEs).
  - Synthetic load for Databricks queries mimicking daily and month-end volumes (specific load profile TBD).
  - Role-based test scripts for RBAC and segregation of duties.
  - Negative and boundary testing for tier thresholds, rates and retroactive vs incremental rules.

# 8. Functional Test Coverage
For each functional requirement and user story from the BRD, list what will be verified.

- Upload of agreement PDFs and amendments
  - Verify upload via Web UI (App Gateway -> Agreement Service -> Blob Storage).
  - Verify storage in Azure Blob Storage and metadata recorded in Azure PostgreSQL.
  - Verify multiple file types of PDFs (single/multi-page); validate page references returned by extraction.
  - Verify error handling for corrupt or non-PDF files.

- AI extraction of supplier, period, tiers, retroactive vs incremental, product lines and exclusions
  - Verify Azure Document Intelligence and Azure OpenAI are invoked through APIM (APIM -> Azure Document Intelligence / Azure OpenAI).
  - Validate extracted fields: supplier, period, each tier (threshold and rate), retroactive vs incremental flag, eligible product lines, exclusions, and page references.
  - Validate extracted tiers have ascending thresholds (tier thresholds ascending quality check).
  - Run extraction tests against golden agreements and measure accuracy (target ≥95% extraction accuracy).
  - Confirm handling of ambiguous/multi-language/complex clause examples (coverage for risk item).

- Analyst confirmation step
  - Verify analyst can view extracted terms with page references in the Web UI.
  - Verify analyst must explicitly confirm terms before calculation is allowed.
  - Verify confirmed terms are written to Azure PostgreSQL and used by Calculation Service.
  - Verify ability to reject and edit extracted terms (edits persist and are auditable).

- Calculation using purchase data from Delta Lake (Databricks SQL)
  - Verify Calculation Service queries Delta Lake via Databricks SQL with OAuth 2.0 (Calculation Service -> Delta Lake connection).
  - Verify eligible spend calculation adheres to product line mappings and exclusions.
  - Verify retroactive calculation: when retroactive flag, apply rate to full spend at tier reached.
  - Verify incremental calculation: apply rate per tier band.
  - Verify tier reached determination is correct for boundary conditions (exact threshold amounts).
  - Verify examples: 100% calculation accuracy vs analyst-verified examples (BRD acceptance criteria).
  - Verify variance to accrual calculation.

- Claim worksheet and export
  - Verify worksheet includes: supplier, period, confirmed terms version, data snapshot date, supporting purchase lines, tier reached, earned rebate, variance to accrual.
  - Verify Excel export works and contains same data (file format and fields).
  - Verify worksheet metadata stored in Azure PostgreSQL and audit references for reproduction.

- RBAC and approval workflow
  - Verify Rebate Analyst role can upload, view extraction, edit/confirm and run calculations.
  - Verify Program Admin role can maintain supplier and product line mappings and calculation settings.
  - Verify Finance Manager role can view and approve claims.
  - Verify approval enforcement: claims > USD 50,000 require Finance Manager approval before marking claim as "approved".
  - Verify analysts cannot approve their own claims (segregation of duties).
  - Verify audit trail of who performed confirmation, calculation and approval.

- Data quality checks and reconciliation
  - Verify agreement term completeness checks (no missing mandatory fields).
  - Verify tier thresholds ascending validation; flag errors when not ascending.
  - Verify purchase data reconciliation to GL totals (reconciliation report generation).
  - Verify owner and classification metadata captured for each data source.

- Integration and connectivity tests (per architecture connections)
  - Rebate Analysts -> App Gateway | HTTPS/443 AD/SSO – verify SSO and UI access.
  - Finance Managers -> App Gateway | HTTPS/443 AD/SSO – verify SSO and UI access.
  - Azure AD (Entra ID) -> App Gateway | HTTPS/443 AD/SSO / OAuth 2.0 – verify authentication and token issuance.
  - App Gateway -> Web UI | HTTPS/443 – verify TLS and routing.
  - Web UI -> Agreement Service | REST – validate API calls, error handling and timeouts.
  - Web UI -> Calculation Service | run calculation – validate request/response and user context propagation.
  - Azure Function (Batch Scheduler) -> Agreement Service | month-end batch – validate scheduled batch invocation and error handling.
  - Agreement Service -> Azure Blob Storage | agreements – verify storage and access controls.
  - Agreement Service -> Azure PostgreSQL | confirmed terms – verify persistence and schema constraints.
  - Calculation Service -> Azure PostgreSQL | results – verify results persistence and versioning.
  - Calculation Service -> Delta Lake EUDM/IAP (Databricks SQL) | HTTPS/443 OAuth 2.0 – verify query execution, performance, and credentials.
  - Agreement Service -> APIM | HTTPS/443 Managed Identity – verify API calls to APIM for AI services.
  - APIM -> Azure Document Intelligence | layout – validate request/response.
  - APIM -> Azure OpenAI | term extraction – validate request/response.
  - Verify managed identity and OAuth 2.0 authentication flows for service-to-service calls.

# 9. Roles, Permissions and Workflow Testing
- Roles to test:
  - Rebate Analyst: upload agreements, review/extract/edit/confirm terms, run calculations, prepare claim worksheet.
  - Finance Manager: view claim worksheets and approve claims above USD 50,000.
  - Program Admin: maintain supplier/product line mappings and calculation settings.
- Tests:
  - Verify role-based UI elements and API access matches privileges.
  - Verify Finance Manager approval enforced for claims > USD 50,000; claims ≤ USD 50,000 can be approved per existing rules (BRD only specifies approval above USD 50,000; default approval for others to be validated) – TBD – confirm with Business Owner.
  - Verify separation of duties: ensure Rebate Analyst cannot approve their own claims (attempted approval should be blocked and logged).
  - Verify audit trail: who uploaded, who confirmed terms, who ran calculation, who approved, with timestamps.
  - Verify Program Admin edits affect subsequent calculations only after confirmation (i.e., changes to mappings reflected in next run when applicable).

# 10. Security, Privacy and Compliance Testing
- Authentication and Authorization:
  - Verify Azure AD (Entra ID) SSO for Rebate Analysts and Finance Managers.
  - Verify role-based access controls enforced at API and UI layers.
- Data protection:
  - Verify agreements (restricted) and calculations (confidential) access restrictions as per BRD.
  - Verify Blob Storage and Azure PostgreSQL access controls, encryption at rest and in transit (validate TLS for HTTPS connections).
- Compliance:
  - Verify logs and artifacts necessary for SOX / C2P relevance are captured (BRD notes SOX relevance assessed via C2P) – confirm exact SOX controls – TBD – confirm with Compliance Owner.
  - Verify AI Governance Council approval artifacts exist (evidence capture) – TBD – confirm with AI Governance Council.
- Penetration / vulnerability:
  - Perform security scans of exposed endpoints and dependencies (APIM, Web UI, Agreement Service, Calculation Service).
- Privacy:
  - Verify data classification labels are applied and enforced for Confidential/Restricted data as listed in BRD.
- Secrets and credential handling:
  - Verify Key Vault usage for secrets per architecture (Key Vault present in supporting services) – validate that no secrets are stored in code or logs.

# 11. AI and Data Quality Validation
- Extraction accuracy validation:
  - Use golden dataset provided by Supplier Programs SMEs to measure extraction accuracy for tier terms and other fields.
  - Acceptance: ≥95% accuracy for extracted tier terms (BRD).
  - Track precision/recall and per-field accuracy (supplier, period, tiers, retroactive flag, product lines, page references).
- Human-in-the-loop controls:
  - Verify mandatory analyst confirmation step prevents unconfirmed terms from entering calculation pipeline.
  - Verify UI displays page references and confidence metadata (if available) from AI services – if confidence metadata is not provided by the AI pipeline, mark as TBD – confirm with AI Owner.
- Controls against hallucination and Responsible AI:
  - Verify that extraction results are traceable back to source page references.
  - Verify that disputed or low-confidence extractions require analyst attention and cannot be auto-applied.
  - Validate that the system logs raw AI responses and the APIM transaction for audit and model debugging.
  - AI Governance: verify documented approval from AI Governance Council is available for MVP1 AI usage (BRD states approval required) – obtain evidence (TBD – confirm with AI Governance Council).
  - If model hallucination controls or specific confidence thresholds are required by governance and are not specified, capture as action item: TBD – confirm confidence thresholds and remediation steps with AI Owner.
- Data quality for Delta Lake:
  - Verify daily refresh of purchase data (BRD frequency: Daily).
  - Verify reconciliation of purchase data to GL totals as a quality test.
  - Verify product line mapping refresh frequency (Monthly) and owner (Program Admin) enforced.
- Auditability and reproducibility:
  - Verify that calculation can be reproduced given agreement version and data snapshot date. Test by running calculation against a saved snapshot and comparing to stored calculation results.
- Acceptance criteria (from BRD):
  - ≥95% extraction accuracy on golden agreements.
  - 100% calculation accuracy vs analyst-verified examples.
  - Reproducible calculations with snapshot date.

# 12. Performance Testing
- Targets (from BRD):
  - Single supplier-year calculation ≤ 2 minutes.
  - Month-end batch of 400 agreements ≤ 8 hours.
- Tests to run:
  - Single-run performance: measure end-to-end time (upload-confirm-calc-export) for representative supplier-year cases with realistic Delta Lake query response times.
  - Month-end batch: run Azure Function (Batch Scheduler) invoking Agreement Service to trigger batch calculations for 400 agreements; measure total runtime and resource utilization.
  - Databricks/Delta Lake query performance: measure Databricks SQL query durations for heavy eligible spend queries; validate OAuth and network latencies.
  - Scalability: subject to environment availability, test incremental batch sizes up to 400 agreements to identify bottlenecks.
- Pass/fail:
  - Pass if measured values meet or are below BRD targets.
  - If not met, capture performance tuning actions, index/query optimizations, or environment sizing (TBD – confirm with Data Platform team).
- Tools and environment for performance tests: TBD – confirm with QA Lead and Data Platform Owner.

# 13. Reliability and Recovery Testing
- Availability target: 99% business hours (BRD).
  - Define business hours window – TBD – confirm with Business Owner.
  - Simulate component failures (Agreement Service, Calculation Service, APIM connectivity to AI services) and verify graceful failure, retries, and alerting.
- Batch scheduler resilience:
  - Simulate partial failures during month-end batch and validate retry semantics and idempotency.
- Data snapshot and reproducibility:
  - Verify ability to run calculation against stored data snapshot date (reproducible).
- Recovery tests:
  - Verify recovery scenarios from storage or DB failure: restoration of confirmed terms and calculation results (where recovery steps are documented) – if recovery processes are not documented, capture as action item – TBD – confirm with Architecture/Platform Owner.
- Monitoring and alerting:
  - Verify alerts configured for failures that would impact 99% availability SLA – confirm alert definitions – TBD – confirm with Monitoring Owner.

# 14. Accessibility and Compatibility Testing
- Accessibility:
  - Verify basic accessibility features for Web UI (keyboard navigation, labels) as required by corporate accessibility standards – confirm standard/level required – TBD – confirm with Accessibility Owner.
- Compatibility:
  - Verify Web UI works over supported browsers and versions used by Rebate Analysts and Finance Managers – supported browsers not specified in BRD; therefore: TBD – confirm with Program Admin/Users.
- Mobile: not in BRD; out of scope unless otherwise requested.

# 15. Logging, Monitoring and Audit Testing
- Verify that all user actions (upload, confirm, calculate, approve) are logged with user id, role, timestamp and action.
- Verify calculation logging includes agreement version, data snapshot date, input parameters, upstream AI response IDs, and calculation result ID.
- Verify APIM and AI service request/response logs retained for root-cause analysis (subject to retention policy – TBD – confirm with Compliance/Architecture).
- Verify monitoring integration points (Datadog, Azure Monitor) produce alerts for:
  - Failed scheduled batch runs
  - Databricks query failures or slow queries
  - Authentication/authorization failures
  - Errors from Azure Document Intelligence or Azure OpenAI
- Verify audit trail sufficient for SOX/C2P evidence (confirm exact evidence required – TBD – confirm with Compliance Owner).

# 16. Test Environments and Test Data
- Environments:
  - Non-production subscription per architecture (Solution labeled Non-production) to be used for system and integration tests.
  - Identity services via Azure AD (Shared Services Subscription).
  - Azure AI Landing Zone for APIM, Document Intelligence and OpenAI.
  - Supporting services: Key Vault, Datadog, Azure Monitor.
  - Exact environment names, IP ranges, and access procedures: TBD – confirm with Architecture Owner.
- Test data:
  - Golden agreements dataset for extraction accuracy – owner: Supplier Programs SMEs (BRD).
  - Purchase data snapshots from Delta Lake (EUDM) for last 24 months – owner: Finance Data (BRD).
  - Product line mapping configuration (monthly) – owner: Program Admin (BRD).
  - Synthetic negative and edge-case agreements to exercise ambiguous clauses and boundary tier thresholds.
  - Data privacy: Use masked/anonymized confidential data where production data is restricted; masking approach: TBD – confirm with Data Owner.
- Test data management:
  - Maintain versioned snapshots of purchase data used for reproducibility tests.
  - Store expected calculation examples and analyst-verified examples for regression.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria (for system/integration testing):
  - Test environment provisioned and accessible (TBD – confirm with Architecture Owner).
  - Azure Document Intelligence and Azure OpenAI available and reachable via APIM.
  - Golden dataset and analyst-verified calculation examples provided by Supplier Programs SMEs.
  - Databricks access and representative Delta Lake snapshots available.
  - Minimum set of APIs deployed: Agreement Service, Calculation Service, Web UI.
- Suspension criteria:
  - Critical defects in core flows (upload, confirm, calculation) that block further testing.
  - Environments unavailable for > 24 hours (or agreed SLA) – escalation to Architecture/Platform Owners.
- Exit criteria (to declare MVP1 tested / ready for UAT or release):
  - All high severity defects resolved or mitigated.
  - BRD acceptance criteria met:
    - ≥95% extraction accuracy on golden dataset.
    - 100% calculation accuracy vs analyst-verified examples.
    - Reproducible calculations with snapshot date.
  - Performance targets met for single-run and month-end batch or documented mitigation plan approved.
  - RBAC and approval enforcement verified (Finance Manager approval above USD 50,000; analyst segregation of duties).
  - Security and compliance checks completed and outstanding items accepted by Compliance.
  - Test deliverables produced (see section 20).

# 18. Defect Management
- Defect severity definitions:
  - Critical (P0): Core flow broken (upload/extraction/confirm/calc/export) or data corruption, security breach, or calculation inaccuracy violating 100% calculation accuracy acceptance criterion.
  - High (P1): Major functionality impaired, performance target missed for single-run that prevents normal operations, or RBAC enforcement failures for approval limits.
  - Medium (P2): Non-blocking functional issues, UI inconsistencies, minor extraction inaccuracies not exceeding acceptance thresholds.
  - Low (P3): Cosmetic issues, minor usability improvements.
- Tracking tool and process:
  - Tracking tool: TBD – confirm with QA Lead.
  - Triage cadence: Daily triage for Critical/High; weekly for Medium/Low (subject to agreement with stakeholders).
  - Defect workflow: New -> Triage -> Assigned -> Fixed -> Verified -> Closed.
- Escalation: Critical defects escalate to Architecture Owner and Business Owner immediately.

# 19. Risks and Mitigations
(Use BRD risk register and add test-specific risks)
- Complex agreement language may cause extraction errors
  - Mitigation: Mandatory analyst confirmation step; include complex examples in golden dataset; increase SME review coverage.
- Data lake gaps or incomplete purchase data
  - Mitigation: Reconciliation checks to GL totals; create test cases for partial data and ensure appropriate warnings/errors.
- Retroactive vs incremental misread by AI
  - Mitigation: Explicit extracted field for retroactive vs incremental and targeted tests; include examples of both modes.
- AI hallucination or incorrect extractions
  - Mitigation: Page-reference traceability, human confirmation, logging of raw AI outputs; require AI Governance Council approval.
- Performance bottlenecks for month-end batch
  - Mitigation: Performance testing at increasing scale; coordinate with Data Platform to tune Databricks queries and resources.
- Environment provisioning delays
  - Mitigation: Early coordination with Architecture and Data Platform teams; escalate per timeline.
- Dependencies on external teams (Data platform, Supplier Programs SMEs)
  - Mitigation: Early confirmation of data access and golden dataset; regular syncs.

# 20. Test Deliverables and Reporting
- Deliverables:
  - Test plan (this document)
  - Test cases and scripts for all functional and non-functional tests (repository) – TBD – confirm location with QA Lead
  - Test data sets (golden agreements, purchase snapshots)
  - Test execution reports and traceability matrix
  - Defect logs and triage reports
  - Performance test reports with metrics vs targets
  - Security and compliance test reports
  - UAT sign-off artifacts
- Reporting cadence:
  - Daily status updates during execution phases (Critical/High issues)
  - Weekly summary reports to Business Owner and Architecture Owner
  - Final test summary and exit report at completion

# 21. Traceability and Metrics
- Traceability:
  - Requirement-to-test mapping: every user story and functional requirement from BRD mapped to one or more test cases (traceability matrix to be produced).
  - Every acceptance criterion (≥95% extraction accuracy; 100% calculation accuracy; reproducible calculations) mapped to test cases.
- Metrics / KPIs to report:
  - Test coverage (% of functional requirements tested)
  - Pass/fail rates by test type (functional, integration, performance, security)
  - Defect counts by severity and status
  - Extraction accuracy metrics (per-field and overall) vs ≥95% target
  - Calculation accuracy (number of examples matched / total) vs 100% target
  - Performance metrics: median and 90th percentile times for single-run; total time for 400-agreement batch vs 8 hours
  - Availability measured during business hours vs 99% target
  - Mean time to detect and mean time to resolve critical defects

# 22. Test Schedule
- Timeline (per BRD):
  - MVP1 development and testing window: Mar–Jun 2026
- Test phases and milestones:
  - Test planning and environment setup: Mar 2026 (exact dates TBD – confirm with QA Lead and Architecture Owner)
  - Component and integration testing: Apr 2026
  - System testing and AI extraction validation (golden dataset): Apr–May 2026
  - Performance and reliability testing (single-run and batch): May 2026
  - Security and compliance testing: May 2026
  - UAT with Rebate Analysts and Finance Managers: Jun 2026
  - Final acceptance and test closure: Jun 2026
- Specific run dates, daily schedules and resource assignments: TBD – confirm with QA Lead and Business Owner.

# 23. End-to-End Scenario
Representative E2E scenario to validate core MVP1 flow:

Scenario: Rebate Analyst uploads an agreement and generates an approved claim worksheet requiring Finance Manager approval
- Pre-conditions:
  - Agreement PDF available (from golden dataset or ad-hoc).
  - Purchase data snapshot present in Delta Lake for the claim period.
  - Rebate Analyst and Finance Manager accounts exist in Azure AD.
- Steps:
  1. Rebate Analyst logs in via Azure AD SSO (Rebate Analysts -> App Gateway | HTTPS/443 AD/SSO).
  2. Upload agreement PDF via Web UI; Agreement Service stores file in Blob Storage and metadata in PostgreSQL.
  3. Agreement Service invokes APIM -> Azure Document Intelligence and APIM -> Azure OpenAI to extract terms.
  4. Web UI displays extracted terms with page references and confidence metadata (if available).
  5. Rebate Analyst reviews and confirms terms; confirmation persisted to Azure PostgreSQL.
  6. Rebate Analyst runs calculation for period; Calculation Service queries Delta Lake via Databricks SQL (HTTPS/443 OAuth 2.0) to retrieve purchase lines and product line mapping; calculation performed (retroactive/incremental as applicable).
  7. Calculation produces claim worksheet with supporting lines, tier reached, earned rebate and variance to accrual; result persisted in Azure PostgreSQL.
  8. Rebate Analyst exports worksheet to Excel; file contents verified against stored results.
  9. If earned rebate > USD 50,000, Finance Manager receives approval request; Finance Manager logs in and approves.
 10. Audit trail contains agreement version, data snapshot date, confirmed terms, calculation ID and approval record.
- Verification points:
  - Extraction accuracy and page reference mapping for tiers.
  - Calculations match analyst-verified examples (100% accuracy).
  - Approval enforcement for > USD 50,000.
  - Logs and artifacts present for reproducibility.
  - End-to-end time for the single supplier-year calculation ≤ 2 minutes.

# 24. Approvals
- Test Plan Reviewers / Approvers (per BRD stakeholders):
  - Supplier Programs Finance – Business Owner (approval required)
  - Architecture Owner (approval required)
  - QA Lead (author and approval)
  - Finance Manager (UAT and approval)
  - AI Governance Council (for AI controls and approvals) – evidence required
  - Compliance / C2P (SOX relevance) – evidence required
- Sign-off: sign-off names and dates to be captured after review (TBD – confirm with owners).