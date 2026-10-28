# 1. Document Control
- Title: QA Master Test Plan
- Version: 1.0
- Application: Supplier Rebate Claim Validation
- Prepared by: QA Lead, Quality Engineering
- Reviewed by: Test Manager
- Audience: Business Stakeholders (Supplier Programs Finance), Architects, Program Admin, Rebate Analysts, Finance Managers, Development Team and QA Team
- Purpose: Define the quality approach to validate Supplier Rebate Claim Validation MVP1: agreement PDF upload and AI extraction of tiers/rates/eligibility, analyst confirmation of extracted terms, calculation of earned rebates from Delta Lake purchase data via Databricks SQL, and production of claim worksheets (including supporting purchase lines, Excel export and variance to accrual). MVP2 items are out of scope for MVP1 unless explicitly approved.

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation (Version 1.0, 17 Feb 2026)
- Solution Architecture diagram (P06_Rebate_Validation_Architecture.png)

# 3. Test Objectives
- Verify AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental flag, eligible product lines and exclusions from uploaded agreement PDFs, with page references.
- Demonstrate analyst confirmation step: only confirmed terms are used in calculations.
- Validate calculation logic against Delta Lake purchase data accessed via Databricks SQL (HTTPS/443 OAuth 2.0):
  - Retroactive calculation applies the extracted rate to full spend for the period.
  - Incremental calculation applies rate per tier band.
- Meet quality targets and acceptance criteria:
  - Extraction accuracy for tier terms: ≥95% on golden agreements.
  - Calculation accuracy: 100% against analyst-verified examples.
  - Reproducibility: every calculation is reproducible with stored agreement version and data snapshot date.
- Validate performance and availability NFRs:
  - Calculation for one supplier-year: within 2 minutes.
  - Month-end batch of 400 agreements: within 8 hours.
  - Availability: 99% during business hours.
- Verify RBAC and approval controls: Finance Manager approval required for claims above USD 50,000; analysts cannot approve their own claims.
- Verify end-to-end traceability and auditability (agreement version, data snapshot date, calculation inputs/outputs).

# 4. In Scope
Functional (MVP1)
- Upload of agreement PDFs and amendments via Web UI to Agreement Service.
- AI extraction using APIM -> Azure Document Intelligence and APIM -> Azure OpenAI: supplier, period, tiers (threshold, rate), retroactive vs incremental, eligible product lines and exclusions, with page references.
- Analyst confirmation step via Agreement Service / Web UI; persisted confirmed terms in Azure PostgreSQL.
- Calculation Service retrieving purchase data from Delta Lake (EUDM/IAP) via Databricks SQL (HTTPS/443 OAuth 2.0) and producing calculation results persisted to Azure PostgreSQL.
- Claim worksheet generation including supporting purchase lines, export to Excel, and variance to accrual.
- Month-end batch scheduling via Azure Function (Batch Scheduler) -> Agreement Service.
- Authentication via Azure AD (Entra ID) and access through App Gateway (HTTPS/443, AD/SSO).
- Auditability: record agreement version and data snapshot date for each calculation.
- Error handling, retries and operational logging per architecture.

Non-functional
- Availability: 99% business hours (as stated).
- Performance: 2 minutes per supplier-year; 8 hours for 400 agreements batch; reproducibility and auditability.
- Security: Azure AD authentication; agreements and spend data restricted.
- Traceability: per-calculation recording of agreement version and data snapshot date.

# 5. Out of Scope
- MVP2 and explicitly excluded items from BRD:
  - Supplier portal submission (MVP2)
  - Dispute tracking (MVP2)
  - Accrual posting to finance (MVP2)
  - Amendment comparison (MVP2)
- Customer rebates (sell-side), price protection claims, supplier payment collection (BRD exclusions)

# 6. Assumptions and Dependencies
- Assumptions (from BRD)
  - Delta Lake purchase data is complete for the last 24 months.
  - Agreements are mostly digital PDFs (suitable for Document Intelligence).
  - Supplier Programs SMEs will provide a golden dataset of agreements for AI validation.
- Dependencies (must be available or mocked for testing)
  - Databricks SQL warehouse access to Delta Lake (EUDM/IAP) with HTTPS/443 OAuth 2.0 – dependency: Data platform team for Databricks access.
  - APIM, Azure Document Intelligence and Azure OpenAI in the Azure AI Landing Zone for extraction flows.
  - Azure Blob Storage for agreement files.
  - Azure PostgreSQL for persisted confirmed terms and results.
  - Azure AD for authentication and role assignment.
  - Azure Function (Batch Scheduler) for month-end batch runs.
  - AI Governance Council approval for model/use (BRD requirement).
