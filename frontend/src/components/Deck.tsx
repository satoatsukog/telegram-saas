import { useEffect, useState } from "react";
import { api, type ApiError, type DeckDetail } from "../lib/api";

export default function Deck({ id, onBack, onUpgrade }: { id: number; onBack: () => void; onUpgrade: () => void }) {
  const [data, setData] = useState<DeckDetail | null>(null);
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [paste, setPaste] = useState("");
  const [err, setErr] = useState("");

  const load = () => api.deck(id).then(setData);
  useEffect(() => {
    load();
  }, [id]);

  if (!data) return <div className="p-6 text-gray-500">Loading…</div>;

  return (
    <div className="space-y-4 p-5">
      <div className="flex items-center justify-between">
        <button onClick={onBack} className="text-blue-600">
          ‹ Back
        </button>
        <button
          onClick={async () => {
            await api.deleteDeck(id);
            onBack();
          }}
          className="text-sm text-red-500"
        >
          Delete deck
        </button>
      </div>
      <h1 className="text-lg font-bold">{data.name}</h1>
      <div className="flex gap-2">
        <input
          className="min-w-0 flex-1 rounded-lg border p-2"
          placeholder="word"
          value={front}
          onChange={(e) => setFront(e.target.value)}
        />
        <input
          className="min-w-0 flex-1 rounded-lg border p-2"
          placeholder="meaning"
          value={back}
          onChange={(e) => setBack(e.target.value)}
        />
        <button
          onClick={async () => {
            if (!front.trim() || !back.trim()) return;
            setErr("");
            try {
              await api.addCard(id, front.trim(), back.trim());
              setFront("");
              setBack("");
              load();
            } catch (e) {
              if ((e as ApiError).status === 402) onUpgrade();
            }
          }}
          className="shrink-0 rounded-lg bg-blue-600 px-3 text-white"
        >
          +
        </button>
      </div>
      <textarea
        className="h-24 w-full rounded-lg border p-2 font-mono text-sm"
        placeholder="Paste more: word - meaning"
        value={paste}
        onChange={(e) => setPaste(e.target.value)}
      />
      <button
        onClick={async () => {
          if (!paste.trim()) return;
          setErr("");
          try {
            await api.pasteInto(id, paste);
            setPaste("");
            load();
          } catch (e) {
            if ((e as ApiError).status === 402) onUpgrade();
            else setErr("No valid pairs found. Use: word - meaning");
          }
        }}
        className="w-full rounded-lg border py-2"
      >
        Add pasted lines
      </button>
      {err && <p className="text-sm text-red-500">{err}</p>}
      <div className="space-y-1">
        {data.cards.map((c) => (
          <div key={c.id} className="flex justify-between rounded border p-2 text-sm">
            <span>
              <b>{c.front}</b> — {c.back}
            </span>
            <button
              onClick={async () => {
                await api.deleteCard(c.id);
                load();
              }}
              className="text-red-400"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
