# 1. Document Control
- Title: QA Master Test Plan
- Version: 1.0
- Application: Supplier Rebate Claim Validation
- Prepared by: QA Lead, Quality Engineering
- Reviewed by: Test Manager (TBD – confirm with Supplier Programs Finance)
- Audience: Business Stakeholders (Supplier Programs Finance), Program Admins, Finance Managers, Architects, Development and QA teams
- Purpose: Defines the test approach, scope, coverage and exit criteria to validate Supplier Rebate Claim Validation MVP1: agreement ingestion, AI extraction of tiers/terms, analyst confirmation, calculation using Delta Lake purchase data, claim worksheet generation and associated controls, to meet BRD acceptance criteria and NFRs.

# 2. References
- Business Requirement Specification – Supplier Rebate Claim Validation, Version 1.0, 17 Feb 2026
- Solution Architecture: P06_Rebate_Validation_Architecture.png

# 3. Test Objectives
- Verify extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental flag, eligible product lines and exclusions from uploaded agreement PDFs with page references, using Azure Document Intelligence and Azure OpenAI.
  - Measurable target: meet acceptance criterion ≥95% accuracy of extracted tier terms on golden agreements (T51, T64).
- Verify analyst confirmation flow: only analyst-confirmed terms persist to Azure PostgreSQL and are used by the Calculation Service (T02, T07, T40).
- Verify calculation correctness for retroactive and incremental methods against Databricks Delta Lake purchase data:
  - Measurable targets: 100% calculation accuracy against analyst-verified examples (T65); calculation for one supplier-year within 2 minutes (T24).
- Verify claim worksheet generation, supporting purchase lines export to Excel, and variance to accrual reported (T09, T20).
- Verify role-based approvals and segregation of duties: Finance Manager approval required above USD 50,000 and analysts cannot approve own claims (T04, T16, T17).
- Verify reproducibility/auditability: each calculation must be reproducible with agreement version and data snapshot date (T26, T66).
- Verify integrations and data flows: Agreement Service -> Blob Storage, Calculation Service -> Delta Lake (Databricks SQL) over HTTPS/443 OAuth 2.0, APIM -> AI services, UI -> services (T32–T45).
- Verify availability target and batch performance: 99% business hours availability (T22); month-end batch of 400 agreements within 8 hours (T25).

# 4. In Scope
- Functional (MVP1)
  - Upload of agreement PDFs and amendments via Web UI with storage in Azure Blob Storage (T05, T39).
  - AI extraction of supplier, period, tiers (threshold, rate), retroactive vs incremental flag, eligible product lines and exclusions via APIM -> Azure Document Intelligence and Azure OpenAI (T06, T43–T45).
  - Analyst confirmation step: confirmed terms persisted to Azure PostgreSQL (T07, T40).
  - Calculation Service reading purchase data from Delta Lake (EUDM) via Databricks SQL to compute eligible spend, tier reached and earned rebate (T08, T42).
  - Claim worksheet with supporting purchase lines, export to Excel and variance to accrual calculation (T09).
  - RBAC per BRD: Rebate Analyst, Finance Manager, Program Admin (T29–T31).
  - Auditability metadata: agreement version, data snapshot date, calculation inputs and outputs (T26).
- Non-functional (MVP1)
  - Availability: 99% business hours (T22).
  - Performance: single supplier-year calculation ≤ 2 minutes; month-end batch (400 agreements) ≤ 8 hours (T24, T25).
  - Security: Azure AD authentication and data restriction per BRD (T23).
  - Observability: logging of agreement upload, extraction run, analyst confirmation, calculation run and result persistence.

# 5. Out of Scope
- All MVP2 items and explicitly listed exclusions:
  - Supplier portal submission (T10)
  - Dispute tracking (T11)
  - Accrual posting to finance (T12)
  - Amendment comparison (T13)
- Additional BRD exclusions:
  - Customer rebates (sell-side) (T53)
  - Price protection claims (T54)
  - Supplier payment collection (T55)

