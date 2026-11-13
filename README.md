# SJDAS — Jacquard design automation research

SJDAS is a Python-based jacquard-pattern design workspace. The repository includes a PyQt6 desktop interface, image-processing and drafting modules, FastAPI services, loom-oriented export experiments, tests and design notes.

**Status:** active engineering work / prototype. This README documents the code present in the repository. It does not certify a particular loom controller, a production release, zero defects or full test coverage.

## Repository map

| Location | Purpose |
| --- | --- |
| `launcher.py` | Starts the PyQt6 desktop app and initialises services |
| `sj_das/` | Designer UI, textile processing and supporting modules |
| `backend/main.py` | FastAPI application with analysis, export and integration routers |
| `backend/routers/` | API modules grouped by operation |
| `tests/` | Test modules for core functionality and integration cases |
| `docs/` | Specifications, integration notes and project discussions |
| `docker-compose.yml` | Backend API and Redis development stack |

## Development setup

The application is desktop-first. Use a Python virtual environment; install dependencies for the part you intend to run.

```bash
git clone https://github.com/BalajiKoushik01/SJDAS.git
cd SJDAS
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python launcher.py
```

Some PyQt, Torch, computer-vision and graphics modules depend on OS libraries, GPU support or separately provisioned model weights. If installation fails, inspect the imported modules and platform requirements before treating it as a code defect.

The API has a separate dependency list at `backend/requirements.txt`. Its startup validates production-related settings, including JWT configuration and allowed origins. See `DEPLOYMENT.md` and the relevant environment example before exposing endpoints.

## Tests

```bash
python -m pytest tests/
```

Pytest settings in `pyproject.toml` enable coverage reporting. No assertion about current pass rate or percentage coverage is made here; run the suite in the target environment and record results before a release.

## Before using exported designs on a loom

- Verify dimensions, indexed colours, float lengths and controller-specific output requirements.
- Review each design in the factory's normal inspection workflow.
- Test on the intended loom/controller combination and document the result.
- Do not assume that source-code support for an export format proves hardware interoperability.

See the [release evidence requirements](docs/RELEASE_EVIDENCE.md), the project specifications and `docs/product/` for design intent. Those documents may describe planned behaviour, not necessarily fully implemented features.

## Security and deployment

Keep factory credentials, model keys and tenant data out of Git. Production operation requires independent assessment of authentication, storage, background workers and equipment safety. None of the repository's promotional version labels is evidence of external certification.