- If any dependency is not available in test environments, use: TBD – confirm with Data platform team or Supplier Programs Finance (as appropriate).

# 7. Test Strategy
Levels of testing
- Unit tests (developer): extraction mappers, calculation logic (retroactive/incremental), Databricks SQL queries. Target coverage: TBD – confirm with QA Lead.
- Component tests: Agreement Service, Calculation Service, APIM extraction flows, Web UI components.
- API and contract tests: Web UI -> Agreement Service, Calculation Service -> Delta Lake (Databricks SQL), Agreement Service -> APIM, Agreement Service -> Blob Storage, Agreement Service -> PostgreSQL, Calculation Service -> PostgreSQL. Validate HTTPS/443, OAuth 2.0 and Managed Identity where applicable.
- Integration tests: full dataflow from upload -> extraction -> confirmation -> calculation -> worksheet export.
- System tests: end-to-end MVP1 scenarios including batch month-end runs.
- UAT: Rebate Analysts and Finance Managers validate extraction confirmation, calculation correctness, worksheets and approval flow.

Test types and techniques
- Requirements-based testing, equivalence partitioning, boundary value analysis, negative testing, data-driven tests, regression suites, exploratory testing and risk-based prioritisation.
- Golden-dataset-driven AI validation and continuous precision/recall tracking for extraction.
- Reproducibility verification by re-running calculations against stored snapshots.

Test data strategy
- Golden agreements (labelled) across representative suppliers and complex language patterns.
- Purchase data from Delta Lake for the same period; synthetic or masked production-like data if required (TBD – confirm with Supplier Programs).
- Edge-case agreements: missing tiers, non-ascending thresholds, overlapping tiers, mixed retroactive/incremental clauses, multiple eligible product lines, exclusions.
- Month-end scale dataset representing 400 agreements.

Environment strategy
- Isolated test environments per BRD architecture: Non-production Subscription with Web UI, Agreement Service, Calculation Service; APIM and AI services in Azure AI Landing Zone; supporting services as per architecture.
- If any enterprise system cannot be reached, use contract mocks (TBD – confirm with Data platform team).

# 8. Functional Test Coverage
For each MVP1 functional requirement and user story, the following will be verified.

Upload of agreement PDFs
- Valid: single- and multi-page PDFs, amended PDFs, PDFs with standard fonts, PDFs with scanned images (if BRD assumption of mostly digital handled), PDFs containing example tier text "2% from USD 1M, 3% from USD 2M" (user story example).
- Invalid: corrupt PDFs, encrypted/password-protected PDFs, unsupported file types — check clear error messages and no partial persisted confirmed terms.
- Large file sizes and timeouts: test failure modes and retries (retry policy TBD – confirm with owner).

AI extraction of terms (APIM -> Azure Document Intelligence / Azure OpenAI)
- Extract fields: supplier, period, tiers (threshold and rate), retroactive vs incremental flag, eligible product lines and exclusions, with page reference for each extracted field.
- Accuracy target: ≥95% for tier terms on golden agreements (BRD acceptance criterion).
- Tests:
  - Positive: well-formed tier language (e.g., "2% from USD 1,000,000; 3% from USD 2,000,000") — verify thresholds and rates parsed correctly and page references present.
  - Boundary and ambiguity: tiers stated using words ("one million") or currency symbols with commas/decimals; verify parsing and normalization.
  - Negative: contradictory language, missing tiers, non-ascending thresholds — extraction should flag "incomplete" or "requires analyst confirmation"; quality check ensures "tier thresholds ascending".
  - Retroactive vs incremental: detect explicit "retroactive" wording and "incremental"/"per tier" wording; where ambiguous, extraction must mark for analyst confirmation.
  - Eligible product lines: multi-line lists, ranges, SKU codes vs text descriptions; verify product line mapping input to Program Admin mapping process.

Analyst confirmation step
- Verify that extracted terms appear with page references in the Web UI and require an explicit confirmation action before being persisted to Azure PostgreSQL and used in calculations.
- Confirm that unconfirmed extractions cannot be used in calculations (attempt to run calculation on unconfirmed terms must fail with clear error).
- Verify audit trail of who confirmed terms and timestamp stored.

