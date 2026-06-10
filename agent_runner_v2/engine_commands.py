"""Engine version management for agent_runner_v2.

Invoked via: ukbe-run-agent engine <subcommand>

  install <tag>                    -- download from GitHub and install globally (~/.ukbe-runner/engines/)
  install <tag> --local            -- install to repo-local .ukbe-runner/engine/versions/
  install <tag> --from-path <dir>  -- copy from a local source directory (useful for private repos)
  snapshot                         -- snapshot live source into repo-local SNAPSHOT version
  use <version>                    -- set active version in .ukbe-runner/engine/config.json
  list                             -- list installed versions (global + repo-local)
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

DEFAULT_GITHUB_REPO = "kkchua/agent-runner-v2"


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def _global_engines_dir() -> Path:
    return Path.home() / ".ukbe-runner" / "engines"


def _global_version_dir(version: str) -> Path:
    return _global_engines_dir() / version


def _local_versions_dir(project_root: Path) -> Path:
    return project_root / ".ukbe-runner" / "engine" / "versions"


def _local_version_dir(project_root: Path, version: str) -> Path:
    return _local_versions_dir(project_root) / version


def _local_config_path(project_root: Path) -> Path:
    return project_root / ".ukbe-runner" / "engine" / "config.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_version_json(version_dir: Path, data: dict) -> None:
    (version_dir / "version.json").write_text(json.dumps(data, indent=2), encoding="utf-8")


def _verify_import(version_dir: Path) -> None:
    env = os.environ.copy()
    # Mirror how _invoke_execute_step_subprocess resolves the engine:
    # prepend <engine_root>/agent_runner_v2 so the inner package is found first,
    # even if agent_runner_v2 is also installed as a pip package.
    env["PYTHONPATH"] = str(version_dir / "agent_runner_v2") + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-c", "import agent_runner_v2.run_agent; print('import OK')"],
        capture_output=True, text=True, env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Import check failed from {version_dir}:\n{result.stderr}")
    print(f"  import check: {result.stdout.strip()}")


def _copy_pkg_to(src_inner_pkg: Path, dest_version_dir: Path) -> None:
    """Copy agent_runner_v2 inner package to a versioned engine store directory.

    src_inner_pkg  — the agent_runner_v2/ package directory (contains __init__.py)
    dest_version_dir — e.g. ~/.ukbe-runner/engines/1.0.1/
    Result layout:
      dest_version_dir/
        agent_runner_v2/
          agent_runner_v2/   <- importable package
    """
    dest_pkg = dest_version_dir / "agent_runner_v2" / "agent_runner_v2"
    if dest_version_dir.exists():
        shutil.rmtree(dest_version_dir)
    dest_pkg.mkdir(parents=True)
    shutil.copytree(str(src_inner_pkg), str(dest_pkg), dirs_exist_ok=True)


def _read_version_meta(d: Path) -> str:
    vfile = d / "version.json"
    if not vfile.exists():
        return ""
    try:
        v = json.loads(vfile.read_text(encoding="utf-8"))
        if d.name == "SNAPSHOT":
            return f"  commit={v.get('short_hash', '?')}  created={v.get('created_at', '?')[:19]}"
        return f"  source={v.get('source', '?')}  installed={v.get('installed_at', '?')[:19]}"
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_snapshot(project_root: Path) -> None:
    """Snapshot the live package source into repo-local SNAPSHOT version."""
    from .runtime_context import PACKAGE_ROOT
    inner_pkg = PACKAGE_ROOT  # agent_runner_v2/agent_runner_v2/ — contains __init__.py

    print("Creating SNAPSHOT from live source...")

    result = subprocess.run(
        [sys.executable, "-c", "import agent_runner_v2.agent_runner_v2.run_agent; print('live source OK')"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: live source does not import cleanly:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)
    print(f"  live source: {result.stdout.strip()}")

    commit_hash = ""
    try:
        pkg_repo = inner_pkg.parent  # agent_runner_v2/ repo root
        commit_hash = subprocess.check_output(
            ["git", "-C", str(pkg_repo), "rev-parse", "HEAD"],
            text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except Exception:
        pass

    dest = _local_version_dir(project_root, "SNAPSHOT")
    _copy_pkg_to(inner_pkg, dest)
    _write_version_json(dest, {
        "version": "SNAPSHOT",
        "commit_hash": commit_hash,
        "short_hash": commit_hash[:7] if commit_hash else "unknown",
        "source": "local",
        "created_at": datetime.datetime.utcnow().isoformat() + "+00:00",
    })

    print(f"  commit: {commit_hash or 'unknown'}")
    _verify_import(dest)
    print(f"SNAPSHOT created at {dest}")


def cmd_install(
    tag: str,
    github_repo: str,
    global_install: bool = True,
    from_path: str | None = None,
    project_root: Path | None = None,
) -> None:
    """Install engine from a local path or a GitHub tag."""
    if project_root is None:
        project_root = Path.cwd()

    dest_dir = _global_version_dir(tag) if global_install else _local_version_dir(project_root, tag)
    store_label = "global (~/.ukbe-runner/engines/)" if global_install else "repo-local (.ukbe-runner/engine/versions/)"

    if from_path:
        src_root = Path(from_path).resolve()
        inner_pkg = src_root / "agent_runner_v2"
        if not inner_pkg.exists():
            print(f"ERROR: agent_runner_v2/ not found under {src_root}", file=sys.stderr)
            print("Pass the root of the agent_runner_v2 source repo, e.g. --from-path ./agent_runner_v2", file=sys.stderr)
            sys.exit(1)
        print(f"Installing engine version {tag!r} from {src_root} [{store_label}]...")
        commit_hash = ""
        try:
            commit_hash = subprocess.check_output(
                ["git", "-C", str(src_root), "rev-parse", "HEAD"],
                text=True, stderr=subprocess.DEVNULL,
            ).strip()
        except Exception:
            pass
        _copy_pkg_to(inner_pkg, dest_dir)
        _write_version_json(dest_dir, {
            "version": tag,
            "source": "local-path",
            "path": str(src_root),
            "commit_hash": commit_hash,
            "installed_at": datetime.datetime.utcnow().isoformat() + "+00:00",
        })
        _verify_import(dest_dir)
        print(f"Version {tag!r} installed at {dest_dir}")
        return

    print(f"Installing engine version {tag!r} from {github_repo} [{store_label}]...")
    url = f"https://github.com/{github_repo}/archive/refs/tags/{tag}.tar.gz"
    print(f"  downloading: {url}")

    with tempfile.TemporaryDirectory(prefix="engine-install-") as tmp:
        archive_path = Path(tmp) / "source.tar.gz"
        try:
            urllib.request.urlretrieve(url, str(archive_path))
        except Exception as exc:
            print(f"ERROR: download failed: {exc}", file=sys.stderr)
            print("Tip: for private repos use --from-path <path/to/agent_runner_v2_repo>", file=sys.stderr)
            sys.exit(1)

        print("  extracting...")
        with tarfile.open(archive_path, "r:gz") as tf:
            tf.extractall(tmp)

        # GitHub archives unpack to <repo-name>-<tag>/
        extracted_dirs = [d for d in Path(tmp).iterdir() if d.is_dir()]
        if not extracted_dirs:
            print("ERROR: no directory found in archive", file=sys.stderr)
            sys.exit(1)
        source_root = extracted_dirs[0]

        # agent-runner-v2 repo layout: agent_runner_v2/ is the inner package at the repo root
        inner_pkg = source_root / "agent_runner_v2"
        if not inner_pkg.exists():
            print(f"ERROR: agent_runner_v2/ package not found in archive at {source_root}", file=sys.stderr)
            sys.exit(1)

        _copy_pkg_to(inner_pkg, dest_dir)
        _write_version_json(dest_dir, {
            "version": tag,
            "source": "github-tag",
            "github_repo": github_repo,
            "installed_at": datetime.datetime.utcnow().isoformat() + "+00:00",
        })

    _verify_import(dest_dir)
    print(f"Version {tag!r} installed at {dest_dir}")


def _global_config_path() -> Path:
    return Path.home() / ".ukbe-runner" / "engine" / "config.json"


def cmd_use(project_root: Path, version: str, local: bool = False) -> None:
    """Set the active engine version in config.json.

    Defaults to global (~/.ukbe-runner/engine/config.json).
    Pass local=True to write to the repo-local .ukbe-runner/engine/config.json instead.
    """
    global_dir = _global_version_dir(version)
    local_dir = _local_version_dir(project_root, version)
    if not global_dir.exists() and not local_dir.exists():
        print(
            f"ERROR: version {version!r} not found in global ({global_dir}) or local ({local_dir}) store",
            file=sys.stderr,
        )
        print("Run: ukbe-run-agent engine list", file=sys.stderr)
        sys.exit(1)

    config_path = _local_config_path(project_root) if local else _global_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps({"engine_version": version}, indent=2), encoding="utf-8")
    store_location = "global" if global_dir.exists() else "local"
    scope_label = "repo-local" if local else "global"
    print(f"Active engine version set to {version!r} (resolved from {store_location} store)")
    print(f"Config ({scope_label}): {config_path}")
    print("Restart the worker to apply.")


def cmd_list(project_root: Path) -> None:
    """List all installed engine versions (global + repo-local)."""
    # Prefer repo-local config; fall back to global config
    local_cfg = _local_config_path(project_root)
    global_cfg = _global_config_path()
    active = None
    active_scope = ""
    for cfg_path, scope in [(local_cfg, "repo-local"), (global_cfg, "global")]:
        if cfg_path.exists():
            try:
                active = json.loads(cfg_path.read_text(encoding="utf-8")).get("engine_version")
                active_scope = scope
                break
            except Exception:
                pass

    global_dir = _global_engines_dir()
    local_dir = _local_versions_dir(project_root)
    found_any = False

    if global_dir.exists() and any(global_dir.iterdir()):
        found_any = True
        print(f"Global engines ({global_dir}):")
        for d in sorted(global_dir.iterdir()):
            if not d.is_dir():
                continue
            marker = " *" if d.name == active else ""
            print(f"  {d.name}{marker}{_read_version_meta(d)}")

    if local_dir.exists() and any(local_dir.iterdir()):
        found_any = True
        print(f"Repo-local engines ({local_dir}):")
        for d in sorted(local_dir.iterdir()):
            if not d.is_dir():
                continue
            marker = " *" if d.name == active else ""
            print(f"  {d.name}{marker}{_read_version_meta(d)}")

    if not found_any:
        print("No engine versions installed.")
        print("Install globally (recommended): ukbe-run-agent engine install <tag>")
        print("Or create local snapshot:       ukbe-run-agent engine snapshot")
        return

    if active:
        cfg_shown = local_cfg if active_scope == "repo-local" else global_cfg
        print(f"\nActive: {active!r}  [{active_scope} config: {cfg_shown}]")
    else:
        print(f"\nNo active version set (live source / dev mode).")
        print(f"Set one: ukbe-run-agent engine use <version>")


# ---------------------------------------------------------------------------
# Entry point (called from run_agent.py)
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ukbe-run-agent engine",
        description="Engine version management for agent_runner_v2.",
    )
    parser.add_argument("--project-root", default=".", help="Workspace root (default: cwd).")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("snapshot", help="Snapshot live source to repo-local SNAPSHOT version.")

    p_install = sub.add_parser("install", help="Install engine from GitHub or a local path.")
    p_install.add_argument("tag", help="Version tag name, e.g. 1.0.1")
    p_install.add_argument("--local", action="store_true", default=False,
                           help="Install to repo-local .ukbe-runner/engine/versions/ instead of ~/.ukbe-runner/engines/")
    p_install.add_argument("--github-repo", default="",
                           help=f"GitHub repo (owner/repo). Defaults to {DEFAULT_GITHUB_REPO}.")
    p_install.add_argument("--from-path", default="",
                           help="Install by copying from a local source directory (root of agent_runner_v2 repo).")

    p_use = sub.add_parser("use", help="Set the active engine version.")
    p_use.add_argument("version", help="Version name or SNAPSHOT.")
    p_use.add_argument("--local", action="store_true", default=False,
                       help="Write config to repo-local .ukbe-runner/engine/config.json instead of ~/.ukbe-runner/engine/config.json")

    sub.add_parser("list", help="List installed versions (global + repo-local).")

    args = parser.parse_args(argv)
    project_root = Path(args.project_root).resolve()

    if args.command == "snapshot":
        cmd_snapshot(project_root)
    elif args.command == "install":
        github_repo = args.github_repo or DEFAULT_GITHUB_REPO
        cmd_install(
            args.tag,
            github_repo=github_repo,
            global_install=not args.local,
            from_path=args.from_path or None,
            project_root=project_root,
        )
    elif args.command == "use":
        cmd_use(project_root, args.version, local=args.local)
    elif args.command == "list":
        cmd_list(project_root)

    return 0
