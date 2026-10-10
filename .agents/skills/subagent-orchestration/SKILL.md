---
name: subagent-orchestration
description: >
  General guide for spawning, managing, and resuming autonomous subagents via the Antigravity CLI (agy).
  Covers session reuse, prompt design, read-only research workflows, and optional parallel worktree coding.
---

# Subagent Orchestration with `agy CLI`

This skill defines the general methodology for creating, controlling, and coordinating autonomous subagents using the Antigravity CLI (`agy`).

---

## 🛑 Golden Invariants (MUST FOLLOW)

1. **Session Reuse by Default**:
   - **NEVER** create a new subagent session unless the user **explicitly** requests a new one.
   - Whenever following up, iterating, fixing, or performing next steps on an existing task, **ALWAYS resume the existing session** using `--conversation <ID>`:
     ```bash
     agy --conversation <conversation-id> --dangerously-skip-permissions --print-timeout 30m -p "<follow_up_prompt>"
     ```
2. **Never Poll in Busy Loops**:
   - When dispatching long-running subagent processes from the IDE, launch them as background tasks with `WaitMsBeforeAsync: 1000`.
   - Rely on system notifications or the `schedule` tool for periodic checks. Do not loop continuously on `manage_task status`.
3. **Cross-Platform Workspace Logging & Lifecycle Management**:
   - Logs are categorized into two lifecycle states:
     - `logs/active/`: Subagents currently running or actively kept open for iterative work.
     - `logs/inactive/`: Subagents whose tasks are completed, retired, or explicitly closed by the user.
   - Standard file naming format:
     ```text
     logs/active/subagent_<task>.log
     logs/inactive/subagent_<task>.log
     ```
   - When a session is retired or the user requests to close it, move the log:
     ```bash
     mv logs/active/subagent_<task>.log logs/inactive/
     ```
   - Always use forward slashes (`/`) for cross-platform compatibility across Windows, Linux, and macOS.
4. **Reactive Inspection & Result Synthesis**:
   - When the system sends an automatic notification that the subagent task has finished, the Orchestrator (Main Agent) MUST immediately read the generated log file in `logs/active/` via `view_file`.
   - Synthesize and present the execution summary, key decisions, and artifacts to the user.
5. **Active Registry Tracking (`logs/active/README.md`)**:
   - **ALWAYS** maintain a concise tracking table in `logs/active/README.md` to track active subagents across sessions:
     `| Task | Conversation ID | Mục đích | Trạng thái |`
   - **On Creation**: Extract the Conversation ID and add a row to `logs/active/README.md`.
   - **On Deactivation**: Remove the row from `logs/active/README.md` and move the log file to `logs/inactive/`.

---

## 1. Invoking Subagents via `agy CLI`

Subagents run non-interactively in print mode (`-p`).

### Critical Flag Ordering Rule:
> [!WARNING]
> In `agy CLI`, placing `-p` before other options can cause it to treat subsequent flags as part of the prompt string.
> **Always place `--log-file`, `--dangerously-skip-permissions`, and other options BEFORE `-p`**:

```bash
# 1. Starting a NEW subagent session:
agy --log-file logs/active/subagent_<task>.log --dangerously-skip-permissions --print-timeout 30m -p "$(cat <prompt_file>)"
# After start/completion, extract Conversation ID and record into logs/active/README.md:
# CID=$(grep -oE "conversation [a-f0-9-]{36}" logs/active/subagent_<task>.log | head -n 1 | awk '{print $2}')
# Update logs/active/README.md: | <task> | <CID> | <purpose> | Active |

# 2. REUSING an existing active subagent session:
# (Check logs/active/README.md to quickly find the Conversation ID for the task):
agy --conversation <conversation-id> --log-file logs/active/subagent_<task>.log --dangerously-skip-permissions --print-timeout 30m -p "$(cat <prompt_file>)"

# 3. CLOSING / DEACTIVATING a subagent session (User requests to close):
# 1) Move log: mv logs/active/subagent_<task>.log logs/inactive/
# 2) Remove task entry from logs/active/README.md
```

---

## 2. Common Execution Workflows

