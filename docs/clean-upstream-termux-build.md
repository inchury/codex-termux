# Clean-upstream Termux release pipeline

The automated release candidate is created from the official `openai/codex` stable `rust-vX.Y.Z` tag. **No previously published Termux release is fetched or used as a source-code delta.**

## Sources of changes

1. `patches/termux-runtime-compat.patch`: a **fixed, reviewed snapshot** of Android/Termux runtime compatibility changes. It is version-controlled in this repository. The original snapshot was extracted once from the prior compatibility release, but future builds never fetch or diff that release.
2. The small, explicitly scoped adaptations in `.github/workflows/termux-auto-release.yml`: Android OpenSSL target dependency, executable resolution and unsupported file-lock handling, temporary directory and Unix socket lock handling.
3. Fork-owned **packaging and build infrastructure only**, including `npm-package/bin`, `codex-rs/.cargo/config.toml`, Android V8 scripts and GitHub Actions.

The official upstream TUI, doctor, version checks and ordinary CLI Rust implementation are **not replaced** by historical fork versions. A GitHub Release is the distribution mechanism; npm publishing is disabled.

## Compatibility maintenance

If a pinned Android patch stops applying to a new upstream release, candidate preparation fails **before compilation**. Rebase only the affected Android patch against that new upstream tag; do not copy whole source files from an older release.

`scripts/verify-termux-runtime.sh` checks basic Android compatibility invariants. It is **not** a replacement for a successful Android ARM64 compilation or on-device smoke test.

## Verification status

The pipeline has been rewritten, and the nine snapshot patch files were compared against the upstream 0.163.0 source for unchanged hunk context. A full GitHub Actions build and Termux device smoke test remain required before declaring the release verified.

## Self-hosted rusty_v8 requirement

The repository's current V8 manifest still contains historical DioNanos download URLs. The automated Codex release now **fails closed** if the selected V8 entry does not point to `inchury/codex-termux`. Never rewrite the repository name while retaining another publisher's hashes.

To bootstrap the required 150.4.0 prebuild:

1. Run `rusty-v8-android-release` with `v8_version=150.4.0`, `target=aarch64-linux-android`, `sandbox=true`, `publish_release=true`.
2. Confirm the job completed and the `rusty-v8-v150.4.0` release contains the archive, Rust binding and SHA256 file.
3. Audit the produced checksums and set the 150.4.0 manifest target `repository = "inchury/codex-termux"` and profile checksum values to those **actually produced**.
4. Only then rerun `termux-auto-release`.

The V8 job is expensive and is not started implicitly by the Codex release job. No successful self-hosted V8 build or end-to-end Codex release has been verified as part of this refactor.
