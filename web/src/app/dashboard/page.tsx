"use client";

import { useEffect, useState } from "react";
import { meRequest, logout, guardrailsRequest } from "@/lib/api";
import { useRouter } from 'next/navigation';
import {JSX} from "react";
import type { MeResponse,GuardrailsResponse, GuardrailDTO } from "@/lib/api";

export default function DashboardPage(): JSX.Element {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [guardrails, setGuardrails] = useState<GuardrailsResponse | null>(null);
  const router = useRouter();
  useEffect(() => {
    async function fetchMe(): Promise<void> {
      try {
        const res = await meRequest();
        const data = await res.json();

        if (!res.ok) {
          if (res.status === 401) {
            router.push("/");
            return;
          }
          let detail: string = "Failed to fetch user";
          try {
            const data: unknown = await res.json();
            if (typeof data === "object" && data !== null && "detail" in data) {
              detail = String((data as { detail?: unknown}).detail ?? detail);
          }
          }catch{

          }
          setError(detail);
          router.push("/");
          return;
        } else {
          setMe(data as MeResponse);
          
        }
      } catch (err) {
        setError("Request failed");
        router.push('/');
      } finally {
        setLoading(false);
      }
    }

    void fetchMe();
  }, [router]);
  useEffect(() => {
    async function fetchGuardRails(): Promise<void> {
    try {
      const res = await guardrailsRequest();
      const data = await res.json();
      if (!res.ok) {
        if(res.status === 401) {
          router.push("/");
          return;
        }
        let detail: string = "Failed to fetch user";
        try {
          const data: unknown = await res.json();
          if(typeof data === "object" && data !== null && "detail" in data) {
            detail = String((data as { detail?: unknown}).detail ?? detail);
          }
        }catch {
        }
        setError(detail);
        router.push("/");
        return;
      } else {
        console.log(data);
        setGuardrails(data as GuardrailsResponse);
      }
    } catch (err) {
    setError("Request failed");
    router.push('/');
  } finally {
    setLoading(false);
  }
  }
  void fetchGuardRails();
  },[router]);

  if (loading) {
    return <main className="p-4">Loading...</main>;
  }

  if (error) {
    return <main className="p-4 text-red-600">{error}</main>;
  }

  if (!me) {
    return <main className="p-4">No user data.</main>;
  }
  async function logoutLocal(){
    await logout();
    router.push('/')
  }
  return (
    <main className="p-4">
      <h1 className="text-xl font-bold mb-2">Dashboard</h1>
      <p>Email: {me.email}</p>
      <p>User ID: {me.id}</p>
      <p>Created at: {me.created_at}</p>
      <div>
        <h2 className="text-l">Guardrails:</h2>
        <div>{guardrails?.guardrails.map((guardrail: GuardrailDTO, index)=>{
          return <div key = {index}>
            <p>Domain:{guardrail.domain}</p>
            <p>active:{guardrail.is_active ? "true" : "false"}</p>
            <p>rule:{guardrail.rule}</p>
            </div>
        })}</div>
      </div>
      <button onClick={()=>{router.push('/settings')}} className="border-2 border-black p-2 hover:bg-gray-100">Settings</button>
      <button onClick={()=>{logoutLocal()}} className="border-2 border-black p-2 hover:bg-gray-100">logout</button>
    </main>
  );
}
