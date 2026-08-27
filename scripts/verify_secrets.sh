#!/usr/bin/env bash
set -euo pipefail

readonly GITLEAKS_VERSION="8.30.1"
readonly GITLEAKS_ARCHIVE="gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
readonly GITLEAKS_SHA256="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
readonly GITLEAKS_URL="https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/${GITLEAKS_ARCHIVE}"

scan_bin="$(command -v gitleaks || true)"
scan_dir=""
if [[ -n "${scan_bin}" ]] && [[ "$("${scan_bin}" version)" != "${GITLEAKS_VERSION}" ]]; then
  scan_bin=""
fi
if [[ -z "${scan_bin}" ]]; then
  scan_dir="$(mktemp -d)"
  trap 'rm -rf -- "${scan_dir}"' EXIT
  curl --fail --silent --show-error --location --retry 3 \
    "${GITLEAKS_URL}" --output "${scan_dir}/${GITLEAKS_ARCHIVE}"
  printf '%s  %s\n' "${GITLEAKS_SHA256}" "${scan_dir}/${GITLEAKS_ARCHIVE}" | sha256sum --check --status
  tar -xzf "${scan_dir}/${GITLEAKS_ARCHIVE}" -C "${scan_dir}" gitleaks
  scan_bin="${scan_dir}/gitleaks"
fi

"${scan_bin}" dir . --redact --no-banner
"${scan_bin}" git . --log-opts="--all" --redact --no-banner
