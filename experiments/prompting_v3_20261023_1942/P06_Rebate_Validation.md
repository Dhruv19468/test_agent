# 1. Document Control
- Title: QA Test Plan  
- Version: 1.0  
- Application: Supplier Rebate Claim Validation (MVP1)  
- Prepared by: TBD – confirm with QA Lead  
- Reviewed by: TBD – confirm with Test Manager  
- Audience: Supplier Programs Finance, Program Admin, Rebate Analysts, Finance Managers, Architects, Development and QA teams  
- Purpose: Define the quality approach to validate Supplier Rebate Claim Validation MVP1 from agreement ingestion and AI extraction through analyst confirmation, calculation against Delta Lake purchase data and claim worksheet production; ensure functional, data quality, AI, performance, security and audit requirements in the BRD are met.

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation (Version 1.0, 17 Feb 2026)  
- Solution Architecture: P06_Rebate_Validation_Architecture.png (as described in architecture document)

# 3. Test Objectives
- Verify accurate extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental flag, eligible product lines and exclusions from uploaded agreement PDFs, including page references. Target: ≥95% accuracy of extracted tier terms on golden agreements (BRD acceptance criteria).
- Verify Analyst confirmation step prevents unconfirmed terms from being used in calculations.
- Validate calculation logic against Delta Lake purchase data (Databricks SQL): eligible spend, tier reached, earned rebate for both retroactive and incremental rules. Target: 100% calculation accuracy against analyst-verified examples (BRD acceptance criteria).
- Validate reproducibility/auditability: every calculation must be reproducible with agreement version and data snapshot date (BRD quality attribute).
- Validate performance NFRs: one supplier-year calculation within 2 minutes; month-end batch of 400 agreements within 8 hours (BRD quality attribute).
- Validate RBAC and segregation of duties: Rebate Analyst, Finance Manager approval above USD 50,000, Program Admin responsibilities and restrictions.
- Validate integrations and data flows per architecture: Web UI, Agreement Service, Calculation Service, Azure Blob Storage, Azure PostgreSQL, Delta Lake (Databricks SQL), APIM -> Azure Document Intelligence and Azure OpenAI, Azure AD authentication, Azure Function (Batch Scheduler).
- Verify security, restricted access to agreements and purchase data, and AI Governance Council requirements (BRD).

# 4. In Scope
- MVP1 functional scope (per BRD):  
  - Upload of agreement PDFs and amendments via Web UI.  
  - AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental indicator, eligible product lines and exclusions using Azure Document Intelligence and Azure OpenAI (via APIM).  
  - Analyst confirmation UI and flow; only confirmed terms used for calculation.  
  - Calculations using purchase data from Delta Lake (EUDM/IAP) via Databricks SQL: eligible spend, tier reached, earned rebate (retroactive applies rate to full spend; incremental applies rate per tier band).  
  - Claim worksheet with supporting purchase lines, export to Excel, and variance to accrual.  
- NFRs in scope (per BRD):  
  - Availability: 99% business hours.  
  - Performance: 2 minutes per supplier-year calculation; month-end batch of 400 agreements within 8 hours.  
  - Auditability: reproducible calculations with agreement version and data snapshot date.  
- Data and integrations in scope: agreement uploads to Blob Storage, confirmed terms in Azure PostgreSQL, calculation results in Azure PostgreSQL, purchase data via Databricks SQL to Delta Lake (EUDM/IAP).  
- AI governance and confirmation controls: extraction quality measurement, analyst confirmation gating.

# 5. Out of Scope
- All BRD-listed MVP2 items and explicit exclusions:  
  - Supplier portal submission (MVP2)  
  - Dispute tracking (MVP2)  
  - Accrual posting to finance (MVP2)  
  - Amendment comparison (MVP2)  
- Other BRD exclusions: customer rebates (sell-side), price protection claims, supplier payment collection

# 6. Assumptions and Dependencies
- Test assumptions (from BRD):  
  - Delta Lake purchase data is complete for the last 24 months.  
  - Agreements are mostly digital PDFs (machine-readable).  
  - Rebate Analysts and Supplier Programs SMEs will provide a labelled golden dataset for extraction validation.  
