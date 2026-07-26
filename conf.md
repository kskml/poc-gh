h1. [System Name] — Software Architecture Document (SWE.2 / arc42)

*Document Control*
||Field||Value||
|System / ECU|[System Name]|
|ASPICE Process|SWE.2 — Software Architectural Design|
|arc42 Version|9 (4+1 view model)|
|Status|Draft|
|Author / Architect|[Name]|
|Baseline / Commit|[Tag / SHA]|

----

h2. 1. Introduction and Goals

h3. 1.1 Purpose
[One-paragraph statement: what this architecture defines, which system it belongs to, and the SWE.2 scope — static decomposition, dynamic behavior, component interfaces, and resource allocation of software requirements to components.]

h3. 1.2 Quality Goals (Top 3–5)
||#||Quality Goal||Scenario / Metric (measurable)||Traceability||
|1|[e.g. Timing]|[e.g. end-to-end latency < 20 ms @ 100% load]|[SR-NNN]|
|2|[Safety]|[ASIL D, no single-point faults]|[SR-NNN]|
|3|[Reliability]|[MTBF > 50k h]|[SR-NNN]|

h3. 1.3 Stakeholders
||Stakeholder||Concern||Expectation||
|System Owner|[cost, schedule]|[...]|
|Safety Manager|[ASIL compliance]|[...]|
|SW Developer|[clarity, buildability]|[...]|

----

h2. 2. Drivers and Constraints

h3. 2.1 Functional Drivers
* [Top-level functional requirements driving the architecture]
* [Each tagged with SR-ID for traceability]

h3. 2.2 Technical Constraints
||ID||Constraint||Source||
|TC-1|[e.g. AUTOSAR Classic 4.4]|[Platform spec]|
|TC-2|[e.g. 32-bit MCU, 512 KB RAM]|[HW spec]|
|TC-3|[e.g. MISRA-C:2012 Mandatory]|[Coding standard]|

h3. 2.3 Organizational & Standards Constraints
* [ISO 26262, ASPICE 4.0, ISO 21434 (Cybersecurity), GDPR, ...]

h3. 2.4 Assumptions
* [Assumption — and impact if wrong]

----

h2. 3. Use Case View (4+1 — Scenarios)

h3. 3.1 Use Case Catalog
||UC-ID||Use Case||Priority||Implements SR||
|UC-01|[primary actor action]|High|[SR-NNN]|
|UC-02|[...]|Medium|[SR-NNN]|

h3. 3.2 Architecturally Significant Scenarios
*UC-01: [name]*
* *Actor:* [...]
* *Precondition:* [...]
* *Main flow:* 1. ... 2. ... 3. ...
* *Postcondition:* [...]
* *Architectural impact:* [which components, which NFRs stressed]

----

h2. 4. Context View (System Boundary)

*(Insert Context Diagram here - e.g., PlantUML macro or draw.io)*

h3. 4.1 External Interfaces
||Interface||Direction||Protocol||Type||Traceability||
|IF-01 CAN-FD|In/Out|CAN 2.0B / ISO 11898|Signal|[SR-NNN]|
|IF-02 SOME/IP|Out|Ethernet / SOME/IP-SD|Service|[SR-NNN]|
|IF-03 UDS|In|DoIP / ISO 14229|Diagnostic|[SR-NNN]|

----

h2. 5. Logical View (Static Decomposition)

*(Insert Component/Block Diagram here - e.g., PlantUML macro or draw.io)*

h3. 5.1 Component Catalog
||ID||Component||Responsibility||Allocates SR||ASIL||
|C-01|[name]|[one-line purpose]|[SR-NNN, SR-NNN]|[B/D]|
|C-02|[name]|[...]|[SR-NNN]|[Q/A/B/C/D]|

h3. 5.2 Component Interfaces (Internal)
||Provider||Consumer||Operation||Signature||Error Behavior||
|C-01|C-02|[opName]|[ret opName(in1: T, in2: T)]|[E_NOT_OK / E_TIMEOUT]|

----

h2. 6. Dynamic View (Runtime Behavior)

h3. 6.1 Sequence: [UC-01 / scenario name]
*(Insert Sequence Diagram here)*

h3. 6.2 State Machine: [component name]
*(Insert State Machine Diagram here)*