Calculation Service (Delta Lake via Databricks SQL)
- Validate both calculation modes using persisted confirmed terms:
  - Retroactive example test (worked numeric example derived from BRD user story):
    - Given tiers: 2% from USD 1,000,000; 3% from USD 2,000,000 and total eligible spend = USD 1,500,000:
      - Retroactive: entire spend gets the rate of the tier reached. Tier reached = 2% tier (since spend >= 1,000,000 but <2,000,000). Expected rebate = 1,500,000 * 2% = USD 30,000.
  - Incremental example test:
    - Same tiers and spend = USD 1,500,000:
      - Incremental: apply 2% on first USD 1,000,000 = USD 20,000; apply 3% on next USD 500,000 = USD 15,000; expected rebate = USD 35,000.
- Calculation accuracy target: 100% vs analyst-verified examples (BRD acceptance criterion). Implement multiple worked examples and assert exact numeric equality.
- Edge cases:
  - Spend exactly at threshold boundaries (e.g., USD 1,000,000 and USD 2,000,000) — verify correct tier selection and calculation.
  - Zero, null or negative spend values — verify handling and meaningful errors.
  - Multiple eligible product lines: calculation must include only purchase lines mapped to eligible product lines.
  - Exclusions: excluded lines removed from eligible spend.
  - Currency handling: if agreements in different currencies, verify calculation inputs and outputs (BRD does not specify currency conversion; if required TBD – confirm with Supplier Programs Finance).
- Purchase data reconciliation: ensure eligible spend from Delta Lake reconciles to GL totals per BRD quality checks.

Claim worksheet, supporting lines and export
- Worksheet must show: confirmed tiers, calculation mode (retroactive/incremental), eligible spend, tier reached, earned rebate, supporting purchase lines (date, PO line, amount, product line), variance to accrual.
- Excel export: verify format, data completeness, and inclusion of agreement version and data snapshot date.
- Variance to accrual: test with example where accrual differs from calculated earned rebate; worksheet must compute variance = calculated rebate – accrual and display.

Month-end batch processing
- Azure Function (Batch Scheduler) -> Agreement Service: verify scheduled processing of up to 400 agreements within 8 hours (performance testing in Section 12).
- Test incremental and full re-run semantics and idempotency for repeated batch runs.

Quality checks (from BRD)
- Agreement term completeness validation: presence of supplier, period, at least one tier, calculation mode, eligible product lines.
- Tier thresholds ascending: detect non-ascending thresholds and flag for analyst review.
- Purchase data reconciliation to GL totals: test reconciliation reports for sample suppliers.

# 9. Roles, Permissions and Workflow Testing
Roles from BRD: Rebate Analyst, Finance Manager, Program Admin. Authentication via Azure AD; App Gateway enforces AD/SSO.

Tests
- Rebate Analyst:
  - Permitted: upload agreements, view extracted terms with page references, confirm terms, run calculations, view claim worksheet, export Excel.
  - Restricted: approve claims above USD 50,000 (BRD business rule).
  - Verify analysts cannot approve their own claims where an approval step exists (RBAC requirement: "analysts cannot approve own claims").
- Finance Manager:
  - Permitted: view claim worksheets, approve claims above USD 50,000.
  - Verify approval action required for claims > USD 50,000; system should block finalization without Finance Manager approval.
- Program Admin:
  - Permitted: maintain supplier mappings, product line mappings and calculation settings (as per BRD).
  - Restricted: not explicitly listed as approver in BRD; verify segregation of duties where Program Admin cannot act as approver for claims they configured (where applicable).
- Workflow tests:
  - Claim > USD 50,000: Rebate Analyst runs calculation producing earned rebate USD 75,000 — system must require Finance Manager approval before claim is finalized.
  - Approval attempt by analyst for claim above USD 50,000 must be blocked.
  - Approval by Finance Manager allowed and recorded with user, role and timestamp.

# 10. Security, Privacy and Compliance Testing
- Authentication/Authorization:
  - Azure AD (Entra ID) enforced via App Gateway (HTTPS/443, AD/SSO / OAuth 2.0) — test login, role assignment, session expiry and unauthorized access attempts.
- Data protection:
  - Agreements and purchase data marked Restricted/Confidential in BRD must only be accessible to permitted roles — verify access controls at UI and API levels.
  - Verify storage and transport security: Blob Storage and PostgreSQL access controls; network transport over HTTPS/443 as in architecture.
  - Key Vault usage for secrets per architecture: validate that services use Managed Identity where indicated (Agreement Service -> APIM uses Managed Identity).
- Injection and file-security:
  - Malicious PDF payloads, embedded scripts or malformed content must be detected and rejected or quarantined — test that these do not execute in processing pipelines.