- Dependencies (from BRD and architecture):  
  - Databricks/Delta Lake access provided by Data platform team for Databricks SQL warehouse (owner: Data platform team).  
  - APIM endpoints to Azure Document Intelligence and Azure OpenAI available in non-production (per architecture).  
  - Azure AD available for authentication and role assignment.  
  - Blob Storage and Azure PostgreSQL test instances available.  
  - Azure Function (Batch Scheduler) available for month-end batch runs.  
- Test constraints: environment and test data must not contain unmasked sensitive data (agreements and purchase data are Restricted/Confidential per BRD).  
- Unknowns requiring confirmation: confidence thresholds for extraction acceptance and any UI/browser compatibility requirements — "TBD – confirm with Program Admin / Product Owner".

# 7. Test Strategy
- Test levels: Unit (developer), Component, API/Contract, Integration, System, Regression and UAT with Rebate Analysts and Finance Managers.  
- Test types: functional, boundary-value, equivalence partitioning, negative/error handling, exploratory, data-driven, AI model/version regression, performance/load, reliability/recovery, security, auditability and reproducibility tests.  
- Technique highlights: create a golden labelled dataset of agreements across suppliers (including complex language and tier layouts), data-driven test harness for calculation permutations, regression suite for extraction and calculation logic, contract tests for Databricks SQL queries and APIM AI calls.  
- Automation approach and tools: TBD – confirm with QA Lead (do not invent tools). Automation focus: extraction validation metrics, calculation result verification, regression for calculation engine, API contract tests, and nightly batch validation.

# 8. Functional Test Coverage
For every MVP1 functional requirement and user story from the BRD, the following will be verified.

- Upload of agreement PDFs and amendments (Web UI / Agreement Service):  
  - Valid PDFs (single-page, multi-page), scanned PDFs (OCR cases), amended PDFs (multiple versions).  
  - Invalid files: corrupted, password-protected, unsupported formats — appropriate error messages, no persisted partial terms.  
  - Page-reference captured for every extracted term.

- AI extraction (Azure Document Intelligence + Azure OpenAI via APIM):  
  - Extracted fields: supplier, period, tiers (threshold, rate), retroactive vs incremental flag, eligible product lines, exclusions.  
  - Validate extracted numeric/monetary formats (USD amounts, thousands separators, decimals) and percent rates (e.g., "2%", "3%").  
  - Confirm page references for each extracted item.  
  - Edge cases: tier thresholds out of order, missing thresholds, overlapping tiers — extraction flags and analyst alerts.  
  - Example test cases derived from user story: verify extraction for a contract that states "2% from USD 1M, 3% from USD 2M" yields two tiers: threshold 1,000,000 -> 2%; threshold 2,000,000 -> 3%. Validate page refs.

- Analyst confirmation step (Agreement Service -> Azure PostgreSQL):  
  - Confirm/unconfirm behavior: only terms marked Confirmed are persisted to calculation input table.  
  - UI and API: prevent calculation runs when terms for the supplier-period are unconfirmed.  
  - Change/override handling: confirm that newly confirmed terms overwrite pending unconfirmed terms only after explicit confirmation. Audit trail of who confirmed and timestamp must be recorded.

- Calculation logic (Calculation Service using Delta Lake via Databricks SQL):  
  - Retroactive calculation test: for a supplier-year with total eligible spend USD 1,500,000 and tiers (2% from USD 1M, 3% from USD 2M), retroactive should apply highest achieved rate to full spend up to tier definitions — verify expected amount per BRD definitions. (Exact numeric expectations constructed from BRD example tiers.)  
  - Incremental calculation test: with the same tiers and spend USD 1,500,000, incremental should apply 2% to the band between USD 1M and USD 2M and lower bands as applicable — verify banded calculation correctness.  
  - Tier boundary tests: spend exactly at thresholds (e.g., USD 1,000,000 and USD 2,000,000).  
  - Product eligibility: include/exclude product lines based on product line mapping; verify excluded items are not counted.  
  - Multiple product lines and mixed eligibility.  
  - Negative/zero spend rows, nulls and missing GL reconciliation lines.  
  - Export to Excel: claim worksheet contains supporting purchase lines, tier reached, earned rebate and variance to accrual.

