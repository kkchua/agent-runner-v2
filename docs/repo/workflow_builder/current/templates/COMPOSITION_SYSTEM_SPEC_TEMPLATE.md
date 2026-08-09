# Composition System Specification: {Domain Name}

> Save to `docs/repo/workflow_builder/specs/{domain_name}_v1.md`.
> The composition system builder (workflow_builder_v2) reads this document
> and generates a complete workflow package that implements this composition
> system.
>
> **Key principle:** Describe the three-layer architecture — what the
> building blocks are (Layer 1), how they snap together (Layer 2), and
> what the assembled deliverable looks like (Layer 3). The builder infers
> the operational workflow (scan, plan, generate, review, refine) and
> generates the complete workflow package.
>
> **Companion documents:**
> - [COMPOSITION_SYSTEM_STANDARD.md](../COMPOSITION_SYSTEM_STANDARD.md) -- the universal pattern
> - [BUILDER_REQUIREMENTS.md](../BUILDER_REQUIREMENTS.md) -- what the builder enforces

---

## 1. Domain Overview

**Domain name:** `{domain_name}`
**Label:** {Human-readable domain label}
**Job prefix:** `XXXX`
**Description:** {One sentence: what this composition system produces}

### 1.1 Purpose

{What problem does this composition system solve? What triggers it?
What is the expected outcome?}

### 1.2 Domain Context

{Brief context about the domain. What are the deliverables used for?
What downstream workflows consume the output?}

---

## 2. Component Schema (Layer 1)

The component library is the set of standardized building blocks for
this domain. Each component has a unique ID and conforms to a type-specific
schema.

### 2.1 Component Types

List all component types this domain recognizes:

| Component Type | Purpose | Required? | Cardinality |
|---|---|---|---|
| `{type_1}` | {What this component represents} | Yes/No | Singleton / Ordered list / Unordered set |
| `{type_2}` | {What this component represents} | Yes/No | Singleton / Ordered list / Unordered set |

### 2.2 Common Properties

All components share these properties (in addition to type-specific ones):

| Property | Type | Required | Description |
|---|---|---|---|
| `component_id` | string | Yes | Unique identifier (format: `{type}-{descriptor}-{seq}`) |
| `component_type` | enum | Yes | One of the types listed in 2.1 |
| `name` | string | Yes | Human-readable display name |
| `version` | string | Yes | Semantic version (MAJOR.MINOR.PATCH) |
| `description` | string | Yes | What this component does and when to use it |

### 2.3 Type-Specific Properties

For each component type, define its type-specific properties:

#### Type: `{type_1}`

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `{property}` | {type/enum} | Yes/No | {Description} | {Example value} |

#### Type: `{type_2}`

| Property | Type | Required | Description | Example |
|---|---|---|---|---|
| `{property}` | {type/enum} | Yes/No | {Description} | {Example value} |

{Repeat for each component type}

### 2.4 Component File Format

Components are stored as {markdown/YAML/JSON} files with this structure:

```
{Example component file showing the format}
```

### 2.5 Validation Rules

Components must pass these checks:

- **Required fields present:** {List required common + type-specific fields}
- **Valid component_type:** Must be one of the types in 2.1
- **Unique component_id:** No duplicates within the library
- **Type-specific schema conformance:** All required properties for the declared type must be present
- {Add domain-specific validation rules}

---

## 3. Composition Format (Layer 2)

Compositions are declarative assembly instructions that reference
components by ID and specify how they fit together.

### 3.1 Composition Structure

Compositions are {YAML/JSON/markdown} files with this structure:

| Field | Type | Required | Description |
|---|---|---|---|
| `composition_id` | string | Yes | Unique identifier for this composition |
| `name` | string | Yes | Human-readable display name |
| `target_metadata` | object | Yes | Domain-specific metadata about the target deliverable |
| `component_bindings` | object | Yes | Assembly instructions mapping binding names to component references |

### 3.2 Binding Rules

