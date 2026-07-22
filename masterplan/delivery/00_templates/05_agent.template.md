# 🤖 Agent Template

## 📌 Metadata
- Doc Type: 05_agent
- Template Version: v1
- Agent ID: AGENT-{{AGENT_NAME_UPPERCASE}}
- Agent Name: {{AGENT_NAME}}
- Role: planner | decomposer | executor | reviewer | memory-manager | other
- Version: v1
- Status: active | draft | retired

---

## 🎯 Purpose
Describe the responsibility and mission of this agent.

---

## 📥 Inputs
### Supported Document Types
- 

### Required Input Fields
- 

### Optional Inputs
- 

---

## 📤 Outputs
- Output Document Type:
- Output Template File:
- Output Folder:
- Expected Naming Convention:

---

## 🧠 Behavior Rules
- Must follow template strictly.
- Must not invent missing facts.
- Must preserve linked IDs and references.
- Must output in markdown only unless otherwise specified.

Add any role-specific rules below:
- 

---

## 🧾 Prompt Contract
### System Prompt
{{SYSTEM_PROMPT}}

### Input Contract
{{INPUT_CONTRACT}}

### Output Contract
{{OUTPUT_CONTRACT}}

---

## 🔄 Execution Flow
1. Receive input document.
2. Validate required fields.
3. Read linked references.
4. Generate output using the correct template.
5. Save output to the correct folder.
6. Return status and summary.

---

## ⚠️ Constraints
- Naming convention constraints:
- Security / compliance constraints:
- Schema constraints:
- Review / approval constraints:

---

## 🔗 References
- Related templates:
- Related workflows:
- Related memory docs:

---

## 📝 Notes
- 