- Claim worksheet and variance to accrual:  
  - Validate worksheet fields: supplier, period, tiers, confirmed terms version, data snapshot date, purchase lines used, eligible spend, tier reached, earned rebate, accrual variance.  
  - Export format correctness, completeness and that exports do not leak other suppliers' confidential data.

- Data quality checks:  
  - Agreement term completeness (all expected fields populated).  
  - Tier threshold ordering ascending; system flags and prevents calculation if violated unless analyst confirms override.  
  - Reconciliation: aggregated purchase data used by calculation must reconcile to GL totals (where GL totals exist in test data); missing reconciliation items must be flagged.

- Integration and contract tests:  
  - APIM -> Azure Document Intelligence: correct request/response shape, error handling for timeouts, authentication.  
  - APIM -> Azure OpenAI: prompt invocation and response schema, error and rate-limiting handling.  
  - Calculation Service -> Delta Lake (Databricks SQL): query correctness, paging, authentication (OAuth 2.0 per architecture), timeouts and retry behavior.  
  - Agreement Service -> Blob Storage and Azure PostgreSQL: upload, retrieval, confirmed terms persistence.  
  - Azure Function (Batch Scheduler) month-end batch: scheduled run triggers Agreement Service and Calculation Service, handles failures and partial successes.

# 9. Roles, Permissions and Workflow Testing
- Roles from BRD to test: Rebate Analyst, Finance Manager, Program Admin.  
- Permission matrix to validate:  
  - Rebate Analyst: Upload agreements, view/extract/confirm terms, run calculations for supplier-periods, view claim worksheet, export to Excel, cannot approve claims above USD 50,000 (BRD).  
  - Finance Manager: Approve claims above USD 50,000, review accrual variances, view all calculation audit details.  
  - Program Admin: Maintain supplier mappings, product line mappings and calculation settings; cannot approve claims (segregation of duties).  
- Segregation of duties tests:  
  - Verify Rebate Analyst cannot approve claims above USD 50,000.  
  - Verify Program Admin cannot self-approve claims.  
  - Verify Finance Manager approval flow enforces approval above USD 50,000.  
  - Verify audit trail captures user, role, timestamp, action (confirm, run, approve).  
  - Verify session timeout, token expiry behavior, and role changes take effect immediately (or as per environment policy — TBD – confirm with Program Admin).

# 10. Security, Privacy and Compliance Testing
- Authentication & Authorization: Azure AD SSO via App Gateway — validate login, role assignment, token expiry, and access-denied responses.  
- Data access controls: agreements and purchase data are Restricted/Confidential — validate least-privilege access to Blob Storage and Azure PostgreSQL; verify Program Admin, Rebate Analyst, Finance Manager access levels.  
- Data masking and export controls: ensure exports and UI do not expose unrelated supplier confidential data. (BRD requires restricted data handling.)  
- Encryption: validate encryption in transit for HTTPS flows and encryption at rest for Blob Storage and PostgreSQL (TBD – confirm with Infrastructure Owner for exact encryption configurations).  
- AI governance and approvals: verify that AI Governance Council approvals are recorded / required for model/prompt changes (BRD notes AI Governance Council). Test that analyst confirmation is required before extracted terms are used.  
- SOX/C2P: verify auditability of approvals and that analysts cannot self-approve claims above USD 50,000. Verify audit trails for calculation inputs and outputs per BRD requirement "Every calculation reproducible with agreement version and data snapshot date."  
- Adversarial inputs: test malicious PDF content, injection-like language in agreements, oversized documents and ensure system handles safely (no code execution, safe logging).

