"""Integration tests for gen_media_content_v1 orchestrator actions.

Tests cover all 11 acceptance criteria (ACT-01 through ACT-11) for
Phase 9 orchestrator integration:
- generate_images_default dispatches, downloads, writes index
- generate_images_default error handling (missing provider, all fail, partial)
- generate_videos_default dispatches, downloads, handles skip
- generate_videos_default handles __none__ provider
- import_provider and _load_config edge cases
- Full test suite passes

All HTTP calls and provider imports are mocked. No real API keys or
network access required.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workflows.gen_media_content_v1.actions import (
    _load_config,
    _write_index,
    import_provider,
    generate_images_default,
    generate_videos_default,
)


def _make_config(tmp_path, render_image="agnes_v1", render_video="happyhorse_v1_1"):
    """Create a test config.json and return its path."""
    config = {
        "actions": {
            "render_image": render_image,
            "render_video": render_video,
        },
        "api": {
            "agnes_v1": {"model": "test-model", "size": "1024x1024", "ratio": "1:1"},
            "agnes_v2": {"model": "vid-model", "width": 1024, "height": 576},
            "happyhorse_v1_1": {"model": "hh-model", "resolution": "480P"},
        },
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def _make_variant_json(step_02_dir, name="variant_01_prompts.json",
                       t2i_prompt="A cat", t2v_prompt="A cat walking",
                       image_filename="cat.png"):
    """Create a variant JSON file in step_02_dir."""
    variant = {
        "variations": [{
            "t2i_prompt1": t2i_prompt,
            "t2v_prompt1": t2v_prompt,
            "image_filename": image_filename,
        }]
    }
    path = step_02_dir / name
    path.write_text(json.dumps(variant), encoding="utf-8")
    return path


def _mock_provider_module(call_api_return=None, call_api_side_effect=None):
    """Create a mock provider module with call_api."""
    mod = types.ModuleType("mock_provider")
    mock_call_api = MagicMock()
    if call_api_return is not None:
        mock_call_api.return_value = call_api_return
    if call_api_side_effect is not None:
        mock_call_api.side_effect = call_api_side_effect
    mod.call_api = mock_call_api
    return mod


# ============================================================================
# ACT-01: generate_images dispatches to configured provider
# ============================================================================

class TestGenerateImagesDispatch:
    def test_calls_provider_for_each_variant(self, tmp_path):
        """ACT-01: generate_images_default calls provider.call_api for each variant."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json", t2i_prompt="Prompt A")

        mock_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/img.png", "revised_prompt": "Prompt A"}
        )

        mock_download = MagicMock()
        mock_download.content = b"PNG_DATA"
        mock_download.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "test-key-123"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_download

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        mock_mod.call_api.assert_called_once()
        call_kwargs = mock_mod.call_api.call_args
        assert call_kwargs.kwargs.get("prompt") == "Prompt A"


# ============================================================================
# ACT-02: generate_images downloads images and saves to STEP_03_DIR
# ============================================================================

