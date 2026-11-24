#!/usr/bin/env python3
"""Patch mxc-sdk b211201/c662018 Android-only compile error in Cargo's fetched git checkout.

The mxc engine refuses Android in ensure_host_supported(), but dispatch.rs
unconditionally references a desktop-only module in unreachable paths.
Keep the rejection and guard only the logging calls.
"""
from pathlib import Path
import os
import sys

home = Path(os.environ.get("CARGO_HOME", str(Path.home() / ".cargo")))
expected_counts = {"b211201": 2, "c662018": 3}
matches = [p for rev in expected_counts for p in (home / "git" / "checkouts").glob(f"mxc-*/{rev}/src/mxc-sdk/src/core/mxc_engine/dispatch.rs")]
if not matches:
    # The upstream MXC dependency has moved beyond the b211201 checkout.
    # Do not patch an unrelated revision using stale source assumptions.
    print("Known mxc-sdk checkouts absent; skipping revision-specific Android patch")
    sys.exit(0)
for path in matches:
    source = path.read_text()
    revision = path.parents[5].name
    expected = expected_counts[revision]
    call = "    crate::mxc_engine::run::log_policy_hash(request, logger);"
    replacement = ('    #[cfg(any(target_os = "windows", target_os = "linux", target_os = "macos"))]\n' + call)
    if source.count(replacement) == expected:
        print(f"Already patched {path}")
        continue
    count = source.count(call)
    if count != expected or source.count(replacement):
        sys.exit(f"mxc-sdk API changed: expected {expected} unguarded calls, found {count}")
    path.write_text(source.replace(call, replacement))
    print(f"Guarded {count} desktop-only mxc-sdk calls in {path}")
