#!/usr/bin/env bash
# Publish/update a Homebrew tap formula from a tagged GitHub release.
set -euo pipefail

DEFAULT_TAP_URL="https://github.com/shahpoll/homebrew-qe.git"
DEFAULT_FORMULA_NAME="qe-apple-silicon-build"
DEFAULT_ALIASES="qe,qe-macos"

VERSION_TAG=""
TAP_URL="$DEFAULT_TAP_URL"
TAP_DIR=""
FORMULA_NAME="$DEFAULT_FORMULA_NAME"
ALIASES="$DEFAULT_ALIASES"
COMMIT_MESSAGE=""
NO_PUSH=0
DRY_RUN=0
KEEP_TAP_DIR=0

usage() {
  cat <<'USAGE'
Usage: scripts/publish_homebrew_tap.sh --version <tag> [options]

Required:
  --version <tag>         Release tag like v1.2.0

Options:
  --tap-url <url>         Tap repo URL (default: https://github.com/shahpoll/homebrew-qe.git)
  --tap-dir <path>        Existing local tap clone (default: temp clone)
  --formula-name <name>   Formula filename (default: qe-apple-silicon-build)
  --aliases <csv>         Alias names (default: qe,qe-macos)
  --message <msg>         Commit message for tap update
  --no-push               Commit locally without pushing
  --dry-run               Preview staged tap changes
  --keep-tap-dir          Keep temporary tap clone directory
  -h, --help              Show this help

Examples:
  bash scripts/publish_homebrew_tap.sh --version v1.2.0
  bash scripts/publish_homebrew_tap.sh --version v1.2.0 --dry-run
  bash scripts/publish_homebrew_tap.sh --version v1.2.0 --aliases "qe,qe-macos,qe-asb,qe-build"
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION_TAG="$2"
      shift 2
      ;;
    --tap-url)
      TAP_URL="$2"
      shift 2
      ;;
    --tap-dir)
      TAP_DIR="$2"
      shift 2
      ;;
    --formula-name)
      FORMULA_NAME="$2"
      shift 2
      ;;
    --aliases)
      ALIASES="$2"
      shift 2
      ;;
    --message)
      COMMIT_MESSAGE="$2"
      shift 2
      ;;
    --no-push)
      NO_PUSH=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --keep-tap-dir)
      KEEP_TAP_DIR=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$VERSION_TAG" ]]; then
  echo "--version is required." >&2
  usage
  exit 2
fi

if [[ ! "$VERSION_TAG" =~ ^v[0-9] ]]; then
  echo "Version tag should look like v1.2.0 (got: $VERSION_TAG)" >&2
  exit 2
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "Missing required command: curl" >&2
  exit 3
fi

if ! command -v shasum >/dev/null 2>&1; then
  echo "Missing required command: shasum" >&2
  exit 3
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Missing required command: git" >&2
  exit 3
fi

TEMP_TAP_DIR=0
if [[ -z "$TAP_DIR" ]]; then
  TAP_DIR=$(mktemp -d)
  TEMP_TAP_DIR=1
else
  mkdir -p "$TAP_DIR"
fi

cleanup() {
  if [[ $TEMP_TAP_DIR -eq 1 && $KEEP_TAP_DIR -eq 0 ]]; then
    rm -rf "$TAP_DIR"
  fi
}
trap cleanup EXIT

if [[ -d "$TAP_DIR/.git" ]]; then
  git -C "$TAP_DIR" fetch --all --prune
  BRANCH=$(git -C "$TAP_DIR" rev-parse --abbrev-ref HEAD)
  git -C "$TAP_DIR" pull --ff-only origin "$BRANCH"
else
  git clone "$TAP_URL" "$TAP_DIR"
fi

SOURCE_URL="https://github.com/shahpoll/qe_apple_silicon_build/archive/refs/tags/${VERSION_TAG}.tar.gz"
SOURCE_TARBALL=$(mktemp)
curl -LfsS "$SOURCE_URL" -o "$SOURCE_TARBALL"
SHA256=$(shasum -a 256 "$SOURCE_TARBALL" | awk '{print $1}')
rm -f "$SOURCE_TARBALL"

