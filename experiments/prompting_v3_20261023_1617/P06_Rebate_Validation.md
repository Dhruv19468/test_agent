# 1. Document Control
- Title: QA Master Test Plan — Supplier Rebate Claim Validation (MVP1)  
- Version: 1.0  
- Application: Supplier Rebate Claim Validation  
- Prepared by: QA Lead, Quality Engineering  
- Reviewed by: Test Manager, Architecture and Business Owners (TBD – confirm with Supplier Programs Finance)  
- Audience: Business Owners (Supplier Programs Finance), Program Admin, Rebate Analysts, Finance Managers, Architects, Development and QA Teams  
- Purpose: Define the quality assurance approach to validate MVP1: agreement PDF ingestion and extraction, analyst confirmation of terms, calculation of earned rebates using Delta Lake purchase data via Databricks SQL, and production of claim worksheets with variance to accrual. This plan covers functional, non‑functional, AI/data quality, integration, security and auditability targets required by the BRD.

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation (Version 1.0, 17 Feb 2026)  
- Solution Architecture: P06_Rebate_Validation_Architecture.png (non-production)  

# 3. Test Objectives
- Verify extraction of supplier, period, tiers (threshold and rate), retroactive vs incremental indicator, eligible product lines and exclusions from uploaded agreement PDFs with page references. Target: ≥95% accuracy on golden agreements (BRD acceptance criterion).
- Verify analyst confirmation step prevents unconfirmed terms from being used.
- Verify calculation correctness: eligible spend, tier reached, earned rebate using Delta Lake data via Databricks SQL. Target: 100% calculation accuracy against analyst‑verified examples.
- Verify retroactive and incremental calculation behaviour: retroactive applies rate to full spend; incremental applies rate per tier band.
- Verify claim worksheet contents: supporting purchase lines, tier reached, earned rebate, export to Excel, and variance to accrual.
- Verify reproducibility: calculation reproducible with recorded agreement version and data snapshot date.
- Validate availability and performance NFRs: 99% availability during business hours (BRD quality attribute); calculation time targets: one supplier-year within 2 minutes and month‑end batch of 400 agreements within 8 hours.
- Validate RBAC and approval rule: Finance Manager approval required for claims above USD 50,000; analysts cannot approve their own claims (segregation of duties).
- Verify integrations and data flows: Agreement Service ↔ Blob Storage, Agreement Service ↔ APIM → Azure Document Intelligence / Azure OpenAI, Calculation Service ↔ Delta Lake via Databricks SQL, Web UI → Agreement/Calculation Services.
- Validate auditability: calculation provenance, agreement version, data snapshot date captured for every run.

# 4. In Scope
Functional (MVP1)
- Upload of agreement PDFs and amendments through Web UI (Agreement Service).
- AI extraction of: supplier, period, tiers (threshold, rate), retroactive vs incremental flag, eligible product lines and exclusions (APIM → Azure Document Intelligence, Azure OpenAI).
- Analyst confirmation step: only confirmed terms persisted to Azure PostgreSQL and used by Calculation Service.
- Calculation Service reads purchase data from Delta Lake (EUDM/IAP) via Databricks SQL (HTTPS/443 OAuth 2.0) to compute eligible spend, tier reached and earned rebate (retroactive and incremental modes).
- Claim worksheet generation: supporting purchase lines, tier reached, earned rebate, variance to accrual; export to Excel.
- Storage: agreements in Azure Blob Storage; confirmed terms and results in Azure PostgreSQL.
- Audit metadata capture: agreement version, extraction page references, confirmation timestamp, data snapshot date, calculation inputs and outputs.

Non‑Functional
- Availability: 99% business hours (BRD quality attribute).
- Performance: single supplier-year calculation ≤ 2 minutes; month-end batch (400 agreements) ≤ 8 hours.
- Security: Azure AD authentication, restricted access to agreements and spend data as per BRD.
- Auditability and reproducibility: record agreement and snapshot metadata.
- AI governance: follow AI Governance Council approvals (BRD).