# 6. Assumptions and Dependencies
- Assumptions (from BRD)
  - Delta Lake purchase data is complete for the last 24 months (T56).
  - Agreements are mostly digital PDFs (T57).
  - Program Admin will supply product line mapping data monthly (T48).
- Dependencies
  - Databricks/Delta Lake access: Data platform team for Databricks access (T58).
  - Golden labelled agreements and SME support: Supplier Programs SMEs (T59).
  - Approvals required: AI Governance Council, Finance (BIR), AI intake, Global Intake, C2P, WAB (T60, T52).
- Test constraints
  - Non-production environment labelled in architecture; test teams must use masked or synthetic data for restricted/confidential fields (T46–T49).
  - If Delta Lake is unavailable in test, approved mocks must be used (T58) — mocking approach: TBD – confirm with Data platform team.

# 7. Test Strategy
- Overall approach: risk-based testing prioritized on extraction accuracy, confirmation flow, calculation correctness, approvals, data reconciliation and performance at month-end scale.
- Test levels
  - Unit tests: developer owned for agreement parsers, DB mappers, calculation logic. Target code coverage: TBD – confirm with dev lead.
  - Component tests: Agreement Service, Calculation Service, UI components, APIM AI connectors.
  - API/contract tests: Web UI -> Agreement Service, Web UI -> Calculation Service, Calculation Service -> Delta Lake (Databricks SQL), Agreement Service -> Blob Storage/PostgreSQL, APIM -> Azure Document Intelligence/OpenAI.
  - Integration tests: full path from upload -> extraction -> confirmation -> calculation -> worksheet.
  - System tests: validate NFRs and security controls.
  - UAT: Rebate Analysts and Finance Managers to validate with golden dataset and approve acceptance criteria.
- Test techniques
  - Requirements-based tests mapped to each TEST BASIS item.
  - Equivalence partitioning and boundary value analysis for thresholds (tier thresholds ascending, completeness).
  - Data-driven tests using labelled golden agreements and representative purchase datasets.
  - Exploratory testing for complex agreement language and edge-cases.
  - Regression suites for extraction models and calculation code after model or code changes.
- Automation
  - Automate API contract tests and calculation correctness checks where possible. Tool(s): TBD – confirm with QA Manager and DevOps.

# 8. Functional Test Coverage
For each functional area below, tests will verify positive, negative and edge cases, and log expected results and evidence.

- Agreement upload (T05, T39)
  - Valid PDF upload -> stored in Blob Storage; metadata recorded (uploader, timestamp, file size).
  - Multiple pages, attachments, amended agreements uploaded and versioned.
  - Invalid files: corrupted PDF, password-protected PDF, non-PDF -> clear UI error, no persisted terms.
  - Large file handling and retry on transient Blob Storage failures.

- AI extraction (T06, T43–T45)
  - Verify extracted fields: supplier, period, tier list (threshold & rate), retroactive vs incremental indicator, eligible product lines, exclusions.
  - Verify page reference recorded for each extracted term.
  - Golden dataset tests: run extraction on labelled agreements; measure accuracy of extracted tier terms against golden labels; target ≥95% (T51, T64).
  - Boundary/edge cases: complex language, tables of tiers, amendments that modify existing tiers, multiple currencies on contract text (confirm only extraction of tier thresholds and rates).
  - Error handling: extraction failures or low-confidence outputs flagged for analyst review; extraction retries for transient APIM/AI errors.

- Analyst confirmation (T02, T07, T40)
  - Unconfirmed extraction: cannot be used by Calculation Service; UI prevents "Run calculation" until confirmation complete.
  - Confirmed terms persisted to Azure PostgreSQL (verify DB record fields and version).
  - Change detection: if analyst edits terms, a new version is saved and prior version retained for audit.
  - Negative tests: accidental confirmation rollback or save failures produce clear error and do not trigger calculation.

