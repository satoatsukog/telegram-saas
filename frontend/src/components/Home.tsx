import { useEffect, useState } from "react";
import { api, type ApiError, type Home as HomeT } from "../lib/api";

export default function Home({
  onOpenDeck,
  onReview,
  onUpgrade,
}: {
  onOpenDeck: (id: number) => void;
  onReview: () => void;
  onUpgrade: () => void;
}) {
  const [data, setData] = useState<HomeT | null>(null);
  const [name, setName] = useState("My IELTS words");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const load = () => api.home().then(setData);
  useEffect(() => {
    load();
  }, []);

  if (!data) return <div className="p-6 text-gray-500">Loading…</div>;

  if (data.decks.length === 0) {
    const create = async () => {
      if (!text.trim()) return;
      setBusy(true);
      setErr("");
      try {
        await api.paste(name.trim() || "My words", text);
        onReview();
      } catch (e) {
        if ((e as ApiError).status === 402) onUpgrade();
        else setErr("No valid pairs found. Use: word - meaning");
      } finally {
        setBusy(false);
      }
    };
    return (
      <div className="space-y-4 p-5">
        <h1 className="text-xl font-bold">Welcome to RecallDeck</h1>
        <p className="text-sm text-gray-500">
          Paste your words, one per line: <code>word - meaning</code>
        </p>
        <input className="w-full rounded-lg border p-3" value={name} onChange={(e) => setName(e.target.value)} />
        <textarea
          data-testid="paste"
          className="h-40 w-full rounded-lg border p-3 font-mono text-sm"
          placeholder={"ubiquitous - present everywhere\nmitigate: to make less severe"}
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        {err && <p className="text-sm text-red-500">{err}</p>}
        <button
          data-testid="create"
          disabled={busy}
          onClick={create}
          className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white disabled:opacity-50"
        >
          Add &amp; start review
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-5">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">RecallDeck</h1>
        <div data-testid="streak" className="text-sm font-semibold">
          🔥 {data.streak}
        </div>
      </div>
      {!data.premium && (
        <button
          data-testid="upgrade"
          onClick={onUpgrade}
          className="w-full rounded-lg border border-amber-400 bg-amber-50 py-2 text-sm font-semibold text-amber-700"
        >
          ⭐ Upgrade to Premium — unlimited decks &amp; cards
        </button>
      )}
      <div className="grid grid-cols-2 gap-3 text-center">
        <div className="rounded-lg bg-gray-100 p-3">
          <div className="text-2xl font-bold">{data.dueToday}</div>
          <div className="text-xs text-gray-500">due today</div>
        </div>
        <div className="rounded-lg bg-gray-100 p-3">
          <div className="text-2xl font-bold">{data.totalCards}</div>
          <div className="text-xs text-gray-500">cards</div>
        </div>
      </div>
      <button
        data-testid="review"
        disabled={data.dueToday === 0}
        onClick={onReview}
        className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white disabled:opacity-50"
      >
        Review {data.dueToday > 0 ? `(${data.dueToday})` : ""}
      </button>
      <div className="space-y-2">
        {data.decks.map((d) => (
          <button
            key={d.id}
            onClick={() => onOpenDeck(d.id)}
            className="flex w-full justify-between rounded-lg border p-3 text-left"
          >
            <span>{d.name}</span>
            <span className="text-sm text-gray-500">
              {d.due}/{d.total}
            </span>
          </button>
        ))}
      </div>
      <NewDeck onCreated={load} />
    </div>
  );
}

function NewDeck({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  if (!open)
    return (
      <button onClick={() => setOpen(true)} className="w-full rounded-lg border border-dashed py-3 text-gray-500">
        + New deck
      </button>
    );
  return (
    <div className="flex gap-2">
      <input
        className="flex-1 rounded-lg border p-2"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Deck name"
      />
      <button
        onClick={async () => {
          if (name.trim()) {
            await api.createDeck(name.trim());
            setName("");
            setOpen(false);
            onCreated();
          }
        }}
        className="rounded-lg bg-blue-600 px-4 text-white"
      >
        Add
      </button>
    </div>
  );
}
