# Docker images

Use this whenever a Dockerfile, `.dockerignore` or compose `build:` section is written, changed or reviewed. The aim is a small image that contains only what runs in production, built from a pinned base and running as a non-root user.

## Checklist

1. **Light, pinned base.** Use `-slim`, `-alpine`, distroless or `scratch`, and for Java a JRE rather than a JDK. Pin the tag to at least a minor version (`python:3.12-slim`, never `latest`). For images that ship to customers, pin the digest too.
2. **Multi-stage build** whenever anything is compiled or built: compilers, `gcc`, `build-essential`, the JDK, `npm run build`, `cargo build` and Python wheels with C extensions. The builder stage does the work, and the final stage copies in only the artifact, the venv or `node_modules` for production. A pure-Python app with only wheel dependencies may stay single-stage. Say so in the review.
3. **`.dockerignore` next to the build context**, excluding at least: `.git`, `.env*`, secrets, `.venv`/`venv`, `node_modules`, `__pycache__`, `tests`, `logs`, `*.db`, and docs that are not needed at runtime. An empty `.dockerignore` counts as missing.
4. **Clean up in the same layer.** Use `apt-get install --no-install-recommends ... && rm -rf /var/lib/apt/lists/*`, `pip install --no-cache-dir`, and `npm ci` followed by `npm cache clean --force`. A file deleted in a later layer still ships.
5. **Production dependencies only.** Use `npm ci --omit=dev`, and for Python a runtime `requirements.txt` without pytest, linters or type stubs; dev tools go in `requirements-dev.txt`.
6. **Non-root `USER`** in the final stage. If root is truly needed (cron, binding ports below 1024 without capabilities), write the reason in a comment.
7. **Cache-friendly order.** Copy the dependency manifests and install them first, then copy the source.
8. **`HEALTHCHECK`** for long-running services, unless compose already defines one.

## Checks that prove it

Run these before calling a Dockerfile done. Install the tools if missing: `winget install hadolint.hadolint wagoodman.dive` on Windows, `brew install hadolint dive` on macOS, or the release binaries from github.com/hadolint/hadolint and github.com/wagoodman/dive. `hadolint` does not flag a missing `USER`; check item 6 by hand.

- `hadolint <Dockerfile>`: fix every finding, or note why one is accepted (for example `DL3008` when a pinned apt version is not available on the distro).
- `docker build -t <name>:check <context>`, then `CI=true dive --ci --lowestEfficiency=0.9 --highestUserWastedPercent=0.1 <name>:check`: it must PASS, or the review states the efficiency and wasted bytes and why they are accepted.
- `docker history --format '{{.Size}}\t{{.CreatedBy}}' <name>:check | head -15` to find the biggest layers, and `docker image inspect <name>:check --format '{{.Size}}'` for the before/after size. Report measured sizes only.

## Scope notes

- Vendor or upstream images are not rebuilt only to satisfy this list. Flag issues; change only what you own.
- Copies of the same Dockerfile across repos or branches are fixed in the source repo, then carried over. Production repos follow the usual approval rules.
