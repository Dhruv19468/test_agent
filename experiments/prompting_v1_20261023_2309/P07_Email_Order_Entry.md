# Test Plan — Email Purchase Order Entry Automation (MVP1 / MVP2)

Version: 1.0  
Author: Senior QA Lead  
Date: 2026-03-XX

Table of contents
- Purpose and objectives
- Scope (In / Out)
- Test strategy and approach
- Requirements traceability (high level)
- Test types to be executed
- Test environment and data
- Test entry and exit criteria
- Test deliverables
- Roles and responsibilities
- Test schedule and milestones
- Test design — test coverage and sample test cases
- Test automation strategy and tools
- Performance, scalability and reliability testing plan
- Security, privacy and compliance testing
- AI-specific testing (Document Intelligence / OpenAI)
- Integration and system interactions (SAP / Graph / Service Bus)
- Observability and logging verification
- Defect management and severity matrix
- Risks, assumptions and mitigations
- Approval / sign-off criteria
---

1. Purpose and objectives
- Validate that Email Purchase Order Entry Automation meets BRD functional and non-functional requirements for MVP1 (primary) and MVP2 (secondary).
- Demonstrate the system:
  - Converts incoming PO emails (body + attachments) into draft sales orders in SAP within acceptance performance limits.
  - Produces required accuracy of extraction and matching (>=95% headers, >=90% line accuracy for pilot customers).
  - Implements duplicate detection, SAP validation rules and CSR review queue (MVP1).
  - Implements MVP2 behaviors where indicated (straight-through release, acknowledgements) in the MVP2 test plan phase.
- Provide risk-based, repeatable verification with automated pipelines where feasible.

2. Scope
- In scope (MVP1):
  - Mailbox monitoring via Graph API; duplicate PO detection.
  - Extraction: header fields (PO number, sold-to, ship-to, requested date), line items (customer part, description, quantity, UoM, price).
  - Attachments: PDF, scanned images, Excel.
  - Customer identification (sender domain + content).
  - Item matching via customer cross-reference and catalog search (Azure AI Search).
  - SAP validation (customer active, material valid, price variance >5% flagged) via APIM; creation of draft sales order (not released).
  - CSR review queue UI with per-field confidences, ability to correct/create draft.
  - RBAC: branch-based queue access.
  - Observability: end-to-end traceability for each processed email.
- Out of scope:
  - EDI ingestion (except detection in MVP2), changes to credit checks/quotations/returns, straight-through release in MVP1, acknowledgements in MVP1, analytics in MVP1.

3. Test strategy and approach
- Risk-based testing, focusing first on high-impact flows (extraction accuracy, SAP validation, duplicate detection, CSR review).
- Hybrid approach: automated API and unit tests + manual exploratory and UAT for UI and complex edge cases and AI behavior.
- Early and continuous integration testing: tests run in CI (GitHub Actions) on every PR; nightly full integration tests against non-prod environment.
- Test pyramid:
  - Unit tests (development responsibility) — not included in this QA plan but verified in CI.
  - Integration/API tests: automated, run in CI.
  - End-to-End tests: automated where feasible (simulate mailbox events) and manual for complex document layouts.
  - Performance and Load tests: automated and scheduled; run before release.
  - Security tests: automated scans + manual penetration tests.
  - AI model validation tests: automated evaluation pipelines + manual spot checks.

4. Requirements traceability (high level)
Map (examples — representative; full traceability matrix delivered as separate artifact)
- BRD: Extraction of headers and lines -> Functional tests: HeaderExtraction_TC*, LineExtraction_TC*, AttachmentParsing_TC*
- BRD: Duplicate PO detection by customer PO number -> DuplicateDetection_TC*
- BRD: Customer identification by sender domain/content -> CustomerIdentification_TC*
- BRD: Item matching via cross-reference then catalog -> ItemMatch_CrossRef_TC, ItemMatch_CatalogFallback_TC
- BRD: SAP validation and price variance flagging -> SAPValidation_TC*, PriceVariance_TC*
- BRD: Draft creation within 5 minutes for 95% -> Performance_DraftLatency_TC
- BRD: CSR review queue, corrections -> CSRQueue_TC*, RBAC_TC*
- Acceptance criteria mapping:
  - ≥95% header field accuracy -> run Extraction Accuracy Validation tests, metrics and reports
  - ≥90% line accuracy -> run Line-level accuracy tests and metrics
  - Draft within 5 minutes for 95% -> Performance tests / production pilot telemetry
  - No orders released without CSR action in MVP1 -> ReleaseControl_TC