# 11. AI and Data Quality Validation
- Gold dataset: obtain labelled golden agreements from Supplier Programs SMEs covering representative suppliers, tiers, retroactive/incremental patterns and complex language. Measure extraction accuracy against golden dataset. Target: ≥95% accuracy of extracted tier terms (BRD acceptance).  
- Extraction metrics: precision, recall and F1 for tier thresholds, rates, retroactive flag, product line extraction and exclusions. Track per-field and aggregate metrics.  
- Human-in-the-loop controls: verify that extracted terms are not used until explicitly confirmed by Rebate Analyst (UI/API tests, persistence validation).  
- Model/prompt/versioning: capture model and prompt version per extraction run in audit logs stored with the agreement and calculation record. Reprocessing behavior after model/prompt change: test re-run and versioned results. (If model versioning storage is not implemented, escalate as defect.)  
- Responsible AI checks: validate that Azure OpenAI normalisation does not alter numeric values (thresholds, rates) or interpretive flags incorrectly. Where normalisation suggests changes, require analyst confirmation.  
- Confidence thresholds: BRD does not specify numeric confidence thresholds — "TBD – confirm with Program Admin" for extraction confidence thresholds and how they influence analyst prioritisation.

# 12. Performance Testing
- Performance targets from BRD (to be verified by tests):  
  - One supplier-year calculation within 2 minutes. Validate for typical and worst-case complexity (many eligible product lines, many purchase rows).  
  - Month-end batch: 400 agreements processed within 8 hours via Azure Function (Batch Scheduler) invoking Agreement Service and Calculation Service. Validate batch parallelism, Databricks SQL throughput and any API throttling.  
- Test scenarios: single supplier-year run (measure end-to-end from confirmed terms to worksheet export), incremental runs after re-confirmation, month-end batch runs at intended scale (400 agreements).  
- Load and concurrency: TBD – confirm with Program Admin for expected concurrent user counts (Rebate Analysts running calculations concurrently). At minimum, test 1, 5 and 10 concurrent calculation requests and measure queueing/backpressure.  
- Monitoring: capture calculation time, Databricks query duration, API latencies and failure rates.

# 13. Reliability and Recovery Testing
- Availability NFR: 99% business hours (BRD). Tests: simulated component failure (e.g., Calculation Service restart), Databricks SQL transient failures and retry behavior, APIM timeouts and recovery, Blob Storage unavailability and recovery. Validate that partial failures do not produce incorrect persisted calculation results and that retries are idempotent.  
- Batch resilience: month-end batch partial failure handling, resume logic in Azure Function (Batch Scheduler) and alerts.  
- Data integrity after recovery: validate persisted confirmed terms, timestamped snapshots and calculation results remain consistent after recovery.  
- Backup/restore: TBD – confirm backup/restore responsibilities and SLAs with Infrastructure Owner.

# 14. Accessibility and Compatibility Testing
- BRD does not mandate accessibility targets; confirm with Program Admin whether accessibility standards apply: "TBD – confirm with Program Admin".  
- Browser compatibility: Web UI via App Gateway — confirm enterprise-supported browsers with Program Admin; until confirmed, test on latest Edge and Chrome in non-production.

# 15. Logging, Monitoring and Audit Testing
- Audit trail requirements (from BRD): every calculation reproducible with agreement version and data snapshot date. Tests must verify logs/audit capture: agreement upload timestamp and file version, extracted terms with page references and extraction model/prompt version, analyst confirmations (user, role, timestamp), Databricks snapshot date used, calculation inputs (purchase data snapshot identifier), calculation outputs, and claim worksheet export events.  
- Monitoring and alerts: validate metrics/alerts for failed extractions, failed calculations, batch failure, and extraction accuracy degradation (if automated). Confirm Datadog / Azure Monitor integration per architecture (TBD – confirm with Ops).  
- Log retention and access controls: TBD – confirm retention policy with Compliance Owner.

