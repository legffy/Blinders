

async function ping(): Promise<void> {
  const API_URL: string = "https://blinders-2l06.onrender.com";
  try {
    const r: Response = await fetch(`${API_URL}/`);
    const j: { status: string } = await r.json();
    console.log("[Blinders] API health:", j.status);
  } catch (e) {
    console.error("[Blinders] API ping failed:", e);
  }
}
chrome.runtime.onInstalled.addListener(() => void ping());
chrome.action.onClicked.addListener(() => void ping());