- Calculation using Delta Lake (T08, T42)
  - Correct retrieval of purchase data via Databricks SQL with HTTPS/443 OAuth 2.0.
  - Correct selection of eligible product lines per product line mapping (T48) and exclusions.
  - Implements business rules:
    - Retroactive: highest achieved rate applied to full spend for the period (T14).
    - Incremental: apply specified rate per tier band (T15).
  - Worked numeric examples (explicit test cases derived from BRD tiers — use tiers exactly as in BRD: threshold USD 1,000,000 -> rate 2%; threshold USD 2,000,000 -> rate 3% (T01, T21)):
    - Case A: Supplier spend = USD 1,500,000; tiers = {1,000,000@2%; 2,000,000@3%}
      - Expected retroactive result: 1,500,000 * 2% = USD 30,000.
      - Expected incremental result (per-tier bands: 0–1,000,000 @2%; 1,000,000–2,000,000 @3%): 
        - 1,000,000 * 2% = 20,000
        - 500,000 * 3% = 15,000
        - Total = USD 35,000.
      - Test verifies Calculation Service produces both results correctly per selected method and records which method used.
    - Case B: Supplier spend = USD 2,500,000; same tiers
      - Expected retroactive: 2,500,000 * 3% = USD 75,000.
      - Expected incremental:
        - 1,000,000 * 2% = 20,000
        - 1,000,000 * 3% = 30,000
        - 500,000 * 3% = 15,000 (amount above highest threshold assumes highest tier rate applies)
        - Total = USD 65,000.
      - Test verifies correct results and identifies difference between retroactive and incremental algorithms.
    - Case C: Supplier spend < first threshold (e.g., USD 900,000)
      - Expected retroactive: highest achieved rate—no tier reached above first threshold; business requirement requires validation before calculation (T19). Specific expected rebate depends on tier definitions; tests will verify system handles "no tier reached" case per BRD and flags zero rebate or as specified by configuration (T19).
      - Note: where BRD does not define base rate below first threshold, tests will verify system behavior is documented and aligned with Program Admin configuration — any gap is captured as defect or requirement clarification.
  - Verify handling of multiple product-line eligible spend and exclusions.
  - Verify rounding and decimal precision rules (T08).
  - Verify calculation reproducibility: calculation records agreement version and data snapshot date used (T26, T66).

- Claim worksheet and exports (T09)
  - Worksheet contains: supplier, period, confirmed tiers & version, eligible spend by purchase line, tier reached, earned rebate per method, variance to accrual.
  - Export to Excel preserves page references, purchase line detail and calculation audit fields.
  - Variance to accrual computed and flagged where reconciliation exceeds configured tolerance (tolerance value TBD – confirm with Program Admin).

- Reconciliation & GL totals (T20)
  - Verify that aggregated purchase data used for rebate calculation reconciles to GL totals for the period (sample reconciliation tests using provided datasets).
  - Where reconciliation fails beyond tolerance, calculation must flag and block claim finalization until reviewed.

# 9. Roles, Permissions and Workflow Testing
- Roles per BRD (T29–T31): Rebate Analyst, Finance Manager, Program Admin.
- Tests:
  - Authentication: Azure AD login, SSO via App Gateway (T32–T35). Verify role assignment maps to permitted actions.
  - Rebate Analyst:
    - Allowed: upload agreements, view extraction results, edit/confirm terms, run calculations, prepare and export claim worksheet (T29).
    - Forbidden: approve claims above USD 50,000, modify approval limits, change Program Admin settings.
  - Finance Manager:
    - Allowed: review and approve claims above USD 50,000 (T30, T16).
    - Verify approval action requires explicit sign-off and is recorded in audit trail with user, role and timestamp (T26).
  - Program Admin:
    - Allowed: maintain supplier mappings, product line mappings and calculation settings (T31).
    - Forbidden: Approve claims (segregation of duties) — verify Admin cannot approve own claims and cannot approve claims they created (T17).
  - Specific workflow tests:
    - Create a claim with calculated rebate = USD 50,001 and verify Finance Manager approval required; Rebate Analyst cannot approve (T04, T16).
    - Attempt self-approval by Rebate Analyst and Program Admin and confirm system rejects and logs attempt (T17).
    - Verify approval metadata persisted in Azure PostgreSQL and exported worksheet.

