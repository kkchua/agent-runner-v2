---
codename: "agentic_workflow_builder"
title: "Agentic Workflow Builder"
version: "1.0"
author: "kengk"
date: "2026-08-10"
description: "Builds executable agent-runner-v2 workflows from JiMeng/Dreamai-style agentic workflow markdown definitions."
---

# Agentic Workflow Builder

## Overview

The Agentic Workflow Builder transforms JiMeng/Dreamai-style agentic workflow markdown files into executable agent-runner-v2 workflow packages. It analyzes prompt-based workflow definitions (with roles, tools, multi-step flows, configuration cards) and produces workflows that can execute those agentic patterns.

**Target use case:** Convert JiMeng agentic workflows (e.g., "电影广告全能导演", "世界观美术设定", "治愈系原创IP孵化助手") into agent-runner-v2 workflows that can be executed via daemon or CLI.

**High-level workflow:** Parse JiMeng markdown → Infer composition spec → Map to agent-runner-v2 concepts → Generate workflow package → Produce runtime implementation doc

## Input Artifacts

### JiMeng Agentic Workflow Markdown
- Format: Rich Markdown with YAML frontmatter (name, description)
- Location: `docs/repo/agentic_workflow_builder/jimeng-workflows/`
- Structure: Role definition, tool specifications, multi-step execution flow, configuration cards, quality criteria, constraints
- Content: Prompt-based workflow definitions describing roles (导演, 助手), tools (generate_form_for_info_collection, text2image, multi_modal2video), step-by-step flows with configuration cards, output specifications
- Encoding: UTF-8

The builder reads the JiMeng markdown from `docs/repo/agentic_workflow_builder/jimeng-workflows/` and produces an executable workflow that follows the same logic but uses agent-runner-v2 infrastructure.

## Output Artifacts

The generator MUST produce **at least 3 different types of output artifacts** from the JiMeng markdown analysis. The LLM infers what these output types should be based on the markdown structure.

**Sample examples** of output types the generator can produce:

### Example Type 1: Workflow Package
- workflow.toml with step definitions
- context_extensions.py with artifact keys
- actions.py with tool integrations
- prompts/ directory with step prompts
- README.md documenting the workflow

### Example Type 2: Input Capture Specification
- What data to capture from users (images, text, configuration)
- Input formats and validation rules
- How to collect configuration parameters

### Example Type 3: Action Integration Specification
- Which actions to call (Agnes API for image/video, file operations, etc.)
- Action parameters and expected responses
- Error handling and retry logic

The LLM decides the actual output artifact types, their names, structure, and content based on what it discovers in the JiMeng markdown. The examples above are guidance, not requirements.

## Transformation Logic

The transformation process involves:

1. **Parse JiMeng markdown** — Extract role definitions, tool specifications, step flow, input requirements, output specifications
2. **Identify input data** — Determine what data needs to be captured from users (images, text, configuration parameters)
3. **Identify actions** — Determine what actions need to be called (Agnes API for image/video generation, file operations, etc.)
4. **Design prompts** — Create LLM prompts for each step that will generate the expected output artifacts
5. **Generate workflow package** — Produce workflow.toml, context_extensions.py, actions.py, prompts/

## Constraints

- **Executable output** — Generated workflows must be executable via agent-runner-v2 daemon or CLI
- **Agnes API for image/video** — If the JiMeng workflow requires image or video generation, the generated workflow MUST use Agnes API (hybrid: some via skills, some via direct API calls)
- **Input capture** — Generated workflows must capture all necessary input data defined in JiMeng markdown
- **Action integration** — Generated workflows must integrate all tools/actions defined in JiMeng markdown
- **Output fidelity** — Generated workflows must produce the same output artifacts as defined in JiMeng markdown
- **No information loss** — All JiMeng markdown content must be represented in the generated workflow

## Extension Points

The generator should support:
- **Custom tool integrations** — Add new tool actions beyond Agnes API (e.g., other AI APIs, file operations)
- **Custom interaction patterns** — Add new user interaction patterns beyond approval gates
- **Multi-language support** — Handle JiMeng markdown in Chinese, English, or mixed languages
- **Workflow composition** — Generated workflows can reference other generated workflows as sub-workflows
