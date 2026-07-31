---
doc_type: "test_criteria"
lifecycle_status: "draft"
effective_version: "WFBUILD-20260728-16472873"
spec_reference: "product_master_generator_v1"
generated_at: "2026-07-28"
workflow_builder_run: "WFBUILD-20260728-16472873"
---

# Test Criteria: Product Master Generator v1

## 1. Spec Objective Summary

The Product Master Generator workflow must transform heterogeneous product information (documents, images, websites, manuals, marketing materials) into a single, reusable, machine-readable Product Master artifact. This artifact serves as the canonical knowledge source for downstream AI workflows, eliminating duplicated product research across campaign planning, media generation, copywriting, localization, and publishing pipelines.

The end-to-end transformation is: raw, unstructured product sources (input) -> consolidated, structured Product Master document (output) that contains sufficient context for downstream workflows to reason about the product without accessing the original research sources. The workflow is strictly scoped to knowledge acquisition and curation; it must NOT generate marketing content, images, videos, or perform any downstream business operations.

---

## 2. Criteria for analyze_spec Step

The analyze_spec step must produce a WORKFLOW_REQUIREMENTS document that accurately captures the intent specification. The following criteria verify correctness.

### 2.1 Workflow Type Classification

1. The requirements document MUST classify the workflow as a knowledge acquisition and consolidation pipeline, not a content generation pipeline.
2. The requirements document MUST identify the workflow pattern as prompt-driven with human review gates, consistent with the spec's "Human Review" guiding principle.
3. The requirements document MUST NOT classify this workflow as an action-only pipeline (the core transformation requires LLM reasoning for knowledge synthesis).

### 2.2 Objective Extraction

4. The requirements document MUST state the primary objective as: producing a reusable, consolidated Product Master artifact from heterogeneous product sources.
5. The requirements document MUST identify the input as heterogeneous product sources (documents, images, websites, manuals, marketing materials, or any combination thereof).
6. The requirements document MUST identify the output as a single Product Master artifact that serves as the canonical knowledge source for downstream workflows.
7. The requirements document MUST capture the transformation: raw sources -> ingestion -> consolidation -> curation/review -> Product Master artifact.

### 2.3 Scope Boundary Identification

8. The requirements document MUST explicitly list out-of-scope items: campaign planning, prompt generation, image generation, video generation, publishing, localization, advertisement optimization, and performance analysis.
9. The requirements document MUST NOT include any requirement for generating marketing content, ad copy, or creative assets.
10. The requirements document MUST NOT include any requirement for image or video generation pipelines.

### 2.4 Guiding Principles Capture

11. The requirements document MUST capture the "Single Responsibility" principle: the workflow acquires and curates product knowledge only.
12. The requirements document MUST capture the "Source Agnostic" principle: the workflow operates independently of where product information originates.
13. The requirements document MUST capture the "Knowledge First" principle: reusable knowledge is prioritized over immediate content generation.
14. The requirements document MUST capture the "Canonical Representation" principle: the Product Master is the single authoritative product representation.
15. The requirements document MUST capture the "Human Review" principle: knowledge quality is prioritized over speed, and human approval is part of the process.
16. The requirements document MUST capture the "Extensible" principle: the workflow must accommodate future knowledge domain expansion without significant redesign.

### 2.5 Artifact Identification

17. The requirements document MUST identify at least one input artifact category: raw product source documents or references.
18. The requirements document MUST identify the Product Master as the primary output artifact.
19. The requirements document MUST identify intermediate artifacts if applicable (e.g., ingestion manifest, source index, consolidation draft).
20. The requirements document MUST NOT identify downstream content artifacts (campaign plans, image prompts, video storyboards) as outputs of this workflow.

---

## 3. Criteria for generate_package Step

The generate_package step must produce a complete workflow package. The following criteria verify each file and its contents.

### 3.1 Required Files

1. The package MUST contain a `workflow.toml` file with valid TOML syntax.
2. The package MUST contain a `context_extensions.py` file implementing the WorkflowExtensions interface.
3. The package MUST contain a `prompts/` directory with at least one `.txt` prompt file per prompt-driven step.
4. The package MUST contain a `README.md` describing the workflow purpose, inputs, outputs, and usage.

### 3.2 Files That Must NOT Be Generated