5. Test types to be executed
- Functional testing
- Integration testing (APIs & messaging)
- End-to-End (E2E) system testing
- UI testing (CSR Review Web UI)
- Regression testing
- Performance (load, stress) and scalability testing
- Reliability / resilience / recovery testing (retries, queue re-delivery)
- Security & access control testing (Azure AD / RBAC, data encryption, secrets)
- Penetration testing & vulnerability scanning
- AI-specific testing:
  - Extraction accuracy measurement (precision/recall per field)
  - Confidence scoring validation
  - Model drift and hallucination checks
  - Adversarial inputs / layout variability
- Data validation and quality tests (mandatory fields, UoM validation, quantity > 0)
- Observability & logging correctness tests (trace per email)
- Privacy & compliance testing (PII handling, retention, access)
- User Acceptance Testing (CSR + CS Supervisor + CS Admin)
- Pilot / business acceptance testing (pilot branches)

6. Test environment and data
- Environments required:
  - Dev: unit/integration development by engineers
  - QA/non-prod: complete stack per architecture diagram (APIM, Order Extraction Service, Order Creation Service, Web UI, Azure DI, Azure OpenAI, Azure AI Search, Blob storage, Cosmos DB, Event Grid, Service Bus, SAP sandbox via APIM, Graph API test mailboxes)
  - Performance test environment: scaled resources to emulate expected peaks
  - UAT environment: mirrors QA environment with CS branch access and SAP test instance
- External system requirements:
  - SAP S/4HANA test instance with sales order and pricing APIs enabled
  - Branch test mailboxes provisioned in Microsoft 365 and Graph API access
  - APIM endpoints configured to route to AI services and SAP test endpoints
- Test data:
  - Synthetic and anonymized real PO emails across representative templates/layouts (top 200 customers, plus edge customers).
  - Attachment types: native PDFs, scanned PDFs (images), Excel spreadsheets, mixed attachments, multiple pages.
  - Variants:
    - Correctly formatted POs (common templates)
    - Unusual layouts, line breaks, multiple POs in one email
    - Missing fields, handwritten signatures, multiple currencies, variable UoMs
    - PDFs with noise/low-quality scans
    - Duplicate POs (same PO number from same customer)
    - POs without cross-references, requiring catalog fallback
  - Cross-reference datasets: full, partial, empty for test cases
  - SAP master data scenarios: active/inactive customers, invalid materials, prices with >5% variance
- Data handling:
  - Use synthetic/anonymized data in non-prod.
  - PII must be tracked and access limited; test accounts use scrubbed data. Ensure Key Vault for secrets.

7. Test entry and exit criteria

7.1 Entry criteria (per phase)
- Unit/integration tests: code merged to branch; unit tests pass.
- QA/System Testing:
  - All required non-prod services deployed.
  - Mailbox access and SAP sandbox endpoints available.
  - Test data loaded (cross-reference files, catalog index).
  - Smoke tests pass (mailbox event triggers pipeline, one end-to-end email processed producing a draft).
- Performance testing:
  - Test harness available; baseline tests executed successfully.
- UAT:
  - QA regression pass.
  - Business stakeholders (CSRs) scheduled to participate.

7.2 Exit criteria
- All priority 1 and 2 defects resolved or mitigated with business sign-off.
- Functional test coverage for critical flows >=95% executed and passed.
- Acceptance criteria met:
  - Header accuracy >=95% and line accuracy >=90% on pilot sample (evidence via automated metrics and sample audit).
  - Draft creation latency: 95% within 5 minutes (evidence: test runs and telemetry).
  - Duplicate detection tests show 100% detection on curated test set.
  - No orders automatically released in MVP1 (validated by SAP audit logs).
- Performance tests: system can process 300 emails/h sustained with acceptable resource utilization and latency.
- Security vulnerabilities: no high or critical unmitigated vulnerabilities.
- Observability: tracing for end-to-end exists and validated.
- UAT sign-off by business owner and CS Supervisors for pilot branches.