# 10. Security, Privacy and Compliance Testing
- Authentication/Authorization
  - Azure AD (Entra ID) SSO via App Gateway and OAuth2.0; verify login, token expiry, session behaviour (T34).
  - Verify least privilege: role-only access to actions/data; confirm restricted classification enforced for agreements and purchase data (T23, T46–T49).
- Data protection
  - Verify agreements and calculation results stored in Blob Storage and Azure PostgreSQL with encryption at rest and in transit per enterprise standards (confirm configuration; if missing, record as finding).
  - Verify UI and exports do not expose restricted fields unless authorized.
- Input validation & hardening
  - Protection against file-based attacks (malicious PDFs), injection in extracted text, oversized payloads.
- Compliance & approvals
  - Confirm dependency on AI Governance Council approval and capture evidence (T52, T60).
  - SOX / C2P relevance: verify segregation of duties enforcement for approvals (T16, T17).
- Penetration & scanning
  - SAST/DAST scans and dependency vulnerability scanning: TBD – confirm with Security Owner.

# 11. AI and Data Quality Validation
- Golden dataset
  - Supplier Programs SMEs to provide labelled golden agreements (T59). Dataset must include complex language and edge cases.
- Accuracy targets
  - Extraction: ≥95% accuracy of extracted tier terms on golden agreements (T51, T64). Measure precision and recall per field (threshold, rate, retroactive/incremental flag).
- Human-in-the-loop controls
  - Analyst confirmation mandatory; only confirmed terms are persisted and used in calculations (T50, T07).
  - Tests to ensure unconfirmed terms are not used, and that confirmation UI forces explicit action.
- Responsible AI controls
  - Capture model and prompt version per extraction run. Verify reprocessing path after model or prompt changes records prior version and results.
  - Verify Azure OpenAI normalisation does not alter numeric values (thresholds/rates) — create tests where OpenAI output must match numeric values from Document Intelligence; any change must be surfaced to analyst.
- Hallucination controls
  - Tests to include deliberately ambiguous or missing tier text to verify AI does not invent tiers; low-confidence outputs must be surfaced for analyst confirmation.
- Metrics and reporting
  - Log extraction confidence scores, operator corrections, and track extraction accuracy over time.

# 12. Performance Testing
- Targets (from BRD)
  - Single supplier-year calculation ≤ 2 minutes (T24).
  - Month-end batch of 400 agreements ≤ 8 hours (T25).
- Tests
  - Single-run performance: measure Calculation Service end-to-end latency (from UI trigger to results persisted) for representative supplier-year with realistic Delta Lake data.
  - Month-end batch: run Azure Function (Batch Scheduler) invocation to process 400 agreements and measure end-to-end completion time and resource utilisation; monitor Databricks query performance and concurrency limits.
  - Load of concurrent analyst users: test concurrent calculations and UI access with TBD – confirm concurrency target with Program Admin.
  - Failure & throttling: test Databricks query timeouts and back-off behaviour.
- Metrics to capture: end-to-end latency, Databricks query time, API response times, CPU/memory usage of Calculation Service, DB write latency, queue/backlog behaviour for batch.

# 13. Reliability and Recovery Testing
- Availability target: 99% business hours (T22).
- Tests
  - Service restart during a running calculation: verify idempotency, partial-result rollback or resume semantics and data consistency.
  - Transient network failure to Delta Lake: verify retry logic, back-off and observable errors for manual resolution.
  - Corrupt or partial agreement upload: ensure no persistent confirmed terms unless full confirmation completed.
  - Database failover: test Calculation Service behaviour and notification/alerting.
  - Batch resilience: partial failures in a 400-agreement batch should be retried and failures reported; successful ones must persist.
- Recovery validation: after recovery, verify calculations remain reproducible with recorded data snapshot.

# 14. Accessibility and Compatibility Testing
- Accessibility checks: keyboard navigation, screen reader labels, focus order, color contrast, error identification and zoom/reflow per enterprise accessibility standards. (Exact standard: TBD – confirm with Accessibility Owner).
- Browser compatibility: Enterprise-supported browsers (TBD – confirm with Program Admin), minimum coverage: current enterprise editions of Edge, Chrome, Firefox.

