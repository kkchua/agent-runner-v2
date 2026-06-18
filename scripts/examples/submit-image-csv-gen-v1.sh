#!/usr/bin/env bash
# Submit a run for: image_csv_gen_v1
#
# Purpose: Takes a folder of images, extracts descriptions, generates a CSV prompt file,
#          reviews it, and produces IMAGE_CSV_JSON + IMAGE_CSV_CSV.
#
# Edit the variables below, then run this script from anywhere.
#
# Required inputs:
#   PROJECT_ROOT — absolute path to the repo you are submitting work for
#   IMAGE_FOLDER — path to the folder containing images, relative to PROJECT_ROOT

set -euo pipefail

PROJECT_ROOT="/workspace/projects/my-repo"
IMAGE_FOLDER="assets/images/batch-01"

ukbe-run-agent submit \
  --workflow-name image_csv_gen_v1 \
  --project-root "$PROJECT_ROOT" \
  --input "IMAGE_FOLDER=${IMAGE_FOLDER}"
