# Agent-Runner-v2 Future Improvements

This document tracks potential enhancements and architectural improvements for future consideration.

---

## Prompt Security & Guardrails

**Priority:** High  
**Status:** Not Started

### Description
Add security audit and guardrails to prompts before LLM execution to prevent:
- Prompt injection attacks
- Sensitive data leakage
- Unauthorized operations
- Content policy violations
- Rate limit/quota abuse

### Potential Implementation
- Pre-execution prompt analyzer/validator
- Pattern matching for known attack vectors
- Sensitive data detection (API keys, credentials, PII)
- Configurable security policies per workflow/step
- Audit logging of prompt content
- Rate limiting middleware

### Files to Modify
- `agent_runner_v2/step_runner.py` - Add pre-execution validation hook
- `agent_runner_v2/coder_adapters.py` - Add security checks before invocation
- New module: `agent_runner_v2/prompt_guardrails.py`

---

## Pluggable Workflow Bundle Architecture

**Priority:** High  
**Status:** Not Started

### Description
Redesign the workflow system from monolithic `template_groups.py` to a pluggable bundle/plugin architecture where users can choose which bundles to install.

### Current Problem
- All workflows defined in single `template_groups.py` file
- No modularity or separation of concerns
- Difficult to share/reuse workflows across projects
- No version management for workflow definitions
- Hard to extend without modifying core code

### Proposed Solution
Each bundle package contains:
- Workflow definitions (steps, configs, routing rules)
- Action implementations (deterministic runner actions)
- Prompt templates
- Documentation templates
- Validation rules
- Metadata (version, dependencies, author)

### Features
- Bundle discovery and installation mechanism
- Version management and dependency resolution
- Hot-swappable bundles without code changes
- Bundle marketplace/repository
- Conflict resolution when multiple bundles define same workflow
- Bundle activation/deactivation

### Implementation Approach
1. Define bundle package structure (directory layout, metadata format)
2. Create bundle loader/installer
3. Migrate existing workflows to bundle format
4. Update workflow resolution to search installed bundles
5. Add bundle management CLI commands

### Files to Create/Modify
- New: `agent_runner_v2/bundle_manager.py` - Bundle lifecycle management
- New: `agent_runner_v2/bundle_loader_v2.py` - Enhanced bundle loading
- New: Bundle package template/skeleton
- Modify: `agent_runner_v2/run_agent.py` - Bundle-aware workflow resolution
- Modify: `agent_runner_v2/runtime_context.py` - Multi-bundle support

---

## Additional Ideas

*(Add more items here as they come up)*
