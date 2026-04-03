import type { CalculateRequest } from '../types/api';

// ── Shared input primitives ───────────────────────────────────────────────

interface CurrencyInputProps {
    id: string;
    label: string;
    hint?: string;
    value: number | undefined;
    onChange: (v: number | undefined) => void;
    required?: boolean;
}

function CurrencyInput({ id, label, hint, value, onChange, required }: CurrencyInputProps) {
    return (
        <div className="flex flex-col gap-1">
            <label htmlFor={id} className="text-sm text-slate-300">
                {label}
                {required && <span className="text-red-400 ml-0.5">*</span>}
            </label>
            {hint && <p className="text-xs text-slate-500 -mt-0.5">{hint}</p>}
            <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm select-none">$</span>
                <input
                    id={id}
                    type="number"
                    inputMode="decimal"
                    min={0}
                    step="any"
                    value={value ?? ''}
                    placeholder="0"
                    onChange={(e) => onChange(e.target.value === '' ? undefined : parseFloat(e.target.value))}
                    className="w-full rounded-lg bg-slate-800 border border-slate-600 text-white text-sm py-2.5 pl-7 pr-3
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-slate-600"
                />
            </div>
        </div>
    );
}

interface PercentageInputProps {
    id: string;
    label: string;
    hint?: string;
    value: number;
    onChange: (v: number) => void;
}

function PercentageInput({ id, label, hint, value, onChange }: PercentageInputProps) {
    return (
        <div className="flex flex-col gap-1">
            <label htmlFor={id} className="text-sm text-slate-300">{label}</label>
            {hint && <p className="text-xs text-slate-500 -mt-0.5">{hint}</p>}
            <div className="relative">
                <input
                    id={id}
                    type="number"
                    inputMode="decimal"
                    min={0}
                    max={100}
                    step="any"
                    value={value}
                    onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
                    className="w-full rounded-lg bg-slate-800 border border-slate-600 text-white text-sm py-2.5 pl-3 pr-8
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
                <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm select-none">%</span>
            </div>
        </div>
    );
}

interface NumberInputProps {
    id: string;
    label: string;
    hint?: string;
    value: number | undefined;
    onChange: (v: number | undefined) => void;
    required?: boolean;
}

function NumberInput({ id, label, hint, value, onChange, required }: NumberInputProps) {
    return (
        <div className="flex flex-col gap-1">
            <label htmlFor={id} className="text-sm text-slate-300">
                {label}
                {required && <span className="text-red-400 ml-0.5">*</span>}
            </label>
            {hint && <p className="text-xs text-slate-500 -mt-0.5">{hint}</p>}
            <input
                id={id}
                type="number"
                inputMode="numeric"
                min={0}
                step={1}
                value={value ?? ''}
                placeholder="0"
                onChange={(e) => onChange(e.target.value === '' ? undefined : parseInt(e.target.value, 10))}
                className="w-full rounded-lg bg-slate-800 border border-slate-600 text-white text-sm py-2.5 px-3
          focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder:text-slate-600"
            />
        </div>
    );
}

interface ToggleChipsProps {
    id: string;
    label: string;
    hint?: string;
    value: boolean;
    onChange: (v: boolean) => void;
}

