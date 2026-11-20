import { useEffect, useState } from "react";
import { api, type Card } from "../lib/api";

export default function Review({ onDone }: { onDone: () => void }) {
  const [card, setCard] = useState<Card | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [streak, setStreak] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const r = await api.nextReview();
    setCard(r.card);
    setRevealed(false);
    setLoading(false);
    if (!r.card) {
      const h = await api.home();
      setStreak(h.streak);
    }
  };
  useEffect(() => {
    load();
  }, []);

  const grade = async (g: string) => {
    if (!card) return;
    const r = await api.grade(card.id, g);
    setStreak(r.streak);
    if (r.due === 0) setCard(null);
    else await load();
  };

  if (loading) return <div className="p-6 text-gray-500">Loading…</div>;

  if (!card)
    return (
      <div className="space-y-4 p-8 text-center">
        <div className="text-5xl">🔥</div>
        <div data-testid="streak-done" className="text-2xl font-bold">
          Streak {streak}
        </div>
        <p className="text-gray-500">All done for today. Come back tomorrow!</p>
        <button onClick={onDone} className="rounded-lg bg-blue-600 px-6 py-3 text-white">
          Home
        </button>
      </div>
    );

  return (
    <div className="flex min-h-screen flex-col p-5">
      <button onClick={onDone} className="self-start text-blue-600">
        ‹ Home
      </button>
      <div className="flex flex-1 items-center justify-center">
        <div className="text-center">
          <div data-testid="front" className="text-3xl font-bold">
            {card.front}
          </div>
          {revealed && (
            <div data-testid="back" className="mt-4 text-xl text-gray-600">
              {card.back}
            </div>
          )}
        </div>
      </div>
      {!revealed ? (
        <button
          data-testid="reveal"
          onClick={() => setRevealed(true)}
          className="w-full rounded-lg bg-gray-800 py-4 font-semibold text-white"
        >
          Show answer
        </button>
      ) : (
        <div className="grid grid-cols-3 gap-2">
          <button data-testid="again" onClick={() => grade("again")} className="rounded-lg bg-red-500 py-4 font-semibold text-white">
            Again
          </button>
          <button data-testid="good" onClick={() => grade("good")} className="rounded-lg bg-blue-600 py-4 font-semibold text-white">
            Good
          </button>
          <button data-testid="easy" onClick={() => grade("easy")} className="rounded-lg bg-green-600 py-4 font-semibold text-white">
            Easy
          </button>
        </div>
      )}
    </div>
  );
}