5. The package MUST NOT contain image generation logic, API calls to image services, or image processing code.
6. The package MUST NOT contain video generation logic, API calls to video services, or video processing code.
7. The package MUST NOT contain campaign planning logic, ad copy generation, or marketing content templates.
8. The package MUST NOT contain publishing or localization logic.
9. The package MUST NOT contain hardcoded API keys, credentials, or secret values in any file.

### 3.3 workflow.toml Criteria

10. The `[workflow]` section MUST set `name` to a valid identifier (matching the directory name convention, e.g., `product_master_generator_v1`).
11. The `[workflow]` section MUST set `init_step` to the first step of the pipeline.
12. The workflow MUST end with a terminal step named `stepCompletion` with `action = "step_completion"`.
13. Each `[[step]]` MUST have `onsuccess` at the `[[step]]` top level, NOT under `[step.artifacts]`.
14. Every artifact key referenced in `produces` or `required_inputs` MUST be registered in `context_extensions.py` `register_artifact_keys()`.
15. The workflow MUST include at least one step with `requires_human_approval_after = true` to implement the Human Review principle.
16. The workflow MUST NOT declare any step that generates images, videos, or marketing content.
17. Prompt-driven steps MUST reference prompt files via relative paths (e.g., `prompts/01_ingest.txt`).
18. Action-driven steps (if any) MUST reference action functions decorated with `@action()`.

### 3.4 context_extensions.py Criteria

19. The class MUST extend `WorkflowExtensions` and set `workflow_name` to match the workflow directory name.
20. The `register_artifact_keys()` method MUST return a dictionary mapping every artifact key used in `workflow.toml` to a relative path.
21. The `build_context_extensions()` method MUST resolve ALL artifact paths to absolute paths using `workspace_root`.
22. The `build_context_extensions()` method MUST use `get_workspace_root()` with a fallback (e.g., `Path(project_root or get_workspace_root() or Path.cwd())`).
23. The file MUST NOT contain hardcoded absolute paths.
24. The file MUST import `WorkflowExtensions` from `agent_runner_v2.workflow_packages.extensions_base`.

### 3.5 Prompt File Criteria

25. Each prompt file MUST use bare `{ARTIFACT_KEY}` placeholders without backtick wrapping.
26. Each prompt file MUST include an Objective section describing what the LLM should accomplish.
27. Each prompt file MUST include a Reference Inputs section listing input artifacts with `{ARTIFACT_KEY}` placeholders.
28. Each prompt file MUST include an Artifacts section listing output artifacts with `{ARTIFACT_KEY}` placeholders.
29. Each prompt file MUST include an Output Instructions section specifying format and encoding requirements.
30. Each prompt file MUST explicitly instruct the LLM to use file-writing tools to create actual files on disk at the paths specified by artifact placeholders.
31. Each prompt file MUST clarify that the `meta.json` result field is for status/summary only, NOT for artifact data.

### 3.6 Action Code Criteria (if actions.py is generated)

32. Each action function MUST be decorated with `@action("action_name")`.
33. Each action function MUST return an `ActionResult` with a valid status ("APPROVED" or "REJECTED").
34. Action functions MUST contain actual implementation logic, not stub or placeholder code.
35. Action functions MUST handle errors gracefully and return "REJECTED" with a descriptive remark on failure.
36. Action functions MUST NOT contain hardcoded credentials or API keys.

### 3.7 Configuration Sample Criteria

37. If a `.env.sample` file is generated, it MUST list required environment variable names without values (e.g., `API_KEY=` not `API_KEY=sk-abc123`).
38. If a `config.json.sample` file is generated, it MUST use placeholder values, not real credentials.

---

## 4. Criteria for validate_bundle Step

The validate_bundle step must verify structural and semantic correctness of the generated workflow package.

### 4.1 Structural Checks

1. The `workflow.toml` MUST parse without TOML syntax errors.
2. All `[[step]]` entries MUST have a `name` field.
3. All prompt-driven steps MUST have a `prompt` field pointing to an existing file.
4. All action-driven steps MUST have an `action` field referencing a valid action name.
5. The `onsuccess` routing chain MUST form a valid path from `init_step` to `stepCompletion` with no orphaned steps.
6. Every artifact key in `workflow.toml` `produces`/`required_inputs` MUST have a corresponding entry in `context_extensions.py` `register_artifact_keys()`.
7. All prompt files referenced in `workflow.toml` MUST exist in the `prompts/` directory.

### 4.2 Semantic Checks

