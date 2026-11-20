import { init, retrieveRawInitData } from "@telegram-apps/sdk-react";

let rawInit = "";

export function initTelegram(): void {
  try {
    init();
  } catch {
    void 0;
  }
  try {
    rawInit = retrieveRawInitData() ?? "";
  } catch {
    rawInit = "";
  }
  const tg = (window as unknown as { Telegram?: { WebApp?: any } }).Telegram?.WebApp;
  if (!rawInit && tg?.initData) rawInit = tg.initData;
  if (tg) {
    try {
      tg.ready();
      tg.expand();
    } catch {
      void 0;
    }
  }
}

export function getInitData(): string {
  return rawInit;
}

export function getTimeZone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

export function openInvoice(url: string): Promise<string> {
  const tg = (window as unknown as { Telegram?: { WebApp?: any } }).Telegram?.WebApp;
  return new Promise((resolve) => {
    if (tg?.openInvoice) tg.openInvoice(url, (status: string) => resolve(status));
    else resolve("unsupported");
  });
}