# 16. Test Environments and Test Data
- Environments required (per architecture): Non-production subscription containing Web UI, Agreement Service, Calculation Service, Azure Function (Batch Scheduler), Blob Storage, Azure PostgreSQL; APIM and Azure AI Landing Zone components available. Confirm environment labels and access: "TBD – confirm with Platform Owner".  
- Test data sets:  
  - Golden agreements (labelled) across representative suppliers and complex tiers (provided by Supplier Programs SMEs).  
  - Delta Lake purchase data seeded for the last 24 months for pilot suppliers (owner: Finance Data).  
  - Product line mapping configuration (monthly frequency; owner Program Admin).  
  - Negative test data: corrupted PDFs, scanned images with low OCR quality, agreements with missing tiers, contradictory tier wording.  
  - Boundary cases: spend exactly at USD 1,000,000 and USD 2,000,000 per BRD tier example; claim amounts at USD 50,000 approval threshold.  
- Data privacy: test data must be masked/synthetic; do not use unmasked production confidential data (BRD security requirement).  
- Test data management: versioned dataset and snapshot dates must be recorded for reproducibility.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria:  
  - BRD approved (confirmed).  
  - Test environments provisioned with connectivity to APIM, Blob Storage, Azure PostgreSQL and Databricks SQL (Delta Lake) or approved mocks.  
  - Golden dataset and purchase data for pilot suppliers available and seeded.  
  - Build deployed to test environment with unit test evidence from developers (TBD – confirm with Dev).  
- Suspension criteria: major infrastructure outage (Delta Lake unavailability for >4 hours during a scheduled test window), unresolved blocking security vulnerability, or missing critical test data required for calculation validation.  
- Exit criteria (must be met before recommending release of MVP1):  
  - ≥95% extraction accuracy for tier terms on the golden agreements (BRD acceptance).  
  - 100% calculation accuracy against analyst-verified examples (BRD acceptance).  
  - All critical-path test cases passed.  
  - No open Critical defects and no open High-severity security defects.  
  - Performance targets met: single supplier-year calculation ≤ 2 minutes and batch of 400 agreements ≤ 8 hours.  
  - Auditability validated: calculations reproducible with agreement version and data snapshot date.  
  - Rebate Analyst and Finance Manager UAT sign-off on representative scenarios.  
- If any exit criterion is not met, a documented risk/impact, mitigation plan and formal acceptance by Product and Supplier Programs Finance is required.

# 18. Defect Management
- Defect severities and definitions (project-level):  
  - Critical: incorrect calculation that materially misstates earned rebate (causing financial misstatement or regulatory exposure), data corruption or security breach. Example: calculation applies wrong tier rates resulting in >USD 50,000 error.  
  - High: core workflow broken or control failure (e.g., Analyst cannot confirm terms, Finance Manager approval flow fails for >USD 50,000).  
  - Medium: functionality degraded with workaround (e.g., export missing supporting purchase lines but can be reconstructed manually).  
  - Low: cosmetic or non-functional issues (UI layout, minor text).  
- Tracking tool: TBD – confirm with QA Lead (do not invent tools).  
- Triage process: daily triage during test execution, with Critical defects triaged immediately and owners assigned; High defects have remediation or mitigation plan within agreed SLA (TBD – confirm with Program Admin).

# 19. Risks and Mitigations
- Risk: Complex agreement language leads to extraction errors. Mitigation: mandatory analyst confirmation step, golden dataset, targeted custom extraction prompts and extra review cases. (BRD risk)  
- Risk: Data lake gaps for required 24-month window. Mitigation: reconciliation checks and fallback/marking of incomplete results; escalate to Data platform team. (BRD risk)  
- Risk: Retroactive vs incremental misinterpretation. Mitigation: explicit extracted field for retroactive vs incremental and dedicated test cases for both behaviors. (BRD risk)  
- Risk: AI model/prompt drift causing extraction accuracy degradation. Mitigation: model/prompt versioning, monitoring of extraction accuracy on golden set and roll-back capability. (derived from BRD AI governance references)

