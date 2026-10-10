# Framework Alignment Reference (AI4A)

> **Tác giả:** MT Đức Thuận — *Hệ thống tài liệu chuẩn hóa cho học viên Agentic AI (AI4A)*

This reference explains how the 4-field Brainstorm Contract maps into the core frameworks taught in the Agentic AI course.

## 1. Mapping: Brainstorm Contract to SCOPE (Project Brief)

| Brainstorm Contract Field | SCOPE Component | Student Document Target |
|---|---|---|
| **Outcome** | **Objective (O)** + **Evaluation (E)** | `docs/project-brief.md` -> ## Objective, ## Success Metric |
| **Constraints** | **Constraints (C)** + **Human Checkpoint** | `docs/project-brief.md` -> ## Constraints, ## Human Checkpoint |
| **Non-goals** | **Out Of Scope** | `docs/project-brief.md` -> ## Out Of Scope |
| **Acceptance Criteria** | **Evaluation (E)** + **Demo Data** | `docs/project-brief.md` -> ## Evaluation, ## Demo Data |

### Illustrative Example: Candidate Resume Screener

- **Outcome:** A ranked CSV file `outputs/candidate-ranking.csv` with top candidates scored 0-100 and reasonings.
- **Constraints:** Must not store unencrypted PII; must flag ambiguous resumes for human review instead of auto-rejecting.
- **Non-goals:** Will not auto-send email replies to candidates in this version; will not parse scanned image PDFs.
- **Acceptance Criteria:** Correctly extracts skills and scores 10 sample CVs in `sample-data/` matching the rubric in `knowledge-base/scoring-rules.json`.

---

## 2. Mapping: Brainstorm Contract to OIPO (Workflow Architecture)

When designing a workflow (Buổi 4), convert the contract into the OIPO structure:

- **Objective (O):** The stated business outcome.
- **Input (I):** Concrete input files (CSV, JSON, Markdown) located in `sample-data/` or `knowledge-base/`.
- **Process (P):** The execution sequence:
  1. Input ingestion and schema validation.
  2. Agent/script execution and scoring.
  3. Human checkpoint for boundary or low-confidence cases.
  4. Final report generation.
- **Output (O):** Measurable artifact placed into `outputs/`.

---

## 3. Mapping: Brainstorm Contract to PDCA (Continuous Improvement)

In Buổi 2 and throughout the project lifecycle:

- **Plan:** Derive the Plan from the recommended brainstorm approach. State the expected hypothesis clearly.
- **Do:** Run the workspace script or agent execution.
- **Check:** Measure output against the brainstorm **Acceptance Criteria**. Note any deviations.
- **Act:** If acceptance fails, document the root cause and adjust constraints or knowledge rules in the next loop.
