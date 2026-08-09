# Case Study: soliloquy

**Repository:** [szmyty/soliloquy](https://github.com/szmyty/soliloquy)
**Maturity:** Active development — usable prototype
**Evidence ID:** `repo-soliloquy`

---

## Problem

Querying private documents against a large language model through cloud APIs
exposes document content to third-party servers and incurs ongoing API costs.
Developers and researchers who work with confidential PDFs, notes, or code have
no straightforward self-hosted alternative that runs in a single command.

## Architectural Approach

`soliloquy` is a single Docker Compose stack that wires together:

- **Ollama** — runs a quantised LLM locally (e.g., Mistral, LLaMA) with no
  external dependency;
- a **Python ingestion layer** — chunks and embeds PDF documents into a local
  vector store;
- a **query interface** — accepts natural-language questions and returns
  grounded answers sourced from the ingested documents.

All data remains on the host machine. The only network calls are to pull the
base Docker images and the model weights on first run; thereafter the stack
operates fully offline.

Key architectural boundaries:

| Boundary | Decision |
|----------|----------|
| Data locality | All embeddings and model weights are stored on the host volume |
| Model agnosticism | Ollama allows swapping models by changing a single environment variable |
| Single-command start | `docker compose up` bootstraps the entire stack |

## Alan's Role and Key Decisions

- Designed the overall single-compose-file architecture to minimise setup
  friction for other developers.
- Selected Ollama as the local model runtime for its cross-platform support
  and simple pull-and-serve model.
- Structured the ingestion pipeline to be document-type-agnostic so it can be
  extended beyond PDFs without architectural changes.

## Current Usable Artifact

The repository ships a `docker-compose.yml` and supporting Python scripts.
A developer with Docker installed can clone the repository and bring the stack
up in a single terminal session.

**Evidence:** [github.com/szmyty/soliloquy](https://github.com/szmyty/soliloquy)

## Maturity and Next Direction

| Attribute | Status |
|-----------|--------|
| Maturity | Usable prototype; not yet production-hardened |
| Test coverage | Minimal — integration tested manually |
| Documentation | README with setup instructions |
| Next direction | Add web UI, multi-document session state, and structured metadata filtering |
