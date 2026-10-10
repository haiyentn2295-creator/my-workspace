---
name: ai4a:brainstorm
description: "Turn unclear ideas, business tasks, or project briefs into bounded execution contracts and compare viable approaches before building. Use when starting a new session task, scoping a workflow, framing a capstone project, or exploring solution trade-offs. Not for executing finished code or diagnosing low-level runtime errors."
user-invocable: true
when_to_use: "Use whenever intent is fuzzy, at the start of a new workflow or project phase, or when choosing between multiple implementation strategies."
category: workflow
keywords: [brainstorm, ideation, oipo, scope, pdca, tradeoffs, contract, ai4a]
argument-hint: "[topic or problem] [--scope] [--oipo] [--pdca] [--html] [--quick]"
metadata:
  author: "MT Đức Thuận"
  brand: "AI4A"
  course: "Agentic AI with Google Antigravity"
  version: "1.1.0"
---

# AI4A: Brainstorm

> **Đóng gói & phát triển bởi MT Đức Thuận**  
> *Dành tặng học viên chương trình Agentic AI with Google Antigravity (AI4A)*

Transform fuzzy ideas, user requests, or business problems into concrete, testable execution plans before touching code or creating complex agent configurations.

## Core Contract

Every brainstorming session establishes four contract fields before proceeding to execution:

1. **Outcome:** The observable end state and tangible artifact produced (for example, a validated CSV report, an automated email draft, or an interactive dashboard).
2. **Constraints:** Real-world boundaries such as available data, privacy rules, execution time, human review requirements, and forbidden actions.
3. **Non-goals:** Explicit items and scope extensions that this iteration will not tackle to prevent project drift.
4. **Acceptance Criteria:** Verifiable, evidence-backed proof that confirms the solution works as intended.

When existing documentation already defines these fields, reuse them and focus only on unresolved decisions.

## Proportional Guidance

Calibrate depth to the complexity of the request:

- **Clear, simple requests:** Summarize the four contract fields immediately and confirm direction in a single step.
- **Ambiguous requests:** Ask at most one or two clarifying questions that materially affect the architecture or safety boundaries. Do not run long interrogations.
- **Flag `--quick`:** Generate the contract and two distinct approaches in a single pass without follow-up questions.
- **Autonomous workflows:** If the user provided enough context to deduce reasonable defaults, document the assumptions and proceed to option exploration.

## Option Exploration

When multiple viable solutions exist, compare two or three approaches:

1. **Approach 1 (Lean / Direct):** The simplest implementation using deterministic scripts or basic prompt-chaining with minimal moving parts.
2. **Approach 2 (Workflow / Agentic):** A structured pipeline with dedicated agent roles, explicit handoffs, and human checkpoints.
3. **Approach 3 (Advanced / Scalable):** A distributed or tool-augmented design suited for high-volume or edge-case-heavy environments.

For each approach, detail:
- **Core trade-off:** What you gain versus what complexity you introduce.
- **Key assumption:** The critical premise that must hold true for this option to succeed.
- **First failure point:** The exact scenario or edge case where this approach degrades first.

Recommend the leanest approach that satisfies the acceptance criteria while remaining straightforward to debug and audit.

## Course Framework Alignment

This skill seamlessly maps brainstorm results into the core course frameworks:

### SCOPE Alignment (Capstone & Project Briefs)
When invoked with `--scope` or during project definition, format findings to populate `docs/project-brief.md`:
- **Situation (S):** Operational context and baseline friction.
- **Constraints (C):** Boundaries, risky data, and rules.
- **Objective (O):** Desired quantifiable result.
- **Proposal (P / OIPO):** Proposed workflow pipeline.
- **Evaluation (E):** Acceptance criteria and test evidence.

### OIPO Alignment (Workflow Design)
When invoked with `--oipo`, format the chosen approach into the standard workflow spec:
- **Objective:** The business goal.
- **Input:** Source files, formats, and sample datasets in `sample-data/`.
- **Process:** Step-by-step logic, agent handoffs, and tool invocations.
- **Output:** Result files in `outputs/` matching the required schema.

### PDCA Alignment (Continuous Improvement)
When invoked with `--pdca`, format the decision as the initial **Plan** entry for `docs/pdca-log.md`, defining the specific hypothesis and the expected evidence file.

## Output Modes

- **Default (Markdown Brief):** Structured terminal or markdown summary containing the 4-field contract, compared approaches, recommended choice, and next action.
- **Flag `--scope`:** Formatted markdown ready to paste directly into `docs/project-brief.md`.
- **Flag `--oipo`:** Formatted workflow specification ready for `docs/workspace-map.md`.
- **Flag `--pdca`:** A ready-to-paste table row and hypothesis for `docs/pdca-log.md`.
- **Flag `--html`:** Produces a standalone, single-file `outputs/brainstorm-brief.html` with an interactive approach comparison matrix and a responsive flowchart illustrating the workflow.

## Boundaries and Guardrails

- Focus on clarifying intent, defining boundaries, and evaluating options. Do not perform large code edits or execute long tasks within this skill.
- Ground feasibility claims in available workspace data, actual files, or real-world evidence; do not assume ideal conditions.
- State any unresolved assumptions at the bottom of the brief so the user can validate them before implementation.
