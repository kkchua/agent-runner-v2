#!/usr/bin/env bash
# Approve or reject a run that is awaiting human action.
#
# Edit the variables below, then run this script from anywhere.
#
# Required:
#   RUN_ID — the run UUID shown in the submit response or run listing

set -euo pipefail

RUN_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Approve:
ukbe-run-agent approve "$RUN_ID"

# Reject (uncomment and comment out the approve line above):
# ukbe-run-agent approve "$RUN_ID" --reject --feedback "Output does not meet requirements"
