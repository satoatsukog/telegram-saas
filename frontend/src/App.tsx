import { useEffect, useState } from "react";
import Deck from "./components/Deck";
import Home from "./components/Home";
import Review from "./components/Review";
import { api, canUse } from "./lib/api";
import { getTimeZone } from "./lib/tg";

type Screen = { name: "home" } | { name: "deck"; id: number } | { name: "review" };

export default function App() {
  const [screen, setScreen] = useState<Screen>({ name: "home" });
  const [ready, setReady] = useState(false);
  const usable = canUse();

  useEffect(() => {
    if (!usable) return;
    api
      .saveSettings(getTimeZone())
      .catch(() => undefined)
      .finally(() => setReady(true));
  }, [usable]);

  if (!usable)
    return (
      <div className="mx-auto flex min-h-screen max-w-md flex-col items-center justify-center gap-3 p-8 text-center">
        <div className="text-5xl">📚</div>
        <h1 className="text-xl font-bold">Open RecallDeck from Telegram</h1>
        <p className="text-gray-500">This app runs inside the RecallDeck Telegram bot.</p>
      </div>
    );

  if (!ready) return <div className="p-6 text-center text-gray-500">Loading…</div>;

  return (
    <div className="mx-auto min-h-screen max-w-md bg-white text-gray-900">
      {screen.name === "home" && (
        <Home onOpenDeck={(id) => setScreen({ name: "deck", id })} onReview={() => setScreen({ name: "review" })} />
      )}
      {screen.name === "deck" && <Deck id={screen.id} onBack={() => setScreen({ name: "home" })} />}
      {screen.name === "review" && <Review onDone={() => setScreen({ name: "home" })} />}
    </div>
  );
}
