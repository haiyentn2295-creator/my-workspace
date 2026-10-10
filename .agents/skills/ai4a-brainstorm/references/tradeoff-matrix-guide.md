# Trade-off Matrix Guide (AI4A)

> **Tác giả:** MT Đức Thuận — *Nguyên tắc thiết kế kiến trúc Lean cho học viên Agentic AI (AI4A)*

When brainstorming a technical solution or agentic workflow, comparing multiple approaches prevents premature commitment to overly complex architectures.

## The 3 Archetype Approaches

| Dimension | Approach 1: Lean / Direct | Approach 2: Workflow / Agentic | Approach 3: Scalable / Advanced |
|---|---|---|---|
| **Architecture** | Python script + Single LLM prompt | Multi-agent pipeline with handoffs | Tool-augmented or RAG-based engine |
| **Setup Effort** | Low (1-2 hours) | Moderate (half day) | High (multiple days) |
| **Auditability** | High (easy to inspect code/prompt) | High (inspectable per agent handoff) | Moderate (depends on tracing tools) |
| **Best Used When** | Input is uniform and task is linear | Task requires distinct roles & checkpoints | Input is massive, messy, or unbounded |

---

## The Evaluation Triad

For each approach, evaluate these three questions:

### 1. What is the load-bearing assumption?
Every architecture relies on one critical premise. If that premise fails, the entire approach collapses.
- *Example (Lean):* Assumes all input files fit comfortably within context limits and follow standard schemas.
- *Example (Multi-Agent):* Assumes inter-agent handoff schemas remain consistent across turns.

### 2. What is the first failure point?
Identify the worst plausible scenario rather than assuming optimal operation.
- *Example:* "If an input CSV has missing column headers, does the pipeline crash or degrade gracefully?"

### 3. Which option is cheapest to abandon?
When uncertain about requirements or user data quality, prefer the architecture that requires the least sunk cost to pivot or replace.

---

## Recommendation Heuristic for Course Projects

1. **Start at Approach 1 or 2:** Avoid jumping straight to Approach 3 unless data scale or tool requirements strictly necessitate it.
2. **Apply KISS (Keep It Simple, Stupid):** If a deterministic Python script can parse and validate data before an agent sees it, do not make the agent do basic regex or math.
3. **Insert Checkpoints for Risk:** Any action that mutates external systems, sends messages, or makes high-stakes evaluations requires an explicit Human Checkpoint.
