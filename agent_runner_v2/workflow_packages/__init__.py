# workflow_packages — Pluggable workflow bundle system for agent-runner-v2
#
# Each workflow is a self-contained directory under workflows/<name>/
# with a workflow.toml manifest, prompts/, and optional context_extensions.py.
# The registry discovers these packages and adapts them into the
# TEMPLATE_GROUPS dict format the runner already consumes.
