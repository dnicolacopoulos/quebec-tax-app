import { useCalculate } from './hooks/useCalculate';
import PropertyForm from './components/PropertyForm';
import ResultsPanel from './components/ResultsPanel';
import ComparisonChart from './components/ComparisonChart';

export default function App() {
  const { formData, result, loading, error, updateField, calculate, reset, resetAll } = useCalculate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await calculate();
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 px-4 py-3 flex items-center justify-between shrink-0">
        <div>
          <h1 className="text-base font-bold text-white leading-tight">
            Quebec Rental Property Advisor
          </h1>
          <p className="text-xs text-slate-500">
            Keep vs. Sell — 10-year analysis · 2026 tax rates
          </p>
        </div>
        {result && (
          <button
            onClick={resetAll}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            Clear All
          </button>
        )}
      </header>

      {/* Body */}
      <main className="flex-1 w-full max-w-2xl mx-auto px-4 py-6 flex flex-col gap-6 overflow-y-auto">
        <PropertyForm
          formData={formData}
          loading={loading}
          error={error}
          updateField={updateField}
          onSubmit={handleSubmit}
        />

        {result && (
          <>
            <ComparisonChart result={result} />
            <ResultsPanel result={result} onReset={reset} />
          </>
        )}
      </main>
    </div>
  );
}


