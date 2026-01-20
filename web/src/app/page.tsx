"use client";
import Image from "next/image";
import React, { useEffect, useState } from "react";
import { meRequest } from "@/lib/api";
import { useRouter } from "next/navigation";
import { JSX } from "react";

type AuthAction = "login" | "signup";

export default function Home(): React.JSX.Element {
  const router = useRouter();
  useEffect(() => {
        async function fetchMe(): Promise<void> {
          try {
            const res = await meRequest();
            const data = await res.json();
    
            if (res.ok) {
              router.push('/dashboard')
            }
          } catch (err) {
            router.push('/');
          } finally {
            setLoading(false);
          }
        }
    
        void fetchMe();
      }, []);
  const [loading, setLoading] = useState<boolean>(false);
  async function goToPage(action: AuthAction): Promise<void>  {
    setLoading(true);
    router.push(`/${action}`);
  }
  return  loading ?  <div className="flex items-center"> loading </div> :
  (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 lg:items-center sm:items-start">
        <h1 className="text-5xl">Welcome to Blinders</h1>
        <div className="flex items-center justify-center space-x-4">
          <button className="border-2 p-2" onClick={() => goToPage("login")}>Login</button>
          <button className="border-2 p-2" onClick={() => goToPage("signup") }>Sign up</button>
        </div>
      </main>
    </div>
  ) 
}
