
import type { ExtensionMessage} from "./shared/messages";
type AuthStatus = 
| { authenticated: true; user: { id: string; email: string} }
| { authenticated: false};
export type Guardrail = {
  id:string;
  domain: string;
  rule: string;
  is_active: boolean;
}
export type Guardrails  = {
  guardrails: Guardrail[], count: number
};
export type FetchGuardrailStatusResult =
  | { authenticated: false }
  | { authenticated: true; guardrails: Guardrails };



const WEB_URL: string = import.meta.env.WEB_URL ?? "http://localhost:3000";
const API_URL: string = import.meta.env.API_URL ?? "http://localhost:8000";

let cachedStatus: AuthStatus = { authenticated: false};
let cachedAtMs: number = 0;
const CACHE_TTL_MS: number= 30_000;


async function fetchAuthStatus(): Promise<AuthStatus> {
  const res: Response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) return {authenticated: false};

  const user: {id: string; email: string } = await res.json();
  return { authenticated: true, user };
}
export async function fetchGuardRailStatus(): Promise<FetchGuardrailStatusResult> {
  const res: Response = await fetch(`${API_URL}/guardrails/`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) return {authenticated: false};

  const guardrails: Guardrails = await res.json();
  return { authenticated: true,  guardrails: guardrails };
}
/*
/*
async function ping(): Promise<void> {
  const API_URL: string = "https://blinders-2l06.onrender.com";
  try {
    const r: Response = await fetch(`${API_URL}/`);
    const j: { status: string } = await r.json();
    console.log("[Blinders] API health:", j.status);
  } catch (e) {
    console.error("[Blinders] API ping failed:", e);
  }
} */
chrome.runtime.onMessage.addListener(
  (msg: unknown, _sender: chrome.runtime.MessageSender, sendResponse: (res: unknown) => void): boolean =>
  { 
    const message: ExtensionMessage = msg as ExtensionMessage;
    console.log("lets see if message is deaduzz messaging")
    console.log(`message ${message}`);
    void (async (): Promise<void> => {
      switch(message.type) {
        case "AUTH_START":{
          await chrome.tabs.create({url: WEB_URL })
          sendResponse({ ok: true});
          return;
        }
        case "AUTH_STATUS":{
          const nowMs: number = Date.now();
          const useCache: boolean = !message.force && (nowMs-cachedAtMs) < CACHE_TTL_MS;
          if(useCache) {
            sendResponse(cachedStatus);
            return;
          }
          const fresh: AuthStatus = await fetchAuthStatus();
          cachedStatus = fresh;
          cachedAtMs = nowMs;
          sendResponse(fresh);
        }
      }
    })();
    return true;
  }
)
//chrome.runtime.onInstalled.addListener(() => void ping());
//chrome.action.onClicked.addListener(() => void ping());
