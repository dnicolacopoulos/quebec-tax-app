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

That's it — no local Python or Node installation is required.

---

## Quick start

```bash
git clone <repo-url>
cd quebec-tax-app
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend (React wizard) | http://localhost:5173 |
| Backend API | http://localhost:8000/api |

The first build downloads base images and installs dependencies — subsequent starts are fast.

To stop:

```bash
docker compose down
```

---

## Local development (optional)

If you want to edit code with full editor intelligence and fast feedback without rebuilding containers, set up the local tooling below.

### Backend

Requires **Python 3.12**.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Run the API locally (port 8000):

```bash
uvicorn app.main:app --reload
```

Lint and type-check:

```bash
ruff check app/
mypy app/ --ignore-missing-imports
```

### Frontend

Requires **Node 20 +**.

```bash
cd frontend
npm install
npm run dev        # starts Vite dev server on http://localhost:5173
npm run lint       # ESLint
npx tsc -b --noEmit  # TypeScript check
```

---

## Project layout

```
quebec-tax-app/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
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
