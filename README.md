# Quebec Rental Property — Keep vs. Sell Decision Engine

A structured wizard that compares the **10-year net financial outcome** of selling a Quebec rental property versus keeping it, fully tax-adjusted for 2026 Quebec and federal rules.

**What it models**

- Capital gains tax (50% inclusion rate)
- CCA recapture (100% income inclusion)
- Progressive 2026 federal brackets (14 %–33 %) with 16.5 % Quebec abatement
- Progressive 2026 Quebec brackets (14 %–25.75 %)
- Mortgage amortisation and interest deductibility on the Keep side
- 7 %/yr ETF compound growth on the Sell & Reinvest side
- 3 %/yr property appreciation on the Keep & Rent side

---

## Prerequisites

| Tool | Minimum version |
|------|----------------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24 + |
| Docker Compose plugin | v2 (bundled with Docker Desktop) |

That's it — no local Python or Node installation is required to run the app.

---

## Quick start

```bash
git clone <repo-url>
cd quebec-tax-app
make up-build
```

| Service | URL |
|---------|-----|
| Frontend (React wizard) | http://localhost:5173 |
| Backend API | http://localhost:8000/api |

The first build downloads base images and installs dependencies — subsequent starts are fast.

To stop:

```bash
make down
```

---

## Make commands

Run `make help` from the repo root to see all available commands.

| Command | Description |
|---------|-------------|
| `make up-build` | Build images and start all services |
| `make up` | Start all services (detached, no rebuild) |
| `make down` | Stop all services |
| `make logs` | Tail logs from all services |
| `make test` | Run backend unit tests (verbose) |
| `make test-q` | Run backend unit tests (quiet) |
| `make lint` | Lint backend (ruff) + frontend (ESLint) |
| `make lint-fix` | Auto-fix lint issues |
| `make typecheck` | Type-check backend (mypy) + frontend (tsc) |
| `make check` | Run all checks — lint + typecheck + tests |

---

## Local development (optional)

If you want editor intelligence and fast feedback without rebuilding containers, set up the local tooling below. The `.venv` is used exclusively for tooling (lint, type-check, tests) — the container is the actual runtime.

### Backend

Requires **Python 3.12**.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pip install ruff mypy
```

Run the API locally (port 8000):

```bash
uvicorn app.main:app --reload
```

### Frontend

Requires **Node 20 +**.

```bash
cd frontend
npm install
npm run dev        # Vite dev server on http://localhost:5173
```

### VS Code

The workspace is pre-configured (`.vscode/settings.json`) to use `backend/.venv` as the Python interpreter, so Pylance resolves all imports without further setup.

---

## Testing

76 unit tests covering all calculation logic:

```bash
make test      # verbose
make test-q    # quiet
make check     # lint + typecheck + tests together
```

Tests are organised by module:

| File | What it covers |
|------|---------------|
| `tests/test_tax.py` | Bracket engine, federal/Quebec/combined tax, BPA credits, Quebec abatement, marginal stacking |
| `tests/test_capital_gains_cca.py` | ACB (including inherited/deemed disposition), capital gain, 50% inclusion, CCA recapture, terminal loss |
| `tests/test_scenarios.py` | Sell & Reinvest compound projection, mortgage payment formula, Keep & Rent 10-year projection |

---

## Project layout

```
quebec-tax-app/
├── Makefile                     # Dev and Docker shortcuts
├── docker-compose.yml
├── .gitignore
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── tests/                   # 76 pytest unit tests
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── api/routes.py        # Session endpoints
│       ├── calculators/         # Tax, CCA, capital gains, projections
│       ├── graph/               # LangGraph wizard state machine
│       └── models/schemas.py    # Pydantic models
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── src/
        ├── App.tsx
        ├── hooks/useSession.ts
        ├── components/          # QuestionCard, ChatWindow, ResultsPanel, ComparisonChart
        └── types/api.ts
```

---

## Tax constants

All 2026 tax parameters are hardcoded in [`backend/app/calculators/tax_config.py`](backend/app/calculators/tax_config.py). Update that file if brackets or rates change in a future year.