# 15. Logging, Monitoring and Audit Testing
- Audit trail fields required (per BRD & architecture): user, role, agreement version, page references for extracted terms, extraction model/prompt version, data snapshot date, calculation inputs (purchase lines used), calculation method (retroactive/incremental), results, approval actions and timestamps (T26).
- Tests
  - Verify every calculation run emits structured logs and metrics: execution time, data snapshot ID, agreement ID/version, DB write success.
  - Verify alerts on batch failures, extraction confidence degradation, or reconciliation failures.
  - Exportability: verify export of audit trail for a calculation run.
  - Retention: retention policy TBD – confirm with Supplier Programs Finance.
- Monitoring tools used in architecture: Datadog, Azure Monitor; verify integration and dashboards configured (TBD – confirm with Ops).

# 16. Test Environments and Test Data
- Environments (per architecture): Non-production subscription with Web UI, Agreement Service, Calculation Service, Azure Function (Batch Scheduler), APIM in Azure AI Landing Zone, and supporting services. Use masked or synthetic data for any restricted/confidential values (T46–T49).
- Test data
  - Golden agreements (labelled) from Supplier Programs SMEs (T59) covering:
    - Simple tier tables, multi-page agreements, amendments, incremental vs retroactive examples, exclusions and product-line mappings.
  - Delta Lake purchase data seeded for test suppliers representing 24 months of data per assumption (T56); if real data not available, use synthetic but reconciliation-capable datasets.
  - Product line mapping configuration (monthly owner: Program Admin).
- Data management
  - Record dataset snapshot IDs and agreement version for every test run to satisfy reproducibility (T26).
  - Ensure no unmasked bank/tax identifiers in test data.
- Test environment provisioning: TBD – confirm with Platform/DevOps team.

# 17. Entry, Suspension and Exit Criteria
- Entry criteria
  - BRD approved and requirements baselined (documented).
  - Test environments provisioned and accessible per architecture (APIM, Blob Storage, PostgreSQL, Databricks access) or approved mocks available (T58).
  - Golden dataset and Delta Lake test data seeded (T59, T56).
  - AI Governance Council approval status available (T52) or explicit path for UAT with model snapshot.
  - Build deployed to non-production with component tests passing.
- Suspension criteria
  - Critical dependency unavailable (e.g., Databricks SQL access) for > 2 business days without approved workaround.
  - Blocking security or data exposure issues discovered.
- Exit criteria (aligned to BRD acceptance)
  - Extraction accuracy target met for golden agreements: ≥95% for tier terms (T51, T64).
  - Calculation correctness: 100% accuracy against analyst-verified examples (T65).
  - All critical path test cases passed.
  - No open Critical defects and no open High-severity security defects (severity definitions below).
  - Performance: single supplier-year calculation ≤ 2 minutes and month-end batch (400 agreements) ≤ 8 hours (T24, T25).
  - Auditability: demonstrations that calculations are reproducible with agreement version and data snapshot date (T26, T66).
  - UAT sign-off by Supplier Programs Finance and sample sign-off by Finance Manager for approval flows.
- Approval to release MVP1: business sign-off (Supplier Programs Finance) after exit criteria met or documented exception accepted by Product/Business.

# 18. Defect Management
- Defect tracking tool: TBD – confirm with QA Manager.
- Severity definitions (aligned to business impact)
  - Critical: incorrect calculation code or wrong match of tiers leading to materially incorrect rebate amounts; data corruption; security breach.
  - High: core workflow blocked (e.g., cannot confirm terms, calculations fail for majority of suppliers), RBAC violation preventing Finance Manager approval enforcement.
  - Medium: function works with workaround (e.g., export formatting issues, minor UI errors).
  - Low: cosmetic or documentation issues.
- Process: defects logged with steps to reproduce, expected/actual results, environment, dataset snapshot ID, agreement version, severity, owner, and retest plan. Triage cadence: daily for Critical/High, weekly for Medium/Low unless risk dictates otherwise.