h3. 6.3 Concurrency & Synchronization
* *Tasks / threads:* [list, priorities, scheduling]
* *Shared resources / locks:* [critical sections, locking strategy]
* *Timing budget (wcet / deadline):* [table or ref]

----

h2. 7. Data Model View

*(Insert Entity-Relationship or Class Diagram here)*

h3. 7.1 Data Dictionary (excerpt)
||Name||Type||Unit||Range||Persistency||Owner||
|[signal]|uint16|ms|0..65535|NVM|C-02|
|[calParam]|float32|deg|-90..90|Flash|C-01|

h3. 7.2 Persistence & Calibration
* *NVM layout:* [module, blocks, CRC scheme]
* *Flash calibration:* [versioning, fallback, integrity check]

----

h2. 8. Deployment View (Physical)

*(Insert Deployment Diagram here)*

h3. 8.1 Resource Budget
||Component||CPU Load (%)||RAM (KB)||Flash (KB)||NVM (bytes)||
|C-01|<5>|<8>|<24>|<128>|
|C-02|<3>|<4>|<12>|<64>|
|*Total*|*<50>*|*<200>*|*<1024>*|*<2048>*|

----

h2. 9. Security View

h3. 9.1 Threat Analysis (excerpt)
||ID||Threat (STRIDE)||Asset||Risk||Control||
|T-01|Spoofing on CAN bus|Signal integrity|H|CRC + SecOC|
|T-02|Tampering of OTA image|Firmware|H|Sig + Rollback|
|T-03|Info disclosure of NVM|Personal data|M|Encryption at rest|

h3. 9.2 Security Controls
* *Secure boot:* [chain of trust, HSM usage]
* *SecOC / Authentication:* [which signals]
* *Key management:* [HSM, key rotation, key storage]
* *Access control:* [UDS security levels, roles]

h3. 9.3 Trust Boundaries
*(Insert Trust Zone Diagram here)*

----

h2. 10. Crosscutting Concepts
||Concept||Description||
|Logging & Tracing|[levels, sinks, formats, ring buffer]|
|Error handling|[fault model, E_NOT_OK propagation, default values]|
|Configuration mgmt|[variant handling, pre-compile/post-build]|
|Diagnostics (UDS)|[DTC handling, snapshot, UDS service map]|
|Memory mgmt|[static alloc only, no malloc in safety path]|

----

h2. 11. Architectural Decisions (ADRs)

h3. ADR-001: [decision title]
* *Status:* [Proposed | Accepted | Deprecated | Superseded]
* *Date:* [YYYY-MM-DD]
* *Context:* [why a decision is needed; alternatives considered]
* *Decision:* [what was decided]
* *Consequences:* [positive / negative; impact on NFRs]
* *Alternatives:* [opt A — rejected because...; opt B — rejected because...]
* *Traceability:* [SR-NNN, TC-NNN]

----

h2. 12. Quality Requirements (NFRs)

h3. 12.1 Quality Tree
*(Insert Quality Tree Diagram here)*

h3. 12.2 Quality Scenarios
||QS-ID||Scenario||Stimulus/Response||Metric||Traceability||
|QS-01|[peak load]|[load 100%, response]|[P99 < 20ms]|[SR-NNN]|
|QS-02|[fault injection]|[single-point fault]|[no violation of SG]|[SR-NNN]|

----

h2. 13. Risks and Technical Debt
||ID||Risk / Debt||Likelihood||Impact||Mitigation / Owner||
|R-01|[external API unstable]|H|H|[mock now, contract test before Baseline]|
|TD-01|[hardcoded config]|—|M|[refactor in SWE.3, ticket-NNN]|

----

h2. 14. Traceability Matrix (SWE.2 BP6)
||SR-ID||Requirement (short)||Component||Use Case||Quality Scenario||Detailed Design (SWE.3)||
|SR-001|[...]|C-01|UC-01|QS-01|DD-001|
|SR-002|[...]|C-02|UC-02|QS-02|DD-002|

----

h2. 15. Open Issues
||ID||Issue||Owner||Due||
|OI-01|[unresolved interface]|[name]|[date]|

----

h2. 16. Glossary
||Term||Definition||Source||
|ASIL|Automotive Safety Integrity Level|ISO 26262|
|SecOC|Secure Onboard Communication|AUTOSAR|
|SG|Safety Goal|ISO 26262|
