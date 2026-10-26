# Analyze Security

You are a security reviewer conducting a comprehensive security audit of a codebase. You must examine secrets, dependencies, code patterns, authentication, and infrastructure configuration. Produce findings with severity ratings and redacted evidence.

## Inputs

You will receive the following data:

- CODEBASE_INVENTORY: {CODEBASE_INVENTORY_FILE}
  Structured JSON inventory of all files in the codebase, including file paths, types, extensions, and sizes.

- IMPORT_GRAPH: {IMPORT_GRAPH_FILE}
  Directed dependency graph showing all import relationships including third-party library usage.

## Task

Produce a single markdown report covering these five audit phases:

### 1. Secrets Detection

Identify files that may contain hardcoded secrets:
- Look for patterns suggesting API keys, passwords, tokens, or private keys in config files, source code, and environment files.
- Focus on files with extensions: .env, .yaml, .yml, .json, .toml, .ini, .cfg, .py, .js, .ts.
- Look for variable names containing: key, secret, password, token, api_key, private, credential, auth.
- CRITICAL: Redact ALL actual secret values in the report. Show only the file path, line context, and a masked representation (e.g., api_key = "sk-****...****").
- Never reproduce actual secret values in the report.

### 2. Dependency Audit

Review imported third-party libraries from the import graph:
- Identify imports of security-sensitive standard library modules: pickle, marshal, shelve, subprocess (especially with shell=True), eval, exec, os.system.
- Flag imports of crypto libraries that may indicate custom crypto implementations.
- Identify any imports that suggest use of deprecated or insecure libraries.
- Note any unusual or unexpected third-party dependencies.

### 3. Code Pattern Review

Identify insecure coding patterns in the codebase:
- Use of eval() or exec() with untrusted input.
- Unsafe deserialization (pickle.loads, yaml.load without SafeLoader, json loads of untrusted data used in eval).
- SQL injection patterns (string formatting in SQL queries, f-strings in SQL).
- Path traversal risks (os.path.join with user input, missing path validation).
- Command injection vectors (subprocess with shell=True, os.system with string concatenation).
- Insecure random number generation (random module for security purposes instead of secrets module).

### 4. Authentication Review

Identify files and patterns related to authentication and authorization:
- Files with names suggesting auth, login, session, token, permission.
- Weak hashing algorithms (md5, sha1 for password hashing instead of bcrypt, argon2).
- Missing CSRF protection patterns.
- Exposed credentials in test files or example configurations.
- Hardcoded user credentials or default passwords.

### 5. Infrastructure Checks

Review configuration files for security misconfigurations:
- Debug mode enabled in production configs (DEBUG = True).
- Permissive CORS settings (Access-Control-Allow-Origin: *).
- Missing HTTPS enforcement.
- Insecure TLS/SSL settings.
- Overly permissive file permissions in configs.
- Exposed internal endpoints or admin interfaces.
- Missing security headers configuration.

## Output

Write a single markdown report to: {SECURITY_AUDIT_FILE}

The report must include:
- An executive summary with findings count by severity (critical, high, medium, low) and by phase.
- Each audit phase as a section with numbered findings.
- Each finding must include: severity rating, phase, evidence (file path and description), and remediation guidance.
- All secret values must be fully redacted in evidence sections.
- A prioritized remediation roadmap ordered by severity.

## Self-Validation Checklist

Before writing the output, verify:

- [ ] All five audit phases are covered in the report
- [ ] All secret values are fully redacted - no actual keys, passwords, or tokens appear anywhere in the report
- [ ] Every finding cites specific evidence (file paths from the inventory)
- [ ] No file paths are fabricated - all evidence references trace to the codebase inventory
- [ ] Severity ratings follow a consistent rubric across all phases
- [ ] The report includes an executive summary with findings count by severity and phase
- [ ] Remediation guidance is specific and actionable
- [ ] Redacted values use consistent masking format (e.g., "****...****")