# 19. Risks and Mitigations
- Complex agreement language causing extraction errors (T61)
  - Mitigation: mandatory analyst confirmation; build golden dataset covering edge cases; create fallbacks to manual term entry.
- Data lake gaps or incomplete Delta Lake data (T62)
  - Mitigation: reconciliation checks to GL totals; block calculations where reconciliation fails; provide clear diagnostics; maintain test data completeness requirement.
- Retroactive vs incremental misinterpretation by AI or code (T63)
  - Mitigation: explicit field captured for calculation method; unit and integration tests for retroactive and incremental; SME review and test cases (worked examples).
- Delayed or missing AI Governance Council approvals (T52)
  - Mitigation: escalate to Product/Business and capture approval milestones; run UAT with approved model snapshots only.
- Performance risk at month-end (T25)
  - Mitigation: performance testing at scale early; Databricks query optimisation and batching; monitor and tune.

# 20. Test Deliverables and Reporting
- Deliverables
  - Test plans and test case suites mapped to requirements.
  - Golden dataset and test data snapshots with labels.
  - Automated API/contract test suites and execution reports.
  - Performance test reports for single-run and 400-agreement batch.
  - Security scan and penetration test reports (as available).
  - Defect reports and triage logs.
  - UAT sign-off evidence and acceptance checklist (includes extraction accuracy and calculation correctness evidence).
- Reporting cadence
  - Weekly QA status reports: planned/executed/passed/failed/blocked, open defects by severity, extraction accuracy metrics, calculation correctness pass rate, performance KPIs and unresolved risks.
  - Ad-hoc escalation reports for Critical defects.

# 21. Traceability and Metrics
- Traceability: every TEST BASIS ID maps to test cases and evidence. Test coverage matrix will be maintained.
- Key metrics to report
  - Extraction accuracy (precision/recall) per field, especially tier thresholds and rates.
  - Calculation correctness rate vs analyst-verified examples.
  - Mean/95th percentile calculation latency for single supplier-year.
  - Batch completion time for 400 agreements.
  - Number and severity of defects open/closed.
  - Reproducibility status (percentage of runs with agreement version + snapshot ID captured).
  - KPI progress: recovered rebate % (target +1.5% of rebate income) and time to prepare claim per supplier (target reduction to 4 hours) — measurement and reporting approach TBD – confirm with Supplier Programs Finance.

