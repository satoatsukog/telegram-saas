import { useEffect, useState } from "react";
import { api, type ApiError, type Home } from "../lib/api";
import { openInvoice } from "../lib/tg";

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export default function Paywall({ onBack, onPaid }: { onBack: () => void; onPaid: () => void }) {
  const [busy, setBusy] = useState("");
  const [err, setErr] = useState("");
  const [home, setHome] = useState<Home | null>(null);

  useEffect(() => {
    api.paywall().catch(() => undefined);
    api.home().then(setHome);
  }, []);

  const buy = async (plan: string) => {
    setBusy(plan);
    setErr("");
    try {
      let link: string;
      try {
        link = (await api.invoice(plan)).link;
      } catch (e) {
        setErr((e as ApiError).status === 409 ? "You already have an active subscription." : "Could not start payment. Try again.");
        return;
      }
      const status = await openInvoice(link);
      if (status === "unsupported") {
        setErr("Open RecallDeck inside Telegram to pay.");
        return;
      }
      if (status === "cancelled") {
        setErr("Payment cancelled.");
        return;
      }
      if (status !== "paid") {
        setErr("Payment failed. Try again.");
        return;
      }
      for (let i = 0; i < 5; i++) {
        const h = await api.home();
        if (h.premium) {
          onPaid();
          return;
        }
        await sleep(1000);
      }
      setErr("Payment received — activating. Reopen in a moment.");
    } finally {
      setBusy("");
    }
  };

  if (!home) return <div className="p-6 text-gray-500">Loading…</div>;

  if (home.premium)
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
      {err && <p data-testid="paywall-error" className="text-sm text-red-500">{err}</p>}
      <button
        data-testid="buy-monthly"
        disabled={!!busy}
        onClick={() => buy("monthly")}
        className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white disabled:opacity-50"
      >
        Monthly — {home.prices.monthly} ⭐ / 30 days
      </button>
      <button
        data-testid="buy-yearly"
        disabled={!!busy}
        onClick={() => buy("yearly")}
        className="w-full rounded-lg bg-green-600 py-3 font-semibold text-white disabled:opacity-50"
      >
        Yearly — {home.prices.yearly} ⭐ / 365 days
      </button>
    </div>
  );
}
