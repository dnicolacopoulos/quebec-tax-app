import type { CalculationResult } from '../types/api';

interface Props {
    result: CalculationResult;
    onReset: () => void;
}

const fmt = (n: number) =>
    n.toLocaleString('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 });

export default function ResultsPanel({ result, onReset }: Props) {
    const { summary } = result;
    const { tax_breakdown: td } = summary;

    const rec = summary.recommendation;
    const verdictLabel = rec === 'sell' ? 'Sell & Reinvest' : rec === 'keep' ? 'Keep & Rent' : 'Too Close to Call';
    const verdictColor =
        rec === 'sell'
            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
            : rec === 'keep'
                ? 'bg-blue-500/20 text-blue-300 border-blue-500/40'
                : 'bg-amber-500/20 text-amber-300 border-amber-500/40';

    return (
        <div className="h-full overflow-y-auto px-4 py-4 space-y-4">
            {/* Verdict */}
            <div className={`rounded-2xl border px-5 py-4 text-center ${verdictColor}`}>
                <p className="text-xs uppercase tracking-widest mb-1 opacity-70">10-Year Recommendation</p>
                <p className="text-2xl font-bold">{verdictLabel}</p>
                {rec !== 'similar' && (
                    <p className="text-sm mt-1 opacity-80">
                        Advantage: {fmt(summary.recommendation_delta)} over 10 years
                    </p>
                )}
            </div>

            {/* Side-by-side Y10 cards */}
            <div className="grid grid-cols-2 gap-3">
                <div className="rounded-xl bg-slate-800 border border-slate-700 p-4">
                    <p className="text-xs text-slate-400 mb-1">Sell & Reinvest (Y10)</p>
                    <p className="text-xl font-bold text-emerald-400">{fmt(summary.sell_year_10)}</p>
                    <p className="text-xs text-slate-500 mt-1">Net proceeds invested at 7%/yr</p>
                </div>
                <div className="rounded-xl bg-slate-800 border border-slate-700 p-4">
                    <p className="text-xs text-slate-400 mb-1">Keep & Rent (Y10)</p>
                    <p className="text-xl font-bold text-blue-400">{fmt(summary.keep_total_year_10)}</p>
                    <p className="text-xs text-slate-500 mt-1">Equity + cumulative cash flow</p>
                </div>
            </div>

            {/* Tax breakdown */}
            <div className="rounded-xl bg-slate-800 border border-slate-700 p-4">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Sale Tax Breakdown</h3>
                <table className="w-full text-sm">
                    <tbody className="divide-y divide-slate-700">
                        {[
                            ['Selling costs', fmt(summary.selling_costs)],
                            ['CCA Recapture (100% income)', fmt(td.recapture_income)],
                            ['Capital gain', fmt(td.capital_gain)],
                            [`Taxable capital gain (50%)`, fmt(td.taxable_capital_gain)],
                            ['Federal tax (after abatement)', fmt(td.federal_tax)],
                            ['Quebec provincial tax', fmt(td.provincial_tax)],
                            ['Total tax', fmt(td.total_tax)],
                            ['Net proceeds after tax & mortgage', fmt(summary.sell_net_proceeds)],
                        ].map(([label, value]) => (
                            <tr key={label}>
                                <td className="py-1.5 text-slate-400">{label}</td>
                                <td className="py-1.5 text-right text-slate-200 font-mono">{value}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Keep detail */}
            <div className="rounded-xl bg-slate-800 border border-slate-700 p-4">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">Keep & Rent — Year 10</h3>
                <table className="w-full text-sm">
                    <tbody className="divide-y divide-slate-700">
                        {[
                            ['Property equity', fmt(summary.keep_equity_year_10)],
                            ['Cumulative after-tax cash flow', fmt(summary.keep_cumulative_cf_year_10)],
                            ['Total wealth (equity + CF)', fmt(summary.keep_total_year_10)],
                        ].map(([label, value]) => (
                            <tr key={label}>
                                <td className="py-1.5 text-slate-400">{label}</td>
                                <td className="py-1.5 text-right text-slate-200 font-mono">{value}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <button
                onClick={onReset}
                className="w-full py-3 rounded-xl border border-slate-600 text-slate-400 hover:text-white hover:border-slate-400 transition-colors text-sm"
            >
                Clear Results
            </button>
        </div>
    );
}
