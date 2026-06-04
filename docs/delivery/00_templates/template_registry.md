# Template Registry

## Document Type Mapping

| Layer | Doc Type | Folder |
|---|---|---|
| Initiative | 01_initiative | 01_initiatives |
| Plan | 02_plan | 02_plans |
| Task Graph | 02b_task_graph | 02_plans/artifacts |
| Task | 03_task | 03_tasks |
| Implementation Plan | 04_implementation_plan | 04_implementation_plans |
| Review | 04_review | 05_reviews |
| Validation | 05_validation | 05_reviews |
| Memory | 06_memory | 06_memory |

## Flow

```
Initiative → Plan → Task Graph → Task → Implementation Plan → Code → Review → Validation → Memory
```

### Stage Descriptions

| Stage | Artifact | Purpose |
|---|---|---|
| Initiative | 01_initiative | Define the problem, scope, success criteria, and governance for agent-runner-v2 delivery efforts |
| Plan | 02_plan | Design the strategy, task breakdown, system design, and execution flow — reference workflow gates from WORKFLOW_SOP_v1.md |
| Task Graph | 02b_task_graph | Decompose the plan into executable task nodes with dependency ordering and parallelism annotations |
| Task | 03_task | Individual task contract with inputs, outputs, acceptance criteria, and validation requirements |
| Implementation Plan | 04_implementation_plan | HOW to implement — file plan with [NEW]/[MODIFY] tags, test plan, module responsibilities |
| Review | 04_review | Independent review of any delivery artifact against its acceptance criteria |
| Validation | 05_validation | Final validation of behavior and contract compliance — verify tests pass, artifacts exist, sidecars valid, traceability correct |
| Memory | 06_memory | Capture durable knowledge, key decisions, architecture notes, and learnings for future delivery cycles |

### Sidecar Expectations

Every generated markdown artifact must have a matching *.meta.json sidecar at the same path. The sidecar contains structured coder output including schema_version: "v2", coder_result with status (APPROVED/REJECTED), remark, artifact paths, usage data, and recorded_at timestamp. The runner reads the sidecar — never stdout — to determine step outcome via step_runner.py and routes via workflow_router.py.

## Template Naming Convention

All templates follow the pattern: `{NN}_{name}.template.md`

Where `NN` is a zero-padded sequence number and `name` is a lowercase, underscore-separated identifier.

The task graph template uses the variant `02b_task_graph.template.md` where `02b` denotes a sub-artifact of the `02_plan` layer.

## Versioning

- Templates are versioned via the `Template Version` field in each template's metadata block.
- Breaking changes to template structure increment the template version.
- Delivery documents reference the template version they were generated from.
- Current version: v1 for all templates.

## Usage

1. Select the appropriate template from this registry for the delivery stage.
2. Substitute placeholder variables ({{YYYYMMDD}}, {{NN}}, {{TITLE}}, {{SLUG}}, etc.) with runtime values.
3. Save the generated document to its corresponding folder under docs/delivery/.
4. Link the document ID back to the parent artifact (initiative → plan → task → etc.).
5. Write a matching *.meta.json sidecar with structured coder output per llm_response_schema.json.

## Agent Roles (Reference)

The following agent roles are defined in WORKFLOW_SOP_v1.md — workflow step configurations in template_groups.py serve as their invocation contracts (agent master prompts in 07_master_prompts/ are deprecated):

| Role | Responsibility |
|---|---|
| Planner | Delivery plan creation from approved init document |
| Task Decomposer | Dependency-aware task graph generation |
| Implementation Planner | Scoped implementation plans with tests and rollback |
| Executor | Implementation within approved scope |
| Reviewer | Independent review of plans, graphs, implementations |
| Validator | Final validation of behavior and contract compliance |
| Memory Manager | Durable context, snapshots, supersession links |
| Architect | Workflow policy, scope, approval gates (project owner) |
| Runner | State enforcement, budget, routing, sidecar validation (automated) |
