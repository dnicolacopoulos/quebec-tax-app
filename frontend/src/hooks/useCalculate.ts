import { useState, useCallback } from 'react';
import axios from 'axios';
import type { CalculateRequest, CalculationResult } from '../types/api';

const API_BASE =
  (import.meta.env.VITE_API_BASE as string | undefined) ??
  'http://localhost:8000/api';

type FormData = Partial<CalculateRequest> & {
  inherited: boolean;
  cca_claimed: boolean;
  has_mortgage: boolean;
  selling_costs_pct: number;
  other_annual_income: number;
};

const DEFAULT_FORM: FormData = {
  inherited: false,
  cca_claimed: false,
  has_mortgage: false,
  selling_costs_pct: 5.0,
  other_annual_income: 0,
};

export function useCalculate() {
  const [formData, setFormData] = useState<FormData>(DEFAULT_FORM);
  const [result, setResult] = useState<CalculationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const updateField = useCallback(
    <K extends keyof FormData>(key: K, value: FormData[K]) => {
      setFormData((prev) => {
        const next = { ...prev, [key]: value };
        // Clear conditional fields when their gating toggle is turned off
        if (key === 'inherited' && !value) {
          next.fmv_at_death = undefined;
        }
        if (key === 'cca_claimed' && !value) {
          next.original_cost = undefined;
          next.ucc = undefined;
        }
        if (key === 'has_mortgage' && !value) {
          next.mortgage_balance = undefined;
          next.mortgage_annual_rate = undefined;
          next.mortgage_months_remaining = undefined;
        }
        return next;
      });
      // Clear result when any input changes so it's not stale
      setResult(null);
      setError(null);
    },
    [],
  );

  const calculate = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.post<CalculationResult>(
        `${API_BASE}/calculate`,
        formData,
      );
      setResult(data);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.data?.detail) {
        setError(String(err.response.data.detail));
      } else {
        setError('Calculation failed. Is the backend running?');
      }
    } finally {
      setLoading(false);
    }
  }, [formData]);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  const resetAll = useCallback(() => {
    setFormData(DEFAULT_FORM);
    setResult(null);
    setError(null);
  }, []);

  return {
    formData,
    result,
    loading,
    error,
    updateField,
    calculate,
    reset,
    resetAll,
  };
}
