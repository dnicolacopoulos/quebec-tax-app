import { useState, useCallback } from 'react';
import axios from 'axios';
import type {
  Question,
  CalculationResult,
  SessionCreatedResponse,
  AnswerResponse,
} from '../types/api';

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  'http://localhost:8000/api';

interface SessionState {
  sessionId: string | null;
  currentQuestion: Question | null;
  result: CalculationResult | null;
  history: { role: 'assistant' | 'user'; text: string }[];
  loading: boolean;
  error: string | null;
}

export function useSession() {
  const [state, setState] = useState<SessionState>({
    sessionId: null,
    currentQuestion: null,
    result: null,
    history: [],
    loading: false,
    error: null,
  });

  const createSession = useCallback(async () => {
    setState((s) => ({ ...s, loading: true, error: null }));
    try {
      const { data } = await axios.post<SessionCreatedResponse>(
        `${API_BASE}/sessions`,
      );
      setState((s) => ({
        ...s,
        sessionId: data.session_id,
        currentQuestion: data.question,
        history: [{ role: 'assistant', text: data.question.text }],
        loading: false,
      }));
    } catch {
      setState((s) => ({
        ...s,
        loading: false,
        error: 'Failed to start session. Is the backend running?',
      }));
    }
  }, []);

  const sendAnswer = useCallback(
    async (value: number | boolean | string) => {
      if (!state.sessionId || !state.currentQuestion) return;
      setState((s) => ({ ...s, loading: true, error: null }));

      const displayValue =
        typeof value === 'boolean' ? (value ? 'Yes' : 'No') : String(value);

      try {
        const { data } = await axios.post<AnswerResponse>(
          `${API_BASE}/sessions/${state.sessionId}/answer`,
          { value },
        );

        if (data.result) {
          setState((s) => ({
            ...s,
            loading: false,
            result: data.result!,
            currentQuestion: null,
            history: [...s.history, { role: 'user', text: displayValue }],
          }));
        } else if (data.question) {
          setState((s) => ({
            ...s,
            loading: false,
            currentQuestion: data.question!,
            history: [
              ...s.history,
              { role: 'user', text: displayValue },
              { role: 'assistant', text: data.question!.text },
            ],
          }));
        }
      } catch {
        setState((s) => ({
          ...s,
          loading: false,
          error: 'Something went wrong. Please try again.',
        }));
      }
    },
    [state.sessionId, state.currentQuestion],
  );

  const reset = useCallback(() => {
    setState({
      sessionId: null,
      currentQuestion: null,
      result: null,
      history: [],
      loading: false,
      error: null,
    });
  }, []);

  return { ...state, createSession, sendAnswer, reset };
}