FORMULA_CLASS=$(echo "$FORMULA_NAME" | awk -F '-' '{for (i=1; i<=NF; i++) printf toupper(substr($i,1,1)) substr($i,2); printf "\n"}')
FORMULA_PATH="$TAP_DIR/Formula/${FORMULA_NAME}.rb"
mkdir -p "$TAP_DIR/Formula"

cat > "$FORMULA_PATH" <<EOF
class ${FORMULA_CLASS} < Formula
  desc "One-command installer/updater and migration validator for QE on Apple Silicon"
  homepage "https://github.com/shahpoll/qe_apple_silicon_build"
  url "${SOURCE_URL}"
  sha256 "${SHA256}"
  license "MIT"
  head "https://github.com/shahpoll/qe_apple_silicon_build.git", branch: "main"

  depends_on "python@3.13"
  depends_on "open-mpi"
  depends_on "gcc"
  depends_on "cmake"
  depends_on "veclibfort"

  def install
    libexec.install Dir["*"]
    bin.install_symlink libexec/"bin/qe-apple-silicon-build"
  end

  def caveats
    <<~EOS
      qe-apple-silicon-build is now installed. To install Quantum ESPRESSO, run:

        qe-apple-silicon-build install --qe-tag qe-7.5 --install-prefix "\$HOME/opt/qe-7.5"

      Or use the interactive menu:

        qe-apple-silicon-build menu

      After installation, validate your build with:

        qe-apple-silicon-build check --qe-bin "\$HOME/opt/qe-7.5/bin"

      For full documentation, see:
        https://github.com/shahpoll/qe_apple_silicon_build

      Tip: short alias install (if enabled in this tap):
        brew install shahpoll/qe/qe
    EOS
  end

  test do
    assert_match "Usage:", shell_output("#{bin}/qe-apple-silicon-build help")
  end
end
EOF

mkdir -p "$TAP_DIR/Aliases"
find "$TAP_DIR/Aliases" -type l -delete
IFS=',' read -r -a ALIAS_LIST <<< "$ALIASES"
PRIMARY_ALIAS=""
for alias in "${ALIAS_LIST[@]}"; do
  alias=$(echo "$alias" | tr -d '[:space:]')
  if [[ -z "$alias" || "$alias" == "$FORMULA_NAME" ]]; then
    continue
  fi
  ln -snf "../Formula/${FORMULA_NAME}.rb" "$TAP_DIR/Aliases/$alias"
  if [[ -z "$PRIMARY_ALIAS" ]]; then
    PRIMARY_ALIAS="$alias"
  fi
done

README_PATH="$TAP_DIR/README.md"
if [[ ! -f "$README_PATH" ]]; then
  cat > "$README_PATH" <<EOF
# homebrew-qe

Homebrew tap for QE Apple Silicon build tooling.

Install (canonical formula):

\`\`\`sh
brew tap shahpoll/qe
brew install shahpoll/qe/${FORMULA_NAME}
\`\`\`
EOF
  if [[ -n "$PRIMARY_ALIAS" ]]; then
    cat >> "$README_PATH" <<EOF

Short alias:

\`\`\`sh
brew install shahpoll/qe/${PRIMARY_ALIAS}
\`\`\`
EOF
  fi
fi

git -C "$TAP_DIR" add Formula Aliases README.md

if git -C "$TAP_DIR" diff --cached --quiet; then
  echo "No tap changes detected."
  exit 0
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry run; staged tap changes:"
  git -C "$TAP_DIR" status --short
  exit 0
fi

if [[ -z "$COMMIT_MESSAGE" ]]; then
  COMMIT_MESSAGE="Release ${VERSION_TAG}: update ${FORMULA_NAME} formula"
fi
git -C "$TAP_DIR" commit -m "$COMMIT_MESSAGE"

if [[ $NO_PUSH -eq 0 ]]; then
  BRANCH=$(git -C "$TAP_DIR" rev-parse --abbrev-ref HEAD)
  git -C "$TAP_DIR" push origin "$BRANCH"
fi

echo "Tap formula ready in: $TAP_DIR"
echo "Formula: Formula/${FORMULA_NAME}.rb"
echo "sha256: $SHA256"