# 5. Out of Scope
- MVP2 capabilities (explicitly out of scope for MVP1):
  - Supplier portal submission of claims (MVP2).
  - Dispute tracking (MVP2).
  - Accrual posting to Finance (MVP2).
  - Amendment comparison automation (MVP2).
- Customer rebates (sell‑side), price protection claims and supplier payment collection.

# 6. Assumptions and Dependencies
- Assumptions (from BRD):
  - Delta Lake purchase data is complete for the last 24 months.
  - Agreements are mostly digital PDFs.
  - Supplier Programs SMEs will provide golden labelled agreements for extraction accuracy validation.
- Dependencies:
  - Databricks/Databricks SQL warehouse access from Calculation Service (Data platform team).
  - APIM connectivity to Azure Document Intelligence and Azure OpenAI (architecture).
  - Azure AD for authentication and role assignment.
  - Blob Storage and Azure PostgreSQL availability in non‑production.
  - AI Governance Council approval (BRD lists as required).
- Test constraints:
  - Test environments must not contain unmasked bank or restricted identifiers; masked or synthetic data to be used (TBD – confirm masking approach with Supplier Programs).
- Items requiring confirmation:
  - Test automation toolchain and defect tracking tool: TBD – confirm with QA Lead / Program Admin.
  - Confidence threshold for automated acceptance of extracted terms (BRD mandates analyst confirmation; numeric confidence threshold is TBD – confirm with Program Admin).

# 7. Test Strategy
Approach
- Risk‑based testing prioritising extraction accuracy, calculation correctness and auditability.
- Mix of automated regression tests (API and calculation engine) and manual exploratory/UAT for complex legal language extraction and analyst confirmation flows.

Levels of testing
- Unit testing: developer-owned, especially calculation service logic for retroactive/incremental algorithms.
- Component testing: Agreement Service extraction flow, Calculation Service logic, integration with Databricks SQL, persistence to PostgreSQL.
- API & contract testing: Web UI ↔ Agreement Service, Web UI ↔ Calculation Service, Agreement Service ↔ APIM, Calculation Service ↔ Databricks SQL (schema, auth, error handling).
- Integration testing: end‑to‑end flows with APIM → Azure Document Intelligence / Azure OpenAI (use golden dataset and controlled AI endpoints), Calculation Service ↔ Delta Lake.
- System testing: full run from upload through confirmation and claim worksheet generation.
- Performance and load testing: single calculation and month‑end batch.
- UAT: Rebate Analysts and Finance Managers validate extraction, confirmation, calculations, worksheet usability and exports.

Techniques
- Requirements-based test design, equivalence partitioning and boundary value analysis for tier thresholds and monetary boundaries.
- Data-driven tests for calculation engine using labelled golden datasets.
- Exploratory testing for legal language variations and edge cases in agreements.
- Regression suite for calculation correctness and API contracts.

Tools and automation
- Test tooling and CI integration: TBD – confirm with QA Lead and DevOps.
- Test data management: golden datasets provided by Supplier Programs SMEs (BRD).

# 8. Functional Test Coverage
Cover every MVP1 functional requirement and user story:

Agreement upload and storage
- Upload scenarios: valid PDF, multi-page PDF, amendment upload, password-protected file, corrupted file, non‑PDF upload; verify clear error messages and no persisted partial terms on failure.
- Verify agreements are stored in Azure Blob Storage and metadata recorded.

AI extraction (Azure Document Intelligence & Azure OpenAI via APIM)
- Verify extraction of: supplier, period, tiers (threshold and rate), retroactive vs incremental indicator, eligible product lines, exclusions.
- Verify extracted fields include page references for each term (per user story).
- Golden dataset checks: measure extraction accuracy and precision; target ≥95% accuracy for tier terms (BRD acceptance criterion).
- Edge cases:
  - Tier thresholds listed out of order – verify system validates "tier thresholds ascending" (BRD quality check).
  - Multiple amendments with conflicting tiers – ensure extraction returns all candidates and page refs.
  - Negative or zero thresholds, decimals, currency presence (e.g. "USD 1,000,000" vs "1M") – ensure parsing.
- Malformed PDFs, scanned images – verify Document Intelligence processing and fallbacks.

Analyst confirmation
- Verify analyst review UI highlights extracted terms with page refs.
- Verify only confirmed terms are persisted to Azure PostgreSQL and only confirmed terms are used by Calculation Service.
- Verify ability to reject extraction and trigger manual correction workflow (UI behaviour and persistence).
- Verify audit metadata: who confirmed, timestamp and agreement version.

Calculation using Delta Lake (Databricks SQL)
- Verify Calculation Service queries Delta Lake via Databricks SQL (HTTPS/443 OAuth 2.0) and handles:
  - No purchase data found for period – report zero eligible spend.
  - Partial data and data gaps – produce reconciliation note and variance to accrual.
  - Multiple product line mappings – filter by eligible product lines as per confirmed terms.
- Calculation correctness tests (numeric examples derived from BRD user story):
  - Example tiers: 2% from USD 1,000,000; 3% from USD 2,000,000.
    - Retroactive example: Eligible spend = USD 1,500,000 → earned rebate = 3%? (confirm BRD semantics: BRD states "retroactive applies rate to full spend" — test should validate expected business rule). Test vectors:
      - Spend USD 1,500,000 with retroactive tier breakpoints at 1,000,000 (2%) and 2,000,000 (3%): for retroactive interpretation test expectations must be defined by Business; for QA, verify implementation matches configured mode. (TBD – confirm with Supplier Programs Finance whether retroactive uses highest tier rate for full spend or immediate tier.)
    - Incremental example: Spend USD 2,500,000 with incremental tiers:
      - Band 0–1,000,000 @ 2% → rebate = 1,000,000 * 2% = 20,000
      - Band 1,000,001–2,000,000 @ 3% → rebate = 1,000,000 * 3% = 30,000
      - Band 2,000,001–2,500,000 @ 3%? (depends on tiers) — construct exact band tests from supplier tiers provided in golden dataset.
  - For each example, verify calculation matches analyst-verified example (BRD acceptance: 100% calculation accuracy).
- Boundary tests:
  - Spend exactly at tier thresholds (e.g. exactly USD 1,000,000 and USD 2,000,000).
  - Very small spend values (zero spend).
  - Negative adjustments or returns.

Claim worksheet and export
- Verify worksheet contains: confirmed terms, supporting purchase lines (with IDs and amounts), eligible spend, tier reached, earned rebate, variance to accrual and calculation provenance (agreement version, confirmation timestamp, data snapshot date).
- Verify Excel export correctness and that exported file omits restricted fields as required.
- Verify sorting, filters and pagination in UI.

Auditability and reproducibility
- For each run, verify stored metadata: agreement version, confirmed terms version, data snapshot date, query used (Databricks SQL statement or identifier), Calculation Service version, timestamp and user who initiated calculation.
- Re-run tests with same snapshot date to verify reproducible outputs.

APIs and error handling
- Verify API contract behaviour for success and failure modes (e.g., Databricks SQL timeouts, APIM errors, Blob Storage unavailability) and that meaningful error messages are surfaced to the analyst.

# 9. Roles, Permissions and Workflow Testing
Roles per BRD: Rebate Analyst, Finance Manager, Program Admin.

Verify role capabilities and segregation of duties:
- Rebate Analyst:
  - Permitted: Upload agreements, review/examine extracted terms with page refs, confirm or reject terms, run calculations for a supplier period, view claim worksheets.
  - Restricted: Approve claims over USD 50,000, modify Program Admin settings.
  - Tests:
    - Analyst cannot approve/finalise claims above USD 50,000; action should be blocked in UI and API.
    - Analyst confirmation logged with user identity.
    - Analyst cannot change approval limits or product mapping.
- Finance Manager:
  - Permitted: Approve claims above USD 50,000 and review accrual variances.
  - Tests:
    - Finance Manager can access pending approvals > USD 50,000 and approve; approval audit recorded.
    - Approval enforces mandatory comment for approvals? (BRD does not mandate mandatory comment: TBD – confirm with Finance Manager if comment is required.)
