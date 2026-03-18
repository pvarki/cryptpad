export type CardTheme = "light" | "dark";

export interface CryptPadCardData {
  url: string;
  sandbox_url: string;
}

export interface CryptPadCardMeta {
  callsign: string;
  theme: string;
}

export interface CryptPadCardDetails {
  callsign: string;
  theme: CardTheme;
}

export function normalizeTheme(theme: string): CardTheme {
  return theme.trim().toLowerCase() === "light" ? "light" : "dark";
}

export function buildCardDetails(meta: CryptPadCardMeta): CryptPadCardDetails {
  return {
    callsign: meta.callsign.trim() || "Unknown",
    theme: normalizeTheme(meta.theme),
  };
}

export function buildLoginUrl(url: string): string {
  try {
    return new URL("/login/", url).toString();
  } catch {
    return `${url.replace(/\/+$/, "")}/login/`;
  }
}