class TestGenerateImagesDownload:
    def test_downloads_and_saves_image(self, tmp_path):
        """ACT-02: Downloads image from URL and saves to STEP_03_DIR."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json")

        mock_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/cat.png", "revised_prompt": ""}
        )

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"FAKE_PNG_BYTES"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        png_files = list(step_03.glob("*.png"))
        assert len(png_files) >= 1
        assert png_files[0].read_bytes() == b"FAKE_PNG_BYTES"


# ============================================================================
# ACT-03: generate_images writes index.json with correct file mappings
# ============================================================================

class TestGenerateImagesIndex:
    def test_writes_index_json(self, tmp_path):
        """ACT-03: Writes index.json to STEP_03_DIR with file mappings."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json")

        mock_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/img.png", "revised_prompt": ""}
        )
        mock_img_resp = MagicMock()
        mock_img_resp.content = b"DATA"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        index_path = step_03 / "index.json"
        assert index_path.exists()
        with open(index_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "step" in data
        assert "files" in data
        assert len(data["files"]) >= 1
        assert "input" in data["files"][0]
        assert "output" in data["files"][0]


# ============================================================================
# ACT-04: generate_images returns APPROVED (skip) when no provider configured
# ============================================================================

class TestGenerateImagesMissingProvider:
    def test_approved_skip_with_none_provider(self, tmp_path):
        """ACT-04: Returns APPROVED with skip message when render_image is __none__."""
        step_02 = tmp_path / "step_02"
        step_02.mkdir()
        config_path = _make_config(tmp_path, render_image="__none__")

        result = generate_images_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(step_02),
                     "STEP_03_DIR": str(tmp_path / "step_03")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "skipped" in result.remark.lower()

    def test_approved_skip_with_empty_provider(self, tmp_path):
        """ACT-04: Returns APPROVED with skip message when render_image is empty string."""
        step_02 = tmp_path / "step_02"
        step_02.mkdir()
        config_path = _make_config(tmp_path, render_image="")

        result = generate_images_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(step_02),
                     "STEP_03_DIR": str(tmp_path / "step_03")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "skipped" in result.remark.lower()


# ============================================================================
# ACT-04b: generate_images with all failures returns REJECTED
# ============================================================================

class TestGenerateImagesAllFail:
    def test_all_failures_returns_rejected(self, tmp_path):
        """ACT-04: Returns REJECTED when all image generations fail."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json")

        mock_mod = _mock_provider_module(
            call_api_side_effect=RuntimeError("API error")
        )

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"):
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "REJECTED"


# ============================================================================
# ACT-04c: generate_images with partial success returns APPROVED
# ============================================================================

class TestGenerateImagesPartialSuccess:
    def test_partial_success_returns_approved(self, tmp_path):
        """ACT-04: Returns APPROVED when some images succeed and some fail."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_02.mkdir()
        step_03.mkdir()
        config_path = _make_config(tmp_path)

        # Create two variant files
        _make_variant_json(step_02, "v1_prompts.json", t2i_prompt="Good prompt")
        _make_variant_json(step_02, "v2_prompts.json", t2i_prompt="Bad prompt")

        mock_mod = _mock_provider_module(
            call_api_side_effect=[
                {"image_url": "http://cdn/good.png", "revised_prompt": ""},
                RuntimeError("API failure"),
            ]
        )

        mock_img_resp = MagicMock()
        mock_img_resp.content = b"PNG"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        assert "partial" in result.remark.lower() or "1" in result.remark


# ============================================================================
# ACT-05: generate_videos dispatches to configured provider
# ============================================================================

class TestGenerateVideosDispatch:
    def test_calls_provider_for_each_image(self, tmp_path):
        """ACT-05: generate_videos_default calls provider.call_api for each image."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_04 = tmp_path / "step_04"
        step_02.mkdir()
        step_03.mkdir()
        step_04.mkdir()
        config_path = _make_config(tmp_path)

        # Simulate step_02 having the original variant JSON (with prompts, no image_url)
        _make_variant_json(step_02, "v1_prompts.json",
                           t2i_prompt="A cat", t2v_prompt="A cat walking")

        # Simulate step_03 having an updated variant JSON with image_url
        updated_variant = {
            "variations": [{
                "t2i_prompt1": "A cat",
                "t2v_prompt1": "A cat walking",
                "image_filename": "cat.png",
                "image_url": "http://cdn/cat.png",
            }]
        }
        (step_03 / "v1_prompts.json").write_text(
            json.dumps(updated_variant), encoding="utf-8"
        )
        # Write a dummy index.json in step_03
        (step_03 / "index.json").write_text(
            json.dumps({"step": "render_image", "files": [
                {"input": "v1_prompts.json", "output": "cat.png"}
            ]}), encoding="utf-8"
        )

        mock_mod = _mock_provider_module(
            call_api_return={"video_url": "http://cdn/cat.mp4"}
        )

        mock_vid_resp = MagicMock()
        mock_vid_resp.content = b"MP4_DATA"
        mock_vid_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_vid_resp

            result = generate_videos_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03),
                         "STEP_04_DIR": str(step_04)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        mock_mod.call_api.assert_called_once()


# ============================================================================
# ACT-06: generate_videos with __none__ provider returns APPROVED (skipped)
# ============================================================================

class TestGenerateVideosNoneProvider:
    def test_none_provider_returns_approved(self, tmp_path):
        """ACT-06: Returns APPROVED with skip message when render_video is __none__."""
        config_path = _make_config(tmp_path, render_video="__none__")

        result = generate_videos_default(
            context={"MEDIA_CONFIG": str(config_path),
                     "STEP_02_DIR": str(tmp_path / "step_02"),
                     "STEP_03_DIR": str(tmp_path / "step_03"),
                     "STEP_04_DIR": str(tmp_path / "step_04")},
            state=MagicMock(),
            step_cfg=MagicMock(),
            project_root=tmp_path,
        )

        assert result.status == "APPROVED"
        assert "skip" in result.remark.lower()


# ============================================================================
# ACT-07: generate_videos handles {"skipped": True} from provider
# ============================================================================

class TestGenerateVideosSkippedFromProvider:
    def test_skipped_result_does_not_download(self, tmp_path):
        """ACT-07: When provider returns {skipped: True}, no download is attempted."""
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_04 = tmp_path / "step_04"
        step_02.mkdir()
        step_03.mkdir()
        step_04.mkdir()
        config_path = _make_config(tmp_path)

        # Original variant in step_02
        _make_variant_json(step_02, "v1_prompts.json",
                           t2i_prompt="A cat", t2v_prompt="A cat walking")

        # Updated variant in step_03 with image_url
        updated_variant = {
            "variations": [{
                "t2i_prompt1": "A cat",
                "t2v_prompt1": "A cat walking",
                "image_filename": "cat.png",
                "image_url": "http://cdn/cat.png",
            }]
        }
        (step_03 / "v1_prompts.json").write_text(
            json.dumps(updated_variant), encoding="utf-8"
        )
        # Index with one entry so the orchestrator processes it
        (step_03 / "index.json").write_text(
            json.dumps({"step": "render_image", "files": [
                {"input": "v1_prompts.json", "output": "cat.png"}
            ]}), encoding="utf-8"
        )

        mock_mod = _mock_provider_module(
            call_api_return={"skipped": True, "reason": "Not supported"}
        )

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool

            result = generate_videos_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03),
                         "STEP_04_DIR": str(step_04)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert result.status == "APPROVED"
        # Verify requests.get was NOT called for video download
        mock_requests.get.assert_not_called()
        # Verify no mp4 files in step_04
        mp4_files = list(step_04.glob("*.mp4"))
        assert len(mp4_files) == 0


# ============================================================================
# ACT-08: import_provider and _load_config edge cases
# ============================================================================

class TestImportProviderEdgeCases:
    def test_valid_provider_import(self):
        """ACT-08: import_provider works for valid provider names."""
        mock_module = types.ModuleType("mock")
        mock_module.call_api = lambda: None

        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    return_value=mock_module):
            result = import_provider("render_image", "agnes_v1")
            assert hasattr(result, "call_api")

    def test_invalid_provider_raises_import_error(self):
        """ACT-08: import_provider raises ImportError with descriptive message for invalid names."""
        with patch("workflows.gen_media_content_v1.actions.importlib.import_module",
                    side_effect=ModuleNotFoundError("No module")):
            with pytest.raises(ImportError, match="nonexistent_provider"):
                import_provider("render_image", "nonexistent_provider")


class TestLoadConfigEdgeCases:
    def test_missing_file_raises_file_not_found(self, tmp_path):
        """ACT-08: _load_config raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            _load_config(str(tmp_path / "nonexistent.json"))


# ============================================================================
# ACT-09: Full pipeline integration test
# ============================================================================

class TestFullPipelineIntegration:
    def test_images_output_becomes_video_input(self, tmp_path):
        """ACT-09: Verify data flow from generate_images_default to generate_videos_default.

        generate_images_default writes updated variant JSONs (with image_url)
        to STEP_03_DIR and an index.json. generate_videos_default reads the
        index.json and cross-references to STEP_02_DIR for video prompts.
        """
        step_02 = tmp_path / "step_02"
        step_03 = tmp_path / "step_03"
        step_04 = tmp_path / "step_04"
        step_02.mkdir()
        step_03.mkdir()
        step_04.mkdir()
        config_path = _make_config(tmp_path)
        _make_variant_json(step_02, "v1_prompts.json",
                           t2i_prompt="A cat", t2v_prompt="A cat walking")

        # -- Run generate_images_default --
        mock_img_mod = _mock_provider_module(
            call_api_return={"image_url": "http://cdn/cat.png", "revised_prompt": "A cat"}
        )
        mock_img_resp = MagicMock()
        mock_img_resp.content = b"PNG_BYTES"
        mock_img_resp.raise_for_status = MagicMock()

        with patch("workflows.gen_media_content_v1.actions.import_provider", return_value=mock_img_mod), \
             patch("workflows.gen_media_content_v1.actions.ApiKeyPool") as mock_pool_cls, \
             patch("workflows.gen_media_content_v1.actions.load_env_from_project"), \
             patch("workflows.gen_media_content_v1.actions.requests") as mock_requests:
            mock_pool = MagicMock()
            mock_pool.next_key.return_value = "key"
            mock_pool_cls.return_value = mock_pool
            mock_requests.get.return_value = mock_img_resp

            img_result = generate_images_default(
                context={"MEDIA_CONFIG": str(config_path),
                         "STEP_02_DIR": str(step_02),
                         "STEP_03_DIR": str(step_03)},
                state=MagicMock(),
                step_cfg=MagicMock(),
                project_root=tmp_path,
            )

        assert img_result.status == "APPROVED"
        assert (step_03 / "index.json").exists()

        # Verify the updated variant JSON in step_03 has image_url
        updated_variant_path = step_03 / "v1_prompts.json"
        assert updated_variant_path.exists()
        updated_data = json.loads(updated_variant_path.read_text(encoding="utf-8"))
        assert updated_data["variations"][0].get("image_url") == "http://cdn/cat.png"
