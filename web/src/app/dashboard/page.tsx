"use client";

import { useEffect, useState } from "react";
import { meRequest, logout } from "@/lib/api";
import { useRouter } from 'next/navigation';
import {JSX} from "react";
import { RSC_CONTENT_TYPE_HEADER } from "next/dist/client/components/app-router-headers";
import type { MeResponse } from "@/lib/api";

export default function DashboardPage(): JSX.Element {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const router = useRouter();
  useEffect(() => {
    async function fetchMe(): Promise<void> {
      try {
        const res = await meRequest();
        const data = await res.json();

        if (!res.ok) {
          setError(data.detail ?? "Failed to fetch user");
          router.push('/');
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
  }, []);

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
    logout()
    router.push('/')
  }
  return (
    <main className="p-4">
      <h1 className="text-xl font-bold mb-2">Dashboard</h1>
      <p>Email: {me.email}</p>
      <p>User ID: {me.id}</p>
      <p>Created at: {me.created_at}</p>
      <button onClick={()=>{logoutLocal()}} className="border-2 border-black p-2 hover:bg-gray-100">logout</button>
    </main>
  );
}
