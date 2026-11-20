import { getInitData } from "./tg";

export type Deck = { id: number; name: string; due: number; total: number };
export type Home = {
  streak: number;
  dueToday: number;
  totalCards: number;
  premium: boolean;
  premiumUntil: string | null;
  prices: { monthly: number; yearly: number };
  decks: Deck[];
};
export type Card = { id: number; front: string; back: string };
export type DeckDetail = { id: number; name: string; cards: Card[] };
export type Next = { card: Card | null; due: number };
export type GradeResult = { streak: number; due: number };

type ApiImpl = {
  home(): Promise<Home>;
  saveSettings(tz: string): Promise<unknown>;
  paste(name: string, text: string): Promise<{ deckId: number; added: number }>;
  deck(id: number): Promise<DeckDetail>;
  createDeck(name: string): Promise<{ id: number; name: string }>;
  renameDeck(id: number, name: string): Promise<unknown>;
  deleteDeck(id: number): Promise<unknown>;
  addCard(id: number, front: string, back: string): Promise<{ id: number }>;
  pasteInto(id: number, text: string): Promise<{ added: number }>;
  importCsv(id: number, text: string): Promise<{ added: number }>;
  deleteCard(id: number): Promise<unknown>;
  nextReview(): Promise<Next>;
  grade(cardId: number, grade: string): Promise<GradeResult>;
  invoice(plan: string): Promise<{ link: string }>;
  paywall(): Promise<unknown>;
};

export type ApiError = Error & { status?: number; detail?: string };