8. Test deliverables
- Test plan (this document)
- Test cases and test scripts (automated & manual)
- Test data sets and test mailboxes
- Test execution reports (daily during execution)
- Defect log and metrics
- Traceability matrix mapping requirements -> tests -> results
- Performance reports and resource utilization graphs
- AI extraction accuracy metrics report
- Security & compliance test reports
- UAT acceptance sign-off document

9. Roles and responsibilities
- QA Lead (owner) — test plan, coordination, test metrics, final test sign-off
- QA Engineers — design and execute test cases, automate tests
- DevOps/Platform — provision and maintain non-prod environments and CI/CD pipelines
- Developers — provide unit tests, instrument logs and traces, fix defects
- Integration/SAP team — provide SAP sandbox and support API contract testing
- CS Business SMEs (CSRs, CS Supervisor, CS Admin) — UAT, acceptance testing, provide PO templates and examples
- Security team — run vulnerability scans and penetration tests
- AI Governance / ML Ops — provide model evaluation artifacts and participate in AI-specific testing
- Product Owner / Business Owner — acceptance criteria sign-off

10. Test schedule and milestones (high level)
- Test planning & environment setup: 2 weeks
- Test case design and automation development: 3 weeks (parallel)
- Integration / System test execution: 2–3 weeks
- Performance & resilience testing: 1 week
- UAT (pilot branches): 1–2 weeks
- Remediation & regression: 1–2 weeks
(Adjust per release sprint schedule: MVP1 Apr–Jul 2026; QA activities align to iteration delivery.)

11. Test design — test coverage and sample test cases
Below are representative test cases across categories. Full test case pack will include positive, negative and exploratory variations.

11.1 Functional / E2E test cases (representative)

- TC-FUNC-001: Mailbox Event Ingestion — Single PO email (simple template)
  - Precondition: Test mailbox contains an email with one PO in body and no attachments.
  - Steps: Trigger new mail event; verify Event Grid -> Service Bus -> Order Extraction Service flow; verify draft created in Cosmos DB and Web UI queue.
  - Expected: Draft sales order created with header (PO number, sold-to, ship-to, requested date), line(s) extracted; per-field confidences populated.

- TC-FUNC-002: Attachment Parsing — PDF (native) with tabular lines
  - Steps: Send test email with structured PDF attachment containing header and lines.
  - Expected: Header and lines extracted correctly; line-level quantities and UoM validated.

- TC-FUNC-003: Attachment Parsing — Scanned PDF (image)
  - Steps: Scanned PDF attached; extraction pipeline uses Azure Document Intelligence OCR.
  - Expected: Extraction succeeds at acceptable accuracy (>target) and confidence flagged appropriately; low-confidence fields highlighted in UI.

- TC-FUNC-004: Attachment Parsing — Excel with multiple sheets
  - Expected: Correct sheet recognized; lines extracted; metadata preserved.

- TC-FUNC-005: Multiple POs in one email (out-of-scope assumption check)
  - Steps: Email contains two distinct PO numbers.
  - Expected: System flags multiple POs (per assumption “one PO per email in most cases”); specific handling: either create two drafts or flag for CSR review. Behavior must match business decision — test both expected behaviors once defined.

- TC-FUNC-006: Duplicate PO detection
  - Steps: Send two emails with same customer PO number for same customer mailbox.
  - Expected: Duplicate detected; second email routed to duplicate review queue or flagged; no duplicate draft created.

- TC-FUNC-007: Customer identification by sender domain + PO content
  - Steps: Verified sender domain mapping and ambiguous content mapping.
  - Expected: Customer resolved to correct SAP sold-to account; if ambiguous, flagged for CSR.

- TC-FUNC-008: Item matching — Cross-reference found
  - Steps: Sample line with customer part that exists in cross-reference file.
  - Expected: Correct material matched and SAP material ID used.

- TC-FUNC-009: Item matching — Cross-reference missing, catalog fallback
  - Steps: Customer part not present; catalog search should find best match.
  - Expected: Best match returned with confidence; if match below threshold, flagged for CSR.