- Compliance:
  - Verify that AI Governance Council approvals and C2P SOX assessments are recorded and available for audit (TBD – confirm with Supplier Programs Finance for evidence repository).
- Penetration and vulnerability scanning:
  - SAST/DAST and dependency scanning required before release — execution schedule TBD – confirm with Security team.

# 11. AI and Data Quality Validation
AI extraction targets and controls
- Target: ≥95% accuracy of extracted tier terms on golden agreements (BRD acceptance criterion).
- Validation dataset:
  - Golden dataset provided by Supplier Programs SMEs covering representative agreement language, complex clauses, amendments and edge cases.
- Metrics:
  - Precision/recall and F1 for tier threshold extraction, rate extraction, retroactive/incremental classification, eligible product line extraction.
  - Record model/prompt version, APIM call ID and extraction confidence per invoice/agreement.
- Human-in-the-loop controls:
  - Analyst confirmation is mandatory: system must prevent use of unconfirmed terms in calculations.
  - Provide extraction confidence indicators to analysts to prioritise review.
- Responsible AI guardrails:
  - Verify Azure OpenAI normalisation does not alter numeric values (thresholds, rates) — tests to assert numeric equality between extracted numeric values and source PDF text.
  - Verify logs capture model version and extraction timestamp for auditability.
  - AI Governance: ensure approval evidence exists before production use of models (BRD requirement).
- Hallucination and sanity checks:
  - Detect improbable extraction results (e.g., negative rates, thresholds decreasing with tiers) and require analyst confirmation.
  - If extraction produces thresholds that are not ascending, flag and block automatic calculation until resolved.

# 12. Performance Testing
Performance targets (from BRD)
- Single calculation: one supplier-year within 2 minutes.
- Batch: month-end run of 400 agreements within 8 hours.
- Availability: 99% business hours.

Tests
- Single-run benchmark:
  - Run calculations for representative supplier-year and measure end-to-end time from calculation request to persisted result; assert ≤ 2 minutes.
  - Include network latencies to Delta Lake via Databricks SQL (HTTPS/443 OAuth 2.0).
- Batch benchmark:
  - Execute a representative month-end batch of 400 agreements (use synthetic or masked production-like data) and measure total processing time; assert ≤ 8 hours.
  - Monitor throughput of Calculation Service and Databricks SQL concurrency.
- Load and stress:
  - Increase concurrent calculation requests to observe resource scaling and identify bottlenecks.
  - Measure failure rates, retries and queuing behaviour for Agreement Service and Calculation Service.
- Availability verification:
  - Simulate business-hours operation and verify monitoring alarms for availability, reporting against 99% target (measurement windows and tooling TBD – confirm with Infrastructure/Monitoring owner).

# 13. Reliability and Recovery Testing
- Resilience:
  - Simulate transient Databricks SQL errors, APIM timeouts or Azure Document Intelligence failures; verify retry logic, backoff and error handling.
- Idempotency:
  - Re-run the same batch or the same individual calculation request and verify idempotent results (no double-posting to results store).
- Partial failure and recovery:
  - Simulate service restart during a batch run; verify partial results persisted, batch resumes or can be safely re-run, and no data corruption.
- Data snapshot and reproducibility:
  - Recover a calculation using saved data snapshot date and agreement version; verify identical results to original run.
- Backup and restore:
  - Verify the ability to restore confirmed terms and calculation results from backups (backup cadence and retention TBD – confirm with Infrastructure owner).

# 14. Accessibility and Compatibility Testing
- Accessibility (enterprise expectation):
  - Web UI: keyboard navigation, screen-reader labels, focus order, colour contrast and error identification.
  - Test with standard enterprise assistive technologies (specific assistive tech versions TBD – confirm with Accessibility owner).
- Browser compatibility:
  - Verify UI in enterprise-supported browsers (Edge, Chrome, Firefox) — specific versions TBD – confirm with Program Admin.

# 15. Logging, Monitoring and Audit Testing
- Audit trail requirements (from BRD)
  - Record for each calculation: agreement version, data snapshot date, confirmed terms used, calculation inputs (eligible spend and supporting purchase lines), calculation outputs, user who confirmed terms, timestamps and approval actions.
- Tests:
  - Verify logs and records in Azure PostgreSQL for each calculation contain agreement version and data snapshot date and are queryable for repro steps.
  - Verify that APIM call IDs, model/prompt version and extraction confidence are persisted with extracted terms.
  - Verify alerts and monitoring metrics for batch completion, error rates, and service availability (SLA).
  - Verify retention and exportability of audit logs (retention schedule TBD – confirm with Compliance owner).
