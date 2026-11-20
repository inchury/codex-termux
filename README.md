# Codex Termux

OpenAI Codex CLI를 **Android ARM64 / Termux**에서 네이티브로 실행하기 위한 커뮤니티 포트입니다.

이 저장소는 OpenAI의 공식 `openai/codex` stable release를 기준으로 Termux에 필요한 Android/Bionic 호환 패치를 적용하고, GitHub Actions에서 ARM64 바이너리와 설치용 `.tgz` 패키지를 자동으로 빌드합니다.

> 이 프로젝트는 OpenAI의 공식 배포판이 아닙니다. 원본 프로젝트와 Codex의 저작권 및 상표는 각 권리자에게 있습니다.

## 주요 특징

- OpenAI Codex 최신 stable release 자동 감지
- Android ARM64 / Termux 네이티브 빌드
- Bionic/Termux 호환 패치 자동 적용
- Android용 V8(code-mode) 지원
- `termux-open-url`을 이용한 브라우저 로그인
- `libc++_shared.so` 포함
- Android 바이너리에 `RUNPATH=$ORIGIN` 적용
- GitHub Actions에서 빌드 및 검증
- GitHub Release에 설치 가능한 `.tgz` 패키지 배포

## 지원 환경

- Android 10 이상 / API 29 이상
- ARM64 (aarch64)
- Termux
- Node.js 18 이상

32-bit ARM 및 x86/x86_64 Android는 현재 배포 대상이 아닙니다.

## 설치

### 1. Termux 준비

Termux에서 Node.js를 설치합니다.

```bash
pkg update
pkg install nodejs-lts -y
```

저장소 접근이나 Release 다운로드에 GitHub CLI를 사용하려면 다음도 설치할 수 있습니다.

```bash
pkg install gh -y
```

### 2. 최신 Release의 .tgz 다운로드

GitHub Release 페이지에서 최신 `*.tgz` 파일을 다운로드합니다.

https://github.com/inchury/codex-termux/releases/latest

GitHub CLI를 사용하면 Termux에서 직접 받을 수도 있습니다.

```bash
gh release download \
  -R inchury/codex-termux \
  -p '*.tgz'
```

### 3. .tgz 패키지 설치

다운로드한 파일이 있는 디렉터리에서 다음과 같이 설치합니다.

```bash
npm install -g ./*.tgz
```

설치 확인:

```bash
codex --version
```

### 4. 로그인

```bash
codex login
```

브라우저 인증이 필요한 경우 Termux의 `termux-open-url`을 이용하도록 호환 패치가 적용되어 있습니다.

## 업데이트

새 버전의 `.tgz`를 받은 뒤 동일하게 설치하면 기존 전역 설치가 업데이트됩니다.

```bash
npm install -g ./새버전.tgz
```

GitHub CLI를 사용한다면 새 디렉터리에서 최신 Release를 내려받아 설치할 수 있습니다.

```bash
mkdir -p ~/codex-termux-update
cd ~/codex-termux-update
rm -f ./*.tgz

gh release download \
  -R inchury/codex-termux \
  -p '*.tgz'

npm install -g ./*.tgz
```

## 자동 Release 구조

이 저장소의 `termux-auto-release` workflow는 공식 OpenAI Codex stable release를 주기적으로 확인합니다.

새 stable 버전이 발견되면 다음 과정을 수행합니다.

1. 공식 OpenAI Codex stable tag를 기준으로 clean candidate를 생성합니다.
2. Termux/Android 호환 변경 사항을 적용합니다.
3. 패치 계약과 소스 호환성을 검증합니다.
4. Android ARM64용 Codex와 V8/code-mode 구성요소를 빌드합니다.
5. 설치 가능한 npm-format `.tgz` 패키지를 생성합니다.
6. 성공한 결과를 이 저장소의 GitHub Release로 게시합니다.

따라서 일반 사용자는 Rust toolchain이나 Android NDK를 직접 설치해 빌드할 필요가 없습니다.

## Termux 호환 변경

현재 포트에는 다음과 같은 Android/Termux 대응이 포함됩니다.

- 브라우저 로그인 시 `termux-open-url` 사용
- Android/Bionic에서 동작하지 않는 파일 잠금 및 PTY 동작 보정
- Termux 환경에 맞는 daemon/process 처리
- Android ARM64 native launcher
- `libc++_shared.so` 번들
- native binary 직접 실행을 위한 `RUNPATH=$ORIGIN`
- Android용 V8 prebuilt를 이용한 code-mode 지원
- Termux 환경에 맞는 실행 경로 및 환경 변수 처리

구체적인 패치 목록은 [patches/README.md](./patches/README.md)를 참고하세요.

## 문서

- [변경 내역](./CHANGELOG.md)
- [Termux 패치 목록](./patches/README.md)
- [소스 빌드](./BUILDING.md)
- [인증](./docs/authentication.md)
- [설정](./docs/config.md)

## 보안 및 배포

설치 패키지는 이 저장소의 GitHub Actions에서 생성하고 GitHub Release를 통해 배포합니다.

배포 파일을 직접 내려받아 설치하는 경우 Release 출처가 `inchury/codex-termux`인지 확인하는 것을 권장합니다. 자동 빌드 과정에서는 설치용 `.tgz`와 SHA-256 체크섬을 생성하므로, 필요하면 설치 전에 체크섬을 비교할 수 있습니다.

이 프로젝트는 커뮤니티 포트이므로 보안이 특히 중요한 환경에서는 공식 OpenAI Codex가 지원하는 플랫폼에서 공식 배포판을 사용하는 것을 권장합니다.

취약점 관련 내용은 [SECURITY.md](./SECURITY.md)를 참고하세요.

## Upstream

원본 프로젝트:

https://github.com/openai/codex

이 저장소는 upstream Codex의 기능 개발을 대체하지 않습니다. Android/Termux에서 실행하기 위해 필요한 호환 계층과 배포 자동화를 유지하는 것이 목적입니다.

## License

Apache License 2.0을 따릅니다.

- Original project: OpenAI Codex
- Android / Termux compatibility port: `inchury/codex-termux`

자세한 내용은 [LICENSE](./LICENSE)를 참고하세요.