| Binding Name | Component Type | Cardinality | Required? | Description |
|---|---|---|---|---|
| `{binding_1}` | `{type_1}` | Singleton | Yes | {What this binding represents} |
| `{binding_2}` | `{type_2}` | Ordered list | Yes | {What this binding represents} |

### 3.3 Override Mechanism

Compositions can override component properties per-binding:

```yaml
{Example showing override syntax}
```

**Override rules:**
- Overrides must conform to the component type's schema
- Override wins on conflict with base component properties
- {Add domain-specific override rules}

### 3.4 Placeholder Resolution

Placeholders (`{placeholder_name}`) in component properties are resolved
from external data sources:

| Data Source | Fields Provided | Required? |
|---|---|---|
| `{source_1}` | {field_1, field_2, ...} | Yes |
| `{source_2}` | {field_1, field_2, ...} | No |

**Resolution rules:**
- Unresolved placeholders are flagged as `{UNRESOLVED: field_name}`
- {Add domain-specific resolution rules}

### 3.5 Example Composition

```yaml
{Complete example composition showing all binding types, overrides, and placeholders}
```

---

## 4. Output Format (Layer 3)

The resolved output is a complete, self-contained deliverable with all
component references expanded, overrides applied, and placeholders filled.

### 4.1 Output Structure

The output is a {markdown/YAML/JSON} file with these sections:

| Section | Source | Description |
|---|---|---|
| {Section 1} | {Which component/binding} | {What this section contains} |
| {Section 2} | {Which component/binding} | {What this section contains} |

### 4.2 Resolution Rules

- **All references expanded:** Every component_id is replaced with full component content
- **Overrides applied:** Override properties merged into base component properties
- **Placeholders resolved:** Every {placeholder} replaced with data source value
- **Self-contained:** Output contains all information needed for downstream consumption
- {Add domain-specific resolution rules}

### 4.3 Quality Requirements

- **No dangling references:** All component_ids resolved
- **No unresolved placeholders:** All placeholders filled or explicitly flagged
- **Schema conformance:** Overrides applied correctly
- **Completeness:** All required sections present
- {Add domain-specific quality requirements}

### 4.4 Example Output

```markdown
{Skeleton of what a resolved output looks like, showing section structure}
```

---

## 5. Operational Requirements

High-level description of how the workflow should process this composition
system. The builder designs the detailed step sequence.

### 5.1 Workflow Phases

| Phase | Purpose |
|---|---|
| **Scan** | Discover and validate all components in the library |
| **Plan** | Read compositions, resolve component references, identify overrides and placeholders |
| **Generate** | For each composition, resolve all components and assemble the output |
| **Review** | Quality review of generated outputs |
| **Refine** | Fix issues found in review (conditional) |

### 5.2 Input Artifacts

| Artifact Key | Description | Required? |
|---|---|---|
| `COMPONENT_LIBRARY_DIR` | Directory containing component files | Yes |
| `COMPOSITIONS_DIR` | Directory containing composition definitions | Yes |
| `DATA_SOURCE_DIR` | Directory containing placeholder resolution data | Yes |

### 5.3 Output Artifacts

| Artifact Key | Description |
|---|---|
| `COMPONENT_INVENTORY_FILE` | Catalog of all discovered components with validation status |
| `RESOLUTION_PLAN_FILE` | Plan mapping compositions to resolved components |
| `OUTPUT_FILE` | The assembled deliverable |
| `REVIEW_FILE_SUGGESTED` | Quality review document |

### 5.4 Action Steps (if needed)

{Describe any custom actions needed beyond the standard scan/plan/generate
pattern. For example: API calls, file format conversions, external service
integrations. If no custom actions are needed, state "No custom actions."}

### 5.5 Domain-Specific Requirements

{Any additional requirements specific to this domain: performance constraints,
error handling preferences, platform-specific considerations, etc.}

---

## 6. References

- **Composition System Standard:** `docs/repo/workflow_builder/current/COMPOSITION_SYSTEM_STANDARD.md`
- **Related workflows:** {List any related workflows or prior art}
- **Example components:** {Path to example component files, if they exist}
- **Example compositions:** {Path to example composition files, if they exist}

---

**End of Specification**
