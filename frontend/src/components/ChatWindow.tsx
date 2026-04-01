import { useEffect, useRef } from 'react';
import type { Question } from '../types/api';
import QuestionCard from './QuestionCard';

interface HistoryItem {
    role: 'assistant' | 'user';
    text: string;
}

interface Props {
    history: HistoryItem[];
    currentQuestion: Question | null;
    loading: boolean;
    error: string | null;
    onAnswer: (value: number | boolean | string) => void;
    onStart: () => void;
    started: boolean;
}

export default function ChatWindow({
    history,
    currentQuestion,
    loading,
    error,
    onAnswer,
    onStart,
    started,
}: Props) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history, currentQuestion]);

    if (!started) {
        return (
            <div className="flex flex-col items-center justify-center h-full gap-6 text-center px-4">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">Quebec Rental Property Advisor</h2>
                    <p className="text-slate-400 max-w-md">
                        Answer a few questions about your property and we'll compare the net 10-year financial
                        outcome of selling vs. keeping it — fully tax-adjusted for Quebec 2026 rules.
                    </p>
                </div>
                <button
                    onClick={onStart}
                    className="px-8 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-lg transition-colors"
                >
                    Start Analysis
                </button>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            {/* Message history */}
            <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
                {history.map((msg, i) => (
                    <div
                        key={i}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${msg.role === 'user'
                                ? 'bg-indigo-600 text-white rounded-br-sm'
                                : 'bg-slate-700 text-slate-100 rounded-bl-sm'
                                }`}
                        >
                            {msg.text}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-slate-700 rounded-2xl rounded-bl-sm px-4 py-2.5">
                            <span className="flex gap-1">
                                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0ms]" />
                                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:150ms]" />
                                <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:300ms]" />
                            </span>
                        </div>
                    </div>
                )}

                {error && (
                    <div className="text-red-400 text-sm text-center py-2">{error}</div>
                )}

                <div ref={bottomRef} />
            </div>

            {/* Active question input */}
            {currentQuestion && !loading && (
                <div className="border-t border-slate-700 px-4 py-3">
                    {currentQuestion.hint && (
                        <p className="text-xs text-slate-500 mb-1">{currentQuestion.hint}</p>
                    )}
                    <QuestionCard
                        question={currentQuestion}
                        onAnswer={onAnswer}
                        loading={loading}
                    />
                </div>
            )}
        </div>
    );
}