8. Action code (if present) MUST contain actual implementation logic, not empty functions or TODO comments.
9. Prompt files MUST NOT contain backtick-wrapped `{ARTIFACT_KEY}` placeholders (which would prevent resolution).
10. The `context_extensions.py` MUST NOT contain undefined variable references (e.g., using `workspace_root` without defining it).
11. The `context_extensions.py` MUST NOT return relative paths from `build_context_extensions()`.
12. The `workflow.toml` MUST NOT have `promotes` under `[step.artifacts]` (it must be at `[[step]]` top level if present).
13. The `workflow.toml` MUST NOT have `onsuccess` under `[step.artifacts]` (it must be at `[[step]]` top level).

### 4.3 File Completeness

14. The package directory MUST contain `workflow.toml`, `context_extensions.py`, and `prompts/` (if prompt steps exist).
15. The package MUST NOT contain extraneous files not required by the workflow (e.g., test scripts, build artifacts, unrelated documentation).
16. The `prompts/` directory MUST contain exactly the prompt files referenced in `workflow.toml`, no more and no fewer.

---

## 5. Criteria for review_package Step

The review_package step must verify the generated workflow fulfills the original spec objective.

### 5.1 Spec Fulfillment

1. The workflow MUST implement knowledge acquisition and consolidation as its core function.
2. The workflow MUST produce a Product Master artifact that consolidates information from heterogeneous sources.
3. The workflow MUST NOT implement content generation, image creation, video production, campaign planning, or publishing.
4. The workflow MUST include human review gates consistent with the "Human Review" guiding principle.
5. The workflow MUST be source-agnostic (able to accept product information from various origins without source-specific hardcoding).

### 5.2 Step-by-Step Verification

6. Each step in the workflow MUST serve a clear purpose in the knowledge acquisition pipeline (ingestion, consolidation, curation, review, or completion).
7. The first step(s) MUST handle ingestion of heterogeneous product sources.
8. The middle step(s) MUST perform knowledge consolidation (merging, deduplicating, structuring information from multiple sources).
9. The review step(s) MUST enable human curation of the Product Master before finalization.
10. The terminal step MUST be `stepCompletion`.

### 5.3 Data Flow Verification

11. Input artifacts (product sources) MUST flow into the ingestion step via `required_inputs`.
12. The Product Master output MUST flow from consolidation through review to final promotion.
13. Each step's `produces` artifacts MUST be consumed by downstream steps via `required_inputs`.
14. No step MUST reference an artifact that is never produced by any preceding step.
15. The artifact path resolution in `context_extensions.py` MUST ensure all artifact keys resolve to valid absolute paths.

### 5.4 No Hallucinations Check

16. The workflow MUST NOT reference API endpoints or services not implied by the spec (e.g., no social media APIs, no ad platform integrations).
17. The workflow MUST NOT declare `required_inputs` for artifacts the spec does not mention (e.g., no brand guidelines, no competitor analysis inputs unless explicitly stated as extensible future capability).
18. The workflow MUST NOT include model-specific configurations (e.g., hardcoded model names) that are not justified by the spec.
19. The workflow MUST NOT generate artifacts that belong to downstream workflows (e.g., campaign plans, image prompts, video storyboards).
20. The workflow MUST NOT include batch processing or scheduling logic unless the spec implies it (the spec does not).

---

## 6. Prompt Quality Criteria

These criteria verify that prompt-driven steps are clear and unambiguous enough for an LLM to follow correctly.

### 6.1 Output Mechanism Clarity

1. Every prompt MUST explicitly instruct the LLM to use file-writing tools (e.g., Write tool, write_file) to create actual files on disk.
2. Every prompt MUST explicitly state that the `meta.json` `result` field is for status summary only (e.g., "APPROVED", "REJECTED", brief remark) and MUST NOT contain artifact data.
3. Every prompt MUST include an explicit example or instruction showing the distinction: "Write the document to {ARTIFACT_KEY}" means create a file at that path, NOT put the document content in the meta.json result field.
4. Every prompt MUST specify the exact file format (e.g., Markdown with YAML frontmatter, TOML, Python) for each output artifact.

### 6.2 Ambiguity Check