- TC-FUNC-010: SAP validation — customer inactive
  - Steps: Provide PO for inactive SAP customer.
  - Expected: SAP validation failure; draft not created; error logged and CSR alerted.

- TC-FUNC-011: SAP validation — price variance >5%
  - Steps: Provide line price deviating by >5% from SAP price.
  - Expected: Line flagged in draft; CSR sees flag; draft saved; no auto-release.

- TC-FUNC-012: CSR review actions (edit line, add line, remove line, save)
  - Expected: Changes persisted to Cosmos DB draft; final draft saved; release action blocked in MVP1.

- TC-FUNC-013: RBAC — branch-based queue access
  - Steps: CSR from Branch A attempts to view Branch B queue.
  - Expected: Access denied.

- TC-FUNC-014: Traceability and observability
  - Steps: Retrieve end-to-end trace using correlation ID from email to draft order number.
  - Expected: Trace exists in logs and Datadog/Azure Monitor linking services.

11.2 Negative and edge cases

- TC-NEG-001: Missing mandatory header fields (PO number)
  - Expected: Draft flagged as incomplete; CSR prompted to fill; system logs error.

- TC-NEG-002: Line with quantity 0 or negative
  - Expected: Validation fails; flagged; CSR correction required.

- TC-NEG-003: Unsupported UoM
  - Expected: Flagged; suggest mapping in UI if possible.

- TC-NEG-004: Malformed Excel / password-protected attachment
  - Expected: Extraction fails gracefully; CSR receives error entry.

11.3 Integration & contract tests

- TC-INTF-001: APIM -> SAP contract test
  - Validate request/response schemas for customer validation and draft creation.

- TC-INTF-002: Graph API mailbox connectivity and permission change
  - Simulate mailbox permission failure; pipeline should retry or fail gracefully and log.

11.4 AI-specific tests (examples)

- TC-AI-001: Extraction accuracy measurement — header fields
  - Run batch of 200 annotated POs representing pilot customers; compute accuracy (% correct) per header field; report precision/recall.
  - Acceptance: >=95% header fields.

- TC-AI-002: Extraction accuracy measurement — line items
  - Run batch of annotated lines; compute line-level accuracy; acceptance: >=90%.

- TC-AI-003: Confidence calibration
  - Validate that confidence thresholds map to expected correctness; test that fields below threshold are flagged.

- TC-AI-004: Hallucination / wrong mapping detection
  - Provide adversarial inputs (ambiguous text, brand names similar to materials) and verify system does not invent material IDs; validate fallback behavior.

- TC-AI-005: Model prompt/regression tests
  - Versioned tests to ensure changes to prompts or model updates don’t reduce accuracy below baseline.

11.5 Performance & scalability test cases

- TC-PERF-001: Throughput baseline
  - Simulate 300 emails/hour sustained with realistic attachments and content variety.
  - Metrics: average end-to-end latency, 95th percentile latency, resource utilization.
  - Acceptance: For 95% of POs, draft created within 5 minutes; less than defined CPU/memory thresholds.

- TC-PERF-002: Peak burst
  - Simulate peak bursts greater than 300/hr (e.g., 500/hr) to observe queuing and auto-scaling; verify retries and no data loss.

- TC-PERF-003: Resilience under SAP API throttling
  - Simulate SAP APIM rate limits; ensure queuing and retry logic works; no lost orders.

11.6 Security & privacy test cases

- TC-SEC-001: Authentication & Authorization
  - Verify Azure AD SSO; validate RBAC for CSR/CS Admin/CS Supervisor.

- TC-SEC-002: Data at rest and in transit
  - Verify Blob and Cosmos DB encryption enabled; APIM/TLS enforced.

- TC-SEC-003: Authorization bypass attempts
  - Attempt direct API calls outside App Gateway with invalid tokens.

- TC-SEC-004: PII access controls
  - Verify logs do not expose sensitive customer data beyond permitted users.

- TC-SEC-005: Penetration test
  - Conduct manual pentest focused on web UI, APIM endpoints, injection vectors.