async function req(path: string, method = "GET", body?: unknown): Promise<any> {
  const res = await fetch("/api" + path, {
    method,
    headers: { "Content-Type": "application/json", Authorization: "tma " + getInitData() },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = "";
    try {
      detail = (await res.json()).detail ?? "";
    } catch {
      detail = "";
    }
    const err: ApiError = new Error(detail || res.statusText);
    err.status = res.status;
    err.detail = detail;
    throw err;
  }
  return res.status === 204 ? null : res.json();
}

const real: ApiImpl = {
  home: () => req("/home"),
  saveSettings: (tz) => req("/settings", "POST", { tz }),
  paste: (name, text) => req("/paste", "POST", { name, text }),
  deck: (id) => req("/decks/" + id),
  createDeck: (name) => req("/decks", "POST", { name }),
  renameDeck: (id, name) => req("/decks/" + id, "PATCH", { name }),
  deleteDeck: (id) => req("/decks/" + id, "DELETE"),
  addCard: (id, front, back) => req("/decks/" + id + "/cards", "POST", { front, back }),
  pasteInto: (id, text) => req("/decks/" + id + "/paste", "POST", { text }),
  importCsv: (id, text) => req("/decks/" + id + "/csv", "POST", { text }),
  deleteCard: (id) => req("/cards/" + id, "DELETE"),
  nextReview: () => req("/review/next"),
  grade: (cardId, grade) => req("/review/grade", "POST", { card_id: cardId, grade }),
  invoice: (plan) => req("/invoice", "POST", { plan }),
  paywall: () => req("/paywall", "POST"),
};

const SEPS = [" - ", " — ", " – "];

function parsePairs(text: string): [string, string][] {
  const out: [string, string][] = [];
  for (const line of text.split(/\r?\n/)) {
    const s = line.trim();
    if (!s) continue;
    const cands: [number, number][] = [];
    for (const sep of SEPS) {
      const i = s.indexOf(sep);
      if (i !== -1) cands.push([i, sep.length]);
    }
    const c = s.indexOf(":");
    if (c !== -1) cands.push([c, 1]);
    if (!cands.length) continue;
    cands.sort((a, b) => a[0] - b[0]);
    const [pos, len] = cands[0];
    const front = s.slice(0, pos).trim();
    const back = s.slice(pos + len).trim();
    if (front && back) out.push([front, back]);
  }
  return out;
}

type MC = { id: number; front: string; back: string; due: boolean };
const store: { id: number; name: string; cards: MC[] }[] = [];
let seq = 1;
let mockStreak = 0;

function dueCount(): number {
  return store.reduce((a, d) => a + d.cards.filter((c) => c.due).length, 0);
}

const mock: ApiImpl = {
  async home() {
    const decks = store.map((d) => ({
      id: d.id,
      name: d.name,
      due: d.cards.filter((c) => c.due).length,
      total: d.cards.length,
    }));
    return {
      streak: mockStreak,
      dueToday: dueCount(),
      totalCards: decks.reduce((a, d) => a + d.total, 0),
      premium: false,
      premiumUntil: null,
      prices: { monthly: 199, yearly: 1499 },
      decks,
    };
  },
  async saveSettings() {
    return null;
  },
  async paste(name, text) {
    const pairs = parsePairs(text);
    if (!pairs.length) throw new Error("no valid pairs found");
    const cards = pairs.map(([f, b]) => ({ id: seq++, front: f, back: b, due: true }));
    const deck = { id: seq++, name, cards };
    store.push(deck);
    return { deckId: deck.id, added: cards.length };
  },
  async deck(id) {
    const d = store.find((x) => x.id === id)!;
    return { id: d.id, name: d.name, cards: d.cards.map((c) => ({ id: c.id, front: c.front, back: c.back })) };
  },
  async createDeck(name) {
    const d = { id: seq++, name, cards: [] as MC[] };
    store.push(d);
    return { id: d.id, name };
  },
  async renameDeck(id, name) {
    const d = store.find((x) => x.id === id)!;
    d.name = name;
    return null;
  },
  async deleteDeck(id) {
    const i = store.findIndex((d) => d.id === id);
    if (i >= 0) store.splice(i, 1);
    return null;
  },
  async addCard(id, front, back) {
    const d = store.find((x) => x.id === id)!;
    const c = { id: seq++, front, back, due: true };
    d.cards.push(c);
    return { id: c.id };
  },
  async pasteInto(id, text) {
    const d = store.find((x) => x.id === id)!;
    const pairs = parsePairs(text);
    if (!pairs.length) throw new Error("no valid pairs found");
    const cs = pairs.map(([f, b]) => ({ id: seq++, front: f, back: b, due: true }));
    d.cards.push(...cs);
    return { added: cs.length };
  },
  async importCsv(id, text) {
    const d = store.find((x) => x.id === id)!;
    const cs: MC[] = [];
    for (const line of text.split(/\r?\n/)) {
      const comma = line.indexOf(",");
      if (comma === -1) continue;
      const front = line.slice(0, comma).trim();
      const back = line.slice(comma + 1).trim();
      if (front && back) cs.push({ id: seq++, front, back, due: true });
    }
    if (!cs.length) throw new Error("no valid pairs found");
    d.cards.push(...cs);
    return { added: cs.length };
  },
  async deleteCard(id) {
    for (const d of store) d.cards = d.cards.filter((c) => c.id !== id);
    return null;
  },
  async nextReview() {
    for (const d of store) {
      const c = d.cards.find((x) => x.due);
      if (c) return { card: { id: c.id, front: c.front, back: c.back }, due: dueCount() };
    }
    return { card: null, due: 0 };
  },
  async grade(cardId) {
    for (const d of store) {
      const c = d.cards.find((x) => x.id === cardId);
      if (c) c.due = false;
    }
    if (mockStreak === 0) mockStreak = 1;
    return { streak: mockStreak, due: dueCount() };
  },
  async invoice() {
    return { link: "https://t.me/invoice/mock" };
  },
  async paywall() {
    return null;
  },
};

export const canUse = (): boolean => Boolean(getInitData()) || import.meta.env.DEV;

const pick = (): ApiImpl => (!getInitData() && import.meta.env.DEV ? mock : real);

export const api: ApiImpl = {
  home: () => pick().home(),
  saveSettings: (tz) => pick().saveSettings(tz),
  paste: (name, text) => pick().paste(name, text),
  deck: (id) => pick().deck(id),
  createDeck: (name) => pick().createDeck(name),
  renameDeck: (id, name) => pick().renameDeck(id, name),
  deleteDeck: (id) => pick().deleteDeck(id),
  addCard: (id, front, back) => pick().addCard(id, front, back),
  pasteInto: (id, text) => pick().pasteInto(id, text),
  importCsv: (id, text) => pick().importCsv(id, text),
  deleteCard: (id) => pick().deleteCard(id),
  nextReview: () => pick().nextReview(),
  grade: (cardId, grade) => pick().grade(cardId, grade),
  invoice: (plan) => pick().invoice(plan),
  paywall: () => pick().paywall(),
};
