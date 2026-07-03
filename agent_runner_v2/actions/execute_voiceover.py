#!/usr/bin/env python3
"""
actions/execute_voiceover.py - Generate voiceover audio for VideoExpress workflow.

Supports multiple TTS providers: elevenlabs, openai, local.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from ..action_result import ActionResult
from ..runtime_context import write_meta_sidecar

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent


def _generate_elevenlabs(
    text: str,
    voice_id: str,
    api_key: str,
    output_path: Path,
) -> bool:
    """Generate audio using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
        },
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio_data = resp.read()
            output_path.write_bytes(audio_data)
            return True
    except Exception as e:
        print(f"[execute_voiceover] ElevenLabs error: {e}", flush=True)
        return False


def _generate_openai(
    text: str,
    voice: str,
    api_key: str,
    output_path: Path,
) -> bool:
    """Generate audio using OpenAI TTS API."""
    url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "tts-1",
        "input": text,
        "voice": voice,
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            audio_data = resp.read()
            output_path.write_bytes(audio_data)
            return True
    except Exception as e:
        print(f"[execute_voiceover] OpenAI error: {e}", flush=True)
        return False


def _generate_local(
    text: str,
    output_path: Path,
) -> bool:
    """Generate audio using local TTS (requires local TTS setup)."""
    # This is a placeholder - requires actual local TTS implementation
    try:
        # Example using system command (customize based on your local setup)
        result = subprocess.run(
            ["tts", "--text", text, "--out_path", str(output_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0 and output_path.exists()
    except Exception as e:
        print(f"[execute_voiceover] Local TTS error: {e}", flush=True)
        return False


def execute_voiceover(
    *,
    context: dict[str, str],
    state: dict,
    step_cfg: dict,
    project_root: Path,
) -> ActionResult:
    """Generate voiceover for all scenes."""

    # Load .env
    env_file = project_root / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    # Get workflow file
    workflow_rel = context.get("VIDEOWORKFLOW_FILE", "")
    if not workflow_rel:
        return ActionResult(
            status="REJECTED",
            remark="VIDEOWORKFLOW_FILE not in context",
            artifacts={},
            reject_code="MISSING_WORKFLOW_FILE",
        )

    workflow_path = project_root / workflow_rel
    if not workflow_path.exists():
        return ActionResult(
            status="REJECTED",
            remark=f"Workflow file not found: {workflow_rel}",
            artifacts={},
            reject_code="WORKFLOW_NOT_FOUND",
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

    # Setup output directory
    output_dir_rel = context.get("GENERATED_AUDIO_FOLDER", "output/generated_audio")
    output_dir = project_root / output_dir_rel
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get TTS config from .env (priority) then step config
    tts_provider = (
        os.environ.get("TTS_PROVIDER", "")
        or context.get("TTS_PROVIDER_OVERRIDE", "")
        or step_cfg.get("tts_provider", "elevenlabs")
    )
    tts_voice = (
        os.environ.get("TTS_VOICE_ID", "")
        or os.environ.get("TTS_VOICE", "")
        or context.get("TTS_VOICE_OVERRIDE", "")
        or step_cfg.get("tts_voice", "default")
    )
    delay = step_cfg.get("delay_seconds", int(os.environ.get("TTS_DELAY_SECONDS", "1")))

    # Get API keys from .env
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")

    # Validate provider
    if tts_provider == "elevenlabs" and not elevenlabs_key:
        write_meta_sidecar(output_dir / "meta.json", status="REJECTED", remark="ELEVENLABS_API_KEY not set", artifacts={})
        return ActionResult(
            status="REJECTED",
            remark="ELEVENLABS_API_KEY not set in environment",
            artifacts={},
            reject_code="API_KEY_MISSING",
        )

    if tts_provider == "openai" and not openai_key:
        write_meta_sidecar(output_dir / "meta.json", status="REJECTED", remark="OPENAI_API_KEY not set", artifacts={})
        return ActionResult(
            status="REJECTED",
            remark="OPENAI_API_KEY not set in environment",
            artifacts={},
            reject_code="API_KEY_MISSING",
        )

    # Voice mapping
    voice_id = tts_voice
    if tts_provider == "openai" and voice_id == "default":
        voice_id = "alloy"

    # Process scenes
    results = []
    succeeded = 0
    failed = 0

    for scene in scenes:
        scene_num = scene.get("scene_number", 0)
        voiceover_text = scene.get("voiceover_prompt", "")

        if not voiceover_text:
            failed += 1
            results.append({
                "scene_number": scene_num,
                "status": "failed",
                "error": "missing_voiceover_prompt",
            })
            continue

        output_filename = f"scene_{scene_num:02d}_voiceover.mp3"
        output_path = output_dir / output_filename

        # Generate audio
        success = False
        if tts_provider == "elevenlabs":
            success = _generate_elevenlabs(voiceover_text, voice_id, elevenlabs_key, output_path)
        elif tts_provider == "openai":
            success = _generate_openai(voiceover_text, voice_id, openai_key, output_path)
        elif tts_provider == "local":
            success = _generate_local(voiceover_text, output_path)
        else:
            failed += 1
            results.append({
                "scene_number": scene_num,
                "status": "failed",
                "error": f"unknown_provider: {tts_provider}",
            })
            write_meta_sidecar(output_dir / "meta.json", status="REJECTED", remark=f"Unknown TTS provider: {tts_provider}", artifacts={})
            return ActionResult(
                status="REJECTED",
                remark=f"Unknown TTS provider: {tts_provider}",
                artifacts={},
                reject_code="UNKNOWN_PROVIDER",
            )

        if success:
            succeeded += 1
            results.append({
                "scene_number": scene_num,
                "status": "succeeded",
                "filename": output_filename,
                "provider": tts_provider,
            })
        else:
            failed += 1
            results.append({
                "scene_number": scene_num,
                "status": "failed",
                "error": f"{tts_provider}_generation_failed",
            })
            write_meta_sidecar(output_dir / "meta.json", status="REJECTED", remark=f"Failed to generate audio for scene {scene_num}", artifacts={})
            return ActionResult(
                status="REJECTED",
                remark=f"Failed to generate audio for scene {scene_num}",
                artifacts={},
                reject_code="GENERATION_FAILED",
            )

        time.sleep(delay)

    # Write results
    summary = {
        "schema_version": "v2",
        "total_scenes": len(scenes),
        "succeeded": succeeded,
        "failed": failed,
        "provider": tts_provider,
        "results": results,
    }
    summary_path = output_dir / "voiceover_results.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if failed > 0:
        remark = f"Voiceover generation: {succeeded} succeeded, {failed} failed"
        write_meta_sidecar(output_dir / "meta.json", status="REJECTED", remark=remark, artifacts={})
        return ActionResult(
            status="REJECTED",
            remark=remark,
            artifacts={},
            reject_code="GENERATION_FAILED",
        )

    remark = f"Voiceover generation complete: {succeeded} scenes using {tts_provider}"
    artifacts = {"GENERATED_AUDIO_FOLDER": str(output_dir_rel)}
    write_meta_sidecar(output_dir / "meta.json", status="APPROVED", remark=remark, artifacts=artifacts)

    return ActionResult(
        status="APPROVED",
        remark=remark,
        artifacts=artifacts,
    )