- Observability:
  - Ensure Datadog / Azure Monitor (as per architecture) capture metrics for Agreement Service, Calculation Service, APIM calls to AI services and Databricks SQL performance (specific dashboards/config TBD – confirm with Monitoring owner).

# 16. Test Environments and Test Data
Environments
- Non-production Subscription per architecture containing Web UI, Agreement Service, Calculation Service, Azure Function (Batch Scheduler), Blob Storage and PostgreSQL.
- Azure AI Landing Zone for APIM, Azure Document Intelligence and Azure OpenAI.
- Databricks SQL access to Delta Lake (EUDM/IAP) – if unavailable in test, use contract-mocked responses (TBD – confirm with Data platform team).
- Supporting services: Datadog, Key Vault, Azure Monitor, GitHub Actions as per architecture (availability TBD – confirm with Infrastructure owner).

Test data
- Golden dataset: labeled agreements from Supplier Programs SMEs (required for AI validation).
- Purchase data: representative Delta Lake extracts for target suppliers and periods; masked or synthetic copies for security if production data not permitted (TBD – confirm with Supplier Programs and Data platform).
- Edge-case agreements: missing tiers, non-ascending thresholds, mixed retroactive/incremental, multiple eligible product lines, excluded lines.
- Batch dataset: 400 agreements with corresponding purchase data for month-end performance tests.
- Record for each test execution: agreement version, dataset snapshot date, model/prompt version and environment details.

# 17. Entry, Suspension and Exit Criteria
Entry criteria
- BRD approved and requirements baselined (BRD status: Approved).
- Architecture and connections documented (P06_Rebate_Validation_Architecture.png).
- Test environments provisioned with Web UI, Agreement Service, Calculation Service, Blob Storage and PostgreSQL, APIM and AI services reachable or mocked.
- Databricks SQL access to Delta Lake (or approved mock).
- Golden dataset and representative purchase data available (TBD – confirm with Supplier Programs).
- Unit and component test evidence from development.

Suspension criteria
- Critical dependency unavailable for > 24 hours without mitigation plan (e.g., Databricks SQL unreachable) — suspend related tests until resolution.
- Discovery of critical data-sensitivity or compliance blocker preventing use of realistic test data (hold until masked/test dataset available).
- High-severity security vulnerability discovered with no mitigation.

Exit criteria (must be met before recommending release of MVP1)
- Functional: ≥95% extraction accuracy for tier terms on golden agreements (BRD acceptance criterion).
- Calculation: 100% calculation accuracy against analyst-verified examples.
- Reproducibility: All tested calculations record agreement version and data snapshot date and can be reproduced.
- Security: No open Critical security defects.
- Defects: No open Critical defects; High-severity defects resolved or have approved mitigations.
- Performance: Single supplier-year calculation ≤2 minutes and batch 400 agreements ≤8 hours in measured tests.
- UAT: Rebate Analysts and Finance Managers have validated representative UAT scenarios and signed off (UAT sign-off: TBD – confirm with Supplier Programs Finance).
- Monitoring: Basic monitoring and alerts in place for availability and batch completion.

# 18. Defect Management
- Defect tracking tool: TBD – confirm with QA Lead.
- Severity definitions (aligned to business impact):
  - Critical: Incorrect rebate calculation, data corruption, loss of auditability or major security breach. Example: retroactive/incremental misapplied leading to wrong rebate amounts across many suppliers.
  - High: Core workflow blocked for users, major export or reconciliation failures, or inability to access Delta Lake for calculation with no fallback.
  - Medium: Functionality works with workaround (e.g., minor UI issue preventing easy review).
  - Low: Cosmetic or minor usability issues.
- Triage and process:
  - Daily defect triage for Critical/High; weekly for Medium/Low or as agreed.
  - Defect record must include steps to reproduce, expected/actual, evidence (logs/screenshots), environment, build, owner and retest steps.

# 19. Risks and Mitigations
- Complex agreement language leading to extraction errors
  - Mitigation: mandatory analyst confirmation; golden dataset for model tuning; targeted training examples from SMEs.
- Databricks / Delta Lake access unavailable or incomplete
  - Mitigation: contract mocks for Databricks SQL; reconciliation checks and validation of completeness vs GL totals (BRD quality check).
- Retroactive vs incremental misinterpretation
  - Mitigation: explicit extraction of calculation mode field; unit tests and worked numeric examples; mandatory analyst review on ambiguous cases.
