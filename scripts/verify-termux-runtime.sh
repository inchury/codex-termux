#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Checking isolated Termux runtime compatibility from $(pwd)"

require_file() {
  if [[ ! -f "$1" ]]; then
    echo "FAIL: missing required file: $1" >&2
    exit 1
  fi
}
require_pattern() {
  if ! grep -Fq -- "$2" "$1"; then
    echo "FAIL: $1 does not contain expected Android compatibility marker: $2" >&2
    exit 1
  fi
}
reject_pattern() {
  if grep -Fq -- "$2" "$1"; then
    echo "FAIL: historical fork implementation leaked into upstream source: $1 ($2)" >&2
    exit 1
  fi
}

require_file patches/termux-runtime-compat.patch
require_file codex-rs/Cargo.toml
require_file codex-rs/arg0/src/lib.rs
require_file codex-rs/app-server-transport/src/transport/unix_socket.rs
require_file codex-rs/core/Cargo.toml
require_file codex-rs/tui/src/updates.rs
require_file codex-rs/cli/src/doctor/updates.rs

require_pattern codex-rs/arg0/src/lib.rs CODEX_SELF_EXE
require_pattern codex-rs/arg0/src/lib.rs is_unsupported_file_lock_error
require_pattern codex-rs/app-server-transport/src/transport/unix_socket.rs is_unsupported_file_lock_error
require_pattern codex-rs/core/Cargo.toml aarch64-linux-android
# Update notifications remain upstream-owned by the release workflow.
# Do not require historical fork-specific release or npm URLs here.

echo "Runtime compatibility contract passed"
