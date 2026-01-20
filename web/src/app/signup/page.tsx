"use client";

import { FormEvent, useState, useEffect } from "react";
import { signupRequest, meRequest } from "@/lib/api";
import { JSX } from "react";
import { useRouter } from "next/navigation";
import  GoogleButton  from "../components/GoogleButton"


export default function SignupPage(): JSX.Element {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();
  async function handleSubmit(e: FormEvent<HTMLFormElement>): Promise<void> {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);

    try {
      const res = await signupRequest(email, password);
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail ?? "Signup failed");
      } else {
        setMessage("Signup successful. You can log in now.");
      }
    } catch (err) {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  }
   useEffect(() => {
      async function fetchMe(): Promise<void> {
        try {
          const res = await meRequest();
          const data = await res.json();
  
          if (!res.ok) {
            setError(data.detail ?? "Failed to fetch user");
          } else {
            router.push('/dashboard')
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
  return (
    <main className="flex min-h-screen items-center justify-center">
      <div className="flex flex-col">
      <form onSubmit={handleSubmit} className="flex flex-col gap-2 w-80">
        <h1 className="text-xl font-bold">Signup</h1>

        <input
          className="border px-2 py-1 rounded"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="email"
          required
        />

        <input
          className="border px-2 py-1 rounded"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          required
        />

        <button
          type="submit"
          className="border px-2 py-1 rounded"
          disabled={loading}
        >
          {loading ? "Signing up..." : "Signup"}
        </button>
       
        {message && <p className="text-green-600 text-sm">{message}</p>}
      {error && <p className="text-red-600 text-sm">{error === "Missing access_token cookie" ? "" : error }</p>}
      </form>
       <GoogleButton/>
       </div>
    </main>
  );
}