- Insufficient golden dataset
  - Mitigation: engage Supplier Programs SMEs early to supply broad examples.
- Scope creep into MVP2 features
  - Mitigation: enforce MVP1 scope and formal change approvals.

# 20. Test Deliverables and Reporting
Deliverables
- Test Plan (this document).
- Test cases and test scripts mapped to BRD requirements.
- AI validation reports (precision/recall for tier extraction, confidence distributions).
- Calculation verification workbook with worked examples and signed analyst verification.
- Performance test reports for single-run and batch runs.
- Defect reports and triage logs.
- UAT sign-off records from Rebate Analysts and Finance Managers.
- Auditability evidence: stored agreement versions and data snapshot metadata for sample calculations.

Reporting cadence
- Weekly test status: planned/executed/passed/failed cases, defect summary by severity, AI extraction metrics, performance run summaries, open risks and mitigations.
- UAT acceptance report at conclusion of UAT phase.

# 21. Traceability and Metrics
- Requirement-to-test traceability matrix: map every BRD MVP1 functional requirement and user story to at least one test case.
- Metrics to track:
  - Test case pass rate and coverage by requirement.
  - Extraction accuracy (tier terms) and AI precision/recall on golden dataset.
  - Calculation accuracy rate versus analyst-verified examples.
  - Reproducibility success rate (ability to reproduce calculations from stored snapshot).
  - Batch and single-run performance timings.
  - Defect ageing and severity distribution.
  - UAT completion and sign-off status.

# 22. Test Schedule
- Overall MVP1 window (from BRD): Mar–Jun 2026.
- High-level phases (dates TBD – confirm with Supplier Programs Finance and QA Lead):
  - Test planning and environment setup: TBD – confirm with QA Lead
  - Component & integration testing: TBD – confirm with QA Lead
  - AI validation (golden dataset): TBD – confirm with Supplier Programs SMEs
  - Performance & batch testing: TBD – confirm with QA/Infrastructure owners
  - UAT with Rebate Analysts & Finance Managers: TBD – confirm with Supplier Programs Finance
  - Sign-off and release decision: TBD – confirm with Product/Business owner

# 23. End-to-End Scenario
Representative E2E scenario (happy path)
- Rebate Analyst logs in via Azure AD -> App Gateway (HTTPS/443, AD/SSO).
- Rebate Analyst uploads agreement PDF to Web UI; Agreement Service stores file in Azure Blob Storage.
- Agreement Service calls APIM -> Azure Document Intelligence and APIM -> Azure OpenAI to extract supplier, period, tiers (thresholds and rates), retroactive/incremental flag, eligible product lines and exclusions; each extracted field includes a page reference.
- Analyst reviews extracted terms in Web UI and confirms terms; Agreement Service persists confirmed terms to Azure PostgreSQL with user and timestamp.
- Rebate Analyst initiates calculation for period; Calculation Service queries Delta Lake (EUDM/IAP) via Databricks SQL (HTTPS/443 OAuth 2.0) for purchase lines, applies product line mappings, computes eligible spend, determines tier reached and calculates rebate (retroactive or incremental as confirmed).
- Calculation Service persists results to Azure PostgreSQL, including agreement version and data snapshot date.
- System produces claim worksheet listing supporting purchase lines and variance to accrual, and allows Excel export.
- If earned rebate > USD 50,000, workflow requires Finance Manager approval; Finance Manager approves via Web UI and approval action is recorded with role and timestamp.
- Audit record demonstrates reproducible calculation (agreement version + data snapshot date) and all steps are traceable.

Alternate / edge scenario examples
- Extraction confidence low: Analyst notified to review; unconfirmed terms cannot be used.
- Non-ascending tier thresholds: extraction flagged and blocked for calculation until resolved.
- Month-end batch: Azure Function triggers Agreement Service to run calculations for 400 agreements; monitors performance and completion within 8 hours.

# 24. Approvals
Required sign-offs (from BRD approvals list and stakeholders)
- Supplier Programs Finance (Business Owner) – final UAT/production readiness sign-off
- AI Governance Council – model/use approval required before production use
- Finance (BIR) – acceptance for financial controls
- AI intake / Global Intake / C2P / WAB – as required by organisational process (evidence of approvals TBD – confirm with Supplier Programs Finance)
- QA Lead and Test Manager – test completion and exit criteria verification

Sign-off matrix and signatures: TBD – confirm with Supplier Programs Finance and QA Lead.