"""
FastAPI routes: session-based wizard.

POST /sessions                     → create session, return first question
POST /sessions/{session_id}/answer → submit answer, return next question or result

Sessions are stored in-memory (dict keyed by UUID).  For a PoC this is fine;
a production version would use Redis or a database.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AnswerRequest,
    AnswerResponse,
    CalculateRequest,
    CalculationResult,
    SessionCreatedResponse,
)
from app.graph.graph import next_step
from app.graph.state import PropertyState
from app.graph.nodes import QUESTIONS, node_calculate

router = APIRouter()

# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

SESSION_TTL = timedelta(hours=1)

_sessions: dict[str, dict[str, Any]] = {}


def _purge_expired() -> None:
    """Remove sessions older than SESSION_TTL."""
    cutoff = datetime.utcnow() - SESSION_TTL
    expired = [sid for sid, s in _sessions.items() if s["created_at"] < cutoff]
    for sid in expired:
        del _sessions[sid]


def _new_session() -> tuple[str, PropertyState]:
    _purge_expired()
    session_id = str(uuid.uuid4())
    state: PropertyState = {"step": "", "history": []}
    _sessions[session_id] = {"state": state, "created_at": datetime.utcnow()}
    return session_id, state


def _get_session(session_id: str) -> PropertyState:
    rec = _sessions.get(session_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Session not found or expired.")
    return rec["state"]


# ---------------------------------------------------------------------------
# Coerce raw answer value to the correct Python type for a given step
# ---------------------------------------------------------------------------

_BOOLEAN_STEPS = {"inherited", "cca_claimed", "has_mortgage"}
_INT_STEPS = {"mortgage_months_remaining"}


def _coerce(step: str, raw: Any) -> Any:
    if step in _BOOLEAN_STEPS:
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, str):
            return raw.strip().lower() in ("yes", "true", "1", "y")
        return bool(raw)
    if step in _INT_STEPS:
        return int(float(raw))
    # percentage fields — store as float (the raw %, e.g. 5.0 or 4.5)
    if step in {"selling_costs_pct", "mortgage_annual_rate"}:
        return float(raw)
    return float(raw)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/sessions", response_model=SessionCreatedResponse, status_code=201)
def create_session() -> SessionCreatedResponse:
    session_id, state = _new_session()
    first_step = next_step(state)
    state["step"] = first_step
    question = QUESTIONS[first_step]
    return SessionCreatedResponse(session_id=session_id, question=question)


@router.post("/sessions/{session_id}/answer", response_model=AnswerResponse)
def submit_answer(session_id: str, body: AnswerRequest) -> AnswerResponse:
    state = _get_session(session_id)
    current_step = state.get("step", "")

    if current_step == "done":
        raise HTTPException(status_code=400, detail="Session is already complete.")

    # Store the answer
    coerced = _coerce(current_step, body.value)
    state[current_step] = coerced  # type: ignore[literal-required]

    # Append to chat history
    q = QUESTIONS.get(current_step)
    if q:
        state.setdefault("history", [])
        state["history"].append({"role": "assistant", "text": q.text})
        display = "Yes" if coerced is True else ("No" if coerced is False else str(coerced))
        state["history"].append({"role": "user", "text": display})

    # Determine next step
    target = next_step(state)

    if target == "calculate":
        node_calculate(state)
        result_raw = state.get("result")  # type: ignore[misc]
        if result_raw is None:
            raise HTTPException(status_code=500, detail="Calculation produced no result.")
        return AnswerResponse(result=CalculationResult(**result_raw))

    if target == "done":
        # Should not happen without going through calculate, but guard anyway
        raise HTTPException(status_code=500, detail="Unexpected state: done without result.")

    state["step"] = target
    return AnswerResponse(question=QUESTIONS[target])


# ---------------------------------------------------------------------------
# Direct calculation endpoint (form-based, no session required)
# ---------------------------------------------------------------------------


@router.post("/calculate", response_model=CalculationResult)
def calculate(body: CalculateRequest) -> CalculationResult:
    state: PropertyState = {
        "step": "other_annual_income",
        "history": [],
        "inherited": body.inherited,
        "fmv_at_death": body.fmv_at_death,
        "user_acb": body.user_acb,
        "sale_price": body.sale_price,
        "selling_costs_pct": body.selling_costs_pct,
        "cca_claimed": body.cca_claimed,
        "original_cost": body.original_cost,
        "ucc": body.ucc,
        "monthly_gross_rent": body.monthly_gross_rent,
        "monthly_expenses": body.monthly_expenses,
        "has_mortgage": body.has_mortgage,
        "mortgage_balance": body.mortgage_balance,
        "mortgage_annual_rate": body.mortgage_annual_rate,
        "mortgage_months_remaining": body.mortgage_months_remaining,
        "other_annual_income": body.other_annual_income,
    }
    node_calculate(state)
    result_raw = state.get("result")
    if result_raw is None:
        raise HTTPException(status_code=500, detail="Calculation produced no result.")
    return CalculationResult(**result_raw)
