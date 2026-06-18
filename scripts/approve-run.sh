#!/usr/bin/env bash
# Approve or reject a run that is awaiting human action.
#
# Edit the variables below, then run this script from anywhere.
#
# Required:
#   RUN_ID — the run UUID shown in the submit response or run listing

set -euo pipefail

# RUN_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

RUN_ID="10a4662b-444b-4d7d-9bfc-e25da9a7c465"

# Approve:
ukbe-run-agent approve "$RUN_ID"

# Reject (uncomment and comment out the approve line above):
# ukbe-run-agent approve "$RUN_ID" --reject --feedback "Output does not meet requirements"
