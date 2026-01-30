
import  type { Guardrail, FetchGuardrailStatusResult, Guardrails}  from "../background";
import { fetchGuardRailStatus } from "../background";
import { useEffect, useState } from "react";
export function Dashboard()
{
    const [ guardrails, setGuardrails] = useState<Guardrails | null>(null);
    const [ auth, setAuth] = useState<boolean>(true);
    const [ error, setError] = useState<string>("");
    const  getGuardrails = async () => {
        try{
        const res:FetchGuardrailStatusResult =  await fetchGuardRailStatus();
        if(!res.authenticated) {
            setAuth(false);
            return;
        }
        setError("");
        setAuth(true);
        setGuardrails(res.guardrails);
        }catch(err){
            setError(String(err));
        }
      }
    useEffect(()=>{getGuardrails();},[]);
    return auth ?  (<div>
        <p>Logged in</p>
       <div>{guardrails?.guardrails.map((guardrail: Guardrail, index)=>{
          return <div key = {index}>
            <p>Domain:{guardrail.domain}</p>
            <p>active:{guardrail.is_active ? "true" : "false"}</p>
            <p>rule:{guardrail.rule}</p>
            </div>
        })}</div>
        <button onClick={() =>{
            chrome.runtime.sendMessage({ type: "LOGOUT"});
            window.close();
        }}>
            Sign out
        </button>
    </div>) :(<><div>not logged in</div> {error &&<div>{error}</div>}</>)
}