Traceability table: Test basis ID | Item (short) | Plan section
| Test basis ID | Item (short) | Plan section |
|---|---:|---|
| T01 | Upload + extracted tiers with page refs | 8 Functional Test Coverage — AI extraction; 11 AI & Data Quality |
| T02 | Analyst confirmation mandatory | 8 Functional Test Coverage — Analyst confirmation; 11 AI & Data Quality |
| T03 | Run calculation and show purchases/tier/rebate | 8 Functional Test Coverage — Calculation; 21 Traceability & Metrics |
| T04 | Finance Manager approves > USD 50,000 | 9 Roles, Permissions and Workflow |
| T05 | Upload agreements -> Blob Storage | 8 Functional Test Coverage — Agreement upload |
| T06 | Extraction via Document Intelligence + OpenAI | 8 Functional Test Coverage — AI extraction |
| T07 | Confirmed terms persisted to PostgreSQL | 8 Functional Test Coverage — Analyst confirmation; 15 Logging & Audit |
| T08 | Calculation reads Delta Lake via Databricks SQL | 8 Functional Test Coverage — Calculation; 12 Performance |
| T09 | Claim worksheet + export + variance to accrual | 8 Functional Test Coverage — Claim worksheet |
| T10 | Supplier portal submission (MVP2) | 5 Out of Scope |
| T11 | Dispute tracking (MVP2) | 5 Out of Scope |
| T12 | Accrual posting to finance (MVP2) | 5 Out of Scope |
| T13 | Amendment comparison (MVP2) | 5 Out of Scope |
| T14 | Business rule: Retroactive calculation | 8 Functional Test Coverage — Calculation (worked examples) |
| T15 | Business rule: Incremental calculation | 8 Functional Test Coverage — Calculation (worked examples) |
| T16 | Finance approval > USD 50,000 | 9 Roles, Permissions and Workflow |
| T17 | Analysts cannot approve own claims | 9 Roles, Permissions and Workflow |
| T18 | Tier thresholds must be ascending | 8 Functional Test Coverage — Data quality checks |
| T19 | Agreement term completeness validated | 8 Functional Test Coverage — Pre-calculation checks |
| T20 | Purchase data must reconcile to GL totals | 8 Functional Test Coverage — Reconciliation; 15 Logging & Audit |
| T21 | Worked example tiers {1M@2%,2M@3%} | 8 Functional Test Coverage — Calculation worked examples |
| T22 | Availability 99% business hours | 12 Performance & 13 Reliability |
| T23 | Security via Azure AD, restricted data | 10 Security, Privacy & Compliance |
| T24 | Performance: one supplier-year ≤2 min | 12 Performance |
| T25 | Performance: 400 agreements ≤8 hours | 12 Performance |
| T26 | Auditability: reproducible with version & snapshot | 15 Logging & Audit; 11 AI & Data Quality |
| T27 | KPI: Recover +1.5% rebate income | 21 Traceability & Metrics (KPI tracking) |
| T28 | KPI: Reduce prep time to 4 hours/supplier | 21 Traceability & Metrics |
| T29 | Role: Rebate Analyst responsibilities | 9 Roles, Permissions and Workflow |
| T30 | Role: Finance Manager responsibilities | 9 Roles, Permissions and Workflow |
| T31 | Role: Program Admin responsibilities | 9 Roles, Permissions and Workflow |
| T32 | Integration: Rebate Analysts -> App Gateway | 7 Test Strategy — Integration tests |
| T33 | Integration: Finance Managers -> App Gateway | 7 Test Strategy — Integration tests |
| T34 | Integration: Azure AD -> App Gateway OAuth2.0 | 10 Security, Privacy & Compliance |
| T35 | Integration: App Gateway -> Web UI HTTPS/443 | 7 Test Strategy — Integration tests |
| T36 | Web UI -> Agreement Service REST | 7 Test Strategy — API tests |
| T37 | Web UI -> Calculation Service | 7 Test Strategy — API tests |
| T38 | Azure Function Batch Scheduler -> Agreement Service | 12 Performance; 13 Reliability |
| T39 | Agreement Service -> Blob Storage | 8 Functional Test Coverage — Agreement upload |
| T40 | Agreement Service -> PostgreSQL (confirmed terms) | 8 Functional Test Coverage — Analyst confirmation; 15 Logging & Audit |
| T41 | Calculation Service -> PostgreSQL (results) | 8 Functional Test Coverage — Calculation persistence |
| T42 | Calculation Service -> Delta Lake via Databricks SQL | 8 Functional Test Coverage — Calculation |
| T43 | Agreement Service -> APIM Managed Identity | 7 Test Strategy — Integration tests |
| T44 | APIM -> Azure Document Intelligence | 8 Functional Test Coverage — AI extraction |
| T45 | APIM -> Azure OpenAI | 8 Functional Test Coverage — AI extraction |
| T46 | Data: Rebate agreements metadata | 16 Test Environments & Test Data |
| T47 | Data: Purchase data from Delta Lake | 16 Test Environments & Test Data |
| T48 | Data: Product line mapping config | 16 Test Environments & Test Data |
| T49 | Data: Calculations tool output | 8 Functional Test Coverage; 15 Logging & Audit |
| T50 | AI quality rule: analyst confirmation mandatory | 11 AI & Data Quality |
| T51 | AI accuracy target ≥95% extracted tier terms | 11 AI & Data Quality |
| T52 | AI Governance Council approval required | 6 Assumptions & Dependencies; 10 Security & Compliance |
| T53 | Out of scope: Customer rebates | 5 Out of Scope |
| T54 | Out of scope: Price protection claims | 5 Out of Scope |
| T55 | Out of scope: Supplier payment collection | 5 Out of Scope |
| T56 | Assumption: Delta Lake complete 24 months | 6 Assumptions & Dependencies |
| T57 | Assumption: Agreements mostly digital PDFs | 6 Assumptions & Dependencies |
| T58 | Dependency: Data platform team for Databricks | 6 Assumptions & Dependencies |
| T59 | Dependency: Supplier Programs SMEs golden dataset | 6 Assumptions & Dependencies |
| T60 | Dependency/approvals: AI Governance Council, Finance (BIR), AI intake, Global Intake, C2P, WAB | 6 Assumptions & Dependencies |
| T61 | Risk: Complex agreement language | 19 Risks and Mitigations |
| T62 | Risk: Data lake gaps | 19 Risks and Mitigations |
| T63 | Risk: Retroactive vs incremental misread | 19 Risks and Mitigations |
| T64 | Acceptance: ≥95% extraction accuracy | 17 Entry/Exit Criteria |
| T65 | Acceptance: 100% calculation accuracy vs verified examples | 17 Entry/Exit Criteria |
| T66 | Acceptance: reproducible calculations with version & snapshot | 17 Entry/Exit Criteria |
| T67 | Timeline: MVP1 Mar–Jun 2026 | 22 Test Schedule |
| T68 | Timeline: MVP2 Q4 2026 | 5 Out of Scope / Future work |

