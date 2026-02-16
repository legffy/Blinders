
import type { ExtensionMessage} from "./shared/messages";
type AuthStatus = 
| { authenticated: true; user: { id: string; email: string} }
| { authenticated: false};
export type Guardrail = {
  id:string;
  domain: string;
  rule: number;
  is_active: boolean;
}
export type Guardrails  = {
  guardrails: Guardrail[], count?: number
};
export type GuardrailsCache = {
guardrails: Guardrail[], count?: number, guardrailsCachedAt: number, guardrailsVersion: number;
}
export type GuardrailsStorage = {
  guardrails?: Guardrail[];
  guardrailsCachedAt?: number;
  guardrailsCount?: number;
  guardrailsVersion?: number;
}
export type FetchGuardrailStatusResult =
  | { authenticated: false }
  | { authenticated: true; guardrails: Guardrails; cachedAtMs: number; version: number; };



const WEB_URL: string = import.meta.env.WEB_URL ?? "http://localhost:3000";
const API_URL: string = import.meta.env.API_URL ?? "http://localhost:8000";

let cachedStatus: AuthStatus = { authenticated: false};
let cachedAtMs: number = 0;
const CACHE_TTL_MS: number= 30_000;
const GUARDRAILS_TTL_MS: number = 5 * 60_000;


async function fetchAuthStatus(): Promise<AuthStatus> {
  const res: Response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) return {authenticated: false};

  const user: {id: string; email: string } = await res.json();
  return { authenticated: true, user };
}
async function cacheGuardrails(guardrails: Guardrails,version: number): Promise<void> {
  await chrome.storage.local.set({
    guardrails: guardrails.guardrails,
    guardrailsCachedAt: Date.now(),
    guardrailsCount: guardrails.count ?? guardrails.guardrails.length,
    guardrailsVersion: version,
  })
}
async function getCachedGuardrails(): Promise<GuardrailsCache| null> {
  const result: GuardrailsStorage= await chrome.storage.local.get([
    "guardrails",
    "guardrailsCachedAt",
    "guardrailsCount",
    "guardrailsVersion"
  ])
  if(!result.guardrails || !result.guardrailsCachedAt){
    return null;
  }
  return {guardrails: result.guardrails,count: result.guardrailsCount ,guardrailsCachedAt: result.guardrailsCachedAt,guardrailsVersion: result.guardrailsVersion ?? 0}
  }
async function fetchGuardrailsMeta(): Promise<{ version: number } | null> {
  const res: Response = await fetch(`${API_URL}/guardrails/meta`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) return null;
  const meta: { version: number } = await res.json();
  return meta;
}
async function fetchGuardrailsFromServer(): Promise<Guardrails | null> {
  const res: Response = await fetch(`${API_URL}/guardrails/`, {
    method: "GET",
    credentials: "include",
  });
  if (!res.ok) return null;
  const data: Guardrails = await res.json();
  return data;
}
async function getAuthStatus(force: boolean): Promise<AuthStatus> {
  const nowMs: number = Date.now();
  const useCache: boolean = !force && (nowMs - cachedAtMs) < CACHE_TTL_MS;
  if (useCache) return cachedStatus;

  const fresh: AuthStatus = await fetchAuthStatus();
  cachedStatus = fresh;
  cachedAtMs = nowMs;
  return fresh;
}
export async function fetchGuardRailStatus(force: boolean = false): Promise<FetchGuardrailStatusResult> {
  const auth: AuthStatus = await getAuthStatus(force);
  if(!auth.authenticated) return {authenticated: false};
  const cache: GuardrailsCache | null = await getCachedGuardrails();
  const now: number = Date.now()
  if(cache && !force && (now -cache.guardrailsCachedAt) < GUARDRAILS_TTL_MS){
    void revalidateGuardrails(cache.guardrailsVersion);
    return {authenticated: true, guardrails: {guardrails: cache.guardrails}, cachedAtMs: cache.guardrailsCachedAt, version: cache.guardrailsVersion }
  }
  const meta: { version: number} | null = await fetchGuardrailsMeta();
  const data: Guardrails | null = await fetchGuardrailsFromServer();
  if(!data) return { authenticated: false};
  await cacheGuardrails(data, meta?.version ?? (cache?.guardrailsVersion ?? 0));
  console.log(data);
  return {authenticated : true, guardrails: {guardrails: data.guardrails}, cachedAtMs: now,  version: meta?.version ?? (cache?.guardrailsVersion ?? 0) };
}
async function revalidateGuardrails(localVersion: number): Promise<void> {
  const meta: { version: number } | null = await fetchGuardrailsMeta();
  if (!meta) return;

  if (meta.version <= localVersion) return;

  const data: Guardrails | null = await fetchGuardrailsFromServer();
  if (!data) return;

  await cacheGuardrails(data, meta.version);

  // Notify all tabs/content scripts that rules changed
  const tabs: chrome.tabs.Tab[] = await chrome.tabs.query({});
  for (const tab of tabs) {
    if (tab.id) {
      chrome.tabs.sendMessage(tab.id, { type: "GUARDRAILS_UPDATED" });
    }
  }
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
          return;
        }
        case "GUARDRAILS_GET":{
          const force: boolean = Boolean(message.force);
          const data: FetchGuardrailStatusResult = await fetchGuardRailStatus(force);

          console.log("[Blinders] GUARDRAILS_GET reuslt:", data);

          sendResponse(data);
          return;
        }
      }
    })();
    return true;
  }
)


//chrome.runtime.onInstalled.addListener(() => void ping());
//chrome.action.onClicked.addListener(() => void ping());