- Program Admin:
  - Permitted: Maintain supplier mappings, product line mappings, calculation settings.
  - Restricted: Should not be able to approve claims (segregation of duties).
- Segregation tests:
  - Program Admin cannot approve claims.
  - Ensure an analyst cannot both confirm terms and approve a claim above USD 50,000; if same user has multiple roles, system should enforce separation (test user with multiple roles).
- Authentication and session tests:
  - Azure AD login, SSO flow via App Gateway, session timeout handling (TBD – confirm session timeout policy with Program Admin).

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization:
  - Verify Azure AD integration for all UI and API access paths (App Gateway → Web UI → Agreement/Calculation Services). Validate OAuth 2.0 flows per architecture.
  - Verify role-based access controls at UI and API layers for all roles.
- Data protection:
  - Verify storage and transport encryption for Blob Storage and Azure PostgreSQL (TBD – confirm encryption-at-rest configuration with Architecture Owner).
  - Verify agreement uploads and calculation outputs do not expose Restricted fields beyond assigned roles.
- Sensitive data handling:
  - Test masking of restricted data in UI and exports (BRD: agreements and spend data are Restricted/Confidential). Confirm masking requirements with Supplier Programs.
- Input validation and injection protection:
  - Test malicious PDF payloads, overly large files, and SQL‑like content in text fields; verify API sanitisation.
- Third‑party and AI governance:
  - Verify that AI Governance Council approvals are recorded and accessible (BRD requires Council approval).
  - Verify that APIM calls to Azure Document Intelligence and Azure OpenAI are authenticated and that keys/secrets are stored in Key Vault (TBD – confirm Key Vault usage with Architecture).
- SOX / audit controls:
  - Verify logs capture who confirmed terms, who ran calculations, who approved claims, and any configuration changes (BRD requires reproducible calculations and auditability).
- Penetration and security scanning:
  - Schedule SAST/DAST/pen test prior to release (TBD – confirm scope with Security Owner).

# 11. AI and Data Quality Validation
Extraction accuracy and validation
- Use golden labelled dataset of agreements provided by Supplier Programs SMEs (BRD). Measure:
  - Field-level extraction accuracy for tier terms (BRD target ≥95%).
  - Precision/recall for eligible product line extraction.
- Test set composition:
  - Representative set covering common clause wordings, multi‑page agreements, amendments, scanned PDFs and edge legal language.
- Analyst confirmation control:
  - Verify analyst confirmation is mandatory before terms are persisted and used.
  - Verify system records both raw extraction and confirmed terms with page refs.

Controls against hallucination and unintended modifications
- Validate Azure OpenAI outputs for term extraction do not invent thresholds or rates:
  - For each extracted numeric term, verify source page reference exists and value matches text on source page.
  - Test negative cases where model might infer missing tiers—ensure extraction returns "not found" rather than inferred value.
- Model and prompt management:
  - Verify model/version/prompt identifier is recorded per extraction run (BRD expects auditability).
  - Reprocessing tests: when model/prompt changes, verify reprocessed agreements record new model/prompt and prior runs are preserved for reproducibility.

Confidence thresholds and handling
- BRD mandates analyst confirmation but does not specify numeric confidence thresholds. Define test to:
  - Validate how the system displays extraction confidence scores (if present).
  - If numeric thresholds are required for automation decisions, obtain threshold from Program Admin (TBD – confirm with Program Admin). Until confirmed, all extractions must require analyst confirmation.

Data quality checks
- Verify "tier thresholds ascending" validation: system should flag if thresholds extracted are not strictly ascending.
- Verify reconciliation of purchase data to GL totals is reported if variance exceeds an acceptable tolerance (tolerance numeric not specified in BRD — TBD – confirm with Finance Manager).

# 12. Performance Testing
NFR targets from BRD must be validated.

Performance tests
- Single calculation performance:
  - Target: calculation for one supplier-year within 2 minutes. Test with representative supplier data (golden dataset).
- Month‑end batch:
  - Target: 400 agreements processed within 8 hours. Execute batch run via Azure Function (Batch Scheduler) → Agreement Service → Calculation Service with realistic Delta Lake data volumes.
