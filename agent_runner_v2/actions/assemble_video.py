#!/usr/bin/env python3
"""
actions/assemble_video.py - Assemble final video from clips and audio.

Uses ffmpeg to concatenate video clips, mix audio, and apply transitions.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult


def _write_meta(
    project_root: Path,
    output_dir: Path,
    status: str,
    remark: str,
    artifacts: dict,
) -> None:
    """Write meta.json sidecar."""
    meta_path = output_dir / "meta.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "schema_version": "v2",
        "coder_result": {
            "status": status,
            "remark": remark,
            "artifacts": artifacts,
            "recorded_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
    }
    meta_path.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _get_video_duration(video_path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def assemble_video(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Assemble final video from clips and audio."""

    # Check ffmpeg
    if not _check_ffmpeg():
        return ActionResult(
            status="REJECTED",
            remark="ffmpeg not found in PATH",
            artifacts={},
            reject_code="FFMPEG_NOT_FOUND",
        )

    # Get required inputs
    workflow_rel = context.get("VIDEOWORKFLOW_FILE", "")
    clips_folder_rel = context.get("GENERATED_VIDEO_CLIPS", "")
    audio_folder_rel = context.get("GENERATED_AUDIO_FOLDER", "")

    if not workflow_rel:
        return ActionResult(
            status="REJECTED",
            remark="VIDEOWORKFLOW_FILE not in context",
            artifacts={},
            reject_code="MISSING_WORKFLOW_FILE",
        )

    if not clips_folder_rel:
        return ActionResult(
            status="REJECTED",
            remark="GENERATED_VIDEO_CLIPS not in context",
            artifacts={},
            reject_code="MISSING_CLIPS_FOLDER",
        )

    if not audio_folder_rel:
        return ActionResult(
            status="REJECTED",
            remark="GENERATED_AUDIO_FOLDER not in context",
            artifacts={},
            reject_code="MISSING_AUDIO_FOLDER",
        )

    workflow_path = project_root / workflow_rel
    clips_folder = project_root / clips_folder_rel
    audio_folder = project_root / audio_folder_rel

    if not workflow_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow file not found: {workflow_rel}",
            artifacts={},
            reject_code="WORKFLOW_NOT_FOUND",
        )

    if not clips_folder.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Clips folder not found: {clips_folder_rel}",
            artifacts={},
            reject_code="CLIPS_NOT_FOUND",
        )

    if not audio_folder.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Audio folder not found: {audio_folder_rel}",
            artifacts={},
            reject_code="AUDIO_NOT_FOUND",
        )

    # Load workflow
    try:
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return ActionResult(
            status="REJECTED",
            remark=f"Failed to parse workflow JSON: {e}",
            artifacts={},
            reject_code="JSON_PARSE_ERROR",
        )

    scenes = workflow.get("scenes", [])
    if not scenes:
        return ActionResult(
            status="REJECTED",
            remark="No scenes found in workflow",
            artifacts={},
            reject_code="NO_SCENES",
        )

    # Setup output
    output_dir_rel = context.get("FINAL_VIDEO_FILE", "output/final_video.mp4")
    output_path = project_root / output_dir_rel
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get config from .env (priority) then context/step config
    aspect_ratio = (
        os.environ.get("VIDEO_ASPECT_RATIO", "")
        or context.get("ASPECT_RATIO_OVERRIDE", "")
        or step_cfg.get("aspect_ratio", "9:16")
    )
    fps = step_cfg.get("fps", int(os.environ.get("VIDEO_FPS", "30")))
    output_format = step_cfg.get("output_format", os.environ.get("VIDEO_FORMAT", "mp4"))

    # Determine resolution from aspect_ratio
    if aspect_ratio == "9:16":
        width, height = 1080, 1920
    elif aspect_ratio == "16:9":
        width, height = 1920, 1080
    elif aspect_ratio == "1:1":
        width, height = 1080, 1080
    else:
        width, height = 1080, 1920  # Default vertical

    # Build concat list for ffmpeg
    concat_files = []
    for scene in scenes:
        scene_num = scene.get("scene_number", 0)
        clip_path = clips_folder / f"scene_{scene_num:02d}_i2v.mp4"
        audio_path = audio_folder / f"scene_{scene_num:02d}_voiceover.mp3"

        if not clip_path.exists():
            _write_meta(project_root, output_path.parent, "REJECTED", f"Clip not found: {clip_path}", {})
            return ActionResult(
                status="REJECTED",
                remark=f"Video clip not found for scene {scene_num}",
                artifacts={},
                reject_code="CLIP_NOT_FOUND",
            )

        if not audio_path.exists():
            _write_meta(project_root, output_path.parent, "REJECTED", f"Audio not found: {audio_path}", {})
            return ActionResult(
                status="REJECTED",
                remark=f"Audio not found for scene {scene_num}",
                artifacts={},
                reject_code="AUDIO_NOT_FOUND",
            )

        concat_files.append({
            "scene_number": scene_num,
            "clip": clip_path,
            "audio": audio_path,
            "transition": scene.get("transition", "cut"),
        })

    # Create temporary concat file for ffmpeg
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        concat_file = Path(f.name)
        for item in concat_files:
            # Escape single quotes in path
            path_escaped = str(item["clip"]).replace("'", "'\\''")
            f.write(f"file '{path_escaped}'\n")

    try:
        # Build ffmpeg command
        # Method: Concatenate video clips, then mix audio
        temp_video = output_path.parent / "temp_video.mp4"

        # Step 1: Concatenate video clips
        concat_cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            str(temp_video),
        ]

        result = subprocess.run(
            concat_cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            _write_meta(project_root, output_path.parent, "REJECTED", f"Video concat failed: {result.stderr}", {})
            return ActionResult(
                status="REJECTED",
                remark=f"Video concatenation failed: {result.stderr[:200]}",
                artifacts={},
                reject_code="CONCAT_FAILED",
            )

        # Step 2: Mix in audio
        # Create audio concat file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as af:
            audio_concat_file = Path(af.name)
            for item in concat_files:
                path_escaped = str(item["audio"]).replace("'", "'\\''")
                af.write(f"file '{path_escaped}'\n")

        # Combine video and audio
        final_cmd = [
            "ffmpeg",
            "-y",
            "-i", str(temp_video),
            "-f", "concat",
            "-safe", "0",
            "-i", str(audio_concat_file),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-r", str(fps),
            "-pix_fmt", "yuv420p",
            str(output_path),
        ]

        result = subprocess.run(
            final_cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )

        # Cleanup temp files
        concat_file.unlink(missing_ok=True)
        audio_concat_file.unlink(missing_ok=True)
        temp_video.unlink(missing_ok=True)

        if result.returncode != 0:
            _write_meta(project_root, output_path.parent, "REJECTED", f"Final assembly failed: {result.stderr}", {})
            return ActionResult(
                status="REJECTED",
                remark=f"Final assembly failed: {result.stderr[:200]}",
                artifacts={},
                reject_code="ASSEMBLY_FAILED",
            )

    except subprocess.TimeoutExpired:
        _write_meta(project_root, output_path.parent, "REJECTED", "ffmpeg timeout", {})
        return ActionResult(
            status="REJECTED",
            remark="Video assembly timed out",
            artifacts={},
            reject_code="TIMEOUT",
        )
    except Exception as e:
        _write_meta(project_root, output_path.parent, "REJECTED", f"Exception: {e}", {})
        return ActionResult(
            status="REJECTED",
            remark=f"Assembly error: {e}",
            artifacts={},
            reject_code="EXECUTION_ERROR",
        )

    # Success
    output_rel = str(output_path.relative_to(project_root))
    remark = f"Final video assembled: {output_rel} ({len(scenes)} scenes)"
    artifacts = {"FINAL_VIDEO_FILE": output_rel}
    _write_meta(project_root, output_path.parent, "APPROVED", remark, artifacts)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )
