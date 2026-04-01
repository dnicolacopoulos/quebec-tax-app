import { useSession } from './hooks/useSession';
import ChatWindow from './components/ChatWindow';
import ResultsPanel from './components/ResultsPanel';
import ComparisonChart from './components/ComparisonChart';

export default function App() {
  const {
    sessionId,
    currentQuestion,
    result,
    history,
    loading,
    error,
    createSession,
    sendAnswer,
    reset,
  } = useSession();

  const started = sessionId !== null || result !== null;

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
        {started && (
          <button
            onClick={reset}
            className="text-xs text-slate-500 hover:text-slate-300 transition-colors"
          >
            Restart
          </button>
        )}
      </header>

      {/* Body */}
      {result ? (
        <main className="flex-1 max-w-2xl w-full mx-auto px-2 py-4 flex flex-col gap-4 overflow-y-auto">
          <ComparisonChart result={result} />
          <ResultsPanel result={result} onReset={reset} />
        </main>
      ) : (
        <main className="flex-1 flex flex-col max-w-xl w-full mx-auto overflow-hidden">
          <ChatWindow
            history={history}
            currentQuestion={currentQuestion}
            loading={loading}
            error={error}
            onAnswer={sendAnswer}
            onStart={createSession}
            started={started}
          />
        </main>
      )}
    </div>
  );
}


