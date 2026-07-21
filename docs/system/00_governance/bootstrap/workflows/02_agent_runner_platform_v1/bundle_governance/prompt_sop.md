# Prompt SOP

1. Every prompt must state that the workflow belongs to Layer 2 and targets agent-runner-v2.
2. Every prompt must distinguish permanent platform standards from temporary evidence artifacts.
3. Generate prompts must treat `masterplan/LAYER_ARCHITECTURE_MASTERPLAN.md` and `masterplan/LAYER2_PLATFORM_CORE_SPECIFICATION.md` as read-only authority inputs.
4. Generate prompts must treat source code modules (runtime context, coder registry, constants, daemon, etc.) as read-only reference — describe them, do not rewrite them.
5. Review and audit prompts must require direct citations to offending text when rejecting content.
6. Refine prompts must prefer removal, reclassification, or rejection over polishing wrong-scope content.
7. No prompt may instruct the model to redefine Layer 1 governance, generate Layer 3 bundle definitions, or perform automated codebase scanning.
8. Prompt edits that change scope or output contracts must be reviewed against the bundle governance package before acceptance.