- Concurrency and throughput:
  - Concurrent user load: multiple Rebate Analysts running calculations concurrently (TBD – confirm expected concurrent users with Program Admin).
- Databricks SQL latency scenarios:
  - Simulate Databricks response times and verify Calculation Service handles timeouts, retries and logs timings.
- Measurement:
  - Capture end‑to‑end timing from user action to claim worksheet readiness, and per‑component timings (AI extraction, confirmation persistence, Databricks query time, calculation processing).
- Performance failure criteria:
  - Any run exceeding targets must be triaged; root cause assigned and mitigated before release.

# 13. Reliability and Recovery Testing
Availability and resilience tests (per architecture)
- Verify system behaviour and data consistency for:
  - Agreement Service restart during upload or confirmation.
  - Calculation Service restart during calculation.
  - APIM or Azure Document Intelligence transient failures: ensure retries/backoff and meaningful user errors.
  - Databricks SQL unavailability: verify calculation fails gracefully and provides reconciliation guidance.
- Idempotency:
  - Re-run same calculation with same data snapshot date and ensure idempotent outputs.
- Recovery:
  - Data snapshot/restore tests for PostgreSQL and Blob Storage (TBD – confirm backup/retention policies with Architecture).
- Monitoring and alerting:
  - Confirm alerts fire on service outages or when batch windows exceed expected durations (TBD – confirm runbook owners).

# 14. Accessibility and Compatibility Testing
Accessibility
- Ensure Web UI meets enterprise accessibility expectations: keyboard navigation, screen reader labels for critical workflows (upload, confirm, run calculation, approve).
- Specific tests:
  - Keyboard-only workflows for confirmation and approval dialogs.
  - Screen reader readout of extraction fields and page references.
  - Contrast and zoom/reflow for key screens.

Browser compatibility
- Test Web UI on enterprise-supported browsers (TBD – confirm with Client/Enterprise Standards). If not specified, list as TBD – confirm with Program Admin.

# 15. Logging, Monitoring and Audit Testing
Logging and traceability
- Verify structured logs capture:
  - User identity (Azure AD), role, action (upload, confirm, run calculation, approve), agreement identifier, confirmed terms version, calculation inputs and outputs, data snapshot date, Calculation Service version, timestamps.
- Verify storage of audit trail in a tamper-evident location (TBD – confirm with Architecture/Compliance).
- Verify ability to export audit trail for a given claim run.

Monitoring and alerts
- Verify metrics and dashboards for:
  - Extraction success rate, extraction accuracy (golden set), calculation latency, batch progress (400 agreements), error rates to Databricks SQL, system availability.
- Verify alerting for:
  - Extraction model failures, Databricks connectivity failures, batch runs exceeding window, and audit-log ingestion failures.

Retention and compliance
- Confirm audit/log retention policy and exportability (TBD – confirm with Compliance/Program Admin).

# 16. Test Environments and Test Data
Environments
- Non‑production subscription environment as per architecture (Agreement Service, Calculation Service, Azure Function Batch Scheduler, APIM, Blob Storage, Azure PostgreSQL, Databricks SQL test endpoint).
- Environment access must be provisioned via Azure AD.
- Environment network boundaries per architecture (Shared Services Subscription, Non‑production Subscription, Azure AI Landing Zone).

Test data
- Golden dataset: labelled agreements (provided by Supplier Programs SMEs) covering typical and edge clause formats, amendments and scanned PDFs.
- Delta Lake test data: representative purchase data for the last 24 months, seeded in Databricks SQL warehouse for pilot suppliers (TBD – confirm with Data Platform team).
- Product line mapping test set (monthly config snapshots).
- Negative and boundary datasets:
  - Agreements with out-of-order tiers, missing tiers, conflicting amendments, zero spend, returns/negative adjustments.
  - Large volume datasets for month‑end batch (400 agreements).
- Security test data:
  - Masked/synthetic PII/Restricted data; confirm masking approach with Supplier Programs (TBD – confirm with Supplier Programs).
