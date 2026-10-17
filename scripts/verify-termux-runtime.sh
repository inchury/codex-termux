#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Checking isolated Termux runtime compatibility from $(pwd)"
test -f patches/termux-runtime-compat.patch
test -f codex-rs/Cargo.toml
test -f codex-rs/arg0/src/lib.rs
test -f codex-rs/app-server-transport/src/transport/unix_socket.rs
grep -q 'CODEX_SELF_EXE' codex-rs/arg0/src/lib.rs
grep -q 'is_unsupported_file_lock_error' codex-rs/arg0/src/lib.rs
grep -q 'is_unsupported_file_lock_error' codex-rs/app-server-transport/src/transport/unix_socket.rs
grep -q 'aarch64-linux-android' codex-rs/core/Cargo.toml
# The generated candidate must not contain the legacy fork update UI or doctor.
if grep -q 'api.github.com/repos/inchury/codex-termux/releases/latest' codex-rs/tui/src/updates.rs; then
  echo "Unexpected old fork update UI was copied into clean upstream" >&2
  exit 1
fi
if grep -q 'registry.npmjs.org/@inchury' codex-rs/cli/src/doctor/updates.rs; then
  echo "Unexpected old fork doctor was copied into clean upstream" >&2
  exit 1
fi
echo "Runtime compatibility contract passed"
