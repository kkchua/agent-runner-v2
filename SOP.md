# Architecture, Implementation, and Validation SOP

## Roles

- **Codex:** Architecture advisor, solution reviewer, tester, and validator. Codex defines requirements and acceptance criteria, reviews Qwen Coder's plan, and validates the finished implementation. When a plan needs changes, Codex drafts a review and a prompt for Qwen Coder to revise it. Codex does not revise Qwen Coder's plan or implement the solution as part of the review workflow.
- **Qwen Coder:** Plan, implementation, and source handoff package owner. Qwen Coder turns Codex's guidance into a functional and implementation plan, revises that plan in response to Codex's review, implements it after user approval, and prepares the deployment package described below.
- **User:** Approves the plan before implementation and decides whether the delivered solution is accepted after validation.

## Workflow

1. Codex clarifies the requirement, proposes the architecture and acceptance criteria, and gives Qwen Coder implementation guidance.
2. Qwen Coder produces a functional and implementation plan for review.
3. Codex reviews the plan for feasibility, completeness, risks, and alignment with the requirements. If revision is needed, Codex gives Qwen Coder a concrete revision prompt; Qwen Coder updates the plan and resubmits it for review. Codex does not edit the plan during this review cycle. The user approves the final plan before implementation begins.
4. Qwen Coder implements the approved plan and prepares the source handoff package under `deployment/`.
5. Codex tests and validates the completed work and handoff package against the approved plan and acceptance criteria, reports defects or gaps for Qwen Coder to fix, and recommends acceptance only when the evidence supports it.
6. The user gives final acceptance and may pass the package to the developer for deployment.

If requirements or architecture change materially during implementation, Qwen Coder submits an updated plan for review and user approval before continuing with the changed scope.

## Plan-First Approval Gate

- For a new feature or material change, Codex prepares a plan-only request for Qwen Coder. Qwen Coder may inspect code and documentation to prepare the plan, but must not edit implementation files, build, or test the change at this stage.
- Save each task's Qwen request and submitted plan in a task-specific folder under `Planning/`. Prefix the folder name with `YYYYMMDD-XX`, where `YYYYMMDD` is the task creation date and `XX` is a two-digit sequence starting at `01` for that date (for example, `20261023-01_TransferOut_PCN_Reprint`). Keep the request separate from the plan so the review trail is clear.
- Codex reviews the submitted plan and sends Qwen Coder concrete revisions when needed. Qwen Coder owns the plan and submits the revised version; Codex does not edit Qwen Coder's plan.
- Implementation may begin only after Codex has completed the review and the user explicitly approves the final plan. Silence, a request to investigate, or approval to draft a plan does not authorize implementation.
- If implementation reveals a material requirement or architecture change, stop implementation for the affected scope, submit a revised plan, and get explicit user approval before continuing.
- After implementation, Codex validates against the approved plan and acceptance criteria. The user makes the final acceptance decision.

## Source Handoff / Deployment Package

- For each approved task, create `deployment/<planning-folder-name>/`, using **exactly the same folder name** as its folder under `Planning/`, including the `YYYYMMDD-XX` prefix. Example: `Planning/20261023-01_TransferOut_PCN_Reprint/` corresponds to `deployment/20261023-01_TransferOut_PCN_Reprint/`.
- Put the complete source of every new and modified file needed for the task in that deployment folder. Preserve each file's path relative to the workspace root, so the package can be copied to the corresponding destination without guessing where a file belongs. For example, `wms7/tomcat/webapps/wms7/WEB-INF/src/example/Foo.java` goes at `deployment/<planning-folder-name>/wms7/tomcat/webapps/wms7/WEB-INF/src/example/Foo.java`. Do the same for web resources, configuration, and SQL scripts. Do not package unrelated files or compiled output unless the approved plan explicitly calls for them.
- Add a root `README.md` to the deployment folder. It must contain separate **New files** and **Modified files** sections. List **every** packaged deliverable, including SQL scripts, in the appropriate section using its complete workspace-relative path (not just its filename), and give a short purpose for each. State the matching target path when it differs from the workspace-relative path. The root README itself need not appear in those lists.
- Add a **Database scripts** section to `README.md`. List every required script by its complete package-relative path, the target database/schema, the execution order, and what it changes. State any prerequisites or manual data steps and the post-execution checks. If no database work is required, say `None`. Include the scripts in the package at their correct paths; listing them alone is insufficient. Do not execute scripts or deploy as part of package creation unless separately authorized.
- Add a short **Deployment order and verification** section explaining when to apply database scripts and source files, any required rebuild/restart, and the checks the developer should perform. State any known limitations or dependencies that affect deployment. The README is a handoff guide, not proof that deployment occurred.
- Before handoff, compare the package file list with the final implementation and approved plan. Confirm each listed path exists in the package, every changed deliverable is included once, and the packaged contents match the reviewed source. Codex checks this package during final validation; Qwen corrects any omissions before the user accepts it.
