import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import type { CalculationResult } from '../types/api';

interface Props {
    result: CalculationResult;
}

interface ChartPoint {
    year: number;
    sell: number;
    keep: number;
}

const fmt = (n: number) =>
    n >= 1_000_000
        ? `$${(n / 1_000_000).toFixed(2)}M`
        : `$${(n / 1_000).toFixed(0)}K`;

export default function ComparisonChart({ result }: Props) {
    const data: ChartPoint[] = result.keep_series.map(k => ({
        year: k.year,
        sell: result.sell_series.find(s => s.year === k.year)?.value ?? 0,
        keep: k.total,
    }));

    // Prepend year-0 sell with keep year-0 equity as 0 cash-flow
    const year0 = { year: 0, sell: result.sell_series[0].value, keep: result.keep_series[0].equity };
    const chartData = [year0, ...data];

    return (
        <div className="rounded-xl bg-slate-800 border border-slate-700 p-4">
            <h3 className="text-sm font-semibold text-slate-300 mb-3">10-Year Wealth Projection</h3>
            <ResponsiveContainer width="100%" height={260}>
                <LineChart data={chartData} margin={{ top: 4, right: 16, left: 8, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis
                        dataKey="year"
                        tick={{ fill: '#94a3b8', fontSize: 11 }}
                        label={{ value: 'Year', position: 'insideBottom', offset: -2, fill: '#64748b', fontSize: 11 }}
                    />
                    <YAxis
                        tick={{ fill: '#94a3b8', fontSize: 11 }}
                        tickFormatter={fmt}
                        width={64}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
                        labelStyle={{ color: '#94a3b8', fontSize: 12 }}
                        itemStyle={{ fontSize: 12 }}
                        formatter={(v) =>
                            typeof v === 'number'
                                ? v.toLocaleString('en-CA', { style: 'currency', currency: 'CAD', maximumFractionDigits: 0 })
                                : String(v)
                        }
                        labelFormatter={(l) => `Year ${l}`}
                    />
                    <Legend
                        wrapperStyle={{ fontSize: 12, color: '#94a3b8' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="sell"
                        name="Sell & Reinvest"
                        stroke="#34d399"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, fill: '#34d399' }}
                    />
                    <Line
                        type="monotone"
                        dataKey="keep"
                        name="Keep & Rent"
                        stroke="#60a5fa"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4, fill: '#60a5fa' }}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