- Test data versioning:
  - Record and store dataset snapshot date/version used for each test run to support reproducibility (BRD acceptance: reproducible calculations with snapshot date).

# 17. Entry, Suspension and Exit Criteria
Entry criteria
- BRD approved and requirements baselined (BRD: Status Approved).
- Non‑production environment provisioned with Agreement Service, Calculation Service, APIM, Blob Storage, Azure PostgreSQL and Databricks SQL access.
- Golden labelled agreements and seeded Delta Lake test data for pilot suppliers available.
- AI Governance Council approval status for extraction models (BRD: required) — if not approved, document allowed test scope.
- Test roles and Azure AD accounts provisioned.

Suspension criteria
- Critical defects block major flows (extraction, confirmation persistence, calculation correctness).
- Databricks SQL or Blob Storage unavailability preventing validation of core scenarios.
- AI Governance Council denies use of required AI services in test environment.

Exit criteria
- Functional:
  - All critical-path test cases passed.
  - 100% calculation accuracy confirmed against analyst-verified examples for tested scenarios (BRD acceptance).
  - Analyst confirmation workflow validated and enforced.
- AI/data:
  - Extraction accuracy for tier terms ≥95% on golden dataset (BRD acceptance).
  - Reproducible calculations verified for sample runs with recorded snapshot dates.
- Non-functional:
  - Performance targets met: single calculation ≤ 2 minutes; month-end batch (400 agreements) ≤ 8 hours.
  - Availability validated to expected behaviour in test window (99% business hours objective).
- Security & audit:
  - RBAC validated; audit trail captures required metadata for sample runs.
- Defects:
  - No open Critical defects; High defects approved for deferred fix with business acceptance.
- UAT:
  - Rebate Analysts and Finance Manager sign‑off on UAT scenarios (TBD – confirm sign‑off owners and process with Supplier Programs).

# 18. Defect Management
Severity definitions (QA Lead authority)
- Critical: Calculation logic error that produces incorrect earned rebate or data corruption; or extraction/confirmation missing causing incorrect claim production. Example: retroactive/incremental calculation misapplied resulting in >0.5% monetary error for test vectors. Requires immediate fix.
- High: Core functionality blocked or major data inconsistency (e.g., Calculation Service cannot connect to Databricks SQL for all runs).
- Medium: Functional issues with workarounds (e.g., UI export formatting problem).
- Low: Cosmetic or non-functional minor issues.

Process
- Defects logged in defect tracking system: TBD – confirm selected tool with QA Lead.
- Each defect must include steps to reproduce, environment, expected vs actual, evidence (logs/screenshots), severity, owner and retest plan.
- Daily triage for Critical/High defects; weekly review for Medium/Low during test cycles.
- Release gating: no Critical defects open; High defects require documented business risk acceptance if unresolved.

# 19. Risks and Mitigations
- Complex agreement language (BRD risk): Mitigation — mandatory analyst confirmation; golden dataset and iterative model improvement.
- Delta Lake data gaps: Mitigation — reconciliation checks and variance reporting; require Data Platform team to seed test data.
- Misinterpretation of retroactive vs incremental semantics: Mitigation — explicit test cases and business validation with Supplier Programs SMEs; require clear configuration flags and UI labels.
- AI Governance Council approval delays: Mitigation — early engagement and fallback manual confirmation process for UAT.
- Performance at month‑end volume: Mitigation — performance testing with 400‑agreement batch and tuning of Calculation Service and Databricks queries.

# 20. Test Deliverables and Reporting
Deliverables
- Test plan (this document).
- Test cases and test scripts mapped to BRD requirements (TBD – test case repository location; confirm with QA Lead).
- Automation scripts for API/contract and calculation engine tests (TBD – confirm framework).
- Golden dataset and test data snapshots with versions.
- Test execution reports: daily/weekly status including passed/failed/blocked counts.
- Defect reports and triage notes.
- Performance test report (single calculation and month‑end batch).
- UAT sign‑off evidence from Rebate Analysts and Finance Manager.

Reporting cadence
- Weekly status to stakeholders including coverage, defects, extraction accuracy metrics, calculation accuracy, performance results and open risks/mitigations.

