import type {
  Guardrail,
  FetchGuardrailStatusResult,
  Guardrails,
} from "../background";
import { useEffect, useState } from "react";
export function Dashboard() {
  const [guardrails, setGuardrails] = useState<Guardrails | null>(null);
  const [cachedAt, setCachedAt] = useState<number | null>(null);
  const [auth, setAuth] = useState<boolean>(true);
  const [error, setError] = useState<string>("");
  function formatAge(ms: number): string {
    const seconds: number = Math.floor(ms / 1000);
    if (seconds < 60) return `${seconds}s ago`;

    const minutes: number = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;

    const hours: number = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;

    const days: number = Math.floor(hours / 24);
    return `${days}d ago`;
  }
  const getGuardrails = async () => {
    try {
      const res: FetchGuardrailStatusResult = await chrome.runtime.sendMessage({
        type: "GUARDRAILS_GET",
        force: false,
      });
      console.log("[Dashboard] guardrails response:", res);
      if (!res.authenticated) {
        setAuth(false);
        return;
      }
      setError("");
      setAuth(true);
      setGuardrails(res.guardrails);
      setCachedAt(res.cachedAtMs);
    } catch (err) {
      setError(String(err));
    }
  };
  useEffect(() => {
    getGuardrails();
  }, []);
  return auth ? (
    <div>
      <p>Logged in</p>
      <div>
        {guardrails?.guardrails?.map((guardrail: Guardrail, index: number) => {
          return (
            <div key={index}>
              <p>Domain:{guardrail.domain}</p>
              <p>active:{guardrail.is_active ? "true" : "false"}</p>
              <p>rule:{guardrail.rule}</p>
            </div>
          );
        })}
        <p>last updated: {cachedAt ? formatAge(Date.now() - cachedAt) : "n/a"}</p>
      </div>
      <button
        onClick={() => {
          chrome.runtime.sendMessage({ type: "LOGOUT" });
          window.close();
        }}
      >
        Sign out
      </button>
    </div>
  ) : (
    <>
      <div>not logged in</div> {error && <div>{error}</div>}
    </>
  );
}