5. Prompts MUST NOT use phrases like "output the result" without specifying whether "result" means a file on disk or a meta.json field value.
6. Prompts MUST NOT use `{ARTIFACT_KEY}` placeholders wrapped in backticks, code blocks, or quotes that could prevent resolution.
7. Prompts MUST clearly distinguish between input artifacts (read these files) and output artifacts (write these files).
8. Prompts MUST specify the encoding (ASCII-only) and character restrictions for all text outputs.
9. Prompts MUST specify naming conventions and section structure for all document outputs.

### 6.3 Common LLM Mistake Guards

10. Prompts for document-generating steps MUST guard against the LLM putting document content in the meta.json result field instead of writing to the artifact file.
11. Prompts MUST guard against the LLM creating placeholder/stub content instead of substantive analysis (e.g., "do not use TBD or TODO as section content").
12. Prompts for consolidation steps MUST guard against the LLM omitting source attribution or traceability information.
13. Prompts MUST guard against the LLM inventing product information not present in the input sources (hallucination prevention).
14. Prompts for review steps MUST guard against the LLM providing vague feedback (e.g., "looks good") instead of specific, actionable findings.

### 6.4 Completeness

15. Each prompt MUST specify all required YAML frontmatter fields for document outputs.
16. Each prompt MUST list all required sections for document outputs with expected content per section.
17. Each prompt MUST specify how to handle cases where input sources are incomplete or contradictory.
18. Each prompt MUST specify the traceability format (e.g., requirement IDs, source references) for linking output back to input.

---

## 7. Audit Criteria

The spec involves aspects that trigger multiple audit categories. The following audit criteria apply.

### 7.1 Security Audit

The spec implies potential interaction with external product sources (websites, APIs for image analysis, document parsing services). If the generated workflow includes external service integration:

1. API keys and credentials MUST be loaded from environment variables via `.env` file, not hardcoded in any source file.
2. Credentials MUST be passed securely (e.g., Bearer token in HTTP headers), not in URL query parameters.
3. Generated files, logs, and prompts MUST NOT contain credential values or secrets.
4. The `.env.sample` file MUST list required environment variable names with empty values (e.g., `IMAGE_ANALYSIS_API_KEY=`).
5. The workflow MUST handle authentication failures gracefully (return REJECTED with descriptive error, not crash).
6. The workflow MUST NOT log or echo credential values in action remarks or meta.json output.

### 7.2 Logic Audit

The spec involves source ingestion, error handling, and conditional branching (heterogeneous source types, partial failures).

7. If the workflow implements retry logic for source ingestion, it MUST handle all relevant failure modes: timeout, HTTP 503, network error, rate limit (HTTP 429), and authentication failure.
8. Timeouts for external requests MUST be configured with reasonable values (e.g., 30-60 seconds for HTTP requests, not infinite).
9. Error handling MUST distinguish between recoverable errors (retry) and fatal errors (abort with REJECTED status).
10. If the workflow processes multiple sources, it MUST handle partial failure (some sources succeed, some fail) without losing the successful results.
11. State MUST be properly managed across step boundaries: artifacts produced by one step MUST be available to the next step via the artifact path resolution mechanism.

### 7.3 Data Integrity Audit

The spec involves file operations (ingesting sources, producing consolidated output, potentially archiving processed inputs).

12. File write operations MUST produce complete files, not partial writes (write to a temporary file then rename, or write the full content atomically).
13. If the workflow maintains an index of processed sources, the index MUST be updated completely and accurately (no missing entries, no duplicate entries).
14. If the workflow archives processed input sources, archiving MUST be done correctly: copy to archive location, then remove original (not a move operation that could lose data on failure).
15. If the workflow performs batch processing of multiple sources, it MUST track which files were processed successfully and which failed.
16. The Product Master output MUST include traceability information linking each knowledge element back to its source (e.g., source document name, URL, or section reference).
17. If the workflow modifies an existing Product Master (refinement loop), it MUST preserve previously approved content and only update changed sections.

### 7.4 Audit Applicability Statement

All three audit categories (Security, Logic, Data Integrity) apply to this spec because:
- Security: The spec's "Source Agnostic" principle implies potential integration with external services for source ingestion and analysis.
- Logic: The spec's handling of "heterogeneous product information" implies complex data flow, conditional branching by source type, and error handling for partial failures.
- Data Integrity: The spec's core function is transforming unstructured sources into a consolidated artifact, requiring file operations, index tracking, and traceability.

If the generated workflow does NOT include external service integration (purely LLM-based consolidation of provided documents), the Security Audit criteria (items 1-6) should be marked as not applicable with explanation.
