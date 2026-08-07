# Meta-Workflow Builder Architecture Standard v1

> **Abstract:** This document defines the universal architecture for meta-workflow
> builders — workflows that generate other workflows. The key insight: the execution
> flow is universal; only the step implementations differ by domain. This standard
> defines the generic skeleton, the step implementation interface, and how to create
> domain-specific builders by implementing the interface.
>
> **Status:** DRAFT
> **Version:** 1.0
> **Effective Date:** 2026-08-07

---

## 1. The Major Insight

### The Problem

Every time we want to build a new domain-specific workflow builder (e.g., "build
workflows for video manuscripts", "build workflows for software applications"),
we face the same architectural questions:

- What's the execution flow?
- How do we validate quality?
- How do we handle review/refine loops?
- How do we ensure completeness?
- How do we gatekeep each layer?

### The Insight

**The execution flow is universal.** Every meta-workflow builder follows the same
pattern:

```
generate_test_criteria → generate_requirements → generate_artifacts → generate_steps 
→ gatekeep_requirements → gatekeep_artifacts → gatekeep_steps → generate_package 
→ gatekeep_package → review_package → refine_package → promote → stepCompletion
```

**What differs is the step implementations** — what each step generates, validates,
and reviews. The skeleton never changes; only the domain-specific logic inside each
step changes.

### The Solution

Abstract the execution flow into a **generic meta-workflow skeleton** and define a
**step implementation interface** that each step must implement. To create a new
domain-specific builder, you just implement the interface for that domain.

This is the **factory pattern** for meta-workflow builders.

---

## 2. The Universal Meta-Workflow Skeleton

### 2.1 Execution Flow

All meta-workflow builders follow this execution flow:

```
Phase 1: Foundation (TDD Loop)
├── generate_test_criteria     — Define acceptance criteria
├── review_test_criteria       — Review criteria quality
└── refine_test_criteria       — Fix issues (conditional)

Phase 2: Requirements
├── generate_requirements      — Define what the domain needs
├── gatekeep_requirements      — Validate requirements completeness
└── [review/refine if needed]

Phase 3: Artifacts
├── generate_artifacts         — Define artifact contract
├── gatekeep_artifacts         — Validate artifact contract
└── [review/refine if needed]

Phase 4: Steps
├── generate_steps             — Define step architecture
├── gatekeep_steps             — Validate step design
└── [review/refine if needed]

Phase 5: Package
├── generate_package           — Generate complete package
├── gatekeep_package           — Validate package completeness
├── review_package             — Comprehensive quality review
└── refine_package             — Fix issues (conditional, loops)

Phase 6: Promotion
├── promote                    — Deploy to target location
└── stepCompletion             — Terminal step
```

### 2.2 Universal Properties

Every meta-workflow builder has these properties:

**Routing:**
- `onsuccess` → next step in sequence
- `on_reject_refine` → refinement loop (review → refine → back to review)
- `exhausted_failure_code` → terminal failure when refine loops exhaust

**Quality Gates:**
- 4 gatekeeper steps (requirements, artifacts, steps, package)
- Each gatekeeper validates a specific layer
- Gatekeepers can REJECT to prevent progression

**Review/Refine Loops:**
- Review step produces detailed findings
- Refine step fixes issues
- Loop returns to review for re-validation
- Exhaustion after N iterations (configurable, default 2)

**Self-Criticism:**
- All generation prompts include self-critic sections
- All review prompts challenge superficial reviews
- All refine prompts verify root cause fixes

### 2.3 What Never Changes

The following are **universal** and never change between domains:

- The execution flow sequence
- The gatekeeper pattern (4 gates)
- The review/refine loop mechanism
- The self-critic pattern
- The TDD loop (generate_test_criteria first)
- The promotion mechanism
- The terminal step (stepCompletion)

### 2.4 What Changes by Domain

The following are **domain-specific** and change for each domain:

- What `generate_requirements` produces (workflow spec vs component schema vs ...)
- What `generate_artifacts` defines (workflow artifacts vs component library vs ...)
- What `generate_steps` designs (workflow steps vs composition resolver vs ...)
- What `generate_package` generates (workflow.toml + prompts vs component schema + resolver + ...)
- What gatekeepers validate (workflow structure vs component schema conformance vs ...)
- What reviewers check (workflow quality vs component quality vs ...)
- What refine steps fix (workflow issues vs component issues vs ...)

---

## 3. Step Implementation Interface

### 3.1 Step Categories

There are 5 categories of steps in the meta-workflow:

1. **Generation Steps** — Produce artifacts (requirements, artifacts, steps, package)
2. **Gatekeeper Steps** — Validate artifacts against criteria
3. **Review Steps** — Comprehensive quality review
4. **Refine Steps** — Fix issues found in review
5. **Promotion Steps** — Deploy the final result

### 3.2 Generation Step Interface

Every generation step must implement this interface:

```python
class GenerationStepInterface:
    """Interface for all generation steps in the meta-workflow."""
    
    # --- Metadata ---
    step_name: str                    # e.g., "generate_requirements"
    step_purpose: str                 # What this step generates
    domain: str                       # Which domain this implements
    
    # --- Input Contract ---
    required_inputs: List[str]        # Artifact keys this step needs
    optional_inputs: List[str]        # Optional artifact keys
    
    # --- Output Contract ---
    produces: List[str]               # Artifact keys this step produces
    optional_produces: List[str]      # Optional artifact keys
    
    # --- Generation Logic ---
    def generate(self, context: dict) -> GenerationResult:
        """
        Generate the artifact for this step.
        
        Args:
            context: Dictionary with all input artifacts and metadata
        
        Returns:
            GenerationResult with:
            - artifact_path: Path to generated artifact
            - artifact_content: The generated content
            - metadata: Generation metadata (timestamp, version, etc.)
        """
        pass
    
    # --- Prompt Template ---
    def get_prompt_template(self) -> str:
        """
        Return the prompt template for LLM-based generation.
        
        The template must include:
        - Objective: What to generate
        - Reference Inputs: What to read (using {ARTIFACT_KEY} placeholders)
        - Domain-Specific Instructions: What the domain requires
        - Output Instructions: Where to write, format requirements
        - Self-Critic: Challenge the generation before completing
        """
        pass
    
    # --- Validation ---
    def validate_output(self, artifact_path: str) -> ValidationResult:
        """
        Validate the generated artifact meets domain requirements.
        
        Returns:
            ValidationResult with:
            - is_valid: bool
            - errors: List[str]
            - warnings: List[str]
        """
        pass
```

### 3.3 Gatekeeper Step Interface

Every gatekeeper step must implement this interface:

```python
class GatekeeperStepInterface:
    """Interface for all gatekeeper steps in the meta-workflow."""
    
    # --- Metadata ---
    step_name: str                    # e.g., "gatekeep_requirements"
    gatekeep_target: str              # Which artifact this gatekeeps
    domain: str                       # Which domain this implements
    
    # --- Input Contract ---
    required_inputs: List[str]        # Artifacts to validate
    validation_criteria: List[str]    # What to check
    
    # --- Output Contract ---
    produces: List[str]               # Gatekeeper report artifact
    
    # --- Gatekeep Logic ---
    def gatekeep(self, context: dict) -> GatekeepResult:
        """
        Validate the target artifact against criteria.
        
        Args:
            context: Dictionary with artifacts and criteria
        
        Returns:
            GatekeepResult with:
            - verdict: APPROVED or REJECTED
            - findings: List[Finding]
            - report_path: Path to gatekeeper report
        """
        pass
    
    # --- Prompt Template ---
    def get_prompt_template(self) -> str:
        """
        Return the prompt template for LLM-based gatekeeping.
        
        The template must include:
        - Objective: What to validate
        - Reference Inputs: What to read
        - Validation Questions: Specific questions to answer
        - Decision Rules: When to APPROVE vs REJECT
        - Self-Critic: Challenge the review before committing
        - Output Instructions: Where to write the report
        """
        pass
    
    # --- Validation Criteria ---
    def get_validation_criteria(self) -> List[ValidationCriterion]:
        """
        Return the list of validation criteria for this gatekeeper.
        
        Each criterion has:
        - criterion_id: Unique identifier
        - description: What to check
        - severity: CRITICAL, MAJOR, MINOR
        - evidence_required: What evidence proves compliance
        """
        pass
```

### 3.4 Review Step Interface

Every review step must implement this interface:

```python
class ReviewStepInterface:
    """Interface for all review steps in the meta-workflow."""
    
    # --- Metadata ---
    step_name: str                    # e.g., "review_package"
    review_scope: str                 # What this review covers
    domain: str                       # Which domain this implements
    
    # --- Input Contract ---
    required_inputs: List[str]        # All artifacts to review
    review_checklist: List[str]       # What to check
    
    # --- Output Contract ---
    produces: List[str]               # Review report artifact
    
    # --- Review Logic ---
    def review(self, context: dict) -> ReviewResult:
        """
        Perform comprehensive quality review.
        
        Args:
            context: Dictionary with all artifacts
        
        Returns:
            ReviewResult with:
            - verdict: APPROVED or REJECTED
            - findings: List[Finding]
            - report_path: Path to review report
            - issues: List[Issue] (if REJECTED)
        """
        pass
    
    # --- Prompt Template ---
    def get_prompt_template(self) -> str:
        """
        Return the prompt template for LLM-based review.
        
        The template must include:
        - Objective: What to review
        - Reference Inputs: What to read
        - Review Checklist: Comprehensive list of checks
        - Decision Rules: When to APPROVE vs REJECT
        - Self-Critic: Challenge superficial reviews
        - Output Instructions: Report structure and format
        """
        pass
    
    # --- Review Checklist ---
    def get_review_checklist(self) -> List[ReviewCheckItem]:
        """
        Return the comprehensive review checklist.
        
        Each check item has:
        - check_id: Unique identifier
        - category: e.g., "structure", "consistency", "quality"
        - description: What to check
        - pass_criteria: What constitutes a pass
        - evidence_required: What evidence proves compliance
        """
        pass
```

### 3.5 Refine Step Interface

Every refine step must implement this interface:

```python
class RefineStepInterface:
    """Interface for all refine steps in the meta-workflow."""
    
    # --- Metadata ---
    step_name: str                    # e.g., "refine_package"
    refine_scope: str                 # What this refine fixes
    domain: str                       # Which domain this implements
    
    # --- Input Contract ---
    required_inputs: List[str]        # Review report + artifacts to fix
    refinement_rules: List[str]       # How to fix issues
    
    # --- Output Contract ---
    produces: List[str]               # Updated artifacts
    
    # --- Refine Logic ---
    def refine(self, context: dict) -> RefineResult:
        """
        Fix issues identified in review.
        
        Args:
            context: Dictionary with review report and artifacts
        
        Returns:
            RefineResult with:
            - fixes_applied: List[Fix]
            - updated_artifacts: List[str]
            - summary: What was fixed
        """
        pass
    
    # --- Prompt Template ---
    def get_prompt_template(self) -> str:
        """
        Return the prompt template for LLM-based refinement.
        
        The template must include:
        - Objective: What to fix
        - Reference Inputs: Review report + current artifacts
        - Refinement Rules: How to fix each type of issue
        - Constraints: What NOT to change
        - Self-Critic: Verify root cause fixes, not symptoms
        - Output Instructions: Update artifacts in-place
        """
        pass
    
    # --- Refinement Rules ---
    def get_refinement_rules(self) -> List[RefinementRule]:
        """
        Return the rules for fixing issues.
        
        Each rule has:
        - rule_id: Unique identifier
        - issue_type: What type of issue this fixes
        - fix_strategy: How to fix it
        - constraints: What to preserve
        """
        pass
```

### 3.6 Promotion Step Interface

Every promotion step must implement this interface:

```python
class PromotionStepInterface:
    """Interface for all promotion steps in the meta-workflow."""
    
    # --- Metadata ---
    step_name: str                    # e.g., "promote"
    promotion_target: str             # Where to promote (e.g., workflows/, docs/)
    domain: str                       # Which domain this implements
    
    # --- Input Contract ---
    required_inputs: List[str]        # Artifacts to promote
    
    # --- Output Contract ---
    produces: List[str]               # Promotion report
    
    # --- Promotion Logic ---
    def promote(self, context: dict) -> PromotionResult:
        """
        Deploy artifacts to target location.
        
        Args:
            context: Dictionary with artifacts and target info
        
        Returns:
            PromotionResult with:
            - promoted_files: List[str]
            - target_location: str
            - promotion_report: str
        """
        pass
```

---

## 4. Domain Implementation Guide

### 4.1 Creating a New Domain Builder

To create a new domain-specific meta-workflow builder:

**Step 1: Define the Domain**

Create a domain specification document:

```markdown
# Domain: {domain_name}

## Purpose
What does this domain build?

## Component Schema (if composition-based)
What are the component types and their properties?

## Output Format
What does the final deliverable look like?

## Quality Requirements
What makes a good output?
```

**Step 2: Implement Step Interfaces**

For each step in the meta-workflow, implement the interface:

```python
# Example: Traditional Workflow Domain
class TraditionalWorkflowGenerationStep(GenerationStepInterface):
    step_name = "generate_requirements"
    domain = "traditional_workflow"
    
    def generate(self, context):
        # Generate workflow requirements (workflow.toml structure, step sequence, etc.)
        pass
    
    def get_prompt_template(self):
        # Return prompt that instructs LLM to generate workflow requirements
        pass

# Example: Composition System Domain
class CompositionSystemGenerationStep(GenerationStepInterface):
    step_name = "generate_requirements"
    domain = "composition_system"
    
    def generate(self, context):
        # Generate component schema, composition format, output format
        pass
    
    def get_prompt_template(self):
        # Return prompt that instructs LLM to generate composition system
        pass
```

**Step 3: Register Step Implementations**

Create a step registry for the domain:

```python
DOMAIN_STEP_REGISTRY = {
    "traditional_workflow": {
        "generate_test_criteria": TraditionalTestCriteriaGenerationStep(),
        "generate_requirements": TraditionalRequirementsGenerationStep(),
        "generate_artifacts": TraditionalArtifactsGenerationStep(),
        "generate_steps": TraditionalStepsGenerationStep(),
        "gatekeep_requirements": TraditionalRequirementsGatekeeper(),
        "gatekeep_artifacts": TraditionalArtifactsGatekeeper(),
        "gatekeep_steps": TraditionalStepsGatekeeper(),
        "generate_package": TraditionalPackageGenerationStep(),
        "gatekeep_package": TraditionalPackageGatekeeper(),
        "review_package": TraditionalPackageReviewStep(),
        "refine_package": TraditionalPackageRefineStep(),
        "promote": TraditionalPromotionStep(),
    },
    "composition_system": {
        "generate_test_criteria": CompositionTestCriteriaGenerationStep(),
        "generate_requirements": CompositionRequirementsGenerationStep(),
        # ... etc
    }
}
```

**Step 4: Create the Workflow Package**

Generate the workflow package (workflow.toml, prompts, actions.py) using the
step implementations. The execution flow is the same; only the step implementations
differ.

### 4.2 Domain Implementation Checklist

- [ ] Define domain specification (purpose, component schema, output format)
- [ ] Implement all generation step interfaces for the domain
- [ ] Implement all gatekeeper step interfaces for the domain
- [ ] Implement review step interface for the domain
- [ ] Implement refine step interface for the domain
- [ ] Implement promotion step interface for the domain
- [ ] Create step registry mapping step names to implementations
- [ ] Generate workflow package using the implementations
- [ ] Test with the meta-workflow skeleton
- [ ] Validate generated workflows work correctly

---

## 5. Reference Implementations

### 5.1 Traditional Workflow Domain (workflow_builder_v1)

**Domain:** Builds traditional workflow packages (workflow.toml, prompts, actions.py)

**Step Implementations:**
- `generate_requirements` → Produces workflow requirements (step sequence, routing, artifacts)
- `generate_artifacts` → Produces artifact contract (artifact keys, paths, types)
- `generate_steps` → Produces step architecture (step details, coder roles, validation)
- `generate_package` → Produces complete workflow package (workflow.toml, prompts, actions.py, README)
- Gatekeepers validate workflow structure, artifact consistency, step routing
- Review checks workflow quality, spec fulfillment, prompt clarity
- Refine fixes issues found in review

**Reference:** Existing `workflow_builder_v1` workflow.

### 5.2 Composition System Domain (workflow_builder_v2)

**Domain:** Builds composition-based workflow packages (component schemas, composition resolvers, output assemblers)

**Step Implementations:**
- `generate_requirements` → Produces component schema, composition format, output format
- `generate_artifacts` → Produces artifact contract (component library, compositions, outputs)
- `generate_steps` → Produces step architecture (scanning, resolution, assembly, review)
- `generate_package` → Produces complete composition workflow (component validator, composition resolver, output assembler, prompts)
- Gatekeepers validate component schema conformance, composition format, output structure
- Review checks component quality, composition resolution, output completeness
- Refine fixes issues found in review

**Reference:** To be implemented as `workflow_builder_v2`.

### 5.3 Future Domains

**Software Application Builder:**
- Components: ui_page, api_endpoint, data_model, service_module, integration
- Output: Application blueprint with UI, API, data model, services

**Podcast Production Builder:**
- Components: segment, music_bed, ad_slot, intro_outro
- Output: Complete podcast episode script with timing and cues

**Content Creation Builder:**
- Components: article_section, tone, visual_style, cta
- Output: Complete content package (article, social posts, visuals)

---

## 6. The Factory Pattern

### 6.1 The Meta-Meta-Workflow

This architecture enables a **factory pattern** for generating meta-workflow builders:

**Input:** Domain specification (component types, composition rules, output format)

**Process:**
1. Parse domain specification
2. Select appropriate step implementations (or generate new ones)
3. Compose into a complete meta-workflow builder
4. Generate workflow package for the builder

**Output:** A complete meta-workflow builder for the domain

### 6.2 Factory Workflow

The factory itself is a meta-meta-workflow:

```
Input: Domain Spec
  ↓
[Factory Workflow]
  ├── Analyze domain requirements
  ├── Select/generate step implementations
  ├── Compose into meta-workflow builder
  ├── Generate workflow package
  ├── Review and refine
  └── Promote the builder
  ↓
Output: Domain-Specific Meta-Workflow Builder
```

### 6.3 Recursive Application

This pattern can be applied recursively:

- **Level 0:** The factory (builds builders)
- **Level 1:** Domain-specific builders (build workflows)
- **Level 2:** Generated workflows (build deliverables)

Each level uses the same meta-workflow skeleton with different step implementations.

---

## 7. Migration Path

### 7.1 From workflow_builder_v1 to v2

**Option 1: Enhancement**
- Add composition system step implementations to v1
- v1 can build both traditional and composition workflows
- Single builder, multiple domain support

**Option 2: Separate v2**
- Create workflow_builder_v2 with composition system implementations
- v1 continues for traditional workflows
- v2 for composition-based workflows
- Both share the same meta-workflow skeleton

**Option 3: Full Refactor**
- Extract the meta-workflow skeleton into a core module
- v1 and v2 become thin wrappers with domain-specific step implementations
- New domains just implement the step interface

### 7.2 Recommended Path

**Start with Option 2 (separate v2)** to validate the architecture, then move to
**Option 3 (full refactor)** once the pattern is proven.

---

## 8. Governance

### 8.1 Step Interface Evolution

The step implementation interface is versioned separately from domain implementations.

**Backward compatible changes:**
- Adding optional methods to the interface
- Adding new step categories
- Extending result types

**Breaking changes:**
- Changing required method signatures
- Removing methods
- Changing result type structure

### 8.2 Domain Implementation Quality

All domain implementations must:

- Implement all required methods in the interface
- Include comprehensive prompt templates with self-critic
- Provide validation criteria for gatekeepers
- Provide review checklists for reviewers
- Include refinement rules for refiners
- Pass integration tests with the meta-workflow skeleton

---

## 9. References

- **Composition System Standard:** `docs/repo/workflow_builder/standards/COMPOSITION_SYSTEM_STANDARD.md`
- **workflow_builder_v1:** `workflows/workflow_builder_v1/`
- **Workflow Creation Guide:** `docs/repo/workflow_builder/current/WORKFLOW_CREATION_GUIDE.md`

---

## Appendix A: Glossary

**Meta-Workflow:** A workflow that generates other workflows.

**Meta-Workflow Skeleton:** The universal execution flow shared by all meta-workflows.

**Step Implementation:** Domain-specific logic for a step in the meta-workflow.

**Step Interface:** The contract that all step implementations must follow.

**Domain:** A specific problem space (traditional workflows, composition systems, software applications, etc.).

**Factory Pattern:** Using the composition system to build meta-workflow builders.

---

## Appendix B: Step Implementation Template

```python
"""
Template for implementing a domain-specific step.
"""

class MyDomainGenerationStep(GenerationStepInterface):
    """Generate {artifact_name} for {domain_name}."""
    
    step_name = "generate_{artifact_name}"
    step_purpose = "Generate {artifact_description}"
    domain = "{domain_name}"
    
    required_inputs = ["{INPUT_KEY_1}", "{INPUT_KEY_2}"]
    optional_inputs = ["{OPTIONAL_KEY}"]
    produces = ["{OUTPUT_KEY}"]
    optional_produces = []
    
    def generate(self, context: dict) -> GenerationResult:
        """Generate the artifact."""
        # Read inputs from context
        input_1 = context["{INPUT_KEY_1}"]
        
        # Generate output
        output_content = self._generate_content(input_1)
        
        # Write to file
        output_path = context["{OUTPUT_KEY}"]
        write_file(output_path, output_content)
        
        return GenerationResult(
            artifact_path=output_path,
            artifact_content=output_content,
            metadata={"generated_at": now(), "domain": self.domain}
        )
    
    def _generate_content(self, input_1):
        """Domain-specific generation logic."""
        # Implement domain logic here
        pass
    
    def get_prompt_template(self) -> str:
        """Return prompt template for LLM-based generation."""
        return """
        Objective
        {Describe what to generate}
        
        Reference Inputs
        - Read {{INPUT_KEY_1}} for {description}
        - Read {{INPUT_KEY_2}} for {description}
        
        Domain-Specific Instructions
        {Domain-specific rules and constraints}
        
        Output Instructions
        - Write to {{OUTPUT_KEY}}
        - Format: {format requirements}
        - Include: {required sections}
        
        Self-Critic
        {Challenge the generation before completing}
        """
    
    def validate_output(self, artifact_path: str) -> ValidationResult:
        """Validate the generated artifact."""
        # Implement validation logic
        errors = []
        warnings = []
        
        # Check required sections
        # Check format compliance
        # Check domain constraints
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

---

**End of Standard**
