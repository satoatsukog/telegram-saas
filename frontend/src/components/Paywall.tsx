import { useEffect, useState } from "react";
import { api, type Home } from "../lib/api";
import { openInvoice } from "../lib/tg";

export default function Paywall({ onBack, onPaid }: { onBack: () => void; onPaid: () => void }) {
  const [busy, setBusy] = useState("");
  const [home, setHome] = useState<Home | null>(null);

  useEffect(() => {
    api.paywall().catch(() => undefined);
    api.home().then(setHome);
  }, []);

  const buy = async (plan: string) => {
    setBusy(plan);
    try {
      const { link } = await api.invoice(plan);
      const status = await openInvoice(link);
      if (status === "paid") onPaid();
    } finally {
      setBusy("");
    }
  };

  if (home?.premium)
    return (
      <div className="space-y-4 p-5">
        <button onClick={onBack} className="text-blue-600">
          ‹ Back
        </button>
        <div className="text-4xl">⭐</div>
        <h1 className="text-xl font-bold">Premium active</h1>
        <p data-testid="premium-until" className="text-gray-600">
          Premium active until {home.premiumUntil ? new Date(home.premiumUntil).toLocaleDateString() : "—"}
        </p>
      </div>
    );

  return (
    <div className="space-y-4 p-5">
      <button onClick={onBack} className="text-blue-600">
        ‹ Back
      </button>
      <div className="text-4xl">⭐</div>
      <h1 className="text-xl font-bold">RecallDeck Premium</h1>
      <p className="text-sm text-gray-500">
        Unlimited decks and cards. The free plan allows 2 decks and 60 cards.
      </p>
      <button
        data-testid="buy-monthly"
        disabled={!!busy}
        onClick={() => buy("monthly")}
        className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white disabled:opacity-50"
      >
        Monthly — 199 ⭐ / 30 days
      </button>
      <button
        data-testid="buy-yearly"
        disabled={!!busy}
        onClick={() => buy("yearly")}
        className="w-full rounded-lg bg-green-600 py-3 font-semibold text-white disabled:opacity-50"
      >
        Yearly — 1499 ⭐ / 365 days
      </button>
    </div>
  );
}