function ToggleChips({ id, label, hint, value, onChange }: ToggleChipsProps) {
    return (
        <div className="flex flex-col gap-1">
            <span className="text-sm text-slate-300">{label}</span>
            {hint && <p className="text-xs text-slate-500 -mt-0.5">{hint}</p>}
            <div className="flex gap-2" role="group" aria-labelledby={id}>
                <button
                    type="button"
                    onClick={() => onChange(true)}
                    className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors
            ${value
                            ? 'bg-indigo-600 text-white ring-2 ring-indigo-400'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                >
                    Yes
                </button>
                <button
                    type="button"
                    onClick={() => onChange(false)}
                    className={`px-5 py-2 rounded-lg text-sm font-medium transition-colors
            ${!value
                            ? 'bg-slate-600 text-white ring-2 ring-slate-400'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                >
                    No
                </button>
            </div>
        </div>
    );
}

interface SectionProps {
    title: string;
    children: React.ReactNode;
}

function Section({ title, children }: SectionProps) {
    return (
        <fieldset className="rounded-xl bg-slate-800/60 border border-slate-700 px-5 py-4 flex flex-col gap-4">
            <legend className="text-xs font-semibold uppercase tracking-widest text-slate-400 px-1">{title}</legend>
            {children}
        </fieldset>
    );
}

// ── Form grid helper ──────────────────────────────────────────────────────

function Row({ children }: { children: React.ReactNode }) {
    return <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{children}</div>;
}

// ── Validation ────────────────────────────────────────────────────────────

type FormData = Partial<CalculateRequest> & {
    inherited: boolean;
    cca_claimed: boolean;
    has_mortgage: boolean;
    selling_costs_pct: number;
    other_annual_income: number;
};

function isValid(f: FormData): boolean {
    if (!f.sale_price) return false;
    if (f.inherited && !f.fmv_at_death) return false;
    if (!f.inherited && !f.user_acb) return false;
    if (f.cca_claimed && (!f.original_cost || !f.ucc)) return false;
    if (!f.monthly_gross_rent) return false;
    if (f.has_mortgage && (!f.mortgage_balance || !f.mortgage_annual_rate || !f.mortgage_months_remaining)) return false;
    return true;
}

// ── Main component ────────────────────────────────────────────────────────

interface Props {
    formData: FormData;
    loading: boolean;
    error: string | null;
    updateField: <K extends keyof FormData>(key: K, value: FormData[K]) => void;
    onSubmit: (e: React.FormEvent) => void;
}

export default function PropertyForm({ formData, loading, error, updateField, onSubmit }: Props) {
    const canSubmit = isValid(formData) && !loading;

    return (
        <form onSubmit={onSubmit} className="flex flex-col gap-5">
            {/* Property Details */}
            <Section title="Property Details">
                <ToggleChips
                    id="inherited"
                    label="Was this property inherited?"
                    value={formData.inherited}
                    onChange={(v) => updateField('inherited', v)}
                />
                {formData.inherited ? (
                    <CurrencyInput
                        id="fmv_at_death"
                        label="Fair Market Value at date of death"
                        hint="Becomes the Adjusted Cost Base (deemed disposition rule)."
                        value={formData.fmv_at_death ?? undefined}
                        onChange={(v) => updateField('fmv_at_death', v)}
                        required
                    />
                ) : (
                    <CurrencyInput
                        id="user_acb"
                        label="Adjusted Cost Base (ACB)"
                        hint="Original purchase price plus capital improvements."
                        value={formData.user_acb ?? undefined}
                        onChange={(v) => updateField('user_acb', v)}
                        required
                    />
                )}
                <Row>
                    <CurrencyInput
                        id="sale_price"
                        label="Expected sale price"
                        value={formData.sale_price}
                        onChange={(v) => updateField('sale_price', v)}
                        required
                    />
                    <PercentageInput
                        id="selling_costs_pct"
                        label="Selling costs"
                        hint="Notary, commission, etc. Typically 4–7%."
                        value={formData.selling_costs_pct}
                        onChange={(v) => updateField('selling_costs_pct', v)}
                    />
                </Row>
            </Section>

            {/* Capital Cost Allowance */}
            <Section title="Capital Cost Allowance (CCA)">
                <ToggleChips
                    id="cca_claimed"
                    label="Have you ever claimed CCA (depreciation) on this property?"
                    value={formData.cca_claimed}
                    onChange={(v) => updateField('cca_claimed', v)}
                />
                {formData.cca_claimed && (
                    <Row>
                        <CurrencyInput
                            id="original_cost"
                            label="Original depreciable cost of the building"
                            hint="Purchase price allocated to the building (not land)."
                            value={formData.original_cost ?? undefined}
                            onChange={(v) => updateField('original_cost', v)}
                            required
                        />
                        <CurrencyInput
                            id="ucc"
                            label="Undepreciated Capital Cost (UCC)"
                            hint="From your most recent T776 / TP-128."
                            value={formData.ucc ?? undefined}
                            onChange={(v) => updateField('ucc', v)}
                            required
                        />
                    </Row>
                )}
            </Section>

            {/* Rental Income & Expenses */}
            <Section title="Rental Income & Expenses">
                <Row>
                    <CurrencyInput
                        id="monthly_gross_rent"
                        label="Monthly gross rental income"
                        value={formData.monthly_gross_rent}
                        onChange={(v) => updateField('monthly_gross_rent', v)}
                        required
                    />
                    <CurrencyInput
                        id="monthly_expenses"
                        label="Monthly operating expenses"
                        hint="Insurance, maintenance, property tax, etc. Exclude mortgage."
                        value={formData.monthly_expenses}
                        onChange={(v) => updateField('monthly_expenses', v)}
                        required
                    />
                </Row>
            </Section>

            {/* Mortgage */}
            <Section title="Mortgage">
                <ToggleChips
                    id="has_mortgage"
                    label="Is there an outstanding mortgage on this property?"
                    value={formData.has_mortgage}
                    onChange={(v) => updateField('has_mortgage', v)}
                />
                {formData.has_mortgage && (
                    <>
                        <Row>
                            <CurrencyInput
                                id="mortgage_balance"
                                label="Outstanding mortgage balance"
                                value={formData.mortgage_balance ?? undefined}
                                onChange={(v) => updateField('mortgage_balance', v)}
                                required
                            />
                            <PercentageInput
                                id="mortgage_annual_rate"
                                label="Mortgage interest rate"
                                hint="E.g. 4.5 for 4.5%."
                                value={formData.mortgage_annual_rate ?? 0}
                                onChange={(v) => updateField('mortgage_annual_rate', v)}
                            />
                        </Row>
                        <NumberInput
                            id="mortgage_months_remaining"
                            label="Months remaining on amortization"
                            hint="E.g. 240 for 20 years."
                            value={formData.mortgage_months_remaining ?? undefined}
                            onChange={(v) => updateField('mortgage_months_remaining', v)}
                            required
                        />
                    </>
                )}
            </Section>

            {/* Tax Profile */}
            <Section title="Tax Profile">
                <CurrencyInput
                    id="other_annual_income"
                    label="Other annual taxable income (employment, pension, etc.)"
                    hint="Used to determine your marginal tax bracket. Leave 0 if none."
                    value={formData.other_annual_income || undefined}
                    onChange={(v) => updateField('other_annual_income', v ?? 0)}
                />
            </Section>

            {/* Submit */}
            {error && (
                <p className="text-sm text-red-400 text-center">{error}</p>
            )}
            <button
                type="submit"
                disabled={!canSubmit}
                className="w-full py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500
          disabled:opacity-40 disabled:cursor-not-allowed
          text-white font-semibold text-base transition-colors"
            >
                {loading ? 'Calculating…' : 'Calculate'}
            </button>
        </form>
    );
}