12. Test automation strategy and tools
- CI/CD: GitHub Actions for automated tests.
- Test frameworks:
  - API/integration tests: pytest + requests or Postman + Newman (contract tests in CI).
  - UI tests: Playwright or Selenium for Web UI flows (CSR queue).
  - Load tests: Azure Load Testing or JMeter for throughput scenarios.
  - AI evaluation: custom Python evaluation scripts to compute extraction metrics; store results in Cosmos DB / dashboards.
  - Containerized test harness for orchestration (simulate Event Grid & Service Bus messages).
  - Logging and tracing verification: Datadog/Azure Monitor SDK checks.
- Test data injection:
  - Automated scripts to push synthetic emails to Graph API test mailboxes or to generate Event Grid events for Service Bus ingestion.
- Test automation coverage target:
  - All API contract tests automated and run in CI.
  - Core E2E happy-path automated where possible; complex document extraction manual/exploratory and periodically automated for regression baselines.
- Regression suite: nightly execution with summary reports.

13. Performance, scalability and reliability testing plan
- Objectives:
  - Validate throughput 300 emails/hour sustained.
  - Validate draft creation within 5 minutes for >=95% of POs.
  - Validate behavior under API throttling, transient failures and bursts.
- Approach:
  - Simulate realistic mix of emails including CPU/OCR-heavy scanned PDFs.
  - Run base load tests and stress tests to failure to observe degradation and recovery.
  - Test autoscaling behavior of AKS services and any serverless components.
  - Monitor resource utilization, queue lengths, retry rates, and failure modes.
- Metrics to capture:
  - End-to-end latency (mean, p50, p95, p99)
  - Processing time per pipeline stage
  - Success rate
  - Resource utilization (CPU, memory), queue lengths
- Acceptance:
  - 95% of drafts created within 5 minutes during normal load (300/hr).
  - Service degrades gracefully and recovers without data loss.

14. Security, privacy and compliance testing
- Conduct:
  - Static Application Security Testing (SAST) and dependency scanning in CI.
  - Dynamic Application Security Testing (DAST) against web UI/APIM.
  - Penetration test (manual) for high-risk areas.
  - Validate Azure AD configurations, OAuth token flows, and scopes.
  - Confirm Key Vault usage for secrets and managed identities used for service-to-service auth.
  - Verify encryption at rest/in transit and role-based access to Blob and Cosmos DB.
  - Validate retention and purge policies for emails and drafts.
  - Confirm AI Governance Council requirements and artifacts documented.
- Acceptance: No critical/high vulnerabilities unmitigated and approvals from security.

15. AI-specific testing (detailed)
- Data labeling and ground truth:
  - Build annotated datasets covering top 200 customers' PO templates plus long-tail layouts.
- Metrics:
  - Per-field accuracy (PO number, sold-to, ship-to, requested date)
  - Line-level match rate (material match correctness)
  - Confidence calibration: map model confidence to empirical correctness
- Drift/regression:
  - Baseline extraction metrics saved per model version and prompt.
  - Regression tests ensure that model or prompt changes do not degrade below baseline.
- Explainability and audit:
  - Per-field provenance (which model/service produced the value, which source location in document).
  - Store model outputs and prompt used for auditability.
- Safety tests:
  - Adversarial and malformed documents to reveal hallucination.
  - Verify fallback rules: if confidence < threshold, field flagged and not auto-corrected.
- Acceptance:
  - Header >=95% accuracy; lines >=90% for pilot dataset.
  - Confidence thresholds reflect actual accuracy: e.g., fields with confidence >0.85 have >95% correctness (calibration target — tune per pilot).

16. Integration and system interactions
- Validate each connection/contract:
  - Graph API -> Event Grid -> Service Bus message schema and reliability (replay/retry).
  - APIM -> Azure Document Intelligence / Azure OpenAI / Azure AI Search: latency, error handling, throttling responses.
  - Order Creation Service -> SAP via APIM: request/response schema, error codes (e.g., customer inactive), idempotency.
- Test message sequencing and ordering: ensure that out-of-order events still produce consistent drafts (idempotency keys: messageId, PO number).
- Test failure cases: APIM responses 429/500 -> verify retry/backoff and dead-letter behavior.

