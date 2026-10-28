#!/usr/bin/env python3
"""Patch mxc-sdk b211201 Android-only compile error in Cargo's fetched git checkout.

The mxc engine refuses Android in ensure_host_supported(), but dispatch.rs
unconditionally references a desktop-only module in two unreachable paths.
Keep the rejection and guard only the logging calls.
"""
from pathlib import Path
import os
import sys

home = Path(os.environ.get("CARGO_HOME", str(Path.home() / ".cargo")))
matches = list((home / "git" / "checkouts").glob("mxc-*/b211201/src/mxc-sdk/src/core/mxc_engine/dispatch.rs"))
if len(matches) != 1:
    sys.exit(f"Expected one pinned mxc-sdk checkout, found {len(matches)}: {matches}")
path = matches[0]
source = path.read_text()
call = "    crate::mxc_engine::run::log_policy_hash(request, logger);"
replacement = ('    #[cfg(any(target_os = "windows", target_os = "linux", target_os = "macos"))]\n' + call)
count = source.count(call)
if count != 2:
    sys.exit(f"mxc-sdk API changed: expected 2 desktop-only log calls, found {count}")
path.write_text(source.replace(call, replacement))
print(f"Guarded {count} unreachable Android mxc-sdk calls in {path}")
