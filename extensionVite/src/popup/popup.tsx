import { useEffect, useState } from "react";
import { Dashboard } from "./Dashboard";
import Signedout from "./Signedout";

type AuthState = "SIGNED_OUT" | "SIGNING_IN" | "SIGNED_IN" | "ERROR";

type AuthStatusResponse =
  | { authenticated: true; user: { id: string; email: string } }
  | { authenticated: false };

export default function Popup() {
  const [authState, setAuthState] = useState<AuthState>("SIGNED_OUT");

  const checkAuth = (force: boolean): void => {
    console.log("hello my nigga");
    chrome.runtime.sendMessage({ type: "AUTH_STATUS", force }, (res: AuthStatusResponse) => {
      if (chrome.runtime.lastError) {
        console.error("AUTH_STATUS failed:", chrome.runtime.lastError.message);
        setAuthState("ERROR");
        return;
      }
      setAuthState(res?.authenticated ? "SIGNED_IN" : "SIGNED_OUT");
    });
  };

  useEffect((): void => {
    console.log("effect");
    checkAuth(false);
    console.log("effect done");
  }, []);

  if (authState === "ERROR") {
    return <p>Extension auth check failed. Check service worker.</p>;
  }

  if (authState === "SIGNING_IN") {
    return (
      <div>
        <p>Finish signing in in the tab we opened.</p>
        <button onClick={(): void => checkAuth(true)}>I signed in — refresh</button>
      </div>
    );
  }

  if (authState === "SIGNED_IN") {
    return <Dashboard />;
  }

  return (
    <Signedout
      onLogin={(): void => {
        setAuthState("SIGNING_IN");
        chrome.runtime.sendMessage({ type: "AUTH_START" }, () => {
          if (chrome.runtime.lastError) {
            console.error("AUTH_START failed:", chrome.runtime.lastError.message);
            setAuthState("ERROR");
          }
        });
      }}
    />
  );
}
