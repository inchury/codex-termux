#!/usr/bin/env python3
"""Resolve or build a versioned, sandbox-enabled Android V8 release and pin its hashes."""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = os.environ["GITHUB_REPOSITORY"]
VERSION = os.environ["V8_VERSION"]
TARGET = "aarch64-linux-android"
PROFILE = "ptrcomp_sandbox_release"
TAG = f"rusty-v8-v{VERSION}"
MANIFEST = Path("third_party/v8/android-artifacts.toml")
ASSETS = [
    f"librusty_v8_{PROFILE}_{TARGET}.a.gz",
    f"src_binding_{PROFILE}_{TARGET}.rs",
    f"rusty_v8_{PROFILE}_{TARGET}.sha256",
]


def gh(*args, check=True):
    return subprocess.run(["gh", *args], text=True, capture_output=True, check=check)


def release_exists():
    return gh("release", "view", TAG, "--repo", REPO, check=False).returncode == 0


if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", VERSION):
    sys.exit(f"Invalid V8 version: {VERSION}")

if not release_exists():
    print(f"Missing {TAG}: dispatching the dedicated Android V8 build", flush=True)
    gh("workflow", "run", "rusty-v8-android-release.yml", "--repo", REPO,
       "--ref", "main", "-f", f"v8_version={VERSION}",
       "-f", f"target={TARGET}", "-f", "sandbox=true",
       "-f", "publish_release=true")
    # V8 builds can take hours. Do not silently proceed without a published release.
    deadline = time.monotonic() + 4 * 60 * 60
    while not release_exists():
        if time.monotonic() >= deadline:
            sys.exit(f"Timed out waiting for {TAG}; inspect rusty-v8-android-release Actions")
        time.sleep(45)

from tempfile import TemporaryDirectory
with TemporaryDirectory() as tmp:
    gh("release", "download", TAG, "--repo", REPO, "--dir", tmp,
       *sum((["--pattern", name] for name in ASSETS), []))
    folder = Path(tmp)
    import hashlib
    hashes = {}
    for line in (folder / ASSETS[2]).read_text().splitlines():
        parts = line.split()
        if len(parts) != 2:
            sys.exit("Malformed V8 SHA256 manifest")
        hashes[parts[1].lstrip("*")] = parts[0]
    for name in ASSETS[:2]:
        digest = hashlib.sha256((folder / name).read_bytes()).hexdigest()
        if hashes.get(name) != digest:
            sys.exit(f"V8 asset checksum mismatch: {name}")
    archive_sha = hashes[ASSETS[0]]
    binding_sha = hashes[ASSETS[1]]

text = MANIFEST.read_text()
header = f'[versions."{VERSION}"]'
target_header = f'[versions."{VERSION}".targets."{TARGET}"]'
profile_header = f'[versions."{VERSION}".targets."{TARGET}".profiles.{PROFILE}]'
# Replace only the matching version's section, preserving historical pins.
lines = text.splitlines(keepends=True)
starts = [i for i, line in enumerate(lines) if line.strip() == header]
if starts:
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith('[versions."') and lines[i].strip().endswith(']') and
                not lines[i].startswith(f'[versions."{VERSION}".')), len(lines))
    del lines[start:end]
text = "".join(lines).rstrip() + "\n\n"
text += (f'{header}\nsource_tag = "v{VERSION}"\n\n'
         f'{target_header}\nrepository = "{REPO}"\nrelease_tag = "{TAG}"\n\n'
         f'{profile_header}\narchive_sha256 = "{archive_sha}"\n'
         f'binding_sha256 = "{binding_sha}"\n')
MANIFEST.write_text(text)
print(f"Verified and pinned {TAG}: {archive_sha} / {binding_sha}", flush=True)