# 20. Test Deliverables and Reporting
- Test deliverables (to be produced): test plan (this document), test cases and mapping to BRD requirements, golden dataset and expected outputs, automated test scripts and execution reports (TBD – confirm automation scope), defect logs and triage notes, test summary and exit criteria evidence pack, UAT sign-off records.  
- Reporting cadence: weekly test status reports including planned/executed/passed/failed cases, defect metrics by severity and ageing, extraction accuracy metrics, calculation accuracy verification, performance run results, and risks/blockers. (Exact recipients and schedule: TBD – confirm with QA Lead / Product Owner)

# 21. Traceability and Metrics
- Traceability: every BRD requirement, user story and acceptance criterion mapped to test cases. Maintain a Requirements-to-Test mapping artifact (TBD – confirm with QA Lead for format/location).  
- Metrics to report: test coverage by requirement, extraction accuracy (per-field and aggregate), calculation accuracy (pass rate vs analyst-verified examples), number of confirmed vs unconfirmed extractions, touchless vs manual-confirmation rate (if measured), defect counts by severity, mean time to resolution for Critical/High defects, performance metrics (calc time per supplier-year, batch duration), availability during business hours (log-derived), and audit trail completeness.

# 22. Test Schedule
- High-level milestones (from BRD): MVP1: Mar–Jun 2026.  
- QA milestones (summary):  
  - Test planning & environment readiness: TBD – confirm with QA Lead and Platform Owner.  
  - Component & integration testing (Agreement Service, Calculation Service, APIM AI calls): TBD – align to development sprints.  
  - System testing (end-to-end): TBD – align to completion of integration work.  
  - Performance and batch testing: schedule month-end batch simulation window (TBD – confirm with Data platform team).  
  - UAT with Rebate Analysts and Finance Managers: TBD – coordinate with Supplier Programs schedule.  
  - Exit criteria verification and release readiness review: TBD – confirm with Product Owner.  
- Detailed dates and sprint alignments: TBD – confirm with Delivery Manager and Product Owner.

# 23. End-to-End Scenario
Representative E2E scenario to be executed and validated in system testing and UAT:
- Rebate Analyst authenticates via Azure AD and accesses Web UI through App Gateway.  
- Rebate Analyst uploads a supplier agreement PDF (multi-page) describing tiers "2% from USD 1M, 3% from USD 2M" and marking incremental vs retroactive language. Agreement Service stores the file in Blob Storage and creates a draft extraction record.  
- APIM invokes Azure Document Intelligence and Azure OpenAI; extracted supplier, period, two tiers, retroactive/incremental flag, eligible product lines and page references are returned and stored. Extraction model/prompt version and timestamp are recorded.  
- Rebate Analyst reviews and confirms the extracted terms in the UI (confirmation persisted to Azure PostgreSQL). Audit entry created with user, role and timestamp.  
- Calculation Service queries Delta Lake (Databricks SQL) for the supplier-period snapshot date, retrieves eligible purchase lines (product line mapping applied), computes earned rebate using both retroactive and incremental logic (per confirmed terms). Calculation inputs include snapshot identifier.  
- Calculation Service persists results to Azure PostgreSQL and produces a claim worksheet listing supporting purchase lines, tier reached, earned rebate and variance to accrual.  
- Rebate Analyst exports the worksheet to Excel. Finance Manager reviews claim worksheet; if the calculated claim > USD 50,000 Finance Manager approves (approve flow tested in separate scenario).  
- Verify audit logs capture agreement version, extraction model/prompt version, confirmed terms version, data snapshot date, calculation inputs and outputs, and export/approval events. Verify reproducibility by re-running calculation using the recorded agreement version and snapshot date and comparing results.

# 24. Approvals
- QA Test Plan approval required from: Supplier Programs Finance (Business Owner), Program Admin (Product Owner), Architecture Owner, AI Governance Council (as relevant for AI usage), and QA Lead / Test Manager.  
- Project-level approvals noted in BRD: AI Governance Council; Finance (BIR); AI intake; Global Intake; C2P; WAB. Test Plan sign-off should reference those stakeholder approvals where applicable.  
- Approval action: TBD – confirm sign-off process and owners with Product Owner.

End of Test Plan.