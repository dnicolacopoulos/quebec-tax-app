import { useState } from 'react';
import type { Question } from '../types/api';

interface Props {
    question: Question;
    onAnswer: (value: number | boolean | string) => void;
    loading: boolean;
}

function fmt(type: Question['type'], val: string): number | boolean | string {
    if (type === 'yesno') return val === 'true';
    if (type === 'number') return parseInt(val, 10);
    return parseFloat(val); // currency, percentage
}

export default function QuestionCard({ question, onAnswer, loading }: Props) {
    const [inputVal, setInputVal] = useState(
        question.default != null ? String(question.default) : ''
    );

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputVal === '') return;
        onAnswer(fmt(question.type, inputVal));
        setInputVal('');
    };

    if (question.type === 'yesno') {
        return (
            <div className="flex gap-3 mt-2">
                <button
                    onClick={() => onAnswer(true)}
                    disabled={loading}
                    className="flex-1 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold transition-colors"
                >
                    Yes
                </button>
                <button
                    onClick={() => onAnswer(false)}
                    disabled={loading}
                    className="flex-1 py-3 rounded-xl bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-white font-semibold transition-colors"
                >
                    No
                </button>
            </div>
        );
    }

    const prefix = question.type === 'currency' ? '$' : null;
    const suffix = question.type === 'percentage' ? '%' : null;
    const inputMode = question.type === 'number' ? 'numeric' : 'decimal';

    return (
        <form onSubmit={handleSubmit} className="mt-2 flex gap-2">
            <div className="relative flex-1">
                {prefix && (
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 font-medium">
                        {prefix}
                    </span>
                )}
                <input
                    type="number"
                    inputMode={inputMode}
                    min={0}
                    step={question.type === 'number' ? 1 : 'any'}
                    value={inputVal}
                    placeholder={question.default != null ? String(question.default) : '0'}
                    onChange={e => setInputVal(e.target.value)}
                    disabled={loading}
                    className={`w-full rounded-xl bg-slate-800 border border-slate-600 text-white py-3
            focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
            disabled:opacity-50
            ${prefix ? 'pl-7 pr-3' : suffix ? 'pl-3 pr-8' : 'px-3'}`}
                />
                {suffix && (
                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-medium">
                        {suffix}
                    </span>
                )}
            </div>
            <button
                type="submit"
                disabled={loading || inputVal === ''}
                className="px-5 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold transition-colors"
            >
                {loading ? '…' : '→'}
            </button>
        </form>
    );
}
