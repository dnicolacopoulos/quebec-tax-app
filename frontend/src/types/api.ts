// API type definitions mirroring backend Pydantic schemas

export type QuestionType = 'currency' | 'number' | 'percentage' | 'yesno';

export interface Question {
  key: string;
  text: string;
  type: QuestionType;
  default?: number | boolean | null;
  hint?: string | null;
}

export interface AnswerRequest {
  value: number | boolean | string;
}

// --- Result types ---

export interface TaxBreakdown {
  recapture_income: number;
  capital_gain: number;
  taxable_capital_gain: number;
  federal_tax: number;
  provincial_tax: number;
  total_tax: number;
}

export interface SellYearPoint {
  year: number;
  value: number;
}

export interface KeepYearPoint {
  year: number;
  property_value: number;
  mortgage_balance: number;
  equity: number;
  annual_cash_flow: number;
  cumulative_cash_flow: number;
  total: number;
}

export interface ResultSummary {
  selling_costs: number;
  tax_breakdown: TaxBreakdown;
  sell_net_proceeds: number;
  sell_year_10: number;
  keep_equity_year_10: number;
  keep_cumulative_cf_year_10: number;
  keep_total_year_10: number;
  recommendation: 'sell' | 'keep' | 'similar';
  recommendation_delta: number;
}

export interface CalculationResult {
  summary: ResultSummary;
  sell_series: SellYearPoint[];
  keep_series: KeepYearPoint[];
}

// --- API responses ---

export interface SessionCreatedResponse {
  session_id: string;
  question: Question;
}

export interface AnswerResponse {
  question?: Question;
  result?: CalculationResult;
}