# 21. Traceability and Metrics
Traceability
- Map each BRD requirement, user story and acceptance criterion to at least one test case. Maintain Requirement-to-Test mapping in the test repository (TBD – confirm repository).

Metrics/KPIs to report
- Requirement coverage (% requirements with executed test cases).
- Test execution: planned / executed / passed / failed / blocked.
- Extraction accuracy (field-level) on golden dataset (target ≥95% for tier terms).
- Calculation accuracy (%) against analyst-verified examples (target 100%).
- Touchpoints: number of agreements processed in batch runs.
- Performance: median and percentile (p50/p95/p99) for single calculation and batch completion time.
- Defect metrics: open / closed by severity and aging.
- Audit completeness: % of runs with complete provenance metadata.

# 22. Test Schedule
- MVP1 timeline as per BRD: Mar–Jun 2026. Use BRD milestone as baseline.
- Proposed test phases (dates to be confirmed with Program Owners):
  - Test planning and environment setup — Mar 2026 (TBD – confirm exact dates).
  - Component & integration testing — Apr 2026 (TBD).
  - System testing & AI/data validation against golden dataset — May 2026 (TBD).
  - Performance and reliability testing (single calc and 400-agreement batch) — May 2026 (TBD).
  - UAT with Rebate Analysts and Finance Manager — Jun 2026 (TBD).
  - Final regression, defect closure and release readiness — Jun 2026 (TBD).
- Exact calendar schedule and resource assignments: TBD – confirm with QA Lead and Program Manager.

# 23. End-to-End Scenario
Representative E2E scenario (to be executed in system testing and UAT):

1. Rebate Analyst logs in via Azure AD SSO (App Gateway → Web UI).
2. Rebate Analyst uploads a multi‑page agreement PDF (including an amendment).
3. Agreement Service stores file in Azure Blob Storage and records metadata.
4. Agreement Service invokes APIM → Azure Document Intelligence and APIM → Azure OpenAI to extract supplier, period, tiers (thresholds and rates), retroactive vs incremental flag, eligible product lines and exclusions; extraction includes page references.
5. Rebate Analyst reviews extracted terms in UI. Analyst rejects one extracted tier and corrects it; confirms final terms. Confirmation persisted to Azure PostgreSQL with agreement version and timestamp.
6. Rebate Analyst runs calculation for specified supplier-year. Calculation Service queries Delta Lake (Databricks SQL via HTTPS/443 OAuth 2.0) for purchase data, filters by confirmed eligible product lines and computes eligible spend, tier reached and earned rebate per configured retroactive/incremental logic. Calculation Service records data snapshot date and calculation provenance.
7. Claim worksheet is produced with supporting purchase lines, tier reached, earned rebate and variance to accrual. Worksheet exported to Excel.
8. If claim amount > USD 50,000, system marks claim pending Finance Manager approval and blocks Analyst approval. Finance Manager logs in, reviews worksheet and approves; approval recorded in audit trail.
9. Verify audit records: agreement version, extraction model identifier, confirmation timestamp, data snapshot date, Calculation Service version and approval log. Re-run calculation using same snapshot date and confirm reproducible results.

# 24. Approvals
- Business Owner (Supplier Programs Finance): signature/approval required for test acceptance and UAT sign‑off (TBD – confirm signatory and process).
- Finance Manager: required sign‑off for claims > USD 50,000 during UAT.
- AI Governance Council: confirmation that models/prompts used in test environment have required approvals (BRD).
- QA Lead/Test Manager: sign‑off on test completion and release recommendation.

Notes and open items (actions required)
- Confirm defect tracking and test case repository locations and tools (TBD – confirm with QA Lead).
- Confirm session timeout, export masking rules, and whether mandatory comment is required on Finance Manager approval (TBD – confirm with Program Admin / Finance Manager).
- Confirm exact interpretation and business rule for retroactive calculation semantics (TBD – confirm with Supplier Programs Finance).
- Confirm encryption-at-rest and backup/retention policies for Blob Storage and PostgreSQL (TBD – confirm with Architecture/Platform Owners).