# 22. Test Schedule
- MVP1 timeline per BRD: Mar–Jun 2026 (T67).
- Detailed test phase plan and dates: TBD – confirm with Program Manager (align testing windows to development sprints and environment availability).
  - Recommended phases (to be scheduled): component/integration testing, AI golden dataset tuning, system testing, performance testing (batch), UAT with Supplier Programs SMEs and Finance Manager, release validation.

# 23. End-to-End Scenario
Representative E2E scenario to validate core MVP1 flow:
- Rebate Analyst logs in via Azure AD SSO (App Gateway) (T32–T35).
- Analyst uploads a 6-page agreement PDF (versioned) via Web UI; file persisted to Azure Blob Storage (T05, T39).
- Agreement Service invokes APIM -> Azure Document Intelligence and APIM -> Azure OpenAI for layout and term extraction. Extracted tiers include thresholds with page references and retroactive flag (T06, T43–T45).
- Analyst reviews extraction, edits as required and confirms terms; confirmed terms are persisted in Azure PostgreSQL with version and audit metadata (T07, T40).
- Analyst triggers Calculation Service for a supplier-year. Calculation Service reads purchase data from Delta Lake via Databricks SQL (HTTPS/443 OAuth 2.0) and applies chosen calculation method (retroactive or incremental) (T08, T42).
- Calculation produces claim worksheet with purchase line details, tier reached and earned rebate; export to Excel includes audit fields and variance to accrual (T09, T20).
- If earned rebate > USD 50,000, the claim requires Finance Manager approval (system prevents analyst approval) (T04, T16, T17).
- Calculation and approval actions are logged with agreement version and data snapshot ID; reproduction of calculation is verified by re-running with the same snapshot (T26, T66).
- Performance and observability metrics for the run recorded; any reconciliation discrepancies are flagged for SME review.

# 24. Approvals
- Required approvals before release:
  - Supplier Programs Finance (business sign-off)
  - AI Governance Council (model/process approval) (T52)
  - Finance (BIR)
  - AI intake, Global Intake, C2P, WAB (as listed in BRD) (T60)
- QA sign-off: QA Lead and Test Manager (names / signatures: TBD – confirm with Supplier Programs Finance)

Notes / Open items (actions)
- Test defect tracking tool and automation toolchain: TBD – confirm with QA Manager / DevOps.
- Performance test concurrency targets for concurrent analyst users: TBD – confirm with Program Admin.
- Export/worksheet variance tolerance thresholds for blocking calculations or flagging to GL reconciliation: TBD – confirm with Finance Data / Program Admin.
- Environment provisioning schedule and Databricks access windows: TBD – confirm with Data platform team.

End of plan.