# Security Policy

## Scope

NEXUS is a portfolio/demonstration project using entirely synthetic data
and simulated infrastructure. It does not connect to real production
systems. That said, the codebase follows security-conscious defaults and
welcomes reports of real vulnerabilities in the code itself (e.g.
injection flaws, auth bypass, secret leakage).

## Reporting a vulnerability

Please do not open a public GitHub issue for security reports. Instead,
open a private security advisory on the repository (GitHub → Security →
Advisories → "Report a vulnerability"), or contact the maintainer directly
if that channel isn't available.

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix, if you have one

## Design principles this project follows

- No secrets committed to source control; all credentials load from
  environment variables.
- LLM output never executes as arbitrary shell commands or unrestricted
  SQL — actions go through an explicit allowlist (`app/tools/`, Phase 7).
- Retrieved documents (RAG) and user-submitted incident text are treated
  as untrusted data, never as trusted instructions (Phase 7 prompt
  injection defenses).
- Role-based authorization gates who can approve/execute remediation
  actions (Phase 7).
- All destructive-looking operations run against a simulated
  infrastructure layer, never real systems.

A full threat model is written in `docs/threat-model.md` as part of
Phase 0/7.