17. Observability and logging verification
- Tests:
  - Validate each processed email yields a correlation ID that is present in logs of all components.
  - Validate Datadog/Azure Monitor dashboards show pipeline metrics and errors.
  - Validate business-level metrics: draft accuracy, time-to-draft, CSR correction rate.
  - Validate alerts fire on SLA breaches (e.g., draft older than 30 minutes flagged) and Supervisors see flagged items.
- Acceptance: Traces are end-to-end and dashboards reflect test runs.

18. Defect management and severity matrix
- Tooling: Azure DevOps/GitHub Issues/Jira (project standard).
- Severity definitions:
  - P0 (Critical): Blocking production release — data-loss, orders incorrectly released, or system inability to process any orders.
  - P1 (High): Major functionality broken for many customers (duplicate detection failure, extraction accuracy below acceptance).
  - P2 (Medium): Partial degradation, UI issues, minor functional gaps.
  - P3 (Low): Cosmetic, usability improvements, documentation.
- SLA for fixes during release:
  - P0: immediate fix/patch (hotfix); P1: fix in next sprint or patch within agreed timeframe with mitigation; P2/P3: scheduled.
- Triage:
  - Daily triage during test execution; business owner engaged for P0/P1 approvals.

19. Risks, assumptions and mitigations
- Risk: PO layout variability reduces extraction accuracy.
  - Mitigation: Broad sample datasets, fallbacks to catalog search, CSR review, iterative model tuning.
- Risk: SAP API throttling or schema drift.
  - Mitigation: Contract tests, queuing, retries, coordinate with SAP integration team.
- Risk: Mailbox access delays or Graph API permission constraints.
  - Mitigation: Early provisioning and smoke tests; simulated Event Grid events if Graph access limited.
- Risk: AI model drift after updates causing regressions.
  - Mitigation: Model version gating, regression dataset tests, AI Governance approval for changes.
- Risk: Non-prod environment not mirroring production scale.
  - Mitigation: Use scaled-up performance environment; validate autoscaling.
- Assumptions:
  - Test data will be provided or synthetic equivalents created.
  - SAP sandbox and mailboxes will be available before system testing.

20. Acceptance / sign-off criteria
- Functional: All critical flows pass smoke and regression suites.
- AI Accuracy: Header accuracy >=95% and line accuracy >=90% on pilot dataset.
- Performance: 95% of drafts created within 5 minutes during simulated 300/hr load.
- Release Control: No order auto-released in MVP1 (validated).
- Duplicate detection: 100% on curated test set.
- Security: No unresolved critical vulnerabilities; penetration test sign-off.
- UAT: Business owners (Customer Service Operations) sign off on pilot.
- Once the above are met and defects at P0/P1 resolved or agreed with mitigations, QA will recommend release to pilot.

21. Appendices

21.1 Test case matrix (summary mapping)
- Extraction tests -> TC-FUNC-001..010, TC-AI-001..003
- Duplicate detection -> TC-FUNC-006
- SAP validation -> TC-FUNC-010..011, TC-INTF-001
- CSR UI -> TC-FUNC-012..013
- Performance -> TC-PERF-001..003
- Security -> TC-SEC-001..005
(Full matrix delivered as spreadsheet linking BRD requirement IDs -> test IDs -> owner -> automation status)

21.2 Example KPIs & test reporting
- Test execution rate (tests run / tests planned)
- Defect density by severity
- AI extraction accuracy per field (daily during pilot)
- Time-to-draft distribution (p50, p95)
- Mean time to resolve P1/P2 defects
- Test coverage (requirements mapped to test cases)

21.3 Pilot plan notes
- Run pilot with selected branches (dev/test branches from BRD) using live but scrubbed emails for 2–4 weeks.
- Measure real-world accuracy and latency; tune models/prompts and adjust thresholds.
- Produce a pilot report for stakeholders before global rollout.

22. Sign-off
- QA Lead: [name / signature / date]
- Product Owner / Business Owner: [name / signature / date]
- Security Lead: [name / signature / date]
- SAP Integration Lead: [name / signature / date]

End of test plan.

If you want, I can:
- Produce the full test case spreadsheet with step-by-step test steps, expected results and automation status.
- Create the AI evaluation dataset specification and a stub evaluation script.
- Draft the CI pipeline tests to inject sample emails into Graph API and validate outputs.