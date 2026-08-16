# Review And Audit Contract

Minimum review obligations:

- reject Layer 1 governance redefinition or contradiction
- reject Layer 3 bundle-specific drift presented as platform-wide rules
- reject missing mandatory permanent documents
- reject platform identity missing or unclear
- reject metadata and authority mismatches
- reject evidence artifacts presented as permanent platform standards
- cite offending text directly

Minimum audit obligations:

- verify the final accepted set still belongs in Layer 2
- verify Layer 1 governance was inherited correctly, not redefined
- verify no bundle-specific content was normalized into platform standards
- verify platform identity is clear throughout
- verify the runtime model accurately reflects the platform source code
- verify the bundle authoring contract is precise enough for Layer 3 authors

Defect classes:

- `layer1_redefinition`
- `layer3_bundle_drift`
- `platform_identity_missing`
- `metadata_noncompliance`
- `missing_required_structure`
- `forbidden_operational_content`
- `wrong_document_inventory`
- `evidence_as_standard`

Routing:

- fixable defects route to refine (metadata omission, missing section, weak wording, removable scope leakage)
- conceptual layer mismatch routes to fail (layer1_redefinition, layer3_bundle_drift)
- wrong document inventory routes to fail
- platform identity missing routes to fail if systemic, refine if isolated
- evidence presented as permanent standard routes to fail