Subagents are general-purpose workers that can be dispatched for various workflows:

### A. Read-Only Tasks (Research, Audit, Analysis, Planning)
For information gathering, investigative debugging, code auditing, or architectural reviews:
- Run directly in the current workspace directory.
- No branch switching, no worktrees, zero filesystem overhead.
- Example:
  ```bash
  agy --dangerously-skip-permissions --print-timeout 20m -p "Audit the usage of legacy modules across src/ and produce an analysis report."
  ```

### B. Single-Task Code Modification
For standard feature development or bug fixes:
- Checkout the dedicated task branch directly in the workspace (`git checkout -b <branch> origin/master`).
- Run the subagent to implement changes, verify quality gates, and commit.

### C. Parallel / Concurrent Coding
When multiple subagents write code at the same time across separate branches:
- Use isolated Git worktrees to prevent branch collisions.
- Full setup and lifecycle details are documented in [**Parallel Worktree Coding**](references/parallel-worktree-coding.md).

---

## 3. Subagent Prompt Design

Prompts should be **problem-oriented and high-level**, granting the subagent autonomy to inspect the codebase and read relevant repository skills rather than prescribing micro-actions.

### Core Elements of an Effective Prompt:
1. **Goal / Problem Statement**: Clearly describe what problem needs to be solved.
2. **Skills to Activate**: Instruct the subagent to read and follow specific skills (e.g. `feature-sliced-design` for frontend architecture, `fsd-audit` for code reviews).
3. **Quality Gates (Mandatory)**:
   - TypeScript verification: `pnpm type-check` (must pass with 0 errors).
   - ESLint verification: `pnpm lint:diff` (must pass with 0 errors, never bypass rules with ignore comments).
   - Automated tests: `pnpm test:unit <target_path>` (100% tests must pass).
4. **Delivery**: Specify the conventional commit message format and Pull Request creation command (`gh pr create`).

---

## 4. Monitoring & Tracking Subagents

### A. Workspace Logs (`logs/active/` and `logs/inactive/`) — Primary & Cross-Platform
Full execution output is saved directly in the workspace, separated by operational state:
- **`logs/active/README.md`**: **Quick Registry Dashboard** — Displays all active subagent tasks, their Conversation IDs, and current purposes in a single markdown table. Any new chat session or agent can read this file to discover and resume existing subagents.
- **`logs/active/subagent_<task>.log`**: Full execution log for running or ready-to-resume subagents.
- **`logs/inactive/subagent_<task>.log`**: Archived execution logs for closed subagents.
- Accessible directly in the IDE file explorer across Linux, macOS, and Windows.
- The Orchestrator agent reads the active log directly via `view_file` to inspect the results.

### B. Internal System Transcripts (Engine Level)
Antigravity CLI also stores full JSONL transcripts and tool calls under the user profile:
- **Linux / macOS**: `~/.gemini/antigravity-cli/brain/<conversation-id>/.system_generated/logs/transcript.jsonl`
- **Windows**: `%USERPROFILE%\.gemini\antigravity-cli\brain\<conversation-id>\.system_generated\logs\transcript.jsonl`

#### Inspection Commands (Linux / macOS / Git Bash):
```bash
# Find recent subagent conversation IDs:
ls -lat ~/.gemini/antigravity-cli/brain/ | head -n 6

# Check recent tool calls and thoughts of a subagent:
tail -n 25 ~/.gemini/antigravity-cli/brain/<id>/.system_generated/logs/transcript.jsonl | jq -r 'select(.tool_calls != null and (.tool_calls | length) > 0) | "\(.tool_calls[0].name): \(.tool_calls[0].args.toolSummary // .tool_calls[0].args.CommandLine)"'
```

---

## 5. Detailed References

- [**Parallel Worktree Coding**](references/parallel-worktree-coding.md): Detailed guide on provisioning isolated worktrees, symlinking `node_modules`, and sequential rebasing for concurrent coding tasks.
- [**FSD Entity Migration Case Study**](references/fsd-entity-migration-case-study.md): Real-world case study migrating 4 domain modules to FSD v2.1 entities via parallel subagents.
