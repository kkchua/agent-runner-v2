# Layer 1 Prompt Layout

## Standard Skeleton

Use this layout when creating or revising prompts for this workflow:

```text
<Role or Purpose>

Read first / Inputs:
- ...

Scope rules:
- ...

Required outcomes:
- ...

Reject or remove if:
- ...

Before returning:
- ...

Required JSON schema:
{
  ...
}
```

## Notes

- Use short headings and stable wording.
- Put hard constraints before examples.
- Keep output schema last.
- Do not rely on implied policy. State it directly.
- If a rule is critical enough to fail a job, it must appear in both prompt
  text and deterministic validation where possible.
