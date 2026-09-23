# Contributing to NEXUS

## Branch strategy

- `main` — stable, always deployable.
- `develop` — integration branch for completed phases/features.
- `feature/<short-description>` — one branch per unit of work, branched
  from `develop`.

## Workflow

1. Branch from `develop`: `git checkout -b feature/my-change develop`
2. Make focused commits using
   [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat: add incident triage agent`
   - `fix: handle malformed agent output`
   - `test: add RAG grounding tests`
   - `docs: add deployment guide`
   - `ci: add evaluation quality gate`
3. Ensure the relevant test suite passes locally before opening a PR:
   - Backend: `make backend-test && make backend-lint`
   - Frontend: `make frontend-test && make frontend-build`
4. Open a PR into `develop`. CI (`.github/workflows/ci.yml`) must pass.
5. After review, merge into `develop`. `develop` is periodically merged
   into `main` at phase boundaries.

## Code standards

- Backend: type-hinted Python, `ruff` clean, `mypy` clean, `pytest` for all
  new logic.
- Frontend: TypeScript strict mode, `tsc -b` clean, `vitest` for new
  components/utilities.
- No secrets, credentials, or real company data in any commit.
- No placeholder/TODO logic in code paths described as complete — if
  something is intentionally deferred to a later phase, say so explicitly
  in `IMPLEMENTATION_STATUS.md`, not as a silent stub.

## Reporting issues

Use GitHub Issues. For security-related reports, see
[`SECURITY.md`](./SECURITY.md) instead of filing a public issue.
